import pytest
import httpx

@pytest.mark.unit
class TestGameEventService:
    
    @pytest.mark.asyncio
    async def test_create_game_event(self, game_event_service_url):
        """Тест создания игрового события"""
        # Подготовка тестовых данных
        event_data = {
            "match_id": "match123",
            "event_type": "ship_hit",
            "ship_id": "ship123",
            "target_ship_id": "ship456",
            "event_data": {
                "damage": 10,
                "position": {"x": 10, "y": 10}
            }
        }
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на создание события
            response = await client.post(
                f"{game_event_service_url}/events",
                json=event_data
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert "event_id" in data
            assert data["event_type"] == event_data["event_type"]
            assert data["ship_id"] == event_data["ship_id"]
    
    @pytest.mark.asyncio
    async def test_get_match_events(self, game_event_service_url):
        """Тест получения событий матча"""
        # Подготовка тестовых данных
        match_id = "match123"
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на получение событий
            response = await client.get(
                f"{game_event_service_url}/matches/{match_id}/events"
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert "events" in data
            assert isinstance(data["events"], list)
    
    @pytest.mark.asyncio
    async def test_get_ship_events(self, game_event_service_url):
        """Тест получения событий корабля"""
        # Подготовка тестовых данных
        ship_id = "ship123"
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на получение событий
            response = await client.get(
                f"{game_event_service_url}/ships/{ship_id}/events"
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert "events" in data
            assert isinstance(data["events"], list)
            for event in data["events"]:
                assert event["ship_id"] == ship_id or event["target_ship_id"] == ship_id 