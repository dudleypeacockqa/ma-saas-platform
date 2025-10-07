"""
Advanced Rate Limiting Middleware
Per-tenant and per-endpoint rate limiting with subscription tier support
"""

import os
import logging
import time
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis
from collections import defaultdict

logger = logging.getLogger(__name__)

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"


class RateLimitConfig:
    """Rate limit configuration for different tiers"""

    TIERS = {
        "free": {
            "requests_per_minute": 60,
            "requests_per_hour": 1000,
            "ai_operations_per_day": 50,
            "webhook_calls_per_minute": 10
        },
        "starter": {
            "requests_per_minute": 300,
            "requests_per_hour": 10000,
            "ai_operations_per_day": 500,
            "webhook_calls_per_minute": 50
        },
        "professional": {
            "requests_per_minute": 1000,
            "requests_per_hour": 50000,
            "ai_operations_per_day": 2000,
            "webhook_calls_per_minute": 200
        },
        "enterprise": {
            "requests_per_minute": 5000,
            "requests_per_hour": 250000,
            "ai_operations_per_day": -1,  # Unlimited
            "webhook_calls_per_minute": 1000
        }
    }

    @classmethod
    def get_limit(cls, tier: str, limit_type: str) -> int:
        """Get rate limit for specific tier and type"""
        tier_config = cls.TIERS.get(tier, cls.TIERS["free"])
        return tier_config.get(limit_type, 60)


class AdvancedRateLimiter:
    """Advanced rate limiter with Redis backend and multiple window support"""

    def __init__(self):
        self.redis_client = self._init_redis()
        self.memory_cache: Dict[str, list] = defaultdict(list)
        self.use_redis = self.redis_client is not None

    def _init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis connection"""
        try:
            client = redis.from_url(REDIS_URL, decode_responses=False)
            client.ping()
            logger.info("Redis connected for advanced rate limiting")
            return client
        except Exception as e:
            logger.warning(f"Redis unavailable, using memory-based rate limiting: {e}")
            return None

    def _get_key(self, identifier: str, window: str) -> str:
        """Generate cache key for rate limit"""
        return f"ratelimit:{identifier}:{window}"

    async def check_limit(
        self,
        identifier: str,
        limit: int,
        window_seconds: int,
        window_name: str = "default"
    ) -> Dict[str, Any]:
        """
        Check rate limit using sliding window algorithm

        Args:
            identifier: Unique identifier (org_id, user_id, IP)
            limit: Maximum requests allowed
            window_seconds: Time window in seconds
            window_name: Name of the window (for multiple concurrent limits)

        Returns:
            Dict with allowed, remaining, reset_at, and current_count
        """
        key = self._get_key(identifier, window_name)
        now = time.time()
        window_start = now - window_seconds

        if self.use_redis and self.redis_client:
            return await self._check_limit_redis(
                key, limit, window_seconds, now, window_start
            )
        else:
            return await self._check_limit_memory(
                key, limit, window_seconds, now, window_start
            )

    async def _check_limit_redis(
        self,
        key: str,
        limit: int,
        window_seconds: int,
        now: float,
        window_start: float
    ) -> Dict[str, Any]:
        """Redis-based rate limiting"""
        try:
            pipe = self.redis_client.pipeline()

            # Remove old entries outside the window
            pipe.zremrangebyscore(key, 0, window_start)

            # Count requests in current window
            pipe.zcard(key)

            # Add current request timestamp
            pipe.zadd(key, {str(now): now})

            # Set expiration
            pipe.expire(key, window_seconds)

            results = pipe.execute()
            current_count = results[1]

            allowed = current_count < limit
            remaining = max(0, limit - current_count - 1)
            reset_at = datetime.fromtimestamp(now + window_seconds)

            return {
                "allowed": allowed,
                "remaining": remaining,
                "reset_at": reset_at,
                "current_count": current_count,
                "limit": limit
            }

        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            # Fall back to allowing the request
            return {
                "allowed": True,
                "remaining": limit,
                "reset_at": datetime.fromtimestamp(now + window_seconds),
                "current_count": 0,
                "limit": limit
            }

    async def _check_limit_memory(
        self,
        key: str,
        limit: int,
        window_seconds: int,
        now: float,
        window_start: float
    ) -> Dict[str, Any]:
        """Memory-based rate limiting (fallback)"""
        if key not in self.memory_cache:
            self.memory_cache[key] = []

        # Remove old timestamps
        self.memory_cache[key] = [
            ts for ts in self.memory_cache[key]
            if ts > window_start
        ]

        current_count = len(self.memory_cache[key])
        allowed = current_count < limit

        if allowed:
            self.memory_cache[key].append(now)

        remaining = max(0, limit - current_count - 1)
        reset_at = datetime.fromtimestamp(now + window_seconds)

        return {
            "allowed": allowed,
            "remaining": remaining,
            "reset_at": reset_at,
            "current_count": current_count,
            "limit": limit
        }

    async def increment_counter(
        self,
        identifier: str,
        counter_name: str,
        window_seconds: int = 86400  # Default: 24 hours
    ) -> int:
        """Increment a counter (for tracking daily limits, etc.)"""
        key = f"counter:{identifier}:{counter_name}"

        if self.use_redis and self.redis_client:
            try:
                pipe = self.redis_client.pipeline()
                pipe.incr(key)
                pipe.expire(key, window_seconds)
                results = pipe.execute()
                return results[0]
            except Exception as e:
                logger.error(f"Redis counter increment failed: {e}")
                return 0

        # Memory-based counter
        if key not in self.memory_cache:
            self.memory_cache[key] = []

        self.memory_cache[key].append(time.time())
        return len(self.memory_cache[key])


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for applying rate limits based on subscription tier
    """

    def __init__(self, app, rate_limiter: Optional[AdvancedRateLimiter] = None):
        super().__init__(app)
        self.rate_limiter = rate_limiter or AdvancedRateLimiter()

    async def dispatch(self, request: Request, call_next):
        """Apply rate limiting"""
        if not ENABLE_RATE_LIMITING:
            return await call_next(request)

        # Get identifier (organization_id > user_id > IP)
        organization_id = getattr(request.state, "organization_id", None)
        user_id = getattr(request.state, "user_id", None)
        client_ip = request.client.host if request.client else "unknown"

        identifier = organization_id or user_id or client_ip

        # Get subscription tier (default to free)
        subscription_tier = getattr(request.state, "subscription_tier", "free")

        # Determine endpoint type
        path = request.url.path
        endpoint_type = self._get_endpoint_type(path)

        # Get rate limit based on tier and endpoint
        limit_type = "requests_per_minute"
        window_seconds = 60

        if endpoint_type == "ai":
            limit_type = "ai_operations_per_day"
            window_seconds = 86400  # 24 hours
        elif endpoint_type == "webhook":
            limit_type = "webhook_calls_per_minute"
            window_seconds = 60

        limit = RateLimitConfig.get_limit(subscription_tier, limit_type)

        # Check rate limit
        if limit > 0:  # -1 means unlimited
            result = await self.rate_limiter.check_limit(
                identifier=identifier,
                limit=limit,
                window_seconds=window_seconds,
                window_name=limit_type
            )

            if not result["allowed"]:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Rate limit exceeded",
                        "limit": result["limit"],
                        "current": result["current_count"],
                        "reset_at": result["reset_at"].isoformat(),
                        "subscription_tier": subscription_tier
                    },
                    headers={
                        "X-RateLimit-Limit": str(result["limit"]),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": result["reset_at"].isoformat(),
                        "Retry-After": str(window_seconds)
                    }
                )

            # Add rate limit headers to response
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(result["limit"])
            response.headers["X-RateLimit-Remaining"] = str(result["remaining"])
            response.headers["X-RateLimit-Reset"] = result["reset_at"].isoformat()

            return response

        # No limit or unlimited
        return await call_next(request)

    def _get_endpoint_type(self, path: str) -> str:
        """Determine endpoint type from path"""
        if "/ai/" in path or "/analyze" in path:
            return "ai"
        elif "/webhook" in path:
            return "webhook"
        else:
            return "api"


# Singleton instance
advanced_rate_limiter = AdvancedRateLimiter()
