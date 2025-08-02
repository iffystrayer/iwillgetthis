"""Google Gemini Provider"""

import asyncio
import time
import json
from typing import Dict, Any, List
import httpx
from .base import BaseLLMProvider, LLMResponse, ProviderStatus, ProviderCapabilities
import logging

logger = logging.getLogger(__name__)

class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("gemini", config)
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "gemini-1.5-pro")
        self.max_tokens = config.get("max_tokens", 4000)
        self.temperature = config.get("temperature", 0.3)
        self.project_id = config.get("project_id", "")
        self.location = config.get("location", "us-central1")
        self.base_url = "https://generativelanguage.googleapis.com"
        
        # Set capabilities
        self.capabilities = ProviderCapabilities(
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=True,
            supports_embeddings=False,
            max_context_length=1000000 if "1.5" in self.model else 30000,
            supports_json_mode=True,
            supports_system_messages=True
        )
    
    async def initialize(self) -> bool:
        """Initialize Gemini client"""
        try:
            if not self.api_key:
                logger.warning("Gemini API key not configured")
                return False
            
            # Test connection
            status = await self.health_check()
            self.enabled = status == ProviderStatus.HEALTHY
            
            logger.info(f"Gemini provider initialized: {self.enabled}")
            return self.enabled
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.metrics.status = ProviderStatus.UNHEALTHY
            return False
    
    def _convert_messages_to_gemini_format(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Convert OpenAI-style messages to Gemini format"""
        contents = []
        system_instruction = None
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                system_instruction = content
            elif role == "user":
                contents.append({
                    "role": "user",
                    "parts": [{"text": content}]
                })
            elif role == "assistant":
                contents.append({
                    "role": "model",
                    "parts": [{"text": content}]
                })
        
        request_data = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": self.max_tokens,
                "temperature": self.temperature,
            }
        }
        
        if system_instruction:
            request_data["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }
        
        return request_data
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> LLMResponse:
        """Generate completion using Gemini"""
        start_time = time.time()
        
        try:
            # Convert messages to Gemini format
            request_data = self._convert_messages_to_gemini_format(messages)
            
            # Override parameters if provided
            if "max_tokens" in kwargs:
                request_data["generationConfig"]["maxOutputTokens"] = kwargs["max_tokens"]
            if "temperature" in kwargs:
                request_data["generationConfig"]["temperature"] = kwargs["temperature"]
            
            # JSON mode support
            if kwargs.get("response_format") == "json":
                request_data["generationConfig"]["response_mime_type"] = "application/json"
            
            url = f"{self.base_url}/v1beta/models/{self.model}:generateContent"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers={
                        "Content-Type": "application/json",
                        "x-goog-api-key": self.api_key
                    },
                    json=request_data,
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
            
            response_time = time.time() - start_time
            
            # Extract content
            content = ""
            if "candidates" in result and result["candidates"]:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    content = candidate["content"]["parts"][0].get("text", "")
            
            # Extract usage information
            usage_metadata = result.get("usageMetadata", {})
            prompt_tokens = usage_metadata.get("promptTokenCount", 0)
            completion_tokens = usage_metadata.get("candidatesTokenCount", 0)
            total_tokens = usage_metadata.get("totalTokenCount", prompt_tokens + completion_tokens)
            
            # Calculate cost
            cost = await self.estimate_cost(prompt_tokens, completion_tokens)
            
            llm_response = LLMResponse(
                content=content,
                provider=self.name,
                model=self.model,
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                },
                finish_reason=result.get("candidates", [{}])[0].get("finishReason", "unknown"),
                response_time=response_time,
                cost=cost
            )
            
            await self.update_metrics(llm_response, success=True)
            return llm_response
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Gemini completion error: {e}")
            
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
        """Check Gemini health"""
        try:
            # Simple test request
            test_messages = [{"role": "user", "content": "Hello"}]
            request_data = self._convert_messages_to_gemini_format(test_messages)
            request_data["generationConfig"]["maxOutputTokens"] = 5
            
            url = f"{self.base_url}/v1beta/models/{self.model}:generateContent"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers={
                        "Content-Type": "application/json",
                        "x-goog-api-key": self.api_key
                    },
                    json=request_data,
                    timeout=10.0
                )
                
                response.raise_for_status()
            
            self.metrics.status = ProviderStatus.HEALTHY
            self._last_health_check = time.time()
            return ProviderStatus.HEALTHY
            
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            self.metrics.status = ProviderStatus.UNHEALTHY
            return ProviderStatus.UNHEALTHY
    
    async def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for Gemini"""
        # Gemini Pro pricing (update as needed)
        if "1.5" in self.model:
            # Gemini 1.5 Pro pricing
            if input_tokens <= 128000:
                input_cost = input_tokens * 0.00000125  # $1.25 per 1M tokens
            else:
                input_cost = input_tokens * 0.0000025   # $2.50 per 1M tokens
            output_cost = output_tokens * 0.000005      # $5.00 per 1M tokens
        else:
            # Gemini 1.0 Pro pricing
            input_cost = input_tokens * 0.0000005    # $0.50 per 1M tokens
            output_cost = output_tokens * 0.0000015   # $1.50 per 1M tokens
        
        return input_cost + output_cost