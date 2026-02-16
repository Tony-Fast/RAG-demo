"""
RAG Service
Core Retrieval-Augmented Generation service
"""

import time
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime

from app.core.config import settings
from app.models.entities import SearchResult, RAGConfig
from app.services.vector_store import vector_store
from app.services.tfidf_embedding_service import embedding_service
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class RAGService:
    """
    Core RAG service combining retrieval and generation
    """
    
    def __init__(self):
        self.config = RAGConfig()
    
    def ask(
        self,
        question: str,
        top_k: Optional[int] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        context: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG
        
        Args:
            question: User question
            top_k: Number of context chunks to retrieve
            temperature: LLM temperature
            max_tokens: Maximum response tokens
            stream: Enable streaming response
            context: Conversation context (list of previous messages)
            
        Returns:
            Dictionary with answer and sources
        """
        start_time = time.time()
        
        # Use default config if not specified
        k = top_k or self.config.top_k
        temp = temperature or self.config.temperature
        tokens = max_tokens or self.config.max_tokens
        
        logger.info(f"Processing question: {question[:100]}...")
        
        try:
            # Step 1: Retrieve relevant documents
            retrieval_start = time.time()
            search_results = vector_store.search_by_text(question, top_k=k)
            retrieval_time = time.time() - retrieval_start
            
            logger.info(f"Retrieved {len(search_results)} relevant chunks in {retrieval_time:.2f}s")
            
            # Filter by similarity threshold
            filtered_results = [
                r for r in search_results 
                if r.similarity_score >= self.config.similarity_threshold
            ]
            
            if not filtered_results:
                # No relevant documents found
                return {
                    "question": question,
                    "answer": "抱歉，我在当前知识库中没有找到与您问题相关的信息。您可以尝试：\n1. 检查问题是否清晰明确\n2. 上传更多相关的文档到知识库\n3. 调整问题的表述方式",
                    "sources": [],
                    "model": settings.DEEPSEEK_MODEL,
                    "response_time": time.time() - start_time,
                    "retrieval_time": retrieval_time,
                    "tokens_used": None
                }
            
            # Step 2: Build context from search results
            context_chunks = [
                {
                    "content": result.content,
                    "source": f"{result.document_name} (相似度: {result.similarity_score:.2f})",
                    "metadata": {
                        "document_id": result.document_id,
                        "chunk_index": result.chunk_index,
                        "score": result.similarity_score
                    }
                }
                for result in filtered_results
            ]
            
            # Step 3: Generate answer
            generation_start = time.time()
            
            # Build prompt with conversation context
            prompt = llm_service.build_rag_prompt(question, context_chunks, context)
            
            if stream:
                # For streaming, we need to handle differently
                generation_result = llm_service.generate(
                    prompt=prompt,
                    temperature=temp,
                    max_tokens=tokens,
                    stream=False  # Get full response first
                )
                generation_time = time.time() - generation_start
            else:
                generation_result = llm_service.generate(
                    prompt=prompt,
                    temperature=temp,
                    max_tokens=tokens
                )
                generation_time = time.time() - generation_start
            
            # Step 4: Format sources for response
            sources = [
                {
                    "id": result.chunk_id,
                    "document_id": result.document_id,
                    "filename": result.document_name,
                    "chunk_index": result.chunk_index,
                    "similarity_score": result.similarity_score,
                    "content": result.content[:200] + "..." if len(result.content) > 200 else result.content
                }
                for result in filtered_results
            ]
            
            total_time = time.time() - start_time
            
            return {
                "question": question,
                "answer": generation_result["content"],
                "sources": sources,
                "model": generation_result["model"],
                "response_time": total_time,
                "retrieval_time": retrieval_time,
                "generation_time": generation_time,
                "tokens_used": generation_result.get("tokens_used")
            }
            
        except Exception as e:
            logger.error(f"RAG processing failed: {e}")
            raise
    
    async def ask_stream(
        self,
        question: str,
        top_k: Optional[int] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream answer generation
        
        Args:
            question: User question
            top_k: Number of context chunks to retrieve
            
        Yields:
            Dictionary chunks with partial results
        """
        k = top_k or self.config.top_k
        
        # Retrieve documents
        search_results = vector_store.search_by_text(question, top_k=k)
        
        if not search_results:
            yield {
                "type": "error",
                "content": "抱歉，没有找到相关信息"
            }
            return
        
        # Build context
        context_chunks = [
            {
                "content": result.content,
                "source": result.document_name
            }
            for result in search_results
        ]
        
        prompt = llm_service.build_rag_prompt(question, context_chunks)
        
        # Stream generation
        yield {"type": "sources", "sources": search_results}
        
        async for chunk in llm_service.generate_stream(prompt):
            yield {"type": "content", "content": chunk}
    
    def update_config(self, config_dict: Dict[str, Any]):
        """
        Update RAG configuration
        
        Args:
            config_dict: Configuration updates
        """
        valid_configs = {
            'top_k': int,
            'temperature': float,
            'max_tokens': int,
            'chunk_size': int,
            'chunk_overlap': int,
            'similarity_threshold': float
        }
        
        for key, value in config_dict.items():
            if key in valid_configs and hasattr(self.config, key):
                # Validate value type
                try:
                    setattr(self.config, key, valid_configs[key](value))
                    logger.info(f"Updated config: {key} = {value}")
                except (ValueError, TypeError) as e:
                    logger.error(f"Invalid config value for {key}: {e}")
        
        # Also update global settings
        if 'top_k' in config_dict:
            settings.DEFAULT_TOP_K = config_dict['top_k']
        if 'temperature' in config_dict:
            settings.TEMPERATURE = config_dict['temperature']
        if 'max_tokens' in config_dict:
            settings.MAX_TOKENS = config_dict['max_tokens']
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get current RAG configuration
        
        Returns:
            Dictionary with current configuration
        """
        return {
            "rag_config": {
                "top_k": self.config.top_k,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "similarity_threshold": self.config.similarity_threshold
            },
            "embedding_config": {
                "model": settings.EMBEDDING_MODEL,
                "dimension": settings.EMBEDDING_DIMENSION
            },
            "llm_config": {
                "model": settings.DEEPSEEK_MODEL,
                "provider": "DeepSeek"
            },
            "document_config": {
                "chunk_size": self.config.chunk_size,
                "chunk_overlap": self.config.chunk_overlap,
                "supported_formats": settings.SUPPORTED_FORMATS
            }
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system statistics
        
        Returns:
            Dictionary with system stats
        """
        vector_stats = vector_store.get_stats()
        embedding_info = embedding_service.get_embedding_info()
        model_info = llm_service.get_model_info()
        
        return {
            "vector_store": vector_stats,
            "embedding_model": embedding_info,
            "llm": model_info,
            "config": self.config.to_dict(),
            "timestamp": datetime.now().isoformat()
        }


# Singleton instance
rag_service = RAGService()
