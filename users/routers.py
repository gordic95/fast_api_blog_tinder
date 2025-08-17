from fastapi import HTTPException, status
from fastapi import APIRouter, Depends, Security
from database.base import get_db # импортируем функцию для получения соединения с БД
from . models import User
from sqlalchemy.orm import Session # импортируем класс для работы с сессиями
from .scheme import UserInDB, UserCreate, Token

from .utils import get_password_hash, verify_password

from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm

from fastapi.security import OAuth2PasswordBearer

import redis

# подключаемся к локальному экземпляру Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")

SECRET_KEY = "tinder-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()  # делаем копию словаря
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # время истечения токена
    to_encode.update({"exp": expire})  # добавляем время истечения токена в словарь
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # кодируем словарь в токен
    return encoded_jwt  # возвращаем токен


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if redis_client.exists(f"blacklist_{token}") > 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не действителен."
            )
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неавторизированный доступ.")
        return user
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
        return new_user


    @routers.post("/login/", response_model=Token)
    async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
        """Логин пользователя и выдача токена."""
        user = db.query(User).filter(User.username == form_data.username).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль.")
        if not verify_password(form_data.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль.")

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}


    @routers.get("/me")
    async def read_users_me(current_user: User = Depends(get_current_user)):
        """Возвращает информацию о текущем пользователе"""
        print(current_user)
        return current_user


    @routers.post("/logout")
    async def logout(token: str = Depends(oauth2_scheme)):
        """Функция для выхода из аккаунта"""
        redis_client.setex(f"blacklist:{token}", ACCESS_TOKEN_EXPIRE_MINUTES, True)
        return {"detail": "Вы успешно вышли из аккаунта."}


    @routers.get("/all_users")
    async def get_all_users(db: Session = Depends(get_db)):
        """Получение всех пользователей"""
        if db:
            users = db.query(User).all()
            return users

    return routers






