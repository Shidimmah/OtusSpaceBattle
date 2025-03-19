import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.models.base import Base
from common.models.match import Match
from common.models.user import User
from common.models.fleet import Fleet

@pytest.mark.unit
class TestMatch:
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
    def user1(self, session):
        """Создаем первого игрока"""
        user = User(username="player1", email="player1@example.com")
        session.add(user)
        session.commit()
        return user
    
    @pytest.fixture
    def user2(self, session):
        """Создаем второго игрока"""
        user = User(username="player2", email="player2@example.com")
        session.add(user)
        session.commit()
        return user
    
    @pytest.fixture
    def fleet1(self, session, user1):
        """Создаем флот для первого игрока"""
        fleet = Fleet(user_id=user1.id, name="Fleet 1")
        session.add(fleet)
        session.commit()
        return fleet
    
    @pytest.fixture
    def fleet2(self, session, user2):
        """Создаем флот для второго игрока"""
        fleet = Fleet(user_id=user2.id, name="Fleet 2")
        session.add(fleet)
        session.commit()
        return fleet
    
    def test_match_creation(self, session, user1):
        """Тест создания матча"""
        match = Match(
            player1_id=user1.id,
            status="waiting",
            is_ranked=True
        )
        session.add(match)
        session.commit()
        
        # Проверяем, что матч создан
        assert match.id is not None
        assert match.player1_id == user1.id
        assert match.player2_id is None
        assert match.status == "waiting"
        assert match.is_ranked is True
        assert isinstance(match.start_time, datetime)
        assert match.end_time is None
        assert match.winner_id is None
    
    def test_match_with_players(self, session, user1, user2, fleet1, fleet2):
        """Тест матча с двумя игроками"""
        match = Match(
            player1_id=user1.id,
            player2_id=user2.id,
            player1_fleet_id=fleet1.id,
            player2_fleet_id=fleet2.id,
            status="in_progress"
        )
        session.add(match)
        session.commit()
        
        # Проверяем связи
        assert match.player1 == user1
        assert match.player2 == user2
        assert match.player1_fleet == fleet1
        assert match.player2_fleet == fleet2
    
    def test_match_completion(self, session, user1, user2):
        """Тест завершения матча"""
        match = Match(
            player1_id=user1.id,
            player2_id=user2.id,
            status="in_progress"
        )
        session.add(match)
        session.commit()
        
        # Завершаем матч
        match.status = "finished"
        match.end_time = datetime.utcnow()
        match.winner_id = user1.id
        session.commit()
        
        # Проверяем результат
        assert match.status == "finished"
        assert match.end_time is not None
        assert match.winner_id == user1.id
    
    def test_match_cascade_delete(self, session, user1, user2):
        """Тест каскадного удаления матча при удалении игрока"""
        match = Match(
            player1_id=user1.id,
            player2_id=user2.id,
            status="in_progress"
        )
        session.add(match)
        session.commit()
        
        # Удаляем первого игрока
        session.delete(user1)
        session.commit()
        
        # Проверяем, что матч удален
        assert session.query(Match).filter_by(id=match.id).first() is None
    
    def test_match_fleet_null_on_delete(self, session, user1, user2, fleet1, fleet2):
        """Тест установки fleet_id в NULL при удалении флота"""
        match = Match(
            player1_id=user1.id,
            player2_id=user2.id,
            player1_fleet_id=fleet1.id,
            player2_fleet_id=fleet2.id,
            status="in_progress"
        )
        session.add(match)
        session.commit()
        
        # Удаляем флоты
        session.delete(fleet1)
        session.delete(fleet2)
        session.commit()
        
        # Проверяем, что fleet_id установлены в NULL
        match = session.query(Match).filter_by(id=match.id).first()
        assert match.player1_fleet_id is None
        assert match.player2_fleet_id is None 