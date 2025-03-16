from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Настройки базы данных
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@database:5432/space_battle"
    
    # Настройки сервиса
    SERVICE_NAME: str = "game_session_service"
    SERVICE_PORT: int = 8004
    
    # Настройки игры
    GAME_FIELD_SIZE: int = 100  # размер игрового поля (100x100)
    TURN_TIME_LIMIT: int = 30  # время на ход в секундах
    MAX_FUEL_CONSUMPTION_PER_TURN: float = 10.0  # максимальный расход топлива за ход
    MAX_ROTATION_PER_TURN: float = 90.0  # максимальный угол поворота за ход
    MAX_MOVE_DISTANCE_PER_TURN: float = 10.0  # максимальное расстояние движения за ход
    TORPEDO_SPEED: float = 20.0  # скорость торпеды
    TORPEDO_DAMAGE_RADIUS: float = 2.0  # радиус поражения торпеды
    
    class Config:
        env_file = ".env"

settings = Settings() 