from pydantic import BaseModel


class User(BaseModel):
    username: str
    email: str
    first_name: str | None
    last_name: str | None
    main_currency: str

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str


class UserModify(BaseModel):
    username: str
    first_name: str
    last_name: str
    main_currency: str


class UserLogin(BaseModel):
    username: str
    password: str


class PasswordReset(BaseModel):
    old_password: str
    new_password: str
    repeat_password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
