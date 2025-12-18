# Navigate to the Backend Directory
 cd C:\PaperTrail\backend

# Create Virtual Environment (powershell)
 cd C:\PaperTrail\backend

# Activate Virtual Enviroment (powershell)
.\.venv\Scripts\Activate.ps1

# The FastAPI Server (install required package)
 pip install fastapi uvicorn

# Run the FastAPI Server
uvicorn main:app --reload
 
# Open API Documentation
Swagger UI:  http://127.0.0.1:8000/docs

# Decrypt Document Password
decryptme!