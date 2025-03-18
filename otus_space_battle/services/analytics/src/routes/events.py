from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from structlog import BoundLogger

from ..database import get_db
from ..services.event_handlers import EventHandlers
from ..logging.logger import get_logger

router = APIRouter(prefix="/analytics/events", tags=["events"])

@router.post("/template_created")
async def handle_template_created(
    event: Dict[str, Any],
    db: Session = Depends(get_db),
    logger: BoundLogger = Depends(get_logger)
) -> Dict[str, str]:
    # Обработка события создания шаблона
    handlers = EventHandlers(db, logger)
    await handlers.handle_template_created(event)
    return {"status": "success"}

@router.post("/ship_created")
async def handle_ship_created(
    event: Dict[str, Any],
    db: Session = Depends(get_db),
    logger: BoundLogger = Depends(get_logger)
) -> Dict[str, str]:
    # Обработка события создания корабля
    handlers = EventHandlers(db, logger)
    await handlers.handle_ship_created(event)
    return {"status": "success"}

@router.post("/template_updated")
async def handle_template_updated(
    event: Dict[str, Any],
    db: Session = Depends(get_db),
    logger: BoundLogger = Depends(get_logger)
) -> Dict[str, str]:
    # Обработка события обновления шаблона
    handlers = EventHandlers(db, logger)
    await handlers.handle_template_updated(event)
    return {"status": "success"}

@router.post("/template_deleted")
async def handle_template_deleted(
    event: Dict[str, Any],
    db: Session = Depends(get_db),
    logger: BoundLogger = Depends(get_logger)
) -> Dict[str, str]:
    # Обработка события удаления шаблона
    handlers = EventHandlers(db, logger)
    await handlers.handle_template_deleted(event)
    return {"status": "success"}

@router.post("/battle_started")
async def handle_battle_started(
    event: Dict[str, Any],
    db: Session = Depends(get_db),
    logger: BoundLogger = Depends(get_logger)
) -> Dict[str, str]:
    # Обработка события начала битвы
    handlers = EventHandlers(db, logger)
    await handlers.handle_battle_started(event)
    return {"status": "success"}

@router.post("/battle_ended")
async def handle_battle_ended(
    event: Dict[str, Any],
    db: Session = Depends(get_db),
    logger: BoundLogger = Depends(get_logger)
) -> Dict[str, str]:
    # Обработка события окончания битвы
    handlers = EventHandlers(db, logger)
    await handlers.handle_battle_ended(event)
    return {"status": "success"} 