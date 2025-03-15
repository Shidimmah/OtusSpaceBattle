from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Match
from datetime import datetime
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import decode, ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:password@database_service/main_db"

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def get_db():
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
async def find_match(payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    user_id = payload["user_id"]

    # Ищем существующий матч, где ещё нет второго игрока
    existing_match = db.query(Match).filter(Match.status == "waiting").first()

    if existing_match:
        existing_match.player2_id = user_id
        existing_match.status = "in_progress"
        db.commit()
        return {"message": "Match started", "match_id": existing_match.id}

    # Создаём новый матч, если свободного нет
    new_match = Match(player1_id=user_id)
    db.add(new_match)
    db.commit()
    return {"message": "Waiting for opponent", "match_id": new_match.id}


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
