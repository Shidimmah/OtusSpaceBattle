from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Fleet(Base):
    __tablename__ = "fleets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Отношения
    user = relationship("User", back_populates="fleets")
    ships = relationship("Ship", back_populates="fleet", cascade="all, delete-orphan")
    
    # Ограничение на количество флотов у пользователя
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='unique_fleet_name_per_user'),
    ) 