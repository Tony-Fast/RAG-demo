"""
Token Usage API Endpoints

Endpoints for retrieving token usage information and limits
"""

from fastapi import APIRouter, HTTPException
from app.services.token_usage_monitor import token_usage_monitor

router = APIRouter()


@router.get("/usage", tags=["Token Usage"])
async def get_token_usage():
    """
    Get current token usage information
    
    Returns:
        Token usage details including current usage, limit, remaining, and percentage
    """
    try:
        usage_info = token_usage_monitor.get_token_usage()
        return usage_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get token usage: {str(e)}")


@router.get("/history", tags=["Token Usage"])
async def get_token_usage_history():
    """
    Get token usage history
    
    Returns:
        Historical token usage by date
    """
    try:
        history = token_usage_monitor.get_usage_history()
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get usage history: {str(e)}")


@router.post("/reset", tags=["Token Usage"])
async def reset_token_usage():
    """
    Reset token usage (admin only)
    
    Returns:
        Success message
    """
    try:
        token_usage_monitor.reset_usage()
        return {"message": "Token usage reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset token usage: {str(e)}")


@router.get("/limit", tags=["Token Usage"])
async def get_token_limit():
    """
    Get current token limit
    
    Returns:
        Token limit information
    """
    try:
        usage_info = token_usage_monitor.get_token_usage()
        return {
            "daily_limit": usage_info["daily_limit"],
            "current_usage": usage_info["current_usage"],
            "remaining": usage_info["remaining"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get token limit: {str(e)}")