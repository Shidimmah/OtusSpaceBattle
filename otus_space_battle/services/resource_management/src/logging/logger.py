import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import structlog
from elasticsearch import AsyncElasticsearch
from structlog.types import Processor

# Настройка базового логгера
logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

# Процессоры для structlog
def add_service_name(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    # Добавляет имя сервиса в лог
    event_dict["service"] = "resource_management"
    return event_dict

def add_timestamp(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    # Добавляет временную метку в лог
    event_dict["timestamp"] = structlog.processors.TimeStamper(fmt="iso")._add_timestamp(logger, method_name, event_dict)
    return event_dict

class ElasticsearchHandler:
    # Handler для отправки логов в Elasticsearch
    
    def __init__(self, host: str, port: int, index: str):
        self.client = AsyncElasticsearch([f"http://{host}:{port}"])
        self.index = index
        self._setup_index_lifecycle()
    
    async def _setup_index_lifecycle(self) -> None:
        # Настраивает политику жизненного цикла индекса
        policy_name = f"{self.index}-policy"
        
        # Создаем политику жизненного цикла
        await self.client.ilm.put_lifecycle(
            policy=policy_name,
            body={
                "policy": {
                    "phases": {
                        "hot": {
                            "min_age": "0ms",
                            "actions": {
                                "rollover": {
                                    "max_size": "2gb",
                                    "max_age": "7d"
                                }
                            }
                        },
                        "delete": {
                            "min_age": "30d",
                            "actions": {
                                "delete": {}
                            }
                        }
                    }
                }
            }
        )
        
        # Применяем политику к индексу
        await self.client.indices.put_settings(
            index=self.index,
            body={
                "index.lifecycle.name": policy_name
            }
        )
    
    async def emit(self, event_dict: Dict[str, Any]) -> None:
        # Отправляет лог в Elasticsearch
        try:
            await self.client.index(
                index=self.index,
                document={
                    **event_dict,
                    "@timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            print(f"Error sending log to Elasticsearch: {e}")

# Список процессоров для логирования
PROCESSORS: list[Processor] = [
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.add_log_level,
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.processors.UnicodeDecoder(),
    structlog.processors.JSONRenderer(),
]

def setup_logging(
    log_level: str = "INFO",
    log_file: str | None = None,
    elasticsearch_host: str | None = None,
    elasticsearch_port: int | None = None,
    elasticsearch_index: str | None = None,
    max_bytes: int = 2 * 1024 * 1024 * 1024,  # 2GB
    backup_count: int = 5
) -> structlog.BoundLogger:
    # Настраивает логирование
    
    Args:
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Путь к файлу логов (если None, логи идут в stdout)
        elasticsearch_host: Хост Elasticsearch
        elasticsearch_port: Порт Elasticsearch
        elasticsearch_index: Имя индекса в Elasticsearch
        max_bytes: Максимальный размер файла лога в байтах
        backup_count: Количество резервных копий файла лога
    
    Returns:
        Настроенный логгер
    # Создаем директорию для логов, если указан файл
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Добавляем ротирующий файловый handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        logging.getLogger().addHandler(file_handler)
    
    # Настраиваем structlog
    structlog.configure(
        processors=PROCESSORS,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, log_level.upper())),
        cache_logger_on_first_use=True,
    )
    
    # Создаем логгер
    logger = structlog.get_logger(
        processors=PROCESSORS + [add_service_name, add_timestamp]
    )
    
    # Добавляем Elasticsearch handler, если указаны настройки
    if all([elasticsearch_host, elasticsearch_port, elasticsearch_index]):
        es_handler = ElasticsearchHandler(
            host=elasticsearch_host,
            port=elasticsearch_port,
            index=elasticsearch_index
        )
        logger = logger.bind(es_handler=es_handler)
    
    return logger 