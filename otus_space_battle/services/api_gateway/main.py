from fastapi import FastAPI, HTTPException, Depends
import httpx
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import decode, ExpiredSignatureError, InvalidTokenError
from pydantic import BaseModel

app = FastAPI(title="Otus Space Battle API Gateway")

AUTH_SERVICE_URL = "http://auth_service:8001"

security = HTTPBearer()

SECRET_KEY = "SECRET123"

# Функция проверки JWT-токена
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ---- Эндпоинты API Gateway ----

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

@app.post("/auth/refresh")
async def refresh_token(refresh_token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/auth/refresh", json={"refresh_token": refresh_token})
    return response.json()

# Прокси-запрос с проверкой авторизации
@app.get("/protected")
async def protected_route(payload: dict = Depends(verify_token)):
    return {"message": "You have access!", "user_id": payload["user_id"]}
