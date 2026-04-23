import os
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

# --- BCRYPT HACK ---
if not hasattr(bcrypt, "__about__"):
    class About:
        __version__ = getattr(bcrypt, "__version__", "4.0.1")
    bcrypt.__about__ = About()

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = os.getenv("SECRET_KEY", "hc-paper-trail-99-key") 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 600 # Long duration for dev

# --- ROLE LOGIC ---
def get_role_from_email(email: str) -> str:
    email = email.lower()
    if "@doctor" in email: return "doctor"
    if "@nurse" in email: return "nurse"
    if "@admin" in email: return "admin"
    return "secretary"

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
    role: str

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/signup/")
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing: raise HTTPException(status_code=400, detail="Email already registered")
    
    role = get_role_from_email(req.email)
    user = User(
        username=req.username or req.email,
        email=req.email,
        password=get_password_hash(req.password),
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email, "role": user.role, "status": "created"}

@router.post("/login/", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.email, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "role": user.role}