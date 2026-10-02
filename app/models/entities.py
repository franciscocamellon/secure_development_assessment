from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    role: str = Field(index=True)
    professional_id: Optional[int] = Field(default=None, foreign_key="healthprofessional.id")
    patient_id: Optional[int] = Field(default=None, foreign_key="patient.id")
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    is_active: bool = True


class Patient(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    document: str = Field(index=True, unique=True)
    email: str


class HealthProfessional(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    registration_number: str = Field(index=True, unique=True)
    specialty: str


class Appointment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patient.id", index=True)
    professional_id: int = Field(foreign_key="healthprofessional.id", index=True)
    scheduled_at: datetime = Field(index=True)
    status: str = Field(default="scheduled", index=True)
    reason: str
    patient_comment: Optional[str] = None
    audit_note: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
