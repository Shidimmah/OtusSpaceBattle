from datetime import datetime, timedelta
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from structlog import BoundLogger

from ..models.analytics import ShipCreationEvent, ShipTemplate, ShipUsageStats
from ..schemas.analytics import (
    ShipCreationEventCreate,
    ShipTemplateCreate,
    ShipUsageStatsCreate,
    AnalyticsSummary
)

class AnalyticsService:
    # Сервис для работы с аналитикой
    
    def __init__(self, logger: BoundLogger):
        self.logger = logger
    
    def record_ship_creation(
        self,
        db: Session,
        event: ShipCreationEventCreate,
        template: ShipTemplateCreate
    ) -> ShipCreationEvent:
        # Записать событие создания корабля
        self.logger.info(
            "recording_ship_creation",
            ship_id=event.ship_id,
            template_id=event.template_id,
            creation_time_ms=event.creation_time_ms
        )
        
        # Создаем или обновляем шаблон
        db_template = db.query(ShipTemplate).filter(ShipTemplate.id == template.id).first()
        if not db_template:
            db_template = ShipTemplate(**template.dict())
            db.add(db_template)
        
        # Создаем событие
        db_event = ShipCreationEvent(**event.dict())
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        
        return db_event
    
    def update_ship_usage(
        self,
        db: Session,
        stats: ShipUsageStatsCreate
    ) -> ShipUsageStats:
        # Обновить статистику использования корабля
        self.logger.info(
            "updating_ship_usage",
            ship_id=stats.ship_id,
            template_id=stats.template_id
        )
        
        db_stats = db.query(ShipUsageStats).filter(
            ShipUsageStats.ship_id == stats.ship_id
        ).first()
        
        if not db_stats:
            db_stats = ShipUsageStats(**stats.dict())
            db.add(db_stats)
        else:
            for key, value in stats.dict().items():
                setattr(db_stats, key, value)
            db_stats.last_used_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_stats)
        return db_stats
    
    def get_analytics_summary(
        self,
        db: Session,
        time_range: timedelta = timedelta(days=30)
    ) -> AnalyticsSummary:
        # Получить сводную статистику
        self.logger.info("getting_analytics_summary")
        
        # Получаем базовую статистику
        total_ships = db.query(func.count(ShipCreationEvent.id)).scalar()
        total_time = db.query(func.sum(ShipCreationEvent.creation_time_ms)).scalar() or 0
        avg_time = total_time / total_ships if total_ships > 0 else 0
        
        # Статистика по типам кораблей
        ships_by_type = dict(
            db.query(
                ShipTemplate.type,
                func.count(ShipCreationEvent.id)
            ).join(
                ShipCreationEvent
            ).group_by(
                ShipTemplate.type
            ).all()
        )
        
        # Самый используемый шаблон
        most_used = db.query(
            ShipTemplate.id,
            func.count(ShipUsageStats.id)
        ).join(
            ShipUsageStats
        ).group_by(
            ShipTemplate.id
        ).order_by(
            func.count(ShipUsageStats.id).desc()
        ).first()
        
        most_used_template = most_used[0] if most_used else None
        
        # Общее количество битв
        total_battles = db.query(func.sum(ShipUsageStats.battles_participated)).scalar() or 0
        
        return AnalyticsSummary(
            total_ships_created=total_ships,
            total_creation_time_ms=total_time,
            average_creation_time_ms=avg_time,
            ships_by_type=ships_by_type,
            most_used_template=most_used_template,
            total_battles=total_battles
        )
    
    def get_template_usage_stats(
        self,
        db: Session,
        template_id: str,
        time_range: timedelta = timedelta(days=30)
    ) -> Dict:
        # Получить статистику использования шаблона
        self.logger.info("getting_template_usage_stats", template_id=template_id)
        
        # Количество созданных кораблей
        ships_created = db.query(func.count(ShipCreationEvent.id)).filter(
            ShipCreationEvent.template_id == template_id,
            ShipCreationEvent.created_at >= datetime.utcnow() - time_range
        ).scalar()
        
        # Среднее время создания
        avg_creation_time = db.query(func.avg(ShipCreationEvent.creation_time_ms)).filter(
            ShipCreationEvent.template_id == template_id,
            ShipCreationEvent.created_at >= datetime.utcnow() - time_range
        ).scalar() or 0
        
        # Статистика использования
        usage_stats = db.query(
            func.avg(ShipUsageStats.total_usage_time),
            func.avg(ShipUsageStats.battles_participated)
        ).join(
            ShipCreationEvent,
            ShipUsageStats.ship_id == ShipCreationEvent.ship_id
        ).filter(
            ShipCreationEvent.template_id == template_id,
            ShipUsageStats.last_used_at >= datetime.utcnow() - time_range
        ).first()
        
        return {
            "ships_created": ships_created,
            "average_creation_time_ms": avg_creation_time,
            "average_usage_time": usage_stats[0] or 0,
            "average_battles": usage_stats[1] or 0
        } 