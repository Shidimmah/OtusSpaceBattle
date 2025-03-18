import pytest
from fastapi.testclient import TestClient
from ..src.app import app
from ..src.models import GameEvent, AnalyticsData

client = TestClient(app)

@pytest.fixture
def test_token():
    return "test-token"

@pytest.fixture
def test_game_id():
    return "game1"

@pytest.fixture
def test_event():
    return {
        "game_id": "game1",
        "event_type": "battle",
        "timestamp": "2024-03-20T10:00:00",
        "data": {
            "attacker_id": "ship1",
            "target_id": "ship2",
            "damage": 50
        }
    }

def test_record_event(test_token, test_event):
    response = client.post(
        "/events/record",
        json=test_event,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "recorded"

def test_get_game_events(test_token, test_game_id):
    response = client.get(
        f"/events/game/{test_game_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_player_stats(test_token):
    player_id = "player1"
    response = client.get(
        f"/stats/player/{player_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "player_id" in data
    assert "battles" in data
    assert "wins" in data
    assert "losses" in data

def test_get_game_stats(test_token, test_game_id):
    response = client.get(
        f"/stats/game/{test_game_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "game_id" in data
    assert "duration" in data
    assert "total_damage" in data
    assert "ships_destroyed" in data

def test_get_leaderboard(test_token):
    response = client.get(
        "/stats/leaderboard",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "player_id" in data[0]
        assert "score" in data[0]

def test_invalid_event_data(test_token):
    invalid_event = {
        "game_id": "game1",
        "event_type": "invalid_type",
        "timestamp": "invalid_timestamp",
        "data": {}
    }
    response = client.post(
        "/events/record",
        json=invalid_event,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 422

def test_get_time_range_stats(test_token, test_game_id):
    response = client.get(
        f"/stats/game/{test_game_id}/time_range",
        params={
            "start_time": "2024-03-20T10:00:00",
            "end_time": "2024-03-20T11:00:00"
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "start_time" in data
    assert "end_time" in data
    assert "events" in data 