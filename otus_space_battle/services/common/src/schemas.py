from pydantic import BaseModel
from typing import List, Dict, Optional

class Ship(BaseModel):
    """Модель для валидации данных корабля в игре"""
    id: str
    player_id: str
    position: Dict[str, float]  # {"x": 123.4, "y": 456.7}
    rotation: float  # угол в радианах
    health: int
    fuel: int
    torpedoes: int

class GameState(BaseModel):
    """Модель для хранения состояния игры"""
    id: str
    players: List[str]
    ships: List[Ship]
    status: str  # "waiting", "in_progress", "finished"
    map_size: Dict[str, int]  # {"width": 1000, "height": 1000}
    turn: int = 0

class MoveAction(BaseModel):
    """Модель для валидации действия перемещения"""
    type: str = "move"
    direction: Dict[str, float]  # {"x": 10.0, "y": 0.0}

class RotateAction(BaseModel):
    """Модель для валидации действия поворота"""
    type: str = "rotate"
    angle: float  # угол в радианах

class FireAction(BaseModel):
    """Модель для валидации действия выстрела"""
    type: str = "fire"
    target: Dict[str, float]  # {"x": 123.4, "y": 456.7}

class GameAction(BaseModel):
    """Модель для валидации хода игрока"""
    player_id: str
    actions: List[MoveAction | RotateAction | FireAction] 