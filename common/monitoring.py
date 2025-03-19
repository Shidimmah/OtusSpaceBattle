from otus_space_battle.common.monitoring import (
    setup_monitoring as original_setup_monitoring,
    get_metrics,
    log_function_call,
    METRICS
)
from prometheus_client import CollectorRegistry

# Сохраняем копию оригинальной функции
_original_setup = original_setup_monitoring

# Переопределяем функцию setup_monitoring для тестов
def setup_monitoring(app, service_name: str, metrics_port: int = 8000, registry=None):
    """
    Версия setup_monitoring для тестов, которая позволяет использовать отдельный реестр
    для метрик, чтобы избежать дублирования.
    """
    # При первом вызове очищаем словарь метрик для тестов
    if service_name == "test_service" and service_name not in METRICS:
        # Используем временную копию класса метрик для тестов
        # Но перезаписываем ее при каждом запуске тестов, чтобы избежать дублирования
        METRICS.pop("test_service", None)
        METRICS["test_service"] = METRICS["api_gateway"].__class__()
        METRICS["test_service"].service_name = "test_service"
    
    # Вызываем оригинальную функцию
    return _original_setup(app, service_name, metrics_port) 