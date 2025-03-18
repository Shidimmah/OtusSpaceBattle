from typing import Dict, Any, List
from .base import ShipPlugin, ShipDSL
from ..models.ships import ShipTemplate, ShipWeapon

class ScoutShipPlugin(ShipPlugin):
    # Плагин для разведывательного корабля
    
    def get_ship_template(self) -> ShipTemplate:
        return ShipDSL.create_template(
            name="Scout Ship",
            description="Быстрый и маневренный разведывательный корабль",
            max_speed=150.0,
            acceleration=15.0,
            rotation_speed=8.0,
            fuel_capacity=800.0,
            fuel_consumption=1.2,
            hull_strength=60.0,
            shield_strength=30.0,
            length=8.0,
            width=6.0,
            is_default=True
        )
    
    def get_weapons(self) -> List[ShipWeapon]:
        return [
            ShipDSL.create_weapon(
                type="laser",
                damage=20.0,
                cooldown=1.0,
                ammunition=-1,
                range=80.0
            )
        ]
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "version": "1.0.0",
            "author": "System",
            "type": "scout",
            "tags": ["fast", "scout", "light"]
        } 