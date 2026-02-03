# Navigate to the Backend Directory
 cd "C:\Users\kkmoo\OneDrive - National College of Ireland\YEAR4\Final Project\PaperTrail\backend"


# Create Virtual Environment (powershell)
python -m venv venv

# Activate Virtual Enviroment (powershell)
 venv\Scripts\Activate.ps1

# The FastAPI Server (install required package)
pip install -r requirements.txt
 pip install fastapi uvicorn
 pip install python-docx

# DownGrade Pip for Testeract
python -m pip install "pip<24.1"

# Run the FastAPI Server
uvicorn main:app --reload
 
# Open API Documentation
Swagger UI:  http://127.0.0.1:8000/docs

# Decrypt Document Password
decryptme!
