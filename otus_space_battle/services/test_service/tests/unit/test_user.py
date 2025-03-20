import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.models.user import User
from common.models.base import Base

@pytest.mark.unit
class TestUser:
    @pytest.fixture
    def engine(self):
        """Фикстура для создания тестового движка базы данных"""
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        yield engine
        Base.metadata.drop_all(engine)

    @pytest.fixture
    def session(self, engine):
        """Фикстура для создания тестовой сессии"""
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_user_creation(self, session):
        """Тест создания пользователя"""
        # Создаем пользователя
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

    def test_user_unique_username(self, session):
        """Тест уникальности имени пользователя"""
        # Создаем первого пользователя
        user1 = User(
            username="test_user",
            email="test1@example.com",
            hashed_password="hashed_password123"
        )
        session.add(user1)
        session.commit()

        # Пытаемся создать второго пользователя с тем же именем
        user2 = User(
            username="test_user",
            email="test2@example.com",
            hashed_password="hashed_password456"
        )
        session.add(user2)
        
        # Проверяем, что возникает исключение
        with pytest.raises(Exception):
            session.commit()

    def test_user_unique_email(self, session):
        """Тест уникальности email"""
        # Создаем первого пользователя
        user1 = User(
            username="test_user1",
            email="test@example.com",
            hashed_password="hashed_password123"
        )
        session.add(user1)
        session.commit()

        # Пытаемся создать второго пользователя с тем же email
        user2 = User(
            username="test_user2",
            email="test@example.com",
            hashed_password="hashed_password456"
        )
        session.add(user2)
        
        # Проверяем, что возникает исключение
        with pytest.raises(Exception):
            session.commit()

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
        user.rating = 1500
        session.commit()

        # Проверяем, что рейтинг обновился
        updated_user = session.query(User).filter_by(username="test_user").first()
        assert updated_user.rating == 1500

    def test_user_relationships(self, session):
        """Тест инициализации отношений пользователя"""
        # Создаем пользователя
        user = User(
            username="test_user",
            email="test@example.com",
            hashed_password="hashed_password123"
        )
        session.add(user)
        session.commit()
        
        # Проверяем инициализацию отношений
        assert user.fleets is not None
        assert user.matches_as_player1 is not None
        assert user.matches_as_player2 is not None

    def test_user_cascade_delete(self, session):
        """Тест каскадного удаления пользователя"""
        user = User(
            username="test_user",
            email="test@example.com",
            hashed_password="hashed_password123"
        )
        session.add(user)
        session.commit()

        # Удаляем пользователя
        session.delete(user)
        session.commit()

        # Проверяем, что пользователь удален
        deleted_user = session.query(User).filter_by(username="test_user").first()
        assert deleted_user is None 