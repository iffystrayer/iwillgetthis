"""Azure OpenAI Provider"""

import asyncio
import time
from typing import Dict, Any, List
from openai import AzureOpenAI, AsyncAzureOpenAI
from .base import BaseLLMProvider, LLMResponse, ProviderStatus, ProviderCapabilities
import logging

logger = logging.getLogger(__name__)

class AzureOpenAIProvider(BaseLLMProvider):
    """Azure OpenAI provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("azure_openai", config)
        self.client = None
        self.async_client = None
        self.api_key = config.get("api_key", "")
        self.endpoint = config.get("endpoint", "")
        self.api_version = config.get("api_version", "2024-02-15-preview")
        self.deployment_name = config.get("deployment_name", "gpt-4")
        self.max_tokens = config.get("max_tokens", 4000)
        self.temperature = config.get("temperature", 0.3)
        
        # Set capabilities
        self.capabilities = ProviderCapabilities(
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=True,
            supports_embeddings=True,
            max_context_length=32000 if "gpt-4" in self.deployment_name else 16000,
            supports_json_mode=True,
            supports_system_messages=True
        )
    
    async def initialize(self) -> bool:
        """Initialize Azure OpenAI client"""
        try:
            if not self.api_key or not self.endpoint:
                logger.warning("Azure OpenAI API key or endpoint not configured")
                return False
            
            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )
            
            self.async_client = AsyncAzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )
            
            # Test connection
            status = await self.health_check()
            self.enabled = status == ProviderStatus.HEALTHY
            
            logger.info(f"Azure OpenAI provider initialized: {self.enabled}")
            return self.enabled
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI: {e}")
            self.metrics.status = ProviderStatus.UNHEALTHY
            return False
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> LLMResponse:
        """Generate completion using Azure OpenAI"""
        start_time = time.time()
        
        try:
            if not self.async_client:
                raise Exception("Azure OpenAI client not initialized")
            
            # Prepare parameters
            params = {
                "model": self.deployment_name,
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
            
            # Calculate cost (approximate)
            usage = response.usage
            cost = await self.estimate_cost(
                usage.prompt_tokens if usage else 0,
                usage.completion_tokens if usage else 0
            )
            
            llm_response = LLMResponse(
                content=content,
                provider=self.name,
                model=self.deployment_name,
                usage={
                    "prompt_tokens": usage.prompt_tokens if usage else 0,
                    "completion_tokens": usage.completion_tokens if usage else 0,
                    "total_tokens": usage.total_tokens if usage else 0
                } if usage else None,
                finish_reason=response.choices[0].finish_reason,
                response_time=response_time,
                cost=cost,
                metadata={"api_version": self.api_version}
            )
            
            await self.update_metrics(llm_response, success=True)
            return llm_response
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Azure OpenAI completion error: {e}")
            
            error_response = LLMResponse(
                content=f"Error: {str(e)}",
                provider=self.name,
                model=self.deployment_name,
                response_time=response_time,
                metadata={"error": str(e)}
            )
            
            await self.update_metrics(error_response, success=False)
            raise e
    
    async def health_check(self) -> ProviderStatus:
        """Check Azure OpenAI health"""
        try:
            if not self.client:
                return ProviderStatus.UNHEALTHY
            
            # Simple test request
            response = await self.async_client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            self.metrics.status = ProviderStatus.HEALTHY
            self._last_health_check = time.time()
            return ProviderStatus.HEALTHY
            
        except Exception as e:
            logger.error(f"Azure OpenAI health check failed: {e}")
            self.metrics.status = ProviderStatus.UNHEALTHY
            return ProviderStatus.UNHEALTHY
    
    async def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for Azure OpenAI"""
        # Approximate pricing (update with actual rates)
        if "gpt-4" in self.deployment_name:
            input_cost = input_tokens * 0.00003  # $0.03 per 1K tokens
            output_cost = output_tokens * 0.00006  # $0.06 per 1K tokens
        else:  # GPT-3.5
            input_cost = input_tokens * 0.0000015  # $0.0015 per 1K tokens
            output_cost = output_tokens * 0.000002  # $0.002 per 1K tokens
        
        return input_cost + output_cost