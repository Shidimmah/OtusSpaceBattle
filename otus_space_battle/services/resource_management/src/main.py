from fastapi import FastAPI
from dependency_injector.wiring import inject, Provide

from .di.container import Container
from .di.config import get_settings
from .routes import ships

def create_app() -> FastAPI:
    # Создание приложения FastAPI
    app = FastAPI(
        title="Resource Management Service",
        description="Сервис управления игровыми ресурсами",
        version="1.0.0"
    )
    
    # Создаем контейнер зависимостей
    container = Container()
    container.config.from_pydantic(get_settings())
    container.wire(packages=[".routes"])
    
    # Регистрируем роуты
    app.include_router(ships.router, prefix="/ships", tags=["ships"])
    
    return app

app = create_app() 