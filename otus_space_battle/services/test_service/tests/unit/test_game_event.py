import pytest
from datetime import datetime
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.models.base import Base
from common.models.game_event import GameEvent
from common.models.match import Match
from common.models.ship import Ship

@pytest.mark.unit
class TestGameEvent:
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
    def match(self, session):
        """Создаем тестовый матч"""
        match = Match(
            player1_id=1,
            player2_id=2,
            status="in_progress"
        )
        session.add(match)
        session.commit()
        return match
    
    @pytest.fixture
    def ship(self, session):
        """Создаем тестовый корабль"""
        ship = Ship(
            fleet_id=1,
            name="Test Ship",
            position_x=100,
            position_y=100,
            rotation=0,
            health=100,
            fuel=100,
            torpedoes=10
        )
        session.add(ship)
        session.commit()
        return ship
    
    def test_game_event_creation(self, session, match, ship):
        """Тест создания игрового события"""
        event_data = {
            "direction": {"x": 10, "y": 0},
            "speed": 5
        }
        
        event = GameEvent(
            match_id=match.id,
            event_type="move",
            ship_id=ship.id,
            event_data=json.dumps(event_data)
        )
        session.add(event)
        session.commit()
        
        # Проверяем, что событие создано
        assert event.id is not None
        assert event.match_id == match.id
        assert event.event_type == "move"
        assert event.ship_id == ship.id
        assert event.event_data == json.dumps(event_data)
        assert isinstance(event.timestamp, datetime)
    
    def test_game_event_with_target(self, session, match, ship):
        """Тест создания события с целевым кораблем"""
        target_ship = Ship(
            fleet_id=2,
            name="Target Ship",
            position_x=200,
            position_y=200,
            rotation=0,
            health=100,
            fuel=100,
            torpedoes=10
        )
        session.add(target_ship)
        session.commit()
        
        event_data = {
            "damage": 50,
            "distance": 150
        }
        
        event = GameEvent(
            match_id=match.id,
            event_type="hit",
            ship_id=ship.id,
            target_ship_id=target_ship.id,
            event_data=json.dumps(event_data)
        )
        session.add(event)
        session.commit()
        
        # Проверяем связи
        assert event.target_ship_id == target_ship.id
        assert event.target_ship == target_ship
    
    def test_game_event_cascade_delete(self, session, match, ship):
        """Тест каскадного удаления события при удалении матча"""
        event = GameEvent(
            match_id=match.id,
            event_type="move",
            ship_id=ship.id,
            event_data=json.dumps({"direction": {"x": 10, "y": 0}})
        )
        session.add(event)
        session.commit()
        
        # Удаляем матч
        session.delete(match)
        session.commit()
        
        # Проверяем, что событие тоже удалено
        assert session.query(GameEvent).filter_by(id=event.id).first() is None
    
    def test_game_event_ship_null_on_delete(self, session, match, ship):
        """Тест установки ship_id в NULL при удалении корабля"""
        event = GameEvent(
            match_id=match.id,
            event_type="move",
            ship_id=ship.id,
            event_data=json.dumps({"direction": {"x": 10, "y": 0}})
        )
        session.add(event)
        session.commit()
        
        # Удаляем корабль
        session.delete(ship)
        session.commit()
        
        # Проверяем, что ship_id установлен в NULL
        event = session.query(GameEvent).filter_by(id=event.id).first()
        assert event.ship_id is None 