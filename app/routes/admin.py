from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlmodel import Session, select
from app.database import get_session
from app.models.entities import User
from app.security.auth import get_current_principal

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
def list_users(
    session: Session = Depends(get_session),
    principal=Security(get_current_principal, scopes=["admin"]),
):
    if isinstance(principal, dict) or principal.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator role required")
    # Safe projection: never serialize hashed_password or mfa_secret.
    users = session.exec(select(User)).all()
    return [{"id": u.id, "username": u.username, "role": u.role, "is_active": u.is_active} for u in users]
