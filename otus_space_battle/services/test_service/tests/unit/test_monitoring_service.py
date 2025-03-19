import pytest
import httpx

@pytest.mark.unit
class TestMonitoringService:
    
    @pytest.mark.asyncio
    async def test_get_service_health(self, monitoring_service_url):
        """Тест проверки здоровья сервиса"""
        # Подготовка тестовых данных
        service_name = "test_service"
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на проверку здоровья
            response = await client.get(
                f"{monitoring_service_url}/health/{service_name}"
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "uptime" in data
            assert "last_check" in data
            assert "dependencies" in data
            assert data["status"] in ["healthy", "degraded", "unhealthy"]
    
    @pytest.mark.asyncio
    async def test_get_system_metrics(self, monitoring_service_url):
        """Тест получения системных метрик"""
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на получение метрик
            response = await client.get(
                f"{monitoring_service_url}/metrics"
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert "cpu_usage" in data
            assert "memory_usage" in data
            assert "disk_usage" in data
            assert "network_io" in data
            assert "active_connections" in data
    
    @pytest.mark.asyncio
    async def test_get_service_alerts(self, monitoring_service_url):
        """Тест получения оповещений сервиса"""
        # Подготовка тестовых данных
        service_name = "test_service"
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на получение оповещений
            response = await client.get(
                f"{monitoring_service_url}/alerts/{service_name}"
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert "alerts" in data
            assert isinstance(data["alerts"], list)
            for alert in data["alerts"]:
                assert "id" in alert
                assert "level" in alert
                assert "message" in alert
                assert "timestamp" in alert
                assert "status" in alert
                assert alert["status"] in ["active", "resolved", "acknowledged"] 