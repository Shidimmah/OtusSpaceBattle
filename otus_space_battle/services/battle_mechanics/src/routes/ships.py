from fastapi import APIRouter, HTTPException, Depends
from typing import List

from ..services.ships import ShipService
from ..models.ships import ShipState, Vector2D, MoveCommand, FireCommand
from ..config import get_settings

router = APIRouter()

def get_ship_service():
    # Получить сервис для работы с кораблями
    settings = get_settings()
    return ShipService(settings.resource_management_url)

@router.post("/create", response_model=ShipState)
async def create_ship(
    template_id: str,
    player_id: str,
    position: Vector2D,
    service: ShipService = Depends(get_ship_service)
):
    # Создать корабль в игре
    try:
        return await service.create_ship(template_id, player_id, position)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{ship_id}", response_model=ShipState)
def get_ship_state(ship_id: str, service: ShipService = Depends(get_ship_service)):
    # Получить состояние корабля
    ship = service.get_ship(ship_id)
    if not ship:
        raise HTTPException(status_code=404, detail="Корабль не найден")
    return ship

@router.post("/{ship_id}/move", response_model=ShipState)
def move_ship(
    ship_id: str,
    command: MoveCommand,
    service: ShipService = Depends(get_ship_service)
):
    # Управление движением корабля
    ship = service.update_ship(ship_id, command)
    if not ship:
        raise HTTPException(status_code=404, detail="Корабль не найден")
    return ship

@router.post("/{ship_id}/fire")
def fire_weapon(
    ship_id: str,
    command: FireCommand,
    service: ShipService = Depends(get_ship_service)
):
    # Выстрел из оружия корабля
    result = service.fire_weapon(ship_id, command)
    if not result:
        raise HTTPException(status_code=404, detail="Корабль не найден")
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result 