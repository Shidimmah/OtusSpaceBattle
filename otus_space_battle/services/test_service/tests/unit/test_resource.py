import pytest
from pydantic import ValidationError
from services.resource_management.src.models import Resource

@pytest.mark.unit
class TestResource:
    def test_resource_creation(self):
        """Тест создания ресурса"""
        resource = Resource(
            id="resource-1",
            type="fuel",
            amount=100,
            ship_id="ship-1"
        )
        
        # Проверяем, что ресурс создан
        assert resource.id == "resource-1"
        assert resource.type == "fuel"
        assert resource.amount == 100
        assert resource.ship_id == "ship-1"
    
    def test_resource_creation_without_ship(self):
        """Тест создания ресурса без привязки к кораблю"""
        resource = Resource(
            id="resource-2",
            type="torpedo",
            amount=50
        )
        
        # Проверяем, что ресурс создан
        assert resource.id == "resource-2"
        assert resource.type == "torpedo"
        assert resource.amount == 50
        assert resource.ship_id is None
    
    def test_resource_validation(self):
        """Тест валидации данных ресурса"""
        # Проверяем, что отрицательное количество вызывает ошибку
        with pytest.raises(ValidationError):
            Resource(
                id="resource-3",
                type="fuel",
                amount=-100,
                ship_id="ship-1"
            )
        
        # Проверяем, что пустой тип вызывает ошибку
        with pytest.raises(ValidationError):
            Resource(
                id="resource-4",
                type="",
                amount=100,
                ship_id="ship-1"
            )
    
    def test_resource_update(self):
        """Тест обновления ресурса"""
        resource = Resource(
            id="resource-5",
            type="fuel",
            amount=100,
            ship_id="ship-1"
        )
        
        # Обновляем количество
        resource.amount = 200
        
        # Проверяем, что количество обновлено
        assert resource.amount == 200
        
        # Обновляем тип
        resource.type = "torpedo"
        
        # Проверяем, что тип обновлен
        assert resource.type == "torpedo"
    
    def test_resource_schema(self):
        """Тест схемы ресурса"""
        resource = Resource(
            id="resource-6",
            type="fuel",
            amount=100,
            ship_id="ship-1"
        )
        
        # Проверяем, что схема соответствует ожидаемой
        schema = resource.schema()
        assert "id" in schema["properties"]
        assert "type" in schema["properties"]
        assert "amount" in schema["properties"]
        assert "ship_id" in schema["properties"]
        assert schema["properties"]["ship_id"]["type"] == "string"
        assert schema["properties"]["ship_id"]["nullable"] is True 