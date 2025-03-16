import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from common.database import Base, get_db
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Создаем тестовую базу данных в памяти
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def test_engine():
    """Фикстура для тестового движка базы данных"""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_db(test_engine):
    """Фикстура для тестовой сессии базы данных"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

@pytest.fixture(scope="function")
def override_get_db(test_db):
    """Фикстура для переопределения функции получения базы данных"""
    def _get_test_db():
        try:
            yield test_db
        finally:
            pass
    return _get_test_db

@pytest.fixture(scope="function")
def test_app(override_get_db):
    """Фикстура для тестового приложения FastAPI"""
    app = FastAPI()
    app.dependency_overrides[get_db] = override_get_db
    return app

@pytest.fixture(scope="function")
def test_client(test_app):
    """Фикстура для тестового клиента FastAPI"""
    return TestClient(test_app)

@pytest.fixture(autouse=True)
def clean_db(test_db):
    """Фикстура для очистки базы данных после каждого теста"""
    yield
    for table in reversed(Base.metadata.sorted_tables):
        test_db.execute(table.delete()) 