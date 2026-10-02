from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Clinic Secure API"
    environment: str = "development"
    database_url: str = "sqlite:///./clinic.db"
    jwt_secret: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    cors_origins: list[str] = ["http://localhost:3000"]
    seed_demo_data: bool = False

    demo_professional_username: str = "doctor.demo"
    demo_professional_password: str | None = None
    demo_receptionist_username: str = "reception.demo"
    demo_receptionist_password: str | None = None
    demo_admin_username: str = "admin.demo"
    demo_admin_password: str | None = None
    demo_admin_mfa_secret: str | None = None
    demo_patient_password: str | None = None

    lab_client_id: str = "lab-demo"
    lab_client_secret: str | None = None

    rate_limit_default_per_minute: int = 120
    rate_limit_login_per_minute: int = 5

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
