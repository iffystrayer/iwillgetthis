"""Base classes for LLM providers"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel
from enum import Enum
import time
import logging

logger = logging.getLogger(__name__)

class ProviderStatus(str, Enum):
    """Provider health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class ProviderCapabilities(BaseModel):
    """Capabilities supported by a provider"""
    supports_streaming: bool = False
    supports_function_calling: bool = False
    supports_vision: bool = False
    supports_embeddings: bool = False
    max_context_length: int = 4000
    supports_json_mode: bool = False
    supports_system_messages: bool = True

class LLMResponse(BaseModel):
    """Standardized LLM response"""
    content: str
    provider: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None
    response_time: float = 0.0
    cost: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class ProviderMetrics(BaseModel):
    """Provider performance and usage metrics"""
    requests_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    avg_response_time: float = 0.0
    last_request_time: Optional[float] = None
    status: ProviderStatus = ProviderStatus.UNKNOWN
    error_rate: float = 0.0

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.enabled = config.get("enabled", False)
        self.metrics = ProviderMetrics()
        self.capabilities = ProviderCapabilities()
        self._last_health_check = 0
        self._health_check_interval = 300  # 5 minutes
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the provider"""
        pass
    
    @abstractmethod
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> LLMResponse:
        """Generate a completion from messages"""
        pass
    
    @abstractmethod
    async def health_check(self) -> ProviderStatus:
        """Check provider health"""
        pass
    
    async def get_capabilities(self) -> ProviderCapabilities:
        """Get provider capabilities"""
        return self.capabilities
    
    async def get_metrics(self) -> ProviderMetrics:
        """Get provider metrics"""
        return self.metrics
    
    def is_healthy(self) -> bool:
        """Check if provider is healthy"""
        return self.metrics.status == ProviderStatus.HEALTHY
    
    def should_check_health(self) -> bool:
        """Check if health check is due"""
        current_time = time.time()
        return (current_time - self._last_health_check) > self._health_check_interval
    
    async def update_metrics(self, response: LLMResponse, success: bool = True):
        """Update provider metrics"""
        self.metrics.requests_count += 1
        self.metrics.last_request_time = time.time()
        
        if success:
            self.metrics.success_count += 1
            if response.usage:
                self.metrics.total_tokens += response.usage.get("total_tokens", 0)
            if response.cost:
                self.metrics.total_cost += response.cost
            
            # Update average response time
            total_time = self.metrics.avg_response_time * (self.metrics.success_count - 1)
            self.metrics.avg_response_time = (total_time + response.response_time) / self.metrics.success_count
        else:
            self.metrics.failure_count += 1
        
        # Calculate error rate
        if self.metrics.requests_count > 0:
            self.metrics.error_rate = self.metrics.failure_count / self.metrics.requests_count
    
    async def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for token usage (override in specific providers)"""
        return 0.0
    
    def __str__(self) -> str:
        return f"{self.name} (status: {self.metrics.status})"