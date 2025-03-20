from pydantic import BaseModel
from typing import List, Dict, Optional
from common.src.schemas import Ship, GameState, MoveAction, RotateAction, FireAction, GameAction

class Ship(BaseModel):
    id: str
    player_id: str
    position: Dict[str, float]  # {"x": 123.4, "y": 456.7}
    rotation: float  # угол в радианах
    health: int
    fuel: int
    torpedoes: int

class GameState(BaseModel):
    """Класс для хранения состояния игры"""
    id: str
    players: List[str]
    ships: List[Ship]
    status: str  # "waiting", "in_progress", "finished"
    map_size: Dict[str, int]  # {"width": 1000, "height": 1000}
    turn: int = 0

# Здесь могут быть дополнительные модели, специфичные для battle_mechanics сервиса 