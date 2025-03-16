from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.sql import func
from common.database import Base

class ShipDB(Base):
    __tablename__ = "ships"

    id = Column(String(36), primary_key=True)
    position_x = Column(Float, nullable=False)
    position_y = Column(Float, nullable=False)
    direction_angle = Column(Float, nullable=False)
    speed = Column(Float, nullable=False)
    rotation_speed = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 