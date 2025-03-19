import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.models.fleet import Fleet
from common.models.user import User
from common.models.base import Base

@pytest.mark.unit
class TestFleet:
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

    @pytest.fixture
    def user(self, session):
        """Фикстура для создания тестового пользователя"""
        user = User(
            username="test_user",
            email="test@example.com",
            hashed_password="hashed_password123"
        )
        session.add(user)
        session.commit()
        return user

    def test_fleet_creation(self, session, user):
        """Тест создания флота"""
        fleet = Fleet(
            user_id=user.id,
            name="Test Fleet",
            description="Test Fleet Description"
        )
        session.add(fleet)
        session.commit()

        # Проверяем, что флот создан
        assert fleet.id is not None
        assert fleet.user_id == user.id
        assert fleet.name == "Test Fleet"
        assert fleet.description == "Test Fleet Description"
        assert isinstance(fleet.created_at, datetime)

    def test_fleet_user_relationship(self, session, user):
        """Тест связи флота с пользователем"""
        fleet = Fleet(
            user_id=user.id,
            name="Test Fleet",
            description="Test Fleet Description"
        )
        session.add(fleet)
        session.commit()

        # Проверяем связь с пользователем
        assert fleet.user == user
        assert fleet in user.fleets

    def test_fleet_ships_relationship(self, session, user):
        """Тест связи флота с кораблями"""
        fleet = Fleet(
            user_id=user.id,
            name="Test Fleet",
            description="Test Fleet Description"
        )
        session.add(fleet)
        session.commit()

        # Проверяем, что связь с кораблями инициализирована
        assert fleet.ships is not None

    def test_fleet_matches_relationship(self, session, user):
        """Тест связи флота с матчами"""
        fleet = Fleet(
            user_id=user.id,
            name="Test Fleet",
            description="Test Fleet Description"
        )
        session.add(fleet)
        session.commit()

        # Проверяем связи с матчами
        assert fleet.matches_as_player1 is not None
        assert fleet.matches_as_player2 is not None

    def test_fleet_cascade_delete(self, session, user):
        """Тест каскадного удаления флота"""
        fleet = Fleet(
            user_id=user.id,
            name="Test Fleet",
            description="Test Fleet Description"
        )
        session.add(fleet)
        session.commit()

        # Удаляем флот
        session.delete(fleet)
        session.commit()

        # Проверяем, что флот удален
        deleted_fleet = session.query(Fleet).filter_by(name="Test Fleet").first()
        assert deleted_fleet is None

    def test_fleet_user_null_on_delete(self, session, user):
        """Тест установки user_id в NULL при удалении пользователя"""
        fleet = Fleet(
            user_id=user.id,
            name="Test Fleet",
            description="Test Fleet Description"
        )
        session.add(fleet)
        session.commit()

        # Удаляем пользователя
        session.delete(user)
        session.commit()

        # Проверяем, что user_id установлен в NULL
        updated_fleet = session.query(Fleet).filter_by(name="Test Fleet").first()
        assert updated_fleet.user_id is None

    def test_fleet_unique_name_per_user(self, session, user):
        """Тест уникальности имени флота для пользователя"""
        # Создаем первый флот
        fleet1 = Fleet(
            user_id=user.id,
            name="Test Fleet",
            description="Test Fleet Description 1"
        )
        session.add(fleet1)
        session.commit()

        # Пытаемся создать второй флот с тем же именем
        fleet2 = Fleet(
            user_id=user.id,
            name="Test Fleet",
            description="Test Fleet Description 2"
        )
        session.add(fleet2)
        
        # Проверяем, что возникает исключение
        with pytest.raises(Exception):
            session.commit()

    def test_fleet_same_name_different_users(self, session):
        """Тест возможности создания флотов с одинаковым именем для разных пользователей"""
        # Создаем двух пользователей
        user1 = User(
            username="test_user1",
            email="test1@example.com",
            hashed_password="hashed_password123"
        )
        user2 = User(
            username="test_user2",
            email="test2@example.com",
            hashed_password="hashed_password456"
        )
        session.add(user1)
        session.add(user2)
        session.commit()

        # Создаем флоты с одинаковым именем для разных пользователей
        fleet1 = Fleet(
            user_id=user1.id,
            name="Test Fleet",
            description="Test Fleet Description 1"
        )
        fleet2 = Fleet(
            user_id=user2.id,
            name="Test Fleet",
            description="Test Fleet Description 2"
        )
        session.add(fleet1)
        session.add(fleet2)
        session.commit()

        # Проверяем, что оба флота созданы
        assert fleet1.id is not None
        assert fleet2.id is not None
        assert fleet1.name == fleet2.name
        assert fleet1.user_id != fleet2.user_id 