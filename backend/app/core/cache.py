"""High-performance caching layer for AI and database operations"""

import json
import hashlib
from typing import Optional, Any, Union
from datetime import timedelta
import redis.asyncio as redis
from functools import wraps
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class CacheService:
    """
    Redis-based caching service for performance optimization.
    Reduces AI API costs and improves response times.
    """

    def __init__(self):
        self.redis_client = None
        self.default_ttl = 3600  # 1 hour
        self.ai_cache_ttl = 7200  # 2 hours for expensive AI calls
        self._initialized = False

    async def initialize(self):
        """Initialize Redis connection"""
        if not self._initialized and settings.REDIS_URL:
            try:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    max_connections=50,
                    socket_keepalive=True,
                    socket_keepalive_options={
                        1: 1,  # TCP_KEEPIDLE
                        2: 3,  # TCP_KEEPINTL
                        3: 5,  # TCP_KEEPCNT
                    }
                )
                await self.redis_client.ping()
                self._initialized = True
                logger.info("Cache service initialized")
            except Exception as e:
                logger.error("Failed to initialize cache", error=str(e))
                self.redis_client = None

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            return None

        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error("Cache get failed", key=key, error=str(e))
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache"""
        if not self.redis_client:
            return False

        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value)
            await self.redis_client.set(key, serialized, ex=ttl)
            return True
        except Exception as e:
            logger.error("Cache set failed", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis_client:
            return False

        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error("Cache delete failed", key=key, error=str(e))
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.redis_client:
            return False

        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error("Cache exists check failed", key=key, error=str(e))
            return False

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter in cache"""
        if not self.redis_client:
            return None

        try:
            return await self.redis_client.incr(key, amount)
        except Exception as e:
            logger.error("Cache increment failed", key=key, error=str(e))
            return None

    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration on key"""
        if not self.redis_client:
            return False

        try:
            await self.redis_client.expire(key, ttl)
            return True
        except Exception as e:
            logger.error("Cache expire failed", key=key, error=str(e))
            return False

    def generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = {
            "args": args,
            "kwargs": kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    async def get_or_set(
        self,
        key: str,
        func,
        ttl: Optional[int] = None,
        *args,
        **kwargs
    ) -> Any:
        """Get from cache or compute and cache"""
        # Try to get from cache
        cached = await self.get(key)
        if cached is not None:
            logger.debug("Cache hit", key=key)
            return cached

        # Compute value
        logger.debug("Cache miss, computing", key=key)
        if asyncio.iscoroutinefunction(func):
            value = await func(*args, **kwargs)
        else:
            value = func(*args, **kwargs)

        # Store in cache
        await self.set(key, value, ttl)
        return value

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.redis_client:
            return 0

        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error("Cache clear pattern failed", pattern=pattern, error=str(e))
            return 0


class AIResponseCache:
    """
    Specialized cache for AI service responses.
    Reduces API costs and improves response times.
    """

    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        self.prefix = "ai:"

    async def get_claude_response(
        self,
        prompt: str,
        context: Optional[dict] = None
    ) -> Optional[dict]:
        """Get cached Claude response"""
        key = self._generate_claude_key(prompt, context)
        return await self.cache.get(key)

    async def set_claude_response(
        self,
        prompt: str,
        response: dict,
        context: Optional[dict] = None,
        ttl: int = 7200
    ):
        """Cache Claude response"""
        key = self._generate_claude_key(prompt, context)
        await self.cache.set(key, response, ttl)

    async def get_embedding(
        self,
        text: str,
        model: str = "text-embedding-3-small"
    ) -> Optional[list]:
        """Get cached embedding"""
        key = f"{self.prefix}embedding:{model}:{hashlib.md5(text.encode()).hexdigest()}"
        return await self.cache.get(key)

    async def set_embedding(
        self,
        text: str,
        embedding: list,
        model: str = "text-embedding-3-small",
        ttl: int = 86400  # 24 hours
    ):
        """Cache embedding"""
        key = f"{self.prefix}embedding:{model}:{hashlib.md5(text.encode()).hexdigest()}"
        await self.cache.set(key, embedding, ttl)

    def _generate_claude_key(self, prompt: str, context: Optional[dict]) -> str:
        """Generate cache key for Claude responses"""
        key_data = {
            "prompt": prompt,
            "context": context or {}
        }
        key_string = json.dumps(key_data, sort_keys=True)
        hash_key = hashlib.md5(key_string.encode()).hexdigest()
        return f"{self.prefix}claude:{hash_key}"


class QueryCache:
    """
    Database query result caching for performance.
    """

    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        self.prefix = "db:"

    async def get_query_result(
        self,
        query: str,
        params: dict
    ) -> Optional[Any]:
        """Get cached query result"""
        key = self._generate_query_key(query, params)
        return await self.cache.get(key)

    async def set_query_result(
        self,
        query: str,
        params: dict,
        result: Any,
        ttl: int = 300  # 5 minutes default
    ):
        """Cache query result"""
        key = self._generate_query_key(query, params)
        await self.cache.set(key, result, ttl)

    async def invalidate_for_model(self, model_name: str):
        """Invalidate all cached queries for a model"""
        pattern = f"{self.prefix}{model_name}:*"
        return await self.cache.clear_pattern(pattern)

    def _generate_query_key(self, query: str, params: dict) -> str:
        """Generate cache key for query"""
        key_data = {
            "query": query,
            "params": params
        }
        key_string = json.dumps(key_data, sort_keys=True)
        hash_key = hashlib.md5(key_string.encode()).hexdigest()
        return f"{self.prefix}query:{hash_key}"


# Cache decorator for async functions
def cache_result(ttl: int = 3600, prefix: str = "func:"):
    """
    Decorator to cache function results.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = cache_service

            # Generate cache key
            key_data = {
                "func": func.__name__,
                "args": str(args),
                "kwargs": str(kwargs)
            }
            key = prefix + hashlib.md5(
                json.dumps(key_data, sort_keys=True).encode()
            ).hexdigest()

            # Check cache
            cached = await cache.get(key)
            if cached is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            await cache.set(key, result, ttl)
            return result

        return wrapper
    return decorator


# Global cache instances
cache_service = CacheService()
ai_cache = AIResponseCache(cache_service)
query_cache = QueryCache(cache_service)


# Performance monitoring for cache
class CacheMetrics:
    """
    Monitor cache performance and hit rates.
    """

    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.errors = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total

    def record_hit(self):
        """Record cache hit"""
        self.hits += 1

    def record_miss(self):
        """Record cache miss"""
        self.misses += 1

    def record_error(self):
        """Record cache error"""
        self.errors += 1

    def get_stats(self) -> dict:
        """Get cache statistics"""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "errors": self.errors,
            "hit_rate": self.hit_rate,
            "total_requests": self.hits + self.misses
        }


# Initialize cache metrics
cache_metrics = CacheMetrics()


import asyncio  # Add this import at the top of the file