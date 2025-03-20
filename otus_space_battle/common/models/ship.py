from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import Base
import json

class ShipType(Base):
    __tablename__ = "ship_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    
    # Характеристики корабля
    base_fuel_capacity = Column(Integer, nullable=False)
    base_torpedo_capacity = Column(Integer, nullable=False)
    base_movement_speed = Column(Float, nullable=False)
    base_rotation_speed = Column(Float, nullable=False)
    fuel_consumption_move = Column(Float, nullable=False)
    fuel_consumption_rotate = Column(Float, nullable=False)
    
    # Отношения
    ships = relationship("Ship", back_populates="ship_type")

class Ship(Base):
    __tablename__ = "ships"

    id = Column(Integer, primary_key=True, index=True)
    fleet_id = Column(Integer, ForeignKey("fleets.id", ondelete="CASCADE"), nullable=False)
    ship_type_id = Column(Integer, ForeignKey("ship_types.id", ondelete="RESTRICT"), nullable=False)
    position = Column(Integer, nullable=False)  # Позиция корабля во флоте (1-3)
    coordinates = Column(String, nullable=True)  # Координаты корабля в JSON формате
    
    # Отношения
    fleet = relationship("Fleet", back_populates="ships")
    ship_type = relationship("ShipType", back_populates="ships")
    
    def get_coordinates(self):
        """Получить координаты корабля в виде словаря"""
        if not self.coordinates:
            return {"x": 0, "y": 0}
        return json.loads(self.coordinates)
    
    def set_coordinates(self, coords_dict):
        """Установить координаты корабля из словаря"""
        self.coordinates = json.dumps(coords_dict) 