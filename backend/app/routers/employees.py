from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/employees",
    tags=["employees"]
)


@router.post("/register", response_model=schemas.EmployeeOut, status_code=status.HTTP_201_CREATED)
def register_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    existing = db.query(models.Employee).filter(models.Employee.email == employee.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    new_employee = models.Employee(
        full_name=employee.full_name,
        email=employee.email,
        password_hash=auth.hash_password(employee.password),
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee


@router.post("/login", response_model=schemas.Token)
def login_employee(credentials: schemas.EmployeeLogin, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.email == credentials.email).first()

    if not employee or not auth.verify_password(credentials.password, employee.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = auth.create_access_token(
        data={"sub": str(employee.id), "role": employee.role}
    )
    return schemas.Token(access_token=access_token)


@router.get("/me", response_model=schemas.EmployeeOut)
def get_current_employee(db: Session = Depends(get_db), employee_id: str = Depends(auth.decode_access_token)):
    # placeholder - we'll wire proper token-based auth dependency next step
    pass