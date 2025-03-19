import pytest
import httpx
import uuid
import time

@pytest.mark.unit
class TestMatchmaking:
    
    @pytest.mark.asyncio
    async def test_add_player_to_queue(self, async_api_client, matchmaking_url):
        """Тест добавления игрока в очередь"""
        # Подготовка данных
        player_id = str(uuid.uuid4())
        fleet_id = str(uuid.uuid4())
        
        queue_data = {
            "player_id": player_id,
            "fleet_id": fleet_id,
            "rating": 1500
        }
        
        # Отправка запроса на добавление в очередь
        response = await async_api_client.post(
            f"{matchmaking_url}/queue/join",
            json=queue_data
        )
        
        # Проверка результата
        assert response.status_code == 200
        data = response.json()
        assert data["player_id"] == player_id
        assert data["fleet_id"] == fleet_id
        assert "position" in data
    
    @pytest.mark.asyncio
    async def test_check_queue_position(self, async_api_client, matchmaking_url):
        """Тест проверки позиции в очереди"""
        # Добавляем игрока в очередь
        player_id = str(uuid.uuid4())
        fleet_id = str(uuid.uuid4())
        
        queue_data = {
            "player_id": player_id,
            "fleet_id": fleet_id,
            "rating": 1500
        }
        
        await async_api_client.post(
            f"{matchmaking_url}/queue/join",
            json=queue_data
        )
        
        # Отправка запроса на проверку позиции
        response = await async_api_client.get(
            f"{matchmaking_url}/queue/position/{player_id}"
        )
        
        # Проверка результата
        assert response.status_code == 200
        data = response.json()
        assert data["player_id"] == player_id
        assert "position" in data
    
    @pytest.mark.asyncio
    async def test_leave_queue(self, async_api_client, matchmaking_url):
        """Тест покидания очереди"""
        # Добавляем игрока в очередь
        player_id = str(uuid.uuid4())
        fleet_id = str(uuid.uuid4())
        
        queue_data = {
            "player_id": player_id,
            "fleet_id": fleet_id,
            "rating": 1500
        }
        
        await async_api_client.post(
            f"{matchmaking_url}/queue/join",
            json=queue_data
        )
        
        # Отправка запроса на покидание очереди
        response = await async_api_client.post(
            f"{matchmaking_url}/queue/leave",
            json={"player_id": player_id}
        )
        
        # Проверка результата
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        
        # Проверяем, что игрока больше нет в очереди
        check_response = await async_api_client.get(
            f"{matchmaking_url}/queue/position/{player_id}"
        )
        assert check_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_find_match(self, async_api_client, matchmaking_url):
        """Тест поиска подходящего соперника"""
        # Добавляем двух игроков с похожим рейтингом
        player1_id = str(uuid.uuid4())
        player2_id = str(uuid.uuid4())
        fleet1_id = str(uuid.uuid4())
        fleet2_id = str(uuid.uuid4())
        
        # Первый игрок
        await async_api_client.post(
            f"{matchmaking_url}/queue/join",
            json={
                "player_id": player1_id,
                "fleet_id": fleet1_id,
                "rating": 1500
            }
        )
        
        # Второй игрок
        await async_api_client.post(
            f"{matchmaking_url}/queue/join",
            json={
                "player_id": player2_id,
                "fleet_id": fleet2_id,
                "rating": 1550  # Близкий рейтинг
            }
        )
        
        # Запрос на поиск матча
        response = await async_api_client.post(
            f"{matchmaking_url}/match/find",
            json={"player_id": player1_id}
        )
        
        # Проверка результата
        assert response.status_code in [200, 202]
        
        if response.status_code == 200:
            # Матч был найден
            data = response.json()
            assert "match_id" in data
            assert "opponent_id" in data
            assert data["opponent_id"] == player2_id
        else:
            # Матч еще не найден, но запрос корректный
            data = response.json()
            assert data["status"] == "pending"
    
    @pytest.mark.asyncio
    async def test_get_queue_status(self, async_api_client, matchmaking_url):
        """Тест получения статуса очереди"""
        # Добавляем нескольких игроков в очередь
        ratings = [1400, 1500, 1600]
        
        for i, rating in enumerate(ratings):
            await async_api_client.post(
                f"{matchmaking_url}/queue/join",
                json={
                    "player_id": str(uuid.uuid4()),
                    "fleet_id": str(uuid.uuid4()),
                    "rating": rating
                }
            )
        
        # Отправка запроса на получение статуса очереди
        response = await async_api_client.get(
            f"{matchmaking_url}/queue/status"
        )
        
        # Проверка результата
        assert response.status_code == 200
        data = response.json()
        assert "total_players" in data
        assert "rating_distribution" in data
        assert data["total_players"] >= len(ratings) 