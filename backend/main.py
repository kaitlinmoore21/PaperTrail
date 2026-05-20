import os, io, uuid, json, tempfile, subprocess, traceback # Imports basic tools for files, IDs, and error tracking
from pathlib import Path # Imports a modern way to handle folder paths (C:/PaperTrail/...)
from datetime import datetime # Imports time tools to timestamp document uploads
from typing import List # Imports a tool to list multiple items (like a list of allowed roles)
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status # Imports the web server core
from fastapi.middleware.cors import CORSMiddleware # Imports the tool that lets your Mobile App talk to the Server
from fastapi.responses import FileResponse, StreamingResponse # Imports ways to send files back to the user
from fastapi.security import OAuth2PasswordBearer # Imports the standard "Login Token" handler
from pydantic import BaseModel # Imports the tool to define how "Data Packages" (JSON) should look
from pdf2image import convert_from_path # Imports the tool to turn PDF pages into images for scanning
from PIL import Image # Imports the tool to open and process images
import pytesseract # Imports the "OCR" engine (the brain that reads text from pictures)
from docx import Document as DocxDocument # Imports the tool to read Word files (.docx)
import textract # Imports a universal tool to pull text from many different file types
from dotenv import load_dotenv # Imports the tool that reads your secret .env file
from urllib.parse import unquote # Imports a tool to clean up messy filenames with spaces or symbols
from sqlalchemy.orm import Session # Imports the connection to your database


import jwt
from jwt.exceptions import InvalidTokenError as JWTError 

from database import SessionLocal, init_db # Imports your database setup
from models import Document, User # Imports your data blueprints (Users and Documents)
from utils_pdf import generate_pdf_bytes, encrypt_and_save_pdf, decrypt_pdf_bytes_from_path # Imports your PDF security tools
from ai_ollama import ai_extract_and_classify # Imports your AI "Brain" function
from auth import router as auth_router, SECRET_KEY, ALGORITHM # Imports your login system and secret keys

load_dotenv() # Reads .env file to get your secret passwords and settings

#  SECURITY CONFIG 
# This defines the "Login Booth" address where the mobile app gets its digital ID badge
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#  TESSERACT CONFIG 
# Tells the app where the OCR scanning software is installed on the computer
TESSERACT_CMD = os.getenv("TESSERACT_CMD")
if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

#  STORAGE CONFIG 
# Creates folders on your computer to store uploaded files and the final encrypted versions
UPLOAD_DIR = Path("C:/PaperTrail/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True) # Creates the "uploads" folder if it doesn't exist
ENCRYPTED_DIR = Path("C:/PaperTrail/storage") 
ENCRYPTED_DIR.mkdir(parents=True, exist_ok=True) # Creates the "secure storage" folder

app = FastAPI(title="PaperTrail Backend") # Initializes the main web application

# This allows your mobile app to talk to this server even if they are on different networks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows any device to connect (for development)
    allow_methods=["*"], # Allows all types of requests (GET, POST, etc.)
    allow_headers=["*"], # Allows all types of data headers
)

init_db() # Runs the command to build the database tables if they aren't there yet
app.include_router(auth_router) # Plugs in the Login/Signup logic from your auth.py file

# A simple rule for when a user needs to send a password to unlock a file
class PasswordRequest(BaseModel):
    password: str

# DEPENDENCIES & SECURITY GUARDS 

# Opens a temporary conversation with the database
def get_db():
    db = SessionLocal()
    try:
        yield db # Hands the connection to the function that asked for it
    finally:
        db.close() # Closes the connection to save computer memory

# The "ID Scanner": Decodes the digital token sent by the mobile app to see who the user is
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Tries to unlock the "Digital ID badge" using your secret master key
        # using PyJWT to decode
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub") # Extracts the user's email from the badge
        if email is None: raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # Looks up the user in the database to make sure they are real
    user = db.query(User).filter(User.email == email).first()
    if user is None: raise credentials_exception
    return user # Returns the full User object (including their name and role)

# The "Bouncer": Checks if a user's job (role) allows them to enter a specific area
def require_roles(allowed_roles: List[str]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            # If a Secretary tries to enter a Doctor-only area, they are kicked out
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access Denied: You are a {current_user.role}."
            )
        return current_user
    return role_checker

# OCR HELPERS (The Scanners) 

# Reads text from Word documents (.docx)
def fast_extract_docx(contents: bytes) -> str | None:
    try:
        doc = DocxDocument(io.BytesIO(contents))
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception: return None

# Reads text from standard images (JPG, PNG)
def ocr_from_image_bytes(contents: bytes) -> str:
    img = Image.open(io.BytesIO(contents)).convert("RGB")
    return pytesseract.image_to_string(img) # Uses Tesseract to "see" the words

# Reads text from PDF files by turning every page into an image first
def ocr_from_pdf_path(pdf_path: str) -> str:
    pages = convert_from_path(pdf_path)
    text_blocks = [pytesseract.image_to_string(pg) for pg in pages]
    return "\n".join(text_blocks)

@app.get("/")
def root():
    return {"message": "PaperTrail API Running"} # A simple "I'm alive" message for testing

# DOCUMENT ROUTES (The Main Actions) 

# 1. UPLOAD: The door where documents enter the system
@app.post("/upload/")
async def upload_and_process(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Only logged-in people can upload
):
    filename = unquote(file.filename or "upload") # Cleans up the name of the file
    ext = Path(filename).suffix.lower() # Gets the file extension (.pdf, .jpg, etc.)
    uid = uuid.uuid4().hex # Generates a random "Unique ID" to prevent filename confusion
    temp_path = UPLOAD_DIR / f"{uid}{ext}" # Creates a temporary home for the file
    raw_text = None

    contents = await file.read() # Reads the file data sent from the mobile app
    temp_path.write_bytes(contents) # Saves it to the computer temporarily

    try:
        # Choose the right "Scanner" based on the file type
        if ext == ".pdf": raw_text = ocr_from_pdf_path(str(temp_path))
        elif ext in [".png", ".jpg", ".jpeg"]: raw_text = ocr_from_image_bytes(contents)
        elif ext == ".docx": raw_text = fast_extract_docx(contents)
        
        if raw_text is None: raise HTTPException(status_code=400, detail="Unsupported file format")

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Document error: {e}")
    finally:
        if os.path.exists(temp_path): os.unlink(temp_path) # Deletes the temporary unencrypted file

    # AI STEP 
    ai_out = ai_extract_and_classify(raw_text) # Asks the AI "Brain" to find facts and classify the doc
    doc_type = ai_out.get("doc_type", "other")
    
    # PDF GENERATION & SECURITY
    metadata = {"filename": filename, "doc_type": doc_type, "created_at": datetime.now().isoformat()}
    pdf_bytes = generate_pdf_bytes(metadata, raw_text, ai_out) # Creates a clean PDF with the AI's findings
    
    file_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uid}.pdf" # Creates a unique filename
    full_save_path = str((ENCRYPTED_DIR / file_id).absolute()) 
    encrypted_path = encrypt_and_save_pdf(pdf_bytes, full_save_path) # Encrypts the file so it's unreadable without a key

    # DATABASE RECORD 
    doc = Document(
        filename=filename, 
        doc_type=doc_type, 
        raw_text=raw_text, 
        fields_json=json.dumps(ai_out, ensure_ascii=False), # Saves AI details as a JSON string
        pdf_path=encrypted_path # Saves the location of the encrypted file
    )
    db.add(doc)
    db.commit() # Saves everything to the database
    db.refresh(doc)

    return {"id": doc.id, "filename": filename, "doc_type": doc_type}

# 2. LIST: Shows all files in the system to any logged-in user
@app.get("/documents/")
def get_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    docs = db.query(Document).all() # Fetches every document record
    return [{"id": d.id, "filename": d.filename, "created_at": d.created_at.strftime("%d/%m/%Y"), "doc_type": d.doc_type} for d in docs]

# 3. DETAILS: Shows the AI findings (Doctor/Nurse/Admin ONLY)
@app.get("/documents/{doc_id}/details")
def get_document_details(
    doc_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["doctor", "nurse", "admin"])) # SECRETARY IS EXCLUDED HERE
):
    d = db.query(Document).filter(Document.id == doc_id).first()
    if not d: raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": d.id,
        "filename": d.filename,
        "doc_type": d.doc_type,
        "extracted_data": json.loads(d.fields_json) if d.fields_json else {} 
    }

# 4. DOWNLOAD: The most secure part. Only Doctors or Admins can download the actual PDF.
@app.get("/documents/{doc_id}/download-decrypted")
def download_decrypted_pdf(
    doc_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["doctor", "admin"])) # NURSES/SECRETARIES EXCLUDED
):
    d = db.query(Document).get(doc_id)
    if not d or d.locked: raise HTTPException(status_code=403, detail="Document locked or unavailable")

    pdf_bytes = decrypt_pdf_bytes_from_path(d.pdf_path) # Decrypts the file in memory only
    return StreamingResponse(
        io.BytesIO(pdf_bytes), 
        media_type="application/pdf", 
        headers={"Content-Disposition": f'attachment; filename="{d.filename}.pdf"'}
    )

# 5. UNLOCK: Allows a Doctor to clear a "Lock" if someone typed the password wrong too many times
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
        d.failed_attempts += 1 # Increments "Strikes"
        if d.failed_attempts >= 3: d.locked = True # Locks the file if they fail 3 times
        db.commit()
        return {"status": "error", "message": "Incorrect password"}
    
    d.failed_attempts = 0 # Resets the strikes on success
    db.commit()
    return {"status": "success", "download_url": f"/documents/{doc_id}/download-decrypted"}
