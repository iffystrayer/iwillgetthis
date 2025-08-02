"""LiteLLM Provider for Unified LLM Interface"""

import asyncio
import time
from typing import Dict, Any, List
from .base import BaseLLMProvider, LLMResponse, ProviderStatus, ProviderCapabilities
import logging

logger = logging.getLogger(__name__)

class LiteLLMProvider(BaseLLMProvider):
    """LiteLLM provider for unified interface to 100+ LLM providers"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("litellm", config)
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "gpt-4")
        self.max_tokens = config.get("max_tokens", 4000)
        self.temperature = config.get("temperature", 0.3)
        self.litellm = None
        
        # Set capabilities (varies by underlying model)
        self.capabilities = ProviderCapabilities(
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=False,  # Depends on underlying model
            supports_embeddings=True,
            max_context_length=32000,  # Depends on underlying model
            supports_json_mode=True,
            supports_system_messages=True
        )
    
    async def initialize(self) -> bool:
        """Initialize LiteLLM"""
        try:
            # Import LiteLLM (install with: pip install litellm)
            import litellm
            self.litellm = litellm
            
            # Set API key if provided
            if self.api_key:
                import os
                os.environ["OPENAI_API_KEY"] = self.api_key
            
            # Test connection
            status = await self.health_check()
            self.enabled = status == ProviderStatus.HEALTHY
            
            logger.info(f"LiteLLM provider initialized: {self.enabled}")
            return self.enabled
            
        except ImportError:
            logger.error("LiteLLM not installed. Install with: pip install litellm")
            self.metrics.status = ProviderStatus.UNHEALTHY
            return False
        except Exception as e:
            logger.error(f"Failed to initialize LiteLLM: {e}")
            self.metrics.status = ProviderStatus.UNHEALTHY
            return False
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> LLMResponse:
        """Generate completion using LiteLLM"""
        start_time = time.time()
        
        try:
            if not self.litellm:
                raise Exception("LiteLLM not initialized")
            
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
            
            # Use LiteLLM's completion function
            response = await self.litellm.acompletion(**params)
            
            response_time = time.time() - start_time
            content = response.choices[0].message.content or ""
            
            # Extract usage information
            usage = response.usage if hasattr(response, 'usage') else None
            prompt_tokens = usage.prompt_tokens if usage else 0
            completion_tokens = usage.completion_tokens if usage else 0
            total_tokens = usage.total_tokens if usage else 0
            
            # Calculate cost using LiteLLM's cost calculation
            cost = 0.0
            try:
                cost = self.litellm.completion_cost(
                    completion_response=response
                ) or 0.0
            except:
                cost = await self.estimate_cost(prompt_tokens, completion_tokens)
            
            llm_response = LLMResponse(
                content=content,
                provider=self.name,
                model=params["model"],
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                },
                finish_reason=response.choices[0].finish_reason,
                response_time=response_time,
                cost=cost,
                metadata={"underlying_provider": getattr(response, '_hidden_params', {}).get('model_provider', 'unknown')}
            )
            
            await self.update_metrics(llm_response, success=True)
            return llm_response
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"LiteLLM completion error: {e}")
            
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
        """Check LiteLLM health"""
        try:
            if not self.litellm:
                return ProviderStatus.UNHEALTHY
            
            # Simple test request
            response = await self.litellm.acompletion(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            self.metrics.status = ProviderStatus.HEALTHY
            self._last_health_check = time.time()
            return ProviderStatus.HEALTHY
            
        except Exception as e:
            logger.error(f"LiteLLM health check failed: {e}")
            self.metrics.status = ProviderStatus.UNHEALTHY
            return ProviderStatus.UNHEALTHY
    
    async def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost using LiteLLM's pricing info"""
        try:
            if self.litellm:
                # Use LiteLLM's cost calculation if available
                return self.litellm.cost_per_token(
                    model=self.model,
                    prompt_tokens=input_tokens,
                    completion_tokens=output_tokens
                ) or 0.0
        except:
            pass
        
        # Fallback to basic estimation
        return (input_tokens * 0.00003) + (output_tokens * 0.00006)