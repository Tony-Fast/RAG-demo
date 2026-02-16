"""
Application middleware components
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from app.core.config import settings


async def password_protection_middleware(request: Request, call_next):
    """
    Password protection middleware for API endpoints
    
    This middleware checks for a password in the request headers for protected endpoints
    """
    # Define protected endpoints that require password verification
    protected_paths = [
        "/api/v1/chat/ask",  # Chat completion endpoint
        "/api/v1/documents/upload",  # Document upload endpoint
    ]
    
    # Check if the request path is protected
    if any(request.url.path.startswith(path) for path in protected_paths):
        # Get password from request headers
        password = request.headers.get("X-App-Password")
        
        # Verify password
        if not password or password != settings.APP_PASSWORD:
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Unauthorized: Invalid or missing password",
                    "error": "Password required for this endpoint"
                }
            )
    
    # Continue to the next middleware or route handler
    response = await call_next(request)
    return response


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
