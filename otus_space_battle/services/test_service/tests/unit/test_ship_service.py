import pytest
import httpx

@pytest.mark.unit
class TestShipService:
    
    @pytest.mark.asyncio
    async def test_create_ship(self, ship_service_url):
        """Тест создания корабля"""
        # Подготовка тестовых данных
        ship_data = {
            "fleet_id": "fleet123",
            "ship_type": "battleship",
            "position": {"x": 10, "y": 10},
            "direction": "horizontal"
        }
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на создание корабля
            response = await client.post(
                f"{ship_service_url}/ships",
                json=ship_data
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert "ship_id" in data
            assert data["ship_type"] == ship_data["ship_type"]
            assert data["position"] == ship_data["position"]
    
    @pytest.mark.asyncio
    async def test_get_ship(self, ship_service_url):
        """Тест получения информации о корабле"""
        # Подготовка тестовых данных
        ship_id = "ship123"
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на получение информации о корабле
            response = await client.get(
                f"{ship_service_url}/ships/{ship_id}"
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert "ship_id" in data
            assert "ship_type" in data
            assert "position" in data
            assert "direction" in data
            assert "fleet_id" in data
    
    @pytest.mark.asyncio
    async def test_update_ship_position(self, ship_service_url):
        """Тест обновления позиции корабля"""
        # Подготовка тестовых данных
        ship_id = "ship123"
        position_data = {
            "position": {"x": 20, "y": 20},
            "direction": "vertical"
        }
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на обновление позиции корабля
            response = await client.put(
                f"{ship_service_url}/ships/{ship_id}/position",
                json=position_data
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert data["position"] == position_data["position"]
            assert data["direction"] == position_data["direction"] 