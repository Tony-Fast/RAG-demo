"""
API Router Configuration
"""

from fastapi import APIRouter
from app.api.v1.endpoints import chat, document, config, health, token

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"]
)

api_router.include_router(
    document.router,
    prefix="/documents",
    tags=["Documents"]
)

api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["Chat"]
)

api_router.include_router(
    config.router,
    prefix="/config",
    tags=["Config"]
)

api_router.include_router(
    token.router,
    prefix="/token",
    tags=["Token"]
)
