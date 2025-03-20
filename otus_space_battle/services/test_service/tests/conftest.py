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
FLEET_SERVICE_URL = os.environ.get("FLEET_SERVICE_URL", "http://fleet_service:8000")
MATCH_SERVICE_URL = os.environ.get("MATCH_SERVICE_URL", "http://match_service:8000")
GAME_EVENT_SERVICE_URL = os.environ.get("GAME_EVENT_SERVICE_URL", "http://game_event_service:8000")
RATING_SERVICE_URL = os.environ.get("RATING_SERVICE_URL", "http://rating_service:8000")
RESOURCE_SERVICE_URL = os.environ.get("RESOURCE_SERVICE_URL", "http://resource_service:8000")
ANALYTICS_SERVICE_URL = os.environ.get("ANALYTICS_SERVICE_URL", "http://analytics_service:8000")

@pytest.fixture
def api_client():
    """HTTP клиент для тестирования API"""
    with httpx.Client(timeout=10.0) as client:
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

@pytest.fixture
def fleet_service_url():
    """URL сервиса флота"""
    return FLEET_SERVICE_URL

@pytest.fixture
def match_service_url():
    """URL сервиса матчей"""
    return MATCH_SERVICE_URL

@pytest.fixture
def game_event_service_url():
    """URL сервиса игровых событий"""
    return GAME_EVENT_SERVICE_URL

@pytest.fixture
def rating_service_url():
    """URL сервиса рейтинга"""
    return RATING_SERVICE_URL

@pytest.fixture
def resource_service_url():
    """URL сервиса ресурсов"""
    return RESOURCE_SERVICE_URL

@pytest.fixture
def analytics_service_url():
    """URL сервиса аналитики"""
    return ANALYTICS_SERVICE_URL 