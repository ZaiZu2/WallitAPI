from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

import api.schemas as s
import database.models as d
from api.auth import authenticate_user, create_token, get_current_user
from database.main import get_db

router = APIRouter()


@router.post("/token", response_model=s.Token)
async def get_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> s.Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return s.Token(access_token=create_token(user))


@router.get("/users/me")
async def me(user: d.User = Depends(get_current_user)) -> s.User:
    return user


@router.post("/users/", response_model=s.User, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: s.UserCreate, db: Session = Depends(get_db)) -> s.User:
    if db.scalar(select(d.User).filter_by(username=user_data.username)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already used",
        )
    if db.scalar(select(d.User).filter_by(email=user_data.email)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail address is already used",
        )

    new_user = d.User(**user_data.dict())
    db.add(new_user)
    db.commit()

    return new_user
