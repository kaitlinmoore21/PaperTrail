from datetime import datetime
from utils_pdf import generate_pdf_bytes

def create_pdf_from_data(filename: str, doc_type: str, extracted_text: str, fields: dict):
    """
    Wrapper that prepares metadata and calls PDF generator.
    Returns raw (unencrypted) PDF bytes.
    """
    metadata = {
        "filename": filename,
        "doc_type": doc_type,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    pdf_bytes = generate_pdf_bytes(metadata, extracted_text, fields)
    return pdf_bytes
