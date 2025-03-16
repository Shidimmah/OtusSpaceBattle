from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from common.database import Base

class GameEventDB(Base):
    __tablename__ = "game_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String(36), nullable=False)
    player_id = Column(String(36), nullable=False)
    event_type = Column(String(50), nullable=False)
    event_data = Column(JSON, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class GameStatsDB(Base):
    __tablename__ = "game_statistics"

    game_id = Column(String(36), primary_key=True)
    duration = Column(Float, nullable=False)
    shots_fired = Column(Integer, nullable=False, default=0)
    hits = Column(Integer, nullable=False, default=0)
    fuel_used = Column(Float, nullable=False, default=0)
    winner_id = Column(String(36), nullable=True)
    is_draw = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class PlayerStatsDB(Base):
    __tablename__ = "player_statistics"

    player_id = Column(String(36), primary_key=True)
    total_games = Column(Integer, nullable=False, default=0)
    total_wins = Column(Integer, nullable=False, default=0)
    total_losses = Column(Integer, nullable=False, default=0)
    total_draws = Column(Integer, nullable=False, default=0)
    average_game_duration = Column(Float, nullable=False, default=0)
    accuracy = Column(Float, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 