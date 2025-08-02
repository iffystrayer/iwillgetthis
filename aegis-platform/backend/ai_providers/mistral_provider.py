from typing import Optional, Dict, Any, List
import httpx
import asyncio
from .base import BaseLLMProvider

class MistralProvider(BaseLLMProvider):
    """Mistral AI provider for AI services."""
    
    def __init__(self, api_key: str, model: str = "mistral-large-latest"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.mistral.ai/v1"
        self.client = httpx.AsyncClient(timeout=60.0)
        
    async def generate_completion(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate completion using Mistral API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            if "system" in kwargs:
                messages.insert(0, {"role": "system", "content": kwargs["system"]})
            
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", 4096),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9)
            }
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                raise Exception(f"Mistral API error: {response.status_code} - {response.text}")
                
            result = response.json()
            
            return {
                "text": result["choices"][0]["message"]["content"],
                "model": self.model,
                "usage": {
                    "input_tokens": result["usage"]["prompt_tokens"],
                    "output_tokens": result["usage"]["completion_tokens"],
                    "total_tokens": result["usage"]["total_tokens"]
                },
                "provider": "mistral"
            }
            
        except Exception as e:
            raise Exception(f"Mistral completion failed: {str(e)}")
            
    async def generate_embeddings(self, texts: List[str], **kwargs) -> Dict[str, Any]:
        """Generate embeddings using Mistral API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": kwargs.get("embedding_model", "mistral-embed"),
                "input": texts
            }
            
            response = await self.client.post(
                f"{self.base_url}/embeddings",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                raise Exception(f"Mistral embeddings API error: {response.status_code} - {response.text}")
                
            result = response.json()
            
            return {
                "embeddings": [item["embedding"] for item in result["data"]],
                "model": data["model"],
                "usage": {
                    "total_tokens": result["usage"]["total_tokens"]
                },
                "provider": "mistral"
            }
            
        except Exception as e:
            raise Exception(f"Mistral embeddings failed: {str(e)}")
        
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Mistral API."""
        try:
            test_response = await self.generate_completion(
                "Hello, please respond with 'Connection successful'.",
                max_tokens=50
            )
            return {
                "status": "success",
                "message": "Mistral connection successful",
                "response": test_response["text"]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Mistral connection failed: {str(e)}"
            }
            
    def get_capabilities(self) -> Dict[str, Any]:
        """Get provider capabilities."""
        return {
            "supports_streaming": True,
            "supports_function_calling": True,
            "supports_vision": False,
            "supports_embeddings": True,
            "max_context_length": 32000,
            "supports_json_mode": True,
            "supports_system_messages": True
        }
        
    async def cleanup(self):
        """Clean up resources."""
        if self.client:
            await self.client.aclose()
