import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from common.database import get_engine, get_session, init_db, Base

@pytest.mark.unit
class TestDatabase:
    @pytest.fixture
    def test_engine(self):
        """Фикстура для создания тестового движка базы данных"""
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        yield engine
        Base.metadata.drop_all(engine)

    @pytest.fixture
    def test_session(self, test_engine):
        """Фикстура для создания тестовой сессии"""
        Session = sessionmaker(bind=test_engine)
        session = Session()
        yield session
        session.close()

    def test_get_engine(self):
        """Тест создания движка базы данных"""
        engine = get_engine()
        assert engine is not None
        assert str(engine.url).startswith('postgresql://')

    def test_get_session(self):
        """Тест создания сессии базы данных"""
        session = get_session()
        assert session is not None
        assert hasattr(session, 'execute')

    def test_init_db(self, test_engine):
        """Тест инициализации базы данных"""
        init_db(test_engine)
        # Проверяем, что таблицы созданы
        with test_engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]
            assert len(tables) > 0

    def test_session_commit(self, test_session):
        """Тест коммита транзакции"""
        # Создаем тестовую таблицу
        test_session.execute(text("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """))
        test_session.commit()

        # Проверяем, что таблица создана
        result = test_session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]
        assert 'test_table' in tables

    def test_session_rollback(self, test_session):
        """Тест отката транзакции"""
        # Создаем тестовую таблицу
        test_session.execute(text("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """))
        test_session.rollback()

        # Проверяем, что таблица не создана
        result = test_session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]
        assert 'test_table' not in tables

    def test_session_close(self, test_session):
        """Тест закрытия сессии"""
        test_session.close()
        assert test_session.is_active is False

    def test_connection_pool(self, test_engine):
        """Тест пула соединений"""
        # Создаем несколько соединений
        conn1 = test_engine.connect()
        conn2 = test_engine.connect()
        
        # Проверяем, что соединения разные
        assert conn1 is not conn2
        
        # Закрываем соединения
        conn1.close()
        conn2.close() 