"""
Configuration Endpoints
Handles RAG system configuration
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException

from app.models.schemas import ConfigUpdateRequest, ConfigResponse
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=ConfigResponse)
async def get_configuration():
    """
    Get current RAG configuration
    
    Returns all configuration settings
    """
    try:
        return rag_service.get_config()
    except Exception as e:
        logger.error(f"Failed to get configuration: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get configuration",
                "detail": str(e)
            }
        )


@router.put("")
async def update_configuration(request: ConfigUpdateRequest):
    """
    Update RAG configuration
    
    - **top_k**: Number of context chunks to retrieve (1-20)
    - **temperature**: LLM temperature (0-2)
    - **max_tokens**: Maximum response tokens (100-4000)
    - **chunk_size**: Text chunk size (100-5000)
    - **chunk_overlap**: Chunk overlap size (0-1000)
    - **similarity_threshold**: Minimum similarity score (0-1)
    
    Returns updated configuration
    """
    try:
        # Extract valid updates from request
        updates = {}
        
        if request.top_k is not None:
            updates['top_k'] = request.top_k
        if request.temperature is not None:
            updates['temperature'] = request.temperature
        if request.max_tokens is not None:
            updates['max_tokens'] = request.max_tokens
        if request.chunk_size is not None:
            updates['chunk_size'] = request.chunk_size
        if request.chunk_overlap is not None:
            updates['chunk_overlap'] = request.chunk_overlap
        if request.similarity_threshold is not None:
            updates['similarity_threshold'] = request.similarity_threshold
        
        if not updates:
            return {
                "message": "No updates provided",
                "config": rag_service.get_config()
            }
        
        # Apply updates
        rag_service.update_config(updates)
        
        logger.info(f"Configuration updated: {updates}")
        
        return {
            "message": "Configuration updated successfully",
            "updates": updates,
            "config": rag_service.get_config()
        }
        
    except Exception as e:
        logger.error(f"Failed to update configuration: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to update configuration",
                "detail": str(e)
            }
        )


@router.get("/defaults")
async def get_default_configuration():
    """
    Get default configuration values
    
    Returns default configuration for reference
    """
    return {
        "defaults": {
            "top_k": 5,
            "temperature": 0.7,
            "max_tokens": 1000,
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "similarity_threshold": 0.5
        },
        "constraints": {
            "top_k": {"min": 1, "max": 20},
            "temperature": {"min": 0.0, "max": 2.0},
            "max_tokens": {"min": 100, "max": 4000},
            "chunk_size": {"min": 100, "max": 5000},
            "chunk_overlap": {"min": 0, "max": 1000},
            "similarity_threshold": {"min": 0.0, "max": 1.0}
        }
    }


@router.post("/reset")
async def reset_configuration():
    """
    Reset configuration to defaults
    
    Returns reset status and default configuration
    """
    try:
        # Reset to defaults
        default_config = {
            'top_k': 5,
            'temperature': 0.7,
            'max_tokens': 1000,
            'chunk_size': 1000,
            'chunk_overlap': 200,
            'similarity_threshold': 0.5
        }
        
        rag_service.update_config(default_config)
        
        logger.info("Configuration reset to defaults")
        
        return {
            "message": "Configuration reset to defaults",
            "config": rag_service.get_config()
        }
        
    except Exception as e:
        logger.error(f"Failed to reset configuration: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to reset configuration",
                "detail": str(e)
            }
        )
