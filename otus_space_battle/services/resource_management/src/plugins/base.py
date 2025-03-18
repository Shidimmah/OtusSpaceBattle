from abc import ABC, abstractmethod
from typing import Dict, Any, List
from ..models.ships import ShipTemplate, ShipWeapon

class ShipPlugin(ABC):
    # Базовый класс для плагинов кораблей
    
    @abstractmethod
    def get_ship_template(self) -> ShipTemplate:
        # Возвращает шаблон корабля
        pass
    
    @abstractmethod
    def get_weapons(self) -> List[ShipWeapon]:
        # Возвращает список оружия корабля
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        # Возвращает метаданные плагина
        pass

class ShipBuilder:
    # Builder для создания кораблей
    
    def __init__(self):
        self.template = None
        self.weapons = []
    
    def set_template(self, template: ShipTemplate) -> 'ShipBuilder':
        self.template = template
        return self
    
    def add_weapon(self, weapon: ShipWeapon) -> 'ShipBuilder':
        self.weapons.append(weapon)
        return self
    
    def build(self) -> ShipTemplate:
        if not self.template:
            raise ValueError("Template must be set")
        
        self.template.weapons = self.weapons
        return self.template

class ShipDSL:
    # DSL для описания характеристик кораблей
    
    @staticmethod
    def create_template(
        name: str,
        description: str = "",
        max_speed: float = 100.0,
        acceleration: float = 10.0,
        rotation_speed: float = 5.0,
        fuel_capacity: float = 1000.0,
        fuel_consumption: float = 1.0,
        hull_strength: float = 100.0,
        shield_strength: float = 50.0,
        length: float = 10.0,
        width: float = 10.0,
        is_default: bool = False
    ) -> ShipTemplate:
        # Создает шаблон корабля с заданными характеристиками
        return ShipTemplate(
            id=f"template_{name.lower().replace(' ', '_')}",
            name=name,
            description=description,
            max_speed=max_speed,
            acceleration=acceleration,
            rotation_speed=rotation_speed,
            fuel_capacity=fuel_capacity,
            fuel_consumption=fuel_consumption,
            hull_strength=hull_strength,
            shield_strength=shield_strength,
            length=length,
            width=width,
            is_default=is_default
        )
    
    @staticmethod
    def create_weapon(
        type: str,
        damage: float,
        cooldown: float,
        ammunition: int = -1,
        range: float = 100.0
    ) -> ShipWeapon:
        # Создает оружие с заданными характеристиками
        return ShipWeapon(
            type=type,
            damage=damage,
            cooldown=cooldown,
            ammunition=ammunition,
            range=range
        ) 