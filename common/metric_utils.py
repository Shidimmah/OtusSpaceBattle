from prometheus_client import Counter, Histogram, Gauge
from typing import List, Optional

def create_counter(name: str, documentation: str, labels: List[str] = None, service_name: str = None) -> Counter:
    """Создание счетчика Prometheus с предотвращением автоматической регистрации
    
    Args:
        name: Имя метрики
        documentation: Документация/описание метрики
        labels: Список меток для метрики
        service_name: Имя сервиса (будет добавлено как префикс к имени)
    
    Returns:
        Counter: Экземпляр счетчика Prometheus
    """
    if service_name:
        name = f"{service_name}_{name}"
    return Counter(name, documentation, labels or [], registry=None)

def create_histogram(name: str, documentation: str, labels: List[str] = None, 
                    buckets=None, service_name: str = None) -> Histogram:
    """Создание гистограммы Prometheus с предотвращением автоматической регистрации
    
    Args:
        name: Имя метрики
        documentation: Документация/описание метрики
        labels: Список меток для метрики
        buckets: Корзины гистограммы
        service_name: Имя сервиса (будет добавлено как префикс к имени)
    
    Returns:
        Histogram: Экземпляр гистограммы Prometheus
    """
    if service_name:
        name = f"{service_name}_{name}"
    return Histogram(name, documentation, labels or [], buckets=buckets, registry=None)

def create_gauge(name: str, documentation: str, labels: List[str] = None, service_name: str = None) -> Gauge:
    """Создание измерителя Prometheus с предотвращением автоматической регистрации
    
    Args:
        name: Имя метрики
        documentation: Документация/описание метрики
        labels: Список меток для метрики
        service_name: Имя сервиса (будет добавлено как префикс к имени)
    
    Returns:
        Gauge: Экземпляр измерителя Prometheus
    """
    if service_name:
        name = f"{service_name}_{name}"
    return Gauge(name, documentation, labels or [], registry=None)

def reset_metrics_for_testing():
    """Сбросить состояние метрик для тестирования
    
    Эта функция удаляет все собранные метрики из глобального реестра Prometheus,
    что позволяет избежать конфликтов между тестами. Используется в фикстурах pytest.
    """
    from prometheus_client import REGISTRY
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        REGISTRY.unregister(collector) 