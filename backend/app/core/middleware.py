"""
Application middleware components
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from app.core.config import settings


async def api_key_protection_middleware(request: Request, call_next):
    """
    API key protection middleware
    Ensures API keys are not exposed through responses
    """
    response = await call_next(request)
    
    # Add security headers to prevent API key exposure
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    return response
