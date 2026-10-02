from datetime import datetime, timedelta, timezone
import secrets
import bcrypt
import jwt
import pyotp
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jwt import InvalidTokenError
from sqlmodel import Session, select

from app.config import get_settings
from app.database import get_session
from app.models.entities import User

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
    scopes={
        "appointments:read": "Read appointments",
        "appointments:write": "Create and update appointments",
        "appointments:read_availability": "Read availability only",
        "admin": "Administrative operations",
    },
)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(*, subject: str, role: str, scopes: list[str], token_type: str, extra_claims: dict | None = None) -> tuple[str, int]:
    expires_minutes = settings.access_token_expire_minutes
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "role": role,
        "scopes": scopes,
        "token_type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)
    encoded = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded, expires_minutes * 60


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc


def authenticate_user(session: Session, username: str, password: str) -> User | None:
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not user.is_active or not verify_password(password, user.hashed_password):
        return None
    return user


def verify_admin_mfa(user: User, mfa_code: str | None) -> bool:
    if user.role != "admin" or not user.mfa_enabled:
        return True
    if not user.mfa_secret or not mfa_code:
        return False
    return pyotp.TOTP(user.mfa_secret).verify(mfa_code, valid_window=1)


def verify_m2m_client(client_id: str, client_secret: str) -> bool:
    if not settings.lab_client_secret:
        return False
    return secrets.compare_digest(client_id, settings.lab_client_id) and secrets.compare_digest(
        client_secret, settings.lab_client_secret
    )


async def get_current_principal(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    payload = decode_token(token)
    token_scopes = set(payload.get("scopes", []))
    required = set(security_scopes.scopes)
    if not required.issubset(token_scopes):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient scope")

    token_type = payload.get("token_type")
    if token_type == "m2m":
        return {"kind": "m2m", **payload}

    username = payload.get("sub")
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown or inactive user")
    return user


def current_user(principal=Security(get_current_principal, scopes=[])) -> User:
    if isinstance(principal, dict):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Human user token required")
    return principal


def require_roles(*roles: str):
    def dependency(user: User = Depends(current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role not allowed")
        return user
    return dependency
