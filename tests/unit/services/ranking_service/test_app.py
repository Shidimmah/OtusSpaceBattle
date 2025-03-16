import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from services.ranking_service.app import app, update_rating, get_leaderboard

client = TestClient(app)

@pytest.fixture
def test_player_id():
    return "test_player_123"

@pytest.mark.asyncio
async def test_get_player_rating(test_player_id, test_db):
    """Тест получения рейтинга игрока"""
    response = await client.get(f"/rating/{test_player_id}")
    assert response.status_code == 200
    data = response.json()
    
    assert "rating" in data
    assert "games_played" in data
    assert "wins" in data
    assert "losses" in data
    assert isinstance(data["rating"], int)

@pytest.mark.asyncio
async def test_update_rating_win(test_player_id, test_db):
    """Тест обновления рейтинга при победе"""
    update_data = {
        "result": "win",
        "opponent_rating": 1000
    }
    
    response = await client.post(
        f"/rating/{test_player_id}/update",
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["rating_change"] > 0
    assert "new_rating" in data

@pytest.mark.asyncio
async def test_update_rating_loss(test_player_id, test_db):
    """Тест обновления рейтинга при поражении"""
    update_data = {
        "result": "loss",
        "opponent_rating": 1000
    }
    
    response = await client.post(
        f"/rating/{test_player_id}/update",
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["rating_change"] < 0
    assert "new_rating" in data

@pytest.mark.asyncio
async def test_update_rating_draw(test_player_id, test_db):
    """Тест обновления рейтинга при ничьей"""
    update_data = {
        "result": "draw",
        "opponent_rating": 1000
    }
    
    response = await client.post(
        f"/rating/{test_player_id}/update",
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "rating_change" in data
    assert "new_rating" in data

@pytest.mark.asyncio
async def test_get_leaderboard(test_db):
    """Тест получения таблицы лидеров"""
    response = await client.get("/leaderboard")
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    if len(data) > 0:
        player = data[0]
        assert "player_id" in player
        assert "rating" in player
        assert "rank" in player
        assert "wins" in player
        assert "losses" in player

@pytest.mark.asyncio
async def test_get_leaderboard_with_limit(test_db):
    """Тест получения таблицы лидеров с лимитом"""
    limit = 5
    response = await client.get(f"/leaderboard?limit={limit}")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) <= limit

@pytest.mark.asyncio
async def test_invalid_result_type(test_player_id):
    """Тест обновления рейтинга с неверным типом результата"""
    update_data = {
        "result": "invalid_result",
        "opponent_rating": 1000
    }
    
    response = await client.post(
        f"/rating/{test_player_id}/update",
        json=update_data
    )
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_invalid_opponent_rating(test_player_id):
    """Тест обновления рейтинга с неверным рейтингом оппонента"""
    update_data = {
        "result": "win",
        "opponent_rating": -100  # Отрицательный рейтинг
    }
    
    response = await client.post(
        f"/rating/{test_player_id}/update",
        json=update_data
    )
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_rating_boundaries(test_player_id, test_db):
    """Тест граничных значений рейтинга"""
    # Тест нижней границы рейтинга
    for _ in range(100):  # Много поражений подряд
        update_data = {
            "result": "loss",
            "opponent_rating": 3000
        }
        response = await client.post(
            f"/rating/{test_player_id}/update",
            json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["new_rating"] >= 0  # Рейтинг не должен стать отрицательным 