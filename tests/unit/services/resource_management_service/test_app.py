import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from services.resource_management_service.app import app, get_ship_resources, update_resources

client = TestClient(app)

@pytest.fixture
def test_ship_id():
    return "test_ship_123"

@pytest.mark.asyncio
async def test_get_ship_resources(test_ship_id, test_db):
    """Тест получения ресурсов корабля"""
    response = await client.get(f"/resources/{test_ship_id}")
    assert response.status_code == 200
    data = response.json()
    
    assert "fuel" in data
    assert "torpedoes" in data
    assert isinstance(data["fuel"], float)
    assert isinstance(data["torpedoes"], int)

@pytest.mark.asyncio
async def test_update_fuel(test_ship_id, test_db):
    """Тест обновления топлива"""
    update_data = {
        "resource_type": "fuel",
        "amount": -10.5  # Расход топлива
    }
    
    response = await client.post(
        f"/resources/{test_ship_id}/update",
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "fuel" in data
    assert data["fuel"] >= 0

@pytest.mark.asyncio
async def test_update_torpedoes(test_ship_id, test_db):
    """Тест обновления торпед"""
    update_data = {
        "resource_type": "torpedoes",
        "amount": -1  # Использование одной торпеды
    }
    
    response = await client.post(
        f"/resources/{test_ship_id}/update",
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "torpedoes" in data
    assert isinstance(data["torpedoes"], int)
    assert data["torpedoes"] >= 0

@pytest.mark.asyncio
async def test_insufficient_resources(test_ship_id, test_db):
    """Тест попытки использования ресурсов при их нехватке"""
    # Пытаемся использовать слишком много топлива
    update_data = {
        "resource_type": "fuel",
        "amount": -1000.0
    }
    
    response = await client.post(
        f"/resources/{test_ship_id}/update",
        json=update_data
    )
    assert response.status_code == 400
    assert "insufficient" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_invalid_resource_type(test_ship_id):
    """Тест обновления несуществующего типа ресурса"""
    update_data = {
        "resource_type": "invalid_resource",
        "amount": 10
    }
    
    response = await client.post(
        f"/resources/{test_ship_id}/update",
        json=update_data
    )
    assert response.status_code == 400
    assert "invalid resource type" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_negative_torpedoes(test_ship_id, test_db):
    """Тест попытки установить отрицательное количество торпед"""
    update_data = {
        "resource_type": "torpedoes",
        "amount": -100
    }
    
    response = await client.post(
        f"/resources/{test_ship_id}/update",
        json=update_data
    )
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_resource_limits(test_ship_id, test_db):
    """Тест лимитов ресурсов"""
    # Тест максимального количества топлива
    update_data = {
        "resource_type": "fuel",
        "amount": 1000000.0
    }
    
    response = await client.post(
        f"/resources/{test_ship_id}/update",
        json=update_data
    )
    assert response.status_code == 400
    
    # Тест максимального количества торпед
    update_data = {
        "resource_type": "torpedoes",
        "amount": 1000
    }
    
    response = await client.post(
        f"/resources/{test_ship_id}/update",
        json=update_data
    )
    assert response.status_code == 400 