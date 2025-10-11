"""
Advanced Caching Strategies with CDN Integration
Multi-layer caching for sub-200ms response times
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import hashlib
import pickle
import json
import aioredis
from aiocache import Cache, caches
from aiocache.serializers import PickleSerializer
import structlog

logger = structlog.get_logger()


class CacheLayer(Enum):
    """Cache layer types"""
    L1_MEMORY = "l1_memory"  # In-process memory
    L2_REDIS = "l2_redis"  # Redis distributed cache
    L3_CDN = "l3_cdn"  # CDN edge cache
    L4_DATABASE = "l4_database"  # Database query cache


class CacheStrategy(Enum):
    """Caching strategies"""
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    CACHE_ASIDE = "cache_aside"
    REFRESH_AHEAD = "refresh_ahead"
    READ_THROUGH = "read_through"


@dataclass
class CacheConfig:
    """Cache configuration"""
    layer: CacheLayer
    ttl: int  # seconds
    max_size: int
    strategy: CacheStrategy
    compression: bool
    encryption: bool
    warmup_enabled: bool


@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    hits: int
    misses: int
    evictions: int
    avg_latency: float
    memory_usage: int
    hit_ratio: float


class MultiLayerCache:
    """Multi-layer caching system with intelligent routing"""

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.layers = self._initialize_layers()
        self.metrics = {layer: CacheMetrics(0, 0, 0, 0, 0, 0) for layer in CacheLayer}
        self.prefetch_queue = asyncio.Queue()
        self.invalidation_queue = asyncio.Queue()

    def _initialize_layers(self) -> Dict[CacheLayer, Cache]:
        """Initialize cache layers"""

        # L1: In-memory cache (fastest, limited size)
        caches.set_config({
            'l1_memory': {
                'cache': "aiocache.SimpleMemoryCache",
                'serializer': {
                    'class': "aiocache.serializers.PickleSerializer"
                },
                'ttl': 60,  # 1 minute
            }
        })

        # L2: Redis cache (distributed, larger)
        caches.set_config({
            'l2_redis': {
                'cache': "aiocache.RedisCache",
                'endpoint': "localhost",
                'port': 6379,
                'serializer': {
                    'class': "aiocache.serializers.PickleSerializer"
                },
                'ttl': 300,  # 5 minutes
            }
        })

        return {
            CacheLayer.L1_MEMORY: caches.get('l1_memory'),
            CacheLayer.L2_REDIS: caches.get('l2_redis'),
        }

    async def get(
        self,
        key: str,
        fetch_func: Optional[callable] = None,
        ttl: Optional[int] = None,
        skip_l1: bool = False
    ) -> Optional[Any]:
        """Get value with multi-layer cache fallback"""

        start_time = datetime.utcnow()
        cache_key = self._generate_key(key)

        # Try L1 (memory) first
        if not skip_l1:
            value = await self._get_from_layer(CacheLayer.L1_MEMORY, cache_key)
            if value is not None:
                await self._record_hit(CacheLayer.L1_MEMORY, start_time)
                return value

        # Try L2 (Redis)
        value = await self._get_from_layer(CacheLayer.L2_REDIS, cache_key)
        if value is not None:
            await self._record_hit(CacheLayer.L2_REDIS, start_time)

            # Backfill L1
            if not skip_l1:
                await self._set_in_layer(CacheLayer.L1_MEMORY, cache_key, value, 60)

            return value

        # Try L3 (CDN) if available
        value = await self._get_from_cdn(cache_key)
        if value is not None:
            await self._record_hit(CacheLayer.L3_CDN, start_time)

            # Backfill L1 and L2
            await self._backfill_cache(cache_key, value)

            return value

        # Cache miss - fetch from source
        await self._record_miss(start_time)

        if fetch_func:
            value = await fetch_func()

            # Write to all cache layers
            await self.set(key, value, ttl)

            return value

        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        strategy: CacheStrategy = CacheStrategy.WRITE_THROUGH
    ) -> bool:
        """Set value in cache with specified strategy"""

        cache_key = self._generate_key(key)

        if strategy == CacheStrategy.WRITE_THROUGH:
            # Write to all layers synchronously
            await self._write_through(cache_key, value, ttl)

        elif strategy == CacheStrategy.WRITE_BEHIND:
            # Write to memory immediately, queue for other layers
            await self._write_behind(cache_key, value, ttl)

        elif strategy == CacheStrategy.CACHE_ASIDE:
            # Application manages cache explicitly
            await self._cache_aside(cache_key, value, ttl)

        return True

    async def invalidate(
        self,
        pattern: str,
        cascade: bool = True
    ) -> int:
        """Invalidate cache entries matching pattern"""

        invalidated = 0

        # Invalidate from all layers
        for layer in [CacheLayer.L1_MEMORY, CacheLayer.L2_REDIS]:
            count = await self._invalidate_layer(layer, pattern)
            invalidated += count

        # Invalidate CDN if cascade enabled
        if cascade:
            await self._invalidate_cdn(pattern)

        # Broadcast invalidation to other nodes
        await self._broadcast_invalidation(pattern)

        logger.info("cache_invalidated", pattern=pattern, count=invalidated)

        return invalidated

    async def warm_cache(
        self,
        queries: List[Dict[str, Any]],
        priority: int = 5
    ) -> None:
        """Proactively warm cache with anticipated queries"""

        logger.info("cache_warming_started", queries=len(queries))

        for query in queries:
            # Add to prefetch queue with priority
            await self.prefetch_queue.put((priority, query))

        # Start prefetch worker if not running
        asyncio.create_task(self._prefetch_worker())

    async def get_metrics(self, layer: Optional[CacheLayer] = None) -> Dict[str, Any]:
        """Get cache performance metrics"""

        if layer:
            metrics = self.metrics[layer]
            return {
                "layer": layer.value,
                "hit_ratio": metrics.hit_ratio,
                "hits": metrics.hits,
                "misses": metrics.misses,
                "avg_latency": metrics.avg_latency,
                "memory_usage": metrics.memory_usage
            }

        # Aggregate metrics
        total_hits = sum(m.hits for m in self.metrics.values())
        total_misses = sum(m.misses for m in self.metrics.values())

        return {
            "overall_hit_ratio": total_hits / (total_hits + total_misses) if (total_hits + total_misses) > 0 else 0,
            "total_hits": total_hits,
            "total_misses": total_misses,
            "layers": {
                layer.value: {
                    "hit_ratio": metrics.hit_ratio,
                    "hits": metrics.hits,
                    "misses": metrics.misses
                }
                for layer, metrics in self.metrics.items()
            }
        }

    async def _get_from_layer(
        self,
        layer: CacheLayer,
        key: str
    ) -> Optional[Any]:
        """Get value from specific cache layer"""

        try:
            cache = self.layers.get(layer)
            if cache:
                return await cache.get(key)
        except Exception as e:
            logger.error(f"cache_get_error", layer=layer.value, error=str(e))

        return None

    async def _set_in_layer(
        self,
        layer: CacheLayer,
        key: str,
        value: Any,
        ttl: int
    ) -> bool:
        """Set value in specific cache layer"""

        try:
            cache = self.layers.get(layer)
            if cache:
                return await cache.set(key, value, ttl=ttl)
        except Exception as e:
            logger.error(f"cache_set_error", layer=layer.value, error=str(e))

        return False

    async def _get_from_cdn(self, key: str) -> Optional[Any]:
        """Get value from CDN edge cache"""

        # Simulate CDN fetch (in production, use actual CDN API)
        cdn_key = f"cdn:{key}"
        value = await self.redis.get(cdn_key)

        if value:
            return pickle.loads(value)

        return None

    async def _invalidate_cdn(self, pattern: str) -> None:
        """Invalidate CDN cache"""

        # In production, call CDN purge API
        logger.info("cdn_invalidation", pattern=pattern)

        # Simulate CDN invalidation
        keys = await self.redis.keys(f"cdn:{pattern}*")
        if keys:
            await self.redis.delete(*keys)

    async def _write_through(
        self,
        key: str,
        value: Any,
        ttl: Optional[int]
    ) -> None:
        """Write-through caching strategy"""

        # Write to all layers synchronously
        tasks = [
            self._set_in_layer(CacheLayer.L1_MEMORY, key, value, ttl or 60),
            self._set_in_layer(CacheLayer.L2_REDIS, key, value, ttl or 300),
            self._set_in_cdn(key, value, ttl or 3600)
        ]

        await asyncio.gather(*tasks)

    async def _write_behind(
        self,
        key: str,
        value: Any,
        ttl: Optional[int]
    ) -> None:
        """Write-behind caching strategy"""

        # Write to L1 immediately
        await self._set_in_layer(CacheLayer.L1_MEMORY, key, value, ttl or 60)

        # Queue writes to other layers
        await self.invalidation_queue.put({
            "action": "set",
            "key": key,
            "value": value,
            "ttl": ttl
        })

        # Process queue asynchronously
        asyncio.create_task(self._process_write_queue())

    async def _cache_aside(
        self,
        key: str,
        value: Any,
        ttl: Optional[int]
    ) -> None:
        """Cache-aside strategy"""

        # Only cache if explicitly requested
        await self._set_in_layer(CacheLayer.L2_REDIS, key, value, ttl or 300)

    async def _set_in_cdn(self, key: str, value: Any, ttl: int) -> None:
        """Set value in CDN cache"""

        # Simulate CDN set (in production, use actual CDN API)
        cdn_key = f"cdn:{key}"
        serialized = pickle.dumps(value)
        await self.redis.set(cdn_key, serialized, ex=ttl)

    async def _backfill_cache(self, key: str, value: Any) -> None:
        """Backfill higher cache layers"""

        tasks = [
            self._set_in_layer(CacheLayer.L1_MEMORY, key, value, 60),
            self._set_in_layer(CacheLayer.L2_REDIS, key, value, 300)
        ]

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _invalidate_layer(
        self,
        layer: CacheLayer,
        pattern: str
    ) -> int:
        """Invalidate entries in specific layer"""

        count = 0

        try:
            cache = self.layers.get(layer)
            if cache and hasattr(cache, 'clear'):
                # For pattern matching, need to iterate keys
                # This is simplified - production would need better implementation
                await cache.clear()
                count = 1  # Approximation
        except Exception as e:
            logger.error(f"invalidation_error", layer=layer.value, error=str(e))

        return count

    async def _broadcast_invalidation(self, pattern: str) -> None:
        """Broadcast cache invalidation to other nodes"""

        await self.redis.publish("cache_invalidation", json.dumps({
            "pattern": pattern,
            "timestamp": datetime.utcnow().isoformat(),
            "node": "current_node_id"
        }))

    async def _prefetch_worker(self) -> None:
        """Worker to handle cache prefetching"""

        while True:
            try:
                priority, query = await self.prefetch_queue.get()

                # Fetch and cache the data
                key = query.get("key")
                fetch_func = query.get("fetch_func")
                ttl = query.get("ttl", 300)

                if key and fetch_func:
                    value = await fetch_func()
                    await self.set(key, value, ttl)

                await asyncio.sleep(0.1)  # Rate limiting

            except Exception as e:
                logger.error("prefetch_error", error=str(e))
                await asyncio.sleep(1)

    async def _process_write_queue(self) -> None:
        """Process write-behind queue"""

        batch = []
        while True:
            try:
                # Batch operations for efficiency
                while len(batch) < 10:
                    try:
                        operation = await asyncio.wait_for(
                            self.invalidation_queue.get(),
                            timeout=1.0
                        )
                        batch.append(operation)
                    except asyncio.TimeoutError:
                        break

                if batch:
                    # Process batch
                    for op in batch:
                        if op["action"] == "set":
                            await self._set_in_layer(
                                CacheLayer.L2_REDIS,
                                op["key"],
                                op["value"],
                                op["ttl"]
                            )

                    batch.clear()

            except Exception as e:
                logger.error("write_queue_error", error=str(e))
                await asyncio.sleep(1)

    def _generate_key(self, key: str) -> str:
        """Generate cache key with versioning"""

        # Add version prefix for cache busting
        version = "v1"
        return f"{version}:{key}"

    async def _record_hit(self, layer: CacheLayer, start_time: datetime) -> None:
        """Record cache hit metrics"""

        latency = (datetime.utcnow() - start_time).total_seconds() * 1000
        metrics = self.metrics[layer]

        metrics.hits += 1
        metrics.avg_latency = (metrics.avg_latency * (metrics.hits - 1) + latency) / metrics.hits
        metrics.hit_ratio = metrics.hits / (metrics.hits + metrics.misses) if (metrics.hits + metrics.misses) > 0 else 0

    async def _record_miss(self, start_time: datetime) -> None:
        """Record cache miss"""

        for metrics in self.metrics.values():
            metrics.misses += 1
            metrics.hit_ratio = metrics.hits / (metrics.hits + metrics.misses) if (metrics.hits + metrics.misses) > 0 else 0


class SmartCacheWarmer:
    """Intelligent cache warming based on usage patterns"""

    def __init__(self, cache: MultiLayerCache, redis_client: aioredis.Redis):
        self.cache = cache
        self.redis = redis_client
        self.patterns = {}
        self.predictions = {}

    async def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze access patterns for intelligent warming"""

        # Get recent access logs
        access_logs = await self._get_access_logs()

        # Identify patterns
        patterns = {
            "time_based": self._analyze_time_patterns(access_logs),
            "user_based": self._analyze_user_patterns(access_logs),
            "content_based": self._analyze_content_patterns(access_logs)
        }

        self.patterns = patterns
        return patterns

    async def warm_predicted_content(self) -> int:
        """Warm cache with predicted content"""

        predictions = await self._predict_next_requests()
        warmed = 0

        for prediction in predictions:
            if prediction["confidence"] > 0.7:
                await self.cache.warm_cache([{
                    "key": prediction["key"],
                    "fetch_func": prediction["fetch_func"],
                    "ttl": prediction["ttl"]
                }], priority=int(prediction["confidence"] * 10))
                warmed += 1

        logger.info("cache_warmed", count=warmed)
        return warmed

    async def _get_access_logs(self) -> List[Dict[str, Any]]:
        """Get recent cache access logs"""

        # Fetch from Redis (simplified)
        logs = []
        keys = await self.redis.keys("access_log:*")

        for key in keys[-1000:]:  # Last 1000 accesses
            log_data = await self.redis.get(key)
            if log_data:
                logs.append(json.loads(log_data))

        return logs

    def _analyze_time_patterns(self, logs: List[Dict]) -> Dict[str, Any]:
        """Analyze time-based access patterns"""

        hourly_access = {}

        for log in logs:
            hour = datetime.fromisoformat(log["timestamp"]).hour
            hourly_access[hour] = hourly_access.get(hour, 0) + 1

        # Identify peak hours
        peak_hours = sorted(hourly_access.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            "peak_hours": [h[0] for h in peak_hours],
            "hourly_distribution": hourly_access
        }

    def _analyze_user_patterns(self, logs: List[Dict]) -> Dict[str, Any]:
        """Analyze user-based access patterns"""

        user_access = {}

        for log in logs:
            user = log.get("user_id", "anonymous")
            user_access[user] = user_access.get(user, [])
            user_access[user].append(log["key"])

        # Identify power users
        power_users = sorted(user_access.items(), key=lambda x: len(x[1]), reverse=True)[:10]

        return {
            "power_users": [u[0] for u in power_users],
            "access_patterns": {u[0]: u[1][:5] for u in power_users}
        }

    def _analyze_content_patterns(self, logs: List[Dict]) -> Dict[str, Any]:
        """Analyze content access patterns"""

        content_access = {}

        for log in logs:
            content_type = log.get("content_type", "unknown")
            content_access[content_type] = content_access.get(content_type, 0) + 1

        return {
            "popular_content": sorted(content_access.items(), key=lambda x: x[1], reverse=True)
        }

    async def _predict_next_requests(self) -> List[Dict[str, Any]]:
        """Predict next likely cache requests"""

        predictions = []
        current_hour = datetime.utcnow().hour

        # Time-based predictions
        if current_hour in self.patterns.get("time_based", {}).get("peak_hours", []):
            # Add frequently accessed content during peak hours
            predictions.extend([
                {
                    "key": "dashboard:metrics",
                    "confidence": 0.9,
                    "fetch_func": lambda: self._fetch_dashboard_metrics(),
                    "ttl": 60
                },
                {
                    "key": "popular:deals",
                    "confidence": 0.85,
                    "fetch_func": lambda: self._fetch_popular_deals(),
                    "ttl": 300
                }
            ])

        # User-based predictions
        power_users = self.patterns.get("user_based", {}).get("power_users", [])
        for user in power_users[:5]:
            predictions.append({
                "key": f"user:{user}:dashboard",
                "confidence": 0.8,
                "fetch_func": lambda u=user: self._fetch_user_dashboard(u),
                "ttl": 120
            })

        return predictions

    async def _fetch_dashboard_metrics(self) -> Dict[str, Any]:
        """Fetch dashboard metrics (placeholder)"""
        return {"metrics": "data"}

    async def _fetch_popular_deals(self) -> List[Dict[str, Any]]:
        """Fetch popular deals (placeholder)"""
        return [{"deal": "data"}]

    async def _fetch_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Fetch user dashboard (placeholder)"""
        return {"user": user_id, "dashboard": "data"}


class CDNIntegration:
    """CDN integration for edge caching"""

    def __init__(self, cdn_provider: str = "cloudflare"):
        self.provider = cdn_provider
        self.edge_locations = [
            "us-east-1", "us-west-1", "eu-west-1",
            "ap-southeast-1", "ap-northeast-1"
        ]

    async def push_to_edge(
        self,
        key: str,
        content: bytes,
        ttl: int = 3600
    ) -> bool:
        """Push content to CDN edge locations"""

        tasks = []
        for location in self.edge_locations:
            tasks.append(self._push_to_location(location, key, content, ttl))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        success = sum(1 for r in results if r is True)
        logger.info("cdn_push_complete", key=key, locations=success)

        return success == len(self.edge_locations)

    async def purge_from_edge(self, pattern: str) -> bool:
        """Purge content from CDN"""

        if self.provider == "cloudflare":
            return await self._cloudflare_purge(pattern)
        elif self.provider == "fastly":
            return await self._fastly_purge(pattern)

        return False

    async def get_edge_metrics(self) -> Dict[str, Any]:
        """Get CDN performance metrics"""

        return {
            "cache_hit_ratio": 0.92,  # Placeholder
            "bandwidth_saved": "1.2TB",
            "avg_response_time": "45ms",
            "edge_locations": len(self.edge_locations),
            "requests_served": 1500000
        }

    async def _push_to_location(
        self,
        location: str,
        key: str,
        content: bytes,
        ttl: int
    ) -> bool:
        """Push content to specific edge location"""

        # Simulate CDN push
        await asyncio.sleep(0.01)
        return True

    async def _cloudflare_purge(self, pattern: str) -> bool:
        """Cloudflare cache purge"""

        # In production, call Cloudflare API
        logger.info("cloudflare_purge", pattern=pattern)
        return True

    async def _fastly_purge(self, pattern: str) -> bool:
        """Fastly cache purge"""

        # In production, call Fastly API
        logger.info("fastly_purge", pattern=pattern)
        return True


class CacheKeyGenerator:
    """Intelligent cache key generation"""

    @staticmethod
    def generate_query_key(
        query: str,
        params: Dict[str, Any],
        user_context: Optional[Dict] = None
    ) -> str:
        """Generate cache key for database query"""

        # Create stable hash
        key_parts = [
            query,
            json.dumps(params, sort_keys=True)
        ]

        if user_context:
            # Add user-specific context if needed
            key_parts.append(json.dumps(user_context, sort_keys=True))

        key_string = ":".join(key_parts)
        hash_digest = hashlib.sha256(key_string.encode()).hexdigest()[:16]

        return f"query:{hash_digest}"

    @staticmethod
    def generate_api_key(
        endpoint: str,
        method: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> str:
        """Generate cache key for API response"""

        key_parts = [
            endpoint,
            method
        ]

        if params:
            key_parts.append(json.dumps(params, sort_keys=True))

        if headers:
            # Only include relevant headers
            relevant_headers = {
                k: v for k, v in headers.items()
                if k.lower() in ["authorization", "accept", "content-type"]
            }
            key_parts.append(json.dumps(relevant_headers, sort_keys=True))

        key_string = ":".join(key_parts)
        hash_digest = hashlib.sha256(key_string.encode()).hexdigest()[:16]

        return f"api:{hash_digest}"

    @staticmethod
    def generate_user_key(user_id: str, resource: str) -> str:
        """Generate user-specific cache key"""
        return f"user:{user_id}:{resource}"

    @staticmethod
    def generate_tenant_key(tenant_id: str, resource: str) -> str:
        """Generate tenant-specific cache key"""
        return f"tenant:{tenant_id}:{resource}"