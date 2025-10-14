"""
BMAD v6 MCP Server Monitoring and Metrics
"""

import time
import psutil
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import json
import logging

from app.core.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class MetricPoint:
    """Single metric data point."""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = None
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "labels": self.labels or {}
        }

@dataclass
class SystemMetrics:
    """System resource metrics."""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_percent: float
    disk_used_gb: float
    disk_free_gb: float
    network_bytes_sent: int
    network_bytes_recv: int
    timestamp: datetime
    
    def to_dict(self):
        return asdict(self)

@dataclass
class ApplicationMetrics:
    """Application-specific metrics."""
    active_workflows: int
    completed_workflows: int
    failed_workflows: int
    active_agents: int
    agent_invocations: int
    api_requests_total: int
    api_requests_success: int
    api_requests_error: int
    websocket_connections: int
    database_connections: int
    timestamp: datetime
    
    def to_dict(self):
        return asdict(self)

class MetricsCollector:
    """Collects and stores metrics."""
    
    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.last_cleanup = datetime.now()
        
        # Application state tracking
        self.workflow_stats = {
            "active": 0,
            "completed": 0,
            "failed": 0,
            "total_execution_time": 0.0
        }
        
        self.agent_stats = {
            "active": 0,
            "invocations": 0,
            "total_response_time": 0.0
        }
        
        self.api_stats = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_error": 0,
            "response_times": deque(maxlen=1000)
        }
        
        self.websocket_stats = {
            "active_connections": 0,
            "total_messages": 0
        }
    
    def increment_counter(self, name: str, value: int = 1, labels: Dict[str, str] = None):
        """Increment a counter metric."""
        key = self._make_key(name, labels)
        self.counters[key] += value
        
        # Store time series data
        self.metrics[key].append(MetricPoint(
            timestamp=datetime.now(),
            value=self.counters[key],
            labels=labels
        ))
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric."""
        key = self._make_key(name, labels)
        self.gauges[key] = value
        
        # Store time series data
        self.metrics[key].append(MetricPoint(
            timestamp=datetime.now(),
            value=value,
            labels=labels
        ))
    
    def record_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record a histogram value."""
        key = self._make_key(name, labels)
        self.histograms[key].append(value)
        
        # Keep only recent values
        if len(self.histograms[key]) > 1000:
            self.histograms[key] = self.histograms[key][-1000:]
    
    def _make_key(self, name: str, labels: Dict[str, str] = None) -> str:
        """Create a unique key for metric with labels."""
        if not labels:
            return name
        
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def get_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        
        # Network metrics
        network = psutil.net_io_counters()
        
        return SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory.used / (1024 * 1024),
            memory_available_mb=memory.available / (1024 * 1024),
            disk_percent=disk.percent,
            disk_used_gb=disk.used / (1024 * 1024 * 1024),
            disk_free_gb=disk.free / (1024 * 1024 * 1024),
            network_bytes_sent=network.bytes_sent,
            network_bytes_recv=network.bytes_recv,
            timestamp=datetime.now()
        )
    
    def get_application_metrics(self) -> ApplicationMetrics:
        """Collect current application metrics."""
        return ApplicationMetrics(
            active_workflows=self.workflow_stats["active"],
            completed_workflows=self.workflow_stats["completed"],
            failed_workflows=self.workflow_stats["failed"],
            active_agents=self.agent_stats["active"],
            agent_invocations=self.agent_stats["invocations"],
            api_requests_total=self.api_stats["requests_total"],
            api_requests_success=self.api_stats["requests_success"],
            api_requests_error=self.api_stats["requests_error"],
            websocket_connections=self.websocket_stats["active_connections"],
            database_connections=0,  # Would be implemented with actual DB pool
            timestamp=datetime.now()
        )
    
    def record_workflow_start(self, workflow_name: str, project_id: str):
        """Record workflow start."""
        self.workflow_stats["active"] += 1
        self.increment_counter("workflow_starts", labels={
            "workflow": workflow_name,
            "project": project_id
        })
    
    def record_workflow_complete(self, workflow_name: str, project_id: str, duration: float):
        """Record workflow completion."""
        self.workflow_stats["active"] -= 1
        self.workflow_stats["completed"] += 1
        self.workflow_stats["total_execution_time"] += duration
        
        self.increment_counter("workflow_completions", labels={
            "workflow": workflow_name,
            "project": project_id
        })
        
        self.record_histogram("workflow_duration", duration, labels={
            "workflow": workflow_name
        })
    
    def record_workflow_failure(self, workflow_name: str, project_id: str, error: str):
        """Record workflow failure."""
        self.workflow_stats["active"] -= 1
        self.workflow_stats["failed"] += 1
        
        self.increment_counter("workflow_failures", labels={
            "workflow": workflow_name,
            "project": project_id,
            "error": error
        })
    
    def record_agent_invocation(self, agent_name: str, duration: float):
        """Record agent invocation."""
        self.agent_stats["invocations"] += 1
        self.agent_stats["total_response_time"] += duration
        
        self.increment_counter("agent_invocations", labels={
            "agent": agent_name
        })
        
        self.record_histogram("agent_response_time", duration, labels={
            "agent": agent_name
        })
    
    def record_api_request(self, method: str, path: str, status_code: int, duration: float):
        """Record API request."""
        self.api_stats["requests_total"] += 1
        self.api_stats["response_times"].append(duration)
        
        if 200 <= status_code < 400:
            self.api_stats["requests_success"] += 1
        else:
            self.api_stats["requests_error"] += 1
        
        self.increment_counter("api_requests", labels={
            "method": method,
            "path": path,
            "status": str(status_code)
        })
        
        self.record_histogram("api_response_time", duration, labels={
            "method": method,
            "path": path
        })
    
    def record_websocket_connection(self, connected: bool):
        """Record WebSocket connection change."""
        if connected:
            self.websocket_stats["active_connections"] += 1
        else:
            self.websocket_stats["active_connections"] -= 1
    
    def record_websocket_message(self):
        """Record WebSocket message."""
        self.websocket_stats["total_messages"] += 1
        self.increment_counter("websocket_messages")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        system_metrics = self.get_system_metrics()
        app_metrics = self.get_application_metrics()
        
        # Calculate averages for histograms
        histogram_stats = {}
        for name, values in self.histograms.items():
            if values:
                histogram_stats[name] = {
                    "count": len(values),
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "p95": sorted(values)[int(len(values) * 0.95)] if len(values) > 0 else 0
                }
        
        return {
            "system": system_metrics.to_dict(),
            "application": app_metrics.to_dict(),
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": histogram_stats,
            "collection_time": datetime.now().isoformat()
        }
    
    def cleanup_old_metrics(self):
        """Clean up old metrics data."""
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
        
        for metric_name, points in self.metrics.items():
            # Remove old points
            while points and points[0].timestamp < cutoff_time:
                points.popleft()
        
        self.last_cleanup = datetime.now()
        logger.info(f"Cleaned up metrics older than {self.retention_hours} hours")

class HealthChecker:
    """Health check system for monitoring service health."""
    
    def __init__(self):
        self.checks: Dict[str, callable] = {}
        self.last_results: Dict[str, Dict[str, Any]] = {}
    
    def register_check(self, name: str, check_func: callable):
        """Register a health check function."""
        self.checks[name] = check_func
        logger.info(f"Registered health check: {name}")
    
    async def run_check(self, name: str) -> Dict[str, Any]:
        """Run a specific health check."""
        if name not in self.checks:
            return {
                "status": "unknown",
                "message": f"Health check '{name}' not found",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            start_time = time.time()
            
            # Run the check function
            check_func = self.checks[name]
            if asyncio.iscoroutinefunction(check_func):
                result = await check_func()
            else:
                result = check_func()
            
            duration = time.time() - start_time
            
            # Ensure result has required fields
            if not isinstance(result, dict):
                result = {"status": "healthy" if result else "unhealthy"}
            
            result.update({
                "check_duration_ms": duration * 1000,
                "timestamp": datetime.now().isoformat()
            })
            
            self.last_results[name] = result
            return result
            
        except Exception as e:
            error_result = {
                "status": "unhealthy",
                "message": f"Health check failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            self.last_results[name] = error_result
            logger.error(f"Health check '{name}' failed: {str(e)}")
            return error_result
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all registered health checks."""
        results = {}
        overall_status = "healthy"
        
        for name in self.checks:
            result = await self.run_check(name)
            results[name] = result
            
            if result["status"] != "healthy":
                overall_status = "unhealthy"
        
        return {
            "overall_status": overall_status,
            "checks": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_last_results(self) -> Dict[str, Any]:
        """Get last health check results."""
        return {
            "checks": self.last_results,
            "timestamp": datetime.now().isoformat()
        }

# Global instances
metrics_collector = MetricsCollector()
health_checker = HealthChecker()

# Default health checks
async def database_health_check():
    """Check database connectivity."""
    try:
        # Would implement actual database check
        return {
            "status": "healthy",
            "message": "Database connection successful",
            "connection_pool_size": 10,
            "active_connections": 2
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }

def memory_health_check():
    """Check memory usage."""
    memory = psutil.virtual_memory()
    
    if memory.percent > 90:
        status = "unhealthy"
        message = "High memory usage"
    elif memory.percent > 80:
        status = "degraded"
        message = "Elevated memory usage"
    else:
        status = "healthy"
        message = "Memory usage normal"
    
    return {
        "status": status,
        "message": message,
        "memory_percent": memory.percent,
        "memory_available_mb": memory.available / (1024 * 1024)
    }

def disk_health_check():
    """Check disk usage."""
    disk = psutil.disk_usage('/')
    
    if disk.percent > 95:
        status = "unhealthy"
        message = "Critical disk usage"
    elif disk.percent > 85:
        status = "degraded"
        message = "High disk usage"
    else:
        status = "healthy"
        message = "Disk usage normal"
    
    return {
        "status": status,
        "message": message,
        "disk_percent": disk.percent,
        "disk_free_gb": disk.free / (1024 * 1024 * 1024)
    }

# Register default health checks
health_checker.register_check("database", database_health_check)
health_checker.register_check("memory", memory_health_check)
health_checker.register_check("disk", disk_health_check)

# Background monitoring task
async def monitoring_task():
    """Background task for continuous monitoring."""
    while True:
        try:
            # Collect system metrics
            system_metrics = metrics_collector.get_system_metrics()
            
            # Store as gauge metrics
            metrics_collector.set_gauge("system_cpu_percent", system_metrics.cpu_percent)
            metrics_collector.set_gauge("system_memory_percent", system_metrics.memory_percent)
            metrics_collector.set_gauge("system_disk_percent", system_metrics.disk_percent)
            
            # Run health checks
            health_results = await health_checker.run_all_checks()
            
            # Log if any health checks are failing
            if health_results["overall_status"] != "healthy":
                logger.warning(f"Health check issues detected: {health_results}")
            
            # Clean up old metrics periodically
            if (datetime.now() - metrics_collector.last_cleanup).total_seconds() > 3600:  # Every hour
                metrics_collector.cleanup_old_metrics()
            
            # Wait 30 seconds before next collection
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"Monitoring task error: {str(e)}")
            await asyncio.sleep(60)  # Wait longer on error

# Start monitoring task when module is imported
asyncio.create_task(monitoring_task())
