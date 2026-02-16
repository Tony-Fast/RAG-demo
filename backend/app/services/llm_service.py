"""
LLM Service
Handles DeepSeek API integration for text generation
"""

import time
import logging
from typing import AsyncGenerator, Optional, Dict, Any, List
from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from app.core.config import settings
from app.services.token_usage_monitor import token_usage_monitor

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for LLM text generation using DeepSeek API
    """
    
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.api_base = settings.DEEPSEEK_API_BASE
        self.model = settings.DEEPSEEK_MODEL
        
        # Synchronous client
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base,
            timeout=60.0
        )
        
        # Asynchronous client
        self.async_client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.api_base,
            timeout=60.0
        )
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate text using DeepSeek API
        
        Args:
            prompt: Input prompt
            temperature: Response creativity (0-2)
            max_tokens: Maximum tokens in response
            stream: Enable streaming response
            
        Returns:
            Dictionary with generated text and metadata
        """
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的AI助手。请根据提供的上下文信息回答用户的问题。如果上下文没有相关信息，请如实告知用户。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                presence_penalty=0.0,
                frequency_penalty=0.0
            )
            
            response_time = time.time() - start_time
            
            # Extract response
            content = response.choices[0].message.content
            
            # Get usage information
            usage = response.usage
            tokens_used = usage.total_tokens if usage else None
            
            # Record token usage
            if tokens_used:
                token_usage_monitor.add_token_usage(tokens_used)
            
            logger.info(f"LLM generation completed in {response_time:.2f}s, tokens: {tokens_used}")
            
            return {
                "content": content,
                "model": self.model,
                "response_time": response_time,
                "tokens_used": tokens_used,
                "finish_reason": response.choices[0].finish_reason
            }
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise
    
    async def generate_async(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Asynchronous text generation
        
        Args:
            prompt: Input prompt
            temperature: Response creativity
            max_tokens: Maximum tokens in response
            
        Returns:
            Dictionary with generated text and metadata
        """
        start_time = time.time()
        
        try:
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的AI助手。请根据提供的上下文信息回答用户的问题。如果上下文没有相关信息，请如实告知用户。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            response_time = time.time() - start_time
            
            content = response.choices[0].message.content
            usage = response.usage
            tokens_used = usage.total_tokens if usage else None
            
            # Record token usage
            if tokens_used:
                token_usage_monitor.add_token_usage(tokens_used)
            
            return {
                "content": content,
                "model": self.model,
                "response_time": response_time,
                "tokens_used": tokens_used
            }
            
        except Exception as e:
            logger.error(f"Async LLM generation failed: {e}")
            raise
    
    async def generate_stream(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> AsyncGenerator[str, None]:
        """
        Stream text generation
        
        Args:
            prompt: Input prompt
            temperature: Response creativity
            max_tokens: Maximum tokens in response
            
        Yields:
            Text chunks as they are generated
        """
        try:
            stream = await self.async_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的AI助手。请根据提供的上下文信息回答用户的问题。如果上下文没有相关信息，请如实告知用户。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                
            # Record token usage from the final chunk
            if hasattr(stream, 'usage') and stream.usage:
                tokens_used = stream.usage.total_tokens
                if tokens_used:
                    token_usage_monitor.add_token_usage(tokens_used)
                    logger.info(f"Stream generation completed, tokens: {tokens_used}")
                    
        except Exception as e:
            logger.error(f"Stream generation failed: {e}")
            raise
    
    def build_rag_prompt(
        self,
        question: str,
        context_chunks: List[Dict[str, str]],
        context: Optional[List[Dict[str, str]]] = None,
        system_prompt: str = None
    ) -> str:
        """
        Build a prompt for RAG with context
        
        Args:
            question: User question
            context_chunks: List of context dictionaries with 'content' and 'source'
            context: Conversation context (list of previous messages)
            system_prompt: Optional custom system prompt
            
        Returns:
            Complete prompt string
        """
        # Build context section
        context_text = "\n\n".join([
            f"[来源 {i+1}] {chunk['content']}"
            for i, chunk in enumerate(context_chunks)
        ])
        
        # Add source attribution
        sources = "\n".join([
            f"[{i+1}] {chunk.get('source', '未知来源')}"
            for i, chunk in enumerate(context_chunks)
        ])
        
        # Add conversation history if provided
        conversation_history = ""
        if context and len(context) > 0:
            conversation_history = "## 对话历史\n"
            for msg in context:
                role = "用户" if msg.get('role') == 'user' else "助手"
                conversation_history += f"{role}：{msg.get('content', '')}\n"
            conversation_history += "\n"
        
        # Build full prompt
        prompt = f"""## 上下文信息
以下是从知识库中检索到的相关信息：

{context_text}

---
信息来源：
{sources}

{conversation_history}## 用户问题
{question}

## 请根据以上上下文信息和对话历史回答用户问题。
请在回答时：
1. 清晰地回答用户的问题
2. 如果需要，可以引用上下文中的具体信息
3. 注明引用的来源编号
4. 考虑对话历史，确保回答的连贯性
5. 如果上下文中没有相关信息，请如实说明

## 回答：
"""
        
        return prompt
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the LLM model
        
        Returns:
            Dictionary with model information
        """
        return {
            "model": self.model,
            "api_base": self.api_base,
            "provider": "DeepSeek"
        }
    
    def check_api_health(self) -> bool:
        """
        Check if the API is accessible
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception as e:
            logger.error(f"API health check failed: {e}")
            return False


# Singleton instance
llm_service = LLMService()
