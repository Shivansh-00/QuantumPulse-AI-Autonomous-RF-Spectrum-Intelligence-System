"""QuantumPulse AI - Backend Configuration Module."""
from __future__ import annotations

import json
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "postgresql+asyncpg://quantumpulse:quantumpulse@localhost:5432/quantumpulse"
    sync_database_url: str = "postgresql://quantumpulse:quantumpulse@localhost:5432/quantumpulse"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # RF Simulation
    default_sample_rate: int = 10000
    default_duration: float = 1.0
    default_num_signals: int = 5

    # AI Model
    model_path: str = "models/saved/congestion_predictor.pt"
    sequence_length: int = 50
    prediction_horizon: int = 10

    # CORS
    cors_origins: str = '["http://localhost:5173","http://localhost:3000","http://localhost:3001"]'

    @property
    def cors_origin_list(self) -> List[str]:
        return json.loads(self.cors_origins)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
