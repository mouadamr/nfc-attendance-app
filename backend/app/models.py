import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Time, SmallInteger, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="worker")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    cards = relationship("Card", back_populates="employee")
    schedules = relationship("Schedule", back_populates="employee")
    attendance_logs = relationship("AttendanceLog", back_populates="employee")

    __table_args__ = (
        CheckConstraint("role IN ('worker', 'admin')", name="check_role"),
    )


class Card(Base):
    __tablename__ = "cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    card_uid = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=True)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee", back_populates="cards")


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(SmallInteger, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    employee = relationship("Employee", back_populates="schedules")

    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 0 AND 6", name="check_day_of_week"),
        CheckConstraint("end_time > start_time", name="check_time_range"),
    )


class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    punch_type = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    synced_at = Column(DateTime(timezone=True), nullable=True)
    source = Column(String, nullable=False)
    device_id = Column(String, nullable=False)

    employee = relationship("Employee", back_populates="attendance_logs")

    __table_args__ = (
        CheckConstraint("punch_type IN ('in', 'out')", name="check_punch_type"),
        CheckConstraint("source IN ('card', 'phone_hce')", name="check_source"),
    )