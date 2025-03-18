from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import analytics, events
from .database import engine, Base

# Создаем таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Analytics Service",
    description="Сервис для сбора и анализа данных о кораблях и битвах",
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

# Подключаем маршруты
app.include_router(analytics.router)
app.include_router(events.router)

@app.get("/")
async def root():
    return {"message": "Analytics Service API"} 