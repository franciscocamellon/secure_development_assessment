from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

SAFE_TEXT_PATTERN = r"^[A-Za-z0-9_À-ÿ .,;:!?()'\-/]{1,300}$"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)


class AppointmentCreate(StrictModel):
    patient_id: int = Field(gt=0)
    professional_id: int = Field(gt=0)
    scheduled_at: datetime
    reason: str = Field(min_length=3, max_length=120, pattern=SAFE_TEXT_PATTERN)
    patient_comment: str | None = Field(default=None, max_length=300, pattern=SAFE_TEXT_PATTERN)

    @field_validator("scheduled_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("scheduled_at must include timezone information")
        return value


class AppointmentUpdate(StrictModel):
    scheduled_at: datetime | None = None
    status: Literal["scheduled", "confirmed", "cancelled", "completed"] | None = None
    reason: str | None = Field(default=None, min_length=3, max_length=120, pattern=SAFE_TEXT_PATTERN)
    patient_comment: str | None = Field(default=None, max_length=300, pattern=SAFE_TEXT_PATTERN)

    @field_validator("scheduled_at")
    @classmethod
    def require_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("scheduled_at must include timezone information")
        return value


class AppointmentPublic(StrictModel):
    id: int
    patient_id: int
    professional_id: int
    scheduled_at: datetime
    status: str
    reason: str
    patient_comment: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AvailabilityPublic(StrictModel):
    professional_id: int
    scheduled_at: datetime
    available: bool
