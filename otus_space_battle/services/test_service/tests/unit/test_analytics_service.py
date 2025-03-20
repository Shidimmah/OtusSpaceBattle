import pytest
import httpx

@pytest.mark.unit
class TestAnalyticsService:
    
    @pytest.mark.asyncio
    async def test_get_game_statistics(self, analytics_service_url):
        """Тест получения игровой статистики"""
        # Подготовка тестовых данных
        game_id = "game123"
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на получение статистики
            response = await client.get(
                f"{analytics_service_url}/games/{game_id}/statistics"
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert "total_players" in data
            assert "active_matches" in data
            assert "average_match_duration" in data
            assert "popular_ship_types" in data
            assert "player_activity" in data
    
    @pytest.mark.asyncio
    async def test_get_player_analytics(self, analytics_service_url):
        """Тест получения аналитики игрока"""
        # Подготовка тестовых данных
        player_id = "player123"
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на получение аналитики
            response = await client.get(
                f"{analytics_service_url}/players/{player_id}/analytics"
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert "win_rate" in data
            assert "average_match_duration" in data
            assert "favorite_ship_types" in data
            assert "performance_trend" in data
            assert "achievement_progress" in data
    
    @pytest.mark.asyncio
    async def test_get_system_metrics(self, analytics_service_url):
        """Тест получения системных метрик"""
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на получение метрик
            response = await client.get(
                f"{analytics_service_url}/system/metrics"
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert "active_users" in data
            assert "server_load" in data
            assert "response_times" in data
            assert "error_rates" in data
            assert "resource_usage" in data 