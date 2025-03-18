from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from structlog import BoundLogger
from datetime import datetime

from ..models.ships import ShipTemplate, ShipWeapon
from ..schemas.ships import ShipTemplateCreate, ShipTemplateUpdate, WeaponCharacteristics
from ..plugins.manager import PluginManager
from ..plugins.scout_ship import ScoutShipPlugin
from ..events.event_bus import EventBus

class ShipService:
    # Сервис для работы с шаблонами кораблей

    def __init__(self, plugin_manager: PluginManager, logger: BoundLogger, event_bus: EventBus):
        self.plugin_manager = plugin_manager
        self.logger = logger
        self.event_bus = event_bus
        self._register_default_plugins()

    def _register_default_plugins(self):
        # Регистрирует предустановленные плагины
        self.plugin_manager.register_plugin(ScoutShipPlugin)

    def get_templates(self, db: Session) -> List[ShipTemplate]:
        # Получить список всех шаблонов кораблей
        self.logger.info("getting_ship_templates")
        return db.query(ShipTemplate).all()

    def get_template(self, db: Session, template_id: str) -> Optional[ShipTemplate]:
        # Получить шаблон корабля по ID
        self.logger.info("getting_ship_template", template_id=template_id)
        return db.query(ShipTemplate).filter(ShipTemplate.id == template_id).first()

    async def create_template(self, db: Session, template: ShipTemplateCreate) -> ShipTemplate:
        # Создать новый шаблон корабля
        self.logger.info("creating_ship_template", template_data=template.dict())
        db_template = ShipTemplate(**template.dict())
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        
        # Отправляем событие создания шаблона
        await self.event_bus.publish(
            "template_created",
            {
                "template_id": db_template.id,
                "name": db_template.name,
                "type": db_template.type,
                "created_at": db_template.created_at.isoformat()
            }
        )
        
        return db_template

    async def create_template_from_plugin(self, db: Session, plugin_type: str) -> ShipTemplate:
        # Создать шаблон корабля из плагина
        self.logger.info("creating_ship_template_from_plugin", plugin_type=plugin_type)
        plugin = self.plugin_manager.get_plugin(plugin_type)
        if not plugin:
            self.logger.error("plugin_not_found", plugin_type=plugin_type)
            raise ValueError(f"Плагин {plugin_type} не найден")
        
        template_data = plugin.get_template_data()
        template = await self.create_template(db, template_data)
        
        # Отправляем событие создания корабля
        await self.event_bus.publish(
            "ship_created",
            {
                "ship_id": template.id,
                "template_id": template.id,
                "type": template.type,
                "name": template.name,
                "created_at": template.created_at.isoformat(),
                "parameters": template_data.dict()
            }
        )
        
        return template

    async def update_template(
        self, db: Session, template_id: str, template: ShipTemplateUpdate
    ) -> Optional[ShipTemplate]:
        # Обновить существующий шаблон корабля
        self.logger.info("updating_ship_template", template_id=template_id, template_data=template.dict())
        db_template = self.get_template(db, template_id)
        if not db_template:
            self.logger.warning("template_not_found", template_id=template_id)
            return None
        
        for key, value in template.dict(exclude_unset=True).items():
            setattr(db_template, key, value)
        
        db.commit()
        db.refresh(db_template)
        
        # Отправляем событие обновления шаблона
        await self.event_bus.publish(
            "template_updated",
            {
                "template_id": db_template.id,
                "name": db_template.name,
                "type": db_template.type,
                "updated_at": datetime.utcnow().isoformat()
            }
        )
        
        return db_template

    async def delete_template(self, db: Session, template_id: str) -> bool:
        # Удалить шаблон корабля
        self.logger.info("deleting_ship_template", template_id=template_id)
        db_template = self.get_template(db, template_id)
        if not db_template:
            self.logger.warning("template_not_found", template_id=template_id)
            return False
        
        db.delete(db_template)
        db.commit()
        
        # Отправляем событие удаления шаблона
        await self.event_bus.publish(
            "template_deleted",
            {
                "template_id": template_id,
                "deleted_at": datetime.utcnow().isoformat()
            }
        )
        
        return True

    def get_available_plugin_types(self) -> List[str]:
        # Получить список доступных типов плагинов
        self.logger.info("getting_available_plugin_types")
        return self.plugin_manager.get_available_ship_types() 