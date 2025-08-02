from typing import Optional, Dict, Any, List
import httpx
import asyncio
from .base import BaseLLMProvider

class LMStudioProvider(BaseLLMProvider):
    """LM Studio provider for local AI services."""
    
    def __init__(self, base_url: str = "http://localhost:1234/v1", model: str = "local-model"):
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=60.0)
        
    async def generate_completion(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate completion using LM Studio API (OpenAI-compatible)."""
        try:
            headers = {
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
                "top_p": kwargs.get("top_p", 0.9),
                "stream": False
            }
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                raise Exception(f"LM Studio API error: {response.status_code} - {response.text}")
                
            result = response.json()
            
            return {
                "text": result["choices"][0]["message"]["content"],
                "model": self.model,
                "usage": {
                    "input_tokens": result.get("usage", {}).get("prompt_tokens", 0),
                    "output_tokens": result.get("usage", {}).get("completion_tokens", 0),
                    "total_tokens": result.get("usage", {}).get("total_tokens", 0)
                },
                "provider": "lmstudio"
            }
            
        except Exception as e:
            raise Exception(f"LM Studio completion failed: {str(e)}")
            
    async def generate_embeddings(self, texts: List[str], **kwargs) -> Dict[str, Any]:
        """Generate embeddings using LM Studio API."""
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "model": kwargs.get("embedding_model", self.model),
                "input": texts
            }
            
            response = await self.client.post(
                f"{self.base_url}/embeddings",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                raise Exception(f"LM Studio embeddings API error: {response.status_code} - {response.text}")
                
            result = response.json()
            
            return {
                "embeddings": [item["embedding"] for item in result["data"]],
                "model": data["model"],
                "usage": {
                    "total_tokens": result.get("usage", {}).get("total_tokens", 0)
                },
                "provider": "lmstudio"
            }
            
        except Exception as e:
            raise Exception(f"LM Studio embeddings failed: {str(e)}")
        
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to LM Studio API."""
        try:
            test_response = await self.generate_completion(
                "Hello, please respond with 'Connection successful'.",
                max_tokens=50
            )
            return {
                "status": "success",
                "message": "LM Studio connection successful",
                "response": test_response["text"]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"LM Studio connection failed: {str(e)}"
            }
            
    def get_capabilities(self) -> Dict[str, Any]:
        """Get provider capabilities."""
        return {
            "supports_streaming": True,
            "supports_function_calling": False,
            "supports_vision": False,
            "supports_embeddings": True,
            "max_context_length": 4096,
            "supports_json_mode": False,
            "supports_system_messages": True
        }
        
    async def cleanup(self):
        """Clean up resources."""
        if self.client:
            await self.client.aclose()
