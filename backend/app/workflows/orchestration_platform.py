"""
Orchestration Platform - Sprint 14
Advanced service orchestration, resource management, and distributed system coordination
"""

from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
import json
import uuid
import psutil
import time
from collections import defaultdict, deque

class ServiceStatus(Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class ResourceType(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    CUSTOM = "custom"

class ScalingType(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    AUTO = "auto"

class LoadBalancingStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    IP_HASH = "ip_hash"
    LEAST_RESPONSE_TIME = "least_response_time"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ServiceInstance:
    """Individual service instance"""
    instance_id: str
    service_name: str
    host: str
    port: int
    status: ServiceStatus
    health_endpoint: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    resource_usage: Dict[str, float] = field(default_factory=dict)
    last_health_check: Optional[datetime] = None
    started_at: datetime = field(default_factory=datetime.now)
    connection_count: int = 0
    response_time_avg: float = 0.0

@dataclass
class ServiceDefinition:
    """Service definition and configuration"""
    service_id: str
    name: str
    description: str
    image: str
    command: Optional[str] = None
    environment: Dict[str, str] = field(default_factory=dict)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    scaling_config: Dict[str, Any] = field(default_factory=dict)
    health_check: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)

@dataclass
class ResourceAllocation:
    """Resource allocation for services"""
    allocation_id: str
    service_id: str
    instance_id: str
    resource_type: ResourceType
    allocated_amount: float
    used_amount: float = 0.0
    reserved_amount: float = 0.0
    allocated_at: datetime = field(default_factory=datetime.now)

@dataclass
class DistributedTask:
    """Distributed task for execution"""
    task_id: str
    name: str
    task_type: str
    priority: TaskPriority
    payload: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    assigned_instance: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class LoadBalancerConfig:
    """Load balancer configuration"""
    balancer_id: str
    service_name: str
    strategy: LoadBalancingStrategy
    health_check_interval: int = 30
    failure_threshold: int = 3
    recovery_threshold: int = 2
    sticky_sessions: bool = False
    session_timeout: int = 3600

class SystemHealthMonitor:
    """Monitors system health and resources"""

    def __init__(self):
        self.metrics_history = deque(maxlen=1440)  # 24 hours at 1-minute intervals
        self.alert_thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "disk_usage": 90.0,
            "response_time": 2000.0  # milliseconds
        }
        self.monitoring_active = False

    async def start_monitoring(self):
        """Start system monitoring"""
        self.monitoring_active = True

        while self.monitoring_active:
            await self._collect_system_metrics()
            await asyncio.sleep(60)  # Collect every minute

    async def _collect_system_metrics(self):
        """Collect current system metrics"""
        metrics = {
            "timestamp": datetime.now(),
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "network_io": psutil.net_io_counters()._asdict(),
            "process_count": len(psutil.pids())
        }

        self.metrics_history.append(metrics)

        # Check for alerts
        await self._check_alert_conditions(metrics)

    async def _check_alert_conditions(self, metrics: Dict[str, Any]):
        """Check if any metrics exceed alert thresholds"""
        alerts = []

        for metric, threshold in self.alert_thresholds.items():
            if metric in metrics and metrics[metric] > threshold:
                alerts.append({
                    "metric": metric,
                    "value": metrics[metric],
                    "threshold": threshold,
                    "timestamp": metrics["timestamp"]
                })

        # Process alerts (would integrate with notification system)
        for alert in alerts:
            print(f"ALERT: {alert['metric']} is {alert['value']}% (threshold: {alert['threshold']}%)")

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return {}

    def get_metrics_history(self, duration_minutes: int = 60) -> List[Dict[str, Any]]:
        """Get metrics history for specified duration"""
        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        return [
            metrics for metrics in self.metrics_history
            if metrics["timestamp"] >= cutoff_time
        ]

class ServiceMesh:
    """Service mesh for service discovery and communication"""

    def __init__(self):
        self.service_registry = {}
        self.service_instances = {}
        self.load_balancers = {}
        self.circuit_breakers = {}
        self.request_routing = {}

    async def register_service(self, service_def: ServiceDefinition) -> bool:
        """Register a service in the mesh"""
        self.service_registry[service_def.service_id] = service_def
        return True

    async def register_instance(self, instance: ServiceInstance) -> bool:
        """Register a service instance"""
        if instance.service_name not in [s.name for s in self.service_registry.values()]:
            return False

        self.service_instances[instance.instance_id] = instance
        return True

    async def discover_service(self, service_name: str) -> List[ServiceInstance]:
        """Discover instances of a service"""
        instances = [
            instance for instance in self.service_instances.values()
            if (instance.service_name == service_name and
                instance.status == ServiceStatus.RUNNING)
        ]
        return instances

    async def health_check_instance(self, instance_id: str) -> bool:
        """Perform health check on service instance"""
        if instance_id not in self.service_instances:
            return False

        instance = self.service_instances[instance_id]

        try:
            # Simulate health check
            # In production, make actual HTTP request to health endpoint
            if instance.health_endpoint:
                # Simulate success/failure
                health_ok = True  # Replace with actual health check

                instance.last_health_check = datetime.now()

                if not health_ok:
                    instance.status = ServiceStatus.ERROR
                    return False

            return True

        except Exception as e:
            instance.status = ServiceStatus.ERROR
            return False

    async def setup_load_balancer(self, config: LoadBalancerConfig) -> bool:
        """Setup load balancer for a service"""
        self.load_balancers[config.balancer_id] = config
        return True

    async def route_request(self, service_name: str,
                          request_data: Dict[str, Any]) -> Optional[ServiceInstance]:
        """Route request to appropriate service instance"""
        instances = await self.discover_service(service_name)
        if not instances:
            return None

        # Find load balancer config
        lb_config = None
        for config in self.load_balancers.values():
            if config.service_name == service_name:
                lb_config = config
                break

        if not lb_config:
            # Default to round-robin
            return instances[0] if instances else None

        # Apply load balancing strategy
        return self._apply_load_balancing(instances, lb_config, request_data)

    def _apply_load_balancing(self, instances: List[ServiceInstance],
                            config: LoadBalancerConfig,
                            request_data: Dict[str, Any]) -> ServiceInstance:
        """Apply load balancing strategy"""
        if config.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            # Simple round-robin (stateless)
            return instances[int(time.time()) % len(instances)]

        elif config.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return min(instances, key=lambda i: i.connection_count)

        elif config.strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
            return min(instances, key=lambda i: i.response_time_avg)

        else:
            return instances[0]

    def get_service_topology(self) -> Dict[str, Any]:
        """Get service mesh topology"""
        return {
            "services": len(self.service_registry),
            "instances": len(self.service_instances),
            "load_balancers": len(self.load_balancers),
            "topology": {
                service_id: {
                    "instances": [
                        i.instance_id for i in self.service_instances.values()
                        if i.service_name == service_def.name
                    ]
                }
                for service_id, service_def in self.service_registry.items()
            }
        }

class ResourceManager:
    """Manages resource allocation and scaling"""

    def __init__(self):
        self.resource_pools = defaultdict(lambda: {"total": 0, "allocated": 0, "available": 0})
        self.allocations = {}
        self.scaling_policies = {}
        self.auto_scaling_enabled = {}

    def initialize_resource_pool(self, resource_type: ResourceType,
                                total_amount: float):
        """Initialize a resource pool"""
        self.resource_pools[resource_type] = {
            "total": total_amount,
            "allocated": 0,
            "available": total_amount
        }

    async def allocate_resources(self, service_id: str, instance_id: str,
                               resource_type: ResourceType,
                               amount: float) -> Optional[str]:
        """Allocate resources to a service instance"""
        pool = self.resource_pools[resource_type]

        if pool["available"] < amount:
            return None  # Insufficient resources

        allocation_id = f"alloc_{uuid.uuid4().hex[:8]}"

        allocation = ResourceAllocation(
            allocation_id=allocation_id,
            service_id=service_id,
            instance_id=instance_id,
            resource_type=resource_type,
            allocated_amount=amount
        )

        self.allocations[allocation_id] = allocation

        # Update pool
        pool["allocated"] += amount
        pool["available"] -= amount

        return allocation_id

    async def deallocate_resources(self, allocation_id: str) -> bool:
        """Deallocate resources"""
        if allocation_id not in self.allocations:
            return False

        allocation = self.allocations[allocation_id]
        pool = self.resource_pools[allocation.resource_type]

        # Return resources to pool
        pool["allocated"] -= allocation.allocated_amount
        pool["available"] += allocation.allocated_amount

        del self.allocations[allocation_id]
        return True

    async def scale_service(self, service_id: str, scaling_type: ScalingType,
                          target_instances: Optional[int] = None,
                          resource_adjustments: Optional[Dict[str, float]] = None) -> bool:
        """Scale a service horizontally or vertically"""
        if scaling_type == ScalingType.HORIZONTAL:
            return await self._scale_horizontal(service_id, target_instances)
        elif scaling_type == ScalingType.VERTICAL:
            return await self._scale_vertical(service_id, resource_adjustments)

        return False

    async def _scale_horizontal(self, service_id: str, target_instances: int) -> bool:
        """Scale service horizontally (add/remove instances)"""
        # This would integrate with container orchestration
        # For now, simulate the scaling
        return True

    async def _scale_vertical(self, service_id: str,
                            resource_adjustments: Dict[str, float]) -> bool:
        """Scale service vertically (adjust resource limits)"""
        # This would adjust resource allocations for existing instances
        return True

    def get_resource_utilization(self) -> Dict[str, Any]:
        """Get current resource utilization"""
        return {
            resource_type.value: {
                "total": pool["total"],
                "allocated": pool["allocated"],
                "available": pool["available"],
                "utilization_percent": (pool["allocated"] / pool["total"]) * 100
                if pool["total"] > 0 else 0
            }
            for resource_type, pool in self.resource_pools.items()
        }

class TaskDistributor:
    """Distributes tasks across service instances"""

    def __init__(self):
        self.task_queue = deque()
        self.running_tasks = {}
        self.completed_tasks = deque(maxlen=1000)
        self.worker_instances = {}

    async def submit_task(self, name: str, task_type: str,
                         payload: Dict[str, Any],
                         priority: TaskPriority = TaskPriority.MEDIUM) -> str:
        """Submit a task for distributed execution"""
        task_id = f"task_{uuid.uuid4().hex[:8]}"

        task = DistributedTask(
            task_id=task_id,
            name=name,
            task_type=task_type,
            priority=priority,
            payload=payload
        )

        # Insert task in priority order
        inserted = False
        for i, existing_task in enumerate(self.task_queue):
            if task.priority.value > existing_task.priority.value:
                self.task_queue.insert(i, task)
                inserted = True
                break

        if not inserted:
            self.task_queue.append(task)

        return task_id

    async def process_task_queue(self):
        """Process pending tasks from queue"""
        while self.task_queue:
            task = self.task_queue.popleft()

            # Find available worker
            worker = await self._find_available_worker(task.task_type)
            if not worker:
                # No available worker, put task back
                self.task_queue.appendleft(task)
                break

            # Assign task to worker
            await self._assign_task_to_worker(task, worker)

    async def _find_available_worker(self, task_type: str) -> Optional[str]:
        """Find available worker for task type"""
        # Simplified worker selection
        # In production, this would check actual worker capacity and type
        for worker_id, worker_info in self.worker_instances.items():
            if (worker_info.get("status") == "available" and
                task_type in worker_info.get("supported_types", [])):
                return worker_id

        return None

    async def _assign_task_to_worker(self, task: DistributedTask, worker_id: str):
        """Assign task to worker instance"""
        task.assigned_instance = worker_id
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()

        self.running_tasks[task.task_id] = task

        # Simulate task execution
        asyncio.create_task(self._execute_task(task))

    async def _execute_task(self, task: DistributedTask):
        """Execute a distributed task"""
        try:
            # Simulate task execution
            await asyncio.sleep(1)  # Simulate work

            # Mark as completed
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = {"success": True, "processed": task.payload}

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            task.error_message = str(e)

        # Move from running to completed
        if task.task_id in self.running_tasks:
            del self.running_tasks[task.task_id]

        self.completed_tasks.append(task)

    def get_task_status(self, task_id: str) -> Optional[DistributedTask]:
        """Get status of a task"""
        # Check running tasks
        if task_id in self.running_tasks:
            return self.running_tasks[task_id]

        # Check completed tasks
        for task in self.completed_tasks:
            if task.task_id == task_id:
                return task

        # Check queue
        for task in self.task_queue:
            if task.task_id == task_id:
                return task

        return None

class OrchestrationPlatform:
    """Central orchestration platform coordinating all systems"""

    def __init__(self):
        self.health_monitor = SystemHealthMonitor()
        self.service_mesh = ServiceMesh()
        self.resource_manager = ResourceManager()
        self.task_distributor = TaskDistributor()
        self.orchestration_stats = {
            "services_managed": 0,
            "instances_running": 0,
            "tasks_processed": 0,
            "uptime_start": datetime.now()
        }

    async def initialize_platform(self):
        """Initialize the orchestration platform"""
        # Initialize resource pools
        self.resource_manager.initialize_resource_pool(ResourceType.CPU, 100.0)
        self.resource_manager.initialize_resource_pool(ResourceType.MEMORY, 64.0)  # GB
        self.resource_manager.initialize_resource_pool(ResourceType.DISK, 1000.0)  # GB

        # Start monitoring
        asyncio.create_task(self.health_monitor.start_monitoring())

        # Start task processing
        asyncio.create_task(self._task_processing_loop())

    async def _task_processing_loop(self):
        """Continuous task processing loop"""
        while True:
            await self.task_distributor.process_task_queue()
            await asyncio.sleep(5)  # Process every 5 seconds

    async def deploy_service(self, service_def: ServiceDefinition,
                           instance_count: int = 1) -> List[str]:
        """Deploy a service with specified instance count"""
        await self.service_mesh.register_service(service_def)

        instance_ids = []
        for i in range(instance_count):
            instance_id = f"{service_def.name}_{i}_{uuid.uuid4().hex[:6]}"

            instance = ServiceInstance(
                instance_id=instance_id,
                service_name=service_def.name,
                host=f"10.0.0.{i + 1}",  # Simulate IPs
                port=8000 + i,
                status=ServiceStatus.STARTING
            )

            await self.service_mesh.register_instance(instance)

            # Allocate resources
            resource_reqs = service_def.resource_requirements
            for resource_type_str, amount in resource_reqs.items():
                resource_type = ResourceType(resource_type_str)
                await self.resource_manager.allocate_resources(
                    service_def.service_id, instance_id, resource_type, amount
                )

            # Start instance (simulated)
            instance.status = ServiceStatus.RUNNING
            instance_ids.append(instance_id)

        self.orchestration_stats["services_managed"] += 1
        self.orchestration_stats["instances_running"] += instance_count

        return instance_ids

    async def scale_service(self, service_name: str, target_instances: int) -> bool:
        """Scale a service to target instance count"""
        current_instances = await self.service_mesh.discover_service(service_name)
        current_count = len(current_instances)

        if target_instances > current_count:
            # Scale up
            return await self._scale_up_service(service_name, target_instances - current_count)
        elif target_instances < current_count:
            # Scale down
            return await self._scale_down_service(service_name, current_count - target_instances)

        return True

    async def _scale_up_service(self, service_name: str, additional_instances: int) -> bool:
        """Scale up service by adding instances"""
        # Find service definition
        service_def = None
        for service in self.service_mesh.service_registry.values():
            if service.name == service_name:
                service_def = service
                break

        if not service_def:
            return False

        # Deploy additional instances
        new_instances = await self.deploy_service(service_def, additional_instances)
        return len(new_instances) == additional_instances

    async def _scale_down_service(self, service_name: str, instances_to_remove: int) -> bool:
        """Scale down service by removing instances"""
        instances = await self.service_mesh.discover_service(service_name)
        instances_to_stop = instances[:instances_to_remove]

        for instance in instances_to_stop:
            # Stop instance and deallocate resources
            instance.status = ServiceStatus.STOPPED
            # In production, would actually stop the container/process

        return True

    def get_platform_status(self) -> Dict[str, Any]:
        """Get overall platform status"""
        uptime = datetime.now() - self.orchestration_stats["uptime_start"]

        return {
            **self.orchestration_stats,
            "uptime_seconds": uptime.total_seconds(),
            "system_health": self.health_monitor.get_current_metrics(),
            "resource_utilization": self.resource_manager.get_resource_utilization(),
            "service_topology": self.service_mesh.get_service_topology(),
            "task_queue_size": len(self.task_distributor.task_queue),
            "running_tasks": len(self.task_distributor.running_tasks)
        }

# Singleton instance
_orchestration_platform_instance: Optional[OrchestrationPlatform] = None

def get_orchestration_platform() -> OrchestrationPlatform:
    """Get the singleton Orchestration Platform instance"""
    global _orchestration_platform_instance
    if _orchestration_platform_instance is None:
        _orchestration_platform_instance = OrchestrationPlatform()
    return _orchestration_platform_instance