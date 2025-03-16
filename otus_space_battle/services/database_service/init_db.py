from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.models import Base  # Подключаем наши модели

DATABASE_URL = "postgresql://user:password@database_service/main_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    print("Создание таблиц в БД...")
    Base.metadata.create_all(engine)
    print("Таблицы успешно созданы!")

if __name__ == "__main__":
    init_db()
