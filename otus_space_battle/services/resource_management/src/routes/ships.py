from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.ships import ShipService
from ..schemas.ships import ShipTemplateResponse, ShipTemplateCreate, ShipTemplateUpdate

router = APIRouter()

@router.get("/templates", response_model=List[ShipTemplateResponse])
def get_ship_templates(db: Session = Depends(get_db)):
    """Получить список всех шаблонов кораблей"""
    return ShipService.get_templates(db)

@router.get("/templates/{template_id}", response_model=ShipTemplateResponse)
def get_ship_template(template_id: str, db: Session = Depends(get_db)):
    """Получить шаблон корабля по ID"""
    template = ShipService.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Шаблон корабля не найден")
    return template

@router.post("/templates", response_model=ShipTemplateResponse)
def create_ship_template(template: ShipTemplateCreate, db: Session = Depends(get_db)):
    """Создать новый шаблон корабля"""
    return ShipService.create_template(db, template)

@router.put("/templates/{template_id}", response_model=ShipTemplateResponse)
def update_ship_template(template_id: str, template: ShipTemplateUpdate, db: Session = Depends(get_db)):
    """Обновить существующий шаблон корабля"""
    updated_template = ShipService.update_template(db, template_id, template)
    if not updated_template:
        raise HTTPException(status_code=404, detail="Шаблон корабля не найден")
    return updated_template

@router.delete("/templates/{template_id}")
def delete_ship_template(template_id: str, db: Session = Depends(get_db)):
    """Удалить шаблон корабля"""
    if not ShipService.delete_template(db, template_id):
        raise HTTPException(status_code=404, detail="Шаблон корабля не найден")
    return {"message": "Шаблон корабля успешно удален"} 