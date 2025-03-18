from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .models import GameState, Ship
from .database import get_db
from .routes import game
from ..common.utils.auth import verify_token

app = FastAPI(title="Battle Mechanics Service")

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 