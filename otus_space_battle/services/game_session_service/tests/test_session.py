import pytest
from fastapi.testclient import TestClient
from otus_space_battle.services.game_session_service.src.app import app
from otus_space_battle.services.game_session_service.src.models import GameSession, Player

client = TestClient(app)

@pytest.fixture
def test_token():
    return "test-token"

@pytest.fixture
def test_player():
    return {
        "id": "player1",
        "username": "testuser",
        "fleet": {
            "ships": [
                {
                    "id": "ship1",
                    "type": "fighter",
                    "health": 100
                }
            ]
        }
    }

@pytest.fixture
def test_session():
    return {
        "id": "session1",
        "players": ["player1", "player2"],
        "status": "active",
        "created_at": "2024-03-20T10:00:00"
    }

def test_create_session(test_token, test_player):
    response = client.post(
        "/sessions/create",
        json={"player": test_player},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["status"] == "created"

def test_join_session(test_token, test_session):
    player_id = "player3"
    response = client.post(
        f"/sessions/{test_session['id']}/join",
        json={"player_id": player_id},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert player_id in data["players"]
    assert data["status"] == "active"

def test_get_session(test_token, test_session):
    response = client.get(
        f"/sessions/{test_session['id']}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_session["id"]
    assert data["status"] == test_session["status"]

def test_update_session_state(test_token, test_session):
    new_state = {
        "status": "in_progress",
        "current_turn": 1
    }
    response = client.put(
        f"/sessions/{test_session['id']}/state",
        json=new_state,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == new_state["status"]
    assert data["current_turn"] == new_state["current_turn"]

def test_end_session(test_token, test_session):
    response = client.post(
        f"/sessions/{test_session['id']}/end",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ended"
    assert "ended_at" in data

def test_invalid_session_id(test_token):
    response = client.get(
        "/sessions/invalid_id",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 404

def test_session_already_ended(test_token, test_session):
    # Сначала завершаем сессию
    client.post(
        f"/sessions/{test_session['id']}/end",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    # Пытаемся присоединиться к завершенной сессии
    response = client.post(
        f"/sessions/{test_session['id']}/join",
        json={"player_id": "player3"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 400 