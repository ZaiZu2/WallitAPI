from datetime import datetime
from functools import lru_cache
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm.session import close_all_sessions

from config import Config, CurrenciesEnum, get_config
from database.main import Base, get_db
from database.models import Bank, Category, Transaction, User
from wallitapi import create_app


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


def get_test_access_token_header(client: TestClient, user: User) -> dict:
    response = client.post(
        "/token",
        data={"username": user.username, "password": f"password{user.id}"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


class TestException(Exception):
    ...


class ModelFactory:
    def __init__(self) -> None:
        self.MAX_INSTANCES = 5
        self.count = {
            User.__name__: 0,
            Category.__name__: 0,
            Bank.__name__: 0,
            Transaction.__name__: 0,
        }
        self.int_map = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five"}

    def create_user(self, main_currency: CurrenciesEnum) -> User:
        self._check_count(User)
        self.count[User.__name__] += 1
        return User(
            username=f"username{self.count[User.__name__]}",
            password=f"password{self.count[User.__name__]}",
            email=f"email{self.count[User.__name__]}@gmail.com",
            first_name=f"first{self.int_map[self.count[User.__name__]]}",
            last_name=f"last{self.int_map[self.count[User.__name__]]}",
            main_currency=main_currency,
        )

    def create_category(self, user: User) -> Category:
        self._check_count(Category)
        self.count[Category.__name__] += 1
        return Category(
            name=f"category{self.int_map[self.count[User.__name__]]}",
            user=user,
        )

    def create_transaction(
        self,
        base_amount: float,
        base_currency: CurrenciesEnum,
        transaction_date: datetime,
        category: Category,
        user: User,
        bank: Bank,
        db: Session,
    ) -> Transaction:
        self._check_count(Transaction)
        self.count[Transaction.__name__] += 1
        return Transaction(
            info=f"info_{self.count[Transaction.__name__]}",
            title=f"title_{self.count[Transaction.__name__]}",
            base_amount=base_amount,
            base_currency=base_currency,
            transaction_date=transaction_date,
            place=f"place_{self.count[Transaction.__name__]}",
            category=category,
            user=user,
            bank=bank,
            db=db,
        )

    def _check_count(self, model: Base) -> None:
        if self.count[model.__name__] > self.MAX_INSTANCES:
            raise TestException(f"Maximum number of {model.__name__} instances reached")


@pytest.fixture()
def model_factory() -> ModelFactory:
    return ModelFactory()
