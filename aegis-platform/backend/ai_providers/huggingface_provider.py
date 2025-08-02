from typing import Optional, Dict, Any, List
import httpx
import asyncio
from .base import BaseLLMProvider

class HuggingFaceProvider(BaseLLMProvider):
    """Hugging Face Inference provider for AI services."""
    
    def __init__(self, api_key: str, model: str = "meta-llama/Meta-Llama-3.1-70B-Instruct"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api-inference.huggingface.co"
        self.client = httpx.AsyncClient(timeout=60.0)
        
    async def generate_completion(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate completion using Hugging Face Inference API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": kwargs.get("max_tokens", 4096),
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                    "return_full_text": False
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/models/{self.model}",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                raise Exception(f"Hugging Face API error: {response.status_code} - {response.text}")
                
            result = response.json()
            
            # Handle both single response and list response formats
            if isinstance(result, list):
                generated_text = result[0]["generated_text"]
            else:
                generated_text = result["generated_text"]
            
            return {
                "text": generated_text,
                "model": self.model,
                "usage": {
                    "input_tokens": len(prompt.split()),  # Approximate
                    "output_tokens": len(generated_text.split()),  # Approximate
                    "total_tokens": len(prompt.split()) + len(generated_text.split())
                },
                "provider": "huggingface"
            }
            
        except Exception as e:
            raise Exception(f"Hugging Face completion failed: {str(e)}")
            
    async def generate_embeddings(self, texts: List[str], **kwargs) -> Dict[str, Any]:
        """Generate embeddings using Hugging Face Inference API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Use a sentence transformer model for embeddings
            embedding_model = kwargs.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
            
            embeddings = []
            for text in texts:
                data = {"inputs": text}
                
                response = await self.client.post(
                    f"{self.base_url}/models/{embedding_model}",
                    headers=headers,
                    json=data
                )
                
                if response.status_code != 200:
                    raise Exception(f"Hugging Face embeddings API error: {response.status_code} - {response.text}")
                    
                embedding = response.json()
                embeddings.append(embedding)
            
            return {
                "embeddings": embeddings,
                "model": embedding_model,
                "usage": {
                    "total_tokens": sum(len(text.split()) for text in texts)
                },
                "provider": "huggingface"
            }
            
        except Exception as e:
            raise Exception(f"Hugging Face embeddings failed: {str(e)}")
        
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Hugging Face API."""
        try:
            test_response = await self.generate_completion(
                "Hello, please respond with 'Connection successful'.",
                max_tokens=50
            )
            return {
                "status": "success",
                "message": "Hugging Face connection successful",
                "response": test_response["text"]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Hugging Face connection failed: {str(e)}"
            }
            
    def get_capabilities(self) -> Dict[str, Any]:
        """Get provider capabilities."""
        return {
            "supports_streaming": False,
            "supports_function_calling": False,
            "supports_vision": False,
            "supports_embeddings": True,
            "max_context_length": 4096,
            "supports_json_mode": False,
            "supports_system_messages": False
        }
        
    async def cleanup(self):
        """Clean up resources."""
        if self.client:
            await self.client.aclose()
