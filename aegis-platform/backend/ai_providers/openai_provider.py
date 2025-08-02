"""OpenAI Provider"""

import asyncio
import time
from typing import Dict, Any, List
from openai import OpenAI, AsyncOpenAI
from .base import BaseLLMProvider, LLMResponse, ProviderStatus, ProviderCapabilities
import logging

logger = logging.getLogger(__name__)

class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("openai", config)
        self.client = None
        self.async_client = None
        self.api_key = config.get("api_key", "")
        self.organization = config.get("organization", "")
        self.model = config.get("model", "gpt-4")
        self.max_tokens = config.get("max_tokens", 4000)
        self.temperature = config.get("temperature", 0.3)
        
        # Set capabilities
        self.capabilities = ProviderCapabilities(
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=True,
            supports_embeddings=True,
            max_context_length=128000 if "gpt-4" in self.model else 16000,
            supports_json_mode=True,
            supports_system_messages=True
        )
    
    async def initialize(self) -> bool:
        """Initialize OpenAI client"""
        try:
            if not self.api_key:
                logger.warning("OpenAI API key not configured")
                return False
            
            kwargs = {"api_key": self.api_key}
            if self.organization:
                kwargs["organization"] = self.organization
            
            self.client = OpenAI(**kwargs)
            self.async_client = AsyncOpenAI(**kwargs)
            
            # Test connection
            status = await self.health_check()
            self.enabled = status == ProviderStatus.HEALTHY
            
            logger.info(f"OpenAI provider initialized: {self.enabled}")
            return self.enabled
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {e}")
            self.metrics.status = ProviderStatus.UNHEALTHY
            return False
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> LLMResponse:
        """Generate completion using OpenAI"""
        start_time = time.time()
        
        try:
            if not self.async_client:
                raise Exception("OpenAI client not initialized")
            
            # Prepare parameters
            params = {
                "model": kwargs.get("model", self.model),
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
            }
            
            # Add optional parameters
            if kwargs.get("response_format") == "json":
                params["response_format"] = {"type": "json_object"}
            
            if kwargs.get("functions"):
                params["functions"] = kwargs["functions"]
            
            response = await self.async_client.chat.completions.create(**params)
            
            response_time = time.time() - start_time
            content = response.choices[0].message.content or ""
            
            # Calculate cost
            usage = response.usage
            cost = await self.estimate_cost(
                usage.prompt_tokens if usage else 0,
                usage.completion_tokens if usage else 0
            )
            
            llm_response = LLMResponse(
                content=content,
                provider=self.name,
                model=params["model"],
                usage={
                    "prompt_tokens": usage.prompt_tokens if usage else 0,
                    "completion_tokens": usage.completion_tokens if usage else 0,
                    "total_tokens": usage.total_tokens if usage else 0
                } if usage else None,
                finish_reason=response.choices[0].finish_reason,
                response_time=response_time,
                cost=cost
            )
            
            await self.update_metrics(llm_response, success=True)
            return llm_response
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"OpenAI completion error: {e}")
            
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
        """Check OpenAI health"""
        try:
            if not self.client:
                return ProviderStatus.UNHEALTHY
            
            # Simple test request
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            self.metrics.status = ProviderStatus.HEALTHY
            self._last_health_check = time.time()
            return ProviderStatus.HEALTHY
            
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            self.metrics.status = ProviderStatus.UNHEALTHY
            return ProviderStatus.UNHEALTHY
    
    async def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for OpenAI"""
        # Current OpenAI pricing (update as needed)
        if "gpt-4" in self.model:
            if "turbo" in self.model:
                input_cost = input_tokens * 0.00001  # $0.01 per 1K tokens
                output_cost = output_tokens * 0.00003  # $0.03 per 1K tokens
            else:
                input_cost = input_tokens * 0.00003  # $0.03 per 1K tokens
                output_cost = output_tokens * 0.00006  # $0.06 per 1K tokens
        else:  # GPT-3.5
            input_cost = input_tokens * 0.0000005  # $0.0005 per 1K tokens
            output_cost = output_tokens * 0.0000015  # $0.0015 per 1K tokens
        
        return input_cost + output_cost