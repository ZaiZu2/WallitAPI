from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from config import get_config

Engine = create_engine(get_config().SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(bind=Engine, autocommit=False, autoflush=True)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
