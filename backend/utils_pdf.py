import os
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from cryptography.fernet import Fernet

# Directory where encrypted PDFs are stored
STORAGE_DIR = os.getenv("STORAGE_DIR", "storage")
os.makedirs(STORAGE_DIR, exist_ok=True)


# ---------------------------------------------------------------------
#                 PDF GENERATION (UNENCRYPTED BYTES)
# ---------------------------------------------------------------------
def generate_pdf_bytes(metadata: dict, raw_text: str, fields: dict) -> bytes:
    """
    Creates a PDF in memory and returns the raw (unencrypted) PDF bytes.

    metadata: {
        filename: original file name,
        doc_type: invoice/email/etc,
        created_at: timestamp string
    }

    fields: dict of AI-extracted structured fields.
    raw_text: OCR text.
    """
    buffer = BytesIO()
    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    story = []

    # Title
    title = f"Processed Document - {metadata.get('filename', '')}"
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 12))

    # Metadata Section
    meta_lines = [
        f"<b>Document Type:</b> {metadata.get('doc_type', '')}",
        f"<b>Filename:</b> {metadata.get('filename', '')}",
        f"<b>Processed:</b> {metadata.get('created_at', '')}",
    ]
    for line in meta_lines:
        story.append(Paragraph(line, styles['Normal']))
    story.append(Spacer(1, 12))

    # Extracted Fields
    story.append(Paragraph("<b>Extracted Fields</b>", styles['Heading2']))
    for key, value in (fields or {}).items():
        story.append(Paragraph(f"<b>{key}:</b> {value}", styles['Normal']))
    story.append(Spacer(1, 12))

    # OCR Text
    story.append(Paragraph("<b>Raw OCR Text</b>", styles['Heading2']))
    for block in raw_text.split("\n\n"):
        block = block.strip()
        if block:
            story.append(Paragraph(block.replace("\n", "<br/>"), styles['Normal']))
            story.append(Spacer(1, 6))

    # Build PDF
    pdf.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


# ---------------------------------------------------------------------
#              ENCRYPTION USING A SHARED PASSWORD KEY
# ---------------------------------------------------------------------
def _get_fernet():
    """
    Returns a Fernet instance using a shared key.

    Uses PDF_PASSWORD from environment.
    If missing, generates a temporary session key.
    """
    key = os.getenv("PDF_PASSWORD")

    if not key:
        # Not for production; ensures encryption always works.
        temp_key = Fernet.generate_key()
        os.environ["PDF_PASSWORD"] = temp_key.decode()
        key = temp_key.decode()

    return Fernet(key.encode())


# ---------------------------------------------------------------------
#                         ENCRYPT + SAVE PDF
# ---------------------------------------------------------------------
def encrypt_and_save_pdf(pdf_bytes: bytes, target_name: str) -> str:
    """
    Encrypts PDF bytes and saves:

        storage/<target_name>.pdf.enc

    Returns: full file path as string.
    """
    fernet = _get_fernet()
    encrypted = fernet.encrypt(pdf_bytes)

    filename = f"{target_name}.pdf.enc"
    path = os.path.join(STORAGE_DIR, filename)

    with open(path, "wb") as file:
        file.write(encrypted)

    return path


# ---------------------------------------------------------------------
#                         DECRYPT PDF BYTES
# ---------------------------------------------------------------------
def decrypt_pdf_bytes_from_path(path: str) -> bytes:
    """
    Reads an encrypted PDF from disk and returns decrypted bytes.
    """
    fernet = _get_fernet()

    with open(path, "rb") as file:
        encrypted = file.read()

    return fernet.decrypt(encrypted)