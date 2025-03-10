from fastapi import FastAPI, HTTPException, Depends
import httpx
from pydantic import BaseModel

app = FastAPI(title="Otus Space Battle API Gateway")

AUTH_SERVICE_URL = "http://auth_service:8001"

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/auth/register")
async def register_user(user: UserRegister):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/auth/register", json=user.dict())
    return response.json()

@app.post("/auth/login")
async def login_user(user: UserLogin):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/auth/login", json=user.dict())
    return response.json()
