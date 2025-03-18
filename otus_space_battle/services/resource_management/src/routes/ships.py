from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependency_injector.wiring import inject, Provide

from ..schemas.ships import ShipTemplateResponse, ShipTemplateCreate, ShipTemplateUpdate
from ..services.ships import ShipService
from ..di.container import Container

router = APIRouter()

@router.get("/templates", response_model=List[ShipTemplateResponse])
@inject
async def get_ship_templates(
    db: Session = Depends(Provide[Container.db]),
    ship_service: ShipService = Depends(Provide[Container.ship_service])
):
    # Получить список всех шаблонов кораблей
    return ship_service.get_templates(db)

@router.get("/templates/{template_id}", response_model=ShipTemplateResponse)
@inject
async def get_ship_template(
    template_id: str,
    db: Session = Depends(Provide[Container.db]),
    ship_service: ShipService = Depends(Provide[Container.ship_service])
):
    # Получить шаблон корабля по ID
    template = ship_service.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    return template

@router.post("/templates", response_model=ShipTemplateResponse)
@inject
async def create_ship_template(
    template: ShipTemplateCreate,
    db: Session = Depends(Provide[Container.db]),
    ship_service: ShipService = Depends(Provide[Container.ship_service])
):
    # Создать новый шаблон корабля
    return ship_service.create_template(db, template)

@router.post("/templates/from-plugin/{plugin_type}", response_model=ShipTemplateResponse)
@inject
async def create_ship_template_from_plugin(
    plugin_type: str,
    db: Session = Depends(Provide[Container.db]),
    ship_service: ShipService = Depends(Provide[Container.ship_service])
):
    # Создать шаблон корабля из плагина
    return ship_service.create_template_from_plugin(db, plugin_type)

@router.put("/templates/{template_id}", response_model=ShipTemplateResponse)
@inject
async def update_ship_template(
    template_id: str,
    template: ShipTemplateUpdate,
    db: Session = Depends(Provide[Container.db]),
    ship_service: ShipService = Depends(Provide[Container.ship_service])
):
    # Обновить существующий шаблон корабля
    updated_template = ship_service.update_template(db, template_id, template)
    if not updated_template:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    return updated_template

@router.delete("/templates/{template_id}")
@inject
async def delete_ship_template(
    template_id: str,
    db: Session = Depends(Provide[Container.db]),
    ship_service: ShipService = Depends(Provide[Container.ship_service])
):
    # Удалить шаблон корабля
    if not ship_service.delete_template(db, template_id):
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    return {"message": "Шаблон успешно удален"}

@router.get("/plugins/types")
@inject
async def get_available_plugin_types(
    ship_service: ShipService = Depends(Provide[Container.ship_service])
):
    # Получить список доступных типов плагинов
    return ship_service.get_available_plugin_types() 