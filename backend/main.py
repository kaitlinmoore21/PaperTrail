from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pdf2image import convert_from_path
from PIL import Image
import traceback
import pytesseract, os, io, uuid, json, tempfile, subprocess
from pathlib import Path
from database import SessionLocal, init_db
from models import Document
from utils_pdf import generate_pdf_bytes, encrypt_and_save_pdf, decrypt_pdf_bytes_from_path
from ai_ollama import ai_extract_and_classify
from datetime import datetime
from docx import Document as DocxDocument
from docx.opc.exceptions import PackageNotFoundError
import textract 


TESSERACT_CMD = os.getenv("TESSERACT_CMD")
if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
    print(f"TESSERACT_CMD set to: {TESSERACT_CMD!r}")

print(f"pytesseract command: {pytesseract.pytesseract.tesseract_cmd!r}")

UPLOAD_DIR = Path("C:/PaperTrail/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="PaperTrail Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db() 

class PasswordRequest(BaseModel):
    password: str

def fast_extract_docx(contents: bytes) -> str | None:
    """Extracts text directly from DOCX bytes without using LibreOffice or OCR."""
    try:
        doc = DocxDocument(io.BytesIO(contents))
        return "\n".join([p.text for p in doc.paragraphs])
    except PackageNotFoundError:
        # File is corrupt or not a true DOCX
        return None
    except Exception as e:
        print(f"python-docx failed: {e}")
        return None


def ocr_from_image_bytes(contents: bytes) -> str:
    img = Image.open(io.BytesIO(contents)).convert("RGB")
    return pytesseract.image_to_string(img)

def ocr_from_pdf_path(pdf_path: str) -> str:
    pages = convert_from_path(pdf_path)
    text_blocks = [pytesseract.image_to_string(pg) for pg in pages]
    return "\n".join(text_blocks)

@app.get("/")
def root():
    return {"message": "PaperTrail API Running"}

@app.post("/upload/")
async def upload_and_process(file: UploadFile = File(...)):
    filename = file.filename or "upload"
    ext = Path(filename).suffix.lower()
    uid = uuid.uuid4().hex
    temp_path = UPLOAD_DIR / f"{uid}{ext}"
    raw_text = None

   
    contents = await file.read()
    temp_path.write_bytes(contents)

    try:
    
        if ext == ".pdf":
            raw_text = ocr_from_pdf_path(str(temp_path))

        elif ext in [".png", ".jpg", ".jpeg", ".tif", ".bmp"]:
            raw_text = ocr_from_image_bytes(contents)
 
        elif ext == ".docx":
            raw_text = fast_extract_docx(contents)
            if raw_text:
                print("DOCX: Fast python-docx extraction successful.")

        elif ext == ".doc":
            try:
                # textract-py3 handles .doc better than LibreOffice/OCR for raw text
                raw_text_bytes = textract.process(str(temp_path))
                raw_text = raw_text_bytes.decode('utf-8')
                print("DOC: textract-py3 extraction successful.")
            except Exception as e:
                print(f"DOC: textract-py3 failed ({e}). Falling through to LibreOffice.")
     
        if raw_text is None and ext in [".doc", ".docx"]:
            print("--- Running Slow LibreOffice Conversion Fallback ---")
            
            # The original contents are already saved to temp_path, but we need
            # a named temp file for the conversion input/output control.
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(contents)
                tmp_doc_path = tmp.name

            soffice = os.getenv(
                "SOFFICE_CMD",
                r"C:\Program Files\LibreOffice\program\soffice.exe"
            )
            outdir = tempfile.gettempdir()

            result = subprocess.run(
                [
                    soffice,
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", outdir,
                    tmp_doc_path
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            print("LibreOffice stdout:", result.stdout)
            print("LibreOffice stderr:", result.stderr)

            pdf_path = os.path.join(outdir, Path(tmp_doc_path).stem + ".pdf")
            os.unlink(tmp_doc_path) # Clean up the input file for soffice

            if not os.path.exists(pdf_path):
                raise HTTPException(status_code=500, detail="File conversion failed (LibreOffice)")

            raw_text = ocr_from_pdf_path(pdf_path)
            os.unlink(pdf_path) # Clean up the output PDF
            
        elif raw_text is None:
             raise HTTPException(status_code=400, detail="Unsupported file format")

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Document processing error: {e}")

    finally:
        # Clean up the original uploaded file
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    if raw_text is None:
        raise HTTPException(status_code=500, detail="Processing failed to generate text.")

    # This call now receives smaller/cleaner text and should complete faster.
    # The fix for the 60-second limit MUST be in ai_ollama.py
    ai_out = ai_extract_and_classify(raw_text) 
    doc_type = ai_out.get("doc_type", "other")

    metadata = {
        "filename": filename,
        "doc_type": doc_type,
        "created_at": datetime.utcnow().isoformat(),
    }

    pdf_bytes = generate_pdf_bytes(metadata, raw_text, ai_out)
    out_name = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{doc_type}_{uid}"
    encrypted_path = encrypt_and_save_pdf(pdf_bytes, out_name)

    db = SessionLocal()
    doc = Document(
        filename=filename,
        doc_type=doc_type,
        raw_text=raw_text,
        fields_json=json.dumps(ai_out),
        pdf_path=encrypted_path
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    db.close()

    return {
        "id": doc.id,
        "filename": filename,
        "doc_type": doc_type,
        "pdf_path": encrypted_path
    }

@app.get("/documents/")
def list_documents(limit: int = 100):
    db = SessionLocal()
    docs = db.query(Document).order_by(Document.created_at.desc()).limit(limit).all()
    db.close()

    return [
        {
            "id": d.id,
            "filename": d.filename,
            "doc_type": d.doc_type,
            "created_at": d.created_at.isoformat(),
            "locked": d.locked
        }
        for d in docs
    ]

#GET DOCUMENT FUNCTION COMMENTED OUT TO PREVENT EXPOSURE TO RAW DATA TEXT
 # @app.get("/documents/{doc_id}")
#def get_document(doc_id: int):
 #   db = SessionLocal()
  #  d = db.query(Document).get(doc_id)
   # db.close()

    #if not d:
     #   raise HTTPException(status_code=404, detail="Not found")

    #try:
     #   fields = json.loads(d.fields_json)
   # except:
    #    fields = {}

    #return {
     #   "id": d.id,
      #  "filename": d.filename,
       # "doc_type": d.doc_type,
        #"created_at": d.created_at.isoformat(),
        #"fields": fields,
        #"locked": d.locked
    #}

@app.post("/documents/{doc_id}/unlock")
def unlock_document(doc_id: int, req: PasswordRequest):
    db = SessionLocal()
    d = db.query(Document).get(doc_id)

    if not d:
        db.close()
        raise HTTPException(status_code=404, detail="Not found")

    if d.locked:
        db.close()
        return {
            "status": "locked",
            "message": "Too many wrong attempts. Document is locked."
        }

    CORRECT_PASSWORD = os.getenv("PAPERTRAIL_PASSWORD", "decryptme!")

    if req.password != CORRECT_PASSWORD:
        d.failed_attempts += 1

        if d.failed_attempts >= 3:
            d.locked = True

        db.commit()
        remaining = max(0, 3 - d.failed_attempts)
        db.close()

        return {
            "status": "error",
            "message": "Incorrect password",
            "remaining_attempts": remaining
        }

    d.failed_attempts = 0
    db.commit()
    db.close()

    return {
        "status": "success",
        "download_url": f"/documents/{doc_id}/download-decrypted"
    }

@app.get("/documents/{doc_id}/download")
def download_encrypted_pdf(doc_id: int):
    db = SessionLocal()
    d = db.query(Document).get(doc_id)
    db.close()

    if not d:
        raise HTTPException(status_code=404, detail="Not found")

    from fastapi.responses import FileResponse
    return FileResponse(
        d.pdf_path,
        media_type="application/octet-stream",
        filename=os.path.basename(d.pdf_path)
    )

@app.get("/documents/{doc_id}/download-decrypted")
def download_decrypted_pdf(doc_id: int):
    db = SessionLocal()
    d = db.query(Document).get(doc_id)

    if not d:
        db.close()
        raise HTTPException(status_code=404, detail="Not found")

    if d.locked:
        db.close()
        raise HTTPException(status_code=403, detail="Document is locked.")

    pdf_bytes = decrypt_pdf_bytes_from_path(d.pdf_path)
    db.close()

    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{d.filename}.pdf"'}
    )