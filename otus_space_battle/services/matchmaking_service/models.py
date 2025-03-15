from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase
from database_service.models import Base

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    player1_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    player2_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    start_time = Column(DateTime, default=func.now())
    end_time = Column(DateTime, nullable=True)
    winner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(String, default="waiting")
    is_ranked = Column(Boolean, default=True)
