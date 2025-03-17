from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import ships

app = FastAPI(
    title="Battle Mechanics Service",
    description="Сервис боевой механики",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(ships.router, prefix="/ships", tags=["ships"]) 