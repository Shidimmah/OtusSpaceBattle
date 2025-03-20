from fastapi import FastAPI, Request, Depends, HTTPException
from pydantic import BaseModel
import httpx
import jwt
import uvicorn
import os
from prometheus_client import start_http_server

app = FastAPI()

AUTH_SERVICE_URL = "http://auth_service:8000"
MATCHMAKING_SERVICE_URL = "http://matchmaking:8000"

SECRET_KEY = "your_secret_key"  

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(UserLogin):
    email: str

async def verify_token(request: Request):
    authorization: str = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def proxy_request(target_url: str, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=request.headers.raw,
            content=await request.body()
        )
    return response.json()

@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_auth(path: str, request: Request):
    target_url = f"{AUTH_SERVICE_URL}/auth/{path}"
    return await proxy_request(target_url, request)

@app.api_route("/matchmaking/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_matchmaking(path: str, request: Request):
    target_url = f"{MATCHMAKING_SERVICE_URL}/matchmaking/{path}"
    return await proxy_request(target_url, request)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Сервис шлюза API"}

if __name__ == "__main__":
    # Start metrics server
    metrics_port = int(os.getenv("METRICS_PORT", "9000"))
    start_http_server(metrics_port)
    
    # Start main API server
    api_port = 8000
    uvicorn.run(app, host="0.0.0.0", port=api_port)