from collections import defaultdict, deque
from threading import Lock
from time import monotonic
from fastapi import HTTPException, Request, status
from app.config import get_settings

settings = get_settings()


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str, limit: int, window_seconds: int = 60) -> None:
        now = monotonic()
        cutoff = now - window_seconds
        with self._lock:
            bucket = self._hits[key]
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= limit:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
            bucket.append(now)


limiter = InMemoryRateLimiter()


def _client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def login_rate_limit(request: Request) -> None:
    limiter.check(f"login:{_client_key(request)}", settings.rate_limit_login_per_minute)


def default_rate_limit(request: Request) -> None:
    limiter.check(f"api:{_client_key(request)}", settings.rate_limit_default_per_minute)
