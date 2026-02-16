"""
Chat/QA Endpoints
Handles RAG question answering
"""

import time
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import (
    QuestionRequest,
    AnswerResponse,
    SearchRequest,
    SearchResponse
)
from app.services.rag_service import rag_service
from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    Ask a question and get an answer from the RAG system
    
    - **question**: Your question
    - **top_k**: Number of context chunks to retrieve (default: 5)
    - **stream**: Enable streaming response (not implemented yet)
    
    Returns answer with sources
    """
    start_time = time.time()
    
    try:
        logger.info(f"Received question: {request.question[:100]}...")
        logger.info(f"Received context: {len(request.context) if request.context else 0} messages")
        
        # Process question using RAG service
        result = rag_service.ask(
            question=request.question,
            top_k=request.top_k,
            stream=request.stream,
            context=request.context
        )
        
        # Calculate total response time
        response_time = time.time() - start_time
        
        # Build response
        return AnswerResponse(
            question=result["question"],
            answer=result["answer"],
            sources=result["sources"],
            model=result["model"],
            response_time=response_time
        )
        
    except Exception as e:
        logger.error(f"Failed to process question: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to process question",
                "detail": str(e)
            }
        )


@router.get("/search")
async def search_documents(
    query: str,
    top_k: int = 5
):
    """
    Search for documents in the knowledge base
    
    - **query**: Search query
    - **top_k**: Number of results (default: 5)
    
    Returns search results
    """
    start_time = time.time()
    
    try:
        logger.info(f"Searching for: {query[:100]}...")
        
        # Perform search
        search_results = vector_store.search_by_text(query, top_k=top_k)
        
        # Format results
        results = [
            {
                "content": result.content,
                "document_id": result.document_id,
                "document_name": result.document_name,
                "chunk_index": result.chunk_index,
                "similarity_score": result.similarity_score
            }
            for result in search_results
        ]
        
        search_time = time.time() - start_time
        
        return SearchResponse(
            query=query,
            results=results,
            total_results=len(results),
            search_time=search_time
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Search failed",
                "detail": str(e)
            }
        )


@router.get("/stats")
async def get_system_stats():
    """
    Get system statistics
    
    Returns system stats including vector store, embedding model, and LLM
    """
    try:
        return rag_service.get_system_stats()
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get stats",
                "detail": str(e)
            }
        )


@router.get("/config")
async def get_rag_config():
    """
    Get current RAG configuration
    
    Returns current configuration settings
    """
    try:
        return rag_service.get_config()
    except Exception as e:
        logger.error(f"Failed to get config: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get config",
                "detail": str(e)
            }
        )
