from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/cards",
    tags=["cards"]
)


@router.post("/enroll", response_model=schemas.CardOut, status_code=status.HTTP_201_CREATED)
def enroll_card(
    card: schemas.CardCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(auth.get_current_employee),
):
    existing_own_card = (
        db.query(models.Card)
        .filter(models.Card.employee_id == current_employee.id, models.Card.is_active == True)
        .first()
    )
    if existing_own_card:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active card enrolled. Deactivate it first to enroll a new one."
        )

    existing_uid = (
        db.query(models.Card)
        .filter(models.Card.card_uid == card.card_uid, models.Card.is_active == True)
        .first()
    )
    if existing_uid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This card is already registered to another employee."
        )

    new_card = models.Card(
        employee_id=current_employee.id,
        card_uid=card.card_uid,
    )
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return new_card


@router.get("/validate/{card_uid}", response_model=schemas.CardOut)
def validate_card(card_uid: str, db: Session = Depends(get_db)):
    """
    Used by the reader device: given a scanned card UID,
    check if it belongs to a real, active employee.
    NOTE: not yet secured with a device API key — planned for a later step.
    """
    card = (
        db.query(models.Card)
        .filter(models.Card.card_uid == card_uid, models.Card.is_active == True)
        .first()
    )
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not recognized or inactive."
        )
    return card