import math
import time
from typing import Dict, Optional
import httpx

from ..models.ships import ShipState, Vector2D, WeaponState, MoveCommand, FireCommand

class ShipService:
    # Сервис для управления кораблями в игре
    def __init__(self, resource_management_url: str):
        self.resource_management_url = resource_management_url
        self.ships: Dict[str, ShipState] = {}
        self.last_update = time.time()

    async def create_ship(self, template_id: str, player_id: str, position: Vector2D) -> ShipState:
        # Создать корабль в игре на основе шаблона
        # Получаем шаблон корабля из сервиса управления ресурсами
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.resource_management_url}/ships/templates/{template_id}")
            if response.status_code != 200:
                raise ValueError(f"Шаблон корабля {template_id} не найден")
            template = response.json()

        # Создаем состояние оружия
        weapons = [
            WeaponState(
                type=w["type"],
                damage=w["damage"],
                cooldown=w["cooldown"],
                ammunition=w["ammunition"],
                range=w["range"],
                last_shot=0.0
            )
            for w in template["weapons"]
        ]

        # Создаем состояние корабля
        ship = ShipState(
            id=f"{player_id}_{template_id}_{len(self.ships)}",
            template_id=template_id,
            player_id=player_id,
            position=position,
            velocity=Vector2D(x=0.0, y=0.0),
            rotation=0.0,
            current_speed=0.0,
            fuel=template["characteristics"]["fuel_capacity"],
            hull_strength=template["characteristics"]["hull_strength"],
            shield_strength=template["characteristics"]["shield_strength"],
            weapons=weapons
        )

        self.ships[ship.id] = ship
        return ship

    def get_ship(self, ship_id: str) -> Optional[ShipState]:
        # Получить состояние корабля
        return self.ships.get(ship_id)

    def update_ship(self, ship_id: str, command: MoveCommand) -> Optional[ShipState]:
        # Обновить состояние корабля на основе команды движения
        ship = self.ships.get(ship_id)
        if not ship:
            return None

        # Получаем время с последнего обновления
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time

        # Обновляем поворот
        ship.rotation += command.rotation * dt

        # Обновляем скорость и позицию
        if command.thrust != 0 and ship.fuel > 0:
            # Расходуем топливо
            ship.fuel = max(0.0, ship.fuel - dt)
            
            # Вычисляем вектор ускорения
            acceleration = Vector2D(
                x=math.cos(ship.rotation) * command.thrust,
                y=math.sin(ship.rotation) * command.thrust
            )
            
            # Обновляем скорость
            ship.velocity.x += acceleration.x * dt
            ship.velocity.y += acceleration.y * dt
            
            # Ограничиваем скорость
            speed = math.sqrt(ship.velocity.x ** 2 + ship.velocity.y ** 2)
            if speed > ship.current_speed:
                ship.velocity.x *= ship.current_speed / speed
                ship.velocity.y *= ship.current_speed / speed

        # Обновляем позицию
        ship.position.x += ship.velocity.x * dt
        ship.position.y += ship.velocity.y * dt

        return ship

    def fire_weapon(self, ship_id: str, command: FireCommand) -> Optional[dict]:
        # Выстрел из оружия корабля
        ship = self.ships.get(ship_id)
        if not ship or ship.is_destroyed:
            return None

        if command.weapon_index >= len(ship.weapons):
            return {"error": "Неверный индекс оружия"}

        weapon = ship.weapons[command.weapon_index]
        current_time = time.time()

        # Проверяем возможность выстрела
        if current_time - weapon.last_shot < weapon.cooldown:
            return {"error": "Оружие перезаряжается"}

        if weapon.ammunition == 0:
            return {"error": "Нет боеприпасов"}

        # Проверяем дальность до цели
        dx = command.target.x - ship.position.x
        dy = command.target.y - ship.position.y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > weapon.range:
            return {"error": "Цель вне зоны поражения"}

        # Выполняем выстрел
        weapon.last_shot = current_time
        if weapon.ammunition > 0:
            weapon.ammunition -= 1

        return {
            "success": True,
            "weapon_type": weapon.type,
            "damage": weapon.damage,
            "target": command.target
        } 