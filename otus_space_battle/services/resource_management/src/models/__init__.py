from pydantic import BaseModel
from typing import Dict, List, Optional

class Resource(BaseModel):
    """Класс для представления ресурса"""
    id: str
    type: str  # fuel, torpedo, etc.
    amount: int
    ship_id: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "id": "resource-1",
                "type": "fuel",
                "amount": 100,
                "ship_id": "ship-1"
            }
        }
