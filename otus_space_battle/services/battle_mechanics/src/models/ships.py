from enum import Enum
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field

class Vector2D(BaseModel):
    """Двумерный вектор для позиции и скорости"""
    x: float
    y: float

class WeaponState(BaseModel):
    """Состояние оружия"""
    type: str
    damage: float
    cooldown: float
    ammunition: int
    range: float
    last_shot: float = 0.0  # Время последнего выстрела

class ShipState(BaseModel):
    """Состояние корабля в игре"""
    id: str
    template_id: str
    player_id: str
    position: Vector2D
    velocity: Vector2D
    rotation: float  # Угол поворота в радианах
    current_speed: float
    fuel: float
    hull_strength: float
    shield_strength: float
    weapons: List[WeaponState]
    is_destroyed: bool = False

class MoveCommand(BaseModel):
    """Команда на движение корабля"""
    thrust: float = Field(ge=-1.0, le=1.0, description="Тяга двигателя от -1 до 1")
    rotation: float = Field(ge=-1.0, le=1.0, description="Поворот от -1 до 1")

class FireCommand(BaseModel):
    """Команда на выстрел"""
    weapon_index: int = Field(ge=0, description="Индекс оружия в массиве weapons")
    target: Vector2D = Field(description="Координаты цели") 