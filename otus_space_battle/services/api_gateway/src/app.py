from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routes import game_router, player_router, analytics_router
from .config import settings
from common.monitoring import setup_monitoring

app = FastAPI(
    title="Space Battle API Gateway",
    description="API Gateway для игры Space Battle",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    swagger_ui_parameters={
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "filter": True,
    }
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене нужно указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка мониторинга
setup_monitoring(app, "api_gateway", metrics_port=8000)

# Подключаем роутеры
app.include_router(game_router)
app.include_router(player_router)
app.include_router(analytics_router)

@app.get("/health")
async def health_check():
    """Эндпоинт для проверки здоровья сервиса"""
    return {"status": "healthy"} 