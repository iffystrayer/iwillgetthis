from typing import Optional, Dict, Any, List
import httpx
import asyncio
from .base import BaseLLMProvider

class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider for AI services."""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1"
        self.client = httpx.AsyncClient(timeout=60.0)
        
    async def generate_completion(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate completion using Anthropic Claude API."""
        try:
            headers = {
                "x-api-key": self.api_key,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            # Convert prompt to messages format
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            data = {
                "model": self.model,
                "max_tokens": kwargs.get("max_tokens", 4096),
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9)
            }
            
            if "system" in kwargs:
                data["system"] = kwargs["system"]
                
            response = await self.client.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                raise Exception(f"Anthropic API error: {response.status_code} - {response.text}")
                
            result = response.json()
            
            return {
                "text": result["content"][0]["text"],
                "model": self.model,
                "usage": {
                    "input_tokens": result["usage"]["input_tokens"],
                    "output_tokens": result["usage"]["output_tokens"],
                    "total_tokens": result["usage"]["input_tokens"] + result["usage"]["output_tokens"]
                },
                "provider": "anthropic"
            }
            
        except Exception as e:
            raise Exception(f"Anthropic completion failed: {str(e)}")
            
    async def generate_embeddings(self, texts: List[str], **kwargs) -> Dict[str, Any]:
        """Anthropic doesn't provide embeddings - raise not implemented."""
        raise NotImplementedError("Anthropic doesn't provide embeddings API")
        
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Anthropic API."""
        try:
            test_response = await self.generate_completion(
                "Hello, please respond with 'Connection successful'.",
                max_tokens=50
            )
            return {
                "status": "success",
                "message": "Anthropic connection successful",
                "response": test_response["text"]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Anthropic connection failed: {str(e)}"
            }
            
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        model_info = {
            "claude-3-5-sonnet-20241022": {
                "name": "Claude 3.5 Sonnet",
                "context_length": 200000,
                "supports_vision": True,
                "supports_function_calling": True
            },
            "claude-3-5-haiku-20241022": {
                "name": "Claude 3.5 Haiku",
                "context_length": 200000,
                "supports_vision": True,
                "supports_function_calling": True
            },
            "claude-3-opus-20240229": {
                "name": "Claude 3 Opus",
                "context_length": 200000,
                "supports_vision": True,
                "supports_function_calling": True
            }
        }
        
        return model_info.get(self.model, {
            "name": self.model,
            "context_length": 200000,
            "supports_vision": False,
            "supports_function_calling": False
        })
        
    def get_capabilities(self) -> Dict[str, Any]:
        """Get provider capabilities."""
        return {
            "supports_streaming": True,
            "supports_function_calling": True,
            "supports_vision": True,
            "supports_embeddings": False,
            "max_context_length": 200000,
            "supports_json_mode": True,
            "supports_system_messages": True
        }
        
    async def cleanup(self):
        """Clean up resources."""
        if self.client:
            await self.client.aclose()
