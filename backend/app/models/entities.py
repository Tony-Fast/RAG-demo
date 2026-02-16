"""
Data entities for the RAG knowledge base
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class DocumentStatus(Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Document:
    """
    Document entity representing an uploaded file
    """
    id: str
    filename: str
    file_path: str
    file_format: str
    file_size: int
    status: DocumentStatus
    created_at: datetime
    title: Optional[str] = None
    updated_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    chunk_count: int = 0
    
    @classmethod
    def create(cls, filename: str, file_path: str, file_format: str, file_size: int) -> "Document":
        """
        Create a new document instance
        """
        # Extract title from filename (remove extension)
        title = filename.rsplit('.', 1)[0] if '.' in filename else filename
        
        return cls(
            id=f"doc_{uuid.uuid4().hex[:12]}",
            filename=filename,
            title=title,
            file_path=file_path,
            file_format=file_format,
            file_size=file_size,
            status=DocumentStatus.PENDING,
            created_at=datetime.now()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "filename": self.filename,
            "title": self.title,
            "file_format": self.file_format,
            "file_size": self.file_size,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "chunk_count": self.chunk_count,
            "metadata": self.metadata
        }


@dataclass
class DocumentChunk:
    """
    Document chunk entity representing a text segment
    """
    id: str
    document_id: str
    chunk_index: int
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    
    @classmethod
    def create(cls, document_id: str, chunk_index: int, content: str, 
               metadata: Optional[Dict[str, Any]] = None) -> "DocumentChunk":
        """
        Create a new document chunk instance
        """
        return cls(
            id=f"chunk_{uuid.uuid4().hex[:12]}",
            document_id=document_id,
            chunk_index=chunk_index,
            content=content,
            metadata=metadata or {}
        )


@dataclass
class SearchResult:
    """
    Search result entity
    """
    chunk_id: str
    document_id: str
    document_name: str
    chunk_index: int
    content: str
    similarity_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_schema(self):
        """Convert to schema for API response"""
        from app.models.schemas import SearchResult as SearchResultSchema
        return SearchResultSchema(
            content=self.content,
            document_id=self.document_id,
            document_name=self.document_name,
            chunk_index=self.chunk_index,
            similarity_score=self.similarity_score,
            metadata=self.metadata
        )


@dataclass
class ChatMessage:
    """
    Chat message entity
    """
    id: str
    role: str  # "user" or "assistant"
    content: str
    sources: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def user_message(cls, content: str) -> "ChatMessage":
        """Create a user message"""
        return cls(
            id=f"msg_{uuid.uuid4().hex[:12]}",
            role="user",
            content=content
        )
    
    @classmethod
    def assistant_message(cls, content: str, sources: List[str] = None) -> "ChatMessage":
        """Create an assistant message"""
        return cls(
            id=f"msg_{uuid.uuid4().hex[:12]}",
            role="assistant",
            content=content,
            sources=sources or []
        )


@dataclass
class Conversation:
    """
    Conversation/chat session entity
    """
    id: str
    title: Optional[str]
    messages: List[ChatMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def create(cls, title: Optional[str] = None) -> "Conversation":
        """Create a new conversation"""
        return cls(
            id=f"conv_{uuid.uuid4().hex[:12]}",
            title=title
        )
    
    def add_message(self, message: ChatMessage):
        """Add a message to the conversation"""
        self.messages.append(message)
        self.updated_at = datetime.now()


@dataclass
class RAGConfig:
    """
    RAG system configuration entity
    """
    top_k: int = 5
    temperature: float = 0.7
    max_tokens: int = 1000
    chunk_size: int = 1000
    chunk_overlap: int = 200
    similarity_threshold: float = 0.1  # Lower threshold for TF-IDF
    model_name: str = "deepseek-chat"
    embedding_model: str = "TF-IDF"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "top_k": self.top_k,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "similarity_threshold": self.similarity_threshold,
            "model_name": self.model_name,
            "embedding_model": self.embedding_model
        }
    
    def update_from_dict(self, config: Dict[str, Any]):
        """Update configuration from dictionary"""
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)


@dataclass
class VectorIndex:
    """
    Vector index metadata entity
    """
    index_path: str
    embedding_model: str
    dimension: int
    total_chunks: int
    created_at: datetime
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "index_path": self.index_path,
            "embedding_model": self.embedding_model,
            "dimension": self.dimension,
            "total_chunks": self.total_chunks,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
