import pytest
import httpx
import uuid

@pytest.mark.unit
class TestBattleMechanics:
    
    @pytest.mark.asyncio
    async def test_create_game(self, async_api_client, battle_mechanics_url):
        """Тест создания игры"""
        # Подготовка тестовых данных
        game_data = {
            "players": ["player1", "player2"],
            "map_size": {"width": 1000, "height": 1000}
        }
        
        # Отправка запроса на создание игры
        response = await async_api_client.post(
            f"{battle_mechanics_url}/games/",
            json=game_data
        )
        
        # Проверка результата
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert len(data["players"]) == 2
        assert data["status"] == "waiting"
        assert data["turn"] == 0
    
    @pytest.mark.asyncio
    async def test_add_ship(self, async_api_client, battle_mechanics_url):
        """Тест добавления корабля в игру"""
        # Создаем игру
        game_data = {
            "players": ["player1", "player2"],
            "map_size": {"width": 1000, "height": 1000}
        }
        game_response = await async_api_client.post(
            f"{battle_mechanics_url}/games/",
            json=game_data
        )
        game_id = game_response.json()["id"]
        
        # Подготовка данных корабля
        ship_data = {
            "player_id": "player1",
            "position": {"x": 100, "y": 100},
            "rotation": 0,
            "health": 100,
            "fuel": 100,
            "torpedoes": 10
        }
        
        # Отправка запроса на добавление корабля
        response = await async_api_client.post(
            f"{battle_mechanics_url}/games/{game_id}/ships",
            json=ship_data
        )
        
        # Проверка результата
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["player_id"] == ship_data["player_id"]
        assert data["position"] == ship_data["position"]
    
    @pytest.mark.asyncio
    async def test_make_move(self, async_api_client, battle_mechanics_url):
        """Тест выполнения хода в игре"""
        # Создаем игру
        game_data = {
            "players": ["player1", "player2"],
            "map_size": {"width": 1000, "height": 1000}
        }
        game_response = await async_api_client.post(
            f"{battle_mechanics_url}/games/",
            json=game_data
        )
        game_id = game_response.json()["id"]
        
        # Добавляем корабли для обоих игроков
        for player_id in ["player1", "player2"]:
            ship_data = {
                "player_id": player_id,
                "position": {"x": 100 if player_id == "player1" else 900, "y": 100},
                "rotation": 0,
                "health": 100,
                "fuel": 100,
                "torpedoes": 10
            }
            await async_api_client.post(
                f"{battle_mechanics_url}/games/{game_id}/ships",
                json=ship_data
            )
        
        # Подготовка данных хода
        move_data = {
            "player_id": "player1",
            "actions": [
                {"type": "move", "direction": {"x": 10, "y": 0}},
                {"type": "rotate", "angle": 45}
            ]
        }
        
        # Отправка запроса на выполнение хода
        response = await async_api_client.post(
            f"{battle_mechanics_url}/games/{game_id}/moves",
            json=move_data
        )
        
        # Проверка результата
        assert response.status_code == 200
        data = response.json()
        assert data["turn"] == 1
        
        # Находим корабль игрока и проверяем его новую позицию
        player1_ship = next(
            (ship for ship in data["ships"] if ship["player_id"] == "player1"),
            None
        )
        assert player1_ship is not None
        assert player1_ship["position"]["x"] > 100  # корабль должен был сдвинуться вправо
        assert abs(player1_ship["rotation"] - 45) < 0.01  # корабль должен был повернуться 