from datetime import datetime

import regex as re
from pydantic import BaseModel, EmailStr, Extra, Field, validator
from typing import Generic, TypeVar, Sequence

from config import CurrenciesEnum

# String must only contain alphanumeric characters and underscores
word_regex = alphanumeric_word_regex = r"^\w+$"


def validate_unicode_name(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("String required")

    regex = re.compile(r"^\p{L}+$", re.UNICODE)
    m = regex.fullmatch(value)
    if not m:
        raise ValueError("String must only contain Unicode letters")
    return m.group()


class GeneralBaseModel(BaseModel):
    class Config:
        extra = Extra.forbid


class User(GeneralBaseModel):
    username: str = Field(
        ...,
        regex=alphanumeric_word_regex,
        description="String must only contain alphanumeric characters and underscores",
    )
    email: EmailStr
    first_name: str
    last_name: str
    main_currency: CurrenciesEnum

    class Config:
        orm_mode = True

    _check_unicode_regex = validator("first_name", "last_name", allow_reuse=True)(
        validate_unicode_name
    )


class UserCreate(GeneralBaseModel):
    username: str = Field(
        ...,
        regex=alphanumeric_word_regex,
        description="String must only contain alphanumeric characters and underscores",
    )
    email: EmailStr
    password: str = Field(..., min_length=5)
    first_name: str
    last_name: str
    main_currency: CurrenciesEnum

    _check_unicode_regex = validator("first_name", "last_name", allow_reuse=True)(
        validate_unicode_name
    )


class UserModify(GeneralBaseModel):
    first_name: str | None
    last_name: str | None
    main_currency: CurrenciesEnum | None = None

    _check_unicode_regex = validator("first_name", "last_name", allow_reuse=True)(
        validate_unicode_name
    )


class Password(GeneralBaseModel):
    password: str


class PasswordReset(GeneralBaseModel):
    old_password: str
    new_password: str = Field(..., min_length=5)
    repeat_password: str

    @validator("new_password")
    def _check_new_password(cls, value: str, values: dict) -> str:
        assert value != values.get(
            "old_password"
        ), "The new password cannot be the same as the old one"
        return value

    @validator("repeat_password")
    def _check_repeated_password(cls, repeat_password: str, values: dict) -> str:
        assert repeat_password == values.get("new_password"), "Passwords do not match"
        return repeat_password


class Token(GeneralBaseModel):
    access_token: str
    token_type: str = "bearer"


class Category(GeneralBaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

    _check_unicode_regex = validator("name", allow_reuse=True)(validate_unicode_name)


class CategoryCreate(GeneralBaseModel):
    name: str

    _check_unicode_regex = validator("name", allow_reuse=True)(validate_unicode_name)


class Bank(GeneralBaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

    _check_unicode_regex = validator("name", allow_reuse=True)(validate_unicode_name)


class Transaction(GeneralBaseModel):
    id: int
    info: str | None
    title: str | None
    main_amount: float
    base_amount: float
    base_currency: CurrenciesEnum
    transaction_date: datetime
    creation_date: datetime
    place: str | None
    category: Category | None
    bank: Bank | None

    class Config:
        orm_mode = True


class TransactionCreate(GeneralBaseModel):
    info: str | None
    title: str | None
    base_amount: float
    base_currency: CurrenciesEnum
    transaction_date: datetime
    place: str | None
    category_id: int | None
    bank_id: int | None

    @validator("transaction_date")
    def _check_date(cls, value: datetime) -> datetime:
        assert (
            value.date() < datetime.utcnow().date()
        ), "Transactions can only be set on for the past days"
        return value


class TransactionModify(GeneralBaseModel):
    info: str | None
    title: str | None
    base_amount: float | None
    base_currency: CurrenciesEnum | None
    transaction_date: datetime | None
    place: str | None
    category_id: int | None
    bank_id: int | None

    @validator("transaction_date")
    def _check_date(cls, value: datetime) -> datetime:
        assert (
            value.date() < datetime.utcnow().date()
        ), "Transactions can only be set on for the past days"
        return value


T = TypeVar("T", User, Transaction, Category, Bank)


class Paginated(Generic[T], GeneralBaseModel):
    items: Sequence[T]
    total: int
    limit: int
    offset: int
