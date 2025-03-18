from datetime import timedelta
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.analytics import AnalyticsService
from ..schemas.analytics import (
    ShipCreationEventCreate,
    ShipTemplateCreate,
    ShipUsageStatsCreate,
    AnalyticsSummary
)

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.post("/events/ship-creation")
async def record_ship_creation(
    event: ShipCreationEventCreate,
    template: ShipTemplateCreate,
    db: Session = Depends(get_db),
    analytics_service: AnalyticsService = Depends()
):
    # Записать событие создания корабля
    return analytics_service.record_ship_creation(db, event, template)

@router.post("/stats/ship-usage")
async def update_ship_usage(
    stats: ShipUsageStatsCreate,
    db: Session = Depends(get_db),
    analytics_service: AnalyticsService = Depends()
):
    # Обновить статистику использования корабля
    return analytics_service.update_ship_usage(db, stats)

@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    time_range_days: int = 30,
    db: Session = Depends(get_db),
    analytics_service: AnalyticsService = Depends()
):
    # Получить сводную статистику
    return analytics_service.get_analytics_summary(
        db,
        time_range=timedelta(days=time_range_days)
    )

@router.get("/templates/{template_id}/stats")
async def get_template_usage_stats(
    template_id: str,
    time_range_days: int = 30,
    db: Session = Depends(get_db),
    analytics_service: AnalyticsService = Depends()
):
    # Получить статистику использования шаблона
    try:
        return analytics_service.get_template_usage_stats(
            db,
            template_id,
            time_range=timedelta(days=time_range_days)
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Шаблон {template_id} не найден") 