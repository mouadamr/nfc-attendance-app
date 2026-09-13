from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/attendance",
    tags=["attendance"]
)


@router.post("/punch", response_model=schemas.AttendanceLogOut, status_code=status.HTTP_201_CREATED)
def punch(payload: schemas.AttendancePunchRequest, db: Session = Depends(get_db)):
    card = (
        db.query(models.Card)
        .filter(models.Card.card_uid == payload.card_uid, models.Card.is_active == True)
        .first()
    )
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not recognized or inactive."
        )

    employee_id = card.employee_id

    if payload.punch_type not in ("in", "out"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="punch_type must be 'in' or 'out'."
        )

    last_log = (
        db.query(models.AttendanceLog)
        .filter(models.AttendanceLog.employee_id == employee_id)
        .order_by(models.AttendanceLog.timestamp.desc())
        .first()
    )

    if last_log is not None and last_log.punch_type == payload.punch_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid punch sequence: last recorded punch was already '{last_log.punch_type}'."
        )

    new_log = models.AttendanceLog(
        employee_id=employee_id,
        punch_type=payload.punch_type,
        timestamp=payload.timestamp,
        synced_at=datetime.now(timezone.utc),
        source=payload.source,
        device_id=payload.device_id,
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


@router.get("/history", response_model=list[schemas.AttendanceLogOut])
def get_my_history(
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(auth.get_current_employee),
):
    logs = (
        db.query(models.AttendanceLog)
        .filter(models.AttendanceLog.employee_id == current_employee.id)
        .order_by(models.AttendanceLog.timestamp.desc())
        .all()
    )
    return logs