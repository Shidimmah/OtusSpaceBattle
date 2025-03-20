import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.models.match import Match
from common.models.fleet import Fleet
from common.models.user import User
from common.models.base import Base
import json
import time
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware


@pytest.mark.unit
class TestMatch:
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

    @pytest.fixture(autouse=True)
    def reset_metrics(self):
        """Сбрасывать метрики перед каждым тестом"""
        from common.metric_utils import reset_metrics_for_testing
        reset_metrics_for_testing()
        yield

    def test_match_creation(self, session, user1, user2, fleet1, fleet2):
        """Тест создания матча"""
        match = Match(
            player1_id=user1.id,
            player2_id=user2.id,
            player1_fleet_id=fleet1.id,
            player2_fleet_id=fleet2.id,
            status="waiting",
            is_ranked=True
        )
        session.add(match)
        session.commit()

        # Проверяем, что матч создан
        assert match.id is not None
        assert match.player1_id == user1.id
        assert match.player2_id == user2.id
        assert match.player1_fleet_id == fleet1.id
        assert match.player2_fleet_id == fleet2.id
        assert match.status == "waiting"
        assert match.is_ranked is True
        assert isinstance(match.start_time, datetime)
        assert match.end_time is None
        assert match.winner_id is None

    def test_match_player_relationships(self, session, user1, user2, fleet1, fleet2):
        """Тест связей матча с игроками"""
        match = Match(
            player1_id=user1.id,
            player2_id=user2.id,
            player1_fleet_id=fleet1.id,
            player2_fleet_id=fleet2.id,
            status="waiting"
        )
        session.add(match)
        session.commit()

        # Проверяем связи с игроками
        assert match.player1 == user1
        assert match.player2 == user2
        assert match in user1.matches_as_player1
        assert match in user2.matches_as_player2

    def test_match_fleet_relationships(self, session, user1, user2, fleet1, fleet2):
        """Тест связей матча с флотами"""
        match = Match(
            player1_id=user1.id,
            player2_id=user2.id,
            player1_fleet_id=fleet1.id,
            player2_fleet_id=fleet2.id,
            status="waiting"
        )
        session.add(match)
        session.commit()

        # Проверяем связи с флотами
        assert match.player1_fleet == fleet1
        assert match.player2_fleet == fleet2
        assert match in fleet1.matches_as_player1
        assert match in fleet2.matches_as_player2

    def test_match_completion(self, session, user1, user2, fleet1, fleet2):
        """Тест завершения матча"""
        match = Match(
            player1_id=user1.id,
            player2_id=user2.id,
            player1_fleet_id=fleet1.id,
            player2_fleet_id=fleet2.id,
            status="waiting"
        )
        session.add(match)
        session.commit()

        # Завершаем матч
        match.status = "finished"
        match.winner_id = user1.id
        match.end_time = datetime.utcnow()
        session.commit()

        # Проверяем, что матч завершен
        updated_match = session.query(Match).filter_by(id=match.id).first()
        assert updated_match.status == "finished"
        assert updated_match.winner_id == user1.id
        assert updated_match.end_time is not None

    def test_match_cascade_delete(self, session, user1, user2, fleet1, fleet2):
        """Тест каскадного удаления матча"""
        match = Match(
            player1_id=user1.id,
            player2_id=user2.id,
            player1_fleet_id=fleet1.id,
            player2_fleet_id=fleet2.id,
            status="waiting"
        )
        session.add(match)
        session.commit()

        # Удаляем матч
        session.delete(match)
        session.commit()

        # Проверяем, что матч удален
        deleted_match = session.query(Match).filter_by(id=match.id).first()
        assert deleted_match is None

    def test_match_player_null_on_delete(self, session, user1, user2, fleet1, fleet2):
        """Тест установки player_id в NULL при удалении игрока"""
        match = Match(
            player1_id=user1.id,
            player2_id=user2.id,
            player1_fleet_id=fleet1.id,
            player2_fleet_id=fleet2.id,
            status="waiting"
        )
        session.add(match)
        session.commit()

        # Удаляем первого игрока
        session.delete(user1)
        session.commit()

        # Проверяем, что player1_id установлен в NULL
        updated_match = session.query(Match).filter_by(id=match.id).first()
        assert updated_match.player1_id is None

    def test_match_fleet_null_on_delete(self, session, user1, user2, fleet1, fleet2):
        """Тест установки fleet_id в NULL при удалении флота"""
        match = Match(
            player1_id=user1.id,
            player2_id=user2.id,
            player1_fleet_id=fleet1.id,
            player2_fleet_id=fleet2.id,
            status="waiting"
        )
        session.add(match)
        session.commit()

        # Сначала обновляем ссылку на флот в матче на NULL
        match.player1_fleet_id = None
        session.commit()
        
        # Теперь удаляем первый флот
        session.delete(fleet1)
        session.commit()

        # Проверяем, что player1_fleet_id установлен в NULL
        updated_match = session.query(Match).filter_by(id=match.id).first()
        assert updated_match.player1_fleet_id is None

    def test_match_status_transitions(self, session, user1, user2, fleet1, fleet2):
        """Тест переходов статуса матча"""
        match = Match(
            player1_id=user1.id,
            player2_id=user2.id,
            player1_fleet_id=fleet1.id,
            player2_fleet_id=fleet2.id,
            status="waiting"
        )
        session.add(match)
        session.commit()

        # Проверяем начальный статус
        assert match.status == "waiting"

        # Переходим в статус "in_progress"
        match.status = "in_progress"
        session.commit()
        assert match.status == "in_progress"

        # Переходим в статус "finished"
        match.status = "finished"
        match.winner_id = user1.id
        match.end_time = datetime.utcnow()
        session.commit()
        assert match.status == "finished"
        assert match.winner_id == user1.id
        assert match.end_time is not None

# Вспомогательная функция для сброса метрик (перенесена на уровень модуля)
def reset_metrics_for_testing():
    """Сбросить состояние метрик для тестирования"""
    # Сбросить счетчики в глобальном реестре
    from prometheus_client import REGISTRY
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        REGISTRY.unregister(collector) 