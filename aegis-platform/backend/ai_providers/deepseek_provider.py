"""DeepSeek Provider"""

import asyncio
import time
from typing import Dict, Any, List
import httpx
from .base import BaseLLMProvider, LLMResponse, ProviderStatus, ProviderCapabilities
import logging

logger = logging.getLogger(__name__)

class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("deepseek", config)
        self.api_key = config.get("api_key", "")
        self.base_url = config.get("base_url", "https://api.deepseek.com")
        self.model = config.get("model", "deepseek-chat")
        self.max_tokens = config.get("max_tokens", 4000)
        self.temperature = config.get("temperature", 0.3)
        
        # Set capabilities
        self.capabilities = ProviderCapabilities(
            supports_streaming=True,
            supports_function_calling=False,  # DeepSeek may not support this
            supports_vision=False,
            supports_embeddings=False,
            max_context_length=32000,
            supports_json_mode=True,
            supports_system_messages=True
        )
    
    async def initialize(self) -> bool:
        """Initialize DeepSeek client"""
        try:
            if not self.api_key:
                logger.warning("DeepSeek API key not configured")
                return False
            
            # Test connection
            status = await self.health_check()
            self.enabled = status == ProviderStatus.HEALTHY
            
            logger.info(f"DeepSeek provider initialized: {self.enabled}")
            return self.enabled
            
        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek: {e}")
            self.metrics.status = ProviderStatus.UNHEALTHY
            return False
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> LLMResponse:
        """Generate completion using DeepSeek"""
        start_time = time.time()
        
        try:
            # Prepare request data
            request_data = {
                "model": kwargs.get("model", self.model),
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "stream": False
            }
            
            # JSON mode support
            if kwargs.get("response_format") == "json":
                request_data["response_format"] = {"type": "json_object"}
            
            url = f"{self.base_url}/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=request_data,
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
            
            response_time = time.time() - start_time
            
            # Extract content
            content = result["choices"][0]["message"]["content"]
            
            # Extract usage information
            usage = result.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)
            
            # Calculate cost
            cost = await self.estimate_cost(prompt_tokens, completion_tokens)
            
            llm_response = LLMResponse(
                content=content,
                provider=self.name,
                model=request_data["model"],
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                },
                finish_reason=result["choices"][0].get("finish_reason"),
                response_time=response_time,
                cost=cost
            )
            
            await self.update_metrics(llm_response, success=True)
            return llm_response
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"DeepSeek completion error: {e}")
            
            error_response = LLMResponse(
                content=f"Error: {str(e)}",
                provider=self.name,
                model=self.model,
                response_time=response_time,
                metadata={"error": str(e)}
            )
            
            await self.update_metrics(error_response, success=False)
            raise e
    
    async def health_check(self) -> ProviderStatus:
        """Check DeepSeek health"""
        try:
            # Simple test request
            request_data = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5,
                "stream": False
            }
            
            url = f"{self.base_url}/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=request_data,
                    timeout=10.0
                )
                
                response.raise_for_status()
            
            self.metrics.status = ProviderStatus.HEALTHY
            self._last_health_check = time.time()
            return ProviderStatus.HEALTHY
            
        except Exception as e:
            logger.error(f"DeepSeek health check failed: {e}")
            self.metrics.status = ProviderStatus.UNHEALTHY
            return ProviderStatus.UNHEALTHY
    
    async def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for DeepSeek"""
        # DeepSeek pricing (update as needed)
        input_cost = input_tokens * 0.00000014   # $0.14 per 1M tokens
        output_cost = output_tokens * 0.00000028  # $0.28 per 1M tokens
        
        return input_cost + output_cost