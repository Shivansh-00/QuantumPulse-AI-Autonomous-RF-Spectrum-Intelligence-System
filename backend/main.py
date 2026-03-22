"""QuantumPulse AI - Main Application Entry Point."""
from __future__ import annotations

import logging
import time
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from database.session import engine, Base
from database.redis_cache import cache
from routes import rf_router, prediction_router, optimization_router, streaming_router, autonomous_router, feature_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("quantumpulse")

_startup_time: float = 0.0


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize DB tables, Redis, and start background tasks."""
    global _startup_time
    _startup_time = time.time()
    logger.info("Starting QuantumPulse AI...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized.")
    except Exception as exc:
        logger.warning("Database initialization failed (non-fatal): %s", exc)

    # Connect Redis (best-effort; app still works without it)
    try:
        await cache.connect()
        logger.info("Redis connected.")
    except Exception as exc:
        logger.warning("Redis unavailable – caching disabled: %s", exc)

    yield

    # Shutdown
    try:
        await cache.disconnect()
    except Exception:
        pass
    try:
        await engine.dispose()
    except Exception:
        pass
    logger.info("QuantumPulse AI shut down.")


settings = get_settings()

app = FastAPI(
    title="QuantumPulse AI",
    description="Autonomous RF Spectrum Intelligence System",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# ── Global exception handler — never return raw 500s ─────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception on %s %s: %s\n%s",
        request.method, request.url.path, exc, traceback.format_exc(),
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred. The system is still operational.",
        },
    )


# ── Request logging middleware ────────────────────────────────
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s → %d (%.1fms)",
        request.method, request.url.path, response.status_code, duration_ms,
    )
    return response


# Register routers
app.include_router(rf_router, prefix="/api/rf", tags=["RF Simulation"])
app.include_router(prediction_router, prefix="/api/predict", tags=["AI Prediction"])
app.include_router(optimization_router, prefix="/api/optimize", tags=["Optimization"])
app.include_router(autonomous_router, prefix="/api/autonomous", tags=["Autonomous"])
app.include_router(feature_router, prefix="/api/features", tags=["Features"])
app.include_router(streaming_router, prefix="/ws", tags=["WebSocket Streaming"])


@app.get("/api/health")
async def health_check():
    uptime_s = time.time() - _startup_time if _startup_time else 0
    redis_ok = cache._redis is not None
    return {
        "status": "healthy",
        "service": "QuantumPulse AI",
        "uptime_seconds": round(uptime_s, 1),
        "redis_connected": redis_ok,
    }
