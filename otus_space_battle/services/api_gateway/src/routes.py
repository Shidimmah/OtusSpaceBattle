from fastapi import APIRouter, Depends, HTTPException
from typing import List
import httpx
from .models import Ship, GameState, GameCommand, PlayerStats, GameEvent
from .config import settings
from .dependencies import verify_api_key, get_current_game, get_current_player

# Создаем роутеры для разных групп эндпоинтов
game_router = APIRouter(prefix="/game", tags=["game"])
player_router = APIRouter(prefix="/player", tags=["player"])
analytics_router = APIRouter(prefix="/analytics", tags=["analytics"])

# Игровые эндпоинты
@game_router.post("/create")
async def create_game(players: List[str], api_key: str = Depends(verify_api_key)) -> GameState:
    """Создание новой игры"""
    async with httpx.AsyncClient() as client:
        # Инициализация кораблей через battle_mechanics
        ships_response = await client.post(
            f"{settings.BATTLE_MECHANICS_URL}/ships/initialize",
            json={"player_ids": players}
        )
        ships_response.raise_for_status()
        
        # Инициализация ресурсов через resource_management
        resources_response = await client.post(
            f"{settings.RESOURCE_MANAGEMENT_URL}/resources/initialize",
            json={"ships": ships_response.json()}
        )
        resources_response.raise_for_status()
        
        return GameState(**ships_response.json())

@game_router.post("/{game_id}/command")
async def execute_command(
    game_id: str,
    command: GameCommand,
    game: dict = Depends(get_current_game),
    api_key: str = Depends(verify_api_key)
) -> GameState:
    """Выполнение игровой команды"""
    async with httpx.AsyncClient() as client:
        if command.command_type == "move":
            response = await client.post(
                f"{settings.BATTLE_MECHANICS_URL}/movement/calculate",
                json=command.parameters
            )
        elif command.command_type == "rotate":
            response = await client.post(
                f"{settings.BATTLE_MECHANICS_URL}/rotation/calculate",
                json=command.parameters
            )
        elif command.command_type == "fire":
            response = await client.post(
                f"{settings.BATTLE_MECHANICS_URL}/fire/calculate",
                json=command.parameters
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid command type")
        
        response.raise_for_status()
        return GameState(**response.json())

@game_router.get("/{game_id}/state")
async def get_game_state(
    game_id: str,
    game: dict = Depends(get_current_game),
    api_key: str = Depends(verify_api_key)
) -> GameState:
    """Получение текущего состояния игры"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.BATTLE_MECHANICS_URL}/game/{game_id}/state")
        response.raise_for_status()
        return GameState(**response.json())

# Эндпоинты для игроков
@player_router.get("/{player_id}/stats")
async def get_player_stats(
    player_id: str,
    player: dict = Depends(get_current_player),
    api_key: str = Depends(verify_api_key)
) -> PlayerStats:
    """Получение статистики игрока"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.RANKING_URL}/player/{player_id}")
        response.raise_for_status()
        return PlayerStats(**response.json())

@player_router.get("/leaderboard")
async def get_leaderboard(
    limit: int = 10,
    api_key: str = Depends(verify_api_key)
) -> List[PlayerStats]:
    """Получение таблицы лидеров"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.RANKING_URL}/ranking/leaderboard?limit={limit}")
        response.raise_for_status()
        return [PlayerStats(**player) for player in response.json()]

# Аналитические эндпоинты
@analytics_router.get("/game/{game_id}/events")
async def get_game_events(
    game_id: str,
    game: dict = Depends(get_current_game),
    api_key: str = Depends(verify_api_key)
) -> List[GameEvent]:
    """Получение событий игры"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.ANALYTICS_URL}/analytics/events/{game_id}")
        response.raise_for_status()
        return [GameEvent(**event) for event in response.json()]

@analytics_router.get("/game/{game_id}/stats")
async def get_game_stats(
    game_id: str,
    game: dict = Depends(get_current_game),
    api_key: str = Depends(verify_api_key)
):
    """Получение статистики игры"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.ANALYTICS_URL}/analytics/game/{game_id}")
        response.raise_for_status()
        return response.json() 