from typing import Optional, Dict, Any, List
import httpx
import asyncio
from .base import BaseLLMProvider

class TextGenWebUIProvider(BaseLLMProvider):
    """Text Generation WebUI provider for local AI services."""
    
    def __init__(self, base_url: str = "http://localhost:5000", model: str = "local-model"):
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=60.0)
        
    async def generate_completion(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate completion using Text Generation WebUI API."""
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            # Text Generation WebUI uses different API endpoints
            # Try the /v1/chat/completions endpoint first (OpenAI compatible)
            try:
                messages = [
                    {"role": "user", "content": prompt}
                ]
                
                if "system" in kwargs:
                    messages.insert(0, {"role": "system", "content": kwargs["system"]})
                
                data = {
                    "messages": messages,
                    "max_tokens": kwargs.get("max_tokens", 4096),
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                    "stream": False
                }
                
                response = await self.client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "text": result["choices"][0]["message"]["content"],
                        "model": self.model,
                        "usage": {
                            "input_tokens": result.get("usage", {}).get("prompt_tokens", 0),
                            "output_tokens": result.get("usage", {}).get("completion_tokens", 0),
                            "total_tokens": result.get("usage", {}).get("total_tokens", 0)
                        },
                        "provider": "textgen_webui"
                    }
            except:
                pass
            
            # Fallback to /api/v1/generate endpoint
            data = {
                "prompt": prompt,
                "max_new_tokens": kwargs.get("max_tokens", 4096),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
                "do_sample": True,
                "stop": kwargs.get("stop", [])
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/generate",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                raise Exception(f"Text Generation WebUI API error: {response.status_code} - {response.text}")
                
            result = response.json()
            
            # Extract generated text
            generated_text = result.get("results", [{}])[0].get("text", "")
            
            return {
                "text": generated_text,
                "model": self.model,
                "usage": {
                    "input_tokens": len(prompt.split()),  # Approximate
                    "output_tokens": len(generated_text.split()),  # Approximate
                    "total_tokens": len(prompt.split()) + len(generated_text.split())
                },
                "provider": "textgen_webui"
            }
            
        except Exception as e:
            raise Exception(f"Text Generation WebUI completion failed: {str(e)}")
            
    async def generate_embeddings(self, texts: List[str], **kwargs) -> Dict[str, Any]:
        """Text Generation WebUI doesn't typically support embeddings."""
        raise NotImplementedError("Text Generation WebUI doesn't support embeddings")
        
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Text Generation WebUI API."""
        try:
            test_response = await self.generate_completion(
                "Hello, please respond with 'Connection successful'.",
                max_tokens=50
            )
            return {
                "status": "success",
                "message": "Text Generation WebUI connection successful",
                "response": test_response["text"]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Text Generation WebUI connection failed: {str(e)}"
            }
            
    def get_capabilities(self) -> Dict[str, Any]:
        """Get provider capabilities."""
        return {
            "supports_streaming": True,
            "supports_function_calling": False,
            "supports_vision": False,
            "supports_embeddings": False,
            "max_context_length": 4096,
            "supports_json_mode": False,
            "supports_system_messages": True
        }
        
    async def cleanup(self):
        """Clean up resources."""
        if self.client:
            await self.client.aclose()
