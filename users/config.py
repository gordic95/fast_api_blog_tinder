import redis
from fastapi.security import OAuth2PasswordBearer

REDIS_CLIENT = redis.Redis(host='localhost', port=6379, db=0)
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="users/login/")