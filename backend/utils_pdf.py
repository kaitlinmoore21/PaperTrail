import os
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load the variables you just provided (ensure your .env is in the backend folder)
load_dotenv()

# --- DYNAMIC PATH SETUP ---
# This ensures 'storage' is always inside your project folder on OneDrive
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")

# Ensure the folder exists on startup
os.makedirs(STORAGE_DIR, exist_ok=True)

def _get_fernet():
    """
    Uses the FERNET_KEY from your environment variables.
    """
    key = os.getenv("FERNET_KEY")
    if not key:
        raise RuntimeError("FERNET_KEY is missing from your .env file!")
    return Fernet(key.encode())

def generate_pdf_bytes(metadata: dict, raw_text: str, fields: dict) -> bytes:
    """
    Creates the PDF structure using ReportLab.
    """
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Document Header
    title = metadata.get('filename', 'Generated_Document')
    story.append(Paragraph(f"PaperTrail Processed: {title}", styles['Title']))
    story.append(Spacer(1, 12))
    
    # Extracted Data
    story.append(Paragraph("<b>Extracted Information</b>", styles['Heading2']))
    story.append(Spacer(1, 6))
    
    if fields:
        for key, value in fields.items():
            story.append(Paragraph(f"<b>{key}:</b> {value}", styles['Normal']))
    else:
        story.append(Paragraph("No specific fields extracted.", styles['Normal']))

    pdf.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def encrypt_and_save_pdf(pdf_bytes: bytes, filename: str) -> str:
    """
    Encrypts the PDF using your Fernet key and saves it to the storage folder.
    """
    # Create path: backend/storage/your_file.pdf
    full_target_path = os.path.join(STORAGE_DIR, filename)
    
    fernet = _get_fernet()
    encrypted_data = fernet.encrypt(pdf_bytes)

    with open(full_target_path, "wb") as file:
        file.write(encrypted_data)

    return full_target_path

def decrypt_pdf_bytes_from_path(path: str) -> bytes:
    """
    Reads the file from the path stored in the DB and decrypts it.
    """
    if not os.path.exists(path):
        # This will tell you exactly where it's looking if it fails
        raise FileNotFoundError(f"File not found at: {path}. Check if OneDrive moved it!")

    fernet = _get_fernet()
    with open(path, "rb") as file:
        encrypted_content = file.read()
    
    return fernet.decrypt(encrypted_content)