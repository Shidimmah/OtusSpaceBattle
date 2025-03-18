from fastapi import Header, HTTPException
from typing import Optional
from .config import settings

async def verify_api_key(api_key: Optional[str] = Header(None)):
    # Проверка API ключа
    if api_key is None:
        raise HTTPException(status_code=401, detail="API Key is missing")
    # Здесь должна быть реальная проверка API ключа
    return api_key

async def get_current_game(game_id: str):
    # Получение текущей игры
    # Здесь должна быть логика получения игры
    return {"game_id": game_id}

async def get_current_player(player_id: str):
    # Получение текущего игрока
    # Здесь должна быть логика получения игрока
    return {"player_id": player_id} 