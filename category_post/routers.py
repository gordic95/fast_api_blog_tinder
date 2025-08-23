from http.client import HTTPException

from fastapi import APIRouter, Depends

from posts.models import Post
from .models import Category, category_post
from sqlalchemy.orm import Session
from database.base import get_db
from .scheme import CategoryScheme, CategoryListScheme
from users.models import User
from users.utils import get_current_user

def register_categories_routers() -> APIRouter:
    routers = APIRouter(prefix="/category", tags=["Категории"])

    @routers.get("/get", )
    async def get_categories(db: Session = Depends(get_db)):
        if db:
            category = db.query(Category).all()
            if len(category) > 0:
                return category
            else:
                return {
                    "message": "Категорий не найдено"
                }
        else:
            return {"message": "Ошибка подключения к базе данных"}

    @routers.post("/post")
    async def add_category(post: CategoryScheme, db: Session = Depends(get_db)):
        if db:
            new_category = Category(
                title=post.title
            )
            if db.query(Category).filter(Category.title == post.title).first():
                return {
                    "message": "Такая категория уже существует"
                }
            else:
                db.add(new_category)
                db.commit()
                return {"message": "Категория успешно добавлена"}

    return routers