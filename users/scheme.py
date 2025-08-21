from typing import Optional
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserInDB(UserCreate):
    """Класс для хранения данных пользователя в базе данных"""
    id: int
    password: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    """Класс для хранения токена"""
    access_token: str
    token_type: str
    refresh_token: str | None