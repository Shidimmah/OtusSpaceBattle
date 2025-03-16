from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from common.database import Base

class PlayerRankDB(Base):
    __tablename__ = "player_rankings"

    player_id = Column(String(36), primary_key=True)
    rank_points = Column(Integer, nullable=False, default=0)
    games_played = Column(Integer, nullable=False, default=0)
    wins = Column(Integer, nullable=False, default=0)
    losses = Column(Integer, nullable=False, default=0)
    draws = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 