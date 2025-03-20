import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.models.ship import Ship, ShipType
from common.models.fleet import Fleet
from common.models.user import User
from common.models.base import Base

@pytest.mark.unit
class TestShip:
    @pytest.fixture
    def engine(self):
        """Фикстура для создания тестового движка базы данных"""
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        yield engine
        Base.metadata.drop_all(engine)

    @pytest.fixture
    def session(self, engine):
        """Фикстура для создания тестовой сессии"""
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    @pytest.fixture
    def user(self, session):
        """Фикстура для создания тестового пользователя"""
        user = User(
            username="test_user",
            email="test@example.com",
            hashed_password="hashed_password123"
        )
        session.add(user)
        session.commit()
        return user

    @pytest.fixture
    def fleet(self, session, user):
        """Фикстура для создания тестового флота"""
        fleet = Fleet(
            user_id=user.id,
            name="Test Fleet",
            description="Test Fleet Description"
        )
        session.add(fleet)
        session.commit()
        return fleet

    @pytest.fixture
    def ship_type(self, session):
        """Фикстура для создания тестового типа корабля"""
        ship_type = ShipType(
            name="Test Ship Type",
            description="Test Ship Type Description",
            base_fuel_capacity=1000,
            base_torpedo_capacity=10,
            base_movement_speed=10.0,
            base_rotation_speed=5.0,
            fuel_consumption_move=1.0,
            fuel_consumption_rotate=0.5
        )
        session.add(ship_type)
        session.commit()
        return ship_type

    def test_ship_creation(self, session, fleet, ship_type):
        """Тест создания корабля"""
        ship = Ship(
            fleet_id=fleet.id,
            ship_type_id=ship_type.id,
            position={"x": 0, "y": 0}
        )
        session.add(ship)
        session.commit()

        # Проверяем, что корабль создан
        assert ship.id is not None
        assert ship.fleet_id == fleet.id
        assert ship.ship_type_id == ship_type.id
        assert ship.position == {"x": 0, "y": 0}
        assert isinstance(ship.created_at, datetime)

    def test_ship_fleet_relationship(self, session, fleet, ship_type):
        """Тест связи корабля с флотом"""
        ship = Ship(
            fleet_id=fleet.id,
            ship_type_id=ship_type.id,
            position={"x": 0, "y": 0}
        )
        session.add(ship)
        session.commit()

        # Проверяем связь с флотом
        assert ship.fleet == fleet
        assert ship in fleet.ships

    def test_ship_type_relationship(self, session, fleet, ship_type):
        """Тест связи корабля с типом корабля"""
        ship = Ship(
            fleet_id=fleet.id,
            ship_type_id=ship_type.id,
            position={"x": 0, "y": 0}
        )
        session.add(ship)
        session.commit()

        # Проверяем связь с типом корабля
        assert ship.ship_type == ship_type

    def test_ship_cascade_delete(self, session, fleet, ship_type):
        """Тест каскадного удаления корабля"""
        ship = Ship(
            fleet_id=fleet.id,
            ship_type_id=ship_type.id,
            position={"x": 0, "y": 0}
        )
        session.add(ship)
        session.commit()

        # Удаляем корабль
        session.delete(ship)
        session.commit()

        # Проверяем, что корабль удален
        deleted_ship = session.query(Ship).filter_by(id=ship.id).first()
        assert deleted_ship is None

    def test_ship_fleet_null_on_delete(self, session, fleet, ship_type):
        """Тест установки fleet_id в NULL при удалении флота"""
        ship = Ship(
            fleet_id=fleet.id,
            ship_type_id=ship_type.id,
            position={"x": 0, "y": 0}
        )
        session.add(ship)
        session.commit()

        # Удаляем флот
        session.delete(fleet)
        session.commit()

        # Проверяем, что fleet_id установлен в NULL
        updated_ship = session.query(Ship).filter_by(id=ship.id).first()
        assert updated_ship.fleet_id is None

    def test_ship_type_restrict_delete(self, session, fleet, ship_type):
        """Тест ограничения удаления типа корабля при наличии кораблей"""
        ship = Ship(
            fleet_id=fleet.id,
            ship_type_id=ship_type.id,
            position={"x": 0, "y": 0}
        )
        session.add(ship)
        session.commit()

        # Пытаемся удалить тип корабля
        session.delete(ship_type)
        
        # Проверяем, что возникает исключение
        with pytest.raises(Exception):
            session.commit()

    def test_ship_position_update(self, session, fleet, ship_type):
        """Тест обновления позиции корабля"""
        ship = Ship(
            fleet_id=fleet.id,
            ship_type_id=ship_type.id,
            position={"x": 0, "y": 0}
        )
        session.add(ship)
        session.commit()

        # Обновляем позицию
        new_position = {"x": 100, "y": 100}
        ship.position = new_position
        session.commit()

        # Проверяем, что позиция обновилась
        updated_ship = session.query(Ship).filter_by(id=ship.id).first()
        assert updated_ship.position == new_position

    def test_ship_type_unique_name(self, session):
        """Тест уникальности имени типа корабля"""
        # Создаем первый тип корабля
        ship_type1 = ShipType(
            name="Test Ship Type",
            description="Test Ship Type Description 1",
            base_fuel_capacity=1000,
            base_torpedo_capacity=10,
            base_movement_speed=10.0,
            base_rotation_speed=5.0,
            fuel_consumption_move=1.0,
            fuel_consumption_rotate=0.5
        )
        session.add(ship_type1)
        session.commit()

        # Пытаемся создать второй тип корабля с тем же именем
        ship_type2 = ShipType(
            name="Test Ship Type",
            description="Test Ship Type Description 2",
            base_fuel_capacity=2000,
            base_torpedo_capacity=20,
            base_movement_speed=20.0,
            base_rotation_speed=10.0,
            fuel_consumption_move=2.0,
            fuel_consumption_rotate=1.0
        )
        session.add(ship_type2)
        
        # Проверяем, что возникает исключение
        with pytest.raises(Exception):
            session.commit() 