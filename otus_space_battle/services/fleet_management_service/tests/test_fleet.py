import pytest
from fastapi.testclient import TestClient
from ..src.app import app
from ..src.models import Fleet, Ship, Formation

client = TestClient(app)

@pytest.fixture
def test_token():
    return "test-token"

@pytest.fixture
def test_ship():
    return {
        "id": "ship1",
        "type": "fighter",
        "health": 100,
        "shield": 50,
        "weapons": ["laser", "missile"]
    }

@pytest.fixture
def test_fleet():
    return {
        "id": "fleet1",
        "name": "Test Fleet",
        "ships": [
            {
                "id": "ship1",
                "type": "fighter",
                "health": 100
            },
            {
                "id": "ship2",
                "type": "bomber",
                "health": 150
            }
        ],
        "formation": "line"
    }

def test_create_fleet(test_token, test_ship):
    response = client.post(
        "/fleets/create",
        json={
            "name": "New Fleet",
            "ships": [test_ship]
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Fleet"
    assert len(data["ships"]) == 1

def test_get_fleet(test_token, test_fleet):
    response = client.get(
        f"/fleets/{test_fleet['id']}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_fleet["id"]
    assert data["name"] == test_fleet["name"]

def test_update_fleet_formation(test_token, test_fleet):
    new_formation = {
        "formation": "circle",
        "spacing": 2.0
    }
    response = client.put(
        f"/fleets/{test_fleet['id']}/formation",
        json=new_formation,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["formation"] == new_formation["formation"]
    assert data["spacing"] == new_formation["spacing"]

def test_add_ship_to_fleet(test_token, test_fleet, test_ship):
    response = client.post(
        f"/fleets/{test_fleet['id']}/ships",
        json={"ship": test_ship},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["ships"]) == len(test_fleet["ships"]) + 1
    assert any(s["id"] == test_ship["id"] for s in data["ships"])

def test_remove_ship_from_fleet(test_token, test_fleet):
    ship_id = test_fleet["ships"][0]["id"]
    response = client.delete(
        f"/fleets/{test_fleet['id']}/ships/{ship_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["ships"]) == len(test_fleet["ships"]) - 1
    assert not any(s["id"] == ship_id for s in data["ships"])

def test_invalid_fleet_id(test_token):
    response = client.get(
        "/fleets/invalid_id",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 404

def test_invalid_formation(test_token, test_fleet):
    invalid_formation = {
        "formation": "invalid_formation",
        "spacing": -1.0
    }
    response = client.put(
        f"/fleets/{test_fleet['id']}/formation",
        json=invalid_formation,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 422

def test_fleet_combat_power(test_token, test_fleet):
    response = client.get(
        f"/fleets/{test_fleet['id']}/combat_power",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_power" in data
    assert "offensive_power" in data
    assert "defensive_power" in data 