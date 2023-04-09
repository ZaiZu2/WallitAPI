from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api import TagsEnum
import api.schemas as s
import database.models as d
from api.auth import get_current_user
from database.main import get_db

router = APIRouter(prefix="/transactions", tags=[TagsEnum.TRANSACTIONS])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_transaction(
    data: s.TransactionCreate,
    user: d.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> s.Transaction:
    transaction = d.Transaction(user=user, **data.dict(exclude_unset=True), db=db)
    db.add(transaction)
    db.commit()
    return transaction


@router.get("/{id}", status_code=status.HTTP_200_OK)
def get_transaction(
    id: int,
    user: d.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> s.Transaction:
    transaction = d.Transaction.get_from_id(id, user, db)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with the {id=} does not exist",
        )
    return transaction


# Create TransactionModify schema
@router.put("/{id}", status_code=status.HTTP_200_OK)
def modify_transaction(
    id: int,
    data: s.TransactionModify,
    user: d.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> s.Transaction:
    transaction = d.Transaction.get_from_id(id, user, db)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with the {id=} does not exist",
        )
    transaction.update(data.dict(exclude_unset=True), db)
    db.commit()
    return transaction


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    id: int,
    user: d.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    transaction = d.Transaction.get_from_id(id, user, db)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with the {id=} does not exist",
        )
    db.delete(transaction)
    db.commit()
