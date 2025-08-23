from pydantic import BaseModel
from typing import Optional, List
from posts.scheme import PostCreate


class CategoryScheme(BaseModel):
    title: str

    class Config:
        # orm_mode = True
        from_attributes = True


class CategoryListScheme(CategoryScheme):
    posts: List[PostCreate]


