from prometheus_client import start_http_server, Counter, Histogram, Gauge
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from functools import wraps
import time
import structlog
from typing import Optional, Type, List, Dict, Any
from .metrics import (
    ServiceMetrics,
    BattleMechanicsMetrics,
    ResourceManagementMetrics,
    RankingMetrics,
    AnalyticsMetrics,
    ApiGatewayMetrics
)

# Настройка структурированного логирования
logger = structlog.get_logger()

# Словарь для хранения метрик сервисов
METRICS = {
    "battle_mechanics": BattleMechanicsMetrics(),
    "resource_management": ResourceManagementMetrics(),
    "ranking": RankingMetrics(),
    "analytics": AnalyticsMetrics(),
    "api_gateway": ApiGatewayMetrics()
}

def get_metrics(service_name: str) -> ServiceMetrics:
    """Получение метрик для конкретного сервиса"""
    return METRICS.get(service_name)

def setup_monitoring(app, service_name: str, metrics_port: int = 8000):
    """Настройка мониторинга для FastAPI приложения"""
    # Настройка OpenTelemetry
    trace.set_tracer_provider(TracerProvider())
    metrics.set_meter_provider(MeterProvider())
    
    # Инструментирование FastAPI
    FastAPIInstrumentor.instrument_app(app)
    
    # Запуск сервера метрик Prometheus
    start_http_server(metrics_port)
    
    # Получаем метрики для сервиса
    service_metrics = get_metrics(service_name)
    if not service_metrics:
        raise ValueError(f"Unknown service: {service_name}")
    
    # Добавляем middleware для сбора метрик
    @app.middleware("http")
    async def monitoring_middleware(request, call_next):
        start_time = time.time()
        
        try:
            # Увеличиваем счетчик активных соединений
            service_metrics.active_connections.labels(service=service_name).inc()
            
            response = await call_next(request)
            
            # Записываем метрики запроса
            service_metrics.request_count.labels(
                service=service_name,
                endpoint=request.url.path,
                method=request.method
            ).inc()
            
            service_metrics.request_latency.labels(
                service=service_name,
                endpoint=request.url.path
            ).observe(time.time() - start_time)
            
            return response
            
        except Exception as e:
            # Записываем ошибки
            service_metrics.error_count.labels(
                service=service_name,
                error_type=type(e).__name__
            ).inc()
            
            # Логируем ошибку
            logger.error(
                "request_error",
                service=service_name,
                endpoint=request.url.path,
                error=str(e),
                error_type=type(e).__name__
            )
            raise
            
        finally:
            # Уменьшаем счетчик активных соединений
            service_metrics.active_connections.labels(service=service_name).dec()

def log_function_call(func):
    """Декоратор для логирования вызовов функций"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(
            "function_call",
            function=func.__name__,
            args=args,
            kwargs=kwargs
        )
        
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            logger.info(
                "function_success",
                function=func.__name__,
                duration=duration
            )
            return result
            
        except Exception as e:
            logger.error(
                "function_error",
                function=func.__name__,
                error=str(e),
                error_type=type(e).__name__
            )
            raise
            
    return wrapper 

def create_counter(name: str, documentation: str, labels: List[str] = None, service_name: str = None) -> Counter:
    """Создание счетчика Prometheus с предотвращением автоматической регистрации"""
    if service_name:
        name = f"{service_name}_{name}"
    return Counter(name, documentation, labels or [], registry=None)

def create_histogram(name: str, documentation: str, labels: List[str] = None, 
                    buckets=None, service_name: str = None) -> Histogram:
    """Создание гистограммы Prometheus с предотвращением автоматической регистрации"""
    if service_name:
        name = f"{service_name}_{name}"
    return Histogram(name, documentation, labels or [], buckets=buckets, registry=None)

def create_gauge(name: str, documentation: str, labels: List[str] = None, service_name: str = None) -> Gauge:
    """Создание измерителя Prometheus с предотвращением автоматической регистрации"""
    if service_name:
        name = f"{service_name}_{name}"
    return Gauge(name, documentation, labels or [], registry=None) 