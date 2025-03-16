import asyncio
from common.models import Base, ShipType
from common.utils.database import engine, async_session

# Начальные типы кораблей
initial_ship_types = [
    {
        "name": "Scout",
        "description": "Легкий и быстрый разведывательный корабль",
        "base_fuel_capacity": 100,
        "base_torpedo_capacity": 3,
        "base_movement_speed": 2.0,
        "base_rotation_speed": 90.0,  # градусов в секунду
        "fuel_consumption_move": 0.5,
        "fuel_consumption_rotate": 0.2
    },
    {
        "name": "Destroyer",
        "description": "Средний боевой корабль с хорошим балансом характеристик",
        "base_fuel_capacity": 150,
        "base_torpedo_capacity": 5,
        "base_movement_speed": 1.5,
        "base_rotation_speed": 60.0,
        "fuel_consumption_move": 0.7,
        "fuel_consumption_rotate": 0.3
    },
    {
        "name": "Battleship",
        "description": "Тяжелый боевой корабль с большим запасом топлива и торпед",
        "base_fuel_capacity": 200,
        "base_torpedo_capacity": 7,
        "base_movement_speed": 1.0,
        "base_rotation_speed": 45.0,
        "fuel_consumption_move": 1.0,
        "fuel_consumption_rotate": 0.4
    }
]

async def init_db():
    async with engine.begin() as conn:
        # Удаляем существующие таблицы
        await conn.run_sync(Base.metadata.drop_all)
        # Создаем новые таблицы
        await conn.run_sync(Base.metadata.create_all)
    
    # Создаем начальные типы кораблей
    async with async_session() as session:
        for ship_type_data in initial_ship_types:
            ship_type = ShipType(**ship_type_data)
            session.add(ship_type)
        await session.commit()

if __name__ == "__main__":
    asyncio.run(init_db())
