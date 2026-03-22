"""Database models / schemas for QuantumPulse AI."""
from __future__ import annotations

import datetime
import uuid
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Text
from sqlalchemy.dialects.postgresql import UUID

from database.session import Base


class SignalLog(Base):
    """Stores RF signal simulation logs."""
    __tablename__ = "signal_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    sample_rate = Column(Integer, nullable=False)
    duration = Column(Float, nullable=False)
    num_signals = Column(Integer, nullable=False)
    noise_level = Column(Float, nullable=False, default=0.1)
    signal_configs = Column(JSON, nullable=False)
    # Store a downsampled summary, not the full signal (can be millions of points)
    signal_summary = Column(JSON, nullable=True)


class PredictionLog(Base):
    """Stores AI prediction results."""
    __tablename__ = "prediction_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    signal_log_id = Column(UUID(as_uuid=True), nullable=True)
    mean_congestion = Column(Float, nullable=False)
    max_congestion = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)
    congestion_levels = Column(JSON, nullable=False)
    model_type = Column(String(50), default="lstm")


class OptimizationLog(Base):
    """Stores optimization results."""
    __tablename__ = "optimization_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    signal_log_id = Column(UUID(as_uuid=True), nullable=True)
    original_allocations = Column(JSON, nullable=False)
    optimized_allocations = Column(JSON, nullable=False)
    total_interference = Column(Float, nullable=False)
    signal_clarity = Column(Float, nullable=False)
    improvement_pct = Column(Float, nullable=False)
    iterations = Column(Integer, nullable=False)
