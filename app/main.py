from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import create_db_and_tables
from app.routes import admin, appointments, auth, partner, web
from app.security.middleware import SecurityHeadersMiddleware
from app.seed import seed_demo_data

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    seed_demo_data()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Secure appointment API used in the DevSecOps assessment.",
    lifespan=lifespan,
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-MFA-Code"],
)
app.include_router(auth.router)
app.include_router(appointments.router)
app.include_router(admin.router)
app.include_router(partner.router)
app.include_router(web.router)


@app.get("/health", tags=["operations"])
def health():
    return {"status": "ok"}
