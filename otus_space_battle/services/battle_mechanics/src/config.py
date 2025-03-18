from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Настройки приложения
    resource_management_url: str = "http://resource_management:8000"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    # Получить настройки приложения
    return Settings() 