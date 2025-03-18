from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base

class ShipCreationEvent(Base):
    # Событие создания корабля
    __tablename__ = "ship_creation_events"
    
    event_id = Column(String, primary_key=True)
    template_id = Column(String, ForeignKey("ship_templates.template_id"))
    user_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    template = relationship("ShipTemplate", back_populates="creation_events")

class ShipTemplate(Base):
    # Шаблон корабля
    __tablename__ = "ship_templates"
    
    template_id = Column(String, primary_key=True)
    name = Column(String)
    type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    creation_events = relationship("ShipCreationEvent", back_populates="template")
    usage_stats = relationship("UsageStats", back_populates="template", uselist=False)

class UsageStats(Base):
    # Статистика использования кораблей
    __tablename__ = "usage_stats"
    
    template_id = Column(String, ForeignKey("ship_templates.template_id"), primary_key=True)
    total_created = Column(Integer, default=0)
    battles_participated = Column(Integer, default=0)
    destroyed_count = Column(Integer, default=0)
    damaged_count = Column(Integer, default=0)
    last_used = Column(DateTime)
    average_creation_time = Column(Float) 