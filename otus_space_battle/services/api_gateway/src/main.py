from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI(
    title="Space Battle API Gateway",
    description="API Gateway для игры Space Battle",
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

# URL сервисов
RESOURCE_MANAGEMENT_URL = os.getenv("RESOURCE_MANAGEMENT_URL", "http://resource_management:8000")
BATTLE_MECHANICS_URL = os.getenv("BATTLE_MECHANICS_URL", "http://battle_mechanics:8000")
RANKING_URL = os.getenv("RANKING_URL", "http://ranking:8000")
ANALYTICS_URL = os.getenv("ANALYTICS_URL", "http://analytics:8000")

@app.api_route("/ships/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_ships(request: Request, path: str):
    """Проксирование запросов к сервису управления ресурсами"""
    client = httpx.AsyncClient()
    url = f"{RESOURCE_MANAGEMENT_URL}/ships/{path}"
    
    # Копируем заголовки запроса
    headers = dict(request.headers)
    headers.pop("host", None)
    
    # Получаем тело запроса
    body = await request.body()
    
    # Выполняем запрос к сервису
    response = await client.request(
        method=request.method,
        url=url,
        headers=headers,
        content=body
    )
    
    await client.aclose()
    return response.json()

@app.api_route("/battles/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_battles(request: Request, path: str):
    """Проксирование запросов к сервису боевой механики"""
    client = httpx.AsyncClient()
    url = f"{BATTLE_MECHANICS_URL}/battles/{path}"
    
    headers = dict(request.headers)
    headers.pop("host", None)
    
    body = await request.body()
    
    response = await client.request(
        method=request.method,
        url=url,
        headers=headers,
        content=body
    )
    
    await client.aclose()
    return response.json()

@app.api_route("/ranking/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_ranking(request: Request, path: str):
    """Проксирование запросов к сервису рейтинга"""
    client = httpx.AsyncClient()
    url = f"{RANKING_URL}/ranking/{path}"
    
    headers = dict(request.headers)
    headers.pop("host", None)
    
    body = await request.body()
    
    response = await client.request(
        method=request.method,
        url=url,
        headers=headers,
        content=body
    )
    
    await client.aclose()
    return response.json()

@app.api_route("/analytics/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_analytics(request: Request, path: str):
    """Проксирование запросов к сервису аналитики"""
    client = httpx.AsyncClient()
    url = f"{ANALYTICS_URL}/analytics/{path}"
    
    headers = dict(request.headers)
    headers.pop("host", None)
    
    body = await request.body()
    
    response = await client.request(
        method=request.method,
        url=url,
        headers=headers,
        content=body
    )
    
    await client.aclose()
    return response.json() 