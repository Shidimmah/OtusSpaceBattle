from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from structlog import BoundLogger

from ..models.analytics import ShipCreationEvent, ShipTemplate, ShipUsageStats
from ..schemas.analytics import ShipCreationEventCreate, ShipTemplateCreate

class EventHandlers:
    # Обработчики событий для аналитики
    
    def __init__(self, db: Session, logger: BoundLogger):
        self.db = db
        self.logger = logger
    
    async def handle_template_created(self, event: Dict[str, Any]) -> None:
        # Обработка события создания шаблона
        self.logger.info(
            "handling_template_created",
            template_id=event["data"]["template_id"]
        )
        
        template = ShipTemplateCreate(
            id=event["data"]["template_id"],
            name=event["data"]["name"],
            type=event["data"]["type"]
        )
        
        db_template = ShipTemplate(**template.dict())
        self.db.add(db_template)
        self.db.commit()
    
    async def handle_ship_created(self, event: Dict[str, Any]) -> None:
        # Обработка события создания корабля
        self.logger.info(
            "handling_ship_created",
            ship_id=event["data"]["ship_id"]
        )
        
        # Создаем событие создания корабля
        creation_event = ShipCreationEventCreate(
            ship_id=event["data"]["ship_id"],
            template_id=event["data"]["template_id"],
            creation_time_ms=event["data"].get("creation_time_ms", 0)
        )
        
        db_event = ShipCreationEvent(**creation_event.dict())
        self.db.add(db_event)
        
        # Создаем начальную статистику использования
        usage_stats = ShipUsageStats(
            ship_id=event["data"]["ship_id"],
            template_id=event["data"]["template_id"],
            last_used_at=datetime.utcnow(),
            total_usage_time=0,
            battles_participated=0
        )
        self.db.add(usage_stats)
        
        self.db.commit()
    
    async def handle_template_updated(self, event: Dict[str, Any]) -> None:
        # Обработка события обновления шаблона
        self.logger.info(
            "handling_template_updated",
            template_id=event["data"]["template_id"]
        )
        
        db_template = self.db.query(ShipTemplate).filter(
            ShipTemplate.id == event["data"]["template_id"]
        ).first()
        
        if db_template:
            db_template.name = event["data"]["name"]
            db_template.type = event["data"]["type"]
            self.db.commit()
    
    async def handle_template_deleted(self, event: Dict[str, Any]) -> None:
        # Обработка события удаления шаблона
        self.logger.info(
            "handling_template_deleted",
            template_id=event["data"]["template_id"]
        )
        
        # Удаляем связанные события и статистику
        self.db.query(ShipCreationEvent).filter(
            ShipCreationEvent.template_id == event["data"]["template_id"]
        ).delete()
        
        self.db.query(ShipUsageStats).filter(
            ShipUsageStats.template_id == event["data"]["template_id"]
        ).delete()
        
        self.db.query(ShipTemplate).filter(
            ShipTemplate.id == event["data"]["template_id"]
        ).delete()
        
        self.db.commit()
    
    async def handle_battle_started(self, event: Dict[str, Any]) -> None:
        # Обработка события начала битвы
        self.logger.info(
            "handling_battle_started",
            battle_id=event["data"]["battle_id"]
        )
        
        # Обновляем статистику использования для каждого корабля
        for ship_id in event["data"]["ship_ids"]:
            stats = self.db.query(ShipUsageStats).filter(
                ShipUsageStats.ship_id == ship_id
            ).first()
            
            if stats:
                stats.battles_participated += 1
                stats.last_used_at = datetime.utcnow()
        
        self.db.commit()
    
    async def handle_battle_ended(self, event: Dict[str, Any]) -> None:
        # Обработка события окончания битвы
        self.logger.info(
            "handling_battle_ended",
            battle_id=event["data"]["battle_id"]
        )
        
        # Обновляем время использования для каждого корабля
        for ship_id, battle_time in event["data"]["ship_battle_times"].items():
            stats = self.db.query(ShipUsageStats).filter(
                ShipUsageStats.ship_id == ship_id
            ).first()
            
            if stats:
                stats.total_usage_time += battle_time
                stats.last_used_at = datetime.utcnow()
        
        self.db.commit() 