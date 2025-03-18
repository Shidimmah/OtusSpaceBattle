from typing import Dict, Type, List, Optional
from .base import ShipPlugin, ShipBuilder
from ..models.ships import ShipTemplate

class PluginManager:
    # Менеджер плагинов кораблей
    
    def __init__(self):
        self._plugins: Dict[str, Type[ShipPlugin]] = {}
    
    def register_plugin(self, plugin_class: Type[ShipPlugin]) -> None:
        # Регистрирует новый плагин
        plugin = plugin_class()
        metadata = plugin.get_metadata()
        plugin_type = metadata.get("type", "unknown")
        self._plugins[plugin_type] = plugin_class
    
    def get_plugin(self, plugin_type: str) -> Optional[ShipPlugin]:
        # Получает плагин по типу
        plugin_class = self._plugins.get(plugin_type)
        if plugin_class:
            return plugin_class()
        return None
    
    def get_all_plugins(self) -> List[ShipPlugin]:
        # Возвращает список всех зарегистрированных плагинов
        return [plugin_class() for plugin_class in self._plugins.values()]
    
    def build_ship(self, plugin_type: str) -> Optional[ShipTemplate]:
        # Создает корабль с помощью плагина
        plugin = self.get_plugin(plugin_type)
        if not plugin:
            return None
        
        builder = ShipBuilder()
        builder.set_template(plugin.get_ship_template())
        
        for weapon in plugin.get_weapons():
            builder.add_weapon(weapon)
        
        return builder.build()
    
    def get_available_ship_types(self) -> List[str]:
        # Возвращает список доступных типов кораблей
        return list(self._plugins.keys()) 