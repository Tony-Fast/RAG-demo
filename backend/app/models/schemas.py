"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentStatus(str, Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentBase(BaseModel):
    """Base document schema"""
    id: str
    filename: str
    file_format: str
    file_size: int
    status: DocumentStatus
    created_at: datetime
    chunk_count: int = 0
    
    class Config:
        from_attributes = True


class DocumentCreate(BaseModel):
    """Schema for creating a document"""
    pass


class DocumentResponse(BaseModel):
    """Document response schema"""
    id: str
    filename: str
    file_format: str
    file_size: int
    status: DocumentStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    chunk_count: int = 0
    metadata: Optional[Dict[str, Any]] = None


class DocumentListResponse(BaseModel):
    """Document list response schema"""
    documents: List[DocumentResponse]
    total_count: int
    total_size: int


class QuestionRequest(BaseModel):
    """Question request schema"""
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: Optional[int] = Field(default=5, ge=1, le=20)
    stream: bool = Field(default=False, description="Enable streaming response")
    context: Optional[List[Dict[str, str]]] = Field(default=None, description="Conversation context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "什么是RAG技术？",
                "top_k": 5,
                "stream": True,
                "context": [
                    {"role": "user", "content": "你好"},
                    {"role": "assistant", "content": "你好，我是你的AI助手"}
                ]
            }
        }


class SourceDocument(BaseModel):
    """Source document schema for citations"""
    id: str
    filename: str
    chunk_index: int
    similarity_score: float
    content: str
    page_number: Optional[int] = None
    start_position: Optional[int] = None
    end_position: Optional[int] = None


class AnswerResponse(BaseModel):
    """Answer response schema"""
    question: str
    answer: str
    sources: List[SourceDocument]
    model: str
    response_time: float
    tokens_used: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "什么是RAG技术？",
                "answer": "RAG（Retrieval-Augmented Generation）是一种...",
                "sources": [
                    {
                        "id": "doc123",
                        "filename": "技术介绍.pdf",
                        "chunk_index": 0,
                        "similarity_score": 0.95,
                        "content": "RAG技术是..."
                    }
                ],
                "model": "deepseek-chat",
                "response_time": 2.5
            }
        }


class ChatHistoryItem(BaseModel):
    """Chat history item schema"""
    id: str
    question: str
    answer: str
    sources: List[str] = []
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    """Chat history response schema"""
    history: List[ChatHistoryItem]
    total_count: int


class SearchRequest(BaseModel):
    """Vector search request schema"""
    query: str = Field(..., min_length=1)
    top_k: Optional[int] = Field(default=5, ge=1, le=20)


class SearchResult(BaseModel):
    """Vector search result schema"""
    content: str
    document_id: str
    document_name: str
    chunk_index: int
    similarity_score: float
    metadata: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    """Search response schema"""
    query: str
    results: List[SearchResult]
    total_results: int
    search_time: float


class VectorIndexStatus(BaseModel):
    """Vector index status schema"""
    index_exists: bool
    total_chunks: int
    index_path: str
    embedding_model: str
    dimension: int


class ConfigUpdateRequest(BaseModel):
    """Configuration update request schema"""
    top_k: Optional[int] = Field(default=None, ge=1, le=20)
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=100, le=4000)
    chunk_size: Optional[int] = Field(default=None, ge=100, le=5000)
    chunk_overlap: Optional[int] = Field(default=None, ge=0, le=1000)
    similarity_threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "top_k": 10,
                "temperature": 0.5,
                "max_tokens": 2000
            }
        }


class ConfigResponse(BaseModel):
    """Configuration response schema"""
    rag_config: Dict[str, Any]
    embedding_config: Dict[str, Any]
    llm_config: Dict[str, Any]
    document_config: Dict[str, Any]


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    status_code: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid file format",
                "detail": "Only PDF, DOCX, XLSX, TXT files are supported",
                "status_code": 400
            }
        }


class UploadResponse(BaseModel):
    """File upload response schema"""
    message: str
    document_id: str
    filename: str
    file_size: int
    processing_time: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Document uploaded successfully",
                "document_id": "doc_abc123",
                "filename": "面试指南.pdf",
                "file_size": 1024000,
                "processing_time": 5.2
            }
        }


class HealthCheck(BaseModel):
    """Health check response schema"""
    status: str
    components: Dict[str, Any]
    timestamp: datetime
