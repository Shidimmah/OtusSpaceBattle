from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from common.database import get_db
from .models import ShipResourcesDB

app = FastAPI(title="Resource Management Service")

# Временное хранилище для демонстрации. В реальности будет использоваться БД
ship_resources: Dict[str, ShipResources] = {}

class ShipResources(BaseModel):
    ship_id: str
    fuel: float
    torpedoes: int
    is_active: bool

class ResourceUpdateRequest(BaseModel):
    ship_id: str
    fuel_consumption: Optional[float] = 0
    torpedoes_used: Optional[int] = 0

def get_ship_resources_from_db(db: Session, ship_id: str) -> ShipResources:
    """Получает ресурсы корабля из базы данных"""
    db_resources = db.query(ShipResourcesDB).filter(ShipResourcesDB.ship_id == ship_id).first()
    if not db_resources:
        raise HTTPException(status_code=404, detail=f"Ship {ship_id} not found")
    
    return ShipResources(
        ship_id=db_resources.ship_id,
        fuel=db_resources.fuel,
        torpedoes=db_resources.torpedoes,
        is_active=db_resources.is_active
    )

@app.get("/resources/{ship_id}")
async def get_ship_resources(ship_id: str, db: Session = Depends(get_db)) -> ShipResources:
    """Получает текущее состояние ресурсов корабля"""
    return get_ship_resources_from_db(db, ship_id)

@app.post("/resources/update")
async def update_resources(request: ResourceUpdateRequest, db: Session = Depends(get_db)) -> ShipResources:
    """Обновляет состояние ресурсов корабля"""
    db_resources = db.query(ShipResourcesDB).filter(ShipResourcesDB.ship_id == request.ship_id).first()
    if not db_resources:
        raise HTTPException(status_code=404, detail=f"Ship {request.ship_id} not found")
    
    # Обновляем топливо
    if request.fuel_consumption > 0:
        if db_resources.fuel < request.fuel_consumption:
            raise HTTPException(status_code=400, detail="Not enough fuel")
        db_resources.fuel -= request.fuel_consumption
    
    # Обновляем торпеды
    if request.torpedoes_used > 0:
        if db_resources.torpedoes < request.torpedoes_used:
            raise HTTPException(status_code=400, detail="Not enough torpedoes")
        db_resources.torpedoes -= request.torpedoes_used
    
    # Проверяем активность корабля
    db_resources.is_active = db_resources.fuel > 0 or db_resources.torpedoes > 0
    
    db.commit()
    db.refresh(db_resources)
    
    return ShipResources(
        ship_id=db_resources.ship_id,
        fuel=db_resources.fuel,
        torpedoes=db_resources.torpedoes,
        is_active=db_resources.is_active
    )

@app.post("/resources/initialize")
async def initialize_ship_resources(resources: ShipResources, db: Session = Depends(get_db)) -> ShipResources:
    """Инициализирует ресурсы нового корабля"""
    db_resources = db.query(ShipResourcesDB).filter(ShipResourcesDB.ship_id == resources.ship_id).first()
    if db_resources:
        raise HTTPException(status_code=400, detail=f"Ship {resources.ship_id} already exists")
    
    # Проверяем валидность начальных значений
    if resources.fuel < 0 or resources.torpedoes < 0:
        raise HTTPException(status_code=400, detail="Invalid initial resource values")
    
    db_resources = ShipResourcesDB(
        ship_id=resources.ship_id,
        fuel=resources.fuel,
        torpedoes=resources.torpedoes,
        is_active=resources.is_active
    )
    
    db.add(db_resources)
    db.commit()
    db.refresh(db_resources)
    
    return resources

@app.get("/resources/check-active/{ship_id}")
async def check_ship_active(ship_id: str, db: Session = Depends(get_db)) -> bool:
    """Проверяет, активен ли корабль (есть ли ресурсы для действий)"""
    db_resources = db.query(ShipResourcesDB).filter(ShipResourcesDB.ship_id == ship_id).first()
    if not db_resources:
        raise HTTPException(status_code=404, detail=f"Ship {ship_id} not found")
    
    return db_resources.is_active 