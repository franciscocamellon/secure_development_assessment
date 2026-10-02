from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


STRICT_CSP = "default-src 'self'; frame-ancestors 'none'; base-uri 'self'"
# Swagger UI/ReDoc load assets from jsDelivr and use an inline bootstrap script.
DOCS_CSP = (
    "default-src 'self'; img-src 'self' data: https://fastapi.tiangolo.com; "
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; worker-src blob:; "
    "frame-ancestors 'none'; base-uri 'self'"
)
DOCS_PATHS = ("/docs", "/redoc")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = DOCS_CSP if request.url.path in DOCS_PATHS else STRICT_CSP
        return response
