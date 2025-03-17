from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from ..models.ships import ShipTemplate, ShipWeapon
from ..schemas.ships import ShipTemplateCreate, ShipTemplateUpdate, WeaponCharacteristics

class ShipService:
    """Сервис для работы с шаблонами кораблей"""

    @staticmethod
    def get_templates(db: Session) -> List[ShipTemplate]:
        """Получить список всех шаблонов кораблей"""
        return db.query(ShipTemplate).all()

    @staticmethod
    def get_template(db: Session, template_id: str) -> Optional[ShipTemplate]:
        """Получить шаблон корабля по ID"""
        return db.query(ShipTemplate).filter(ShipTemplate.id == template_id).first()

    @staticmethod
    def create_template(db: Session, template: ShipTemplateCreate) -> ShipTemplate:
        """Создать новый шаблон корабля"""
        try:
            # Создаем шаблон корабля
            db_template = ShipTemplate(
                id=template.id,
                name=template.name,
                description=template.description,
                max_speed=template.characteristics.max_speed,
                acceleration=template.characteristics.acceleration,
                rotation_speed=template.characteristics.rotation_speed,
                fuel_capacity=template.characteristics.fuel_capacity,
                fuel_consumption=template.characteristics.fuel_consumption,
                hull_strength=template.characteristics.hull_strength,
                shield_strength=template.characteristics.shield_strength,
                length=template.size[0],
                width=template.size[1]
            )
            db.add(db_template)

            # Добавляем оружие
            for weapon in template.weapons:
                db_weapon = ShipWeapon(
                    ship_template=db_template,
                    type=weapon.type,
                    damage=weapon.damage,
                    cooldown=weapon.cooldown,
                    ammunition=weapon.ammunition,
                    range=weapon.range
                )
                db.add(db_weapon)

            db.commit()
            db.refresh(db_template)
            return db_template

        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Шаблон с таким ID или именем уже существует")

    @staticmethod
    def update_template(db: Session, template_id: str, template: ShipTemplateUpdate) -> Optional[ShipTemplate]:
        """Обновить существующий шаблон корабля"""
        db_template = ShipService.get_template(db, template_id)
        if not db_template:
            return None

        if db_template.is_default:
            raise HTTPException(status_code=400, detail="Нельзя изменять предустановленные шаблоны")

        try:
            # Обновляем основные характеристики
            if template.name is not None:
                db_template.name = template.name
            if template.description is not None:
                db_template.description = template.description
            if template.characteristics is not None:
                db_template.max_speed = template.characteristics.max_speed
                db_template.acceleration = template.characteristics.acceleration
                db_template.rotation_speed = template.characteristics.rotation_speed
                db_template.fuel_capacity = template.characteristics.fuel_capacity
                db_template.fuel_consumption = template.characteristics.fuel_consumption
                db_template.hull_strength = template.characteristics.hull_strength
                db_template.shield_strength = template.characteristics.shield_strength
            if template.size is not None:
                db_template.length = template.size[0]
                db_template.width = template.size[1]

            # Обновляем оружие
            if template.weapons is not None:
                # Удаляем старое оружие
                db.query(ShipWeapon).filter(ShipWeapon.ship_template_id == template_id).delete()
                
                # Добавляем новое оружие
                for weapon in template.weapons:
                    db_weapon = ShipWeapon(
                        ship_template=db_template,
                        type=weapon.type,
                        damage=weapon.damage,
                        cooldown=weapon.cooldown,
                        ammunition=weapon.ammunition,
                        range=weapon.range
                    )
                    db.add(db_weapon)

            db.commit()
            db.refresh(db_template)
            return db_template

        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Шаблон с таким именем уже существует")

    @staticmethod
    def delete_template(db: Session, template_id: str) -> bool:
        """Удалить шаблон корабля"""
        db_template = ShipService.get_template(db, template_id)
        if not db_template:
            return False

        if db_template.is_default:
            raise HTTPException(status_code=400, detail="Нельзя удалять предустановленные шаблоны")

        if db_template.in_use:
            raise HTTPException(status_code=400, detail="Нельзя удалить шаблон, который используется")

        db.delete(db_template)
        db.commit()
        return True 