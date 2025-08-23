from fastapi import HTTPException, status
from fastapi import APIRouter, Depends
from database.base import get_db # импортируем функцию для получения соединения с БД
from . models import User
from sqlalchemy.orm import Session # импортируем класс для работы с сессиями
from .scheme import UserInDB, UserCreate, Token
from .utils import get_password_hash, verify_password, create_access_token, create_refresh_token, get_current_user, \
    decode_token, check_token_expiration
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from decouple import config
from . config import REDIS_CLIENT, OAUTH2_SCHEME


ACCESS_TOKEN_EXPIRE_MINUTES = int(config("ACCESS_TOKEN_EXPIRE_MINUTES"))


#---------------------------------------------------------------------------------------------
def register_users_routers() -> APIRouter:
    routers = APIRouter(prefix="/users", tags=["Пользователи"])

    @routers.post("/register/")
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
        return {"status_code": status.HTTP_201_CREATED, "message": "Пользователь успешно создан."}


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
    async def logout(token: str = Depends(OAUTH2_SCHEME)):
        """Функция для выхода из аккаунта"""
        REDIS_CLIENT.setex(f"blacklist:{token}", ACCESS_TOKEN_EXPIRE_MINUTES, 0)
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

    @routers.post("/refresh-token/", response_model=Token)
    async def refresh_tokens(refresh_token: str, db: Session = Depends(get_db)):
        """Обновление токенов с помощью refresh token."""
        decoded_payload = decode_token(refresh_token)
        if not decoded_payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token недействителен.")

        # Проверяем, не истек ли refresh token
        if not check_token_expiration(decoded_payload):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Срок действия refresh token истек.")

        username = decoded_payload["sub"]
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден.")

        # Генерируем новые токены
        new_access_token = create_access_token(data={"sub": username})
        new_refresh_token = create_refresh_token(data={"sub": username})
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "refresh_token": new_refresh_token
        }

    return routers






