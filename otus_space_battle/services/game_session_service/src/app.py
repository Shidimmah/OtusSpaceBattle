from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import json
import uvicorn

from common.models.match import Match
from common.models.user import User
from common.models.fleet import Fleet
from common.models.ship import Ship
from common.models.game_event import GameEvent
from common.utils.database import get_session

app = FastAPI(title="Game Session Service")

# Хранилище активных WebSocket соединений
# match_id -> {player_id -> WebSocket}
active_connections: Dict[int, Dict[int, WebSocket]] = {}

class GameState(BaseModel):
    match_id: int
    ships: Dict[int, dict]  # ship_id -> ship_state
    status: str
    current_turn: int
    turn_deadline: Optional[datetime]

# Хранилище состояний игр
game_states: Dict[int, GameState] = {}

class ShipState(BaseModel):
    id: int
    position_x: float
    position_y: float
    rotation: float  # в градусах
    fuel: float
    torpedoes: int
    is_destroyed: bool = False

class GameCommand(BaseModel):
    command_type: str  # move, rotate, fire, self_destruct
    ship_id: int
    params: dict

@app.websocket("/ws/game/{match_id}/{player_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    match_id: int,
    player_id: int,
    session: AsyncSession = Depends(get_session)
):
    # Получаем информацию о матче
    match = await session.get(Match, match_id)
    if not match:
        await websocket.close(code=4004, reason="Match not found")
        return
    
    # Проверяем, что игрок участвует в матче
    if player_id not in [match.player1_id, match.player2_id]:
        await websocket.close(code=4003, reason="Player not in match")
        return
    
    await websocket.accept()
    
    # Добавляем соединение в хранилище
    if match_id not in active_connections:
        active_connections[match_id] = {}
    active_connections[match_id][player_id] = websocket
    
    try:
        # Если это первое подключение к матчу, инициализируем состояние игры
        if match_id not in game_states:
            game_state = await initialize_game_state(match_id, session)
            game_states[match_id] = game_state
        
        # Отправляем текущее состояние игры
        await websocket.send_json(game_states[match_id].dict())
        
        # Основной цикл обработки сообщений
        while True:
            data = await websocket.receive_text()
            command = GameCommand.parse_raw(data)
            
            # Проверяем валидность команды
            if not await validate_command(command, player_id, match_id, session):
                await websocket.send_json({
                    "error": "Invalid command",
                    "command": command.dict()
                })
                continue
            
            # Применяем команду и получаем обновленное состояние
            new_state = await apply_command(command, match_id, player_id, session)
            
            # Отправляем обновленное состояние всем игрокам
            await broadcast_state(match_id, new_state)
            
    except WebSocketDisconnect:
        # Удаляем соединение при отключении
        del active_connections[match_id][player_id]
        if not active_connections[match_id]:
            del active_connections[match_id]

async def initialize_game_state(match_id: int, session: AsyncSession) -> GameState:
    match = await session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Получаем корабли обоих игроков
    ships_query = select(Ship).where(
        Ship.fleet_id.in_([match.player1_fleet_id, match.player2_fleet_id])
    )
    result = await session.execute(ships_query)
    ships = result.scalars().all()
    
    # Инициализируем состояние кораблей
    ships_state = {}
    for ship in ships:
        # Определяем начальную позицию в зависимости от того, какому игроку принадлежит корабль
        is_player1_ship = ship.fleet_id == match.player1_fleet_id
        
        ships_state[ship.id] = ShipState(
            id=ship.id,
            # Игрок 1 начинает в верхнем левом углу, Игрок 2 - в правом нижнем
            position_x=10 if is_player1_ship else 90,
            position_y=10 if is_player1_ship else 90,
            rotation=45 if is_player1_ship else 225,  # Корабли смотрят друг на друга
            fuel=ship.ship_type.base_fuel_capacity,
            torpedoes=ship.ship_type.base_torpedo_capacity
        )
    
    return GameState(
        match_id=match_id,
        ships=ships_state,
        status="in_progress",
        current_turn=1,
        turn_deadline=datetime.utcnow()  # TODO: добавить реальный таймер хода
    )

async def validate_command(
    command: GameCommand,
    player_id: int,
    match_id: int,
    session: AsyncSession
) -> bool:
    # Получаем информацию о корабле
    ship = await session.get(Ship, command.ship_id)
    if not ship:
        return False
    
    # Проверяем, что корабль принадлежит игроку
    fleet = await session.get(Fleet, ship.fleet_id)
    if not fleet or fleet.user_id != player_id:
        return False
    
    # Проверяем состояние корабля
    ship_state = game_states[match_id].ships.get(command.ship_id)
    if not ship_state or ship_state.is_destroyed:
        return False
    
    # Проверяем специфичные для команды условия
    if command.command_type == "move":
        return ship_state.fuel > 0
    elif command.command_type == "rotate":
        return ship_state.fuel > 0
    elif command.command_type == "fire":
        return ship_state.torpedoes > 0
    elif command.command_type == "self_destruct":
        return True
    
    return False

async def apply_command(
    command: GameCommand,
    match_id: int,
    player_id: int,
    session: AsyncSession
) -> GameState:
    game_state = game_states[match_id]
    ship_state = game_state.ships[command.ship_id]
    
    # Получаем информацию о корабле и его типе
    ship = await session.get(Ship, command.ship_id)
    
    # Применяем команду
    if command.command_type == "move":
        distance = command.params.get("distance", 0)
        # Уменьшаем топливо
        fuel_consumption = ship.ship_type.fuel_consumption_move * distance
        ship_state.fuel -= fuel_consumption
        # Обновляем позицию
        # TODO: добавить реальные расчеты движения
        
    elif command.command_type == "rotate":
        angle = command.params.get("angle", 0)
        # Уменьшаем топливо
        fuel_consumption = ship.ship_type.fuel_consumption_rotate * abs(angle)
        ship_state.fuel -= fuel_consumption
        # Обновляем поворот
        ship_state.rotation = (ship_state.rotation + angle) % 360
        
    elif command.command_type == "fire":
        # Уменьшаем количество торпед
        ship_state.torpedoes -= 1
        # TODO: добавить реальные расчеты попадания
        
    elif command.command_type == "self_destruct":
        ship_state.is_destroyed = True
    
    # Создаем запись о событии
    event = GameEvent(
        match_id=match_id,
        event_type=command.command_type,
        ship_id=command.ship_id,
        event_data=json.dumps(command.params)
    )
    session.add(event)
    await session.commit()
    
    # Проверяем условия окончания игры
    await check_game_end(match_id, session)
    
    return game_state

async def broadcast_state(match_id: int, state: GameState):
    if match_id in active_connections:
        for websocket in active_connections[match_id].values():
            await websocket.send_json(state.dict())

async def check_game_end(match_id: int, session: AsyncSession):
    game_state = game_states[match_id]
    match = await session.get(Match, match_id)
    
    # Группируем корабли по флотам
    fleet1_ships = {}
    fleet2_ships = {}
    
    for ship_id, ship_state in game_state.ships.items():
        ship = await session.get(Ship, ship_id)
        if ship.fleet_id == match.player1_fleet_id:
            fleet1_ships[ship_id] = ship_state
        else:
            fleet2_ships[ship_id] = ship_state
    
    # Проверяем условия победы
    fleet1_destroyed = all(ship.is_destroyed for ship in fleet1_ships.values())
    fleet2_destroyed = all(ship.is_destroyed for ship in fleet2_ships.values())
    
    if fleet1_destroyed and fleet2_destroyed:
        # Ничья
        game_state.status = "draw"
        match.status = "finished"
        match.end_time = datetime.utcnow()
    elif fleet1_destroyed:
        # Победил второй игрок
        game_state.status = "finished"
        match.status = "finished"
        match.winner_id = match.player2_id
        match.end_time = datetime.utcnow()
    elif fleet2_destroyed:
        # Победил первый игрок
        game_state.status = "finished"
        match.status = "finished"
        match.winner_id = match.player1_id
        match.end_time = datetime.utcnow()
    
    await session.commit()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 