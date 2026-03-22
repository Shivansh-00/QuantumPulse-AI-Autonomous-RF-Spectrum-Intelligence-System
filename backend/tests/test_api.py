"""API endpoint tests using FastAPI TestClient."""
import pytest
import pytest_asyncio
from contextlib import asynccontextmanager
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock

from database.session import get_db
from main import app


# Override get_db to avoid needing a real database
async def _fake_db():
    """Yield a mock session so routes don't need a running Postgres."""
    session = AsyncMock()
    # Session.add() is synchronous in SQLAlchemy — use a regular MagicMock
    # to avoid 'coroutine was never awaited' warnings.
    session.add = MagicMock()
    yield session


# Replace the real lifespan so tests skip DB/Redis init
@asynccontextmanager
async def _noop_lifespan(app):
    yield


app.dependency_overrides[get_db] = _fake_db
app.router.lifespan_context = _noop_lifespan


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"


@pytest.mark.asyncio
async def test_quick_sim(client):
    resp = await client.get("/api/rf/quick-sim")
    assert resp.status_code == 200
    body = resp.json()
    assert "signal" in body
    assert "time" in body
    assert body["num_signals"] == 5


@pytest.mark.asyncio
async def test_simulate(client):
    resp = await client.post("/api/rf/simulate", json={
        "num_signals": 3,
        "sample_rate": 5000,
        "duration": 0.5,
        "noise_level": 0.1,
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["num_signals"] == 3
    assert len(body["signal"]) > 0


@pytest.mark.asyncio
async def test_predict_congestion(client):
    import numpy as np
    signal = np.random.randn(200).tolist()
    resp = await client.post("/api/predict/congestion", json={
        "signal_data": signal,
        "model_type": "lstm",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["risk_level"] in ("LOW", "MEDIUM", "HIGH")
    assert len(body["congestion_levels"]) > 0


@pytest.mark.asyncio
async def test_optimize_frequency(client):
    resp = await client.post("/api/optimize/frequency", json={
        "signal_configs": [
            {"frequency": 500, "bandwidth": 100},
            {"frequency": 600, "bandwidth": 100},
        ]
    })
    assert resp.status_code == 200
    body = resp.json()
    assert "optimized_allocations" in body
    assert "improvement_pct" in body


@pytest.mark.asyncio
async def test_predict_invalid_model_type(client):
    """Should reject invalid model_type."""
    import numpy as np
    signal = np.random.randn(200).tolist()
    resp = await client.post("/api/predict/congestion", json={
        "signal_data": signal,
        "model_type": "invalid",
    })
    assert resp.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_predict_too_short_signal(client):
    """Should reject signal_data shorter than min_length."""
    resp = await client.post("/api/predict/congestion", json={
        "signal_data": [0.1] * 10,  # too short (min 50)
        "model_type": "lstm",
    })
    assert resp.status_code == 422
