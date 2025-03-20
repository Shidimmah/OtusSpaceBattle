import pytest
import httpx

@pytest.mark.unit
class TestFleetService:
    
    @pytest.mark.asyncio
    async def test_create_fleet(self, fleet_service_url):
        """Тест создания флота"""
        # Подготовка тестовых данных
        fleet_data = {
            "user_id": "testuser123",
            "name": "Test Fleet",
            "ships": [
                {
                    "ship_type": "battleship",
                    "position": {"x": 10, "y": 10},
                    "direction": "horizontal"
                }
            ]
        }
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на создание флота
            response = await client.post(
                f"{fleet_service_url}/fleets",
                json=fleet_data
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert "fleet_id" in data
            assert data["name"] == fleet_data["name"]
            assert len(data["ships"]) == len(fleet_data["ships"])
    
    @pytest.mark.asyncio
    async def test_get_fleet(self, fleet_service_url):
        """Тест получения информации о флоте"""
        # Подготовка тестовых данных
        fleet_id = "fleet123"
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на получение информации о флоте
            response = await client.get(
                f"{fleet_service_url}/fleets/{fleet_id}"
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert "fleet_id" in data
            assert "name" in data
            assert "ships" in data
            assert "user_id" in data
    
    @pytest.mark.asyncio
    async def test_update_fleet(self, fleet_service_url):
        """Тест обновления флота"""
        # Подготовка тестовых данных
        fleet_id = "fleet123"
        update_data = {
            "name": "Updated Fleet",
            "ships": [
                {
                    "ship_type": "cruiser",
                    "position": {"x": 20, "y": 20},
                    "direction": "vertical"
                }
            ]
        }
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на обновление флота
            response = await client.put(
                f"{fleet_service_url}/fleets/{fleet_id}",
                json=update_data
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == update_data["name"]
            assert len(data["ships"]) == len(update_data["ships"]) 