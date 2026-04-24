import os # Imports the tool to handle folders and file paths on your computer
from io import BytesIO # Imports a "virtual folder" in the computer's memory (very fast)
from datetime import datetime # Imports tools to handle dates
from reportlab.lib.pagesizes import A4 # Imports standard paper size (A4)
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer # Imports tools to build the PDF layout
from reportlab.lib.styles import getSampleStyleSheet # Imports pre-made fonts and styles
from cryptography.fernet import Fernet # Imports the "Lock and Key" system for encryption
from dotenv import load_dotenv # Imports the tool to read your secret keys from the .env file

# Load settings from your .env file
load_dotenv()

# --- DYNAMIC PATH SETUP ---
# This finds exactly where this script is sitting on your computer
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# This creates a path for a folder called "storage" inside your project
STORAGE_DIR = os.path.join(BASE_DIR, "storage")

# This physically creates the "storage" folder on your hard drive if it isn't there yet
os.makedirs(STORAGE_DIR, exist_ok=True)

# This helper function gets your secret encryption key ready
def _get_fernet():
    """
    Uses the FERNET_KEY from your environment variables.
    """
    key = os.getenv("FERNET_KEY") # Looks for the secret key in your .env file
    if not key:
        # If the key is missing, the app stops and warns you
        raise RuntimeError("FERNET_KEY is missing from your .env file!")
    return Fernet(key.encode()) # Turns the text key into a working "Lock"

# This function builds the actual PDF document
def generate_pdf_bytes(metadata: dict, raw_text: str, fields: dict) -> bytes:
    """
    Creates the PDF structure using ReportLab.
    """
    buffer = BytesIO() # Starts a "virtual file" in memory instead of saving to disk yet
    pdf = SimpleDocTemplate(buffer, pagesize=A4) # Sets up the PDF "canvas"
    styles = getSampleStyleSheet() # Gets a list of text styles (Bold, Title, etc.)
    story = [] # This is the "List of Content" we will put on the page

    # Document Header: Adds the title to the top of the page
    title = metadata.get('filename', 'Generated_Document')
    story.append(Paragraph(f"PaperTrail Processed: {title}", styles['Title']))
    story.append(Spacer(1, 12)) # Adds a small gap
    
    # Extracted Data: Adds a section for the information the AI found
    story.append(Paragraph("<b>Extracted Information</b>", styles['Heading2']))
    story.append(Spacer(1, 6))
    
    # This loops through every piece of data (Price, Date, etc.) and lists it
    if fields:
        for key, value in fields.items():
            story.append(Paragraph(f"<b>{key}:</b> {value}", styles['Normal']))
    else:
        story.append(Paragraph("No specific fields extracted.", styles['Normal']))

    pdf.build(story) # This "flattens" everything onto the digital page
    pdf_bytes = buffer.getvalue() # Gets the final digital data of the PDF
    buffer.close() # Cleans up the memory
    return pdf_bytes # Returns the unencrypted PDF data

# This function locks the PDF and saves it to your folder
def encrypt_and_save_pdf(pdf_bytes: bytes, filename: str) -> str:
    """
    Encrypts the PDF using your Fernet key and saves it to the storage folder.
    """
    # Combines the folder path and filename (e.g., C:/Project/storage/my_file.pdf)
    full_target_path = os.path.join(STORAGE_DIR, filename)
    
    fernet = _get_fernet() # Gets our secret "Lock"
    encrypted_data = fernet.encrypt(pdf_bytes) # Scrambles the PDF data so it's unreadable

    # This opens a file on your computer and writes the scrambled data into it
    with open(full_target_path, "wb") as file:
        file.write(encrypted_data)

    return full_target_path # Tells the app where the file was saved

# This function unlocks a file so a Doctor can view it
def decrypt_pdf_bytes_from_path(path: str) -> bytes:
    """
    Reads the file from the path stored in the DB and decrypts it.
    """
    # Checks if the file actually exists where the database says it is
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found at: {path}. Check if OneDrive moved it!")

    fernet = _get_fernet() # Gets the secret "Key"
    with open(path, "rb") as file:
        encrypted_content = file.read() # Reads the scrambled data from the disk
    
    # Unscrambles the data and returns the original PDF bytes
    return fernet.decrypt(encrypted_content)