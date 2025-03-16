import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import math
from services.battle_mechanics_service.app import (
    app,
    Position,
    Direction,
    Ship,
    MovementCommand,
    RotationCommand,
    FireCommand,
    calculate_distance,
    normalize_angle,
    is_position_valid,
    FIELD_MAX_SIZE,
    COLLISION_DISTANCE,
    TORPEDO_MAX_DISTANCE
)

client = TestClient(app)

@pytest.fixture
def test_ship():
    """Фикстура для тестового корабля"""
    return Ship(
        id="test_ship",
        position=Position(x=50.0, y=50.0),
        direction=Direction(angle=0.0),
        speed=10.0,
        rotation_speed=math.pi/4,  # 45 градусов в секунду
        fuel=100.0,
        torpedoes=10
    )

def test_calculate_distance():
    """Тест расчета расстояния между точками"""
    pos1 = Position(x=0.0, y=0.0)
    pos2 = Position(x=3.0, y=4.0)
    assert calculate_distance(pos1, pos2) == 5.0

def test_normalize_angle():
    """Тест нормализации угла"""
    assert normalize_angle(0.0) == 0.0
    assert normalize_angle(2 * math.pi) == 0.0
    assert normalize_angle(4 * math.pi) == 0.0
    assert normalize_angle(-math.pi) == math.pi
    assert abs(normalize_angle(3 * math.pi) - math.pi) < 1e-10

def test_is_position_valid():
    """Тест проверки валидности позиции"""
    assert is_position_valid(Position(x=0.0, y=0.0)) == True
    assert is_position_valid(Position(x=FIELD_MAX_SIZE, y=FIELD_MAX_SIZE)) == True
    assert is_position_valid(Position(x=-1.0, y=0.0)) == False
    assert is_position_valid(Position(x=0.0, y=FIELD_MAX_SIZE + 1)) == False

@pytest.mark.asyncio
async def test_calculate_movement(test_ship):
    """Тест расчета движения"""
    command = MovementCommand(ship_id=test_ship.id, duration=1.0)
    
    # Движение вправо (угол 0)
    response = await client.post("/movement/calculate", json=command.dict())
    assert response.status_code == 200
    new_position = Position(**response.json())
    assert new_position.x == pytest.approx(60.0)  # 50 + 10 * 1.0 * cos(0)
    assert new_position.y == pytest.approx(50.0)  # 50 + 10 * 1.0 * sin(0)
    
    # Тест выхода за пределы поля
    test_ship.position.x = FIELD_MAX_SIZE - 5
    command.duration = 1.0
    response = await client.post("/movement/calculate", json=command.dict())
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_calculate_rotation(test_ship):
    """Тест расчета поворота"""
    # Поворот по часовой стрелке
    command = RotationCommand(
        ship_id=test_ship.id,
        direction="clockwise",
        duration=1.0
    )
    response = await client.post("/rotation/calculate", json=command.dict())
    assert response.status_code == 200
    new_direction = Direction(**response.json())
    assert new_direction.angle == pytest.approx(math.pi/4)
    
    # Поворот против часовой стрелки
    command.direction = "counterclockwise"
    response = await client.post("/rotation/calculate", json=command.dict())
    assert response.status_code == 200
    new_direction = Direction(**response.json())
    assert new_direction.angle == pytest.approx(0.0)

@pytest.mark.asyncio
async def test_calculate_fire(test_ship):
    """Тест расчета выстрела"""
    # Выстрел в пределах дальности
    command = FireCommand(
        ship_id=test_ship.id,
        target_position=Position(x=60.0, y=50.0)  # 10 единиц от корабля
    )
    response = await client.post("/fire/calculate", json=command.dict())
    assert response.status_code == 200
    assert response.json() == True
    
    # Выстрел за пределами дальности
    command.target_position = Position(
        x=50.0 + TORPEDO_MAX_DISTANCE + 10,
        y=50.0
    )
    response = await client.post("/fire/calculate", json=command.dict())
    assert response.status_code == 200
    assert response.json() == False

@pytest.mark.asyncio
async def test_check_collision():
    """Тест проверки коллизий"""
    # Нет коллизии
    positions = [
        Position(x=0.0, y=0.0),
        Position(x=10.0, y=10.0)
    ]
    response = await client.post("/collision/check", json=[p.dict() for p in positions])
    assert response.status_code == 200
    assert response.json() == False
    
    # Есть коллизия
    positions = [
        Position(x=0.0, y=0.0),
        Position(x=0.5, y=0.5)  # Расстояние меньше COLLISION_DISTANCE
    ]
    response = await client.post("/collision/check", json=[p.dict() for p in positions])
    assert response.status_code == 200
    assert response.json() == True
    
    # Пустой список позиций
    response = await client.post("/collision/check", json=[])
    assert response.status_code == 200
    assert response.json() == False

def test_edge_cases():
    """Тест граничных случаев"""
    # Тест расчета расстояния для совпадающих точек
    pos = Position(x=0.0, y=0.0)
    assert calculate_distance(pos, pos) == 0.0
    
    # Тест нормализации нулевого угла
    assert normalize_angle(0.0) == 0.0
    
    # Тест позиции на границе поля
    assert is_position_valid(Position(x=FIELD_MAX_SIZE, y=FIELD_MAX_SIZE)) == True
    assert is_position_valid(Position(x=FIELD_MAX_SIZE + 0.1, y=FIELD_MAX_SIZE)) == False 