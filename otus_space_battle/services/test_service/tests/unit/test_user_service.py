import pytest
import httpx

@pytest.mark.unit
class TestUserService:
    
    @pytest.mark.asyncio
    async def test_create_user(self, user_service_url):
        """Тест создания пользователя"""
        # Подготовка тестовых данных
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на создание пользователя
            response = await client.post(
                f"{user_service_url}/users",
                json=user_data
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert "user_id" in data
            assert data["username"] == user_data["username"]
            assert data["email"] == user_data["email"]
    
    @pytest.mark.asyncio
    async def test_get_user_profile(self, user_service_url):
        """Тест получения профиля пользователя"""
        # Подготовка тестовых данных
        user_id = "testuser123"
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на получение профиля
            response = await client.get(
                f"{user_service_url}/users/{user_id}/profile"
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert "username" in data
            assert "email" in data
            assert "rating" in data
            assert "created_at" in data
    
    @pytest.mark.asyncio
    async def test_update_user_profile(self, user_service_url):
        """Тест обновления профиля пользователя"""
        # Подготовка тестовых данных
        user_id = "testuser123"
        update_data = {
            "username": "newusername",
            "email": "newemail@example.com"
        }
        
        # Создаем клиент для теста
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Отправка запроса на обновление профиля
            response = await client.put(
                f"{user_service_url}/users/{user_id}/profile",
                json=update_data
            )
            
            # Проверка результата
            assert response.status_code == 200
            data = response.json()
            assert data["username"] == update_data["username"]
            assert data["email"] == update_data["email"] 