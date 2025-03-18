import os
import sys
from sqlalchemy import create_engine, text
from pathlib import Path

# Добавляем путь к корневой директории проекта в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent.parent))

from common.database import Base, engine

def init_database():
    # Инициализирует базу данных
    # Создаем все таблицы
    Base.metadata.create_all(bind=engine)
    
    # Применяем миграции
    migrations_dir = Path(__file__).parent / "migrations"
    if migrations_dir.exists():
        # Создаем таблицу для отслеживания миграций, если её нет
        with engine.connect() as conn:
            conn.execute(text(# CREATE TABLE IF NOT EXISTS migrations (
                    id SERIAL PRIMARY KEY,
                    version VARCHAR(255) NOT NULL UNIQUE,
                    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )))
            conn.commit()
        
        # Применяем все SQL-миграции в порядке версий
        for migration_file in sorted(migrations_dir.glob("V*__*.sql")):
            version = migration_file.name.split("__")[0]
            
            # Проверяем, была ли миграция уже применена
            with engine.connect() as conn:
                result = conn.execute(
                    text("SELECT version FROM migrations WHERE version = :version"),
                    {"version": version}
                ).fetchone()
                
                if not result:
                    # Применяем миграцию
                    with open(migration_file, "r") as f:
                        sql = f.read()
                        conn.execute(text(sql))
                        conn.execute(
                            text("INSERT INTO migrations (version) VALUES (:version)"),
                            {"version": version}
                        )
                        conn.commit()
                    print(f"Applied migration: {migration_file.name}")

if __name__ == "__main__":
    init_database()
