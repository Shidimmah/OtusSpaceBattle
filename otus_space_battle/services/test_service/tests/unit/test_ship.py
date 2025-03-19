import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.models.base import Base
from common.models.ship import Ship, ShipType
from common.models.fleet import Fleet
from common.models.user import User

@pytest.mark.unit
class TestShip:
    @pytest.fixture
    def engine(self):
        """Создаем тестовую базу данных"""
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        return engine
    
    @pytest.fixture
    def session(self, engine):
        """Создаем сессию для тестов"""
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    @pytest.fixture
    def user(self, session):
        """Создаем тестового пользователя"""
        user = User(username="test_user", email="test@example.com")
        session.add(user)
        session.commit()
        return user
    
    @pytest.fixture
    def fleet(self, session, user):
        """Создаем тестовый флот"""
        fleet = Fleet(user_id=user.id, name="Test Fleet")
        session.add(fleet)
        session.commit()
        return fleet
    
    @pytest.fixture
    def ship_type(self, session):
        """Создаем тип корабля"""
        ship_type = ShipType(
            name="Test Ship Type",
            description="Test Description",
            base_fuel_capacity=100,
            base_torpedo_capacity=10,
            base_movement_speed=5.0,
            base_rotation_speed=2.0,
            fuel_consumption_move=1.0,
            fuel_consumption_rotate=0.5
        )
        session.add(ship_type)
        session.commit()
        return ship_type
    
    def test_ship_type_creation(self, session):
        """Тест создания типа корабля"""
        ship_type = ShipType(
            name="New Ship Type",
            description="New Description",
            base_fuel_capacity=150,
            base_torpedo_capacity=15,
            base_movement_speed=6.0,
            base_rotation_speed=2.5,
            fuel_consumption_move=1.2,
            fuel_consumption_rotate=0.6
        )
        session.add(ship_type)
        session.commit()
        
        # Проверяем, что тип корабля создан
        assert ship_type.id is not None
        assert ship_type.name == "New Ship Type"
        assert ship_type.base_fuel_capacity == 150
        assert ship_type.base_torpedo_capacity == 15
        assert ship_type.base_movement_speed == 6.0
        assert ship_type.base_rotation_speed == 2.5
        assert ship_type.fuel_consumption_move == 1.2
        assert ship_type.fuel_consumption_rotate == 0.6
    
    def test_ship_type_unique_name(self, session):
        """Тест уникальности имени типа корабля"""
        # Создаем первый тип корабля
        ship_type1 = ShipType(
            name="Unique Type",
            description="First Description",
            base_fuel_capacity=100,
            base_torpedo_capacity=10,
            base_movement_speed=5.0,
            base_rotation_speed=2.0,
            fuel_consumption_move=1.0,
            fuel_consumption_rotate=0.5
        )
        session.add(ship_type1)
        session.commit()
        
        # Пытаемся создать второй тип с тем же именем
        ship_type2 = ShipType(
            name="Unique Type",
            description="Second Description",
            base_fuel_capacity=200,
            base_torpedo_capacity=20,
            base_movement_speed=7.0,
            base_rotation_speed=3.0,
            fuel_consumption_move=1.5,
            fuel_consumption_rotate=0.7
        )
        session.add(ship_type2)
        
        # Проверяем, что возникает ошибка
        with pytest.raises(Exception):
            session.commit()
    
    def test_ship_creation(self, session, fleet, ship_type):
        """Тест создания корабля"""
        ship = Ship(
            fleet_id=fleet.id,
            ship_type_id=ship_type.id,
            position=1
        )
        session.add(ship)
        session.commit()
        
        # Проверяем, что корабль создан
        assert ship.id is not None
        assert ship.fleet_id == fleet.id
        assert ship.ship_type_id == ship_type.id
        assert ship.position == 1
        
        # Проверяем связи
        assert ship.fleet == fleet
        assert ship.ship_type == ship_type
    
    def test_ship_cascade_delete(self, session, fleet, ship_type):
        """Тест каскадного удаления корабля при удалении флота"""
        ship = Ship(
            fleet_id=fleet.id,
            ship_type_id=ship_type.id,
            position=1
        )
        session.add(ship)
        session.commit()
        
        # Удаляем флот
        session.delete(fleet)
        session.commit()
        
        # Проверяем, что корабль удален
        assert session.query(Ship).filter_by(id=ship.id).first() is None
    
    def test_ship_type_restrict_delete(self, session, fleet, ship_type):
        """Тест ограничения удаления типа корабля при наличии кораблей"""
        ship = Ship(
            fleet_id=fleet.id,
            ship_type_id=ship_type.id,
            position=1
        )
        session.add(ship)
        session.commit()
        
        # Пытаемся удалить тип корабля
        session.delete(ship_type)
        
        # Проверяем, что возникает ошибка
        with pytest.raises(Exception):
            session.commit() 