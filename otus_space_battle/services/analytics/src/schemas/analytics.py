from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class ShipCreationEventBase(BaseModel):
    # Базовая схема события создания корабля
    ship_id: str
    template_id: str
    creation_time_ms: float

class ShipCreationEventCreate(ShipCreationEventBase):
    # Схема для создания события
    pass

class ShipCreationEventResponse(ShipCreationEventBase):
    # Схема ответа с событием
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ShipTemplateBase(BaseModel):
    # Базовая схема шаблона корабля
    id: str
    name: str
    type: str

class ShipTemplateCreate(ShipTemplateBase):
    # Схема для создания шаблона
    pass

class ShipTemplateResponse(ShipTemplateBase):
    # Схема ответа с шаблоном
    created_at: datetime
    creation_events: List[ShipCreationEventResponse] = []
    
    class Config:
        from_attributes = True

class ShipUsageStatsBase(BaseModel):
    # Базовая схема статистики использования
    ship_id: str
    template_id: str
    total_usage_time: float
    battles_participated: int

class ShipUsageStatsCreate(ShipUsageStatsBase):
    # Схема для создания статистики
    pass

class ShipUsageStatsResponse(ShipUsageStatsBase):
    # Схема ответа со статистикой
    id: int
    last_used_at: datetime
    
    class Config:
        from_attributes = True

class AnalyticsSummary(BaseModel):
    # Сводная статистика
    total_ships_created: int
    total_creation_time_ms: float
    average_creation_time_ms: float
    ships_by_type: dict[str, int]
    most_used_template: Optional[str]
    total_battles: int 