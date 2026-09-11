import uuid
from datetime import datetime, time
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


# ---------- Employee ----------

class EmployeeCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str  # plain password, only used at registration time


class EmployeeLogin(BaseModel):
    email: EmailStr
    password: str


class EmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: EmailStr
    role: str
    created_at: datetime


# ---------- Card ----------

class CardCreate(BaseModel):
    card_uid: str


class CardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    card_uid: str
    is_active: bool
    enrolled_at: datetime


# ---------- Schedule ----------

class ScheduleCreate(BaseModel):
    day_of_week: int
    start_time: time
    end_time: time


class ScheduleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    day_of_week: int
    start_time: time
    end_time: time


# ---------- Attendance ----------

class AttendanceLogCreate(BaseModel):
    punch_type: str        # "in" or "out"
    timestamp: datetime
    source: str             # "card" or "phone_hce"
    device_id: str


class AttendanceLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    employee_id: uuid.UUID
    punch_type: str
    timestamp: datetime
    synced_at: Optional[datetime]
    source: str
    device_id: str


# ---------- Auth token ----------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"