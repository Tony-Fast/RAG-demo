"""
Application configuration management
"""

import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseModel):
    """
    Application settings with environment variable support
    """
    
    # API Configuration
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True
    
    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:5174,https://kef-ragdemo.top"
    
    # DeepSeek API Configuration
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    # Vector Store Configuration (use simple English paths)
    VECTOR_STORE_PATH: str = str(BASE_DIR / "data" / "vectorstore")
    DOCUMENTS_PATH: str = str(BASE_DIR / "data" / "documents")
    
    # Embedding Model Configuration (TF-IDF - no download required)
    EMBEDDING_MODEL: str = "TF-IDF"
    EMBEDDING_DIMENSION: int = 512
    
    # RAG Configuration
    DEFAULT_TOP_K: int = 5
    MAX_TOKENS: int = 20000
    TEMPERATURE: float = 0.7
    SIMILARITY_THRESHOLD: float = 0.1
    
    # Document Processing Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Supported Document Formats
    SUPPORTED_FORMATS: List[str] = [
        ".pdf",      # PDF documents
        ".docx",     # Word documents
        ".xlsx",     # Excel spreadsheets
        ".txt",      # Plain text files
        ".csv"       # CSV files
    ]
    
    # Maximum file size (50MB)
    MAX_FILE_SIZE: int = 50 * 1024 * 1024
    
    # Security Configuration
    APP_PASSWORD: str = "demo123"  # Default password, should be changed in production
    
    model_config = {
        "env_prefix": "",
        "env_file": ".env",
        "extra": "ignore"
    }
    
    @classmethod
    def from_env(cls, env_file: Optional[str] = None):
        """Create settings from environment variables"""
        # Read from environment variables
        return cls(
            APP_HOST=os.getenv("APP_HOST", "0.0.0.0"),
            APP_PORT=int(os.getenv("APP_PORT", 8000)),
            DEBUG=os.getenv("DEBUG", "true").lower() == "true",
            CORS_ORIGINS=os.getenv("CORS_ORIGINS", "http://localhost:5173"),
            DEEPSEEK_API_KEY=os.getenv("DEEPSEEK_API_KEY", ""),
            DEEPSEEK_API_BASE=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1"),
            DEEPSEEK_MODEL=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            VECTOR_STORE_PATH=os.getenv("VECTOR_STORE_PATH", str(BASE_DIR / "data" / "vectorstore")),
            DOCUMENTS_PATH=os.getenv("DOCUMENTS_PATH", str(BASE_DIR / "data" / "documents")),
            EMBEDDING_MODEL=os.getenv("EMBEDDING_MODEL", "TF-IDF"),
            EMBEDDING_DIMENSION=int(os.getenv("EMBEDDING_DIMENSION", 512)),
            DEFAULT_TOP_K=int(os.getenv("DEFAULT_TOP_K", 5)),
            MAX_TOKENS=int(os.getenv("MAX_TOKENS", 1000)),
            TEMPERATURE=float(os.getenv("TEMPERATURE", 0.7)),
            SIMILARITY_THRESHOLD=float(os.getenv("SIMILARITY_THRESHOLD", 0.1)),
            CHUNK_SIZE=int(os.getenv("CHUNK_SIZE", 1000)),
            CHUNK_OVERLAP=int(os.getenv("CHUNK_OVERLAP", 200)),
            APP_PASSWORD=os.getenv("APP_PASSWORD", "demo123"),
        )
    
    @property
    def vector_store_dir(self) -> Path:
        """Get vector store directory path"""
        return Path(self.VECTOR_STORE_PATH)
    
    @property
    def documents_dir(self) -> Path:
        """Get documents directory path"""
        return Path(self.DOCUMENTS_PATH)
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        self.vector_store_dir.mkdir(parents=True, exist_ok=True)
        self.documents_dir.mkdir(parents=True, exist_ok=True)


# Create settings instance (read from environment variables)
settings = Settings.from_env()


def get_settings() -> Settings:
    """
    Get application settings
    """
    return settings
