import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from common.database import get_engine, get_session, init_db, get_db, init_models, Base
import asyncio

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

    def test_get_db_yield(self):
        """Тест функции get_db как генератора"""
        db_gen = get_db()
        db = next(db_gen)
        
        # Проверяем, что сессия создана
        assert db is not None
        assert hasattr(db, 'execute')
        assert hasattr(db, 'commit')
        
        # Закрываем сессию
        try:
            next(db_gen)
        except StopIteration:
            pass  # Ожидаемое поведение
            
    @pytest.mark.asyncio
    async def test_init_models(self):
        """Тест асинхронной инициализации моделей"""
        # Создаем тестовый движок
        test_engine = create_engine('sqlite:///:memory:')
        
        # Сохраняем оригинальный движок и устанавливаем тестовый
        original_engine = Base.metadata.bind
        Base.metadata.bind = test_engine
        
        try:
            # Вызываем асинхронную функцию init_models
            await init_models()
            
            # Проверяем, что таблицы созданы
            with test_engine.connect() as conn:
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result]
                assert len(tables) > 0
        finally:
            # Восстанавливаем оригинальный движок
            Base.metadata.bind = original_engine

    def test_get_db_exception(self):
        """Тест обработки исключений в get_db"""
        db_gen = get_db()
        db = next(db_gen)
        
        # Симулируем исключение при работе с сессией
        db.execute(text("SELECT 1"))  # Выполняем запрос
        
        # Проверяем, что сессия закрывается даже при исключении
        try:
            # Вызываем исключение в контексте сессии
            try:
                raise ValueError("Test exception")
            finally:
                # Завершаем генератор (should close the session)
                try:
                    next(db_gen)
                except StopIteration:
                    pass
            
            # Проверяем, что сессия закрыта
            assert db.is_active is False
        except Exception as e:
            pytest.fail(f"Исключение не должно быть выброшено: {e}")
            
    def test_database_url_environment(self, monkeypatch):
        """Тест использования переменной окружения DATABASE_URL"""
        # Устанавливаем тестовую переменную окружения
        test_url = "postgresql://testuser:testpass@testhost/testdb"
        monkeypatch.setenv("DATABASE_URL", test_url)
        
        # Импортируем модуль заново, чтобы переменная окружения была применена
        import importlib
        import common.database
        importlib.reload(common.database)
        
        # Проверяем, что URL базы данных установлен правильно
        assert str(common.database.engine.url) == test_url 