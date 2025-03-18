import pytest
from fastapi.testclient import TestClient
from datetime import timedelta
from ..src.app import app, create_access_token, verify_password
from ..src.models import UserCreate, TokenData

client = TestClient(app)

@pytest.fixture
def test_user():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword"
    }

@pytest.fixture
def test_token():
    return create_access_token({"sub": "testuser"})

def test_register(test_user):
    response = client.post("/register", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]

def test_login(test_user):
    # Сначала регистрируем пользователя
    client.post("/register", json=test_user)
    # Затем пытаемся войти
    response = client.post("/login", data={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_verify_token(test_token):
    response = client.get("/verify", headers={"Authorization": f"Bearer {test_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"

def test_verify_password():
    password = "testpassword"
    hashed = verify_password(password, password)
    assert verify_password(password, hashed)

def test_invalid_token():
    response = client.get("/verify", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401

def test_invalid_credentials():
    response = client.post("/login", data={
        "username": "wronguser",
        "password": "wrongpass"
    })
    assert response.status_code == 401 