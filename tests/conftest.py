from functools import lru_cache
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm.session import close_all_sessions

from api import create_app
from config import Config, get_config
from database.main import Base, get_db
from database.models import User


@lru_cache()
def get_test_config() -> Config:
    return Config(
        SECRET_KEY="test",
        SQLALCHEMY_DATABASE_URI="postgresql://test:test@localhost:5434/wallit_test",
    )


Engine = create_engine(get_test_config().SQLALCHEMY_DATABASE_URI)
TestSessionLocal = sessionmaker(bind=Engine, autocommit=False, autoflush=True)


def get_test_db() -> Generator[Session, None, None]:
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture()
def app() -> Generator[FastAPI, None, None]:
    app = create_app()
    app.dependency_overrides[get_config] = get_test_config
    app.dependency_overrides[get_db] = get_test_db

    try:
        Base.metadata.create_all(bind=Engine)
        yield app
    finally:
        close_all_sessions()
        Base.metadata.drop_all(bind=Engine)


@pytest.fixture()
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture()
def db() -> Session:
    return next(get_test_db())


class TestException(Exception):
    ...


class TestUser(User):
    MAX_INSTANCES = 5
    count = 1
    int_map = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}

    def __init__(self, main_currency, *args, **kwargs) -> None:
        if TestUser.count <= TestUser.MAX_INSTANCES:
            super().__init__(
                username=f"username{TestUser.count}",
                password=f"password{TestUser.count}",
                email=f"email{TestUser.count}@gmail.com",
                first_name=f"first_{TestUser.int_map[TestUser.count]}",
                last_name=f"last_{TestUser.int_map[TestUser.count]}",
                main_currency=main_currency,
            )
            self.instance_number = TestUser.count
            TestUser.count += 1
        else:
            raise TestException(
                f"Maximum number of {TestUser.__name__} instances reached"
            )


@pytest.fixture(autouse=True)
def reset_test_models() -> None:
    TestUser.count = 1


def get_test_access_token_header(client: TestClient, user: "TestUser") -> dict:
    response = client.post(
        "/token",
        data={"username": user.username, "password": f"password{user.instance_number}"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
