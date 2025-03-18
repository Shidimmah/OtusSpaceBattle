from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .models import GameEvent, AnalyticsData
from .database import get_db
from .routes import analytics
from ..common.utils.auth import verify_token

app = FastAPI(title="Analytics Service")

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 