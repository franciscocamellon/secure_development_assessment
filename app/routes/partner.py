from datetime import datetime
from fastapi import APIRouter, Depends, Security
from sqlmodel import Session, select
from app.database import get_session
from app.models.entities import Appointment
from app.models.schemas import AvailabilityPublic
from app.security.auth import get_current_principal
from app.security.rate_limit import default_rate_limit

router = APIRouter(prefix="/partner", tags=["partner"], dependencies=[Depends(default_rate_limit)])


@router.get("/availability", response_model=list[AvailabilityPublic])
def availability(
    start: datetime,
    end: datetime,
    professional_id: int,
    session: Session = Depends(get_session),
    principal=Security(get_current_principal, scopes=["appointments:read_availability"]),
):
    # The partner receives no patient identifiers or reasons, only occupied slots.
    rows = session.exec(
        select(Appointment).where(
            Appointment.professional_id == professional_id,
            Appointment.scheduled_at >= start,
            Appointment.scheduled_at <= end,
            Appointment.status != "cancelled",
        )
    ).all()
    return [AvailabilityPublic(professional_id=professional_id, scheduled_at=row.scheduled_at, available=False) for row in rows]
