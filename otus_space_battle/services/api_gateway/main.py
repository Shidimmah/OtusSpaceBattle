from fastapi import FastAPI, Depends
import httpx

app = FastAPI(title="Cosmic Battle API Gateway")

AUTH_SERVICE_URL = "http://auth_service:8001"
MATCHMAKING_SERVICE_URL = "http://matchmaking_service:8002"
GAME_SERVER_URL = "http://game_server:8003"

@app.get("/")
async def root():
    return {"message": "Welcome to Cosmic Battle API Gateway"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/register")
async def register_user(username: str, password: str, email: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/register", json={"username": username, "password": password, "email": email})
    return response.json()

@app.post("/login")
async def login_user(username: str, password: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/login", json={"username": username, "password": password})
    return response.json()

@app.post("/create_game")
async def create_game():
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{MATCHMAKING_SERVICE_URL}/create_game")
    return response.json()

@app.post("/join_game")
async def join_game(game_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{MATCHMAKING_SERVICE_URL}/join_game", json={"game_id": game_id})
    return response.json()
