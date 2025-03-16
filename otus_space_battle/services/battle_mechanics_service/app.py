from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import math
from sqlalchemy.orm import Session
from common.database import get_db
from common.monitoring import setup_monitoring, log_function_call, get_metrics
from .models import ShipDB

# Настраиваем мониторинг
setup_monitoring(app, "battle_mechanics", metrics_port=8001)
metrics = get_metrics("battle_mechanics")

# Константы для игровой механики
FIELD_MIN_SIZE = 50
FIELD_MAX_SIZE = 100
COLLISION_DISTANCE = 1.0  # минимальное расстояние между объектами
TORPEDO_SPEED = 10.0  # скорость торпеды в единицах в секунду
TORPEDO_MAX_DISTANCE = 100.0  # максимальная дистанция полета торпеды

app = FastAPI(title="Battle Mechanics Service")

class Position(BaseModel):
    x: float
    y: float

class Direction(BaseModel):
    angle: float  # в радианах

class Ship(BaseModel):
    id: str
    position: Position
    direction: Direction
    speed: float
    rotation_speed: float
    fuel: float
    torpedoes: int

class MovementCommand(BaseModel):
    ship_id: str
    duration: float  # время движения в секундах

class RotationCommand(BaseModel):
    ship_id: str
    direction: str  # "clockwise" или "counterclockwise"
    duration: float

class FireCommand(BaseModel):
    ship_id: str
    target_position: Position

def calculate_distance(pos1: Position, pos2: Position) -> float:
    """Рассчитывает расстояние между двумя точками"""
    return math.sqrt((pos2.x - pos1.x) ** 2 + (pos2.y - pos1.y) ** 2)

def normalize_angle(angle: float) -> float:
    """Нормализует угол в диапазоне [0, 2π]"""
    return angle % (2 * math.pi)

def is_position_valid(pos: Position) -> bool:
    """Проверяет, находится ли позиция в пределах игрового поля"""
    return (0 <= pos.x <= FIELD_MAX_SIZE and 
            0 <= pos.y <= FIELD_MAX_SIZE)

def get_ship_from_db(db: Session, ship_id: str) -> Ship:
    """Получает корабль из базы данных"""
    db_ship = db.query(ShipDB).filter(ShipDB.id == ship_id).first()
    if not db_ship:
        raise HTTPException(status_code=404, detail=f"Ship {ship_id} not found")
    
    return Ship(
        id=db_ship.id,
        position=Position(x=db_ship.position_x, y=db_ship.position_y),
        direction=Direction(angle=db_ship.direction_angle),
        speed=db_ship.speed,
        rotation_speed=db_ship.rotation_speed,
        fuel=0,  # Эти данные получаем из resource_management_service
        torpedoes=0  # Эти данные получаем из resource_management_service
    )

def update_ship_in_db(db: Session, ship: Ship) -> None:
    """Обновляет позицию и направление корабля в базе данных"""
    db_ship = db.query(ShipDB).filter(ShipDB.id == ship.id).first()
    if not db_ship:
        raise HTTPException(status_code=404, detail=f"Ship {ship.id} not found")
    
    db_ship.position_x = ship.position.x
    db_ship.position_y = ship.position.y
    db_ship.direction_angle = ship.direction.angle
    db.commit()

@app.post("/movement/calculate")
@log_function_call
async def calculate_movement(command: MovementCommand, db: Session = Depends(get_db)) -> Position:
    """Рассчитывает новую позицию корабля после движения"""
    try:
        ship = get_ship_from_db(db, command.ship_id)
        
        # Рассчитываем новую позицию
        new_x = ship.position.x + ship.speed * command.duration * math.cos(ship.direction.angle)
        new_y = ship.position.y + ship.speed * command.duration * math.sin(ship.direction.angle)
        new_position = Position(x=new_x, y=new_y)
        
        # Проверяем, не выходит ли корабль за пределы поля
        if not is_position_valid(new_position):
            metrics.movement_count.labels(result="failure").inc()
            raise HTTPException(
                status_code=400,
                detail="Movement would place ship outside the game field"
            )
        
        # Обновляем позицию в базе данных
        ship.position = new_position
        update_ship_in_db(db, ship)
        
        metrics.movement_count.labels(result="success").inc()
        return new_position
    except Exception as e:
        metrics.movement_count.labels(result="failure").inc()
        raise

@app.post("/rotation/calculate")
@log_function_call
async def calculate_rotation(command: RotationCommand, db: Session = Depends(get_db)) -> Direction:
    """Рассчитывает новое направление корабля после поворота"""
    try:
        ship = get_ship_from_db(db, command.ship_id)
        
        # Рассчитываем изменение угла
        angle_change = ship.rotation_speed * command.duration
        if command.direction == "counterclockwise":
            angle_change = -angle_change
        
        # Рассчитываем новый угол и нормализуем его
        new_angle = normalize_angle(ship.direction.angle + angle_change)
        
        # Обновляем направление в базе данных
        ship.direction.angle = new_angle
        update_ship_in_db(db, ship)
        
        metrics.rotation_count.labels(result="success").inc()
        return Direction(angle=new_angle)
    except Exception as e:
        metrics.rotation_count.labels(result="failure").inc()
        raise

@app.post("/fire/calculate")
@log_function_call
async def calculate_fire(command: FireCommand, db: Session = Depends(get_db)) -> bool:
    """Рассчитывает попадание торпеды"""
    try:
        ship = get_ship_from_db(db, command.ship_id)
        
        # Проверяем дистанцию до цели
        distance = calculate_distance(ship.position, command.target_position)
        result = distance <= TORPEDO_MAX_DISTANCE
        
        metrics.fire_count.labels(result="success" if result else "miss").inc()
        return result
    except Exception as e:
        metrics.fire_count.labels(result="failure").inc()
        raise

@app.post("/collision/check")
@log_function_call
async def check_collision(positions: List[Position]) -> bool:
    """Проверяет наличие коллизий между объектами"""
    try:
        if len(positions) < 2:
            metrics.collision_count.labels(result="no_collision").inc()
            return False
        
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                if calculate_distance(positions[i], positions[j]) < COLLISION_DISTANCE:
                    metrics.collision_count.labels(result="collision").inc()
                    return True
        
        metrics.collision_count.labels(result="no_collision").inc()
        return False
    except Exception as e:
        metrics.collision_count.labels(result="error").inc()
        raise 