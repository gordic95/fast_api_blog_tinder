from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey

from category_post.models import Category
from database.base import Base


class Post(Base):
    __tablename__ = 'posts'


    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(String(255))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    author: Mapped['User'] = relationship(back_populates="posts")
    categories: Mapped['Category'] = relationship(Category, secondary='category_post', back_populates='posts', cascade='all')






