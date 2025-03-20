import pytest
import httpx
from unittest.mock import MagicMock, patch
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from common.monitoring import get_metrics, setup_monitoring, log_function_call

@pytest.mark.unit
class TestMonitoring:
    
    def test_get_metrics(self):
        """Тестирование функции get_metrics"""
        # Проверка получения метрик для существующего сервиса
        metrics = get_metrics("battle_mechanics")
        assert metrics is not None
        assert metrics.__class__.__name__ == "BattleMechanicsMetrics"
        
        # Проверка получения метрик для другого сервиса
        metrics = get_metrics("resource_management")
        assert metrics is not None
        assert metrics.__class__.__name__ == "ResourceManagementMetrics"
        
        # Проверка получения метрик для несуществующего сервиса
        metrics = get_metrics("non_existent_service")
        assert metrics is None
    
    @patch('common.monitoring.start_http_server')
    @patch('common.monitoring.TracerProvider')
    @patch('common.monitoring.MeterProvider')
    @patch('common.monitoring.FastAPIInstrumentor')
    def test_setup_monitoring(self, mock_instrumentor, mock_meter, mock_tracer, mock_server):
        """Тестирование функции setup_monitoring"""
        # Создаем тестовое FastAPI приложение
        app = FastAPI()
        
        # Вызываем функцию setup_monitoring
        setup_monitoring(app, "battle_mechanics", 9000)
        
        # Проверяем, что все нужные функции были вызваны
        mock_tracer.assert_called_once()
        mock_meter.assert_called_once()
        mock_instrumentor.instrument_app.assert_called_once_with(app)
        mock_server.assert_called_once_with(9000)
        
        # Проверяем, что middleware был добавлен в приложение
        assert len(app.middleware_stack.middlewares) > 0
    
    @patch('common.monitoring.start_http_server')
    @patch('common.monitoring.TracerProvider')
    @patch('common.monitoring.MeterProvider')
    @patch('common.monitoring.FastAPIInstrumentor')
    def test_setup_monitoring_invalid_service(self, mock_instrumentor, mock_meter, mock_tracer, mock_server):
        """Тестирование функции setup_monitoring с неправильным сервисом"""
        # Создаем тестовое FastAPI приложение
        app = FastAPI()
        
        # Проверяем, что вызов с неправильным сервисом вызывает исключение
        with pytest.raises(ValueError):
            setup_monitoring(app, "non_existent_service", 9000)
    
    @pytest.mark.asyncio
    async def test_monitoring_middleware(self):
        """Тестирование middleware мониторинга"""
        # Создаем тестовое FastAPI приложение
        app = FastAPI()
        
        # Настраиваем мониторинг
        setup_monitoring(app, "battle_mechanics", 9000)
        
        # Добавляем тестовый маршрут
        @app.get("/test")
        async def test_route():
            return {"status": "ok"}
        
        # Создаем тестовый клиент
        async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
            # Делаем запрос
            response = await client.get("/test")
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}
    
    @pytest.mark.asyncio
    async def test_monitoring_middleware_with_error(self):
        """Тестирование middleware мониторинга при ошибке"""
        # Создаем тестовое FastAPI приложение
        app = FastAPI()
        
        # Настраиваем мониторинг
        setup_monitoring(app, "battle_mechanics", 9000)
        
        # Добавляем тестовый маршрут с ошибкой
        @app.get("/error")
        async def error_route():
            raise ValueError("Test error")
        
        # Обработчик ошибок
        @app.exception_handler(ValueError)
        async def value_error_handler(request: Request, exc: ValueError):
            return JSONResponse(
                status_code=400,
                content={"message": str(exc)},
            )
        
        # Создаем тестовый клиент
        async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
            # Делаем запрос
            response = await client.get("/error")
            assert response.status_code == 400
            assert response.json() == {"message": "Test error"}
    
    @pytest.mark.asyncio
    async def test_log_function_call(self):
        """Тестирование декоратора log_function_call"""
        # Тестовая функция
        @log_function_call
        async def test_function(a, b, c=None):
            if c == "error":
                raise ValueError("Test error")
            return a + b
        
        # Тестируем успешный вызов
        result = await test_function(1, 2)
        assert result == 3
        
        # Тестируем вызов с ошибкой
        with pytest.raises(ValueError):
            await test_function(1, 2, c="error") 