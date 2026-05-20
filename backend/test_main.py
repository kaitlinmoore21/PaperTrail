import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


from main import app, get_db
import auth
from database import Base 


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="session")
def session_fixture():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="client")
def client_fixture(session):
    def override_get_db():
        try:
            yield session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[auth.get_db] = override_get_db 
    
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_signup(client):
    """Test user registration"""
    response = client.post("/signup/", json={
        "email": "unique_test@example.com",
        "password": "strongpassword123",
        "employee_number": "12345"
    })
    assert response.status_code == 200

def test_login_success(client):
    """Test successful login and token generation"""
    email = "login_test@example.com"
    client.post("/signup/", json={
        "email": email,
        "password": "password",
        "employee_number": "5555"
    })
    
    response = client.post("/login/", json={
        "email": email,
        "password": "password",
        "employee_number": "5555"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_protected_route_access(client):
    """Test accessing documents with a valid token"""
    email = "doc_test@doctor.com" 
    client.post("/signup/", json={
        "email": email,
        "password": "password",
        "employee_number": "8888"
    })
    login_res = client.post("/login/", json={
        "email": email,
        "password": "password",
        "employee_number": "8888"
    })
    token = login_res.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/documents/", headers=headers)
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_unauthorized_access(client):
    response = client.get("/documents/")
    assert response.status_code == 401