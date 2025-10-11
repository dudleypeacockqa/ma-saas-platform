"""Performance monitoring and optimization for the M&A platform"""

import time
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import wraps
import statistics
import structlog
from contextlib import asynccontextmanager

logger = structlog.get_logger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring"""
    request_count: int = 0
    total_time: float = 0
    min_time: float = float('inf')
    max_time: float = 0
    response_times: List[float] = field(default_factory=list)
    errors: int = 0
    last_reset: datetime = field(default_factory=datetime.utcnow)

    @property
    def avg_time(self) -> float:
        """Calculate average response time"""
        if self.request_count == 0:
            return 0
        return self.total_time / self.request_count

    @property
    def p95_time(self) -> float:
        """Calculate 95th percentile response time"""
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.95)
        return sorted_times[min(index, len(sorted_times) - 1)]

    @property
    def p99_time(self) -> float:
        """Calculate 99th percentile response time"""
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.99)
        return sorted_times[min(index, len(sorted_times) - 1)]

    def record_request(self, duration: float):
        """Record a request's performance"""
        self.request_count += 1
        self.total_time += duration
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)
        self.response_times.append(duration)

        # Keep only last 1000 response times for percentile calculation
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]

    def record_error(self):
        """Record an error"""
        self.errors += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            "request_count": self.request_count,
            "avg_response_time_ms": self.avg_time * 1000,
            "min_response_time_ms": self.min_time * 1000 if self.min_time != float('inf') else 0,
            "max_response_time_ms": self.max_time * 1000,
            "p95_response_time_ms": self.p95_time * 1000,
            "p99_response_time_ms": self.p99_time * 1000,
            "error_count": self.errors,
            "error_rate": self.errors / max(self.request_count, 1),
            "uptime_minutes": (datetime.utcnow() - self.last_reset).total_seconds() / 60
        }


class PerformanceMonitor:
    """
    Comprehensive performance monitoring for the platform.
    Tracks API, database, and AI service performance.
    """

    def __init__(self):
        self.metrics: Dict[str, PerformanceMetrics] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.thresholds = {
            "api_response_ms": 200,
            "db_query_ms": 50,
            "ai_processing_ms": 1000,
            "error_rate": 0.01
        }

    def get_or_create_metrics(self, category: str) -> PerformanceMetrics:
        """Get or create metrics for a category"""
        if category not in self.metrics:
            self.metrics[category] = PerformanceMetrics()
        return self.metrics[category]

    async def record_performance(
        self,
        category: str,
        duration: float,
        success: bool = True
    ):
        """Record performance metrics"""
        metrics = self.get_or_create_metrics(category)

        if success:
            metrics.record_request(duration)
        else:
            metrics.record_error()

        # Check thresholds and create alerts
        await self._check_thresholds(category, duration)

    async def _check_thresholds(self, category: str, duration: float):
        """Check if performance exceeds thresholds"""
        duration_ms = duration * 1000

        if category == "api" and duration_ms > self.thresholds["api_response_ms"]:
            await self._create_alert(
                "API_SLOW_RESPONSE",
                f"API response time {duration_ms:.2f}ms exceeds threshold",
                "warning"
            )
        elif category == "database" and duration_ms > self.thresholds["db_query_ms"]:
            await self._create_alert(
                "DB_SLOW_QUERY",
                f"Database query time {duration_ms:.2f}ms exceeds threshold",
                "warning"
            )
        elif category == "ai" and duration_ms > self.thresholds["ai_processing_ms"]:
            await self._create_alert(
                "AI_SLOW_PROCESSING",
                f"AI processing time {duration_ms:.2f}ms exceeds threshold",
                "warning"
            )

    async def _create_alert(self, alert_type: str, message: str, severity: str):
        """Create performance alert"""
        alert = {
            "type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.alerts.append(alert)
        logger.warning("Performance alert", **alert)

        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get performance dashboard data"""
        return {
            "metrics": {
                category: metrics.get_stats()
                for category, metrics in self.metrics.items()
            },
            "alerts": self.alerts[-10:],  # Last 10 alerts
            "health_status": self._calculate_health_status(),
            "recommendations": self._generate_recommendations()
        }

    def _calculate_health_status(self) -> str:
        """Calculate overall system health status"""
        if not self.metrics:
            return "unknown"

        # Check error rates
        for metrics in self.metrics.values():
            if metrics.error_rate > 0.05:
                return "critical"
            elif metrics.error_rate > 0.01:
                return "warning"

        # Check response times
        api_metrics = self.metrics.get("api")
        if api_metrics:
            if api_metrics.p95_time * 1000 > 500:
                return "warning"

        return "healthy"

    def _generate_recommendations(self) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []

        # Check API performance
        api_metrics = self.metrics.get("api")
        if api_metrics and api_metrics.p95_time * 1000 > 200:
            recommendations.append("Consider implementing additional caching for API endpoints")

        # Check database performance
        db_metrics = self.metrics.get("database")
        if db_metrics and db_metrics.avg_time * 1000 > 30:
            recommendations.append("Database queries need optimization - review slow query log")

        # Check error rates
        for category, metrics in self.metrics.items():
            if metrics.error_rate > 0.01:
                recommendations.append(f"High error rate in {category} - investigate root cause")

        return recommendations


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


# Performance tracking decorator
def track_performance(category: str = "api"):
    """
    Decorator to track function performance.
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            success = True

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.perf_counter() - start_time
                await performance_monitor.record_performance(category, duration, success)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            success = True

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.perf_counter() - start_time
                asyncio.create_task(
                    performance_monitor.record_performance(category, duration, success)
                )

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


@asynccontextmanager
async def track_operation(name: str, category: str = "operation"):
    """
    Context manager for tracking operation performance.
    """
    start_time = time.perf_counter()
    success = True

    try:
        yield
    except Exception:
        success = False
        raise
    finally:
        duration = time.perf_counter() - start_time
        await performance_monitor.record_performance(
            f"{category}:{name}",
            duration,
            success
        )


class QueryOptimizer:
    """
    Database query optimization helper.
    """

    def __init__(self):
        self.slow_queries: List[Dict[str, Any]] = []
        self.query_patterns: Dict[str, int] = {}

    def analyze_query(self, query: str, duration: float):
        """Analyze query performance"""
        if duration > 0.05:  # 50ms threshold
            self.slow_queries.append({
                "query": query,
                "duration_ms": duration * 1000,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Track query patterns
            pattern = self._extract_pattern(query)
            self.query_patterns[pattern] = self.query_patterns.get(pattern, 0) + 1

            # Keep only last 100 slow queries
            if len(self.slow_queries) > 100:
                self.slow_queries = self.slow_queries[-100:]

    def _extract_pattern(self, query: str) -> str:
        """Extract query pattern for analysis"""
        # Simple pattern extraction - could be enhanced
        if "SELECT" in query.upper():
            if "JOIN" in query.upper():
                return "SELECT_WITH_JOIN"
            return "SELECT"
        elif "INSERT" in query.upper():
            return "INSERT"
        elif "UPDATE" in query.upper():
            return "UPDATE"
        elif "DELETE" in query.upper():
            return "DELETE"
        return "OTHER"

    def get_optimization_suggestions(self) -> List[str]:
        """Get query optimization suggestions"""
        suggestions = []

        # Analyze slow queries
        if self.slow_queries:
            avg_duration = statistics.mean(q["duration_ms"] for q in self.slow_queries)
            if avg_duration > 100:
                suggestions.append(f"Average slow query time is {avg_duration:.2f}ms - review indexes")

        # Analyze patterns
        if self.query_patterns.get("SELECT_WITH_JOIN", 0) > 50:
            suggestions.append("High number of JOIN queries - consider denormalization")

        return suggestions


# Global query optimizer
query_optimizer = QueryOptimizer()


class LoadBalancer:
    """
    Simple load balancing for distributed operations.
    """

    def __init__(self, instances: List[str]):
        self.instances = instances
        self.current_index = 0
        self.instance_health: Dict[str, bool] = {
            instance: True for instance in instances
        }
        self.instance_load: Dict[str, int] = {
            instance: 0 for instance in instances
        }

    def get_next_instance(self) -> Optional[str]:
        """Get next healthy instance using round-robin"""
        healthy_instances = [
            inst for inst in self.instances
            if self.instance_health.get(inst, False)
        ]

        if not healthy_instances:
            logger.error("No healthy instances available")
            return None

        # Simple round-robin
        instance = healthy_instances[self.current_index % len(healthy_instances)]
        self.current_index += 1
        self.instance_load[instance] += 1

        return instance

    def mark_unhealthy(self, instance: str):
        """Mark instance as unhealthy"""
        self.instance_health[instance] = False
        logger.warning("Instance marked unhealthy", instance=instance)

    def mark_healthy(self, instance: str):
        """Mark instance as healthy"""
        self.instance_health[instance] = True
        logger.info("Instance marked healthy", instance=instance)

    def get_status(self) -> Dict[str, Any]:
        """Get load balancer status"""
        return {
            "instances": self.instances,
            "health": self.instance_health,
            "load": self.instance_load,
            "healthy_count": sum(1 for h in self.instance_health.values() if h)
        }


class CircuitBreaker:
    """
    Circuit breaker pattern for fault tolerance.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = "closed"

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning("Circuit breaker opened", failures=self.failure_count)

    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit"""
        if not self.last_failure_time:
            return False

        time_since_failure = (datetime.utcnow() - self.last_failure_time).seconds
        return time_since_failure >= self.recovery_timeout