from fastapi import FastAPI, APIRouter

from category_post.routers import register_categories_routers
from database.base import init_db
from posts.routers import register_posts_routers
from users.routers import register_users_routers

init_db()

app = FastAPI()


app.include_router(register_users_routers())
app.include_router(register_posts_routers())
app.include_router(register_categories_routers())

