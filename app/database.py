import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# En Docker siempre llega por variable de entorno; sin ella se usa SQLite en memoria.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite://")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
