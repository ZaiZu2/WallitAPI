from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api import TagsEnum
import api.schemas as s
import database.models as d
from api.auth import get_current_user
from database.main import get_db

router = APIRouter(prefix="/categories", tags=[TagsEnum.CATEGORIES])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_category(
    data: s.CategoryCreate,
    user: d.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> s.Category:
    if db.scalar(select(d.Category).filter_by(name=data.name, user=user)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category '{data.name}' already exists",
        )

    category = d.Category(user=user, **data.dict(exclude_unset=True))
    db.add(category)
    db.commit()
    return category


@router.get("/{id}", status_code=status.HTTP_200_OK)
def get_category(
    id: int,
    user: d.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> s.Category:
    category = d.Category.get_from_id(id, user, db)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with the {id=} does not exist",
        )
    return category


@router.put("/{id}", status_code=status.HTTP_200_OK)
def modify_category(
    id: int,
    data: s.CategoryCreate,
    user: d.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> s.Category:
    category = d.Category.get_from_id(id, user, db)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with the {id=} does not exist",
        )
    if db.scalar(select(d.Category).filter_by(name=data.name, user=user)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category with the '{data.name=}' already exists",
        )
    category.update(data.dict(exclude_unset=True))
    db.commit()
    return category


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    id: int,
    user: d.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    category = d.Category.get_from_id(id, user, db)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with the {id=} does not exist",
        )
    db.delete(category)
    db.commit()