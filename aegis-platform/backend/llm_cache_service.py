"""LLM Response Caching Service using Redis"""

import asyncio
import hashlib
import json
import logging
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta

import redis.asyncio as redis
from config import settings
from ai_providers import LLMResponse

logger = logging.getLogger(__name__)

class LLMCacheService:
    """Redis-based caching service for LLM responses"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = False
        self.default_ttl = settings.LLM_CACHE_TTL_HOURS * 3600  # Convert hours to seconds
        self.cache_hit_count = 0
        self.cache_miss_count = 0
        self._initialization_lock = asyncio.Lock()
        self._initialized = False
        
        # Cache key prefixes for different types of requests
        self.key_prefixes = {
            "risk_analysis": "llm_cache:risk:",
            "evidence_analysis": "llm_cache:evidence:",
            "control_narrative": "llm_cache:control:",
            "assessment": "llm_cache:assessment:",
            "general": "llm_cache:general:"
        }
        
    async def initialize(self) -> bool:
        """Initialize Redis connection"""
        async with self._initialization_lock:
            if self._initialized:
                return self.enabled
                
            try:
                if not settings.ENABLE_LLM_CACHING:
                    logger.info("LLM caching disabled in configuration")
                    return False
                
                # Initialize Redis connection
                self.redis_client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB_CACHE,
                    password=settings.REDIS_PASSWORD,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                
                # Test Redis connection
                await self.redis_client.ping()
                
                # Set up cache statistics key
                await self.redis_client.hset(
                    "llm_cache:stats",
                    mapping={
                        "initialized_at": datetime.utcnow().isoformat(),
                        "hits": "0",
                        "misses": "0",
                        "hit_rate": "0.0"
                    }
                )
                
                self.enabled = True
                self._initialized = True
                
                logger.info(f"LLM cache service initialized with Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
                
                # Start background cleanup task
                asyncio.create_task(self._cleanup_expired_keys())
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to initialize LLM cache service: {e}")
                self.enabled = False
                return False
    
    def _generate_cache_key(
        self,
        messages: List[Dict[str, str]],
        task_type: str = "general",
        provider: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate a unique cache key for the request"""
        # Create a deterministic hash of the request parameters
        cache_data = {
            "messages": messages,
            "task_type": task_type,
            "provider": provider,
            "kwargs": {k: v for k, v in kwargs.items() if k in ["temperature", "max_tokens", "model"]}
        }
        
        # Convert to JSON string and hash
        cache_str = json.dumps(cache_data, sort_keys=True)
        cache_hash = hashlib.sha256(cache_str.encode()).hexdigest()
        
        # Use appropriate prefix based on task type
        prefix = self.key_prefixes.get(task_type, self.key_prefixes["general"])
        return f"{prefix}{cache_hash}"
    
    async def get_cached_response(
        self,
        messages: List[Dict[str, str]],
        task_type: str = "general",
        provider: Optional[str] = None,
        **kwargs
    ) -> Optional[LLMResponse]:
        """Get cached LLM response if available"""
        if not self.enabled or not self.redis_client:
            return None
            
        try:
            cache_key = self._generate_cache_key(messages, task_type, provider, **kwargs)
            
            # Get cached data
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                # Cache hit
                await self._update_cache_stats("hit")
                
                # Deserialize and reconstruct LLMResponse
                data = json.loads(cached_data)
                response = LLMResponse(
                    content=data["content"],
                    provider=data["provider"],
                    model=data["model"],
                    usage=data.get("usage", {}),
                    cost=data.get("cost"),
                    response_time=data.get("response_time"),
                    cached=True,
                    cache_hit_time=time.time()
                )
                
                logger.debug(f"Cache hit for task_type: {task_type}")
                return response
            else:
                # Cache miss
                await self._update_cache_stats("miss")
                return None
                
        except Exception as e:
            logger.warning(f"Error retrieving from cache: {e}")
            return None
    
    async def cache_response(
        self,
        messages: List[Dict[str, str]],
        response: LLMResponse,
        task_type: str = "general",
        provider: Optional[str] = None,
        ttl_hours: Optional[int] = None,
        **kwargs
    ) -> bool:
        """Cache an LLM response"""
        if not self.enabled or not self.redis_client:
            return False
            
        try:
            cache_key = self._generate_cache_key(messages, task_type, provider, **kwargs)
            
            # Serialize response data
            cache_data = {
                "content": response.content,
                "provider": response.provider,
                "model": response.model,
                "usage": response.usage or {},
                "cost": response.cost,
                "response_time": response.response_time,
                "cached_at": time.time(),
                "task_type": task_type
            }
            
            # Determine TTL
            ttl = ttl_hours * 3600 if ttl_hours else self.default_ttl
            
            # Different TTL for different task types
            if task_type == "risk_analysis":
                ttl = 24 * 3600  # 24 hours for risk analysis
            elif task_type == "evidence_analysis":
                ttl = 12 * 3600  # 12 hours for evidence analysis
            elif task_type == "control_narrative":
                ttl = 48 * 3600  # 48 hours for control narratives (more stable)
            elif task_type == "assessment":
                ttl = 6 * 3600   # 6 hours for assessments (more dynamic)
            
            # Cache the response
            await self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(cache_data)
            )
            
            logger.debug(f"Cached response for task_type: {task_type}, TTL: {ttl}s")
            return True
            
        except Exception as e:
            logger.warning(f"Error caching response: {e}")
            return False
    
    async def _update_cache_stats(self, event_type: str):
        """Update cache hit/miss statistics"""
        try:
            if event_type == "hit":
                self.cache_hit_count += 1
                await self.redis_client.hincrby("llm_cache:stats", "hits", 1)
            elif event_type == "miss":
                self.cache_miss_count += 1
                await self.redis_client.hincrby("llm_cache:stats", "misses", 1)
            
            # Update hit rate
            total_requests = self.cache_hit_count + self.cache_miss_count
            if total_requests > 0:
                hit_rate = self.cache_hit_count / total_requests
                await self.redis_client.hset("llm_cache:stats", "hit_rate", f"{hit_rate:.3f}")
                
        except Exception as e:
            logger.warning(f"Error updating cache stats: {e}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.enabled or not self.redis_client:
            return {"enabled": False}
            
        try:
            stats = await self.redis_client.hgetall("llm_cache:stats")
            
            # Get Redis info
            info = await self.redis_client.info("memory")
            
            # Count cache entries by type
            cache_counts = {}
            for prefix_name, prefix in self.key_prefixes.items():
                count = len(await self.redis_client.keys(f"{prefix}*"))
                cache_counts[prefix_name] = count
            
            return {
                "enabled": True,
                "hits": int(stats.get("hits", 0)),
                "misses": int(stats.get("misses", 0)),
                "hit_rate": float(stats.get("hit_rate", 0.0)),
                "memory_usage_mb": round(info.get("used_memory", 0) / (1024 * 1024), 2),
                "cache_entries_by_type": cache_counts,
                "total_entries": sum(cache_counts.values()),
                "initialized_at": stats.get("initialized_at")
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"enabled": True, "error": str(e)}
    
    async def invalidate_cache_by_pattern(self, pattern: str) -> int:
        """Invalidate cached responses matching a pattern"""
        if not self.enabled or not self.redis_client:
            return 0
            
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache entries matching pattern: {pattern}")
                return len(keys)
            return 0
            
        except Exception as e:
            logger.warning(f"Error invalidating cache: {e}")
            return 0
    
    async def clear_cache(self) -> bool:
        """Clear all cached LLM responses"""
        if not self.enabled or not self.redis_client:
            return False
            
        try:
            # Get all cache keys
            all_keys = []
            for prefix in self.key_prefixes.values():
                keys = await self.redis_client.keys(f"{prefix}*")
                all_keys.extend(keys)
            
            if all_keys:
                await self.redis_client.delete(*all_keys)
                logger.info(f"Cleared {len(all_keys)} cache entries")
            
            # Reset stats
            await self.redis_client.hset(
                "llm_cache:stats",
                mapping={
                    "hits": "0",
                    "misses": "0",
                    "hit_rate": "0.0",
                    "cleared_at": datetime.utcnow().isoformat()
                }
            )
            
            self.cache_hit_count = 0
            self.cache_miss_count = 0
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    async def _cleanup_expired_keys(self):
        """Background task to clean up expired keys and maintain cache health"""
        while self.enabled:
            try:
                # Sleep for 1 hour between cleanup runs
                await asyncio.sleep(3600)
                
                if not self.redis_client:
                    continue
                
                # Get memory info
                info = await self.redis_client.info("memory")
                memory_usage_mb = info.get("used_memory", 0) / (1024 * 1024)
                
                # If memory usage is high, be more aggressive about cleanup
                if memory_usage_mb > 500:  # > 500MB
                    logger.info(f"Cache memory usage high: {memory_usage_mb:.1f}MB, running cleanup")
                    
                    # Remove oldest entries if memory usage is too high
                    for prefix in self.key_prefixes.values():
                        keys = await self.redis_client.keys(f"{prefix}*")
                        if len(keys) > 1000:  # If more than 1000 entries per type
                            # Delete random 20% of keys to make space
                            import random
                            keys_to_delete = random.sample(keys, len(keys) // 5)
                            if keys_to_delete:
                                await self.redis_client.delete(*keys_to_delete)
                                logger.info(f"Cleaned up {len(keys_to_delete)} cache entries for memory management")
                
            except Exception as e:
                logger.warning(f"Error in cache cleanup task: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying

# Global cache service instance
llm_cache_service = LLMCacheService()