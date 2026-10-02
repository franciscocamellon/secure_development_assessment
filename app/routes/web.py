from datetime import date, datetime, time, timezone
from pathlib import Path
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlmodel import Session, select
from starlette.templating import Jinja2Templates

from app.database import get_session
from app.models.entities import Appointment, User
from app.security.auth import require_roles

router = APIRouter(tags=["internal-web"])
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(enabled_extensions=("html", "xml"), default_for_string=True),
)
templates = Jinja2Templates(env=env)


@router.get("/internal/agenda", response_class=HTMLResponse)
def daily_agenda(
    request: Request,
    day: date,
    session: Session = Depends(get_session),
    _user: User = Depends(require_roles("receptionist", "admin")),
):
    start = datetime.combine(day, time.min, tzinfo=timezone.utc)
    end = datetime.combine(day, time.max, tzinfo=timezone.utc)
    appointments = session.exec(
        select(Appointment).where(Appointment.scheduled_at >= start, Appointment.scheduled_at <= end)
    ).all()
    return templates.TemplateResponse(request, "agenda.html", {"day": day, "appointments": appointments})
