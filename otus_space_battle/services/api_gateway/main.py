from fastapi import FastAPI
import httpx

app = FastAPI(title="Otus Space Battle API Gateway", docs_url="/docs", openapi_url="/openapi.json")

# URL других сервисов внутри Docker-сети
AUTH_SERVICE_URL = "http://auth_service:8001"
MATCHMAKING_SERVICE_URL = "http://matchmaking_service:8002"
GAME_SERVER_URL = "http://game_server:8003"

@app.get("/health")
async def health_check():
    """Проверка состояния API Gateway"""
    return {"status": "ok"}

@app.post("/register")
async def register_user(username: str, password: str, email: str):
    """Регистрация пользователя через Auth Service"""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/register", json={"username": username, "password": password, "email": email})
    return response.json()

@app.post("/auth/login")
async def login_user(username: str, password: str):
    """Авторизация пользователя через Auth Service"""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/auth/login", json={"username": username, "password": password})
    return response.json()

@app.post("/create_game")
async def create_game():
    """Создание новой игровой сессии через Matchmaking Service"""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{MATCHMAKING_SERVICE_URL}/create_game")
    return response.json()

@app.post("/join_game")
async def join_game(game_id: str):
    """Присоединение к существующей игре через Matchmaking Service"""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{MATCHMAKING_SERVICE_URL}/join_game", json={"game_id": game_id})
    return response.json()

# Запуск API Gateway через Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
