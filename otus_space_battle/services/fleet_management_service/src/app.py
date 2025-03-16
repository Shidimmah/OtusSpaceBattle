from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_session
from models import Fleet, Ship, ShipType

app = FastAPI(title="Fleet Management Service")

class ShipBase(BaseModel):
    ship_type_id: int
    position: int

class ShipCreate(ShipBase):
    pass

class ShipResponse(ShipBase):
    id: int
    fleet_id: int

    class Config:
        from_attributes = True

class FleetBase(BaseModel):
    name: str
    user_id: int

class FleetCreate(FleetBase):
    ships: List[ShipCreate]

class FleetResponse(FleetBase):
    id: int
    ships: List[ShipResponse]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

@app.post("/fleets/", response_model=FleetResponse)
async def create_fleet(fleet: FleetCreate, session: AsyncSession = Depends(get_session)):
    # Проверяем количество кораблей
    if len(fleet.ships) != 3:
        raise HTTPException(status_code=400, detail="Fleet must have exactly 3 ships")
    
    # Проверяем уникальность позиций
    positions = [ship.position for ship in fleet.ships]
    if len(set(positions)) != len(positions):
        raise HTTPException(status_code=400, detail="Ship positions must be unique")
    
    # Проверяем существование типов кораблей
    for ship in fleet.ships:
        ship_type = await session.get(ShipType, ship.ship_type_id)
        if not ship_type:
            raise HTTPException(status_code=404, detail=f"Ship type {ship.ship_type_id} not found")
    
    # Создаем флот
    db_fleet = Fleet(
        name=fleet.name,
        user_id=fleet.user_id
    )
    session.add(db_fleet)
    await session.flush()  # Получаем id флота
    
    # Создаем корабли
    for ship_data in fleet.ships:
        db_ship = Ship(
            fleet_id=db_fleet.id,
            ship_type_id=ship_data.ship_type_id,
            position=ship_data.position
        )
        session.add(db_ship)
    
    await session.commit()
    await session.refresh(db_fleet)
    return db_fleet

@app.get("/fleets/{user_id}", response_model=List[FleetResponse])
async def get_user_fleets(user_id: int, session: AsyncSession = Depends(get_session)):
    query = select(Fleet).where(Fleet.user_id == user_id)
    result = await session.execute(query)
    fleets = result.scalars().all()
    return fleets

@app.get("/ship-types/", response_model=List[dict])
async def get_ship_types(session: AsyncSession = Depends(get_session)):
    query = select(ShipType)
    result = await session.execute(query)
    ship_types = result.scalars().all()
    return [
        {
            "id": st.id,
            "name": st.name,
            "description": st.description,
            "base_fuel_capacity": st.base_fuel_capacity,
            "base_torpedo_capacity": st.base_torpedo_capacity,
            "base_movement_speed": st.base_movement_speed,
            "base_rotation_speed": st.base_rotation_speed,
            "fuel_consumption_move": st.fuel_consumption_move,
            "fuel_consumption_rotate": st.fuel_consumption_rotate
        }
        for st in ship_types
    ]

@app.put("/fleets/{fleet_id}", response_model=FleetResponse)
async def update_fleet(
    fleet_id: int,
    fleet_update: FleetCreate,
    session: AsyncSession = Depends(get_session)
):
    # Получаем существующий флот
    db_fleet = await session.get(Fleet, fleet_id)
    if not db_fleet:
        raise HTTPException(status_code=404, detail="Fleet not found")
    
    # Проверяем владельца
    if db_fleet.user_id != fleet_update.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this fleet")
    
    # Обновляем имя флота
    db_fleet.name = fleet_update.name
    
    # Удаляем существующие корабли
    query = select(Ship).where(Ship.fleet_id == fleet_id)
    result = await session.execute(query)
    existing_ships = result.scalars().all()
    for ship in existing_ships:
        await session.delete(ship)
    
    # Создаем новые корабли
    for ship_data in fleet_update.ships:
        db_ship = Ship(
            fleet_id=fleet_id,
            ship_type_id=ship_data.ship_type_id,
            position=ship_data.position
        )
        session.add(db_ship)
    
    await session.commit()
    await session.refresh(db_fleet)
    return db_fleet

@app.delete("/fleets/{fleet_id}")
async def delete_fleet(fleet_id: int, session: AsyncSession = Depends(get_session)):
    db_fleet = await session.get(Fleet, fleet_id)
    if not db_fleet:
        raise HTTPException(status_code=404, detail="Fleet not found")
    
    await session.delete(db_fleet)
    await session.commit()
    return {"message": "Fleet deleted"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 