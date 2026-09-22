import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import health, recommendation, subdistricts

# Local dev frontend origins, used when CORS_ORIGINS is not set.
DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


def _cors_origins() -> list[str]:
    """Return CORS origins from the CORS_ORIGINS env var (comma-separated).

    Falls back to the local dev origins when the variable is unset/empty, so
    the same code runs locally and on Render without changes.
    """
    raw = os.environ.get("CORS_ORIGINS", "").strip()
    if not raw:
        return DEFAULT_CORS_ORIGINS
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app = FastAPI(
    title="Bhilwara Water Structure Recommendation API",
    description="Recommends suitable water harvesting/recharge structures for locations in Bhilwara district, Rajasthan.",
    version="0.1.0",
)

# Allow the local Vite dev server and, on Render, the deployed frontend
# origin (set via the CORS_ORIGINS environment variable) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(recommendation.router)
app.include_router(subdistricts.router)