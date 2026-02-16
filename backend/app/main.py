"""
RAG Knowledge Base - FastAPI Application Entry Point

A complete RAG (Retrieval-Augmented Generation) knowledge base system
for interview demonstrations.
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

# Add the app directory to Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

from app.core.config import settings
from app.core.middleware import password_protection_middleware, api_key_protection_middleware
from app.api.v1.router import api_router

# Define FastAPI application
app = FastAPI(
    title="RAG Knowledge Base API",
    description="""
    ## RAG知识库系统 API
    
    提供完整的RAG功能：
    
    - 📄 **文档管理** - 上传、解析、存储文档
    - 🧠 **向量存储** - 文本向量化与FAISS索引
    - 💬 **智能问答** - 基于检索的问答生成
    - ⚙️ **配置管理** - 实时参数调整
    
    ### 技术栈
    - FastAPI + Python
    - FAISS 向量数据库
    - DeepSeek LLM
    - Sentence-Transformers 嵌入模型
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Configuration
if settings.CORS_ORIGINS:
    origins = settings.CORS_ORIGINS.split(",")
else:
    origins = ["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.middleware("http")(password_protection_middleware)
app.middleware("http")(api_key_protection_middleware)

# Include API routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API welcome message
    """
    return {
        "message": "Welcome to RAG Knowledge Base API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "RAG Knowledge Base"
    }


def setup_static_files():
    """
    Setup static files directory for frontend build
    """
    static_dir = app_dir.parent / "frontend" / "dist"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


def configure_logging():
    """
    Configure application logging
    """
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


if __name__ == "__main__":
    # Configure logging
    configure_logging()
    
    # Print startup message
    print(f"""
    🚀 RAG Knowledge Base Server Starting...
    
    📖 API Documentation: http://{settings.APP_HOST}:{settings.APP_PORT}/docs
    🔄 ReDoc: http://{settings.APP_HOST}:{settings.APP_PORT}/redoc
    🏠 API Base URL: http://{settings.APP_HOST}:{settings.APP_PORT}/api/v1
    
    ⏳ Waiting for requests...
    """)
    
    # Run the server
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
