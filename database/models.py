from __future__ import annotations

from datetime import datetime
from enum import Enum

import sqlalchemy as sa
import sqlalchemy.orm as so
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session, with_parent

from database.main import Base
from api.exceptions import RatesUnavailableError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UpdatableMixin:
    def update(self, data: dict, *args: list, **kwargs: dict) -> None:
        for column, value in data.items():
            setattr(self, column, value)


class User(Base, UpdatableMixin):
    __tablename__ = "users"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.Text, index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.Text, unique=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.Text)
    first_name: so.Mapped[str] = so.mapped_column(sa.Text)
    last_name: so.Mapped[str] = so.mapped_column(sa.Text)
    main_currency: so.Mapped[str] = so.mapped_column(sa.String(3), default="CZK")

    transactions: so.Mapped[list[Transaction]] = so.relationship(
        "Transaction",
        cascade="all, delete",
        passive_deletes=True,
        back_populates="user",
        lazy=True,
        uselist=True,
    )
    categories: so.Mapped[list[Category]] = so.relationship(
        "Category",
        cascade="all, delete",
        passive_deletes=True,
        back_populates="user",
        lazy=True,
        uselist=True,
    )

    @property
    def password(self) -> None:
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password: str) -> None:
        self.set_password(password)

    def __repr__(self) -> str:
        return f"{self.username}: {self.first_name} {self.last_name} under email: {self.email}"

    def update(self, data: dict, db: Session, *args, **kwargs) -> None:
        if "main_currency" in data and data["main_currency"] != self.main_currency:
            for transaction in self.select_transactions(db):
                transaction.convert_to_main_amount(data["main_currency"])
        super(self.__class__, self).update(data)

    def set_password(self, password: str) -> None:
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.password_hash)

    def select_transactions(self, db: Session) -> list[Transaction]:
        return list(
            db.scalars(
                select(Transaction).where(with_parent(self, User.transactions))
            ).all()
        )

    def select_categories(self, db: Session) -> list[Category]:
        return list(
            db.scalars(select(Category).filter(Category.user.has(id=self.id))).all()
        )

    def select_banks(self, db: Session) -> list[Bank]:
        return list(
            db.scalars(
                select(Bank)
                .join(Transaction)
                .filter(Transaction.user == self)
                .distinct()
            ).all()
        )

    def select_base_currencies(self, db: Session) -> list[str]:
        return list(
            db.scalars(
                select(Transaction.base_currency)
                .where(with_parent(self, User.transactions))
                .distinct()
            ).all()
        )


class Transaction(Base, UpdatableMixin):
    __tablename__ = "transactions"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    info: so.Mapped[str | None] = so.mapped_column(sa.Text, index=True)
    title: so.Mapped[str | None] = so.mapped_column(sa.Text)
    main_amount: so.Mapped[float] = so.mapped_column("main_amount", index=True)
    base_amount: so.Mapped[float] = so.mapped_column(index=True)
    base_currency: so.Mapped[str] = so.mapped_column(sa.String(3), index=True)
    transaction_date: so.Mapped[datetime] = so.mapped_column(sa.DateTime, index=True)
    creation_date: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime, index=True, default=datetime.utcnow
    )
    place: so.Mapped[str | None] = so.mapped_column(sa.Text)

    category_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("categories.id"), index=True
    )
    user_id: so.Mapped[int | None] = so.mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE")
    )
    bank_id: so.Mapped[int | None] = so.mapped_column(sa.ForeignKey("banks.id"))

    category: so.Mapped[Category | None] = so.relationship(
        "Category", back_populates="transactions"
    )
    user: so.Mapped[User] = so.relationship("User", back_populates="transactions")
    bank: so.Mapped[Bank | None] = so.relationship(
        "Bank", back_populates="transactions"
    )

    def __init__(
        self,
        base_amount: float,
        base_currency: str,
        transaction_date: datetime,
        db: Session,
        **kwargs: dict,
    ) -> None:
        super(Transaction, self).__init__(
            base_amount=base_amount,
            base_currency=base_currency,
            transaction_date=transaction_date,
            **kwargs,
        )
        self.convert_to_main_amount(db=db)

    def __repr__(self) -> str:
        return f"Transaction: {self.base_amount} {self.base_currency} on {self.transaction_date}"

    def update(self, data: dict, db: Session, *args, **kwargs) -> None:
        super(self.__class__, self).update(data)
        if "base_amount" in data or "base_currency" in data:
            self.convert_to_main_amount(db=db)

    def convert_to_main_amount(
        self, db: Session, target_currency: str | None = None
    ) -> None:
        if target_currency is None:
            target_currency = self.user.main_currency
        if target_currency == self.base_currency:
            self.main_amount = self.base_amount
            return

        # No_autoflush is necessary as this is part of Transaction initialization process
        with db.no_autoflush:
            exchange_rate = ExchangeRate.find_exchange_rate(
                self.transaction_date, self.base_currency, target_currency, db
            )
        self.main_amount = round(self.base_amount * exchange_rate, 2)

    @classmethod
    def get_from_id(cls, id: int, user: User, db: Session) -> Transaction | None:
        return db.query(cls).filter_by(id=id, user=user).first()


class MyBanks(Enum):
    REVOLUT = "revolut"
    EQUABANK = "equabank"


class Bank(Base):
    __tablename__ = "banks"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.Text, index=True, unique=True)
    statement_type: so.Mapped[str] = so.mapped_column(sa.String(10))
    name_enum: so.Mapped[MyBanks] = so.mapped_column(unique=True)

    transactions: so.Mapped[int] = so.relationship(
        "Transaction", back_populates="bank", lazy=True, uselist=True
    )

    def __repr__(self) -> str:
        return f"Bank: {self.name}"


class Category(Base, UpdatableMixin):
    __tablename__ = "categories"
    __table_args__ = (sa.UniqueConstraint("name", "user_id"),)

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(
        sa.Text,
        sa.CheckConstraint(
            # Single chain of characters/digits
            # with no whitespaces (foreign characters included)
            "name ~ '^[\u00BF-\u1FFF\u2C00-\uD7FF\w]+$'",
            name="single_word_name_check",
        ),
        index=True,
    )
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE")
    )

    user: so.Mapped[User] = so.relationship(
        "User", back_populates="categories", lazy=True
    )
    transactions: so.Mapped[list[Transaction]] = so.relationship(
        "Transaction", back_populates="category", lazy=True
    )

    def __repr__(self) -> str:
        return f"Category: {self.name}"

    @classmethod
    def get_from_id(cls, id: int, user: User, db: Session) -> Category | None:
        """Query for Category with an id"""
        return db.query(cls).filter_by(id=id, user=user).first()


class ExchangeRate(Base, UpdatableMixin):
    """Table holding exchange rates of various currencies to a single, 'bridge' currency"""

    __tablename__ = "exchange_rates"
    __table_args__ = (sa.UniqueConstraint("date", "source", "rate"),)

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    date: so.Mapped[datetime] = so.mapped_column(sa.DateTime)
    target: so.Mapped[str] = so.mapped_column(sa.String(3), default="EUR")
    source: so.Mapped[str] = so.mapped_column(sa.String(3))
    rate: so.Mapped[float] = so.mapped_column()

    def __repr__(self) -> str:
        return f"""{type(self).__name__}: 1 {self.source} : {self.rate:.2f} {self.target if self.target else 'EUR'} on {self.date.strftime('%Y-%m-%d')}"""

    @classmethod
    def find_exchange_rate(
        cls, date: datetime, source: str, target: str, db: Session
    ) -> float:
        source_rate = db.query(cls).filter_by(date=date.date(), source=source).scalar()
        target_rate = db.query(cls).filter_by(date=date.date(), source=target).scalar()

        if not source_rate or not target_rate:
            raise RatesUnavailableError(source, target, date)

        return (1 / source_rate.rate) * target_rate.rate
