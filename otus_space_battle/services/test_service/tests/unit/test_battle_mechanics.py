import pytest
import httpx

@pytest.mark.unit
class TestBattleMechanics:
    
    @pytest.mark.asyncio
    async def test_create_game(self, battle_mechanics_url):
        """Тест создания игры"""
        # Подготовка тестовых данных
        game_data = {
            "player1_id": "player1",
            "player2_id": "player2",
            "map_size": {"width": 100, "height": 100}
        }
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на создание игры
            response = await client.post(
                f"{battle_mechanics_url}/game/create",
                json=game_data
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert "game_id" in data
            assert data["status"] == "created"
    
    @pytest.mark.asyncio
    async def test_add_ship(self, battle_mechanics_url):
        """Тест добавления корабля"""
        # Создаем игру
        game_data = {
            "player1_id": "player1",
            "player2_id": "player2",
            "map_size": {"width": 100, "height": 100}
        }
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Создаем игру
            game_response = await client.post(
                f"{battle_mechanics_url}/game/create",
                json=game_data
            )
            game_id = game_response.json()["game_id"]
            
            # Добавляем корабль
            ship_data = {
                "game_id": game_id,
                "player_id": "player1",
                "ship_type": "battleship",
                "position": {"x": 10, "y": 10},
                "direction": "horizontal"
            }
            
            response = await client.post(
                f"{battle_mechanics_url}/game/{game_id}/ships",
                json=ship_data
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert "ship_id" in data
            assert data["position"] == ship_data["position"]
    
    @pytest.mark.asyncio
    async def test_make_move(self, battle_mechanics_url):
        """Тест выполнения хода"""
        # Создаем игру
        game_data = {
            "player1_id": "player1",
            "player2_id": "player2",
            "map_size": {"width": 100, "height": 100}
        }
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Создаем игру
            game_response = await client.post(
                f"{battle_mechanics_url}/game/create",
                json=game_data
            )
            game_id = game_response.json()["game_id"]
            
            # Добавляем корабль
            ship_data = {
                "game_id": game_id,
                "player_id": "player1",
                "ship_type": "battleship",
                "position": {"x": 10, "y": 10},
                "direction": "horizontal"
            }
            await client.post(
                f"{battle_mechanics_url}/game/{game_id}/ships",
                json=ship_data
            )
            
            # Выполняем ход
            move_data = {
                "game_id": game_id,
                "player_id": "player2",
                "target_position": {"x": 10, "y": 10}
            }
            
            response = await client.post(
                f"{battle_mechanics_url}/game/{game_id}/moves",
                json=move_data
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert "hit" in data
            assert data["hit"] is True 