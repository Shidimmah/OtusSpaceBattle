from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import uvicorn

from common.models.match import Match
from common.models.user import User
from common.models.fleet import Fleet
from common.utils.database import get_session

app = FastAPI(title="Matchmaking Service")

class MatchCreate(BaseModel):
    player1_id: int
    player1_fleet_id: int
    is_ranked: bool = True

class MatchUpdate(BaseModel):
    player2_id: Optional[int] = None
    player2_fleet_id: Optional[int] = None
    status: Optional[str] = None
    winner_id: Optional[int] = None

class MatchResponse(BaseModel):
    id: int
    player1_id: int
    player2_id: Optional[int]
    player1_fleet_id: Optional[int]
    player2_fleet_id: Optional[int]
    start_time: datetime
    end_time: Optional[datetime]
    winner_id: Optional[int]
    status: str
    is_ranked: bool

    class Config:
        from_attributes = True

@app.post("/matches/", response_model=MatchResponse)
async def create_match(
    match: MatchCreate,
    session: AsyncSession = Depends(get_session)
):
    # Проверяем существование игрока и флота
    player = await session.get(User, match.player1_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    fleet = await session.get(Fleet, match.player1_fleet_id)
    if not fleet or fleet.user_id != match.player1_id:
        raise HTTPException(status_code=404, detail="Fleet not found or doesn't belong to player")
    
    # Проверяем, нет ли уже активного матча у игрока
    query = select(Match).where(
        and_(
            (Match.player1_id == match.player1_id) | (Match.player2_id == match.player1_id),
            Match.status.in_(["waiting", "in_progress"])
        )
    )
    result = await session.execute(query)
    existing_match = result.scalar_one_or_none()
    
    if existing_match:
        raise HTTPException(
            status_code=400,
            detail="Player already has an active match"
        )
    
    # Создаем новый матч
    db_match = Match(
        player1_id=match.player1_id,
        player1_fleet_id=match.player1_fleet_id,
        is_ranked=match.is_ranked,
        status="waiting"
    )
    session.add(db_match)
    await session.commit()
    await session.refresh(db_match)
    
    return db_match

@app.get("/matches/waiting", response_model=List[MatchResponse])
async def get_waiting_matches(session: AsyncSession = Depends(get_session)):
    query = select(Match).where(Match.status == "waiting")
    result = await session.execute(query)
    matches = result.scalars().all()
    return matches

@app.put("/matches/{match_id}", response_model=MatchResponse)
async def update_match(
    match_id: int,
    match_update: MatchUpdate,
    session: AsyncSession = Depends(get_session)
):
    db_match = await session.get(Match, match_id)
    if not db_match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if match_update.player2_id is not None:
        # Проверяем существование второго игрока
        player2 = await session.get(User, match_update.player2_id)
        if not player2:
            raise HTTPException(status_code=404, detail="Player 2 not found")
        
        # Проверяем флот второго игрока
        if match_update.player2_fleet_id:
            fleet2 = await session.get(Fleet, match_update.player2_fleet_id)
            if not fleet2 or fleet2.user_id != match_update.player2_id:
                raise HTTPException(
                    status_code=404,
                    detail="Fleet not found or doesn't belong to player 2"
                )
        
        db_match.player2_id = match_update.player2_id
        db_match.player2_fleet_id = match_update.player2_fleet_id
        
        # Если присоединился второй игрок, меняем статус на in_progress
        if db_match.status == "waiting":
            db_match.status = "in_progress"
    
    if match_update.status:
        db_match.status = match_update.status
        if match_update.status == "finished":
            db_match.end_time = datetime.utcnow()
    
    if match_update.winner_id is not None:
        # Проверяем, что победитель является одним из игроков
        if match_update.winner_id not in [db_match.player1_id, db_match.player2_id]:
            raise HTTPException(
                status_code=400,
                detail="Winner must be one of the players"
            )
        db_match.winner_id = match_update.winner_id
    
    await session.commit()
    await session.refresh(db_match)
    return db_match

@app.get("/matches/active/{player_id}", response_model=Optional[MatchResponse])
async def get_active_match(player_id: int, session: AsyncSession = Depends(get_session)):
    query = select(Match).where(
        and_(
            (Match.player1_id == player_id) | (Match.player2_id == player_id),
            Match.status.in_(["waiting", "in_progress"])
        )
    )
    result = await session.execute(query)
    match = result.scalar_one_or_none()
    
    if not match:
        return None
    return match

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 