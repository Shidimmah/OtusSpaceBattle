from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Настройки приложения
    
    # Database
    database_url: str = "sqlite:///./space_battle.db"
    
    # Logging
    log_level: str = "INFO"
    log_file: str | None = "logs/resource_management.log"
    
    # Elasticsearch
    elasticsearch_host: str = "localhost"
    elasticsearch_port: int = 9200
    elasticsearch_index: str = "resource-management-logs"
    
    class Config:
        env_file = ".env"

def get_settings() -> Settings:
    # Получить настройки приложения
    return Settings() 