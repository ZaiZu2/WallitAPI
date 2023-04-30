from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

import api.schemas as s
import database.models as d
from api import TagsEnum
from api.auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_current_user,
    verify_refresh_token,
)
from config import Config, get_config
from database.main import get_db

router = APIRouter(tags=[TagsEnum.USER])


@router.post("/token", response_model=s.Token)
def get_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    config: Config = Depends(get_config),
) -> s.Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user, config)
    refresh_token = create_refresh_token(user, config)
    response.set_cookie(
        "refresh_token",
        refresh_token,
        path=router.url_path_for("refresh_token"),
        secure=True,
        httponly=True,
        samesite="strict",
    )

    return s.Token(access_token=access_token)


@router.put("/token", response_model=s.Token)
def refresh_token(
    refresh_token: str = Cookie(),
    db: Session = Depends(get_db),
    config: Config = Depends(get_config),
) -> s.Token:
    user = verify_refresh_token(refresh_token, db, config)
    access_token = create_access_token(user, config)
    return s.Token(access_token=access_token)


@router.post("/user", response_model=s.User, status_code=status.HTTP_201_CREATED)
def create_user(data: s.UserCreate, db: Session = Depends(get_db)) -> s.User:
    if db.scalar(select(d.User).filter_by(username=data.username)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is already used",
        )
    if db.scalar(select(d.User).filter_by(email=data.email)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail address is already used",
        )

    new_user = d.User(**data.dict())
    db.add(new_user)
    db.commit()

    return new_user


@router.get("/user")
def current_user(user: d.User = Depends(get_current_user)) -> s.User:
    return user


@router.put("/user", response_model=s.User, status_code=status.HTTP_200_OK)
def modify_current_user(
    data: s.UserModify,
    user: d.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> s.User:
    user.update(data.dict(exclude_unset=True), db)
    db.commit()
    return user


@router.delete("/user", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user(
    data: s.Password,
    user: d.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    if not user.verify_password(data.password):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Incorrect password")

    db.delete(user)
    db.commit()


@router.put("/user/password", status_code=status.HTTP_200_OK)
def change_password(
    data: s.PasswordReset,
    user: d.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    if not user.verify_password(data.old_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords does not match"
        )
    user.set_password(data.new_password)
    db.commit()
