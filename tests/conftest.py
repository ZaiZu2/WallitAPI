from typing import Generator

import pytest
from fastapi import FastAPI

from api import create_app
from config import Config, get_config
from database.main import Base, Engine


def get_test_config() -> Config:
    return Config(
        SECRET_KEY="test",
        SQLALCHEMY_DATABASE_URI="postgresql://test:test@localhost:5434/wallit_test",
    )


@pytest.fixture()
def app() -> Generator[FastAPI, None, None]:
    app = create_app()
    app.dependency_overrides[get_config] = get_test_config
    Base.metadata.create_all(bind=Engine)

    yield app

    Base.metadata.drop_all(bind=Engine)
