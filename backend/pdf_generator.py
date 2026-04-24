from datetime import datetime # Imports the tool to check the current date and time
from utils_pdf import generate_pdf_bytes # Imports the specific tool that builds the actual PDF file

# This function organizes the data so it's ready to be turned into a PDF document
def create_pdf_from_data(filename: str, doc_type: str, extracted_text: str, fields: dict):
    """
    Wrapper that prepares metadata and calls PDF generator.
    Returns raw (unencrypted) PDF bytes.
    """
    
    # 1. This creates a "Metadata" dictionary—like a digital sticker on a file folder.
    # It stores the name, what kind of document it is, and exactly when this happened.
    metadata = {
        "filename": filename, # Saves the original name of the file (e.g., "Report.jpg")
        "doc_type": doc_type, # Saves the category found by the AI (e.g., "Prescription")
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # Records the date and time in a readable format
    }

    # 2. This line sends three things to the PDF generator:
    # - The "Sticker" (metadata)
    # - The raw words found on the page (extracted_text)
    # - The specific facts the AI found, like prices or dates (fields)
    pdf_bytes = generate_pdf_bytes(metadata, extracted_text, fields)

    # 3. This gives back the "Raw PDF" data (not a file yet, just the digital code for one)
    return pdf_bytes