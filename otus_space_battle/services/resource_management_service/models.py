from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from common.database import Base

class ShipResourcesDB(Base):
    __tablename__ = "ship_resources"

    ship_id = Column(String(36), ForeignKey("ships.id"), primary_key=True)
    fuel = Column(Float, nullable=False)
    torpedoes = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 