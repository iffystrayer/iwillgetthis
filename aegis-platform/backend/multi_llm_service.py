"""Multi-LLM Provider Service"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional, Union
from config import settings
from ai_providers import (
    BaseLLMProvider, LLMResponse, ProviderStatus,
    AzureOpenAIProvider, OpenAIProvider, GeminiProvider,
    DeepSeekProvider, OllamaProvider, LiteLLMProvider,
    OpenRouterProvider, CustomProvider
)
from .ai_providers.anthropic_provider import AnthropicProvider
from .ai_providers.cohere_provider import CohereProvider
from .ai_providers.mistral_provider import MistralProvider
from .ai_providers.huggingface_provider import HuggingFaceProvider
from .ai_providers.together_provider import TogetherProvider
from .ai_providers.lmstudio_provider import LMStudioProvider
from .ai_providers.textgen_provider import TextGenWebUIProvider

logger = logging.getLogger(__name__)

class MultiLLMService:
    """Multi-provider LLM service with failover and load balancing"""
    
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.provider_priorities: List[str] = []
        self.fallback_chain: List[str] = []
        self.enabled = False
        self.cost_tracking = {}
        self.daily_limits = {}
        self._initialization_lock = asyncio.Lock()
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize all configured LLM providers"""
        async with self._initialization_lock:
            if self._initialized:
                return self.enabled
            
            try:
                if not settings.ENABLE_AI_FEATURES:
                    logger.info("AI features disabled in configuration")
                    return False
                
                # Initialize providers based on configuration
                await self._initialize_providers()
                
                # Set up provider priorities and fallback chain
                await self._setup_provider_chain()
                
                # Initialize cost tracking
                await self._initialize_cost_tracking()
                
                # Start background health checks
                asyncio.create_task(self._health_check_loop())
                
                self.enabled = len([p for p in self.providers.values() if p.enabled]) > 0
                self._initialized = True
                
                logger.info(f"Multi-LLM service initialized with {len(self.providers)} providers, {len([p for p in self.providers.values() if p.enabled])} enabled")
                return self.enabled
                
            except Exception as e:
                logger.error(f"Failed to initialize Multi-LLM service: {e}")
                return False
    
    async def _initialize_providers(self):
        """Initialize all configured providers"""
        # Azure OpenAI
        if settings.ENABLE_AZURE_OPENAI:
            azure_config = {
                "api_key": settings.AZURE_OPENAI_API_KEY,
                "endpoint": settings.AZURE_OPENAI_ENDPOINT,
                "api_version": settings.AZURE_OPENAI_API_VERSION,
                "deployment_name": settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                "max_tokens": settings.AZURE_OPENAI_MAX_TOKENS,
                "temperature": settings.AZURE_OPENAI_TEMPERATURE,
                "enabled": True
            }
            self.providers["azure_openai"] = AzureOpenAIProvider(azure_config)
        
        # OpenAI
        if settings.ENABLE_OPENAI:
            openai_config = {
                "api_key": settings.OPENAI_API_KEY,
                "organization": settings.OPENAI_ORGANIZATION,
                "model": settings.OPENAI_MODEL,
                "max_tokens": settings.OPENAI_MAX_TOKENS,
                "temperature": settings.OPENAI_TEMPERATURE,
                "enabled": True
            }
            self.providers["openai"] = OpenAIProvider(openai_config)
        
        # Google Gemini
        if settings.ENABLE_GEMINI:
            gemini_config = {
                "api_key": settings.GEMINI_API_KEY,
                "model": settings.GEMINI_MODEL,
                "max_tokens": settings.GEMINI_MAX_TOKENS,
                "temperature": settings.GEMINI_TEMPERATURE,
                "project_id": settings.GEMINI_PROJECT_ID,
                "location": settings.GEMINI_LOCATION,
                "enabled": True
            }
            self.providers["gemini"] = GeminiProvider(gemini_config)
        
        # DeepSeek
        if settings.ENABLE_DEEPSEEK:
            deepseek_config = {
                "api_key": settings.DEEPSEEK_API_KEY,
                "base_url": settings.DEEPSEEK_BASE_URL,
                "model": settings.DEEPSEEK_MODEL,
                "max_tokens": settings.DEEPSEEK_MAX_TOKENS,
                "temperature": settings.DEEPSEEK_TEMPERATURE,
                "enabled": True
            }
            self.providers["deepseek"] = DeepSeekProvider(deepseek_config)
        
        # Ollama
        if settings.ENABLE_OLLAMA:
            ollama_config = {
                "base_url": settings.OLLAMA_BASE_URL,
                "model": settings.OLLAMA_MODEL,
                "max_tokens": settings.OLLAMA_MAX_TOKENS,
                "temperature": settings.OLLAMA_TEMPERATURE,
                "enabled": True
            }
            self.providers["ollama"] = OllamaProvider(ollama_config)
        
        # LiteLLM
        if settings.ENABLE_LITELLM:
            litellm_config = {
                "api_key": settings.LITELLM_API_KEY,
                "model": settings.LITELLM_MODEL,
                "max_tokens": settings.LITELLM_MAX_TOKENS,
                "temperature": settings.LITELLM_TEMPERATURE,
                "enabled": True
            }
            self.providers["litellm"] = LiteLLMProvider(litellm_config)
        
        # OpenRouter
        if settings.ENABLE_OPENROUTER:
            openrouter_config = {
                "api_key": settings.OPENROUTER_API_KEY,
                "model": settings.OPENROUTER_MODEL,
                "max_tokens": settings.OPENROUTER_MAX_TOKENS,
                "temperature": settings.OPENROUTER_TEMPERATURE,
                "site_url": settings.OPENROUTER_SITE_URL,
                "app_name": settings.OPENROUTER_APP_NAME,
                "enabled": True
            }
            self.providers["openrouter"] = OpenRouterProvider(openrouter_config)
        
        # Anthropic Claude
        if hasattr(settings, 'ENABLE_ANTHROPIC') and settings.ENABLE_ANTHROPIC:
            if hasattr(settings, 'ANTHROPIC_API_KEY') and settings.ANTHROPIC_API_KEY:
                self.providers["anthropic"] = AnthropicProvider(
                    api_key=settings.ANTHROPIC_API_KEY,
                    model=getattr(settings, 'ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
                )
        
        # Cohere
        if hasattr(settings, 'ENABLE_COHERE') and settings.ENABLE_COHERE:
            if hasattr(settings, 'COHERE_API_KEY') and settings.COHERE_API_KEY:
                self.providers["cohere"] = CohereProvider(
                    api_key=settings.COHERE_API_KEY,
                    model=getattr(settings, 'COHERE_MODEL', 'command-r-plus')
                )
        
        # Mistral AI
        if hasattr(settings, 'ENABLE_MISTRAL') and settings.ENABLE_MISTRAL:
            if hasattr(settings, 'MISTRAL_API_KEY') and settings.MISTRAL_API_KEY:
                self.providers["mistral"] = MistralProvider(
                    api_key=settings.MISTRAL_API_KEY,
                    model=getattr(settings, 'MISTRAL_MODEL', 'mistral-large-latest')
                )
        
        # Hugging Face
        if hasattr(settings, 'ENABLE_HUGGINGFACE') and settings.ENABLE_HUGGINGFACE:
            if hasattr(settings, 'HUGGINGFACE_API_KEY') and settings.HUGGINGFACE_API_KEY:
                self.providers["huggingface"] = HuggingFaceProvider(
                    api_key=settings.HUGGINGFACE_API_KEY,
                    model=getattr(settings, 'HUGGINGFACE_MODEL', 'meta-llama/Meta-Llama-3.1-70B-Instruct')
                )
        
        # Together AI
        if hasattr(settings, 'ENABLE_TOGETHER') and settings.ENABLE_TOGETHER:
            if hasattr(settings, 'TOGETHER_API_KEY') and settings.TOGETHER_API_KEY:
                self.providers["together"] = TogetherProvider(
                    api_key=settings.TOGETHER_API_KEY,
                    model=getattr(settings, 'TOGETHER_MODEL', 'meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo')
                )
        
        # LM Studio
        if hasattr(settings, 'ENABLE_LMSTUDIO') and settings.ENABLE_LMSTUDIO:
            self.providers["lmstudio"] = LMStudioProvider(
                base_url=getattr(settings, 'LMSTUDIO_BASE_URL', 'http://localhost:1234/v1'),
                model=getattr(settings, 'LMSTUDIO_MODEL', 'local-model')
            )
        
        # Text Generation WebUI
        if hasattr(settings, 'ENABLE_TEXTGEN_WEBUI') and settings.ENABLE_TEXTGEN_WEBUI:
            self.providers["textgen_webui"] = TextGenWebUIProvider(
                base_url=getattr(settings, 'TEXTGEN_WEBUI_BASE_URL', 'http://localhost:5000'),
                model=getattr(settings, 'TEXTGEN_WEBUI_MODEL', 'local-model')
            )

        # Custom endpoints
        if settings.CUSTOM_LLM_ENDPOINTS:
            try:
                custom_endpoints = json.loads(settings.CUSTOM_LLM_ENDPOINTS)
                for name, config in custom_endpoints.items():
                    config["enabled"] = True
                    self.providers[f"custom_{name}"] = CustomProvider(f"custom_{name}", config)
            except (json.JSONDecodeError, Exception) as e:
                logger.error(f"Failed to parse custom LLM endpoints: {e}")
        
        # Initialize all providers
        for name, provider in self.providers.items():
            try:
                initialized = await provider.initialize()
                logger.info(f"Provider {name}: {'initialized' if initialized else 'failed to initialize'}")
            except Exception as e:
                logger.error(f"Failed to initialize provider {name}: {e}")
    
    async def _setup_provider_chain(self):
        """Set up provider priorities and fallback chain"""
        # Set primary provider
        if settings.DEFAULT_LLM_PROVIDER in self.providers:
            self.provider_priorities = [settings.DEFAULT_LLM_PROVIDER]
        else:
            self.provider_priorities = []
        
        # Add fallback providers
        fallback_providers = settings.FALLBACK_LLM_PROVIDERS or []
        for provider in fallback_providers:
            if provider in self.providers and provider not in self.provider_priorities:
                self.provider_priorities.append(provider)
        
        # Add any remaining enabled providers
        for name, provider in self.providers.items():
            if provider.enabled and name not in self.provider_priorities:
                self.provider_priorities.append(name)
        
        logger.info(f"Provider chain: {' -> '.join(self.provider_priorities)}")
    
    async def _initialize_cost_tracking(self):
        """Initialize cost tracking and daily limits"""
        if settings.ENABLE_COST_TRACKING:
            # Parse daily limits
            if settings.PROVIDER_DAILY_LIMITS:
                try:
                    self.daily_limits = json.loads(settings.PROVIDER_DAILY_LIMITS)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse provider daily limits")
            
            # Initialize cost tracking for each provider
            for provider_name in self.providers.keys():
                self.cost_tracking[provider_name] = {
                    "daily_cost": 0.0,
                    "daily_requests": 0,
                    "last_reset": time.time()
                }
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        task_type: str = "general",
        preferred_provider: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate completion with automatic failover"""
        if not self.enabled:
            raise Exception("Multi-LLM service not enabled or no providers available")
        
        # Determine provider order
        provider_order = await self._get_provider_order(task_type, preferred_provider)
        
        last_error = None
        
        for provider_name in provider_order:
            if provider_name not in self.providers:
                continue
            
            provider = self.providers[provider_name]
            
            # Check if provider is healthy and within limits
            if not await self._can_use_provider(provider_name):
                continue
            
            try:
                # Generate completion
                response = await provider.generate_completion(messages, **kwargs)
                
                # Update cost tracking
                await self._update_cost_tracking(provider_name, response)
                
                return response
                
            except Exception as e:
                last_error = e
                logger.warning(f"Provider {provider_name} failed: {e}")
                continue
        
        # All providers failed
        raise Exception(f"All providers failed. Last error: {last_error}")
    
    async def _get_provider_order(
        self,
        task_type: str,
        preferred_provider: Optional[str]
    ) -> List[str]:
        """Get provider order based on task type and preferences"""
        # Start with preferred provider if specified
        if preferred_provider and preferred_provider in self.providers:
            order = [preferred_provider]
            # Add other providers as fallbacks
            order.extend([p for p in self.provider_priorities if p != preferred_provider])
            return order
        
        # Task-specific provider selection
        if task_type == "reasoning":
            # Prefer reasoning-optimized models
            reasoning_providers = ["deepseek", "openai", "azure_openai", "gemini"]
            order = [p for p in reasoning_providers if p in self.providers]
            order.extend([p for p in self.provider_priorities if p not in order])
            return order
        
        elif task_type == "creative":
            # Prefer creative models
            creative_providers = ["openai", "gemini", "azure_openai"]
            order = [p for p in creative_providers if p in self.providers]
            order.extend([p for p in self.provider_priorities if p not in order])
            return order
        
        elif task_type == "cost_sensitive":
            # Prefer cost-effective models
            cost_effective = ["ollama", "deepseek", "gemini"]
            order = [p for p in cost_effective if p in self.providers]
            order.extend([p for p in self.provider_priorities if p not in order])
            return order
        
        # Default order
        return self.provider_priorities
    
    async def _can_use_provider(self, provider_name: str) -> bool:
        """Check if provider can be used (health, cost limits, etc.)"""
        if provider_name not in self.providers:
            return False
        
        provider = self.providers[provider_name]
        
        # Check if provider is healthy
        if not provider.is_healthy():
            return False
        
        # Check cost limits
        if settings.ENABLE_COST_TRACKING and provider_name in self.cost_tracking:
            tracking = self.cost_tracking[provider_name]
            
            # Check daily limit
            if provider_name in self.daily_limits:
                if tracking["daily_cost"] >= self.daily_limits[provider_name]:
                    return False
            
            # Check monthly budget
            total_cost = sum(t["daily_cost"] for t in self.cost_tracking.values())
            if total_cost >= settings.MONTHLY_AI_BUDGET:
                return False
        
        return True
    
    async def _update_cost_tracking(self, provider_name: str, response: LLMResponse):
        """Update cost tracking for provider"""
        if not settings.ENABLE_COST_TRACKING or provider_name not in self.cost_tracking:
            return
        
        tracking = self.cost_tracking[provider_name]
        
        # Reset daily tracking if needed
        current_time = time.time()
        if current_time - tracking["last_reset"] > 86400:  # 24 hours
            tracking["daily_cost"] = 0.0
            tracking["daily_requests"] = 0
            tracking["last_reset"] = current_time
        
        # Update tracking
        if response.cost:
            tracking["daily_cost"] += response.cost
        tracking["daily_requests"] += 1
    
    async def _health_check_loop(self):
        """Background health check loop"""
        while True:
            try:
                await asyncio.sleep(settings.LLM_HEALTH_CHECK_INTERVAL)
                
                for name, provider in self.providers.items():
                    if provider.should_check_health():
                        try:
                            await provider.health_check()
                        except Exception as e:
                            logger.error(f"Health check failed for {name}: {e}")
                            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
    
    async def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {}
        
        for name, provider in self.providers.items():
            metrics = await provider.get_metrics()
            capabilities = await provider.get_capabilities()
            
            status[name] = {
                "enabled": provider.enabled,
                "status": metrics.status.value,
                "requests_count": metrics.requests_count,
                "success_rate": (metrics.success_count / metrics.requests_count * 100) if metrics.requests_count > 0 else 0,
                "avg_response_time": metrics.avg_response_time,
                "total_cost": metrics.total_cost,
                "capabilities": capabilities.dict(),
                "cost_tracking": self.cost_tracking.get(name, {})
            }
        
        return status
    
    async def get_recommended_provider(self, task_type: str = "general") -> Optional[str]:
        """Get recommended provider for a task type"""
        provider_order = await self._get_provider_order(task_type, None)
        
        for provider_name in provider_order:
            if await self._can_use_provider(provider_name):
                return provider_name
        
        return None
    
    def is_enabled(self) -> bool:
        """Check if the multi-LLM service is enabled"""
        return self.enabled

# Global multi-LLM service instance
multi_llm_service = MultiLLMService()