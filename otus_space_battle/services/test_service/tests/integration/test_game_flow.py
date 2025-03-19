import pytest
import httpx
import time
import uuid

@pytest.mark.integration
class TestGameFlow:
    """Интеграционные тесты для проверки полного потока игры между сервисами"""
    
    @pytest.mark.asyncio
    async def test_complete_game_flow(self, async_api_client, api_gateway_url, auth_service_url):
        """Тест полного потока игры от регистрации до завершения матча"""
        # 1. Регистрация двух пользователей
        users = []
        for i in range(2):
            username = f"test_user_{uuid.uuid4().hex[:8]}"
            user_data = {
                "username": username,
                "email": f"{username}@example.com",
                "password": "TestPassword123"
            }
            
            response = await async_api_client.post(
                f"{auth_service_url}/auth/register",
                json=user_data
            )
            assert response.status_code == 200
            user = response.json()
            users.append(user)
            
            # Авторизация
            login_data = {
                "username": user_data["username"],
                "password": user_data["password"]
            }
            login_response = await async_api_client.post(
                f"{auth_service_url}/auth/login",
                json=login_data
            )
            assert login_response.status_code == 200
            token_data = login_response.json()
            users[i]["token"] = token_data["access_token"]
        
        # 2. Создание флотов для каждого пользователя
        for i, user in enumerate(users):
            # Запрос на создание флота
            fleet_data = {
                "name": f"Test Fleet {i+1}",
                "ships": [
                    {"ship_type_id": 1, "position": 1},
                    {"ship_type_id": 2, "position": 2},
                    {"ship_type_id": 3, "position": 3}
                ]
            }
            
            headers = {"Authorization": f"Bearer {user['token']}"}
            fleet_response = await async_api_client.post(
                f"{api_gateway_url}/fleets/",
                json=fleet_data,
                headers=headers
            )
            assert fleet_response.status_code == 200
            fleet = fleet_response.json()
            users[i]["fleet_id"] = fleet["id"]
        
        # 3. Пользователь 1 создает матч
        match_data = {
            "opponent_username": users[1]["username"],
            "fleet_id": users[0]["fleet_id"]
        }
        
        headers = {"Authorization": f"Bearer {users[0]['token']}"}
        match_response = await async_api_client.post(
            f"{api_gateway_url}/matches/",
            json=match_data,
            headers=headers
        )
        assert match_response.status_code == 200
        match = match_response.json()
        match_id = match["id"]
        
        # 4. Пользователь 2 принимает матч
        accept_data = {
            "fleet_id": users[1]["fleet_id"]
        }
        
        headers = {"Authorization": f"Bearer {users[1]['token']}"}
        accept_response = await async_api_client.post(
            f"{api_gateway_url}/matches/{match_id}/accept",
            json=accept_data,
            headers=headers
        )
        assert accept_response.status_code == 200
        
        # 5. Ожидаем начала игры
        time.sleep(2)
        
        # 6. Получаем состояние игры
        headers = {"Authorization": f"Bearer {users[0]['token']}"}
        game_response = await async_api_client.get(
            f"{api_gateway_url}/matches/{match_id}/status",
            headers=headers
        )
        assert game_response.status_code == 200
        game_status = game_response.json()
        assert game_status["status"] == "in_progress"
        
        # 7. Делаем несколько ходов
        for turn in range(3):
            # Ход первого игрока
            move_data = {
                "actions": [
                    {"type": "move", "direction": {"x": 10, "y": 5}},
                    {"type": "rotate", "angle": 15}
                ]
            }
            
            headers = {"Authorization": f"Bearer {users[turn % 2]['token']}"}
            move_response = await async_api_client.post(
                f"{api_gateway_url}/matches/{match_id}/move",
                json=move_data,
                headers=headers
            )
            assert move_response.status_code == 200
            
            # Небольшая задержка между ходами
            time.sleep(1)
        
        # 8. Завершаем игру (например, один из игроков сдается)
        headers = {"Authorization": f"Bearer {users[0]['token']}"}
        surrender_response = await async_api_client.post(
            f"{api_gateway_url}/matches/{match_id}/surrender",
            headers=headers
        )
        assert surrender_response.status_code == 200
        
        # 9. Проверяем, что игра завершена и победитель - второй игрок
        time.sleep(1)
        headers = {"Authorization": f"Bearer {users[0]['token']}"}
        final_status_response = await async_api_client.get(
            f"{api_gateway_url}/matches/{match_id}/status",
            headers=headers
        )
        assert final_status_response.status_code == 200
        final_status = final_status_response.json()
        assert final_status["status"] == "finished"
        assert final_status["winner_id"] == users[1]["id"]
        
        # 10. Проверяем, что рейтинг изменился
        for user in users:
            headers = {"Authorization": f"Bearer {user['token']}"}
            profile_response = await async_api_client.get(
                f"{api_gateway_url}/users/profile",
                headers=headers
            )
            assert profile_response.status_code == 200
            profile = profile_response.json()
            assert "rating" in profile 