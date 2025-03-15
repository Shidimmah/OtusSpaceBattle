from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, create_engine
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker
from sqlalchemy.sql import func

DATABASE_URL = "postgresql://user:password@database_service/main_db"

# Базовый класс для всех моделей
class Base(DeclarativeBase):
    pass

# Таблица пользователей
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

# Таблица матчей
class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    player1_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    player2_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    start_time = Column(DateTime, default=func.now())
    end_time = Column(DateTime, nullable=True)
    winner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(String, default="waiting")
    is_ranked = Column(Boolean, default=True)
