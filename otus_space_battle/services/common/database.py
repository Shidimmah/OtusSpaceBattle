from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@database_service/main_db")

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency для FastAPI, возвращает сессию базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_models():
    """Инициализирует модели базы данных"""
    Base.metadata.create_all(bind=engine)

def get_engine():
    """Возвращает экземпляр движка базы данных"""
    return engine

def get_session():
    """Возвращает новую сессию базы данных"""
    return SessionLocal()

def init_db():
    """Инициализирует базу данных, создавая все таблицы"""
    Base.metadata.create_all(bind=engine) 