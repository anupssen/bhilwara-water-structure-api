import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from .routes import health, recommendation, subdistricts, water_bodies

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# The water-bodies GeoJSON is ~3.4 MB raw and ~0.65 MB gzipped.
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(health.router)
app.include_router(recommendation.router)
app.include_router(subdistricts.router)
app.include_router(water_bodies.router)