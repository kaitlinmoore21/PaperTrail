import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
import jwt

try:
    from passlib.context import CryptContext
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception:
    pwd_ctx = None

router = APIRouter(prefix="/auth", tags=["auth"])

# Config via env
INSECURE = os.getenv("INSECURE_AUTH", "0") == "1"
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Request/response models
class SignupRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: Optional[str] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain, hashed):
    if INSECURE:
        # insecure compare: plaintext equality
        return plain == hashed
    else:
        if not pwd_ctx:
            raise RuntimeError("passlib required for secure mode")
        return pwd_ctx.verify(plain, hashed)

def get_password_hash(password):
    if INSECURE:
        # insecure: store plaintext (DEMO ONLY)
        return password
    else:
        if not pwd_ctx:
            raise RuntimeError("passlib required for secure mode")
        return pwd_ctx.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    now = datetime.utcnow()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": now})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token, expire.isoformat()

@router.post("/signup", response_model=dict)
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    # check existing
    existing = db.query(User).filter((User.username == req.username) | (User.email == req.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="username or email already exists")
    user = User(username=req.username, email=req.email, password=get_password_hash(req.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username}

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(req.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Build token payload
    token_payload = {"sub": user.username, "user_id": user.id}
    token, expires_at = create_access_token(token_payload)
    return {"access_token": token, "expires_at": expires_at}
