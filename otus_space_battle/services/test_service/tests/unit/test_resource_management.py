import pytest
import httpx
import uuid

@pytest.mark.unit
class TestResourceManagement:
    
    @pytest.mark.asyncio
    async def test_get_resources(self, async_api_client, resource_management_url):
        """Тест получения списка ресурсов"""
        # Отправка запроса на получение ресурсов
        response = await async_api_client.get(
            f"{resource_management_url}/resources/"
        )
        
        # Проверка результата
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_create_resource(self, async_api_client, resource_management_url):
        """Тест создания нового ресурса"""
        # Подготовка тестовых данных
        resource_data = {
            "type": "fuel",
            "amount": 100
        }
        
        # Отправка запроса на создание ресурса
        response = await async_api_client.post(
            f"{resource_management_url}/resources/",
            json=resource_data
        )
        
        # Проверка результата
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["type"] == resource_data["type"]
        assert data["amount"] == resource_data["amount"]
    
    @pytest.mark.asyncio
    async def test_assign_resource(self, async_api_client, resource_management_url):
        """Тест назначения ресурса кораблю"""
        # Создаем ресурс
        resource_data = {
            "type": "torpedo",
            "amount": 50
        }
        resource_response = await async_api_client.post(
            f"{resource_management_url}/resources/",
            json=resource_data
        )
        resource_id = resource_response.json()["id"]
        
        # Данные о назначении
        ship_id = str(uuid.uuid4())
        assign_data = {
            "ship_id": ship_id
        }
        
        # Отправка запроса на назначение ресурса
        response = await async_api_client.put(
            f"{resource_management_url}/resources/{resource_id}/assign",
            json=assign_data
        )
        
        # Проверка результата
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == resource_id
        assert data["ship_id"] == ship_id
    
    @pytest.mark.asyncio
    async def test_consume_resource(self, async_api_client, resource_management_url):
        """Тест расхода ресурса"""
        # Создаем ресурс
        resource_data = {
            "type": "fuel",
            "amount": 100
        }
        resource_response = await async_api_client.post(
            f"{resource_management_url}/resources/",
            json=resource_data
        )
        resource_id = resource_response.json()["id"]
        
        # Назначаем ресурс кораблю
        ship_id = str(uuid.uuid4())
        await async_api_client.put(
            f"{resource_management_url}/resources/{resource_id}/assign",
            json={"ship_id": ship_id}
        )
        
        # Данные о расходе
        consume_data = {
            "amount": 25
        }
        
        # Отправка запроса на расход ресурса
        response = await async_api_client.put(
            f"{resource_management_url}/resources/{resource_id}/consume",
            json=consume_data
        )
        
        # Проверка результата
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == resource_id
        assert data["amount"] == resource_data["amount"] - consume_data["amount"] 