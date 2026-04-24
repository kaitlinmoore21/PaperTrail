from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean # Imports the "building blocks" for database columns
from datetime import datetime # Imports the tool to handle dates and times
from database import Base # Imports the "foundation" that connects these models to your database

# This creates the "User" table (the list of people who can log in)
class User(Base):
    __tablename__ = "users" # Tells the database to name the actual table "users"

    id = Column(Integer, primary_key=True, index=True) # Gives every user a unique number (ID) so they are easy to find
    username = Column(String, unique=True, index=True, nullable=False) # Stores the username; no two people can have the same one
    email = Column(String, unique=True, index=True, nullable=True) # Stores the email; helps the database find users quickly
    password = Column(String, nullable=False) # Stores the secret password (encrypted as a scrambled code)
    employee_number_hash = Column(String, nullable=False) # Stores the secret Employee ID (also scrambled for security)
    role = Column(String, nullable=False, default="secretary") # Assigns a job title (doctor/nurse/admin); defaults to secretary

# This creates the "Document" table (the list of files uploaded to the app)
class Document(Base):
    __tablename__ = "documents" # Tells the database to name the table "documents"

    id = Column(Integer, primary_key=True, index=True) # Unique ID number for every single document
    filename = Column(String, nullable=False) # Stores the actual name of the file (e.g., "blood_test.pdf")
    doc_type = Column(String, index=True) # Stores what kind of file it is (e.g., "Medical Record" or "Insurance")
    raw_text = Column(Text) # Stores the big block of words extracted from the document
    fields_json = Column(Text) # Stores specific data found in the document (like names or dates) in a list format
    pdf_path = Column(String) # Stores the "address" of where the actual PDF file is saved on the computer
    created_at = Column(DateTime, default=datetime.utcnow) # Automatically records the exact second the document was uploaded

    failed_attempts = Column(Integer, default=0) # Counts how many times someone tried and failed to open this file
    locked = Column(Boolean, default=False) # A "Yes/No" switch; if True, no one can open the file without permission

    # This is a "Developer Tool" - it controls how the document looks when printed in the server logs
    def __repr__(self):
        # Shows the ID, filename, and lock status in a neat format for the programmer to see
        return f"<Document id={self.id} filename='{self.filename}' locked={self.locked}>"