from fastapi import FastAPI, APIRouter

from database.base import init_db
from posts.routers import register_posts_routers
from users.routers import register_users_routers

init_db()

app = FastAPI()


app.include_router(register_users_routers())
app.include_router(register_posts_routers())


