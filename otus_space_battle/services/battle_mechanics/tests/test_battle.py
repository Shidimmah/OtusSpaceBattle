import pytest
from fastapi.testclient import TestClient
from otus_space_battle.services.battle_mechanics.src.app import app
from otus_space_battle.services.battle_mechanics.src.models import Ship, Position, GameState

client = TestClient(app)

@pytest.fixture
def test_token():
    return "test-token"

@pytest.fixture
def test_ship():
    return {
        "id": "ship1",
        "type": "fighter",
        "position": {"x": 0, "y": 0},
        "health": 100,
        "shield": 50,
        "weapons": ["laser", "missile"]
    }

@pytest.fixture
def test_game_state():
    return {
        "game_id": "game1",
        "ships": [
            {
                "id": "ship1",
                "type": "fighter",
                "position": {"x": 0, "y": 0},
                "health": 100,
                "shield": 50
            },
            {
                "id": "ship2",
                "type": "bomber",
                "position": {"x": 10, "y": 10},
                "health": 150,
                "shield": 75
            }
        ]
    }

def test_create_game(test_token):
    response = client.post(
        "/game/create",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "game_id" in data
    assert "ships" in data

def test_get_game_state(test_token, test_game_state):
    response = client.get(
        f"/game/{test_game_state['game_id']}/state",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["game_id"] == test_game_state["game_id"]
    assert len(data["ships"]) == len(test_game_state["ships"])

def test_move_ship(test_token, test_game_state):
    ship_id = test_game_state["ships"][0]["id"]
    command = {
        "ship_id": ship_id,
        "command_type": "move",
        "parameters": {
            "x": 5,
            "y": 5
        }
    }
    response = client.post(
        f"/game/{test_game_state['game_id']}/command",
        json=command,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ship_id"] == ship_id
    assert data["position"]["x"] == 5
    assert data["position"]["y"] == 5

def test_attack_ship(test_token, test_game_state):
    attacker_id = test_game_state["ships"][0]["id"]
    target_id = test_game_state["ships"][1]["id"]
    command = {
        "ship_id": attacker_id,
        "command_type": "attack",
        "parameters": {
            "target_id": target_id,
            "weapon": "laser"
        }
    }
    response = client.post(
        f"/game/{test_game_state['game_id']}/command",
        json=command,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["attacker_id"] == attacker_id
    assert data["target_id"] == target_id
    assert "damage" in data

def test_invalid_command(test_token, test_game_state):
    command = {
        "ship_id": "invalid_ship",
        "command_type": "invalid_command",
        "parameters": {}
    }
    response = client.post(
        f"/game/{test_game_state['game_id']}/command",
        json=command,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 400

def test_ship_destruction(test_token, test_game_state):
    ship_id = test_game_state["ships"][0]["id"]
    command = {
        "ship_id": ship_id,
        "command_type": "attack",
        "parameters": {
            "target_id": ship_id,
            "weapon": "laser",
            "damage": 1000
        }
    }
    response = client.post(
        f"/game/{test_game_state['game_id']}/command",
        json=command,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ship_id"] == ship_id
    assert data["status"] == "destroyed" 