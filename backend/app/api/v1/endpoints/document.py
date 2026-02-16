"""
Document Endpoints
Handles document upload, retrieval, and management
"""

import os
import time
import logging
from pathlib import Path
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.models.schemas import (
    DocumentResponse,
    DocumentListResponse,
    UploadResponse,
    ErrorResponse
)
from app.models.entities import DocumentStatus
from app.services.document_processor import document_processor
from app.services.vector_store import vector_store
from app.services.tfidf_embedding_service import embedding_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document for processing
    
    - **file**: Document file (PDF, DOCX, XLSX, TXT, CSV)
    
    Returns upload status and document info
    """
    start_time = time.time()
    
    # Validate file format
    file_format = Path(file.filename).suffix.lower()
    if file_format not in settings.SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid file format",
                "detail": f"Supported formats: {', '.join(settings.SUPPORTED_FORMATS)}",
                "received": file_format
            }
        )
    
    # Validate file size
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "File too large",
                "detail": f"Maximum file size: {settings.MAX_FILE_SIZE // (1024*1024)}MB",
                "received": f"{file_size / (1024*1024):.2f}MB"
            }
        )
    
    try:
        import uuid
        
        # Generate document ID first
        document_id = str(uuid.uuid4())
        
        # Save file with document_id as filename
        documents_dir = Path(settings.DOCUMENTS_PATH)
        documents_dir.mkdir(parents=True, exist_ok=True)
        
        file_ext = Path(file.filename).suffix.lower()
        saved_filename = f"{document_id}{file_ext}"
        file_path = documents_dir / saved_filename
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"File saved: {file_path}")
        
        # Process document
        document, chunks = await document_processor.process_document(
            str(file_path),
            file.filename
        )
        
        if document.status == DocumentStatus.COMPLETED:
            # Generate embeddings
            embeddings = embedding_service.encode(
                [chunk.content for chunk in chunks],
                show_progress=False
            )
            
            # Add to vector store with document name
            vector_store.add_chunks(chunks, embeddings, document_name=document.filename)
            
            logger.info(f"Document indexed: {document.id}")
        
        processing_time = time.time() - start_time
        
        return UploadResponse(
            message="Document uploaded and processed successfully" if document.status == DocumentStatus.COMPLETED else "Document uploaded but processing failed",
            document_id=document.id,
            filename=document.filename,
            file_size=document.file_size,
            processing_time=round(processing_time, 2)
        )
        
    except Exception as e:
        import traceback
        logger.error(f"Document upload failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Upload failed",
                "detail": str(e),
                "type": type(e).__name__
            }
        )


@router.get("/list", response_model=DocumentListResponse)
async def list_documents():
    """
    List all documents in the knowledge base
    
    Returns list of documents with metadata
    """
    try:
        documents_dir = Path(settings.DOCUMENTS_PATH)
        
        if not documents_dir.exists():
            return DocumentListResponse(
                documents=[],
                total_count=0,
                total_size=0
            )
        
        documents = []
        total_size = 0
        
        # Get document info from files
        for file_path in documents_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in settings.SUPPORTED_FORMATS:
                stat = file_path.stat()
                
                # Try to get original filename from metadata file
                original_filename = file_path.name
                metadata_file_path = file_path.with_suffix('.metadata.json')
                
                if metadata_file_path.exists():
                    try:
                        import json
                        with open(metadata_file_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            if 'original_filename' in metadata:
                                original_filename = metadata['original_filename']
                                logger.info(f"Found original filename for {file_path.name}: {original_filename}")
                    except Exception as e:
                        logger.error(f"Failed to read metadata file {metadata_file_path}: {e}")
                
                doc = DocumentResponse(
                    id=file_path.stem,
                    filename=original_filename,
                    file_format=file_path.suffix.lower(),
                    file_size=stat.st_size,
                    status=DocumentStatus.COMPLETED,
                    created_at=stat.st_ctime,
                    chunk_count=0  # Would need metadata file for this
                )
                documents.append(doc)
                total_size += stat.st_size
        
        # Sort by creation time
        documents.sort(key=lambda x: x.created_at, reverse=True)
        
        return DocumentListResponse(
            documents=documents,
            total_count=len(documents),
            total_size=total_size
        )
        
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to list documents",
                "detail": str(e)
            }
        )


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document from the knowledge base
    
    - **document_id**: Document ID to delete
    
    Returns deletion status
    """
    try:
        # Find document file (try all common extensions)
        documents_dir = Path(settings.DOCUMENTS_PATH)
        file_path = None
        
        for ext in ['.pdf', '.docx', '.xlsx', '.txt', '.csv', '.doc', '.xls']:
            candidate = documents_dir / f"{document_id}{ext}"
            if candidate.exists():
                file_path = candidate
                break
        
        if not file_path:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Document not found",
                    "document_id": document_id
                }
            )
        
        # Delete from vector store
        deleted_chunks = vector_store.delete_by_document_id(document_id)
        logger.info(f"Deleted {deleted_chunks} chunks from vector store")
        
        # Delete file
        file_path.unlink()
        
        return {
            "message": "Document deleted successfully",
            "document_id": document_id,
            "chunks_deleted": deleted_chunks
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to delete document",
                "detail": str(e)
            }
        )


@router.get("/{document_id}/preview")
async def preview_document(document_id: str):
    """
    Preview document content (first portion)
    
    - **document_id**: Document ID
    
    Returns document preview
    """
    try:
        documents_dir = Path(settings.DOCUMENTS_PATH)
        file_path = None
        
        for f in documents_dir.iterdir():
            if f.is_file() and f.stem == document_id:
                file_path = f
                break
        
        if not file_path:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Document not found",
                    "document_id": document_id
                }
            )
        
        # Process document for preview
        document, chunks = await document_processor.process_document(
            str(file_path),
            file_path.name
        )
        
        # Get preview text (first 2000 characters)
        preview_text = ""
        for chunk in chunks[:3]:
            preview_text += chunk.content + "\n\n"
        
        preview_text = preview_text[:2000] + ("..." if len(preview_text) > 2000 else "")
        
        return {
            "document_id": document.id,
            "filename": document.filename,
            "format": document.file_format,
            "status": document.status.value,
            "chunk_count": len(chunks),
            "preview": preview_text
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to preview document: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to preview document",
                "detail": str(e)
            }
        )


@router.post("/rebuild-index")
async def rebuild_index(background_tasks: BackgroundTasks = None):
    """
    Rebuild the entire vector index
    
    Returns index rebuild status
    """
    try:
        # Get all documents
        documents_dir = Path(settings.DOCUMENTS_PATH)
        
        if not documents_dir.exists():
            return {
                "message": "No documents to index",
                "total_chunks": 0
            }
        
        all_chunks = []
        
        for file_path in documents_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in settings.SUPPORTED_FORMATS:
                try:
                    document, chunks = await document_processor.process_document(
                        str(file_path),
                        file_path.name
                    )
                    all_chunks.extend(chunks)
                    logger.info(f"Processed: {file_path.name} ({len(chunks)} chunks)")
                except Exception as e:
                    logger.error(f"Failed to process {file_path.name}: {e}")
        
        if all_chunks:
            # Clear existing index
            vector_store.clear()
            
            # Generate embeddings
            embeddings = embedding_service.encode(
                [chunk.content for chunk in all_chunks],
                show_progress=True
            )
            
            # Add to vector store
            vector_store.add_chunks(all_chunks, embeddings)
        
        return {
            "message": "Index rebuilt successfully",
            "total_documents": len(list(documents_dir.iterdir())),
            "total_chunks": len(all_chunks)
        }
        
    except Exception as e:
        logger.error(f"Failed to rebuild index: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to rebuild index",
                "detail": str(e)
            }
        )
