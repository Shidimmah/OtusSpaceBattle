import pytest
from sqlalchemy import Column, Integer, String
from common.models.base import Base

@pytest.mark.unit
class TestBaseModel:
    def test_base_model_inheritance(self):
        """Тест наследования от базовой модели"""
        class TestModel(Base):
            __tablename__ = "test_table"
            id = Column(Integer, primary_key=True)
            name = Column(String)
        
        # Проверяем, что модель правильно наследуется от Base
        assert issubclass(TestModel, Base)
        assert hasattr(TestModel, '__tablename__')
        assert hasattr(TestModel, 'id')
        assert hasattr(TestModel, 'name')
        
        # Проверяем, что колонки правильно определены
        assert isinstance(TestModel.id, Column)
        assert isinstance(TestModel.name, Column)
        
        # Проверяем, что primary key установлен
        assert TestModel.id.primary_key 