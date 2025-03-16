import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from services.analytics_service.app import app, process_event, get_player_stats, get_game_stats

client = TestClient(app)

@pytest.fixture
def test_game_id():
    return "test_game_123"

@pytest.fixture
def test_player_id():
    return "test_player_123"

@pytest.fixture
def test_event():
    return {
        "event_type": "battle_start",
        "game_id": "test_game_123",
        "player_id": "test_player_123",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "position": {"x": 50.0, "y": 50.0},
            "direction": 0.0,
            "health": 100
        }
    }

@pytest.mark.asyncio
async def test_process_event(test_event, test_db):
    """Тест обработки игрового события"""
    response = await client.post("/events", json=test_event)
    assert response.status_code == 200
    data = response.json()
    
    assert "event_id" in data
    assert "processed_at" in data

@pytest.mark.asyncio
async def test_get_player_stats(test_player_id, test_db):
    """Тест получения статистики игрока"""
    response = await client.get(f"/stats/player/{test_player_id}")
    assert response.status_code == 200
    data = response.json()
    
    assert "total_games" in data
    assert "total_wins" in data
    assert "total_losses" in data
    assert "average_game_duration" in data
    assert "total_shots_fired" in data
    assert "accuracy" in data

@pytest.mark.asyncio
async def test_get_game_stats(test_game_id, test_db):
    """Тест получения статистики игры"""
    response = await client.get(f"/stats/game/{test_game_id}")
    assert response.status_code == 200
    data = response.json()
    
    assert "game_duration" in data
    assert "players" in data
    assert "events" in data
    assert "winner" in data

@pytest.mark.asyncio
async def test_process_multiple_events(test_db):
    """Тест обработки нескольких событий"""
    events = [
        {
            "event_type": "battle_start",
            "game_id": "test_game_123",
            "player_id": "player1",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {"position": {"x": 0, "y": 0}}
        },
        {
            "event_type": "movement",
            "game_id": "test_game_123",
            "player_id": "player1",
            "timestamp": (datetime.utcnow() + timedelta(seconds=1)).isoformat(),
            "data": {"position": {"x": 10, "y": 10}}
        },
        {
            "event_type": "battle_end",
            "game_id": "test_game_123",
            "player_id": "player1",
            "timestamp": (datetime.utcnow() + timedelta(seconds=2)).isoformat(),
            "data": {"winner": "player1"}
        }
    ]
    
    for event in events:
        response = await client.post("/events", json=event)
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_invalid_event_type(test_db):
    """Тест обработки события с неверным типом"""
    event = {
        "event_type": "invalid_event",
        "game_id": "test_game_123",
        "player_id": "test_player_123",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {}
    }
    
    response = await client.post("/events", json=event)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_missing_required_fields(test_db):
    """Тест обработки события с отсутствующими обязательными полями"""
    event = {
        "event_type": "battle_start",
        # Отсутствует game_id
        "player_id": "test_player_123",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    response = await client.post("/events", json=event)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_invalid_timestamp(test_db):
    """Тест обработки события с неверным форматом времени"""
    event = {
        "event_type": "battle_start",
        "game_id": "test_game_123",
        "player_id": "test_player_123",
        "timestamp": "invalid_timestamp",
        "data": {}
    }
    
    response = await client.post("/events", json=event)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_stats_aggregation(test_db):
    """Тест агрегации статистики"""
    # Создаем серию событий для тестирования агрегации
    game_id = "test_game_456"
    player_id = "test_player_456"
    
    events = [
        {
            "event_type": "battle_start",
            "game_id": game_id,
            "player_id": player_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {"position": {"x": 0, "y": 0}}
        },
        {
            "event_type": "shot_fired",
            "game_id": game_id,
            "player_id": player_id,
            "timestamp": (datetime.utcnow() + timedelta(seconds=1)).isoformat(),
            "data": {"hit": True}
        },
        {
            "event_type": "shot_fired",
            "game_id": game_id,
            "player_id": player_id,
            "timestamp": (datetime.utcnow() + timedelta(seconds=2)).isoformat(),
            "data": {"hit": False}
        },
        {
            "event_type": "battle_end",
            "game_id": game_id,
            "player_id": player_id,
            "timestamp": (datetime.utcnow() + timedelta(seconds=3)).isoformat(),
            "data": {"winner": player_id}
        }
    ]
    
    # Отправляем события
    for event in events:
        response = await client.post("/events", json=event)
        assert response.status_code == 200
    
    # Проверяем статистику игрока
    response = await client.get(f"/stats/player/{player_id}")
    assert response.status_code == 200
    player_stats = response.json()
    
    assert player_stats["total_games"] >= 1
    assert player_stats["total_wins"] >= 1
    assert player_stats["total_shots_fired"] >= 2
    assert 0 <= player_stats["accuracy"] <= 1.0
    
    # Проверяем статистику игры
    response = await client.get(f"/stats/game/{game_id}")
    assert response.status_code == 200
    game_stats = response.json()
    
    assert game_stats["winner"] == player_id
    assert len(game_stats["events"]) >= 4 