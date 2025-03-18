from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .models import Resource
from .database import get_db
from .routes import resources
from ..common.utils.auth import verify_token

app = FastAPI(title="Resource Management Service")

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 