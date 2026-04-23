import os, io, uuid, json, tempfile, subprocess, traceback
from pathlib import Path
from datetime import datetime
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from docx import Document as DocxDocument
import textract 
from dotenv import load_dotenv
from urllib.parse import unquote
from sqlalchemy.orm import Session
from jose import jwt, JWTError

# Database and Local Logic
from database import SessionLocal, init_db
from models import Document, User
from utils_pdf import generate_pdf_bytes, encrypt_and_save_pdf, decrypt_pdf_bytes_from_path
from ai_ollama import ai_extract_and_classify
from auth import router as auth_router, SECRET_KEY, ALGORITHM 

load_dotenv()

# --- SECURITY CONFIG ---
# This tells FastAPI where to look for the "Login" token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

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

init_db()
app.include_router(auth_router)

class PasswordRequest(BaseModel):
    password: str

# --- DEPENDENCIES & SECURITY GUARDS ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Decodes the JWT token sent from the mobile app to identify 
    who is logged in and what their role is.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def require_roles(allowed_roles: List[str]):
    """
    The 'Bouncer' function. Checks the current user's role against 
    the list of roles allowed for a specific action.
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access Denied: Required role {allowed_roles}. You are a {current_user.role}."
            )
        return current_user
    return role_checker

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
async def upload_and_process(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    # LEVEL 0: Any logged in user (Secretary, Nurse, Doctor, Admin) can upload
    current_user: User = Depends(get_current_user) 
):
    filename = unquote(file.filename or "upload")
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
        
        if raw_text is None:
             raise HTTPException(status_code=400, detail="Unsupported file format")

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Document error: {e}")
    finally:
        if os.path.exists(temp_path): os.unlink(temp_path)

    # AI Process
    ai_out = ai_extract_and_classify(raw_text) 
    doc_type = ai_out.get("doc_type", "other")
    
    metadata = {"filename": filename, "doc_type": doc_type, "created_at": datetime.utcnow().isoformat()}
    pdf_bytes = generate_pdf_bytes(metadata, raw_text, ai_out)
    
    safe_doc_type = "".join(char for char in doc_type if char.isalnum())
    file_id = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{safe_doc_type}_{uid}.pdf"
    full_save_path = str((ENCRYPTED_DIR / file_id).absolute()) 
    encrypted_path = encrypt_and_save_pdf(pdf_bytes, full_save_path)

    doc = Document(
        filename=filename, 
        doc_type=doc_type, 
        raw_text=raw_text, 
        fields_json=json.dumps(ai_out, ensure_ascii=False), 
        pdf_path=encrypted_path
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    db.close()

    return {"id": doc.id, "filename": filename, "doc_type": doc_type}

@app.get("/documents/")
def get_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List documents for all registered users."""
    docs = db.query(Document).all()
    results = [{"id": d.id, "filename": d.filename, "created_at": d.created_at.strftime("%d/%m/%Y"), "doc_type": d.doc_type} for d in docs]
    return results

@app.get("/documents/{doc_id}/details")
def get_document_details(
    doc_id: int, 
    db: Session = Depends(get_db),
    # LEVEL 1: Secretary is EXCLUDED. Only Medical Staff/Admin can see AI details.
    current_user: User = Depends(require_roles(["doctor", "nurse", "admin"]))
):
    d = db.query(Document).filter(Document.id == doc_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        extracted_data_object = json.loads(d.fields_json) if d.fields_json else {}
    except:
        extracted_data_object = {"error": "Could not parse data"}
    
    return {
        "id": d.id,
        "filename": d.filename,
        "doc_type": d.doc_type,
        "extracted_data": extracted_data_object 
    }

@app.get("/documents/{doc_id}/download-decrypted")
def download_decrypted_pdf(
    doc_id: int, 
    db: Session = Depends(get_db),
    # LEVEL 2: High security. Only Doctor or Admin can actually download the file.
    current_user: User = Depends(require_roles(["doctor", "admin"]))
):
    d = db.query(Document).get(doc_id)
    if not d or d.locked:
        raise HTTPException(status_code=403, detail="Document locked or unavailable")

    pdf_bytes = decrypt_pdf_bytes_from_path(d.pdf_path)
    return StreamingResponse(
        io.BytesIO(pdf_bytes), 
        media_type="application/pdf", 
        headers={"Content-Disposition": f'attachment; filename="{d.filename}.pdf"'}
    )

@app.post("/documents/{doc_id}/unlock")
def unlock_document(
    doc_id: int, 
    req: PasswordRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["doctor", "admin"]))
):
    d = db.query(Document).get(doc_id)
    if not d: raise HTTPException(status_code=404)
    
    CORRECT_PASSWORD = os.getenv("PAPERTRAIL_PASSWORD", "decryptme!")
    if req.password != CORRECT_PASSWORD:
        d.failed_attempts += 1
        if d.failed_attempts >= 3: d.locked = True
        db.commit()
        return {"status": "error", "message": "Incorrect password"}
    
    d.failed_attempts = 0
    db.commit()
    return {"status": "success", "download_url": f"/documents/{doc_id}/download-decrypted"}