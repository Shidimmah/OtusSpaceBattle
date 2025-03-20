import pytest
import httpx
from unittest.mock import patch, MagicMock

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
    
    @pytest.mark.asyncio
    async def test_create_battle(self, httpx_mock):
        # Подготавливаем данные для запроса
        battle_data = {
            "match_id": "123e4567-e89b-12d3-a456-426614174000",
            "player1_fleet_id": "123e4567-e89b-12d3-a456-426614174001",
            "player2_fleet_id": "123e4567-e89b-12d3-a456-426614174002",
            "map_size": {"width": 1000, "height": 1000},
            "game_rules": {"max_turns": 100, "victory_conditions": ["elimination"]}
        }
        
        # Настраиваем мок для HTTP-запроса
        httpx_mock.add_response(
            method="POST",
            url="http://battle-service:8080/battles",
            json={
                "battle_id": "123e4567-e89b-12d3-a456-426614174003",
                "status": "created",
                "match_id": battle_data["match_id"],
                "player1_fleet_id": battle_data["player1_fleet_id"],
                "player2_fleet_id": battle_data["player2_fleet_id"],
                "current_turn": 0,
                "map_size": battle_data["map_size"],
                "game_rules": battle_data["game_rules"]
            },
            status_code=201
        )
        
        # Отправляем запрос
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://battle-service:8080/battles",
                json=battle_data
            )
            
        # Проверяем ответ
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["battle_id"] is not None
        assert response_data["status"] == "created"
        assert response_data["match_id"] == battle_data["match_id"]
        assert response_data["player1_fleet_id"] == battle_data["player1_fleet_id"]
        assert response_data["player2_fleet_id"] == battle_data["player2_fleet_id"]
        assert response_data["current_turn"] == 0
        assert response_data["map_size"] == battle_data["map_size"]
        assert response_data["game_rules"] == battle_data["game_rules"]
    
    @pytest.mark.asyncio
    async def test_get_battle_state(self, httpx_mock):
        # Идентификатор битвы
        battle_id = "123e4567-e89b-12d3-a456-426614174003"
        
        # Настраиваем мок для HTTP-запроса
        httpx_mock.add_response(
            method="GET",
            url=f"http://battle-service:8080/battles/{battle_id}",
            json={
                "battle_id": battle_id,
                "status": "in_progress",
                "match_id": "123e4567-e89b-12d3-a456-426614174000",
                "player1_fleet_id": "123e4567-e89b-12d3-a456-426614174001",
                "player2_fleet_id": "123e4567-e89b-12d3-a456-426614174002",
                "current_turn": 3,
                "map_size": {"width": 1000, "height": 1000},
                "game_rules": {"max_turns": 100, "victory_conditions": ["elimination"]},
                "ships": [
                    {
                        "ship_id": "123e4567-e89b-12d3-a456-426614174010",
                        "fleet_id": "123e4567-e89b-12d3-a456-426614174001",
                        "type": "destroyer",
                        "position": {"x": 100, "y": 200},
                        "health": 80,
                        "weapons": [{"name": "laser", "damage": 20, "cooldown": 2}]
                    },
                    {
                        "ship_id": "123e4567-e89b-12d3-a456-426614174011",
                        "fleet_id": "123e4567-e89b-12d3-a456-426614174002",
                        "type": "cruiser",
                        "position": {"x": 500, "y": 600},
                        "health": 150,
                        "weapons": [{"name": "missiles", "damage": 30, "cooldown": 3}]
                    }
                ],
                "actions_history": [
                    {"turn": 1, "ship_id": "123e4567-e89b-12d3-a456-426614174010", "action": "move", "params": {"x": 100, "y": 200}},
                    {"turn": 2, "ship_id": "123e4567-e89b-12d3-a456-426614174011", "action": "move", "params": {"x": 500, "y": 600}},
                    {"turn": 3, "ship_id": "123e4567-e89b-12d3-a456-426614174010", "action": "attack", "params": {"target_id": "123e4567-e89b-12d3-a456-426614174011"}}
                ]
            },
            status_code=200
        )
        
        # Отправляем запрос
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://battle-service:8080/battles/{battle_id}")
            
        # Проверяем ответ
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["battle_id"] == battle_id
        assert response_data["status"] == "in_progress"
        assert response_data["current_turn"] == 3
        assert len(response_data["ships"]) == 2
        assert len(response_data["actions_history"]) == 3
        
        # Проверяем состояние кораблей
        ship1 = next(ship for ship in response_data["ships"] if ship["fleet_id"] == "123e4567-e89b-12d3-a456-426614174001")
        ship2 = next(ship for ship in response_data["ships"] if ship["fleet_id"] == "123e4567-e89b-12d3-a456-426614174002")
        assert ship1["type"] == "destroyer"
        assert ship2["type"] == "cruiser"
        assert ship1["health"] == 80
        assert ship2["health"] == 150
    
    @pytest.mark.asyncio
    async def test_submit_action(self, httpx_mock):
        # Подготавливаем данные для запроса
        battle_id = "123e4567-e89b-12d3-a456-426614174003"
        action_data = {
            "ship_id": "123e4567-e89b-12d3-a456-426614174010",
            "action": "attack",
            "params": {"target_id": "123e4567-e89b-12d3-a456-426614174011"}
        }
        
        # Настраиваем мок для HTTP-запроса
        httpx_mock.add_response(
            method="POST",
            url=f"http://battle-service:8080/battles/{battle_id}/actions",
            json={
                "success": True,
                "message": "Action submitted successfully",
                "action_id": "123e4567-e89b-12d3-a456-426614174020",
                "battle_id": battle_id,
                "turn": 4
            },
            status_code=200
        )
        
        # Отправляем запрос
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://battle-service:8080/battles/{battle_id}/actions",
                json=action_data
            )
            
        # Проверяем ответ
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["action_id"] is not None
        assert response_data["battle_id"] == battle_id
        assert response_data["turn"] == 4
    
    @pytest.mark.asyncio
    async def test_end_turn(self, httpx_mock):
        # Подготавливаем данные для запроса
        battle_id = "123e4567-e89b-12d3-a456-426614174003"
        
        # Настраиваем мок для HTTP-запроса
        httpx_mock.add_response(
            method="POST",
            url=f"http://battle-service:8080/battles/{battle_id}/end-turn",
            json={
                "success": True,
                "message": "Turn ended successfully",
                "battle_id": battle_id,
                "previous_turn": 4,
                "current_turn": 5,
                "status": "in_progress",
                "events": [
                    {"type": "damage", "ship_id": "123e4567-e89b-12d3-a456-426614174011", "amount": 20},
                    {"type": "move", "ship_id": "123e4567-e89b-12d3-a456-426614174010", "x": 120, "y": 220}
                ]
            },
            status_code=200
        )
        
        # Отправляем запрос
        async with httpx.AsyncClient() as client:
            response = await client.post(f"http://battle-service:8080/battles/{battle_id}/end-turn")
            
        # Проверяем ответ
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["battle_id"] == battle_id
        assert response_data["previous_turn"] == 4
        assert response_data["current_turn"] == 5
        assert response_data["status"] == "in_progress"
        assert len(response_data["events"]) == 2
        
        # Проверяем события
        damage_event = next(event for event in response_data["events"] if event["type"] == "damage")
        move_event = next(event for event in response_data["events"] if event["type"] == "move")
        assert damage_event["ship_id"] == "123e4567-e89b-12d3-a456-426614174011"
        assert damage_event["amount"] == 20
        assert move_event["ship_id"] == "123e4567-e89b-12d3-a456-426614174010"
        assert move_event["x"] == 120
        assert move_event["y"] == 220
    
    @pytest.mark.asyncio
    async def test_end_battle(self, httpx_mock):
        # Подготавливаем данные для запроса
        battle_id = "123e4567-e89b-12d3-a456-426614174003"
        
        # Настраиваем мок для HTTP-запроса
        httpx_mock.add_response(
            method="POST",
            url=f"http://battle-service:8080/battles/{battle_id}/end",
            json={
                "success": True,
                "message": "Battle ended successfully",
                "battle_id": battle_id,
                "winner_fleet_id": "123e4567-e89b-12d3-a456-426614174001",
                "status": "completed",
                "turns_played": 10,
                "victory_condition": "elimination"
            },
            status_code=200
        )
        
        # Отправляем запрос
        async with httpx.AsyncClient() as client:
            response = await client.post(f"http://battle-service:8080/battles/{battle_id}/end")
            
        # Проверяем ответ
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["battle_id"] == battle_id
        assert response_data["winner_fleet_id"] == "123e4567-e89b-12d3-a456-426614174001"
        assert response_data["status"] == "completed"
        assert response_data["turns_played"] == 10
        assert response_data["victory_condition"] == "elimination" 