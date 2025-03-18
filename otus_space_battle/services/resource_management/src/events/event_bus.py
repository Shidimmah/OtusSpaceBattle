from typing import Any, Dict, List, Callable
import aiohttp
import json
from datetime import datetime
from structlog import BoundLogger

class EventBus:
    # Система событий для взаимодействия между сервисами
    
    def __init__(self, logger: BoundLogger):
        self.logger = logger
        self.analytics_url = "http://analytics_service:8004"
        self.battle_service_url = "http://battle_service:8003"
        self._handlers: Dict[str, List[Callable]] = {}
    
    async def publish(self, event_type: str, data: Dict[str, Any]) -> None:
        # Публикует событие
        
        Args:
            event_type: Тип события
            data: Данные события
        self.logger.info(
            "publishing_event",
            event_type=event_type,
            data=data
        )
        
        # Добавляем метаданные
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Отправляем в сервис аналитики
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    f"{self.analytics_url}/analytics/events/{event_type}",
                    json=event
                )
        except Exception as e:
            self.logger.error(
                "failed_to_send_to_analytics",
                event_type=event_type,
                error=str(e)
            )
        
        # Отправляем в боевой сервис, если это событие создания корабля
        if event_type == "ship_created":
            try:
                async with aiohttp.ClientSession() as session:
                    await session.post(
                        f"{self.battle_service_url}/battle/ships",
                        json=data
                    )
            except Exception as e:
                self.logger.error(
                    "failed_to_send_to_battle_service",
                    event_type=event_type,
                    error=str(e)
                )
        
        # Вызываем локальные обработчики
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    self.logger.error(
                        "handler_error",
                        event_type=event_type,
                        error=str(e)
                    )
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        # Подписывается на события
        
        Args:
            event_type: Тип события
            handler: Обработчик события
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler) 