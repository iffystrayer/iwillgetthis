"""OpenRouter Provider for Model Marketplace"""

import asyncio
import time
from typing import Dict, Any, List
import httpx
from .base import BaseLLMProvider, LLMResponse, ProviderStatus, ProviderCapabilities
import logging

logger = logging.getLogger(__name__)

class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter provider for accessing multiple models through one API"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("openrouter", config)
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "anthropic/claude-3-sonnet")
        self.max_tokens = config.get("max_tokens", 4000)
        self.temperature = config.get("temperature", 0.3)
        self.site_url = config.get("site_url", "")
        self.app_name = config.get("app_name", "Aegis Risk Platform")
        self.base_url = "https://openrouter.ai/api/v1"
        
        # Set capabilities (varies by model)
        self.capabilities = ProviderCapabilities(
            supports_streaming=True,
            supports_function_calling=True,  # Depends on model
            supports_vision=False,  # Depends on model
            supports_embeddings=False,
            max_context_length=200000,  # Varies by model
            supports_json_mode=True,
            supports_system_messages=True
        )
    
    async def initialize(self) -> bool:
        """Initialize OpenRouter connection"""
        try:
            if not self.api_key:
                logger.warning("OpenRouter API key not configured")
                return False
            
            # Test connection
            status = await self.health_check()
            self.enabled = status == ProviderStatus.HEALTHY
            
            logger.info(f"OpenRouter provider initialized: {self.enabled}")
            return self.enabled
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenRouter: {e}")
            self.metrics.status = ProviderStatus.UNHEALTHY
            return False
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> LLMResponse:
        """Generate completion using OpenRouter"""
        start_time = time.time()
        
        try:
            # Prepare request data
            request_data = {
                "model": kwargs.get("model", self.model),
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
            }
            
            # Add optional parameters
            if kwargs.get("response_format") == "json":
                request_data["response_format"] = {"type": "json_object"}
            
            if kwargs.get("functions"):
                request_data["functions"] = kwargs["functions"]
            
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": self.site_url,  # Optional, for including your app on openrouter.ai rankings
                "X-Title": self.app_name,  # Optional, shows in rankings on openrouter.ai
            }
            
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
            
            # Calculate cost (OpenRouter provides this in response)
            cost = 0.0
            if "cost" in result:
                cost = float(result["cost"])
            else:
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
                metadata={
                    "model_id": result.get("id"),
                    "generation_id": result.get("generation_id")
                }
            )
            
            await self.update_metrics(llm_response, success=True)
            return llm_response
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"OpenRouter completion error: {e}")
            
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
        """Check OpenRouter health"""
        try:
            # Test with a simple request
            request_data = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5
            }
            
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": self.site_url,
                "X-Title": self.app_name,
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
            logger.error(f"OpenRouter health check failed: {e}")
            self.metrics.status = ProviderStatus.UNHEALTHY
            return ProviderStatus.UNHEALTHY
    
    async def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for OpenRouter (varies by model)"""
        # OpenRouter pricing varies greatly by model
        # This is a rough estimate - actual costs are provided in responses
        model_lower = self.model.lower()
        
        if "claude-3" in model_lower:
            input_cost = input_tokens * 0.000015   # ~$15 per 1M tokens
            output_cost = output_tokens * 0.000075  # ~$75 per 1M tokens
        elif "gpt-4" in model_lower:
            input_cost = input_tokens * 0.00003     # ~$30 per 1M tokens
            output_cost = output_tokens * 0.00006   # ~$60 per 1M tokens
        elif "mixtral" in model_lower:
            input_cost = input_tokens * 0.00000027  # ~$0.27 per 1M tokens
            output_cost = output_tokens * 0.00000027 # ~$0.27 per 1M tokens
        else:
            # Default estimation
            input_cost = input_tokens * 0.00001
            output_cost = output_tokens * 0.00003
        
        return input_cost + output_cost