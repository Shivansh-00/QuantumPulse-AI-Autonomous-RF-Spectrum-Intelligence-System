from .rf_routes import router as rf_router
from .prediction_routes import router as prediction_router
from .optimization_routes import router as optimization_router
from .streaming import router as streaming_router
from .autonomous_routes import router as autonomous_router
from .feature_routes import router as feature_router

__all__ = [
    "rf_router",
    "prediction_router",
    "optimization_router",
    "streaming_router",
    "autonomous_router",
    "feature_router",
]
