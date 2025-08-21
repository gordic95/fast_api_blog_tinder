from sqlalchemy import String, Integer, ForeignKey, Table, Column
from sqlalchemy.orm import relationship, Mapped, MappedColumn
from database.base import engine, Base


# category_post = Table("category_post", Base.metadata,
#                 Column("post_id", Integer, ForeignKey("posts.id"), primary_key=True),
#                       Column("category_id", Integer, ForeignKey("category.id"), primary_key=True)
#                       )

class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = MappedColumn(Integer, primary_key=True)
    title: Mapped[str] = MappedColumn(String(255), unique=True)

    # posts = relationship("Post", secondary=category_post, back_populates="categories")




