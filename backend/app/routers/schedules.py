from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/schedules",
    tags=["schedules"]
)


@router.post("/", response_model=schemas.ScheduleOut, status_code=status.HTTP_201_CREATED)
def create_schedule(
    schedule: schemas.ScheduleCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(auth.get_current_employee),
):
    # NOTE: for now, employees set their own schedule.
    # Future improvement: restrict this to role == "admin" once an admin panel exists.

    if not (0 <= schedule.day_of_week <= 6):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="day_of_week must be between 0 (Sunday) and 6 (Saturday)."
        )

    if schedule.end_time <= schedule.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_time must be after start_time."
        )

    new_schedule = models.Schedule(
        employee_id=current_employee.id,
        day_of_week=schedule.day_of_week,
        start_time=schedule.start_time,
        end_time=schedule.end_time,
    )
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule


@router.get("/", response_model=list[schemas.ScheduleOut])
def get_my_schedule(
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(auth.get_current_employee),
):
    schedules = (
        db.query(models.Schedule)
        .filter(models.Schedule.employee_id == current_employee.id)
        .order_by(models.Schedule.day_of_week)
        .all()
    )
    return schedules


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(
    schedule_id: str,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(auth.get_current_employee),
):
    schedule = (
        db.query(models.Schedule)
        .filter(models.Schedule.id == schedule_id, models.Schedule.employee_id == current_employee.id)
        .first()
    )
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule entry not found."
        )

    db.delete(schedule)
    db.commit()
    return None