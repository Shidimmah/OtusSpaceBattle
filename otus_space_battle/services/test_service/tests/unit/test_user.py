import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.models.base import Base
from common.models.user import User
from common.models.fleet import Fleet
from common.models.match import Match

@pytest.mark.unit
class TestUser:
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
    
    def test_user_creation(self, session):
        """Тест создания пользователя"""
        user = User(
            username="test_user",
            email="test@example.com",
            hashed_password="hashed_password123",
            rating=1000
        )
        session.add(user)
        session.commit()
        
        # Проверяем, что пользователь создан
        assert user.id is not None
        assert user.username == "test_user"
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_password123"
        assert user.rating == 1000
    
    def test_user_unique_constraints(self, session):
        """Тест уникальных ограничений пользователя"""
        # Создаем первого пользователя
        user1 = User(
            username="unique_user",
            email="unique@example.com",
            hashed_password="hashed_password123"
        )
        session.add(user1)
        session.commit()
        
        # Пытаемся создать второго пользователя с тем же username
        user2 = User(
            username="unique_user",
            email="another@example.com",
            hashed_password="hashed_password456"
        )
        session.add(user2)
        
        # Проверяем, что возникает ошибка
        with pytest.raises(Exception):
            session.commit()
        
        # Пытаемся создать пользователя с тем же email
        user3 = User(
            username="another_user",
            email="unique@example.com",
            hashed_password="hashed_password789"
        )
        session.add(user3)
        
        # Проверяем, что возникает ошибка
        with pytest.raises(Exception):
            session.commit()
    
    def test_user_relationships(self, session):
        """Тест связей пользователя"""
        # Создаем пользователя
        user = User(
            username="test_user",
            email="test@example.com",
            hashed_password="hashed_password123"
        )
        session.add(user)
        session.commit()
        
        # Создаем флот для пользователя
        fleet = Fleet(
            user_id=user.id,
            name="Test Fleet"
        )
        session.add(fleet)
        session.commit()
        
        # Создаем матч с пользователем
        match = Match(
            player1_id=user.id,
            status="waiting"
        )
        session.add(match)
        session.commit()
        
        # Проверяем связи
        assert fleet in user.fleets
        assert match in user.matches_as_player1
        
        # Проверяем обратные связи
        assert fleet.user == user
        assert match.player1 == user
    
    def test_user_rating_update(self, session):
        """Тест обновления рейтинга пользователя"""
        user = User(
            username="test_user",
            email="test@example.com",
            hashed_password="hashed_password123",
            rating=1000
        )
        session.add(user)
        session.commit()
        
        # Обновляем рейтинг
        user.rating = 1200
        session.commit()
        
        # Проверяем, что рейтинг обновлен
        assert user.rating == 1200
    
    def test_user_default_rating(self, session):
        """Тест значения рейтинга по умолчанию"""
        user = User(
            username="test_user",
            email="test@example.com",
            hashed_password="hashed_password123"
        )
        session.add(user)
        session.commit()
        
        # Проверяем значение рейтинга по умолчанию
        assert user.rating == 1000 