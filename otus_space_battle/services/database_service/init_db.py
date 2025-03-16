import sys
import os

# Добавляем путь к common в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'common'))

from models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@database_service/main_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    print("Создание таблиц в БД...")
    Base.metadata.create_all(engine)
    print("Таблицы успешно созданы!")

if __name__ == "__main__":
    init_db()
