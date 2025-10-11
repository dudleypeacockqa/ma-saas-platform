"""
Enterprise Auto-Scaling Configuration
Intelligent resource management for 10,000+ concurrent users
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import psutil
import aioredis
from prometheus_client import Counter, Gauge, Histogram
import structlog

logger = structlog.get_logger()


class ScalingTrigger(Enum):
    """Auto-scaling trigger types"""
    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_UTILIZATION = "memory_utilization"
    REQUEST_RATE = "request_rate"
    RESPONSE_TIME = "response_time"
    QUEUE_LENGTH = "queue_length"
    CUSTOM_METRIC = "custom_metric"
    PREDICTIVE = "predictive"


class ScalingAction(Enum):
    """Scaling action types"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    SCALE_OUT = "scale_out"
    SCALE_IN = "scale_in"
    NO_ACTION = "no_action"


@dataclass
class ScalingPolicy:
    """Auto-scaling policy configuration"""
    name: str
    trigger: ScalingTrigger
    threshold_up: float
    threshold_down: float
    cooldown_period: int  # seconds
    min_instances: int
    max_instances: int
    scale_increment: int
    evaluation_periods: int
    breach_duration: int  # seconds


@dataclass
class ResourceMetrics:
    """Current resource metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    request_rate: float
    avg_response_time: float
    queue_length: int
    active_connections: int
    error_rate: float
    throughput: float


# Prometheus metrics
scaling_events = Counter('autoscaling_events_total', 'Total scaling events', ['action', 'trigger'])
current_instances = Gauge('autoscaling_current_instances', 'Current number of instances')
resource_utilization = Gauge('resource_utilization_percent', 'Resource utilization', ['resource'])
scaling_latency = Histogram('autoscaling_latency_seconds', 'Scaling operation latency')


class IntelligentAutoScaler:
    """Intelligent auto-scaling system with predictive capabilities"""

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.policies = self._initialize_policies()
        self.current_instances = 2  # Starting instances
        self.last_scale_time = {}
        self.metrics_history = []
        self.prediction_model = PredictiveScaler()

    def _initialize_policies(self) -> List[ScalingPolicy]:
        """Initialize scaling policies"""
        return [
            ScalingPolicy(
                name="cpu_scaling",
                trigger=ScalingTrigger.CPU_UTILIZATION,
                threshold_up=70,
                threshold_down=30,
                cooldown_period=300,
                min_instances=2,
                max_instances=100,
                scale_increment=2,
                evaluation_periods=2,
                breach_duration=120
            ),
            ScalingPolicy(
                name="memory_scaling",
                trigger=ScalingTrigger.MEMORY_UTILIZATION,
                threshold_up=80,
                threshold_down=40,
                cooldown_period=300,
                min_instances=2,
                max_instances=100,
                scale_increment=1,
                evaluation_periods=3,
                breach_duration=180
            ),
            ScalingPolicy(
                name="response_time_scaling",
                trigger=ScalingTrigger.RESPONSE_TIME,
                threshold_up=200,  # 200ms
                threshold_down=50,  # 50ms
                cooldown_period=180,
                min_instances=2,
                max_instances=100,
                scale_increment=3,
                evaluation_periods=2,
                breach_duration=60
            ),
            ScalingPolicy(
                name="request_rate_scaling",
                trigger=ScalingTrigger.REQUEST_RATE,
                threshold_up=1000,  # requests per second
                threshold_down=100,
                cooldown_period=240,
                min_instances=2,
                max_instances=100,
                scale_increment=2,
                evaluation_periods=2,
                breach_duration=90
            ),
            ScalingPolicy(
                name="predictive_scaling",
                trigger=ScalingTrigger.PREDICTIVE,
                threshold_up=0.8,  # 80% probability of high load
                threshold_down=0.2,
                cooldown_period=600,
                min_instances=2,
                max_instances=100,
                scale_increment=4,
                evaluation_periods=1,
                breach_duration=0
            )
        ]

    async def monitor_and_scale(self) -> None:
        """Main monitoring and scaling loop"""
        while True:
            try:
                # Collect current metrics
                metrics = await self._collect_metrics()
                self.metrics_history.append(metrics)

                # Evaluate scaling policies
                scaling_decision = await self._evaluate_policies(metrics)

                # Execute scaling action
                if scaling_decision != ScalingAction.NO_ACTION:
                    await self._execute_scaling(scaling_decision, metrics)

                # Update metrics
                current_instances.set(self.current_instances)
                resource_utilization.labels(resource='cpu').set(metrics.cpu_percent)
                resource_utilization.labels(resource='memory').set(metrics.memory_percent)

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error("auto_scaling_error", error=str(e))
                await asyncio.sleep(60)

    async def _collect_metrics(self) -> ResourceMetrics:
        """Collect current system metrics"""

        # CPU and Memory from psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent

        # Application metrics from Redis
        request_rate = await self._get_metric("request_rate") or 0
        avg_response_time = await self._get_metric("avg_response_time") or 0
        queue_length = await self._get_metric("queue_length") or 0
        active_connections = await self._get_metric("active_connections") or 0
        error_rate = await self._get_metric("error_rate") or 0
        throughput = await self._get_metric("throughput") or 0

        return ResourceMetrics(
            timestamp=datetime.utcnow(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            request_rate=request_rate,
            avg_response_time=avg_response_time,
            queue_length=queue_length,
            active_connections=active_connections,
            error_rate=error_rate,
            throughput=throughput
        )

    async def _evaluate_policies(self, metrics: ResourceMetrics) -> ScalingAction:
        """Evaluate all scaling policies"""

        scaling_votes = {
            ScalingAction.SCALE_UP: 0,
            ScalingAction.SCALE_DOWN: 0,
            ScalingAction.NO_ACTION: 0
        }

        for policy in self.policies:
            # Check cooldown period
            if not self._is_cooldown_expired(policy):
                continue

            # Evaluate policy
            action = await self._evaluate_single_policy(policy, metrics)

            if action != ScalingAction.NO_ACTION:
                scaling_votes[action] += self._get_policy_weight(policy)

        # Predictive scaling
        predictive_action = await self._evaluate_predictive_scaling(metrics)
        if predictive_action != ScalingAction.NO_ACTION:
            scaling_votes[predictive_action] += 3  # Higher weight for predictions

        # Determine final action
        if scaling_votes[ScalingAction.SCALE_UP] > scaling_votes[ScalingAction.SCALE_DOWN]:
            return ScalingAction.SCALE_UP
        elif scaling_votes[ScalingAction.SCALE_DOWN] > scaling_votes[ScalingAction.SCALE_UP]:
            return ScalingAction.SCALE_DOWN
        else:
            return ScalingAction.NO_ACTION

    async def _evaluate_single_policy(
        self,
        policy: ScalingPolicy,
        metrics: ResourceMetrics
    ) -> ScalingAction:
        """Evaluate a single scaling policy"""

        metric_value = self._get_metric_value(policy.trigger, metrics)

        # Check if metric breaches thresholds
        if metric_value > policy.threshold_up:
            # Check if we need to scale up
            if self.current_instances < policy.max_instances:
                # Verify breach duration
                if await self._check_breach_duration(policy, metric_value, True):
                    return ScalingAction.SCALE_UP

        elif metric_value < policy.threshold_down:
            # Check if we can scale down
            if self.current_instances > policy.min_instances:
                # Verify breach duration
                if await self._check_breach_duration(policy, metric_value, False):
                    return ScalingAction.SCALE_DOWN

        return ScalingAction.NO_ACTION

    async def _evaluate_predictive_scaling(self, metrics: ResourceMetrics) -> ScalingAction:
        """Evaluate predictive scaling using ML model"""

        # Use historical data to predict future load
        if len(self.metrics_history) < 10:
            return ScalingAction.NO_ACTION

        # Predict load for next 15 minutes
        predicted_load = await self.prediction_model.predict_load(
            self.metrics_history,
            horizon_minutes=15
        )

        # Determine if we need to scale preemptively
        if predicted_load > 0.8:  # High load predicted
            if self.current_instances < 20:
                logger.info("predictive_scaling_triggered",
                          predicted_load=predicted_load,
                          action="scale_up")
                return ScalingAction.SCALE_UP
        elif predicted_load < 0.3:  # Low load predicted
            if self.current_instances > 4:
                logger.info("predictive_scaling_triggered",
                          predicted_load=predicted_load,
                          action="scale_down")
                return ScalingAction.SCALE_DOWN

        return ScalingAction.NO_ACTION

    async def _execute_scaling(
        self,
        action: ScalingAction,
        metrics: ResourceMetrics
    ) -> None:
        """Execute scaling action"""

        start_time = datetime.utcnow()

        try:
            if action == ScalingAction.SCALE_UP:
                await self._scale_up(metrics)
            elif action == ScalingAction.SCALE_DOWN:
                await self._scale_down(metrics)

            # Record scaling event
            scaling_events.labels(
                action=action.value,
                trigger=self._identify_trigger(metrics)
            ).inc()

            # Record latency
            latency = (datetime.utcnow() - start_time).total_seconds()
            scaling_latency.observe(latency)

            logger.info("scaling_executed",
                       action=action.value,
                       instances=self.current_instances,
                       latency=latency)

        except Exception as e:
            logger.error("scaling_execution_failed",
                        action=action.value,
                        error=str(e))

    async def _scale_up(self, metrics: ResourceMetrics) -> None:
        """Scale up instances"""

        # Calculate optimal increment
        increment = self._calculate_scale_increment(metrics, True)

        new_instances = min(
            self.current_instances + increment,
            100  # Max instances
        )

        # Execute scaling on infrastructure
        await self._provision_instances(new_instances - self.current_instances)

        self.current_instances = new_instances
        self.last_scale_time["up"] = datetime.utcnow()

        # Update Redis
        await self.redis.set("current_instances", self.current_instances)

    async def _scale_down(self, metrics: ResourceMetrics) -> None:
        """Scale down instances"""

        # Calculate optimal decrement
        decrement = self._calculate_scale_increment(metrics, False)

        new_instances = max(
            self.current_instances - decrement,
            2  # Min instances
        )

        # Execute scaling on infrastructure
        await self._deprovision_instances(self.current_instances - new_instances)

        self.current_instances = new_instances
        self.last_scale_time["down"] = datetime.utcnow()

        # Update Redis
        await self.redis.set("current_instances", self.current_instances)

    async def _provision_instances(self, count: int) -> None:
        """Provision new instances"""

        # In production, this would interface with cloud provider APIs
        # For now, simulate provisioning

        logger.info("provisioning_instances", count=count)

        # Simulate provisioning time
        await asyncio.sleep(0.1 * count)

        # Update load balancer
        await self._update_load_balancer()

    async def _deprovision_instances(self, count: int) -> None:
        """Deprovision instances"""

        # Graceful shutdown process
        logger.info("deprovisioning_instances", count=count)

        # Drain connections
        await self._drain_connections(count)

        # Simulate deprovisioning
        await asyncio.sleep(0.05 * count)

        # Update load balancer
        await self._update_load_balancer()

    async def _update_load_balancer(self) -> None:
        """Update load balancer configuration"""

        # Update backend pool
        await self.redis.hset(
            "load_balancer_config",
            "backend_count",
            self.current_instances
        )

    async def _drain_connections(self, instance_count: int) -> None:
        """Gracefully drain connections from instances"""

        # Mark instances for draining
        await self.redis.sadd(
            "draining_instances",
            *[f"instance_{i}" for i in range(instance_count)]
        )

        # Wait for connections to drain (max 30 seconds)
        await asyncio.sleep(min(30, instance_count * 2))

    def _calculate_scale_increment(
        self,
        metrics: ResourceMetrics,
        scale_up: bool
    ) -> int:
        """Calculate optimal scaling increment"""

        base_increment = 2

        # Adjust based on severity
        if scale_up:
            if metrics.cpu_percent > 90 or metrics.avg_response_time > 500:
                return base_increment * 3  # Aggressive scaling
            elif metrics.cpu_percent > 80 or metrics.avg_response_time > 300:
                return base_increment * 2  # Moderate scaling
            else:
                return base_increment  # Conservative scaling
        else:
            # Scale down more conservatively
            if metrics.cpu_percent < 20 and metrics.avg_response_time < 30:
                return base_increment * 2  # Can scale down more
            else:
                return 1  # Conservative scale down

    def _get_metric_value(
        self,
        trigger: ScalingTrigger,
        metrics: ResourceMetrics
    ) -> float:
        """Get metric value for trigger type"""

        mapping = {
            ScalingTrigger.CPU_UTILIZATION: metrics.cpu_percent,
            ScalingTrigger.MEMORY_UTILIZATION: metrics.memory_percent,
            ScalingTrigger.REQUEST_RATE: metrics.request_rate,
            ScalingTrigger.RESPONSE_TIME: metrics.avg_response_time,
            ScalingTrigger.QUEUE_LENGTH: metrics.queue_length
        }

        return mapping.get(trigger, 0)

    def _is_cooldown_expired(self, policy: ScalingPolicy) -> bool:
        """Check if cooldown period has expired"""

        last_scale = self.last_scale_time.get(policy.name)
        if not last_scale:
            return True

        elapsed = (datetime.utcnow() - last_scale).total_seconds()
        return elapsed >= policy.cooldown_period

    async def _check_breach_duration(
        self,
        policy: ScalingPolicy,
        metric_value: float,
        is_upper_breach: bool
    ) -> bool:
        """Check if threshold breach persists for required duration"""

        breach_key = f"breach:{policy.name}:{is_upper_breach}"

        # Check if breach is ongoing
        breach_start = await self.redis.get(breach_key)

        if breach_start:
            # Check duration
            start_time = datetime.fromisoformat(breach_start)
            duration = (datetime.utcnow() - start_time).total_seconds()

            if duration >= policy.breach_duration:
                # Clear breach and return true
                await self.redis.delete(breach_key)
                return True
        else:
            # Start tracking breach
            await self.redis.set(
                breach_key,
                datetime.utcnow().isoformat(),
                ex=policy.breach_duration * 2
            )

        return False

    def _get_policy_weight(self, policy: ScalingPolicy) -> int:
        """Get policy weight for voting"""

        weights = {
            ScalingTrigger.RESPONSE_TIME: 3,  # Highest priority
            ScalingTrigger.CPU_UTILIZATION: 2,
            ScalingTrigger.MEMORY_UTILIZATION: 2,
            ScalingTrigger.REQUEST_RATE: 2,
            ScalingTrigger.QUEUE_LENGTH: 1
        }

        return weights.get(policy.trigger, 1)

    def _identify_trigger(self, metrics: ResourceMetrics) -> str:
        """Identify primary trigger for scaling"""

        if metrics.avg_response_time > 200:
            return "response_time"
        elif metrics.cpu_percent > 70:
            return "cpu"
        elif metrics.memory_percent > 80:
            return "memory"
        elif metrics.request_rate > 1000:
            return "request_rate"
        else:
            return "unknown"

    async def _get_metric(self, key: str) -> Optional[float]:
        """Get metric from Redis"""

        value = await self.redis.get(f"metric:{key}")
        return float(value) if value else None


class PredictiveScaler:
    """Machine learning based predictive scaler"""

    def __init__(self):
        self.model = None
        self.scaler = None

    async def predict_load(
        self,
        metrics_history: List[ResourceMetrics],
        horizon_minutes: int = 15
    ) -> float:
        """Predict future load using historical metrics"""

        if len(metrics_history) < 10:
            return 0.5  # Default to medium load

        # Extract features from recent history
        recent_metrics = metrics_history[-20:]  # Last 10 minutes

        features = self._extract_features(recent_metrics)

        # Simple prediction based on trends
        cpu_trend = self._calculate_trend([m.cpu_percent for m in recent_metrics])
        request_trend = self._calculate_trend([m.request_rate for m in recent_metrics])
        response_trend = self._calculate_trend([m.avg_response_time for m in recent_metrics])

        # Combine trends with weights
        predicted_load = (
            cpu_trend * 0.3 +
            request_trend * 0.4 +
            response_trend * 0.3
        )

        # Add time-based patterns (e.g., daily peaks)
        hour = datetime.utcnow().hour
        if 9 <= hour <= 11 or 14 <= hour <= 16:  # Business hours peaks
            predicted_load *= 1.3
        elif 0 <= hour <= 6:  # Night time
            predicted_load *= 0.5

        # Normalize to 0-1 range
        return max(0, min(1, predicted_load))

    def _extract_features(self, metrics: List[ResourceMetrics]) -> List[float]:
        """Extract features for ML model"""

        features = []

        # Average metrics
        features.append(sum(m.cpu_percent for m in metrics) / len(metrics))
        features.append(sum(m.memory_percent for m in metrics) / len(metrics))
        features.append(sum(m.request_rate for m in metrics) / len(metrics))
        features.append(sum(m.avg_response_time for m in metrics) / len(metrics))

        # Variance (volatility)
        cpu_values = [m.cpu_percent for m in metrics]
        features.append(self._variance(cpu_values))

        # Trend
        features.append(self._calculate_trend(cpu_values))

        return features

    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend from values"""

        if len(values) < 2:
            return 0.5

        # Simple linear regression
        n = len(values)
        x = list(range(n))

        x_mean = sum(x) / n
        y_mean = sum(values) / n

        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.5

        slope = numerator / denominator

        # Normalize slope to 0-1 range
        # Positive slope indicates increasing load
        normalized = (slope + 10) / 20  # Assuming slope range of -10 to 10

        return max(0, min(1, normalized))

    def _variance(self, values: List[float]) -> float:
        """Calculate variance of values"""

        if not values:
            return 0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)

        return variance


class ResourceOptimizer:
    """Optimize resource allocation"""

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client

    async def optimize_resources(self, metrics: ResourceMetrics) -> Dict[str, Any]:
        """Optimize resource allocation based on current metrics"""

        optimizations = {}

        # CPU optimization
        if metrics.cpu_percent > 80:
            optimizations["cpu"] = {
                "action": "throttle_background_tasks",
                "target_reduction": 20
            }

        # Memory optimization
        if metrics.memory_percent > 85:
            optimizations["memory"] = {
                "action": "trigger_garbage_collection",
                "cache_eviction": "aggressive"
            }

        # Connection pool optimization
        if metrics.active_connections > 5000:
            optimizations["connections"] = {
                "action": "expand_connection_pool",
                "new_size": metrics.active_connections * 1.2
            }

        # Queue optimization
        if metrics.queue_length > 1000:
            optimizations["queue"] = {
                "action": "increase_workers",
                "additional_workers": max(2, metrics.queue_length // 500)
            }

        return optimizations

    async def apply_optimizations(self, optimizations: Dict[str, Any]) -> None:
        """Apply resource optimizations"""

        for resource, optimization in optimizations.items():
            logger.info(f"applying_optimization",
                       resource=resource,
                       optimization=optimization)

            # Store optimization in Redis for workers to pick up
            await self.redis.hset(
                "resource_optimizations",
                resource,
                str(optimization)
            )


class LoadBalancer:
    """Intelligent load balancing"""

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.health_checks = {}
        self.instance_loads = {}

    async def route_request(self, request_type: str) -> str:
        """Route request to optimal instance"""

        # Get available instances
        instances = await self._get_healthy_instances()

        if not instances:
            raise Exception("No healthy instances available")

        # Select instance based on routing algorithm
        if request_type == "heavy":
            # Route to least loaded instance for heavy requests
            instance = await self._select_least_loaded(instances)
        elif request_type == "realtime":
            # Route to fastest responding instance for realtime
            instance = await self._select_fastest(instances)
        else:
            # Round-robin for normal requests
            instance = await self._round_robin(instances)

        # Update instance load
        await self._update_instance_load(instance, 1)

        return instance

    async def _get_healthy_instances(self) -> List[str]:
        """Get list of healthy instances"""

        instances = await self.redis.smembers("active_instances")
        healthy = []

        for instance in instances:
            if await self._is_healthy(instance):
                healthy.append(instance)

        return healthy

    async def _is_healthy(self, instance: str) -> bool:
        """Check if instance is healthy"""

        health_key = f"health:{instance}"
        last_check = await self.redis.get(health_key)

        if not last_check:
            return False

        # Check if health check is recent (within 30 seconds)
        check_time = datetime.fromisoformat(last_check)
        age = (datetime.utcnow() - check_time).total_seconds()

        return age < 30

    async def _select_least_loaded(self, instances: List[str]) -> str:
        """Select least loaded instance"""

        min_load = float('inf')
        selected = instances[0]

        for instance in instances:
            load = await self.redis.get(f"load:{instance}")
            load_value = float(load) if load else 0

            if load_value < min_load:
                min_load = load_value
                selected = instance

        return selected

    async def _select_fastest(self, instances: List[str]) -> str:
        """Select fastest responding instance"""

        min_latency = float('inf')
        selected = instances[0]

        for instance in instances:
            latency = await self.redis.get(f"latency:{instance}")
            latency_value = float(latency) if latency else 1000

            if latency_value < min_latency:
                min_latency = latency_value
                selected = instance

        return selected

    async def _round_robin(self, instances: List[str]) -> str:
        """Round-robin selection"""

        # Get last selected index
        last_index = await self.redis.get("rr_index")
        index = (int(last_index) if last_index else 0) + 1

        # Update index
        await self.redis.set("rr_index", index % len(instances))

        return instances[index % len(instances)]

    async def _update_instance_load(self, instance: str, delta: int) -> None:
        """Update instance load"""

        await self.redis.hincrby("instance_loads", instance, delta)