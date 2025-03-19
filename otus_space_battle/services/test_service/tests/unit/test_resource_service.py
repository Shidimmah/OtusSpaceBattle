import pytest
import httpx

@pytest.mark.unit
class TestResourceService:
    
    @pytest.mark.asyncio
    async def test_create_resource(self, resource_service_url):
        """Тест создания ресурса"""
        # Подготовка тестовых данных
        resource_data = {
            "user_id": "user123",
            "resource_type": "fuel",
            "amount": 100,
            "location": {"x": 10, "y": 10}
        }
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на создание ресурса
            response = await client.post(
                f"{resource_service_url}/resources",
                json=resource_data
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert "resource_id" in data
            assert data["resource_type"] == resource_data["resource_type"]
            assert data["amount"] == resource_data["amount"]
    
    @pytest.mark.asyncio
    async def test_get_user_resources(self, resource_service_url):
        """Тест получения ресурсов пользователя"""
        # Подготовка тестовых данных
        user_id = "user123"
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на получение ресурсов
            response = await client.get(
                f"{resource_service_url}/users/{user_id}/resources"
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert "resources" in data
            assert isinstance(data["resources"], list)
            for resource in data["resources"]:
                assert resource["user_id"] == user_id
    
    @pytest.mark.asyncio
    async def test_update_resource_amount(self, resource_service_url):
        """Тест обновления количества ресурса"""
        # Подготовка тестовых данных
        resource_id = "resource123"
        update_data = {
            "amount": 150,
            "operation": "add"
        }
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на обновление количества
            response = await client.put(
                f"{resource_service_url}/resources/{resource_id}/amount",
                json=update_data
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert data["amount"] == 250  # Предполагая, что начальное количество было 100
            assert "updated_at" in data 