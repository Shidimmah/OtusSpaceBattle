from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import decode, ExpiredSignatureError, InvalidTokenError
import httpx
from matchmaking import router as matchmaking_router
import asyncio
from database import init_db

async def startup_event():
    await init_db()

app = FastAPI(title="Matchmaking Service", on_startup=[startup_event])

app.include_router(matchmaking_router, prefix="/matchmaking")

SECRET_KEY = "SECRET123"
security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

app.include_router(matchmaking_router, prefix="/matchmaking")
