from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from app.database import get_session
from app.models.entities import Appointment, User
from app.security.auth import current_user


def authorize_appointment_access(appointment: Appointment, user: User, *, write: bool = False) -> None:
    if write:
        if user.role == "professional" and user.professional_id == appointment.professional_id:
            return
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owning professional may modify this appointment")

    if user.role in {"admin", "receptionist"}:
        return
    if user.role == "professional" and user.professional_id == appointment.professional_id:
        return
    if user.role == "patient" and user.patient_id == appointment.patient_id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Resource ownership check failed")


def owned_appointment(
    appointment_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(current_user),
) -> Appointment:
    appointment = session.get(Appointment, appointment_id)
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    authorize_appointment_access(appointment, user, write=False)
    return appointment
