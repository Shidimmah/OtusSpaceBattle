import pytest
from fastapi.testclient import TestClient
from ..src.app import app
from ..src.models import Resource, ResourceType

client = TestClient(app)

@pytest.fixture
def test_token():
    return "test-token"

@pytest.fixture
def test_resources():
    return {
        "metal": 1000,
        "crystal": 500,
        "deuterium": 200
    }

def test_get_resources(test_token):
    response = client.get("/resources", headers={"Authorization": f"Bearer {test_token}"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert all(key in data for key in ["metal", "crystal", "deuterium"])

def test_update_resources(test_token, test_resources):
    response = client.put(
        "/resources",
        json=test_resources,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data == test_resources

def test_add_resources(test_token, test_resources):
    response = client.post(
        "/resources/add",
        json=test_resources,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert all(data[key] >= test_resources[key] for key in test_resources)

def test_consume_resources(test_token, test_resources):
    response = client.post(
        "/resources/consume",
        json=test_resources,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert all(data[key] <= test_resources[key] for key in test_resources)

def test_insufficient_resources(test_token):
    large_resources = {
        "metal": 1000000,
        "crystal": 1000000,
        "deuterium": 1000000
    }
    response = client.post(
        "/resources/consume",
        json=large_resources,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 400

def test_invalid_resource_type(test_token):
    invalid_resources = {
        "invalid_resource": 100
    }
    response = client.put(
        "/resources",
        json=invalid_resources,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 422 