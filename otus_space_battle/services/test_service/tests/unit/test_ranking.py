import pytest
import httpx
import uuid

@pytest.mark.unit
class TestRanking:
    
    @pytest.mark.asyncio
    async def test_get_leaderboard(self, async_api_client, ranking_url):
        """Тест получения таблицы лидеров"""
        # Отправка запроса на получение таблицы лидеров
        response = await async_api_client.get(
            f"{ranking_url}/leaderboard"
        )
        
        # Проверка результата
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_player_rank(self, async_api_client, ranking_url):
        """Тест получения ранга игрока"""
        # Создаем уникальный ID игрока
        player_id = str(uuid.uuid4())
        
        # Отправка запроса на получение ранга игрока
        response = await async_api_client.get(
            f"{ranking_url}/players/{player_id}/rank"
        )
        
        # Проверка результата
        # Если игрок новый, его может не быть в системе, но запрос должен отработать
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "rank" in data
            assert "rating" in data
    
    @pytest.mark.asyncio
    async def test_update_player_rating(self, async_api_client, ranking_url):
        """Тест обновления рейтинга игрока"""
        # Создаем уникальный ID игрока
        player_id = str(uuid.uuid4())
        
        # Данные для обновления рейтинга
        rating_data = {
            "result": "win",
            "opponent_rating": 1500
        }
        
        # Отправка запроса на обновление рейтинга
        response = await async_api_client.post(
            f"{ranking_url}/players/{player_id}/update_rating",
            json=rating_data
        )
        
        # Проверка результата
        assert response.status_code == 200
        data = response.json()
        assert "new_rating" in data
        assert data["player_id"] == player_id
        assert data["new_rating"] > 1000  # Начальный рейтинг должен быть увеличен за победу
    
    @pytest.mark.asyncio
    async def test_get_rating_history(self, async_api_client, ranking_url):
        """Тест получения истории рейтинга игрока"""
        # Создаем уникальный ID игрока
        player_id = str(uuid.uuid4())
        
        # Сначала обновляем рейтинг несколько раз
        for result in ["win", "loss", "win"]:
            rating_data = {
                "result": result,
                "opponent_rating": 1500
            }
            await async_api_client.post(
                f"{ranking_url}/players/{player_id}/update_rating",
                json=rating_data
            )
        
        # Отправка запроса на получение истории рейтинга
        response = await async_api_client.get(
            f"{ranking_url}/players/{player_id}/rating_history"
        )
        
        # Проверка результата
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3  # Должно быть не менее 3 записей об изменении рейтинга
    
    @pytest.mark.asyncio
    async def test_compare_players(self, async_api_client, ranking_url):
        """Тест сравнения игроков по рейтингу"""
        # Создаем уникальные ID игроков
        player1_id = str(uuid.uuid4())
        player2_id = str(uuid.uuid4())
        
        # Обновляем рейтинг первого игрока - две победы
        for _ in range(2):
            await async_api_client.post(
                f"{ranking_url}/players/{player1_id}/update_rating",
                json={"result": "win", "opponent_rating": 1500}
            )
        
        # Обновляем рейтинг второго игрока - одна победа, одно поражение
        await async_api_client.post(
            f"{ranking_url}/players/{player2_id}/update_rating",
            json={"result": "win", "opponent_rating": 1500}
        )
        await async_api_client.post(
            f"{ranking_url}/players/{player2_id}/update_rating",
            json={"result": "loss", "opponent_rating": 1500}
        )
        
        # Отправка запроса на сравнение игроков
        response = await async_api_client.get(
            f"{ranking_url}/compare?player1_id={player1_id}&player2_id={player2_id}"
        )
        
        # Проверка результата
        assert response.status_code == 200
        data = response.json()
        assert "player1" in data
        assert "player2" in data
        assert "difference" in data
        assert data["player1"]["rating"] > data["player2"]["rating"]  # Первый игрок должен иметь более высокий рейтинг 