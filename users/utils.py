from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") #для хеширования паролей


def verify_password(plain_password, password):  #проверка пароля
    return pwd_context.verify(plain_password, password)

def get_password_hash(password):  #получение хеша пароля
    return pwd_context.hash(password)