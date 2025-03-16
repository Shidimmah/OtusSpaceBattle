from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum
from sqlalchemy.orm import Session
from common.database import get_db
from .models import PlayerRankDB

app = FastAPI(title="Ranking Service")

# Константы для расчета рейтинга
WIN_POINTS = 10
LOSS_POINTS = -10
DRAW_POINTS = -5

class GameResult(str, Enum):
    WIN = "win"
    LOSS = "loss"
    DRAW = "draw"

class PlayerRank(BaseModel):
    player_id: str
    rank_points: int
    games_played: int
    wins: int
    losses: int
    draws: int

class GameOutcome(BaseModel):
    game_id: str
    player_id: str
    result: GameResult

def get_player_rank_from_db(db: Session, player_id: str) -> PlayerRank:
    """Получает рейтинг игрока из базы данных"""
    db_rank = db.query(PlayerRankDB).filter(PlayerRankDB.player_id == player_id).first()
    if not db_rank:
        raise HTTPException(status_code=404, detail=f"Player {player_id} not found")
    
    return PlayerRank(
        player_id=db_rank.player_id,
        rank_points=db_rank.rank_points,
        games_played=db_rank.games_played,
        wins=db_rank.wins,
        losses=db_rank.losses,
        draws=db_rank.draws
    )

@app.get("/ranking/{player_id}")
async def get_player_rank(player_id: str, db: Session = Depends(get_db)) -> PlayerRank:
    """Получает текущий рейтинг игрока"""
    return get_player_rank_from_db(db, player_id)

@app.post("/ranking/update")
async def update_ranking(outcome: GameOutcome, db: Session = Depends(get_db)) -> PlayerRank:
    """Обновляет рейтинг игрока после игры"""
    db_rank = db.query(PlayerRankDB).filter(PlayerRankDB.player_id == outcome.player_id).first()
    if not db_rank:
        raise HTTPException(status_code=404, detail=f"Player {outcome.player_id} not found")
    
    db_rank.games_played += 1
    
    # Обновляем статистику и очки в зависимости от результата
    if outcome.result == GameResult.WIN:
        db_rank.wins += 1
        db_rank.rank_points += WIN_POINTS
    elif outcome.result == GameResult.LOSS:
        db_rank.losses += 1
        db_rank.rank_points += LOSS_POINTS
    else:  # DRAW
        db_rank.draws += 1
        db_rank.rank_points += DRAW_POINTS
    
    # Убеждаемся, что рейтинг не уходит в отрицательные значения
    db_rank.rank_points = max(0, db_rank.rank_points)
    
    db.commit()
    db.refresh(db_rank)
    
    return PlayerRank(
        player_id=db_rank.player_id,
        rank_points=db_rank.rank_points,
        games_played=db_rank.games_played,
        wins=db_rank.wins,
        losses=db_rank.losses,
        draws=db_rank.draws
    )

@app.get("/ranking/leaderboard")
async def get_leaderboard(limit: int = 10, db: Session = Depends(get_db)) -> List[PlayerRank]:
    """Получает список лучших игроков"""
    # Сортируем игроков по очкам рейтинга
    db_ranks = db.query(PlayerRankDB).order_by(
        PlayerRankDB.rank_points.desc(),
        PlayerRankDB.wins.desc(),
        PlayerRankDB.losses.asc()
    ).limit(limit).all()
    
    return [
        PlayerRank(
            player_id=rank.player_id,
            rank_points=rank.rank_points,
            games_played=rank.games_played,
            wins=rank.wins,
            losses=rank.losses,
            draws=rank.draws
        )
        for rank in db_ranks
    ]

@app.post("/ranking/initialize")
async def initialize_player_ranking(player_id: str, db: Session = Depends(get_db)) -> PlayerRank:
    """Инициализирует рейтинг нового игрока"""
    db_rank = db.query(PlayerRankDB).filter(PlayerRankDB.player_id == player_id).first()
    if db_rank:
        raise HTTPException(status_code=400, detail=f"Player {player_id} already exists")
    
    # Создаем начальный рейтинг для нового игрока
    db_rank = PlayerRankDB(
        player_id=player_id,
        rank_points=0,
        games_played=0,
        wins=0,
        losses=0,
        draws=0
    )
    
    db.add(db_rank)
    db.commit()
    db.refresh(db_rank)
    
    return PlayerRank(
        player_id=db_rank.player_id,
        rank_points=db_rank.rank_points,
        games_played=db_rank.games_played,
        wins=db_rank.wins,
        losses=db_rank.losses,
        draws=db_rank.draws
    ) 