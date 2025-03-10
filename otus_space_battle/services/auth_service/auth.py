from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
import bcrypt
import jwt

router = APIRouter()

SECRET_KEY = "SECRET123"


@router.post("/register")
async def register(username: str, email: str, password: str, db: Session = Depends(get_db)):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    new_user = User(username=username, email=email, hashed_password=hashed_password)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"message": "User created"}


@router.post("/login")
async def login(username: str, password: str, db: Session = Depends(get_db)):
    user = await db.execute(User.__table__.select().where(User.username == username))
    user = user.scalar()

    if not user or not bcrypt.checkpw(password.encode(), user.hashed_password.encode()):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = jwt.encode({"user_id": user.id}, SECRET_KEY, algorithm="HS256")
    return {"access_token": token}
