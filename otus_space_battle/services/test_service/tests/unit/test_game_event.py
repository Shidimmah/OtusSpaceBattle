import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.models.game_event import GameEvent
from common.models.match import Match
from common.models.fleet import Fleet
from common.models.user import User
from common.models.ship import Ship, ShipType
from common.models.base import Base

@pytest.mark.unit
class TestGameEvent:
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
    def user1(self, session):
        """Фикстура для создания первого тестового пользователя"""
        user = User(
            username="test_user1",
            email="test1@example.com",
            hashed_password="hashed_password123"
        )
        session.add(user)
        session.commit()
        return user

    @pytest.fixture
    def user2(self, session):
        """Фикстура для создания второго тестового пользователя"""
        user = User(
            username="test_user2",
            email="test2@example.com",
            hashed_password="hashed_password456"
        )
        session.add(user)
        session.commit()
        return user

    @pytest.fixture
    def fleet1(self, session, user1):
        """Фикстура для создания первого тестового флота"""
        fleet = Fleet(
            user_id=user1.id,
            name="Test Fleet 1"
        )
        session.add(fleet)
        session.commit()
        return fleet

    @pytest.fixture
    def fleet2(self, session, user2):
        """Фикстура для создания второго тестового флота"""
        fleet = Fleet(
            user_id=user2.id,
            name="Test Fleet 2"
        )
        session.add(fleet)
        session.commit()
        return fleet

    @pytest.fixture
    def match(self, session, user1, user2, fleet1, fleet2):
        """Фикстура для создания тестового матча"""
        match = Match(
            player1_id=user1.id,
            player2_id=user2.id,
            player1_fleet_id=fleet1.id,
            player2_fleet_id=fleet2.id,
            status="in_progress"
        )
        session.add(match)
        session.commit()
        return match

    @pytest.fixture
    def ship_type(self, session):
        """Фикстура для создания тестового типа корабля"""
        ship_type = ShipType(
            name="Test Ship Type",
            description="Test Ship Type Description",
            base_fuel_capacity=1000,
            base_torpedo_capacity=10,
            base_movement_speed=10.0,
            base_rotation_speed=5.0,
            fuel_consumption_move=1.0,
            fuel_consumption_rotate=0.5
        )
        session.add(ship_type)
        session.commit()
        return ship_type

    @pytest.fixture
    def ship(self, session, fleet1, ship_type):
        """Фикстура для создания тестового корабля"""
        ship = Ship(
            fleet_id=fleet1.id,
            ship_type_id=ship_type.id,
            position={"x": 0, "y": 0}
        )
        session.add(ship)
        session.commit()
        return ship

    def test_game_event_creation(self, session, match, ship):
        """Тест создания игрового события"""
        event = GameEvent(
            match_id=match.id,
            event_type="move",
            ship_id=ship.id,
            data={"x": 100, "y": 100}
        )
        session.add(event)
        session.commit()

        # Проверяем, что событие создано
        assert event.id is not None
        assert event.match_id == match.id
        assert event.event_type == "move"
        assert event.ship_id == ship.id
        assert event.data == {"x": 100, "y": 100}
        assert isinstance(event.timestamp, datetime)

    def test_game_event_without_ship(self, session, match):
        """Тест создания игрового события без корабля"""
        event = GameEvent(
            match_id=match.id,
            event_type="match_start",
            data={"status": "started"}
        )
        session.add(event)
        session.commit()

        # Проверяем, что событие создано
        assert event.id is not None
        assert event.match_id == match.id
        assert event.event_type == "match_start"
        assert event.ship_id is None
        assert event.data == {"status": "started"}
        assert isinstance(event.timestamp, datetime)

    def test_game_event_match_relationship(self, session, match, ship):
        """Тест связи игрового события с матчем"""
        event = GameEvent(
            match_id=match.id,
            event_type="move",
            ship_id=ship.id,
            data={"x": 100, "y": 100}
        )
        session.add(event)
        session.commit()

        # Проверяем связь с матчем
        assert event.match == match
        assert event in match.events

    def test_game_event_ship_relationship(self, session, match, ship):
        """Тест связи игрового события с кораблем"""
        event = GameEvent(
            match_id=match.id,
            event_type="move",
            ship_id=ship.id,
            data={"x": 100, "y": 100}
        )
        session.add(event)
        session.commit()

        # Проверяем связь с кораблем
        assert event.ship == ship
        assert event in ship.events

    def test_game_event_cascade_delete(self, session, match, ship):
        """Тест каскадного удаления игрового события"""
        event = GameEvent(
            match_id=match.id,
            event_type="move",
            ship_id=ship.id,
            data={"x": 100, "y": 100}
        )
        session.add(event)
        session.commit()

        # Удаляем событие
        session.delete(event)
        session.commit()

        # Проверяем, что событие удалено
        deleted_event = session.query(GameEvent).filter_by(id=event.id).first()
        assert deleted_event is None

    def test_game_event_match_cascade_delete(self, session, match, ship):
        """Тест каскадного удаления матча"""
        event = GameEvent(
            match_id=match.id,
            event_type="move",
            ship_id=ship.id,
            data={"x": 100, "y": 100}
        )
        session.add(event)
        session.commit()

        # Удаляем матч
        session.delete(match)
        session.commit()

        # Проверяем, что событие удалено
        deleted_event = session.query(GameEvent).filter_by(id=event.id).first()
        assert deleted_event is None

    def test_game_event_ship_null_on_delete(self, session, match, ship):
        """Тест установки ship_id в NULL при удалении корабля"""
        event = GameEvent(
            match_id=match.id,
            event_type="move",
            ship_id=ship.id,
            data={"x": 100, "y": 100}
        )
        session.add(event)
        session.commit()

        # Удаляем корабль
        session.delete(ship)
        session.commit()

        # Проверяем, что ship_id установлен в NULL
        updated_event = session.query(GameEvent).filter_by(id=event.id).first()
        assert updated_event.ship_id is None

    def test_game_event_data_update(self, session, match, ship):
        """Тест обновления данных события"""
        event = GameEvent(
            match_id=match.id,
            event_type="move",
            ship_id=ship.id,
            data={"x": 100, "y": 100}
        )
        session.add(event)
        session.commit()

        # Обновляем данные
        new_data = {"x": 200, "y": 200}
        event.data = new_data
        session.commit()

        # Проверяем, что данные обновились
        updated_event = session.query(GameEvent).filter_by(id=event.id).first()
        assert updated_event.data == new_data 