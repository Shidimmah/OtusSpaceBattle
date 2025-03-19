import pytest
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient
import time
from prometheus_client import REGISTRY, CollectorRegistry
from common.monitoring import (
    setup_monitoring,
    log_function_call,
    get_metrics
)

# Используем одну общую фикстуру на уровне модуля, чтобы избежать дублирования
@pytest.fixture(scope="module")
def test_app():
    """Фикстура для тестового FastAPI приложения"""
    # Создаем отдельный реестр для тестов
    test_registry = CollectorRegistry()
    app = FastAPI()
    # Здесь можно переопределить реестр в setup_monitoring
    setup_monitoring(app, "test_service", metrics_port=8002)
    return app

@pytest.fixture(scope="module")
def test_client(test_app):
    """Фикстура для тестового клиента"""
    return TestClient(test_app)

def test_metrics_initialization(test_app):
    """Тест инициализации метрик"""
    metrics = get_metrics("test_service")
    assert metrics is not None
    assert metrics.service_name == "test_service"

def test_request_metrics(test_app, test_client):
    """Тест сбора метрик запросов"""
    @test_app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    # Делаем тестовый запрос
    response = test_client.get("/test")
    assert response.status_code == 200
    
    # Проверяем метрики
    metrics = get_metrics("test_service")
    
    # Проверяем счетчик запросов
    assert float(metrics.request_count.labels(
        service="test_service",
        endpoint="/test",
        method="GET"
    )._value.get()) > 0
    
    # Проверяем метрику активных соединений
    assert float(metrics.active_connections.labels(
        service="test_service"
    )._value.get()) == 0

def test_error_metrics(test_app, test_client):
    """Тест сбора метрик ошибок"""
    @test_app.get("/error")
    async def error_endpoint():
        raise ValueError("Test error")
    
    # Делаем запрос, который вызовет ошибку
    response = test_client.get("/error")
    assert response.status_code == 500
    
    # Проверяем метрики ошибок
    metrics = get_metrics("test_service")
    assert float(metrics.error_count.labels(
        service="test_service",
        error_type="ValueError"
    )._value.get()) > 0

@pytest.mark.asyncio
async def test_log_function_call_decorator():
    """Тест декоратора логирования вызовов функций"""
    @log_function_call
    async def test_function(x: int, y: int):
        return x + y
    
    # Вызываем функцию и проверяем результат
    result = await test_function(1, 2)
    assert result == 3

def test_latency_metrics(test_app, test_client):
    """Тест метрик латентности"""
    @test_app.get("/slow")
    async def slow_endpoint():
        time.sleep(0.1)  # Имитируем медленный ответ
        return {"message": "slow"}
    
    # Делаем запрос к медленному эндпоинту
    response = test_client.get("/slow")
    assert response.status_code == 200
    
    # Проверяем метрики латентности
    metrics = get_metrics("test_service")
    histogram = metrics.request_latency.labels(
        service="test_service",
        endpoint="/slow"
    )
    
    # Проверяем, что значение латентности было записано
    assert histogram._sum.get() > 0

def test_concurrent_requests(test_app, test_client):
    """Тест обработки одновременных запросов"""
    @test_app.get("/concurrent")
    async def concurrent_endpoint():
        return {"message": "concurrent"}
    
    # Делаем несколько одновременных запросов
    responses = []
    for _ in range(5):
        responses.append(test_client.get("/concurrent"))
    
    # Проверяем, что все запросы успешны
    for response in responses:
        assert response.status_code == 200
    
    # Проверяем метрики
    metrics = get_metrics("test_service")
    assert float(metrics.request_count.labels(
        service="test_service",
        endpoint="/concurrent",
        method="GET"
    )._value.get()) == 5

def test_middleware_exception_handling(test_app, test_client):
    """Тест обработки исключений в middleware"""
    @test_app.get("/exception")
    async def exception_endpoint():
        raise RuntimeError("Unexpected error")
    
    # Делаем запрос, который вызовет исключение
    response = test_client.get("/exception")
    assert response.status_code == 500
    
    # Проверяем, что метрики ошибок обновились
    metrics = get_metrics("test_service")
    assert float(metrics.error_count.labels(
        service="test_service",
        error_type="RuntimeError"
    )._value.get()) > 0

def test_metrics_reset(test_app, test_client):
    """Тест сброса метрик"""
    @test_app.get("/reset")
    async def reset_endpoint():
        return {"message": "reset"}
    
    # Делаем запрос
    response = test_client.get("/reset")
    assert response.status_code == 200
    
    # Получаем текущие значения метрик
    metrics = get_metrics("test_service")
    initial_count = float(metrics.request_count.labels(
        service="test_service",
        endpoint="/reset",
        method="GET"
    )._value.get())
    
    # Делаем еще один запрос
    response = test_client.get("/reset")
    assert response.status_code == 200
    
    # Проверяем, что счетчик увеличился
    new_count = float(metrics.request_count.labels(
        service="test_service",
        endpoint="/reset",
        method="GET"
    )._value.get())
    assert new_count > initial_count 