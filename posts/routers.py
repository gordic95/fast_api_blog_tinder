from http.client import HTTPException
from typing import Optional

from fastapi import APIRouter, Depends
from . models import Post
from sqlalchemy.orm import Session
from database.base import get_db
from . scheme import PostCreate
from users.models import User

from users.routers import get_current_user
from users.scheme import UserCreate


# routers = APIRouter(prefix="/posts", tags=["Посты"])
def register_posts_routers() -> APIRouter:
    routers = APIRouter(prefix="/posts", tags=["Посты"])

    @routers.get("/get")
    async def get_posts(db: Session = Depends(get_db)):
        """Получение всех постов, смотреть могут все пользователи"""
        if len(db.query(Post).all()) <= 0:
            return {"Message": "Постов нет"}
        else:
            all_posts = db.query(Post).all()
            return all_posts

    @routers.get("/get/{id}")
    async def get_post(id: int, db: Session = Depends(get_db)):
        """Получение поста по id, смотреть могут все пользователи"""
        if len(db.query(Post).filter(Post.id == id).all()) <= 0:
            return {"Message": "Поста нет"}
        else:
            post = db.query(Post).filter(Post.id == id).first()
            return post


#нужно доработать
    @routers.post("/create")
    async def create_post(post: PostCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        """Создание поста, только для авторизованных пользователей"""
        new_post = Post(
            title=post.title,
            content=post.content,

            user_id=current_user.id
        )
        users = db.query(User).all()
        for user in users:
            if new_post.user_id == user.id:
                db.add(new_post)
                db.commit()
                db.refresh(new_post)
                return new_post
        else:
            return {"Message": "Пользователя нет"}



    @routers.put("/update")
    async def update_post(id: int, post: PostCreate, db: Session = Depends(get_db)):
        post_to_update = db.query(Post).filter(Post.id == id).first()
        if post_to_update:
            post_to_update.title = post.title
            post_to_update.content = post.content
            db.commit()
        return {"message": "Пост обновлен"}

    @routers.delete("/delete")
    async def delete_post(id: int, db: Session = Depends(get_db)):
        post = db.query(Post).filter(Post.id == id).first()
        if post:
            db.delete(post)
            db.commit()
        return {"message": "Пост удален"}




    return routers


