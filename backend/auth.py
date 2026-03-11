import os
import bcrypt # Import bcrypt directly to fix the passlib bug
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
import jwt
from passlib.context import CryptContext

# --- THE BCRYPT HACK FOR PYTHON 3.14 ---
# Passlib looks for bcrypt.__about__.__version__, which is gone in newer bcrypt.
# We manually inject it here so Passlib stops crashing.
if not hasattr(bcrypt, "__about__"):
    class About:
        __version__ = getattr(bcrypt, "__version__", "4.0.1")
    bcrypt.__about__ = About()

# Now we can safely define the context
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(tags=["auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "hc-paper-trail-99-key") 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# --- MODELS ---
class SignupRequest(BaseModel):
    email: str 
    password: str 
    username: Optional[str] = None

class LoginRequest(BaseModel):
    email: str 
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- SECURITY HELPERS ---
def verify_password(plain_password: str, hashed_password: str):
    # Convert strings to bytes for the bcrypt library
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    # This direct call bypasses the Passlib version check bug
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def get_password_hash(password: str):
    # Convert string to bytes
    password_bytes = password.encode('utf-8')
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    # Return as a string to store in the database
    return hashed_bytes.decode('utf-8')

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- ROUTES ---

@router.post("/signup/")
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = get_password_hash(req.password)
    
    db_username = req.username if req.username else req.email
    
    user = User(
        username=db_username,
        email=req.email,
        password=hashed_pwd
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email, "status": "created"}

@router.post("/login/", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    
    if not user or not verify_password(req.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_payload = {"sub": user.email, "user_id": user.id}
    token = create_access_token(token_payload)
    
    return {"access_token": token, "token_type": "bearer"}