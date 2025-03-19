import pytest
import httpx
import uuid
import time

@pytest.mark.unit
class TestAnalytics:
    
    @pytest.mark.asyncio
    async def test_create_event(self, async_api_client, analytics_url):
        """Тест создания игрового события"""
        # Подготовка тестовых данных
        game_id = str(uuid.uuid4())
        ship_id = str(uuid.uuid4())
        
        event_data = {
            "match_id": game_id,
            "event_type": "move",
            "ship_id": ship_id,
            "event_data": '{"direction": {"x": 10, "y": 0}}'
        }
        
        # Отправка запроса на создание события
        response = await async_api_client.post(
            f"{analytics_url}/events/",
            json=event_data
        )
        
        # Проверка результата
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["match_id"] == event_data["match_id"]
        assert data["event_type"] == event_data["event_type"]
        assert data["ship_id"] == event_data["ship_id"]
    
    @pytest.mark.asyncio
    async def test_get_game_events(self, async_api_client, analytics_url):
        """Тест получения событий игры"""
        # Создаем игру и несколько событий
        game_id = str(uuid.uuid4())
        ship_id = str(uuid.uuid4())
        
        # Создаем несколько событий для игры
        event_types = ["move", "rotate", "fire"]
        for event_type in event_types:
            event_data = {
                "match_id": game_id,
                "event_type": event_type,
                "ship_id": ship_id,
                "event_data": f'{{"action": "{event_type}"}}'
            }
            await async_api_client.post(
                f"{analytics_url}/events/",
                json=event_data
            )
        
        # Небольшая задержка для индексации в Elasticsearch
        time.sleep(1)
        
        # Отправка запроса на получение событий игры
        response = await async_api_client.get(
            f"{analytics_url}/games/{game_id}/events"
        )
        
        # Проверка результата
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == len(event_types)
        
        # Проверяем, что все наши события есть в результате
        event_types_in_response = [event["event_type"] for event in data]
        for event_type in event_types:
            assert event_type in event_types_in_response
    
    @pytest.mark.asyncio
    async def test_get_player_statistics(self, async_api_client, analytics_url):
        """Тест получения статистики игрока"""
        # Создаем игрока и события
        player_id = str(uuid.uuid4())
        ship_id = str(uuid.uuid4())
        game_id = str(uuid.uuid4())
        
        # Создаем несколько событий для игрока
        for i in range(3):
            event_data = {
                "match_id": game_id,
                "event_type": "move" if i % 2 == 0 else "fire",
                "ship_id": ship_id,
                "player_id": player_id,
                "event_data": f'{{"turn": {i}}}'
            }
            await async_api_client.post(
                f"{analytics_url}/events/",
                json=event_data
            )
        
        # Небольшая задержка для индексации в Elasticsearch
        time.sleep(1)
        
        # Отправка запроса на получение статистики игрока
        response = await async_api_client.get(
            f"{analytics_url}/players/{player_id}/statistics"
        )
        
        # Проверка результата
        assert response.status_code == 200
        data = response.json()
        assert "total_games" in data
        assert "total_moves" in data
        assert "total_shots" in data
        
        # Проверяем, что статистика соответствует нашим событиям
        assert data["total_games"] >= 1  # Должна быть хотя бы одна игра
        assert data["total_moves"] >= 2  # Два "move" события
        assert data["total_shots"] >= 1  # Одно "fire" событие
    
    @pytest.mark.asyncio
    async def test_get_game_summary(self, async_api_client, analytics_url):
        """Тест получения сводки по игре"""
        # Создаем игру и события
        game_id = str(uuid.uuid4())
        player1_id = str(uuid.uuid4())
        player2_id = str(uuid.uuid4())
        ship1_id = str(uuid.uuid4())
        ship2_id = str(uuid.uuid4())
        
        # Создаем события для игры
        events = [
            {"match_id": game_id, "event_type": "move", "ship_id": ship1_id, 
             "player_id": player1_id, "event_data": '{"direction": {"x": 10, "y": 0}}'},
            {"match_id": game_id, "event_type": "move", "ship_id": ship2_id, 
             "player_id": player2_id, "event_data": '{"direction": {"x": -5, "y": 5}}'},
            {"match_id": game_id, "event_type": "fire", "ship_id": ship1_id, 
             "player_id": player1_id, "target_ship_id": ship2_id, "event_data": '{"hit": true}'},
            {"match_id": game_id, "event_type": "hit", "ship_id": ship2_id, 
             "player_id": player2_id, "event_data": '{"damage": 25}'},
        ]
        
        for event in events:
            await async_api_client.post(
                f"{analytics_url}/events/",
                json=event
            )
        
        # Небольшая задержка для индексации в Elasticsearch
        time.sleep(1)
        
        # Отправка запроса на получение сводки по игре
        response = await async_api_client.get(
            f"{analytics_url}/games/{game_id}/summary"
        )
        
        # Проверка результата
        assert response.status_code == 200
        data = response.json()
        assert "total_events" in data
        assert "player_stats" in data
        
        # Проверяем, что сводка соответствует нашим событиям
        assert data["total_events"] >= len(events)
        assert len(data["player_stats"]) >= 2  # Должно быть два игрока 