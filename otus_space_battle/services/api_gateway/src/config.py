from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Базовые URL сервисов
    BATTLE_MECHANICS_URL: str = "http://localhost:8001"
    RESOURCE_MANAGEMENT_URL: str = "http://localhost:8002"
    RANKING_URL: str = "http://localhost:8003"
    ANALYTICS_URL: str = "http://localhost:8004"
    
    # Настройки API Gateway
    API_GATEWAY_HOST: str = "0.0.0.0"
    API_GATEWAY_PORT: int = 8000
    
    # Настройки безопасности
    API_KEY_HEADER: str = "X-API-Key"
    SECRET_KEY: str = "your-secret-key-here"
    
    class Config:
        env_file = ".env"

settings = Settings() 