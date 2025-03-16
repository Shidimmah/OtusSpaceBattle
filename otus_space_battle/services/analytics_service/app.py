from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict

app = FastAPI(title="Analytics Service")

# Временные хранилища для демонстрации. В реальности будет использоваться БД
game_events: Dict[str, List[GameEvent]] = defaultdict(list)
game_statistics: Dict[str, GameStats] = {}
player_statistics: Dict[str, PlayerStats] = {}

class GameEvent(BaseModel):
    game_id: str
    player_id: str
    event_type: str
    event_data: Dict
    timestamp: datetime

class GameStats(BaseModel):
    game_id: str
    duration: float
    shots_fired: int
    hits: int
    fuel_used: float
    winner_id: Optional[str]
    is_draw: bool

class PlayerStats(BaseModel):
    player_id: str
    total_games: int
    total_wins: int
    total_losses: int
    total_draws: int
    average_game_duration: float
    accuracy: float  # hits / shots_fired

@app.post("/analytics/event")
async def log_game_event(event: GameEvent):
    """Логирует игровое событие"""
    # Добавляем событие в список событий игры
    game_events[event.game_id].append(event)
    
    # Обновляем статистику игрока, если это необходимо
    if event.player_id not in player_statistics:
        player_statistics[event.player_id] = PlayerStats(
            player_id=event.player_id,
            total_games=0,
            total_wins=0,
            total_losses=0,
            total_draws=0,
            average_game_duration=0,
            accuracy=0
        )

@app.post("/analytics/game-stats")
async def save_game_stats(stats: GameStats):
    """Сохраняет статистику игры"""
    game_statistics[stats.game_id] = stats
    
    # Обновляем статистику игроков
    events = game_events.get(stats.game_id, [])
    player_shots = defaultdict(lambda: {"shots": 0, "hits": 0})
    
    # Собираем статистику по выстрелам
    for event in events:
        if event.event_type == "shot":
            player_shots[event.player_id]["shots"] += 1
        elif event.event_type == "hit":
            player_shots[event.player_id]["hits"] += 1
    
    # Обновляем статистику для каждого игрока
    for player_id, shots_data in player_shots.items():
        if player_id not in player_statistics:
            continue
        
        player_stats = player_statistics[player_id]
        player_stats.total_games += 1
        
        if stats.winner_id == player_id:
            player_stats.total_wins += 1
        elif stats.is_draw:
            player_stats.total_draws += 1
        else:
            player_stats.total_losses += 1
        
        # Обновляем среднюю длительность игры
        player_stats.average_game_duration = (
            (player_stats.average_game_duration * (player_stats.total_games - 1) + stats.duration)
            / player_stats.total_games
        )
        
        # Обновляем точность
        if shots_data["shots"] > 0:
            player_stats.accuracy = shots_data["hits"] / shots_data["shots"]

@app.get("/analytics/player/{player_id}")
async def get_player_stats(player_id: str) -> PlayerStats:
    """Получает статистику игрока"""
    if player_id not in player_statistics:
        raise HTTPException(
            status_code=404,
            detail=f"Player {player_id} not found"
        )
    return player_statistics[player_id]

@app.get("/analytics/game/{game_id}")
async def get_game_stats(game_id: str) -> GameStats:
    """Получает статистику конкретной игры"""
    if game_id not in game_statistics:
        raise HTTPException(
            status_code=404,
            detail=f"Game {game_id} not found"
        )
    return game_statistics[game_id]

@app.get("/analytics/events/{game_id}")
async def get_game_events(game_id: str) -> List[GameEvent]:
    """Получает все события игры"""
    if game_id not in game_events:
        raise HTTPException(
            status_code=404,
            detail=f"Game {game_id} not found"
        )
    return sorted(game_events[game_id], key=lambda x: x.timestamp) 