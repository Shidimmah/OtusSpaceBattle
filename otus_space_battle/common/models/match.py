from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    player1_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    player2_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    player1_fleet_id = Column(Integer, ForeignKey("fleets.id", ondelete="SET NULL"), nullable=True)
    player2_fleet_id = Column(Integer, ForeignKey("fleets.id", ondelete="SET NULL"), nullable=True)
    start_time = Column(DateTime, default=func.now())
    end_time = Column(DateTime, nullable=True)
    winner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(String, default="waiting")
    is_ranked = Column(Boolean, default=True)
    
    # Отношения
    player1 = relationship("User", foreign_keys=[player1_id], back_populates="matches_as_player1")
    player2 = relationship("User", foreign_keys=[player2_id], back_populates="matches_as_player2")
    player1_fleet = relationship("Fleet", foreign_keys=[player1_fleet_id])
    player2_fleet = relationship("Fleet", foreign_keys=[player2_fleet_id]) 