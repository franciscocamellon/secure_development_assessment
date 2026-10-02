from datetime import date, datetime, time, timezone
from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.entities import Appointment, HealthProfessional, Patient, User
from app.models.schemas import AppointmentCreate, AppointmentPublic, AppointmentUpdate
from app.security.auth import get_current_principal
from app.security.authorization import authorize_appointment_access, owned_appointment
from app.security.rate_limit import default_rate_limit

router = APIRouter(prefix="/appointments", tags=["appointments"], dependencies=[Depends(default_rate_limit)])


def _assert_create_ownership(payload: AppointmentCreate, user: User) -> None:
    if user.role != "professional" or user.professional_id != payload.professional_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owning professional may create this appointment")


@router.post("/", response_model=AppointmentPublic, status_code=status.HTTP_201_CREATED)
def create_appointment(
    payload: AppointmentCreate,
    session: Session = Depends(get_session),
    principal=Security(get_current_principal, scopes=["appointments:write"]),
):
    if isinstance(principal, dict):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Human user required")
    _assert_create_ownership(payload, principal)

    if not session.get(Patient, payload.patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")
    if not session.get(HealthProfessional, payload.professional_id):
        raise HTTPException(status_code=404, detail="Professional not found")

    appointment = Appointment(**payload.model_dump(), audit_note="created-via-api")
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment


@router.get("/{appointment_id}", response_model=AppointmentPublic)
def get_appointment(appointment: Appointment = Depends(owned_appointment)):
    return appointment


@router.get("/", response_model=list[AppointmentPublic])
def list_appointments(
    day: date | None = None,
    session: Session = Depends(get_session),
    principal=Security(get_current_principal, scopes=["appointments:read"]),
):
    if isinstance(principal, dict):
        raise HTTPException(status_code=403, detail="Human user required")

    statement = select(Appointment)
    if principal.role == "professional":
        statement = statement.where(Appointment.professional_id == principal.professional_id)
    elif principal.role == "patient":
        statement = statement.where(Appointment.patient_id == principal.patient_id)

    if day:
        start = datetime.combine(day, time.min, tzinfo=timezone.utc)
        end = datetime.combine(day, time.max, tzinfo=timezone.utc)
        statement = statement.where(Appointment.scheduled_at >= start, Appointment.scheduled_at <= end)
    return list(session.exec(statement).all())


@router.patch("/{appointment_id}", response_model=AppointmentPublic)
def update_appointment(
    appointment_id: int,
    payload: AppointmentUpdate,
    session: Session = Depends(get_session),
    principal=Security(get_current_principal, scopes=["appointments:write"]),
):
    if isinstance(principal, dict):
        raise HTTPException(status_code=403, detail="Human user required")
    appointment = session.get(Appointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    authorize_appointment_access(appointment, principal, write=True)

    for key, value in payload.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(appointment, key, value)
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(
    appointment_id: int,
    session: Session = Depends(get_session),
    principal=Security(get_current_principal, scopes=["appointments:write"]),
):
    if isinstance(principal, dict):
        raise HTTPException(status_code=403, detail="Human user required")
    appointment = session.get(Appointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    authorize_appointment_access(appointment, principal, write=True)
    session.delete(appointment)
    session.commit()
    return None
