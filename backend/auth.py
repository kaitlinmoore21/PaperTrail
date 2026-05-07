import os  # Imports a tool to talk to the computer's operating system (used for secret keys)
import bcrypt  # Imports the tool used to "scramble" (hash) passwords so they can't be read
from datetime import datetime, timedelta  # Imports tools to handle dates and times (for token expiration)
from typing import Optional  # Imports a way to say "this piece of info is optional"
from fastapi import APIRouter, Depends, HTTPException, status  # Imports the core web server tools
from pydantic import BaseModel, field_validator  # Imports tools to check if the user sent the right data
from sqlalchemy.orm import Session  # Imports the connection to your database
from database import SessionLocal  # Imports your specific database setup
from models import User  # Imports your "User" blueprint (from the models file we discussed)
import jwt  # Imports the tool to create "digital ID badges" (tokens)
from passlib.context import CryptContext  # Imports another layer of password security
from fastapi.security import OAuth2PasswordBearer  # Imports the standard way to handle logins online

# BCRYPT HACK 
# This part fixes a small technical glitch in some versions of the bcrypt library
if not hasattr(bcrypt, "__about__"):
    class About:
        __version__ = getattr(bcrypt, "__version__", "4.0.1")
    bcrypt.__about__ = About()

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")  # Configures how passwords are scrambled
router = APIRouter(tags=["auth"])  # Groups all these security paths under the "Auth" label
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # Defines where the login "booth" is located

SECRET_KEY = "paper-trail-super-long-secure-key-32-chars-minimum" # A secret "master key" used to sign ID badges
ALGORITHM = "HS256"  # The math formula used to create the digital signatures
ACCESS_TOKEN_EXPIRE_MINUTES = 600  # Sets how long a user stays logged in (10 hours)

# ROLE LOGIC 
# This logic looks at an email address and decides if the user is a doctor, nurse, or admin
def get_role_from_email(email: str) -> str:
    email = email.lower()  # Converts email to lowercase so it's not case-sensitive
    if "@doctor" in email: return "doctor"  # If it has @doctor, they are a doctor
    if "@nurse" in email: return "nurse"  # If it has @nurse, they are a nurse
    if "@admin" in email: return "admin"  # If it has @admin, they are an admin
    return "secretary"  # Everyone else is a secretary by default

# This defines the "Application Form" for joining the app
class SignupRequest(BaseModel):
    email: str  # Requires an email string
    password: str  # Requires a password string
    employee_number: str  # Requires an employee number string

    # This part double-checks the employee number before the server even tries to save it
    @field_validator('employee_number')
    def validate_number(cls, v):
        if not v.isdigit() or len(v) < 4:  # If it's not all numbers or is too short
            raise ValueError('Employee number must be at least 4 digits')  # Reject the form
        return v

# This defines what is needed to "Sign In"
class LoginRequest(BaseModel):
    email: str  # Need the email
    password: str  # Need the password
    employee_number: str  # Now also needs the Employee ID to log in

# This defines what the server sends back after a successful login
class TokenResponse(BaseModel):
    access_token: str  # The digital "ID badge"
    token_type: str = "bearer"  # Says "this is a standard badge"
    role: str  # Tells the app if the user is a doctor, nurse, etc.

# This sets up a temporary connection to the database
def get_db():
    db = SessionLocal()  # Opens the database door
    try: yield db  # Hands the connection to the function that needs it
    finally: db.close()  # Closes the door when finished to save memory

# This compares a typed password with the scrambled one in the database
def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# This turns a plain password into a scrambled code (hash) for safe storage
def get_password_hash(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# This creates the digital "ID badge" (token) that the user keeps in their phone
def create_access_token(data: dict):
    to_encode = data.copy()  # Makes a copy of the user's info
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # Sets the expiration time
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})  # Adds "expires at" and "created at" timestamps
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Signs the badge with the master key

# THE SIGNUP DOOR 
@router.post("/signup/")
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    # Check if someone is already using that email
    existing = db.query(User).filter(User.email == req.email).first()
    if existing: 
        raise HTTPException(status_code=400, detail="Email already registered") # Stop if email is taken
    
    role = get_role_from_email(req.email) # Decide the user's role based on their email
    
    # Create the new user record
    user = User(
        username=req.email, # Uses email as the username
        email=req.email,
        password=get_password_hash(req.password), # Scramble and save the password
        employee_number_hash=get_password_hash(req.employee_number), # Scramble and save the ID number
        role=role
    )
    db.add(user) # Put the new user in the "waiting area"
    db.commit() # Permanently save the user to the database
    db.refresh(user) # Refresh the data to get the new ID number assigned by the database
    return {"id": user.id, "email": user.email, "role": user.role, "status": "created"} # Tell the user it worked

# THE LOGIN DOOR 
@router.post("/login/", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    # Find the user in the database by their email
    user = db.query(User).filter(User.email == req.email).first()
    
    # Step 1: Does the user even exist?
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials") # Stop if email isn't found

    # Step 2: Does the password match the scrambled one we have?
    is_pw_valid = verify_password(req.password, user.password)
    
    # Step 3: Does the Employee ID match the scrambled one we have?
    is_emp_num_valid = verify_password(req.employee_number, user.employee_number_hash)

    # If EITHER the password or the ID is wrong, reject the login
    if not is_pw_valid or not is_emp_num_valid:
        raise HTTPException(status_code=401, detail="Invalid credentials") # Generic error for security

    # If everything is correct, create a digital "ID badge"
    token = create_access_token({"sub": user.email, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "role": user.role} # Give the badge to the user
