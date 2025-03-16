import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from ..src.app import app
from ..src.models import GameState, Ship, Position, Direction

client = TestClient(app)

@pytest.fixture
def api_key():
    return "test-api-key"

@pytest.fixture
def game_id():
    return "test-game-id"

@pytest.fixture
def player_id():
    return "test-player-id"

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_game(api_key):
    players = ["player1", "player2"]
    response = client.post(
        "/game/create",
        json=players,
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    game_state = GameState(**response.json())
    assert len(game_state.ships) == len(players)

def test_execute_command(api_key, game_id):
    command = {
        "game_id": game_id,
        "ship_id": "ship1",
        "command_type": "move",
        "parameters": {
            "duration": 1.0
        }
    }
    response = client.post(
        f"/game/{game_id}/command",
        json=command,
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200

def test_get_game_state(api_key, game_id):
    response = client.get(
        f"/game/{game_id}/state",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    game_state = GameState(**response.json())
    assert game_state.game_id == game_id

def test_get_player_stats(api_key, player_id):
    response = client.get(
        f"/player/{player_id}/stats",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    stats = response.json()
    assert stats["player_id"] == player_id

def test_get_leaderboard(api_key):
    response = client.get(
        "/player/leaderboard",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    leaderboard = response.json()
    assert isinstance(leaderboard, list)

def test_get_game_events(api_key, game_id):
    response = client.get(
        f"/analytics/game/{game_id}/events",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    events = response.json()
    assert isinstance(events, list)

def test_get_game_stats(api_key, game_id):
    response = client.get(
        f"/analytics/game/{game_id}/stats",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    stats = response.json()
    assert isinstance(stats, dict) 