import pytest
import httpx
from datetime import datetime

@pytest.mark.integration
class TestBattleFlow:
    """Тесты полного цикла боя между двумя игроками"""

    async def test_complete_battle_flow(self):
        """Тест полного цикла боя от создания матча до его завершения"""
        async with httpx.AsyncClient() as client:
            # 1. Регистрация двух игроков
            player1_data = {
                "username": "test_player1",
                "email": "player1@test.com",
                "password": "test_password123"
            }
            player2_data = {
                "username": "test_player2",
                "email": "player2@test.com",
                "password": "test_password456"
            }

            player1_response = await client.post("/auth/register", json=player1_data)
            player2_response = await client.post("/auth/register", json=player2_data)

            assert player1_response.status_code == 200
            assert player2_response.status_code == 200

            player1_token = player1_response.json()["access_token"]
            player2_token = player2_response.json()["access_token"]

            # 2. Создание флотов для обоих игроков
            fleet1_data = {
                "name": "Test Fleet 1",
                "description": "Test Fleet Description 1"
            }
            fleet2_data = {
                "name": "Test Fleet 2",
                "description": "Test Fleet Description 2"
            }

            fleet1_response = await client.post(
                "/fleets",
                json=fleet1_data,
                headers={"Authorization": f"Bearer {player1_token}"}
            )
            fleet2_response = await client.post(
                "/fleets",
                json=fleet2_data,
                headers={"Authorization": f"Bearer {player2_token}"}
            )

            assert fleet1_response.status_code == 200
            assert fleet2_response.status_code == 200

            fleet1_id = fleet1_response.json()["fleet_id"]
            fleet2_id = fleet2_response.json()["fleet_id"]

            # 3. Добавление кораблей во флоты
            ship_type_data = {
                "name": "Test Ship Type",
                "description": "Test Ship Type Description",
                "fuel_capacity": 1000,
                "movement_speed": 10,
                "rotation_speed": 5,
                "torpedo_capacity": 10,
                "torpedo_damage": 50,
                "torpedo_speed": 20,
                "torpedo_range": 100,
                "torpedo_reload_time": 5,
                "shield_capacity": 100,
                "shield_recharge_rate": 5,
                "shield_recharge_delay": 2
            }

            # Создание типа корабля
            ship_type_response = await client.post(
                "/ships/types",
                json=ship_type_data,
                headers={"Authorization": f"Bearer {player1_token}"}
            )
            assert ship_type_response.status_code == 200
            ship_type_id = ship_type_response.json()["ship_type_id"]

            # Добавление кораблей во флоты
            ship1_data = {
                "fleet_id": fleet1_id,
                "ship_type_id": ship_type_id,
                "position": {"x": 0, "y": 0}
            }
            ship2_data = {
                "fleet_id": fleet2_id,
                "ship_type_id": ship_type_id,
                "position": {"x": 100, "y": 100}
            }

            ship1_response = await client.post(
                "/ships",
                json=ship1_data,
                headers={"Authorization": f"Bearer {player1_token}"}
            )
            ship2_response = await client.post(
                "/ships",
                json=ship2_data,
                headers={"Authorization": f"Bearer {player2_token}"}
            )

            assert ship1_response.status_code == 200
            assert ship2_response.status_code == 200

            ship1_id = ship1_response.json()["ship_id"]
            ship2_id = ship2_response.json()["ship_id"]

            # 4. Создание матча
            match_data = {
                "player1_fleet_id": fleet1_id,
                "player2_fleet_id": fleet2_id
            }

            match_response = await client.post(
                "/matches",
                json=match_data,
                headers={"Authorization": f"Bearer {player1_token}"}
            )
            assert match_response.status_code == 200
            match_id = match_response.json()["match_id"]

            # 5. Симуляция боя
            # Движение кораблей
            move1_data = {
                "ship_id": ship1_id,
                "position": {"x": 50, "y": 50}
            }
            move2_data = {
                "ship_id": ship2_id,
                "position": {"x": 150, "y": 150}
            }

            move1_response = await client.post(
                f"/matches/{match_id}/move",
                json=move1_data,
                headers={"Authorization": f"Bearer {player1_token}"}
            )
            move2_response = await client.post(
                f"/matches/{match_id}/move",
                json=move2_data,
                headers={"Authorization": f"Bearer {player2_token}"}
            )

            assert move1_response.status_code == 200
            assert move2_response.status_code == 200

            # Стрельба торпедами
            torpedo1_data = {
                "ship_id": ship1_id,
                "target_position": {"x": 150, "y": 150}
            }
            torpedo2_data = {
                "ship_id": ship2_id,
                "target_position": {"x": 50, "y": 50}
            }

            torpedo1_response = await client.post(
                f"/matches/{match_id}/torpedo",
                json=torpedo1_data,
                headers={"Authorization": f"Bearer {player1_token}"}
            )
            torpedo2_response = await client.post(
                f"/matches/{match_id}/torpedo",
                json=torpedo2_data,
                headers={"Authorization": f"Bearer {player2_token}"}
            )

            assert torpedo1_response.status_code == 200
            assert torpedo2_response.status_code == 200

            # 6. Завершение матча
            end_match_response = await client.post(
                f"/matches/{match_id}/end",
                headers={"Authorization": f"Bearer {player1_token}"}
            )
            assert end_match_response.status_code == 200

            # 7. Проверка результатов матча
            match_result_response = await client.get(
                f"/matches/{match_id}",
                headers={"Authorization": f"Bearer {player1_token}"}
            )
            assert match_result_response.status_code == 200
            match_result = match_result_response.json()

            assert match_result["status"] == "finished"
            assert "winner_id" in match_result
            assert "end_time" in match_result

            # 8. Проверка обновления рейтинга
            player1_rating_response = await client.get(
                f"/users/{player1_response.json()['user_id']}/rating",
                headers={"Authorization": f"Bearer {player1_token}"}
            )
            player2_rating_response = await client.get(
                f"/users/{player2_response.json()['user_id']}/rating",
                headers={"Authorization": f"Bearer {player2_token}"}
            )

            assert player1_rating_response.status_code == 200
            assert player2_rating_response.status_code == 200

            # 9. Проверка создания игровых событий
            events_response = await client.get(
                f"/matches/{match_id}/events",
                headers={"Authorization": f"Bearer {player1_token}"}
            )
            assert events_response.status_code == 200
            events = events_response.json()["events"]

            assert len(events) > 0
            event_types = [event["event_type"] for event in events]
            assert "move" in event_types
            assert "torpedo" in event_types
            assert "match_end" in event_types 