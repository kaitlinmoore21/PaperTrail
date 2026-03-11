import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
import jwt
from passlib.context import CryptContext

# Bcrypt handles salting automatically
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

# No prefix, so it matches /signup/ and /login/ exactly
router = APIRouter(tags=["auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "hc-paper-trail-99-key") 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# --- MODELS ADJUSTED FOR FRONTEND JSON ---
class SignupRequest(BaseModel):
    email: str             # Frontend sends 'email'
    password: str          # Frontend sends 'password'
    username: Optional[str] = None # Make this optional to avoid 422 errors

class LoginRequest(BaseModel):
    email: str             # Changed from username to email to match frontend
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

# --- Security Helpers ---
def verify_password(plain_password, hashed_password):
    return pwd_ctx.verify(plain_password, hashed_password)

def get_password_hash(password):
    # Passlib can sometimes get confused with plain strings on newer Python versions
    # We ensure it's handled properly by the context
    return pwd_ctx.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- Routes ---

@router.post("/signup/")
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    # Check if email is already taken
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = get_password_hash(req.password)
    
    # Use email as username if frontend didn't provide a specific username
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
    # Look up by email since that's what your frontend is sending
    user = db.query(User).filter(User.email == req.email).first()
    
    if not user or not verify_password(req.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_payload = {"sub": user.email, "user_id": user.id}
    token = create_access_token(token_payload)
    
    return {"access_token": token, "token_type": "bearer"}