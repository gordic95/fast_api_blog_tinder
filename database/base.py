from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite:///./database.db"

# создание движка
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def init_db():
    pass
    # Base.metadata.drop_all(bind=engine) #удаление таблиц
    Base.metadata.create_all(bind=engine) #создание таблиц

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

