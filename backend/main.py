import os, io, uuid, json, tempfile, subprocess, traceback
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from docx import Document as DocxDocument
import textract 
from dotenv import load_dotenv

# Database and Local Logic
from database import SessionLocal, init_db
from models import Document
from utils_pdf import generate_pdf_bytes, encrypt_and_save_pdf, decrypt_pdf_bytes_from_path
from ai_ollama import ai_extract_and_classify
from auth import router as auth_router # Import our new auth router

load_dotenv()

# --- TESSERACT CONFIG ---
TESSERACT_CMD = os.getenv("TESSERACT_CMD")
if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# --- STORAGE CONFIG ---
UPLOAD_DIR = Path("C:/PaperTrail/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ENCRYPTED_DIR = Path("C:/PaperTrail/storage") 
ENCRYPTED_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="PaperTrail Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB and Include Auth
init_db()
app.include_router(auth_router)

class PasswordRequest(BaseModel):
    password: str

# --- OCR HELPERS ---
def fast_extract_docx(contents: bytes) -> str | None:
    try:
        doc = DocxDocument(io.BytesIO(contents))
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception: return None

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

# --- DOCUMENT ROUTES ---
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
        elif ext == ".doc":
            try:
                raw_text_bytes = textract.process(str(temp_path))
                raw_text = raw_text_bytes.decode('utf-8')
            except Exception: pass
        
        if raw_text is None and ext in [".doc", ".docx"]:
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(contents)
                tmp_doc_path = tmp.name
            soffice = os.getenv("SOFFICE_CMD", r"C:\Program Files\LibreOffice\program\soffice.exe")
            outdir = tempfile.gettempdir()
            subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", outdir, tmp_doc_path])
            pdf_path = os.path.join(outdir, Path(tmp_doc_path).stem + ".pdf")
            os.unlink(tmp_doc_path)
            if os.path.exists(pdf_path):
                raw_text = ocr_from_pdf_path(pdf_path)
                os.unlink(pdf_path)

        if raw_text is None:
             raise HTTPException(status_code=400, detail="Unsupported file format")

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Document error: {e}")
    finally:
        if os.path.exists(temp_path): os.unlink(temp_path)

    ai_out = ai_extract_and_classify(raw_text) 
    doc_type = ai_out.get("doc_type", "other")
    
    metadata = {"filename": filename, "doc_type": doc_type, "created_at": datetime.utcnow().isoformat()}
    pdf_bytes = generate_pdf_bytes(metadata, raw_text, ai_out)
    file_id = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{doc_type}_{uid}.pdf"
    full_save_path = str((ENCRYPTED_DIR / file_id).absolute()) 
    encrypted_path = encrypt_and_save_pdf(pdf_bytes, full_save_path)

    db = SessionLocal()
    doc = Document(filename=filename, doc_type=doc_type, raw_text=raw_text, fields_json=json.dumps(ai_out), pdf_path=encrypted_path)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    db.close()

    return {"id": doc.id, "filename": filename, "doc_type": doc_type}

@app.get("/documents/")
def get_documents():
    db = SessionLocal()
    docs = db.query(Document).all()
    results = [{"id": d.id, "filename": d.filename, "created_at": d.created_at.strftime("%d/%m/%Y"), "doc_type": d.doc_type} for d in docs]
    db.close()
    return results

@app.get("/documents/{doc_id}")
def get_document(doc_id: int):
    db = SessionLocal()
    d = db.query(Document).get(doc_id)
    db.close()
    if not d: raise HTTPException(status_code=404)
    return {"id": d.id, "filename": d.filename, "doc_type": d.doc_type, "created_at": d.created_at.isoformat(), "fields": json.loads(d.fields_json), "locked": d.locked}

@app.post("/documents/{doc_id}/unlock")
def unlock_document(doc_id: int, req: PasswordRequest):
    db = SessionLocal()
    d = db.query(Document).get(doc_id)
    if not d: 
        db.close()
        raise HTTPException(status_code=404)
    
    CORRECT_PASSWORD = os.getenv("PAPERTRAIL_PASSWORD", "decryptme!")
    if req.password != CORRECT_PASSWORD:
        d.failed_attempts += 1
        if d.failed_attempts >= 3: d.locked = True
        db.commit()
        db.close()
        return {"status": "error", "message": "Incorrect password"}
    
    d.failed_attempts = 0
    db.commit()
    db.close()
    return {"status": "success", "download_url": f"/documents/{doc_id}/download-decrypted"}

@app.get("/documents/{doc_id}/download-decrypted")
def download_decrypted_pdf(doc_id: int):
    db = SessionLocal()
    d = db.query(Document).get(doc_id)
    if not d or d.locked:
        db.close()
        raise HTTPException(status_code=403)
    pdf_bytes = decrypt_pdf_bytes_from_path(d.pdf_path)
    db.close()
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{d.filename}.pdf"'})

# --- NEW: VIEW IN APP FEATURE ---
@app.get("/documents/{doc_id}/details")
def get_document_details(doc_id: int):
    """
    Retrieves the extracted JSON data for the mobile app's 'View In-App' modal.
    """
    db = SessionLocal()
    d = db.query(Document).filter(Document.id == doc_id).first()
    db.close()
    if not d:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": d.id,
        "filename": d.filename,
        "doc_type": d.doc_type,
        "extracted_data": json.loads(d.fields_json) if d.fields_json else {}
    }