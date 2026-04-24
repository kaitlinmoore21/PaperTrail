import os # Imports the tool to look at your computer's settings (like finding the database location)
from sqlalchemy import create_engine # Imports the "Engine" which is the actual motor that drives the database
from sqlalchemy.orm import sessionmaker, declarative_base # Imports tools to create "sessions" (conversations with the DB) and "blueprints"

# 1. This tells the app where the database file lives. 
# It looks for a setting called DATABASE_URL, or defaults to a local file named "papertrail.db"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./papertrail.db")

# 2. This creates the "Engine." 
# Think of this as the main connection hub. 
# 'check_same_thread: False' is a special rule for SQLite that lets multiple parts of your app talk at once.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 3. This creates a "Session Factory."
# Every time a user logs in or uploads a file, we create a new "Session" (a temporary conversation) 
# to send that specific data to the engine.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# 4. This is the "Base" or the "Master Blueprint."
# All your models (User, Document) must follow this Base so the database knows they belong together.
# IMPORTANT: This must be defined here so every other file can use the same foundation.
Base = declarative_base()

# 5. This is the "Startup Button."
# When you run this function, it looks at your blueprints (Base) and 
# physically creates the tables and columns in your .db file if they don't exist yet.
def init_db():
    Base.metadata.create_all(bind=engine)