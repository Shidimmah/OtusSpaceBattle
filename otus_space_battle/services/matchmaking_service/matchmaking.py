from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from sqlalchemy.future import select
from common.models import Match
from datetime import datetime
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import decode, ExpiredSignatureError, InvalidTokenError
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
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))

async def get_db():
    await wait_for_db()  # Ждём, пока БД будет доступна
    async with SessionLocal() as session:
        yield session

router = APIRouter()

security = HTTPBearer()
SECRET_KEY = "SECRET123"


# Проверка токена
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/find_match")
async def find_match(payload: dict = Depends(verify_token), db: AsyncSession = Depends(get_db)):
    user_id = payload["user_id"]

    # Ищем существующий матч, где ещё нет второго игрока
    stmt = select(Match).where(Match.status == "waiting")
    result = await db.execute(stmt)
    existing_match = result.scalars().first()

    if existing_match:
        existing_match.player2_id = user_id
        existing_match.status = "in_progress"
        await db.commit()
        await db.refresh(existing_match)
        return {"message": "Матч начат.", "match_id": existing_match.id}

    # Создаём новый матч, если свободного нет
    new_match = Match(player1_id=user_id, status="waiting")
    db.add(new_match)
    await db.commit()
    await db.refresh(new_match)
    return {"message": "Ожидание оппонента. ", "match_id": new_match.id}


@router.post("/finish_match")
async def finish_match(match_id: int, winner_id: int, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if match.status != "in_progress":
        raise HTTPException(status_code=400, detail="Match already finished")

    match.winner_id = winner_id
    match.end_time = datetime.utcnow()
    match.status = "finished"
    db.commit()

    return {"message": "Match finished", "winner_id": winner_id}

@router.get("/health")
async def health_check():
    return {"status": "ok"}