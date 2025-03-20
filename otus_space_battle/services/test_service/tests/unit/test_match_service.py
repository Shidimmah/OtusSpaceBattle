import pytest
import httpx

@pytest.mark.unit
class TestMatchService:
    
    @pytest.mark.asyncio
    async def test_create_match(self, match_service_url):
        """Тест создания матча"""
        # Подготовка тестовых данных
        match_data = {
            "player1_id": "player1",
            "player2_id": "player2",
            "player1_fleet_id": "fleet1",
            "player2_fleet_id": "fleet2",
            "is_ranked": True
        }
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на создание матча
            response = await client.post(
                f"{match_service_url}/matches",
                json=match_data
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert "match_id" in data
            assert data["status"] == "waiting"
            assert data["is_ranked"] == match_data["is_ranked"]
    
    @pytest.mark.asyncio
    async def test_get_match(self, match_service_url):
        """Тест получения информации о матче"""
        # Подготовка тестовых данных
        match_id = "match123"
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на получение информации о матче
            response = await client.get(
                f"{match_service_url}/matches/{match_id}"
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert "match_id" in data
            assert "status" in data
            assert "player1_id" in data
            assert "player2_id" in data
            assert "start_time" in data
    
    @pytest.mark.asyncio
    async def test_update_match_status(self, match_service_url):
        """Тест обновления статуса матча"""
        # Подготовка тестовых данных
        match_id = "match123"
        status_data = {
            "status": "finished",
            "winner_id": "player1"
        }
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на обновление статуса
            response = await client.put(
                f"{match_service_url}/matches/{match_id}/status",
                json=status_data
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == status_data["status"]
            assert data["winner_id"] == status_data["winner_id"]
            assert "end_time" in data 