import pytest
import httpx

@pytest.mark.unit
class TestAchievementService:
    
    @pytest.mark.asyncio
    async def test_get_player_achievements(self, achievement_service_url):
        """Тест получения достижений игрока"""
        # Подготовка тестовых данных
        player_id = "player123"
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на получение достижений
            response = await client.get(
                f"{achievement_service_url}/players/{player_id}/achievements"
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert "achievements" in data
            assert isinstance(data["achievements"], list)
            for achievement in data["achievements"]:
                assert "id" in achievement
                assert "name" in achievement
                assert "description" in achievement
                assert "progress" in achievement
                assert "completed" in achievement
    
    @pytest.mark.asyncio
    async def test_update_achievement_progress(self, achievement_service_url):
        """Тест обновления прогресса достижения"""
        # Подготовка тестовых данных
        player_id = "player123"
        achievement_id = "achievement123"
        progress_data = {
            "progress": 50,
            "event_type": "match_completed"
        }
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на обновление прогресса
            response = await client.post(
                f"{achievement_service_url}/players/{player_id}/achievements/{achievement_id}/progress",
                json=progress_data
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert data["progress"] == progress_data["progress"]
            assert "completed" in data
            assert "completed_at" in data if data["completed"] else "completed_at" not in data
    
    @pytest.mark.asyncio
    async def test_get_achievement_details(self, achievement_service_url):
        """Тест получения детальной информации о достижении"""
        # Подготовка тестовых данных
        achievement_id = "achievement123"
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на получение деталей
            response = await client.get(
                f"{achievement_service_url}/achievements/{achievement_id}"
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == achievement_id
            assert "name" in data
            assert "description" in data
            assert "requirements" in data
            assert "rewards" in data
            assert "rarity" in data 