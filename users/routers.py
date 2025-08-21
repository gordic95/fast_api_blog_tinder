from typing import Optional
from fastapi import HTTPException, status
from fastapi import APIRouter, Depends, Security
from database.base import get_db # импортируем функцию для получения соединения с БД
from . models import User
from sqlalchemy.orm import Session # импортируем класс для работы с сессиями
from .scheme import UserInDB, UserCreate, Token
from .utils import get_password_hash, verify_password
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis
from decouple import config

# подключаемся к локальному экземпляру Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login/")


SECRET_KEY = config('SECRET_KEY')
ALGORITHM = config("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(config("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRES_DAYS = int(config("REFRESH_TOKEN_EXPIRES_DAYS"))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRES_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Функция для получения текущего пользователя"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # декодируем токен
        username = payload.get("sub") # получаем имя пользователя из токена

        if redis_client.exists(f"blacklist_{token}") > 0: # проверяем, есть ли токен в черном списке
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

#---------------------------------------------------------------------------------------------
def register_users_routers() -> APIRouter:
    routers = APIRouter(prefix="/users", tags=["Пользователи"])

    @routers.post("/register/", response_model=UserInDB)
    async def register(user_data: UserCreate, db: Session = Depends(get_db)):
        """функция регистрации пользователя"""
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")

        password = get_password_hash(user_data.password)
        new_user = User(username=user_data.username, password=password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "Пользователь успешно зарегистрирован"}


    @routers.post("/login/", response_model=Token)
    async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
        """Логин пользователя и выдача токена."""
        user = db.query(User).filter(User.username == form_data.username).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль.")
        if not verify_password(form_data.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль.")
        access_token = create_access_token(data={"sub": user.username})
        refresh_token = create_refresh_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


    @routers.get("/me")
    async def read_users_me(current_user: User = Depends(get_current_user)):
        """Возвращает информацию о текущем пользователе"""
        return current_user


    @routers.post("/logout")
    async def logout(token: str = Depends(oauth2_scheme)):
        """Функция для выхода из аккаунта"""
        redis_client.setex(f"blacklist:{token}", ACCESS_TOKEN_EXPIRE_MINUTES, 0)
        return {"detail": "Вы успешно вышли из аккаунта."}


    @routers.delete("/delete")
    async def delete_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        if db:
            db.delete(current_user)
            db.commit()
            return {"detail": "Пользователь успешно удален."}


    @routers.get("/all_users")
    async def get_all_users(db: Session = Depends(get_db)):
        """Получение всех пользователей"""
        if db:
            users = db.query(User).all()
            return users

    return routers






