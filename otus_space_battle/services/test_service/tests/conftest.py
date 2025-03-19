import pytest
import os
import httpx

# URL-адреса сервисов
API_GATEWAY_URL = os.environ.get("API_GATEWAY_URL", "http://api_gateway:8000")
AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://auth_service:8000")
BATTLE_MECHANICS_URL = os.environ.get("BATTLE_MECHANICS_URL", "http://battle_mechanics:8000")
MATCHMAKING_URL = os.environ.get("MATCHMAKING_URL", "http://matchmaking:8000")
RANKING_URL = os.environ.get("RANKING_URL", "http://ranking:8000")
RESOURCE_MANAGEMENT_URL = os.environ.get("RESOURCE_MANAGEMENT_URL", "http://resource_management:8000")
ANALYTICS_URL = os.environ.get("ANALYTICS_URL", "http://analytics:8000")

@pytest.fixture
def api_client():
    """HTTP клиент для тестирования API"""
    with httpx.Client(timeout=10.0) as client:
        yield client

@pytest.fixture
async def async_api_client():
    """Асинхронный HTTP клиент для тестирования API"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        yield client

@pytest.fixture
def api_gateway_url():
    """URL API Gateway"""
    return API_GATEWAY_URL

@pytest.fixture
def auth_service_url():
    """URL сервиса авторизации"""
    return AUTH_SERVICE_URL

@pytest.fixture
def battle_mechanics_url():
    """URL сервиса боевой механики"""
    return BATTLE_MECHANICS_URL

@pytest.fixture
def matchmaking_url():
    """URL сервиса подбора игроков"""
    return MATCHMAKING_URL

@pytest.fixture
def ranking_url():
    """URL сервиса рейтинга"""
    return RANKING_URL

@pytest.fixture
def resource_management_url():
    """URL сервиса управления ресурсами"""
    return RESOURCE_MANAGEMENT_URL

@pytest.fixture
def analytics_url():
    """URL сервиса аналитики"""
    return ANALYTICS_URL 