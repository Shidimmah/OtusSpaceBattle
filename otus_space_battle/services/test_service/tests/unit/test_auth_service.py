import pytest
import httpx

@pytest.mark.unit
class TestAuthService:
    
    @pytest.mark.asyncio
    async def test_register_user(self, async_api_client, auth_service_url):
        """Тест регистрации пользователя"""
        # Подготовка тестовых данных
        test_user = {
            "username": "test_user",
            "email": "test@example.com",
            "password": "testPassword123"
        }
        
        # Отправка запроса на регистрацию
        response = await async_api_client.post(
            f"{auth_service_url}/auth/register",
            json=test_user
        )
        
        # Проверка результата
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["username"] == test_user["username"]
        assert data["email"] == test_user["email"]
        assert "password" not in data  # Пароль не должен возвращаться
    
    @pytest.mark.asyncio
    async def test_login_user(self, async_api_client, auth_service_url):
        """Тест авторизации пользователя"""
        # Подготовка тестовых данных
        test_user = {
            "username": "test_user",
            "email": "test@example.com",
            "password": "testPassword123"
        }
        
        # Сначала регистрируем пользователя
        await async_api_client.post(
            f"{auth_service_url}/auth/register",
            json=test_user
        )
        
        # Отправка запроса на авторизацию
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        response = await async_api_client.post(
            f"{auth_service_url}/auth/login",
            json=login_data
        )
        
        # Проверка результата
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_invalid_login(self, async_api_client, auth_service_url):
        """Тест неудачной авторизации"""
        # Подготовка тестовых данных
        login_data = {
            "username": "nonexistent_user",
            "password": "wrongPassword123"
        }
        
        # Отправка запроса на авторизацию
        response = await async_api_client.post(
            f"{auth_service_url}/auth/login",
            json=login_data
        )
        
        # Проверка результата
        assert response.status_code == 401  # Unauthorized 