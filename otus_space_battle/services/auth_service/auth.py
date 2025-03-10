from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
import bcrypt
import jwt

router = APIRouter()

SECRET_KEY = "SECRET123"


# Описание схемы данных
class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


@router.post("/register")
async def register(user: UserRegister, db: Session = Depends(get_db)):
    hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"message": "User created"}


@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    result = await db.execute(User.__table__.select().where(User.username == user.username))
    user_in_db = result.fetchone()

    if not user_in_db:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    user_dict = dict(user_in_db)

    if not bcrypt.checkpw(user.password.encode(), user_dict["hashed_password"].encode()):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = jwt.encode({"user_id": user_dict["id"]}, SECRET_KEY, algorithm="HS256")
    return {"access_token": token}
