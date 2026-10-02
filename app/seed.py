from sqlmodel import Session, select
from app.config import get_settings
from app.database import engine
from app.models.entities import HealthProfessional, Patient, User
from app.security.auth import hash_password


def seed_demo_data() -> None:
    settings = get_settings()
    if not settings.seed_demo_data:
        return
    required = {
        "DEMO_PROFESSIONAL_PASSWORD": settings.demo_professional_password,
        "DEMO_RECEPTIONIST_PASSWORD": settings.demo_receptionist_password,
        "DEMO_ADMIN_PASSWORD": settings.demo_admin_password,
        "DEMO_ADMIN_MFA_SECRET": settings.demo_admin_mfa_secret,
        "DEMO_PATIENT_PASSWORD": settings.demo_patient_password,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(f"SEED_DEMO_DATA=true but demo secrets are missing: {', '.join(missing)}")
    with Session(engine) as session:
        if session.exec(select(User)).first():
            return
        professional = HealthProfessional(full_name="Dr. Demo", registration_number="CRM-DEMO-001", specialty="Clínica geral")
        patient = Patient(full_name="Paciente Demo", document="DEMO-0001", email="patient@example.test")
        session.add(professional)
        session.add(patient)
        session.commit()
        session.refresh(professional)
        session.refresh(patient)

        users = [
            User(username=settings.demo_professional_username, hashed_password=hash_password(settings.demo_professional_password), role="professional", professional_id=professional.id),
            User(username=settings.demo_receptionist_username, hashed_password=hash_password(settings.demo_receptionist_password), role="receptionist"),
            User(username=settings.demo_admin_username, hashed_password=hash_password(settings.demo_admin_password), role="admin", mfa_enabled=True, mfa_secret=settings.demo_admin_mfa_secret),
            User(username="patient.demo", hashed_password=hash_password(settings.demo_patient_password), role="patient", patient_id=patient.id),
        ]
        session.add_all(users)
        session.commit()
