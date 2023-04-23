from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

import database.models as d
from config import get_config
from database.main import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def authenticate_user(db: Session, username: str, password: str) -> d.User | None:
    user = db.scalar(select(d.User).filter_by(username=username))
    if user is None:
        return None
    if not user.verify_password(password):
        return None

    return user


def get_current_user(
    access_token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> d.User | None:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate the credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="The access token has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(access_token, get_config().SECRET_KEY, ["HS256"])
        username = payload.get("sub")
    except ExpiredSignatureError:
        raise token_expired_exception
    except JWTError:
        raise credentials_exception

    user = db.scalar(select(d.User).filter_by(username=username))
    if user is None:
        raise credentials_exception

    return user


def create_access_token(user: d.User) -> str:
    settings = get_config()

    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRATION_MINUTES
    )
    data = {"sub": user.username, "expire": expire.isoformat()}
    return jwt.encode(data, settings.SECRET_KEY, algorithm="HS256")


def create_refresh_token(user: d.User) -> str:
    settings = get_config()

    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRATION_DAYS)
    data = {"sub": user.username, "expire": expire.isoformat()}
    return jwt.encode(data, settings.SECRET_KEY, algorithm="HS256")


def verify_refresh_token(refresh_token: str, db: Session = Depends(get_db)) -> d.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh_token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="The refresh token has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(refresh_token, get_config().SECRET_KEY, ["HS256"])
        username = payload.get("sub")
    except ExpiredSignatureError:
        raise token_expired_exception
    except JWTError:
        raise credentials_exception

    user = db.scalar(select(d.User).filter_by(username=username))
    if user is None:
        raise credentials_exception

    return user
