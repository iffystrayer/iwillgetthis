"""Ollama Provider for Local LLM Deployment"""

import asyncio
import time
from typing import Dict, Any, List
import httpx
from .base import BaseLLMProvider, LLMResponse, ProviderStatus, ProviderCapabilities
import logging

logger = logging.getLogger(__name__)

class OllamaProvider(BaseLLMProvider):
    """Ollama provider for local LLM deployment"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("ollama", config)
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.model = config.get("model", "llama3.1")
        self.max_tokens = config.get("max_tokens", 4000)
        self.temperature = config.get("temperature", 0.3)
        
        # Set capabilities (varies by model)
        self.capabilities = ProviderCapabilities(
            supports_streaming=True,
            supports_function_calling=False,  # Depends on model
            supports_vision=False,  # Depends on model
            supports_embeddings=True,
            max_context_length=8000,  # Depends on model
            supports_json_mode=True,
            supports_system_messages=True
        )
    
    async def initialize(self) -> bool:
        """Initialize Ollama connection"""
        try:
            # Check if Ollama is running and model is available
            status = await self.health_check()
            
            # Try to pull the model if it's not available
            if status != ProviderStatus.HEALTHY:
                await self._ensure_model_available()
                status = await self.health_check()
            
            self.enabled = status == ProviderStatus.HEALTHY
            
            logger.info(f"Ollama provider initialized: {self.enabled}")
            return self.enabled
            
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            self.metrics.status = ProviderStatus.UNHEALTHY
            return False
    
    async def _ensure_model_available(self):
        """Ensure the model is pulled and available"""
        try:
            url = f"{self.base_url}/api/pull"
            request_data = {"name": self.model}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=request_data,
                    timeout=300.0  # Model pulling can take time
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully pulled model {self.model}")
                
        except Exception as e:
            logger.warning(f"Failed to pull model {self.model}: {e}")
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> LLMResponse:
        """Generate completion using Ollama"""
        start_time = time.time()
        
        try:
            # Convert messages to prompt format for Ollama
            prompt = self._convert_messages_to_prompt(messages)
            
            request_data = {
                "model": kwargs.get("model", self.model),
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", self.temperature),
                    "num_predict": kwargs.get("max_tokens", self.max_tokens)
                }
            }
            
            # JSON mode support
            if kwargs.get("response_format") == "json":
                request_data["format"] = "json"
            
            url = f"{self.base_url}/api/generate"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=request_data,
                    timeout=60.0
                )
                
                response.raise_for_status()
                result = response.json()
            
            response_time = time.time() - start_time
            content = result.get("response", "")
            
            # Estimate token usage (Ollama doesn't always provide this)
            prompt_tokens = len(prompt.split()) * 1.3  # Rough estimation
            completion_tokens = len(content.split()) * 1.3
            total_tokens = prompt_tokens + completion_tokens
            
            # Ollama is free for local use
            cost = 0.0
            
            llm_response = LLMResponse(
                content=content,
                provider=self.name,
                model=request_data["model"],
                usage={
                    "prompt_tokens": int(prompt_tokens),
                    "completion_tokens": int(completion_tokens),
                    "total_tokens": int(total_tokens)
                },
                finish_reason="stop" if result.get("done") else "length",
                response_time=response_time,
                cost=cost,
                metadata={
                    "local_model": True,
                    "total_duration": result.get("total_duration"),
                    "load_duration": result.get("load_duration")
                }
            )
            
            await self.update_metrics(llm_response, success=True)
            return llm_response
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Ollama completion error: {e}")
            
            error_response = LLMResponse(
                content=f"Error: {str(e)}",
                provider=self.name,
                model=self.model,
                response_time=response_time,
                metadata={"error": str(e)}
            )
            
            await self.update_metrics(error_response, success=False)
            raise e
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to a single prompt"""
        prompt_parts = []
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"Human: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)
    
    async def health_check(self) -> ProviderStatus:
        """Check Ollama health"""
        try:
            # Check if Ollama is running
            url = f"{self.base_url}/api/tags"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5.0)
                response.raise_for_status()
                
                models = response.json().get("models", [])
                model_names = [model["name"] for model in models]
                
                # Check if our model is available
                if not any(self.model in name for name in model_names):
                    self.metrics.status = ProviderStatus.DEGRADED
                    return ProviderStatus.DEGRADED
            
            # Test generation
            test_data = {
                "model": self.model,
                "prompt": "Hello",
                "stream": False,
                "options": {"num_predict": 5}
            }
            
            url = f"{self.base_url}/api/generate"
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=test_data,
                    timeout=10.0
                )
                response.raise_for_status()
            
            self.metrics.status = ProviderStatus.HEALTHY
            self._last_health_check = time.time()
            return ProviderStatus.HEALTHY
            
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            self.metrics.status = ProviderStatus.UNHEALTHY
            return ProviderStatus.UNHEALTHY
    
    async def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for Ollama (free for local use)"""
        return 0.0  # Local models are free to use