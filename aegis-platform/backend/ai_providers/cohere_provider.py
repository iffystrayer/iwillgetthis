from typing import Optional, Dict, Any, List
import httpx
import asyncio
from .base import BaseLLMProvider

class CohereProvider(BaseLLMProvider):
    """Cohere provider for AI services."""
    
    def __init__(self, api_key: str, model: str = "command-r-plus"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.cohere.ai/v1"
        self.client = httpx.AsyncClient(timeout=60.0)
        
    async def generate_completion(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate completion using Cohere API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "message": prompt,
                "max_tokens": kwargs.get("max_tokens", 4096),
                "temperature": kwargs.get("temperature", 0.7),
                "p": kwargs.get("top_p", 0.9)
            }
            
            if "system" in kwargs:
                data["preamble"] = kwargs["system"]
                
            response = await self.client.post(
                f"{self.base_url}/chat",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                raise Exception(f"Cohere API error: {response.status_code} - {response.text}")
                
            result = response.json()
            
            return {
                "text": result["text"],
                "model": self.model,
                "usage": {
                    "input_tokens": result.get("meta", {}).get("tokens", {}).get("input_tokens", 0),
                    "output_tokens": result.get("meta", {}).get("tokens", {}).get("output_tokens", 0),
                    "total_tokens": result.get("meta", {}).get("tokens", {}).get("input_tokens", 0) + result.get("meta", {}).get("tokens", {}).get("output_tokens", 0)
                },
                "provider": "cohere"
            }
            
        except Exception as e:
            raise Exception(f"Cohere completion failed: {str(e)}")
            
    async def generate_embeddings(self, texts: List[str], **kwargs) -> Dict[str, Any]:
        """Generate embeddings using Cohere API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "texts": texts,
                "model": kwargs.get("embedding_model", "embed-english-v3.0"),
                "input_type": kwargs.get("input_type", "search_document")
            }
            
            response = await self.client.post(
                f"{self.base_url}/embed",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                raise Exception(f"Cohere embeddings API error: {response.status_code} - {response.text}")
                
            result = response.json()
            
            return {
                "embeddings": result["embeddings"],
                "model": data["model"],
                "usage": {
                    "total_tokens": result.get("meta", {}).get("tokens", {}).get("input_tokens", 0)
                },
                "provider": "cohere"
            }
            
        except Exception as e:
            raise Exception(f"Cohere embeddings failed: {str(e)}")
        
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Cohere API."""
        try:
            test_response = await self.generate_completion(
                "Hello, please respond with 'Connection successful'.",
                max_tokens=50
            )
            return {
                "status": "success",
                "message": "Cohere connection successful",
                "response": test_response["text"]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Cohere connection failed: {str(e)}"
            }
            
    def get_capabilities(self) -> Dict[str, Any]:
        """Get provider capabilities."""
        return {
            "supports_streaming": True,
            "supports_function_calling": True,
            "supports_vision": False,
            "supports_embeddings": True,
            "max_context_length": 128000,
            "supports_json_mode": False,
            "supports_system_messages": True
        }
        
    async def cleanup(self):
        """Clean up resources."""
        if self.client:
            await self.client.aclose()
