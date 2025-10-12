"""
Performance & Scalability Layer
High-performance caching, queueing, and optimization services
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio
import json
import hashlib
import time
from abc import ABC, abstractmethod

class CacheStrategy(str, Enum):
    """Cache invalidation strategies"""
    TTL = "ttl"  # Time to live
    LRU = "lru"  # Least recently used
    LFU = "lfu"  # Least frequently used
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    REFRESH_AHEAD = "refresh_ahead"

class QueuePriority(str, Enum):
    """Task queue priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class TaskStatus(str, Enum):
    """Background task status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    last_accessed: datetime
    access_count: int
    size_bytes: int
    tags: List[str] = None
    
@dataclass
class QueueTask:
    """Background queue task"""
    task_id: str
    task_name: str
    queue_name: str
    priority: QueuePriority
    payload: Dict[str, Any]
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    result: Optional[Any] = None
    metadata: Dict[str, Any] = None
    
@dataclass
class PerformanceMetrics:
    """Performance monitoring metrics"""
    metric_name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = None
    unit: str = "count"
    
class CacheManager:
    """High-performance caching layer"""
    
    def __init__(self, max_size: int = 10000, default_ttl: int = 3600):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_size_bytes": 0
        }
    
    def _generate_key(self, namespace: str, key: str) -> str:
        """Generate a cache key with namespace"""
        return f"{namespace}:{key}"
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired"""
        if entry.expires_at is None:
            return False
        return datetime.now() > entry.expires_at
    
    def _evict_lru(self) -> None:
        """Evict least recently used entries"""
        if len(self.cache) <= self.max_size:
            return
        
        # Sort by last accessed time
        sorted_entries = sorted(
            self.cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        # Remove oldest 10% of entries
        evict_count = max(1, len(self.cache) // 10)
        for i in range(evict_count):
            key, entry = sorted_entries[i]
            self.stats["total_size_bytes"] -= entry.size_bytes
            del self.cache[key]
            self.stats["evictions"] += 1
    
    def get(self, namespace: str, key: str) -> Optional[Any]:
        """Get value from cache"""
        cache_key = self._generate_key(namespace, key)
        entry = self.cache.get(cache_key)
        
        if entry is None:
            self.stats["misses"] += 1
            return None
        
        if self._is_expired(entry):
            del self.cache[cache_key]
            self.stats["misses"] += 1
            self.stats["total_size_bytes"] -= entry.size_bytes
            return None
        
        # Update access metadata
        entry.last_accessed = datetime.now()
        entry.access_count += 1
        self.stats["hits"] += 1
        
        return entry.value
    
    def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: List[str] = None
    ) -> bool:
        """Set value in cache"""
        try:
            cache_key = self._generate_key(namespace, key)
            
            # Calculate size (rough estimate)
            value_size = len(str(value).encode('utf-8'))
            
            # Set expiration
            expires_at = None
            if ttl is not None:
                expires_at = datetime.now() + timedelta(seconds=ttl)
            elif self.default_ttl > 0:
                expires_at = datetime.now() + timedelta(seconds=self.default_ttl)
            
            # Create cache entry
            entry = CacheEntry(
                key=cache_key,
                value=value,
                created_at=datetime.now(),
                expires_at=expires_at,
                last_accessed=datetime.now(),
                access_count=0,
                size_bytes=value_size,
                tags=tags or []
            )
            
            # Remove old entry if exists
            if cache_key in self.cache:
                old_entry = self.cache[cache_key]
                self.stats["total_size_bytes"] -= old_entry.size_bytes
            
            # Add new entry
            self.cache[cache_key] = entry
            self.stats["total_size_bytes"] += value_size
            
            # Evict if necessary
            self._evict_lru()
            
            return True
            
        except Exception:
            return False
    
    def delete(self, namespace: str, key: str) -> bool:
        """Delete value from cache"""
        cache_key = self._generate_key(namespace, key)
        entry = self.cache.get(cache_key)
        
        if entry:
            self.stats["total_size_bytes"] -= entry.size_bytes
            del self.cache[cache_key]
            return True
        
        return False
    
    def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate cache entries by tags"""
        invalidated = 0
        keys_to_delete = []
        
        for cache_key, entry in self.cache.items():
            if entry.tags and any(tag in entry.tags for tag in tags):
                keys_to_delete.append(cache_key)
                self.stats["total_size_bytes"] -= entry.size_bytes
        
        for key in keys_to_delete:
            del self.cache[key]
            invalidated += 1
        
        return invalidated
    
    def clear_namespace(self, namespace: str) -> int:
        """Clear all entries in a namespace"""
        cleared = 0
        keys_to_delete = []
        
        for cache_key, entry in self.cache.items():
            if cache_key.startswith(f"{namespace}:"):
                keys_to_delete.append(cache_key)
                self.stats["total_size_bytes"] -= entry.size_bytes
        
        for key in keys_to_delete:
            del self.cache[key]
            cleared += 1
        
        return cleared
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / max(total_requests, 1)) * 100
        
        return {
            **self.stats,
            "total_entries": len(self.cache),
            "hit_rate_percent": round(hit_rate, 2),
            "total_requests": total_requests,
            "memory_usage_mb": round(self.stats["total_size_bytes"] / (1024 * 1024), 2)
        }

class QueueManager:
    """Background task queue management"""
    
    def __init__(self):
        self.queues: Dict[str, List[QueueTask]] = {
            "default": [],
            "high_priority": [],
            "background": [],
            "notifications": [],
            "integrations": [],
            "analytics": []
        }
        self.workers: Dict[str, bool] = {}  # worker_id -> is_running
        self.task_handlers: Dict[str, Callable] = {}
        self.processing_tasks: Dict[str, QueueTask] = {}
        self.completed_tasks: List[QueueTask] = []
        
    def register_task_handler(self, task_name: str, handler: Callable) -> None:
        """Register a task handler function"""
        self.task_handlers[task_name] = handler
    
    def enqueue(
        self,
        task_name: str,
        payload: Dict[str, Any],
        queue_name: str = "default",
        priority: QueuePriority = QueuePriority.NORMAL,
        max_retries: int = 3
    ) -> str:
        """Add a task to the queue"""
        task_id = f"task_{int(time.time() * 1000)}_{len(self.queues[queue_name])}"
        
        task = QueueTask(
            task_id=task_id,
            task_name=task_name,
            queue_name=queue_name,
            priority=priority,
            payload=payload,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            max_retries=max_retries
        )
        
        if queue_name not in self.queues:
            self.queues[queue_name] = []
        
        # Insert based on priority
        if priority == QueuePriority.CRITICAL:
            self.queues[queue_name].insert(0, task)
        elif priority == QueuePriority.HIGH:
            # Insert after critical tasks
            insert_pos = 0
            for i, existing_task in enumerate(self.queues[queue_name]):
                if existing_task.priority != QueuePriority.CRITICAL:
                    insert_pos = i
                    break
                insert_pos = i + 1
            self.queues[queue_name].insert(insert_pos, task)
        else:
            self.queues[queue_name].append(task)
        
        return task_id
    
    async def process_queue(self, queue_name: str = "default") -> Optional[QueueTask]:
        """Process next task in queue"""
        if queue_name not in self.queues or not self.queues[queue_name]:
            return None
        
        task = self.queues[queue_name].pop(0)
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        self.processing_tasks[task.task_id] = task
        
        try:
            # Get task handler
            handler = self.task_handlers.get(task.task_name)
            if not handler:
                raise Exception(f"No handler registered for task {task.task_name}")
            
            # Execute task
            if asyncio.iscoroutinefunction(handler):
                result = await handler(task.payload)
            else:
                result = handler(task.payload)
            
            # Mark as completed
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            
        except Exception as e:
            # Handle failure
            task.error_message = str(e)
            
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.RETRYING
                # Re-queue for retry
                self.queues[queue_name].append(task)
            else:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now()
        
        finally:
            # Move to completed tasks
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                del self.processing_tasks[task.task_id]
                self.completed_tasks.append(task)
                
                # Keep only last 1000 completed tasks
                if len(self.completed_tasks) > 1000:
                    self.completed_tasks = self.completed_tasks[-1000:]
        
        return task
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        # Check processing tasks
        if task_id in self.processing_tasks:
            task = self.processing_tasks[task_id]
            return {
                "task_id": task.task_id,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "retry_count": task.retry_count
            }
        
        # Check completed tasks
        for task in self.completed_tasks:
            if task.task_id == task_id:
                return {
                    "task_id": task.task_id,
                    "status": task.status.value,
                    "created_at": task.created_at.isoformat(),
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "retry_count": task.retry_count,
                    "error_message": task.error_message,
                    "result": task.result
                }
        
        # Check pending tasks
        for queue_tasks in self.queues.values():
            for task in queue_tasks:
                if task.task_id == task_id:
                    return {
                        "task_id": task.task_id,
                        "status": task.status.value,
                        "created_at": task.created_at.isoformat(),
                        "queue_position": queue_tasks.index(task)
                    }
        
        return None
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        queue_lengths = {name: len(tasks) for name, tasks in self.queues.items()}
        
        return {
            "queue_lengths": queue_lengths,
            "processing_tasks": len(self.processing_tasks),
            "completed_tasks": len(self.completed_tasks),
            "registered_handlers": len(self.task_handlers),
            "total_pending": sum(queue_lengths.values())
        }

class PerformanceManager:
    """Central performance and optimization manager"""
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.queue_manager = QueueManager()
        self.metrics: List[PerformanceMetrics] = []
        self.connection_pools: Dict[str, Dict[str, Any]] = {}
        self.optimization_settings = {
            "enable_caching": True,
            "enable_compression": True,
            "enable_query_optimization": True,
            "max_connection_pool_size": 20,
            "connection_timeout": 30,
            "read_timeout": 60
        }
        
        # Register default task handlers
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default task handlers"""
        async def send_notification_task(payload: Dict[str, Any]) -> Dict[str, Any]:
            """Send notification task handler"""
            # Mock notification sending
            await asyncio.sleep(0.1)
            return {
                "notification_sent": True,
                "recipient": payload.get("recipient"),
                "type": payload.get("type", "email")
            }
        
        async def sync_integration_task(payload: Dict[str, Any]) -> Dict[str, Any]:
            """Integration sync task handler"""
            # Mock integration sync
            await asyncio.sleep(0.5)
            return {
                "sync_completed": True,
                "integration_id": payload.get("integration_id"),
                "records_synced": 25
            }
        
        def generate_report_task(payload: Dict[str, Any]) -> Dict[str, Any]:
            """Report generation task handler"""
            # Mock report generation
            time.sleep(0.3)
            return {
                "report_generated": True,
                "report_id": payload.get("report_id"),
                "format": payload.get("format", "pdf")
            }
        
        self.queue_manager.register_task_handler("send_notification", send_notification_task)
        self.queue_manager.register_task_handler("sync_integration", sync_integration_task)
        self.queue_manager.register_task_handler("generate_report", generate_report_task)
    
    def record_metric(
        self,
        metric_name: str,
        value: float,
        tags: Dict[str, str] = None,
        unit: str = "count"
    ) -> None:
        """Record a performance metric"""
        metric = PerformanceMetrics(
            metric_name=metric_name,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {},
            unit=unit
        )
        
        self.metrics.append(metric)
        
        # Keep only last 10,000 metrics
        if len(self.metrics) > 10000:
            self.metrics = self.metrics[-10000:]
    
    def get_metrics(
        self,
        metric_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[PerformanceMetrics]:
        """Get performance metrics with filtering"""
        filtered_metrics = self.metrics
        
        if metric_name:
            filtered_metrics = [m for m in filtered_metrics if m.metric_name == metric_name]
        
        if start_time:
            filtered_metrics = [m for m in filtered_metrics if m.timestamp >= start_time]
        
        if end_time:
            filtered_metrics = [m for m in filtered_metrics if m.timestamp <= end_time]
        
        # Sort by timestamp, most recent first
        filtered_metrics.sort(key=lambda x: x.timestamp, reverse=True)
        
        return filtered_metrics[:limit]
    
    def configure_connection_pool(
        self,
        pool_name: str,
        max_connections: int = 20,
        timeout: int = 30
    ) -> bool:
        """Configure database connection pool"""
        try:
            self.connection_pools[pool_name] = {
                "max_connections": max_connections,
                "timeout": timeout,
                "current_connections": 0,
                "created_at": datetime.now().isoformat()
            }
            return True
        except Exception:
            return False
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get performance optimization recommendations"""
        recommendations = []
        
        # Cache hit rate recommendation
        cache_stats = self.cache_manager.get_stats()
        if cache_stats["hit_rate_percent"] < 50:
            recommendations.append({
                "type": "cache_optimization",
                "priority": "high",
                "description": f"Cache hit rate is low ({cache_stats['hit_rate_percent']:.1f}%). Consider increasing cache size or TTL.",
                "current_value": cache_stats["hit_rate_percent"],
                "target_value": 75
            })
        
        # Queue length recommendation
        queue_stats = self.queue_manager.get_queue_stats()
        if queue_stats["total_pending"] > 100:
            recommendations.append({
                "type": "queue_optimization",
                "priority": "medium",
                "description": f"High queue backlog ({queue_stats['total_pending']} tasks). Consider adding more workers.",
                "current_value": queue_stats["total_pending"],
                "target_value": 50
            })
        
        # Memory usage recommendation
        if cache_stats["memory_usage_mb"] > 500:
            recommendations.append({
                "type": "memory_optimization",
                "priority": "medium",
                "description": f"High cache memory usage ({cache_stats['memory_usage_mb']:.1f}MB). Consider implementing LRU eviction.",
                "current_value": cache_stats["memory_usage_mb"],
                "target_value": 300
            })
        
        if not recommendations:
            recommendations.append({
                "type": "status",
                "priority": "info",
                "description": "Performance metrics are within optimal ranges.",
                "current_value": "optimal",
                "target_value": "optimal"
            })
        
        return recommendations
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        return {
            "cache_stats": self.cache_manager.get_stats(),
            "queue_stats": self.queue_manager.get_queue_stats(),
            "metrics_count": len(self.metrics),
            "connection_pools": len(self.connection_pools),
            "optimization_settings": self.optimization_settings,
            "recommendations": self.get_optimization_recommendations(),
            "timestamp": datetime.now().isoformat()
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on performance layer"""
        cache_stats = self.cache_manager.get_stats()
        queue_stats = self.queue_manager.get_queue_stats()
        
        return {
            "status": "healthy",
            "cache_entries": cache_stats["total_entries"],
            "cache_hit_rate": cache_stats["hit_rate_percent"],
            "pending_tasks": queue_stats["total_pending"],
            "processing_tasks": queue_stats["processing_tasks"],
            "metrics_tracked": len(self.metrics),
            "timestamp": datetime.now().isoformat()
        }

# Global performance manager instance
_performance_manager: Optional[PerformanceManager] = None

def get_performance_manager() -> PerformanceManager:
    """Get global performance manager instance"""
    global _performance_manager
    if _performance_manager is None:
        _performance_manager = PerformanceManager()
    return _performance_manager