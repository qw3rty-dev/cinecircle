import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine= create_engine(url=DATABASE_URL)

sessionLocal= sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db= sessionLocal()
    try:
        yield db
    finally:
        db.close()


