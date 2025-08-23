from datetime import datetime, timedelta
from decouple import config
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.base import get_db
from . config import REDIS_CLIENT, OAUTH2_SCHEME
from passlib.context import CryptContext
from users.models import User


SECRET_KEY = config('SECRET_KEY')
ALGORITHM = config("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(config("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRES_DAYS = int(config("REFRESH_TOKEN_EXPIRES_DAYS"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") #для хеширования паролей


def verify_password(plain_password, password):  #проверка пароля
    return pwd_context.verify(plain_password, password)

def get_password_hash(password):  #получение хеша пароля
    return pwd_context.hash(password)

def create_access_token(data: dict):
    """Функция для создания токена.
    Сначала копируем словарь в котором у нас указан username, добавляем в него словарь с временем истечения токена.
    Создаем токен, передавая в него словарь с данными, секретный ключ и алгоритм, который используем."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Функция для обновления токена.
    Когда время созданного токена истекает, нужно обновить его.
    Точно так же как и при создании"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRES_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(OAUTH2_SCHEME), db: Session = Depends(get_db)):
    """Функция для получения текущего пользователя"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # декодируем токен
        username = payload.get("sub") # получаем имя пользователя из токена

        if REDIS_CLIENT.exists(f"blacklist_{token}") > 0: # проверяем, есть ли токен в черном списке
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не действителен."
            ) # если токен в черном списке, возвращаем ошибку

        user = db.query(User).filter(User.username == username).first() # получаем пользователя из БД
        if user is None: # если пользователь не найден, возвращаем ошибку
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не авторизированный доступ.")
        return user # если все ок, возвращаем пользователя
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный токен.")

def decode_token(token: str):
    """Функция для декодирования токена"""
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    else:
        return None

def check_token_expiration(payload: dict):
    """Функция для проверки истечения токена"""
    exp_time = payload.get("exp")
    current_time = datetime.utcnow().timestamp()
    if exp_time <= current_time:
        return False #Токен истек
    else:
        return True #Токен не истек