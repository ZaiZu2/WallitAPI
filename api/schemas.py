from typing import Any

from pydantic import BaseModel, EmailStr, Extra, Field, StrictStr, validator

from config import CurrenciesEnum


class GeneralBaseModel(BaseModel):
    class Config:
        extra = Extra.forbid


class User(GeneralBaseModel):
    username: StrictStr
    email: EmailStr
    first_name: StrictStr
    last_name: StrictStr
    main_currency: CurrenciesEnum

    class Config:
        orm_mode = True


class UserCreate(GeneralBaseModel):
    username: StrictStr
    email: EmailStr
    password: str = Field(..., min_length=5)
    first_name: StrictStr
    last_name: StrictStr
    main_currency: CurrenciesEnum

    @validator("*")
    def _prevent_empty_fields(cls, value: Any) -> Any:
        assert value, "Field cannot be empty"
        return value


class UserModify(GeneralBaseModel):
    first_name: StrictStr | None = None
    last_name: StrictStr | None = None
    main_currency: CurrenciesEnum | None = None

    @validator("*")
    def _prevent_empty_fields(cls, value: Any) -> Any:
        assert value, "Field cannot be empty"
        return value


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
