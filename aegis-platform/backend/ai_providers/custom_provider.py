"""Custom Provider for OpenAI-Compatible Endpoints"""

import asyncio
import time
from typing import Dict, Any, List
import httpx
from .base import BaseLLMProvider, LLMResponse, ProviderStatus, ProviderCapabilities
import logging

logger = logging.getLogger(__name__)

class CustomProvider(BaseLLMProvider):
    """Custom provider for OpenAI-compatible endpoints"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.base_url = config.get("base_url", "")
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "gpt-3.5-turbo")
        self.max_tokens = config.get("max_tokens", 4000)
        self.temperature = config.get("temperature", 0.3)
        self.auth_header = config.get("auth_header", "Authorization")
        self.auth_prefix = config.get("auth_prefix", "Bearer")
        
        # Set capabilities (configurable)
        self.capabilities = ProviderCapabilities(
            supports_streaming=config.get("supports_streaming", True),
            supports_function_calling=config.get("supports_function_calling", False),
            supports_vision=config.get("supports_vision", False),
            supports_embeddings=config.get("supports_embeddings", False),
            max_context_length=config.get("max_context_length", 4000),
            supports_json_mode=config.get("supports_json_mode", True),
            supports_system_messages=config.get("supports_system_messages", True)
        )
    
    async def initialize(self) -> bool:
        """Initialize custom provider"""
        try:
            if not self.base_url or not self.api_key:
                logger.warning(f"Custom provider {self.name}: base_url or api_key not configured")
                return False
            
            # Test connection
            status = await self.health_check()
            self.enabled = status == ProviderStatus.HEALTHY
            
            logger.info(f"Custom provider {self.name} initialized: {self.enabled}")
            return self.enabled
            
        except Exception as e:
            logger.error(f"Failed to initialize custom provider {self.name}: {e}")
            self.metrics.status = ProviderStatus.UNHEALTHY
            return False
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> LLMResponse:
        """Generate completion using custom endpoint"""
        start_time = time.time()
        
        try:
            # Prepare request data
            request_data = {
                "model": kwargs.get("model", self.model),
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
            }
            
            # Add optional parameters if supported
            if self.capabilities.supports_json_mode and kwargs.get("response_format") == "json":
                request_data["response_format"] = {"type": "json_object"}
            
            if self.capabilities.supports_function_calling and kwargs.get("functions"):
                request_data["functions"] = kwargs["functions"]
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                self.auth_header: f"{self.auth_prefix} {self.api_key}"
            }
            
            # Add custom headers if configured
            custom_headers = self.config.get("headers", {})
            headers.update(custom_headers)
            
            url = f"{self.base_url.rstrip('/')}/v1/chat/completions"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=request_data,
                    timeout=60.0
                )
                
                response.raise_for_status()
                result = response.json()
            
            response_time = time.time() - start_time
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
                cost=cost,
                metadata={"custom_endpoint": self.base_url}
            )
            
            await self.update_metrics(llm_response, success=True)
            return llm_response
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Custom provider {self.name} completion error: {e}")
            
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
        """Check custom provider health"""
        try:
            # Test with a simple request
            request_data = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5
            }
            
            headers = {
                "Content-Type": "application/json",
                self.auth_header: f"{self.auth_prefix} {self.api_key}"
            }
            
            # Add custom headers if configured
            custom_headers = self.config.get("headers", {})
            headers.update(custom_headers)
            
            url = f"{self.base_url.rstrip('/')}/v1/chat/completions"
            
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
            logger.error(f"Custom provider {self.name} health check failed: {e}")
            self.metrics.status = ProviderStatus.UNHEALTHY
            return ProviderStatus.UNHEALTHY
    
    async def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for custom provider"""
        # Use configured cost rates or default estimation
        input_rate = self.config.get("input_cost_per_token", 0.00001)
        output_rate = self.config.get("output_cost_per_token", 0.00003)
        
        return (input_tokens * input_rate) + (output_tokens * output_rate)