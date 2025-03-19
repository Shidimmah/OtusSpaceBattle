import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.models.base import Base
from common.models.fleet import Fleet
from common.models.user import User

@pytest.mark.unit
class TestFleet:
    @pytest.fixture
    def engine(self):
        """Создаем тестовую базу данных"""
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        return engine
    
    @pytest.fixture
    def session(self, engine):
        """Создаем сессию для тестов"""
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    @pytest.fixture
    def user(self, session):
        """Создаем тестового пользователя"""
        user = User(username="test_user", email="test@example.com")
        session.add(user)
        session.commit()
        return user
    
    def test_fleet_creation(self, session, user):
        """Тест создания флота"""
        fleet = Fleet(
            user_id=user.id,
            name="Test Fleet"
        )
        session.add(fleet)
        session.commit()
        
        # Проверяем, что флот создан
        assert fleet.id is not None
        assert fleet.user_id == user.id
        assert fleet.name == "Test Fleet"
        assert isinstance(fleet.created_at, datetime)
        assert isinstance(fleet.updated_at, datetime)
    
    def test_fleet_update(self, session, user):
        """Тест обновления флота"""
        fleet = Fleet(
            user_id=user.id,
            name="Test Fleet"
        )
        session.add(fleet)
        session.commit()
        
        # Обновляем флот
        fleet.name = "Updated Fleet"
        session.commit()
        
        # Проверяем, что updated_at изменился
        assert fleet.name == "Updated Fleet"
        assert fleet.updated_at > fleet.created_at
    
    def test_unique_fleet_name_per_user(self, session, user):
        """Тест уникальности имени флота для пользователя"""
        # Создаем первый флот
        fleet1 = Fleet(
            user_id=user.id,
            name="Test Fleet"
        )
        session.add(fleet1)
        session.commit()
        
        # Пытаемся создать второй флот с тем же именем
        fleet2 = Fleet(
            user_id=user.id,
            name="Test Fleet"
        )
        session.add(fleet2)
        
        # Проверяем, что возникает ошибка
        with pytest.raises(Exception):
            session.commit()
    
    def test_fleet_cascade_delete(self, session, user):
        """Тест каскадного удаления флота"""
        fleet = Fleet(
            user_id=user.id,
            name="Test Fleet"
        )
        session.add(fleet)
        session.commit()
        
        # Удаляем пользователя
        session.delete(user)
        session.commit()
        
        # Проверяем, что флот тоже удален
        assert session.query(Fleet).filter_by(id=fleet.id).first() is None 