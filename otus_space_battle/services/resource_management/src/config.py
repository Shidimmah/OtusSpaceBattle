from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Настройки приложения
    # Настройки PostgreSQL
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_db: str = "space_battle"

    class Config:
        env_file = ".env"

settings = Settings() 