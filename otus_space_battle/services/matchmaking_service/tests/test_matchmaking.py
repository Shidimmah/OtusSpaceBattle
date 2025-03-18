import pytest
from fastapi.testclient import TestClient
from ..src.app import app
from ..src.models import Player, MatchRequest

client = TestClient(app)

@pytest.fixture
def test_token():
    return "test-token"

@pytest.fixture
def test_player():
    return {
        "id": "player1",
        "username": "testuser",
        "rating": 1000,
        "fleet_power": 500
    }

@pytest.fixture
def test_match_request():
    return {
        "player_id": "player1",
        "game_type": "ranked",
        "preferences": {
            "min_rating": 900,
            "max_rating": 1100,
            "max_wait_time": 300
        }
    }

def test_join_queue(test_token, test_match_request):
    response = client.post(
        "/queue/join",
        json=test_match_request,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert "queue_position" in data

def test_leave_queue(test_token, test_player):
    response = client.post(
        f"/queue/leave/{test_player['id']}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "left"

def test_get_queue_status(test_token, test_player):
    response = client.get(
        f"/queue/status/{test_player['id']}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "position" in data
    assert "estimated_wait_time" in data

def test_find_match(test_token, test_match_request):
    # Сначала добавляем игрока в очередь
    client.post(
        "/queue/join",
        json=test_match_request,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    # Затем ищем матч
    response = client.post(
        "/queue/match",
        json={"player_id": test_match_request["player_id"]},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "match_id" in data
    assert "players" in data

def test_invalid_queue_leave(test_token):
    response = client.post(
        "/queue/leave/invalid_player",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 404

def test_queue_timeout(test_token, test_match_request):
    # Добавляем игрока в очередь с коротким таймаутом
    test_match_request["preferences"]["max_wait_time"] = 1
    response = client.post(
        "/queue/join",
        json=test_match_request,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    # Ждем таймаут
    import time
    time.sleep(2)
    # Проверяем статус
    response = client.get(
        f"/queue/status/{test_match_request['player_id']}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 404

def test_rating_range_match(test_token):
    # Создаем двух игроков с разным рейтингом
    player1 = {
        "id": "player1",
        "rating": 1000,
        "preferences": {"min_rating": 900, "max_rating": 1100}
    }
    player2 = {
        "id": "player2",
        "rating": 2000,
        "preferences": {"min_rating": 1900, "max_rating": 2100}
    }
    # Добавляем их в очередь
    client.post("/queue/join", json=player1, headers={"Authorization": f"Bearer {test_token}"})
    client.post("/queue/join", json=player2, headers={"Authorization": f"Bearer {test_token}"})
    # Пытаемся найти матч
    response = client.post(
        "/queue/match",
        json={"player_id": player1["id"]},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["players"]) == 1  # Должен найти только одного игрока 