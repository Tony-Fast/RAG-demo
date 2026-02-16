"""
Health Check Endpoints
System health and status monitoring
"""

import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter

from app.models.schemas import HealthCheck
from app.services.vector_store import vector_store
from app.services.tfidf_embedding_service import embedding_service
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=HealthCheck)
async def health_check():
    """
    Comprehensive health check
    
    Returns system health status including all components
    """
    components = {}
    overall_status = "healthy"
    
    # Check vector store
    try:
        stats = vector_store.get_stats()
        components["vector_store"] = {
            "status": "healthy",
            "total_vectors": stats["total_vectors"],
            "documents": stats["documents_count"]
        }
    except Exception as e:
        components["vector_store"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_status = "degraded"
    
    # Check embedding service
    try:
        info = embedding_service.get_embedding_info()
        components["embedding"] = {
            "status": "healthy",
            "model": info["model_name"],
            "dimension": info["dimension"]
        }
    except Exception as e:
        components["embedding"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_status = "degraded"
    
    # Check LLM service
    try:
        api_healthy = llm_service.check_api_health()
        model_info = llm_service.get_model_info()
        components["llm"] = {
            "status": "healthy" if api_healthy else "unhealthy",
            "model": model_info["model"],
            "api_accessible": api_healthy
        }
        if not api_healthy:
            overall_status = "degraded"
    except Exception as e:
        components["llm"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_status = "degraded"
    
    # Check application
    components["app"] = {
        "status": "healthy",
        "version": "1.0.0"
    }
    
    return HealthCheck(
        status=overall_status,
        components=components,
        timestamp=datetime.now()
    )


@router.get("/live")
async def liveness_check():
    """
    Simple liveness check
    
    Returns 200 if the application is running
    """
    return {"status": "alive", "timestamp": datetime.now().isoformat()}


@router.get("/ready")
async def readiness_check():
    """
    Readiness check
    
    Returns 200 if the application is ready to serve traffic
    """
    try:
        # Check critical components
        vector_store.get_stats()
        llm_service.check_api_health()
        
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/info")
async def get_system_info():
    """
    Get system information
    
    Returns detailed system information
    """
    try:
        return {
            "system": {
                "version": "1.0.0",
                "name": "RAG Knowledge Base"
            },
            "components": {
                "vector_store": vector_store.get_stats(),
                "embedding": embedding_service.get_embedding_info(),
                "llm": llm_service.get_model_info()
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
