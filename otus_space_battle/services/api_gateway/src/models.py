from pydantic import BaseModel, UUID4
from typing import List, Optional
from datetime import datetime

class Position(BaseModel):
    x: float
    y: float

class Direction(BaseModel):
    angle: float

class Ship(BaseModel):
    id: str
    position: Position
    direction: Direction
    speed: float
    rotation_speed: float
    fuel: float
    torpedoes: int

class GameState(BaseModel):
    game_id: str
    ships: List[Ship]
    started_at: datetime
    is_finished: bool
    winner_id: Optional[str] = None

class GameCommand(BaseModel):
    game_id: str
    ship_id: str
    command_type: str  # "move", "rotate", "fire"
    parameters: dict

class PlayerStats(BaseModel):
    player_id: str
    rank_points: int
    games_played: int
    wins: int
    losses: int
    draws: int

class GameEvent(BaseModel):
    game_id: str
    event_type: str
    event_data: dict
    timestamp: datetime 