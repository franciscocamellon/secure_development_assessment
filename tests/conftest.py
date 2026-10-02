import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET"] = "test-secret-that-is-definitely-long-enough-12345"
os.environ["SEED_DEMO_DATA"] = "false"
os.environ["LAB_CLIENT_SECRET"] = "test-lab-client-secret-12345"
os.environ["RATE_LIMIT_LOGIN_PER_MINUTE"] = "100"

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

from app.database import get_session
from app.main import app
from app.models.entities import Appointment, HealthProfessional, Patient, User
from app.security.auth import create_access_token, hash_password


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture
def seeded(session):
    p1 = Patient(full_name="Alice", document="P-1", email="alice@example.test")
    p2 = Patient(full_name="Bob", document="P-2", email="bob@example.test")
    d1 = HealthProfessional(full_name="Dr One", registration_number="CRM-1", specialty="Cardio")
    d2 = HealthProfessional(full_name="Dr Two", registration_number="CRM-2", specialty="Ortho")
    session.add_all([p1, p2, d1, d2])
    session.commit()
    for obj in [p1, p2, d1, d2]:
        session.refresh(obj)

    users = {
        "pro1": User(username="pro1", hashed_password=hash_password("StrongPass-1!"), role="professional", professional_id=d1.id),
        "pro2": User(username="pro2", hashed_password=hash_password("StrongPass-2!"), role="professional", professional_id=d2.id),
        "admin": User(username="admin", hashed_password=hash_password("StrongAdmin-1!"), role="admin"),
        "reception": User(username="reception", hashed_password=hash_password("StrongReception-1!"), role="receptionist"),
        "patient1": User(username="patient1", hashed_password=hash_password("StrongPatient-1!"), role="patient", patient_id=p1.id),
    }
    session.add_all(list(users.values()))
    session.commit()
    for user in users.values():
        session.refresh(user)

    a1 = Appointment(patient_id=p1.id, professional_id=d1.id, scheduled_at=datetime.fromisoformat("2026-10-05T10:00:00+00:00"), reason="Consulta retorno", patient_comment="Tudo bem", audit_note="SECRET-AUDIT")
    a2 = Appointment(patient_id=p2.id, professional_id=d2.id, scheduled_at=datetime.fromisoformat("2026-10-05T11:00:00+00:00"), reason="Consulta inicial", patient_comment="Sem observacao", audit_note="SECRET-AUDIT-2")
    session.add_all([a1, a2])
    session.commit()
    session.refresh(a1)
    session.refresh(a2)
    return {"p1": p1, "p2": p2, "d1": d1, "d2": d2, "a1": a1, "a2": a2, **users}


@pytest.fixture
def client(engine):
    def override_session():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def token_for(user, scopes=None):
    if scopes is None:
        scopes = ["appointments:read", "appointments:write"]
    token, _ = create_access_token(subject=user.username, role=user.role, scopes=scopes, token_type="human", extra_claims={"uid": user.id})
    return token
