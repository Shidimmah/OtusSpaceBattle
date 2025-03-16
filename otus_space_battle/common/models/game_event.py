from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class GameEvent(Base):
    __tablename__ = "game_events"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(50), nullable=False)  # move, rotate, fire, hit, destroy
    ship_id = Column(Integer, ForeignKey("ships.id", ondelete="SET NULL"), nullable=True)
    target_ship_id = Column(Integer, ForeignKey("ships.id", ondelete="SET NULL"), nullable=True)
    event_data = Column(String)  # JSON с дополнительными данными события
    timestamp = Column(DateTime, default=func.now())

    # Отношения
    match = relationship("Match")
    ship = relationship("Ship", foreign_keys=[ship_id])
    target_ship = relationship("Ship", foreign_keys=[target_ship_id]) 