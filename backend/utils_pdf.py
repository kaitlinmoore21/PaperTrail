import os
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from cryptography.fernet import Fernet

def generate_pdf_bytes(metadata: dict, raw_text: str, fields: dict) -> bytes:
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Content generation
    story.append(Paragraph(f"Processed Document - {metadata.get('filename', '')}", styles['Title']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>Extracted Fields</b>", styles['Heading2']))
    for key, value in (fields or {}).items():
        story.append(Paragraph(f"<b>{key}:</b> {value}", styles['Normal']))

    pdf.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def _get_fernet():
    key = os.getenv("FERNET_KEY")
    if not key:
        raise RuntimeError("FERNET_KEY not set!")
    return Fernet(key.encode())

def encrypt_and_save_pdf(pdf_bytes: bytes, full_target_path: str) -> str:
    """
    Saves the encrypted file exactly where main.py tells it to.
    """
    # Create the directory (e.g., /storage/invoice) if it doesn't exist
    os.makedirs(os.path.dirname(full_target_path), exist_ok=True)
    
    fernet = _get_fernet()
    encrypted = fernet.encrypt(pdf_bytes)

    with open(full_target_path, "wb") as file:
        file.write(encrypted)

    return full_target_path

def decrypt_pdf_bytes_from_path(path: str) -> bytes:
    fernet = _get_fernet()
    with open(path, "rb") as file:
        encrypted = file.read()
    return fernet.decrypt(encrypted)