from fastapi import APIRouter, Depends, Form, Header, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.database import get_session
from app.models.schemas import TokenResponse
from app.security.auth import (
    authenticate_user,
    create_access_token,
    verify_admin_mfa,
    verify_m2m_client,
)
from app.security.rate_limit import login_rate_limit

router = APIRouter(prefix="/auth", tags=["authentication"])

ROLE_SCOPES = {
    "professional": ["appointments:read", "appointments:write"],
    "receptionist": ["appointments:read"],
    "admin": ["appointments:read", "admin"],
    "patient": ["appointments:read"],
}


@router.post("/token", response_model=TokenResponse, dependencies=[Depends(login_rate_limit)])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    x_mfa_code: str | None = Header(default=None, alias="X-MFA-Code"),
    session: Session = Depends(get_session),
):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not verify_admin_mfa(user, x_mfa_code):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="MFA required or invalid")

    scopes = ROLE_SCOPES.get(user.role, [])
    token, expires_in = create_access_token(
        subject=user.username,
        role=user.role,
        scopes=scopes,
        token_type="human",
        extra_claims={"uid": user.id},
    )
    return TokenResponse(access_token=token, expires_in=expires_in)


@router.post("/m2m-token", response_model=TokenResponse, dependencies=[Depends(login_rate_limit)])
def m2m_token(
    grant_type: str = Form(..., pattern=r"^client_credentials$"),
    client_id: str = Form(..., min_length=3, max_length=80, pattern=r"^[A-Za-z0-9._-]+$"),
    client_secret: str = Form(..., min_length=12, max_length=200),
    scope: str = Form(default="appointments:read_availability"),
):
    if not verify_m2m_client(client_id, client_secret):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid client credentials")

    allowed_scopes = {"appointments:read_availability"}
    requested_scopes = set(scope.split()) if scope else set()
    if not requested_scopes or not requested_scopes.issubset(allowed_scopes):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requested scope is not allowed")

    token, expires_in = create_access_token(
        subject=client_id,
        role="partner_lab",
        scopes=sorted(requested_scopes),
        token_type="m2m",
        extra_claims={"client_id": client_id, "grant_type": "client_credentials"},
    )
    return TokenResponse(access_token=token, expires_in=expires_in)
