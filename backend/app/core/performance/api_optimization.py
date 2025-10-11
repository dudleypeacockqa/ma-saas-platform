"""
API Performance Optimization
Response time enhancement and reliability improvement for sub-200ms targets
"""

from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import time
import gzip
import json
import msgpack
from functools import wraps
from fastapi import Request, Response, HTTPException
from fastapi.responses import StreamingResponse
import structlog

logger = structlog.get_logger()


class OptimizationStrategy(Enum):
    """API optimization strategies"""
    COMPRESSION = "compression"
    PAGINATION = "pagination"
    FIELD_FILTERING = "field_filtering"
    BATCH_PROCESSING = "batch_processing"
    ASYNC_PROCESSING = "async_processing"
    CONNECTION_POOLING = "connection_pooling"
    RESPONSE_CACHING = "response_caching"
    PREFETCHING = "prefetching"


@dataclass
class APIMetrics:
    """API performance metrics"""
    endpoint: str
    method: str
    response_time: float
    payload_size: int
    status_code: int
    cache_hit: bool
    timestamp: datetime


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    requests_per_second: int = 100
    burst_size: int = 200
    window_size: int = 60  # seconds
    by_endpoint: Dict[str, int] = None


class APIOptimizer:
    """Main API optimization controller"""

    def __init__(self, cache_client, redis_client):
        self.cache = cache_client
        self.redis = redis_client
        self.metrics_buffer = []
        self.rate_limiter = AdaptiveRateLimiter(redis_client)
        self.response_compressor = ResponseCompressor()
        self.batch_processor = BatchProcessor()
        self.circuit_breaker = CircuitBreaker()

    async def optimize_request(
        self,
        request: Request,
        endpoint_handler: Callable
    ) -> Response:
        """Optimize API request processing"""

        start_time = time.time()

        # Apply rate limiting
        await self.rate_limiter.check_rate_limit(request)

        # Check circuit breaker
        if not await self.circuit_breaker.is_healthy(str(request.url)):
            raise HTTPException(status_code=503, detail="Service temporarily unavailable")

        # Check cache for GET requests
        if request.method == "GET":
            cached_response = await self._get_cached_response(request)
            if cached_response:
                return cached_response

        # Process request with optimizations
        try:
            # Batch similar requests if applicable
            if await self._should_batch(request):
                response = await self.batch_processor.process(request, endpoint_handler)
            else:
                response = await endpoint_handler(request)

            # Compress response if beneficial
            response = await self.response_compressor.compress_if_beneficial(
                request,
                response
            )

            # Cache successful responses
            if request.method == "GET" and response.status_code == 200:
                await self._cache_response(request, response)

            # Record metrics
            await self._record_metrics(
                request,
                response,
                time.time() - start_time
            )

            # Mark circuit as healthy
            await self.circuit_breaker.record_success(str(request.url))

            return response

        except Exception as e:
            # Record failure for circuit breaker
            await self.circuit_breaker.record_failure(str(request.url))
            raise

    async def _get_cached_response(self, request: Request) -> Optional[Response]:
        """Get cached response if available"""

        cache_key = self._generate_cache_key(request)
        cached_data = await self.cache.get(cache_key)

        if cached_data:
            logger.info("api_cache_hit", endpoint=str(request.url))
            return Response(
                content=cached_data["content"],
                status_code=cached_data["status_code"],
                headers=cached_data["headers"]
            )

        return None

    async def _cache_response(self, request: Request, response: Response) -> None:
        """Cache API response"""

        cache_key = self._generate_cache_key(request)
        ttl = self._get_cache_ttl(str(request.url))

        cache_data = {
            "content": response.body,
            "status_code": response.status_code,
            "headers": dict(response.headers)
        }

        await self.cache.set(cache_key, cache_data, ttl=ttl)

    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key for request"""

        import hashlib

        key_parts = [
            request.method,
            str(request.url),
            str(request.query_params),
            request.headers.get("authorization", "")
        ]

        key_string = ":".join(key_parts)
        return f"api:{hashlib.sha256(key_string.encode()).hexdigest()[:16]}"

    def _get_cache_ttl(self, endpoint: str) -> int:
        """Get cache TTL for endpoint"""

        # Different TTLs for different endpoints
        if "/metrics" in endpoint:
            return 30  # 30 seconds for metrics
        elif "/deals" in endpoint:
            return 300  # 5 minutes for deals
        elif "/static" in endpoint:
            return 3600  # 1 hour for static content
        else:
            return 60  # 1 minute default

    async def _should_batch(self, request: Request) -> bool:
        """Determine if request should be batched"""

        # Batch similar requests arriving within time window
        endpoint = str(request.url.path)

        if endpoint in ["/api/deals/search", "/api/analytics/aggregate"]:
            # Check if similar requests are queued
            queue_size = await self.redis.get(f"batch_queue:{endpoint}")
            return int(queue_size) > 1 if queue_size else False

        return False

    async def _record_metrics(
        self,
        request: Request,
        response: Response,
        response_time: float
    ) -> None:
        """Record API metrics"""

        metric = APIMetrics(
            endpoint=str(request.url.path),
            method=request.method,
            response_time=response_time * 1000,  # Convert to ms
            payload_size=len(response.body) if hasattr(response, 'body') else 0,
            status_code=response.status_code,
            cache_hit=False,  # Set appropriately
            timestamp=datetime.utcnow()
        )

        self.metrics_buffer.append(metric)

        # Flush metrics periodically
        if len(self.metrics_buffer) >= 100:
            await self._flush_metrics()

    async def _flush_metrics(self) -> None:
        """Flush metrics to storage"""

        if not self.metrics_buffer:
            return

        # Store metrics in time-series database
        for metric in self.metrics_buffer:
            await self.redis.zadd(
                f"api_metrics:{metric.endpoint}",
                {json.dumps(metric.__dict__, default=str): metric.timestamp.timestamp()}
            )

        # Calculate aggregates
        avg_response_time = sum(m.response_time for m in self.metrics_buffer) / len(self.metrics_buffer)

        logger.info("api_metrics_flushed",
                   count=len(self.metrics_buffer),
                   avg_response_time=avg_response_time)

        self.metrics_buffer.clear()


class ResponseCompressor:
    """Intelligent response compression"""

    def __init__(self):
        self.min_size_for_compression = 1024  # 1KB minimum
        self.compression_formats = ["gzip", "br", "deflate"]

    async def compress_if_beneficial(
        self,
        request: Request,
        response: Response
    ) -> Response:
        """Compress response if beneficial"""

        # Check if client accepts compression
        accept_encoding = request.headers.get("accept-encoding", "")

        if not any(fmt in accept_encoding for fmt in self.compression_formats):
            return response

        # Check if response is large enough to benefit
        if len(response.body) < self.min_size_for_compression:
            return response

        # Compress with best available algorithm
        if "br" in accept_encoding:
            compressed = await self._brotli_compress(response.body)
            response.headers["content-encoding"] = "br"
        elif "gzip" in accept_encoding:
            compressed = await self._gzip_compress(response.body)
            response.headers["content-encoding"] = "gzip"
        else:
            return response

        # Update response
        original_size = len(response.body)
        compressed_size = len(compressed)

        response.body = compressed
        response.headers["content-length"] = str(compressed_size)

        logger.debug("response_compressed",
                    original=original_size,
                    compressed=compressed_size,
                    ratio=f"{(1 - compressed_size/original_size) * 100:.1f}%")

        return response

    async def _gzip_compress(self, data: bytes) -> bytes:
        """Compress with gzip"""
        return gzip.compress(data, compresslevel=6)

    async def _brotli_compress(self, data: bytes) -> bytes:
        """Compress with Brotli"""
        try:
            import brotli
            return brotli.compress(data, quality=4)
        except ImportError:
            # Fallback to gzip if Brotli not available
            return await self._gzip_compress(data)


class BatchProcessor:
    """Batch request processing for efficiency"""

    def __init__(self):
        self.batch_queues = {}
        self.batch_size = 10
        self.batch_timeout = 100  # ms

    async def process(
        self,
        request: Request,
        handler: Callable
    ) -> Response:
        """Process request as part of batch"""

        endpoint = str(request.url.path)

        # Add to batch queue
        if endpoint not in self.batch_queues:
            self.batch_queues[endpoint] = []

        # Create future for this request
        future = asyncio.Future()
        self.batch_queues[endpoint].append({
            "request": request,
            "future": future,
            "timestamp": time.time()
        })

        # Process batch if ready
        if len(self.batch_queues[endpoint]) >= self.batch_size:
            await self._process_batch(endpoint, handler)
        else:
            # Schedule batch processing after timeout
            asyncio.create_task(self._delayed_batch_process(endpoint, handler))

        # Wait for result
        return await future

    async def _process_batch(self, endpoint: str, handler: Callable) -> None:
        """Process batch of requests"""

        if endpoint not in self.batch_queues or not self.batch_queues[endpoint]:
            return

        batch = self.batch_queues[endpoint]
        self.batch_queues[endpoint] = []

        logger.info("batch_processing", endpoint=endpoint, size=len(batch))

        try:
            # Combine requests for batch processing
            combined_request = self._combine_requests([item["request"] for item in batch])

            # Process combined request
            combined_response = await handler(combined_request)

            # Split response for individual requests
            individual_responses = self._split_response(combined_response, len(batch))

            # Set results for each future
            for item, response in zip(batch, individual_responses):
                item["future"].set_result(response)

        except Exception as e:
            # Set exception for all futures
            for item in batch:
                item["future"].set_exception(e)

    async def _delayed_batch_process(self, endpoint: str, handler: Callable) -> None:
        """Process batch after timeout"""

        await asyncio.sleep(self.batch_timeout / 1000)
        await self._process_batch(endpoint, handler)

    def _combine_requests(self, requests: List[Request]) -> Request:
        """Combine multiple requests into one"""

        # Simplified combination - in production would be more sophisticated
        combined = requests[0]
        # Add batch information
        combined.state.batch_size = len(requests)
        combined.state.batch_requests = requests

        return combined

    def _split_response(self, response: Response, batch_size: int) -> List[Response]:
        """Split combined response into individual responses"""

        # Simplified splitting - in production would be more sophisticated
        responses = []

        for i in range(batch_size):
            responses.append(Response(
                content=response.body,
                status_code=response.status_code,
                headers=response.headers
            ))

        return responses


class AdaptiveRateLimiter:
    """Adaptive rate limiting based on system load"""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.default_limit = 100  # requests per second
        self.adaptive_factor = 1.0

    async def check_rate_limit(self, request: Request) -> None:
        """Check if request should be rate limited"""

        # Get client identifier
        client_id = self._get_client_id(request)

        # Get current limit based on system load
        current_limit = await self._get_adaptive_limit()

        # Check rate limit using sliding window
        key = f"rate_limit:{client_id}"
        current_time = time.time()

        # Remove old entries
        await self.redis.zremrangebyscore(key, 0, current_time - 60)

        # Count recent requests
        request_count = await self.redis.zcard(key)

        if request_count >= current_limit:
            # Calculate retry after
            oldest_request = await self.redis.zrange(key, 0, 0, withscores=True)
            if oldest_request:
                retry_after = 60 - (current_time - oldest_request[0][1])
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded",
                    headers={"Retry-After": str(int(retry_after))}
                )

        # Add current request
        await self.redis.zadd(key, {str(current_time): current_time})
        await self.redis.expire(key, 60)

    async def _get_adaptive_limit(self) -> int:
        """Get adaptive rate limit based on system metrics"""

        # Check system load
        cpu_usage = await self.redis.get("system:cpu_usage")
        response_time = await self.redis.get("api:avg_response_time")

        # Adjust limit based on metrics
        if cpu_usage and float(cpu_usage) > 80:
            self.adaptive_factor = 0.5  # Reduce limit by 50%
        elif response_time and float(response_time) > 500:
            self.adaptive_factor = 0.7  # Reduce limit by 30%
        else:
            self.adaptive_factor = min(1.5, self.adaptive_factor + 0.1)  # Gradually increase

        return int(self.default_limit * self.adaptive_factor)

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""

        # Try to get authenticated user ID
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"

        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"


class CircuitBreaker:
    """Circuit breaker for fault tolerance"""

    def __init__(self):
        self.failure_threshold = 5
        self.success_threshold = 2
        self.timeout = 60  # seconds
        self.half_open_requests = 3
        self.states = {}  # endpoint -> state

    async def is_healthy(self, endpoint: str) -> bool:
        """Check if endpoint circuit is healthy"""

        state = self.states.get(endpoint, {"state": "closed", "failures": 0})

        if state["state"] == "open":
            # Check if timeout has passed
            if time.time() - state["opened_at"] > self.timeout:
                state["state"] = "half_open"
                state["half_open_successes"] = 0
                self.states[endpoint] = state
            else:
                return False

        if state["state"] == "half_open":
            # Allow limited requests in half-open state
            if state.get("half_open_requests", 0) >= self.half_open_requests:
                return False

        return True

    async def record_success(self, endpoint: str) -> None:
        """Record successful request"""

        state = self.states.get(endpoint, {"state": "closed", "failures": 0})

        if state["state"] == "half_open":
            state["half_open_successes"] = state.get("half_open_successes", 0) + 1

            if state["half_open_successes"] >= self.success_threshold:
                # Close circuit
                state["state"] = "closed"
                state["failures"] = 0
                logger.info("circuit_closed", endpoint=endpoint)

        elif state["state"] == "closed":
            # Reset failure count on success
            state["failures"] = 0

        self.states[endpoint] = state

    async def record_failure(self, endpoint: str) -> None:
        """Record failed request"""

        state = self.states.get(endpoint, {"state": "closed", "failures": 0})

        state["failures"] = state.get("failures", 0) + 1

        if state["state"] == "closed" and state["failures"] >= self.failure_threshold:
            # Open circuit
            state["state"] = "open"
            state["opened_at"] = time.time()
            logger.warning("circuit_opened", endpoint=endpoint)

        elif state["state"] == "half_open":
            # Return to open state
            state["state"] = "open"
            state["opened_at"] = time.time()

        self.states[endpoint] = state


def response_time_tracker(target_ms: int = 200):
    """Decorator to track and enforce response time targets"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()

            # Set timeout for target response time
            try:
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=target_ms / 1000
                )

                elapsed = (time.time() - start) * 1000

                if elapsed > target_ms:
                    logger.warning("response_time_exceeded",
                                 endpoint=func.__name__,
                                 target=target_ms,
                                 actual=elapsed)
                else:
                    logger.debug("response_time_ok",
                               endpoint=func.__name__,
                               time=elapsed)

                return result

            except asyncio.TimeoutError:
                logger.error("response_timeout",
                           endpoint=func.__name__,
                           timeout=target_ms)
                raise HTTPException(status_code=504, detail="Gateway timeout")

        return wrapper
    return decorator


class ResponseStreamer:
    """Stream large responses for better performance"""

    @staticmethod
    async def stream_json_array(data_generator):
        """Stream JSON array response"""

        async def generate():
            yield b"["
            first = True

            async for item in data_generator:
                if not first:
                    yield b","
                yield json.dumps(item).encode()
                first = False

            yield b"]"

        return StreamingResponse(
            generate(),
            media_type="application/json"
        )

    @staticmethod
    async def stream_ndjson(data_generator):
        """Stream newline-delimited JSON"""

        async def generate():
            async for item in data_generator:
                yield json.dumps(item).encode() + b"\n"

        return StreamingResponse(
            generate(),
            media_type="application/x-ndjson"
        )


class GraphQLOptimizer:
    """GraphQL-specific optimizations"""

    def __init__(self):
        self.query_depth_limit = 5
        self.query_complexity_limit = 1000

    async def optimize_graphql_query(self, query: str) -> str:
        """Optimize GraphQL query"""

        # Parse and analyze query
        depth = self._calculate_query_depth(query)
        complexity = self._calculate_query_complexity(query)

        # Reject overly complex queries
        if depth > self.query_depth_limit:
            raise HTTPException(400, f"Query depth {depth} exceeds limit {self.query_depth_limit}")

        if complexity > self.query_complexity_limit:
            raise HTTPException(400, f"Query complexity {complexity} exceeds limit {self.query_complexity_limit}")

        # Optimize query
        optimized = self._apply_graphql_optimizations(query)

        return optimized

    def _calculate_query_depth(self, query: str) -> int:
        """Calculate GraphQL query depth"""

        # Simplified depth calculation
        max_depth = 0
        current_depth = 0

        for char in query:
            if char == "{":
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == "}":
                current_depth -= 1

        return max_depth

    def _calculate_query_complexity(self, query: str) -> int:
        """Calculate GraphQL query complexity"""

        # Simplified complexity calculation
        # Count fields and multiply by depth
        field_count = query.count(":")
        depth = self._calculate_query_depth(query)

        return field_count * depth

    def _apply_graphql_optimizations(self, query: str) -> str:
        """Apply GraphQL-specific optimizations"""

        # Add field limiting
        # Add query batching hints
        # Add caching directives

        return query


class APIMonitor:
    """Real-time API monitoring"""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.alert_thresholds = {
            "response_time": 500,  # ms
            "error_rate": 0.01,  # 1%
            "throughput": 10000  # requests/min
        }

    async def monitor_health(self) -> Dict[str, Any]:
        """Monitor API health metrics"""

        health = {
            "status": "healthy",
            "metrics": {},
            "alerts": []
        }

        # Get current metrics
        response_time = await self.redis.get("api:avg_response_time")
        error_rate = await self.redis.get("api:error_rate")
        throughput = await self.redis.get("api:throughput")

        health["metrics"] = {
            "response_time": float(response_time) if response_time else 0,
            "error_rate": float(error_rate) if error_rate else 0,
            "throughput": float(throughput) if throughput else 0
        }

        # Check thresholds
        if health["metrics"]["response_time"] > self.alert_thresholds["response_time"]:
            health["alerts"].append({
                "type": "response_time",
                "message": f"Response time {health['metrics']['response_time']}ms exceeds threshold"
            })
            health["status"] = "degraded"

        if health["metrics"]["error_rate"] > self.alert_thresholds["error_rate"]:
            health["alerts"].append({
                "type": "error_rate",
                "message": f"Error rate {health['metrics']['error_rate']*100:.2f}% exceeds threshold"
            })
            health["status"] = "unhealthy"

        return health