from fastapi import FastAPI
from auth import router as auth_router
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from models import Base  # Подключаем модели из единого источника

DATABASE_URL = "postgresql+asyncpg://user:password@database_service/main_db"

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def get_db():
    async with SessionLocal() as session:
        yield session

app = FastAPI(title="Auth Service")

app.include_router(auth_router, prefix="/auth")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
