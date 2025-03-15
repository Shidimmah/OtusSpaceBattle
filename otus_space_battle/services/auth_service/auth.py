from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from models import User
import bcrypt
from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta
import time
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from tenacity import retry, stop_after_attempt, wait_fixed

DATABASE_URL = "postgresql+asyncpg://user:password@database_service/main_db"

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

@retry(stop=stop_after_attempt(10), wait=wait_fixed(5))
async def wait_for_db():
    async with engine.begin() as conn:
        await conn.run_sync(lambda c: c.execute("SELECT 1"))

async def get_db():
    await wait_for_db()  # Ждём, пока БД будет доступна
    async with SessionLocal() as session:
        yield session

security = HTTPBearer()
router = APIRouter()

SECRET_KEY = "SECRET123"
REFRESH_SECRET_KEY = "REFRESH_SECRET123"
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Время жизни access-токена (15 мин)
REFRESH_TOKEN_EXPIRE_DAYS = 7     # Время жизни refresh-токена (7 дней)

# Описание схемы данных
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

def create_access_token(user_id: int):
    expiration = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"user_id": user_id, "exp": expiration}
    return encode(payload, SECRET_KEY, algorithm="HS256")

def create_refresh_token(user_id: int):
    expiration = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"user_id": user_id, "exp": expiration}
    return encode(payload, REFRESH_SECRET_KEY, algorithm="HS256")

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        payload = decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен ситёк")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Неверный токен")

def verify_refresh_token(refresh_token: str):
    try:
        payload = decode(refresh_token, REFRESH_SECRET_KEY, algorithms=["HS256"])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Рефреш токен истёк")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Неверный рефреш токен")


@router.post("/register")
async def register(user: UserRegister, db: Session = Depends(get_db)):
    hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"message": "Пользователь создан"}


@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == user.username))
    user_in_db = result.scalars().first()

    if not user_in_db:
        raise HTTPException(status_code=400, detail="Неверные логин/пароль")

    if not bcrypt.checkpw(user.password.encode(), user_in_db.hashed_password.encode()):
        raise HTTPException(status_code=400, detail="Неверные логин/пароль")

    access_token = create_access_token(user_in_db.id)
    refresh_token = create_refresh_token(user_in_db.id)

    return {"access_token": access_token, "refresh_token": refresh_token}

@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest):
    payload = verify_refresh_token(request.refresh_token)
    new_access_token = create_access_token(payload["user_id"])
    return {"access_token": new_access_token}

@router.get("/protected")
async def protected_route(payload: dict = Depends(verify_token)):
    return {"message": "Доступ получен!", "user_id": payload["user_id"]}