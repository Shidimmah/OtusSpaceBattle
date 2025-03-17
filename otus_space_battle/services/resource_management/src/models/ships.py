from enum import Enum
from typing import List
from sqlalchemy import Column, String, Float, Boolean, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from ..database import Base

class WeaponType(str, Enum):
    """Типы оружия"""
    TORPEDO = "torpedo"
    LASER = "laser"
    MISSILE = "missile"

class ShipTemplate(Base):
    """Модель шаблона корабля"""
    __tablename__ = "ship_templates"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    is_default = Column(Boolean, default=False)  # Предустановленный шаблон или нет
    in_use = Column(Boolean, default=False)      # Используется ли шаблон в активных играх
    
    # Характеристики корабля
    max_speed = Column(Float, nullable=False)
    acceleration = Column(Float, nullable=False)
    rotation_speed = Column(Float, nullable=False)
    fuel_capacity = Column(Float, nullable=False)
    fuel_consumption = Column(Float, nullable=False)
    hull_strength = Column(Float, nullable=False)
    shield_strength = Column(Float, nullable=False)
    
    # Размеры корабля
    length = Column(Float, nullable=False, default=10.0)
    width = Column(Float, nullable=False, default=10.0)

    # Оружие хранится в отдельной таблице
    weapons = relationship("ShipWeapon", back_populates="ship_template", cascade="all, delete-orphan")

class ShipWeapon(Base):
    """Модель оружия корабля"""
    __tablename__ = "ship_weapons"

    id = Column(Integer, primary_key=True)
    ship_template_id = Column(String, ForeignKey('ship_templates.id', ondelete='CASCADE'), nullable=False)
    
    type = Column(SQLEnum(WeaponType), nullable=False)
    damage = Column(Float, nullable=False)
    cooldown = Column(Float, nullable=False)
    ammunition = Column(Integer, nullable=False)  # -1 для бесконечных боеприпасов
    range = Column(Float, nullable=False)

    ship_template = relationship("ShipTemplate", back_populates="weapons") 