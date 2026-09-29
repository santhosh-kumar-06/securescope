import logging
import time
from collections import defaultdict, deque

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .database import Base, engine
from .routers import scan, assets, events, incidents, defenses

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("securescope")

app = FastAPI(
    title="SecureScope API",
    description="Healthcare Network Exposure, Threat Detection & Incident Response Platform (training tool)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production via env-configured allowlist
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(scan.router)
app.include_router(assets.router)
app.include_router(events.router)
app.include_router(incidents.router)
app.include_router(defenses.router)

# --- simple in-memory rate limiting on write-heavy endpoints ---
RATE_LIMIT_WINDOW_SECONDS = 10
RATE_LIMIT_MAX_REQUESTS = 20
_request_log: dict[str, deque] = defaultdict(deque)
RATE_LIMITED_PATHS = {"/api/scan", "/api/test-events"}


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path in RATE_LIMITED_PATHS:
        client_key = request.client.host if request.client else "unknown"
        now = time.monotonic()
        q = _request_log[client_key]
        while q and now - q[0] > RATE_LIMIT_WINDOW_SECONDS:
            q.popleft()
        if len(q) >= RATE_LIMIT_MAX_REQUESTS:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Please slow down."})
        q.append(now)
    return await call_next(request)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "An unexpected error occurred."})


@app.get("/api/health")
def health():
    return {"status": "operational"}
