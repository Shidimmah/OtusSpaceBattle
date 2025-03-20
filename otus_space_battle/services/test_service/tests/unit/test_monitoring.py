import pytest
import httpx
import time
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock, call
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from common.monitoring import get_metrics, setup_monitoring, log_function_call, FastAPIInstrumentor, TracerProvider, MeterProvider, METRICS, ServiceMetrics
from common.metric_utils import create_counter, create_histogram, create_gauge
from common.metrics import BattleMechanicsMetrics, ResourceManagementMetrics, RankingMetrics, AnalyticsMetrics, ApiGatewayMetrics

@pytest.mark.unit
class TestMonitoring:
    
    def test_get_metrics(self):
        """Тестирование функции get_metrics"""
        # Проверка получения метрик для существующего сервиса
        metrics = get_metrics("battle_mechanics")
        assert metrics is not None
        assert metrics.service_name == "battle_mechanics"
        
        # Проверка получения метрик для другого сервиса
        metrics = get_metrics("resource_management")
        assert metrics is not None
        assert metrics.service_name == "resource_management"
        
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
    
    @pytest.mark.asyncio
    async def test_log_function_call_with_params(self):
        """Тестирование декоратора log_function_call с разными параметрами"""
        # Тестовая функция
        @log_function_call
        async def test_function_with_params(a, b, *args, **kwargs):
            return a + b + sum(args) + sum(kwargs.values())
        
        # Тестируем вызов с разными параметрами
        result = await test_function_with_params(1, 2, 3, 4, c=5, d=6)
        assert result == 21  # 1 + 2 + 3 + 4 + 5 + 6
    
    @pytest.mark.asyncio
    async def test_log_function_call_performance(self):
        """Тестирование производительности декоратора log_function_call"""
        # Тестовая функция с задержкой
        @log_function_call
        async def test_function_sleep(sleep_time):
            await asyncio.sleep(sleep_time)
            return sleep_time
        
        # Тестируем вызов с минимальной задержкой
        start_time = time.time()
        result = await test_function_sleep(0.01)
        elapsed_time = time.time() - start_time
        
        # Проверяем, что задержка была не менее заданного времени
        assert elapsed_time >= 0.01
        assert result == 0.01
    
    @patch('common.monitoring.logger')
    @pytest.mark.asyncio
    async def test_log_function_call_logging(self, mock_logger):
        """Тестирование логирования в декораторе log_function_call"""
        # Тестовая функция
        @log_function_call
        async def test_logging_function(a, b):
            return a + b
        
        # Вызываем функцию
        result = await test_logging_function(5, 7)
        
        # Проверяем логирование
        assert mock_logger.info.call_count >= 2  # Должны быть вызовы для начала и конца функции
        assert mock_logger.error.call_count == 0  # Не должно быть ошибок
        
        # Проверяем результат
        assert result == 12
    
    @patch('common.monitoring.logger')
    @pytest.mark.asyncio
    async def test_log_function_call_error_logging(self, mock_logger):
        """Тестирование логирования ошибок в декораторе log_function_call"""
        # Тестовая функция с ошибкой
        @log_function_call
        async def test_error_function():
            raise RuntimeError("Test runtime error")
        
        # Вызываем функцию и ожидаем ошибку
        with pytest.raises(RuntimeError):
            await test_error_function()
        
        # Проверяем логирование ошибки
        assert mock_logger.info.call_count >= 1  # Должен быть вызов для начала функции
        assert mock_logger.error.call_count >= 1  # Должен быть вызов для ошибки
        
        # Проверяем параметры вызова error
        error_call_args = mock_logger.error.call_args[0]
        assert "function_error" in error_call_args
        
        error_call_kwargs = mock_logger.error.call_args[1]
        assert "error" in error_call_kwargs or "error_type" in error_call_kwargs

    @patch('common.monitoring.start_http_server')
    @pytest.mark.asyncio
    async def test_middleware_request_logging(self, mock_server):
        """Тестирование логирования запросов в middleware"""
        # Создаем тестовое FastAPI приложение
        app = FastAPI()
        
        # Настраиваем мониторинг с мок-логгером
        with patch('common.monitoring.logger') as mock_logger:
            setup_monitoring(app, "test_service", 9000)
            
            # Добавляем тестовый маршрут
            @app.get("/test-logging")
            async def test_logging_route():
                return {"status": "logged"}
            
            # Создаем тестовый клиент и делаем запрос
            async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
                response = await client.get("/test-logging")
                
                # Проверяем, что запрос был залогирован
                assert mock_logger.info.call_count >= 1
                
                # Проверяем параметры вызова info
                info_call_args = mock_logger.info.call_args[0]
                assert "request" in info_call_args
                
                # Проверяем результат запроса
                assert response.status_code == 200
                assert response.json() == {"status": "logged"}
    
    @patch('common.monitoring.start_http_server')
    @pytest.mark.asyncio
    async def test_monitoring_middleware_with_metrics_tracking(self, mock_server):
        """Тестирование monitoring_middleware с учетом трекинга метрик"""
        # Создаем тестовое FastAPI приложение
        app = FastAPI()
        
        # Создаем mock-объект для метрик
        mock_metrics = MagicMock()
        mock_metrics.active_connections = MagicMock()
        mock_metrics.active_connections.labels.return_value = MagicMock()
        mock_metrics.request_count = MagicMock()
        mock_metrics.request_count.labels.return_value = MagicMock()
        mock_metrics.request_latency = MagicMock()
        mock_metrics.request_latency.labels.return_value = MagicMock()
        mock_metrics.error_count = MagicMock()
        mock_metrics.error_count.labels.return_value = MagicMock()
        
        # Патчим get_metrics для возврата нашего mock-объекта
        with patch('common.monitoring.get_metrics', return_value=mock_metrics):
            # Вызываем setup_monitoring, которая добавит middleware с нашими mock-метриками
            setup_monitoring(app, "test_service", 9000)
            
            # Добавляем тестовый маршрут
            @app.get("/test-metrics")
            async def test_route():
                return {"status": "metrics_tracked"}
                
            # Добавляем маршрут с ошибкой
            @app.get("/error-metrics")
            async def error_route():
                raise ValueError("Test error for metrics")
                
            # Обработчик ошибок
            @app.exception_handler(ValueError)
            async def value_error_handler(request: Request, exc: ValueError):
                return JSONResponse(
                    status_code=400,
                    content={"message": str(exc)},
                )
            
            # Создаем тестовый клиент
            async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
                # Делаем успешный запрос
                response = await client.get("/test-metrics")
                assert response.status_code == 200
                
                # Проверяем, что метрики были собраны
                mock_metrics.active_connections.labels.assert_called_with(service="test_service")
                mock_metrics.active_connections.labels().inc.assert_called()
                mock_metrics.active_connections.labels().dec.assert_called()
                mock_metrics.request_count.labels.assert_called_with(
                    service="test_service", 
                    endpoint="/test-metrics", 
                    method="GET"
                )
                mock_metrics.request_count.labels().inc.assert_called()
                mock_metrics.request_latency.labels.assert_called_with(
                    service="test_service", 
                    endpoint="/test-metrics"
                )
                mock_metrics.request_latency.labels().observe.assert_called()
                
                # Делаем запрос с ошибкой
                response = await client.get("/error-metrics")
                assert response.status_code == 400
                
                # Проверяем, что метрики ошибок были собраны
                mock_metrics.error_count.labels.assert_called_with(
                    service="test_service",
                    error_type="ValueError"
                )
                mock_metrics.error_count.labels().inc.assert_called()
    
    def test_fastapi_instrumentor_class(self):
        """Тест заглушки класса FastAPIInstrumentor"""
        # Создаем тестовое FastAPI приложение
        app = FastAPI()
        
        # Вызываем метод instrument_app заглушки
        FastAPIInstrumentor.instrument_app(app)
        
        # Проверяем, что метод заглушки ничего не возвращает
        assert FastAPIInstrumentor.instrument_app(app) is None
    
    def test_tracer_provider_class(self):
        """Тест заглушки класса TracerProvider"""
        # Создаем экземпляр TracerProvider
        tracer = TracerProvider()
        
        # Проверяем, что заглушка создана
        assert isinstance(tracer, TracerProvider)
    
    def test_meter_provider_class(self):
        """Тест заглушки класса MeterProvider"""
        # Создаем экземпляр MeterProvider
        meter = MeterProvider()
        
        # Проверяем, что заглушка создана
        assert isinstance(meter, MeterProvider)
    
    def test_metrics_dictionary(self):
        """Тест словаря метрик сервисов"""
        # Проверяем, что словарь METRICS содержит нужные ключи
        assert "battle_mechanics" in METRICS
        assert "resource_management" in METRICS
        
        # Проверяем, что значения словаря - экземпляры нужных классов
        assert isinstance(METRICS["battle_mechanics"], ServiceMetrics)
        assert isinstance(METRICS["resource_management"], ServiceMetrics)
        
        # Проверяем service_name для каждой метрики
        assert METRICS["battle_mechanics"].service_name == "battle_mechanics"
        assert METRICS["resource_management"].service_name == "resource_management"
    
    def test_service_metrics_class(self):
        """Тест базового класса метрик ServiceMetrics"""
        # Создаем экземпляр класса
        metrics = ServiceMetrics("test_service_name")
        
        # Проверяем service_name
        assert metrics.service_name == "test_service_name"
    
    @pytest.mark.asyncio
    async def test_sync_function_with_log_decorator(self):
        """Тест декоратора log_function_call с синхронной функцией"""
        # Проверяем, что декоратор корректно обрабатывает синхронную функцию
        with pytest.raises(TypeError):
            @log_function_call
            def sync_function(a, b):
                return a + b
            
            result = sync_function(2, 3)
        
    @patch('common.monitoring.logger')
    @pytest.mark.asyncio
    async def test_log_function_call_args_capture(self, mock_logger):
        """Тест логирования аргументов в log_function_call"""
        @log_function_call
        async def test_args_capture(a, b, c=None):
            return a + b + (c or 0)
        
        # Вызываем функцию с разными аргументами
        result = await test_args_capture(1, 2, c=3)
        
        # Проверяем, что вызов логгера содержит информацию об аргументах
        first_call_args = mock_logger.info.call_args_list[0]
        assert "function_call" in first_call_args[0]
        assert first_call_args[1].get('function') == 'test_args_capture'
        
        # Проверяем результат
        assert result == 6
        
    @patch('common.monitoring.start_http_server')
    @pytest.mark.asyncio
    async def test_setup_monitoring_returns_middleware(self, mock_server):
        """Тест возвращения middleware из setup_monitoring"""
        app = FastAPI()
        
        # Получаем middleware функцию из setup_monitoring
        with patch('common.monitoring.get_metrics') as mock_get_metrics:
            mock_get_metrics.return_value = MagicMock()
            
            # Настраиваем мониторинг и проверяем, что middleware добавлен
            setup_monitoring(app, "test_service", 9000)
            
            # Проверяем, что middleware добавлен в приложение
            assert len(app.middleware_stack.middlewares) > 0 

    @pytest.mark.unit
    def test_service_metrics_creation(self):
        """Тестирование создания и инициализации метрик в разных сервисах"""
        # Проверка метрик для боевой механики
        battle_metrics = BattleMechanicsMetrics()
        assert battle_metrics.service_name == "battle_mechanics"
        assert hasattr(battle_metrics, "request_count")
        assert hasattr(battle_metrics, "request_latency")
        assert hasattr(battle_metrics, "error_count")
        assert hasattr(battle_metrics, "active_connections")
        assert hasattr(battle_metrics, "movement_count")
        assert hasattr(battle_metrics, "rotation_count")
        assert hasattr(battle_metrics, "fire_count")
        assert hasattr(battle_metrics, "collision_count")
        
        # Проверка метрик для управления ресурсами
        resource_metrics = ResourceManagementMetrics()
        assert resource_metrics.service_name == "resource_management"
        assert hasattr(resource_metrics, "fuel_usage")
        assert hasattr(resource_metrics, "torpedo_usage")
        assert hasattr(resource_metrics, "resource_check_count")
        assert hasattr(resource_metrics, "active_ships")
        
        # Проверка метрик для рейтинга
        ranking_metrics = RankingMetrics()
        assert ranking_metrics.service_name == "ranking"
        assert hasattr(ranking_metrics, "rank_updates")
        assert hasattr(ranking_metrics, "points_awarded")
        assert hasattr(ranking_metrics, "leaderboard_queries")
        assert hasattr(ranking_metrics, "active_players")
        
        # Проверка метрик для аналитики
        analytics_metrics = AnalyticsMetrics()
        assert analytics_metrics.service_name == "analytics"
        assert hasattr(analytics_metrics, "events_processed")
        assert hasattr(analytics_metrics, "stats_queries")
        assert hasattr(analytics_metrics, "event_processing_time")
        assert hasattr(analytics_metrics, "stored_events")
        
        # Проверка метрик для API Gateway
        api_gateway_metrics = ApiGatewayMetrics()
        assert api_gateway_metrics.service_name == "api_gateway"
        assert hasattr(api_gateway_metrics, "upstream_latency")
        assert hasattr(api_gateway_metrics, "upstream_errors")
        assert hasattr(api_gateway_metrics, "active_games")
        assert hasattr(api_gateway_metrics, "api_key_validations")

    @pytest.mark.unit
    def test_metric_registry_isolation(self):
        """Тестирование изоляции метрик между сервисами"""
        # Создаем экземпляры метрик для разных сервисов
        battle_metrics = BattleMechanicsMetrics()
        resource_metrics = ResourceManagementMetrics()
        
        # Проверяем, что метрики имеют разные имена сервисов
        assert battle_metrics.service_name != resource_metrics.service_name
        
        # Проверяем, что у каждого сервиса свой набор специфичных метрик
        assert hasattr(battle_metrics, "movement_count")
        assert not hasattr(resource_metrics, "movement_count")
        
        assert hasattr(resource_metrics, "fuel_usage")
        assert not hasattr(battle_metrics, "fuel_usage")
        
        # Проверяем, что базовые метрики присутствуют у обоих сервисов
        assert hasattr(battle_metrics, "request_count")
        assert hasattr(resource_metrics, "request_count")
        assert hasattr(battle_metrics, "request_latency")
        assert hasattr(resource_metrics, "request_latency")

    @pytest.mark.unit
    def test_create_counter(self):
        """Тестирование функции create_counter"""
        # Создание счетчика без имени сервиса
        counter = create_counter("test_counter", "Test counter documentation", ["label1", "label2"])
        assert counter.name == "test_counter"
        assert counter._documentation == "Test counter documentation"
        assert counter._labelnames == ("label1", "label2")
        
        # Создание счетчика с именем сервиса
        service_counter = create_counter("service_counter", "Service counter", ["label1"], service_name="test_service")
        assert service_counter.name == "test_service_service_counter"
        assert service_counter._documentation == "Service counter"
        assert service_counter._labelnames == ("label1",)

    @pytest.mark.unit
    def test_create_histogram(self):
        """Тестирование функции create_histogram"""
        # Создание гистограммы без имени сервиса
        histogram = create_histogram("test_histogram", "Test histogram documentation", 
                                     ["label1"], buckets=[0.1, 0.5, 1.0])
        assert histogram.name == "test_histogram"
        assert histogram._documentation == "Test histogram documentation"
        assert histogram._labelnames == ("label1",)
        assert 0.1 in histogram._buckets
        assert 0.5 in histogram._buckets
        assert 1.0 in histogram._buckets
        
        # Создание гистограммы с именем сервиса
        service_histogram = create_histogram("service_histogram", "Service histogram", 
                                            ["label1"], buckets=[0.1, 0.5], service_name="test_service")
        assert service_histogram.name == "test_service_service_histogram"
        assert service_histogram._documentation == "Service histogram"
        assert service_histogram._labelnames == ("label1",)
        assert 0.1 in service_histogram._buckets
        assert 0.5 in service_histogram._buckets

    @pytest.mark.unit
    def test_create_gauge(self):
        """Тестирование функции create_gauge"""
        # Создание gauge без имени сервиса
        gauge = create_gauge("test_gauge", "Test gauge documentation", ["label1"])
        assert gauge.name == "test_gauge"
        assert gauge._documentation == "Test gauge documentation"
        assert gauge._labelnames == ("label1",)
        
        # Создание gauge с именем сервиса
        service_gauge = create_gauge("service_gauge", "Service gauge", ["label1"], service_name="test_service")
        assert service_gauge.name == "test_service_service_gauge"
        assert service_gauge._documentation == "Service gauge"
        assert service_gauge._labelnames == ("label1",)

    @pytest.mark.unit
    def test_no_duplicate_metrics(self):
        """Проверка отсутствия дублирования метрик между сервисами"""
        # Создаем 2 экземпляра метрик для одного сервиса с одинаковыми названиями
        # Но благодаря registry=None они не должны конфликтовать
        counter1 = create_counter("test_duplicate", "First counter", service_name="test_service")
        counter2 = create_counter("test_duplicate", "Second counter", service_name="test_service")
        
        # Создаем счетчики с одинаковыми названиями для разных сервисов
        # С префиксом сервиса они должны иметь разные имена
        service1_counter = create_counter("request_count", "Service 1 requests", service_name="service1")
        service2_counter = create_counter("request_count", "Service 2 requests", service_name="service2")
        
        # Проверяем, что счетчики с разными префиксами имеют разные имена
        assert service1_counter.name == "service1_request_count"
        assert service2_counter.name == "service2_request_count"
        assert service1_counter.name != service2_counter.name
        
        # Создаем разные типы метрик с одинаковыми базовыми именами
        counter = create_counter("metric", "Counter metric")
        histogram = create_histogram("metric", "Histogram metric")
        gauge = create_gauge("metric", "Gauge metric")
        
        # Вызываем inc() для всех счетчиков, чтобы проверить отсутствие конфликтов
        counter1.inc()
        counter2.inc()
        service1_counter.inc()
        service2_counter.inc()
        counter.inc()
        
        # Проверка успешна, если при вызове методов не возникает исключений 

    @pytest.mark.unit
    def test_battle_mechanics_metrics_usage(self):
        """Тестирование использования метрик боевой механики"""
        # Создаем экземпляр метрик
        metrics = BattleMechanicsMetrics()
        
        # Проверяем, что можно использовать метрики
        metrics.movement_count.labels(result="success").inc()
        metrics.rotation_count.labels(result="success").inc()
        metrics.fire_count.labels(result="failure").inc()
        metrics.collision_count.labels(result="detected").inc()
        
        # Проверяем базовые метрики
        metrics.request_count.labels(service="battle_mechanics", endpoint="/test", method="GET").inc()
        metrics.request_latency.labels(service="battle_mechanics", endpoint="/test").observe(0.1)
        metrics.error_count.labels(service="battle_mechanics", error_type="ValueError").inc()
        metrics.active_connections.labels(service="battle_mechanics").inc()
        
        # Если мы дошли до этой точки без исключений, тест считается успешным 