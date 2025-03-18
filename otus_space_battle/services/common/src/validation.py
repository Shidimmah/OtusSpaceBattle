from pydantic import BaseModel, Field, validator, constr
from typing import List, Optional, Dict, Any
from datetime import datetime
import re

class ShipTemplate(BaseModel):
    name: constr(min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9\s-]+$')
    type: constr(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9-]+$')
    description: Optional[constr(max_length=500)] = None
    parameters: Dict[str, Any] = Field(..., min_items=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('parameters')
    def validate_parameters(cls, v):
        required_fields = ['health', 'shield', 'speed', 'attack']
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Missing required parameter: {field}")
        return v

class User(BaseModel):
    username: constr(min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    email: constr(regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: constr(min_length=8, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('password')
    def validate_password(cls, v):
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', v):
            raise ValueError('Password must contain at least one letter and one number')
        return v

class Fleet(BaseModel):
    name: constr(min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9\s-]+$')
    ships: List[Dict[str, Any]] = Field(..., min_items=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('ships')
    def validate_ships(cls, v):
        for ship in v:
            if 'template_id' not in ship or 'quantity' not in ship:
                raise ValueError('Each ship must have template_id and quantity')
            if ship['quantity'] < 1:
                raise ValueError('Ship quantity must be greater than 0')
        return v

class BattleRequest(BaseModel):
    attacker_fleet_id: int
    defender_fleet_id: int
    battle_type: constr(pattern=r'^(pvp|pve)$')
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AnalyticsRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    metrics: List[constr(pattern=r'^(ships_created|combat_stats|resource_usage)$')]
    group_by: Optional[constr(pattern=r'^(day|week|month)$')] = 'day'

    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be greater than start_date')
        return v

class MatchmakingRequest(BaseModel):
    user_id: int
    fleet_id: int
    preferences: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('preferences')
    def validate_preferences(cls, v):
        allowed_keys = {'min_players', 'max_players', 'battle_type', 'difficulty'}
        if not all(key in allowed_keys for key in v.keys()):
            raise ValueError('Invalid preference key')
        return v 