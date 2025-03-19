import pytest
from sqlalchemy.orm import Session
from common.database import get_db, init_models, engine, Base, SessionLocal
from sqlalchemy import Column, Integer, String, inspect

@pytest.mark.unit
class TestDatabase:
    def test_get_db(self):
        """Тест получения сессии базы данных"""
        db = next(get_db())
        assert isinstance(db, Session)
        db.close()
    
    @pytest.mark.asyncio
    async def test_init_models(self):
        """Тест инициализации моделей базы данных"""
        # Создаем тестовую таблицу
        class TestModel(Base):
            __tablename__ = "test_table"
            id = Column(Integer, primary_key=True)
            name = Column(String)
        
        # Инициализируем модели
        await init_models()
        
        # Проверяем, что таблица создана
        inspector = inspect(engine)
        assert "test_table" in inspector.get_table_names()
        
        # Очищаем после теста
        TestModel.__table__.drop(engine)
    
    def test_session_local(self):
        """Тест создания сессии через SessionLocal"""
        db = SessionLocal()
        assert isinstance(db, Session)
        db.close()
    
    def test_engine_pool(self):
        """Тест пула соединений"""
        assert engine.pool.size() <= 5  # Проверяем размер пула
        assert engine.pool.checkedin() >= 0  # Проверяем количество активных соединений 