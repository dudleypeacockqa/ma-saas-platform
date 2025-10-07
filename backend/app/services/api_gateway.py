"""
API Gateway Service
Centralized request routing, load balancing, rate limiting, and authentication
"""

import os
import logging
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
import redis

logger = logging.getLogger(__name__)

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"


class RateLimiter:
    """Rate limiting for API requests with Redis backend"""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.memory_cache: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.use_redis = redis_client is not None

    def _get_key(self, identifier: str, endpoint: str) -> str:
        """Generate rate limit cache key"""
        return f"ratelimit:{identifier}:{endpoint}"

    async def check_rate_limit(
        self,
        identifier: str,
        endpoint: str,
        limit: int,
        window_seconds: int
    ) -> Dict[str, Any]:
        """
        Check if request is within rate limit

        Returns dict with:
        - allowed: bool
        - remaining: int
        - reset_at: datetime
        """
        key = self._get_key(identifier, endpoint)
        now = time.time()
        window_start = now - window_seconds

        if self.use_redis and self.redis_client:
            try:
                # Use Redis sliding window
                pipe = self.redis_client.pipeline()

                # Remove old entries
                pipe.zremrangebyscore(key, 0, window_start)

                # Count current requests
                pipe.zcard(key)

                # Add current request
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
                    "limit": limit
                }

            except Exception as e:
                logger.error(f"Redis rate limit error: {e}")
                # Fall through to memory-based limiting

        # Memory-based rate limiting (fallback)
        if key not in self.memory_cache:
            self.memory_cache[key] = {
                "requests": [],
                "window_start": now
            }

        cache_entry = self.memory_cache[key]

        # Remove old requests
        cache_entry["requests"] = [
            req_time for req_time in cache_entry["requests"]
            if req_time > window_start
        ]

        current_count = len(cache_entry["requests"])
        allowed = current_count < limit

        if allowed:
            cache_entry["requests"].append(now)

        remaining = max(0, limit - current_count - 1)
        reset_at = datetime.fromtimestamp(now + window_seconds)

        return {
            "allowed": allowed,
            "remaining": remaining,
            "reset_at": reset_at,
            "limit": limit
        }


class APIGateway:
    """API Gateway for request management"""

    def __init__(self):
        self.rate_limiter = self._initialize_rate_limiter()
        self.routes: Dict[str, Dict[str, Any]] = {}
        self.middleware_chain: List[Callable] = []

    def _initialize_rate_limiter(self) -> RateLimiter:
        """Initialize rate limiter with Redis if available"""
        try:
            redis_client = redis.from_url(REDIS_URL, decode_responses=True)
            redis_client.ping()
            logger.info("Redis connected for rate limiting")
            return RateLimiter(redis_client=redis_client)
        except Exception as e:
            logger.warning(f"Redis connection failed, using memory-based rate limiting: {e}")
            return RateLimiter()

    def register_route(
        self,
        path: str,
        methods: List[str],
        rate_limit: Optional[int] = None,
        rate_window: int = 60,
        auth_required: bool = True,
        roles: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Register a route with the API gateway"""
        self.routes[path] = {
            "methods": methods,
            "rate_limit": rate_limit,
            "rate_window": rate_window,
            "auth_required": auth_required,
            "roles": roles or [],
            "metadata": metadata or {}
        }

    async def process_request(
        self,
        request: Request,
        organization_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process incoming request through gateway"""
        path = request.url.path
        method = request.method

        # Get route configuration
        route_config = self.routes.get(path, {})

        # Apply rate limiting if configured
        if ENABLE_RATE_LIMITING and route_config.get("rate_limit"):
            identifier = organization_id or user_id or request.client.host
            endpoint = f"{method}:{path}"

            rate_check = await self.rate_limiter.check_rate_limit(
                identifier=identifier,
                endpoint=endpoint,
                limit=route_config["rate_limit"],
                window_seconds=route_config.get("rate_window", 60)
            )

            if not rate_check["allowed"]:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "limit": rate_check["limit"],
                        "reset_at": rate_check["reset_at"].isoformat()
                    }
                )

            # Add rate limit headers
            return {
                "rate_limit_headers": {
                    "X-RateLimit-Limit": str(rate_check["limit"]),
                    "X-RateLimit-Remaining": str(rate_check["remaining"]),
                    "X-RateLimit-Reset": rate_check["reset_at"].isoformat()
                }
            }

        return {}


class APIGatewayMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for API Gateway"""

    def __init__(self, app, gateway: APIGateway):
        super().__init__(app)
        self.gateway = gateway

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Extract user/org info from request if available
        organization_id = request.headers.get("X-Organization-ID")
        user_id = request.headers.get("X-User-ID")

        try:
            # Process through gateway
            gateway_result = await self.gateway.process_request(
                request,
                organization_id=organization_id,
                user_id=user_id
            )

            # Continue with request
            response = await call_next(request)

            # Add rate limit headers if present
            if "rate_limit_headers" in gateway_result:
                for header, value in gateway_result["rate_limit_headers"].items():
                    response.headers[header] = value

            # Add processing time header
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except HTTPException as e:
            # Return rate limit error
            return JSONResponse(
                status_code=e.status_code,
                content=e.detail
            )
        except Exception as e:
            logger.error(f"API Gateway error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Internal server error"}
            )


# Rate limit configurations for different endpoint types
RATE_LIMIT_CONFIGS = {
    "public": {
        "limit": 100,
        "window": 60  # 100 requests per minute
    },
    "authenticated": {
        "limit": 1000,
        "window": 60  # 1000 requests per minute
    },
    "premium": {
        "limit": 5000,
        "window": 60  # 5000 requests per minute
    },
    "ai_operations": {
        "limit": 50,
        "window": 60  # 50 AI operations per minute
    },
    "webhook": {
        "limit": 500,
        "window": 60  # 500 webhook calls per minute
    }
}


def get_rate_limit_for_endpoint(
    endpoint_type: str,
    plan_tier: Optional[str] = None
) -> Dict[str, int]:
    """Get rate limit configuration based on endpoint type and plan tier"""
    base_config = RATE_LIMIT_CONFIGS.get(endpoint_type, RATE_LIMIT_CONFIGS["public"])

    # Adjust limits based on subscription tier
    if plan_tier == "enterprise":
        return {
            "limit": base_config["limit"] * 10,
            "window": base_config["window"]
        }
    elif plan_tier == "professional":
        return {
            "limit": base_config["limit"] * 5,
            "window": base_config["window"]
        }
    elif plan_tier == "starter":
        return {
            "limit": base_config["limit"] * 2,
            "window": base_config["window"]
        }

    return base_config


# Singleton instance
api_gateway = APIGateway()


# Helper function to register common routes
def register_default_routes():
    """Register default rate limits for common routes"""

    # Authentication endpoints - higher limits
    api_gateway.register_route(
        "/api/auth/login",
        methods=["POST"],
        rate_limit=20,
        rate_window=60,
        auth_required=False
    )

    # Deal management - authenticated users
    api_gateway.register_route(
        "/api/deals",
        methods=["GET", "POST", "PUT", "DELETE"],
        rate_limit=500,
        rate_window=60,
        auth_required=True
    )

    # AI operations - lower limits
    api_gateway.register_route(
        "/api/ai/analyze",
        methods=["POST"],
        rate_limit=50,
        rate_window=60,
        auth_required=True
    )

    # Webhooks - moderate limits
    api_gateway.register_route(
        "/api/webhooks/clerk",
        methods=["POST"],
        rate_limit=500,
        rate_window=60,
        auth_required=False
    )

    api_gateway.register_route(
        "/api/payments/webhook",
        methods=["POST"],
        rate_limit=500,
        rate_window=60,
        auth_required=False
    )

    logger.info("Default API Gateway routes registered")


# Initialize on import
register_default_routes()
