from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum
import httpx

from ..config import get_settings
from ..auth import get_current_admin_user

router = APIRouter(prefix="/ships", tags=["ships"])

class WeaponType(str, Enum):
    """Типы оружия"""
    TORPEDO = "torpedo"  # Торпеды
    LASER = "laser"     # Лазерное оружие
    MISSILE = "missile" # Ракеты

class WeaponCharacteristics(BaseModel):
    """Характеристики оружия"""
    type: WeaponType
    damage: float = Field(..., gt=0)
    cooldown: float = Field(..., gt=0)
    ammunition: int = Field(..., ge=-1)
    range: float = Field(..., gt=0)

class ShipCharacteristics(BaseModel):
    """Характеристики корабля"""
    max_speed: float = Field(..., gt=0)
    acceleration: float = Field(..., gt=0)
    rotation_speed: float = Field(..., gt=0)
    fuel_capacity: float = Field(..., gt=0)
    fuel_consumption: float = Field(..., gt=0)
    hull_strength: float = Field(..., gt=0)
    shield_strength: float = Field(..., gt=0)

class ShipTemplate(BaseModel):
    """Шаблон корабля"""
    id: Optional[str] = None
    name: str
    description: str
    characteristics: ShipCharacteristics
    weapons: List[WeaponCharacteristics]
    size: tuple[float, float] = Field(default=(10.0, 10.0))
    is_default: bool = False
    in_use: bool = False

async def get_resource_service():
    """Получить URL сервиса управления ресурсами"""
    settings = get_settings()
    return settings.resource_management_url

@router.get("/templates", response_model=List[ShipTemplate])
async def get_ship_templates():
    """Получить список всех доступных шаблонов кораблей"""
    resource_url = await get_resource_service()
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{resource_url}/ships/templates")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()

@router.get("/templates/{template_id}", response_model=ShipTemplate)
async def get_ship_template(template_id: str):
    """Получить шаблон корабля по ID"""
    resource_url = await get_resource_service()
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{resource_url}/ships/templates/{template_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()

@router.post("/templates", response_model=ShipTemplate)
async def create_ship_template(template: ShipTemplate, admin: dict = Depends(get_current_admin_user)):
    """Создать новый шаблон корабля (только для администраторов)"""
    resource_url = await get_resource_service()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{resource_url}/ships/templates",
            json=template.dict(exclude_unset=True),
            headers={"Authorization": f"Bearer {admin['token']}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()

@router.put("/templates/{template_id}", response_model=ShipTemplate)
async def update_ship_template(
    template_id: str,
    template: ShipTemplate,
    admin: dict = Depends(get_current_admin_user)
):
    """Обновить существующий шаблон корабля (только для администраторов)"""
    resource_url = await get_resource_service()
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{resource_url}/ships/templates/{template_id}",
            json=template.dict(exclude_unset=True),
            headers={"Authorization": f"Bearer {admin['token']}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()

@router.delete("/templates/{template_id}")
async def delete_ship_template(template_id: str, admin: dict = Depends(get_current_admin_user)):
    """Удалить шаблон корабля (только для администраторов)"""
    resource_url = await get_resource_service()
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{resource_url}/ships/templates/{template_id}",
            headers={"Authorization": f"Bearer {admin['token']}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json() 