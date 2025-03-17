from typing import List, Optional, Tuple
from pydantic import BaseModel, Field
from ..models.ships import WeaponType

class WeaponCharacteristics(BaseModel):
    """Характеристики оружия"""
    type: WeaponType
    damage: float = Field(gt=0, description="Урон")
    cooldown: float = Field(gt=0, description="Время перезарядки в секундах")
    ammunition: int = Field(description="Количество боеприпасов (-1 для бесконечных)")
    range: float = Field(gt=0, description="Дальность стрельбы")

class ShipCharacteristics(BaseModel):
    """Характеристики корабля"""
    max_speed: float = Field(gt=0, description="Максимальная скорость")
    acceleration: float = Field(gt=0, description="Ускорение")
    rotation_speed: float = Field(gt=0, description="Скорость поворота")
    fuel_capacity: float = Field(gt=0, description="Емкость топливного бака")
    fuel_consumption: float = Field(gt=0, description="Расход топлива")
    hull_strength: float = Field(gt=0, description="Прочность корпуса")
    shield_strength: float = Field(gt=0, description="Прочность щита")

class ShipTemplateBase(BaseModel):
    """Базовая схема шаблона корабля"""
    name: str = Field(min_length=1, max_length=100, description="Название шаблона")
    description: Optional[str] = Field(None, max_length=500, description="Описание шаблона")
    characteristics: ShipCharacteristics
    weapons: List[WeaponCharacteristics]
    size: Tuple[float, float] = Field(default=(10.0, 10.0), description="Размеры корабля (длина, ширина)")

class ShipTemplateCreate(ShipTemplateBase):
    """Схема для создания шаблона корабля"""
    id: str = Field(min_length=1, max_length=50, description="Уникальный идентификатор шаблона")

class ShipTemplateUpdate(BaseModel):
    """Схема для обновления шаблона корабля"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Название шаблона")
    description: Optional[str] = Field(None, max_length=500, description="Описание шаблона")
    characteristics: Optional[ShipCharacteristics] = None
    weapons: Optional[List[WeaponCharacteristics]] = None
    size: Optional[Tuple[float, float]] = Field(None, description="Размеры корабля (длина, ширина)")

class ShipTemplateResponse(ShipTemplateBase):
    """Схема для ответа с шаблоном корабля"""
    id: str
    is_default: bool
    in_use: bool

    class Config:
        from_attributes = True 