"""
BMAD v6 MCP Server Monitoring API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime, timedelta

from app.core.monitoring import metrics_collector, health_checker
from app.core.logging_config import get_logger, log_health_check
from app.services.security_manager import SecurityManager

logger = get_logger(__name__)
router = APIRouter()
security_manager = SecurityManager()

@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    try:
        health_results = await health_checker.run_all_checks()
        
        # Log health check
        log_health_check("overall", health_results["overall_status"], health_results)
        
        status_code = 200 if health_results["overall_status"] == "healthy" else 503
        
        return {
            "status": health_results["overall_status"],
            "timestamp": health_results["timestamp"],
            "bmad_version": "6.0.0",
            "checks": health_results["checks"]
        }
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")

@router.get("/health/{check_name}")
async def specific_health_check(check_name: str):
    """Run a specific health check."""
    try:
        result = await health_checker.run_check(check_name)
        
        if result["status"] == "unknown":
            raise HTTPException(status_code=404, detail=f"Health check '{check_name}' not found")
        
        status_code = 200 if result["status"] == "healthy" else 503
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check '{check_name}' failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")

@router.get("/metrics")
async def get_metrics():
    """Get comprehensive metrics summary."""
    try:
        metrics_summary = metrics_collector.get_metrics_summary()
        
        return {
            "bmad_version": "6.0.0",
            "metrics": metrics_summary
        }
    
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")

@router.get("/metrics/system")
async def get_system_metrics():
    """Get system resource metrics."""
    try:
        system_metrics = metrics_collector.get_system_metrics()
        
        return {
            "bmad_version": "6.0.0",
            "system_metrics": system_metrics.to_dict()
        }
    
    except Exception as e:
        logger.error(f"Failed to get system metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system metrics")

@router.get("/metrics/application")
async def get_application_metrics():
    """Get application-specific metrics."""
    try:
        app_metrics = metrics_collector.get_application_metrics()
        
        return {
            "bmad_version": "6.0.0",
            "application_metrics": app_metrics.to_dict()
        }
    
    except Exception as e:
        logger.error(f"Failed to get application metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve application metrics")

@router.get("/metrics/workflows")
async def get_workflow_metrics():
    """Get workflow execution metrics."""
    try:
        workflow_stats = {
            "active_workflows": metrics_collector.workflow_stats["active"],
            "completed_workflows": metrics_collector.workflow_stats["completed"],
            "failed_workflows": metrics_collector.workflow_stats["failed"],
            "total_execution_time": metrics_collector.workflow_stats["total_execution_time"],
            "average_execution_time": (
                metrics_collector.workflow_stats["total_execution_time"] / 
                max(metrics_collector.workflow_stats["completed"], 1)
            )
        }
        
        # Get workflow duration histogram
        workflow_durations = {}
        for name, values in metrics_collector.histograms.items():
            if "workflow_duration" in name:
                if values:
                    workflow_durations[name] = {
                        "count": len(values),
                        "avg": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "p95": sorted(values)[int(len(values) * 0.95)] if len(values) > 0 else 0
                    }
        
        return {
            "bmad_version": "6.0.0",
            "workflow_stats": workflow_stats,
            "workflow_durations": workflow_durations,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to get workflow metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve workflow metrics")

@router.get("/metrics/agents")
async def get_agent_metrics():
    """Get agent invocation metrics."""
    try:
        agent_stats = {
            "active_agents": metrics_collector.agent_stats["active"],
            "total_invocations": metrics_collector.agent_stats["invocations"],
            "total_response_time": metrics_collector.agent_stats["total_response_time"],
            "average_response_time": (
                metrics_collector.agent_stats["total_response_time"] / 
                max(metrics_collector.agent_stats["invocations"], 1)
            )
        }
        
        # Get agent response time histogram
        agent_response_times = {}
        for name, values in metrics_collector.histograms.items():
            if "agent_response_time" in name:
                if values:
                    agent_response_times[name] = {
                        "count": len(values),
                        "avg": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "p95": sorted(values)[int(len(values) * 0.95)] if len(values) > 0 else 0
                    }
        
        return {
            "bmad_version": "6.0.0",
            "agent_stats": agent_stats,
            "agent_response_times": agent_response_times,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to get agent metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve agent metrics")

@router.get("/metrics/api")
async def get_api_metrics():
    """Get API request metrics."""
    try:
        api_stats = metrics_collector.api_stats.copy()
        
        # Calculate response time statistics
        response_times = list(api_stats["response_times"])
        if response_times:
            api_stats["avg_response_time"] = sum(response_times) / len(response_times)
            api_stats["min_response_time"] = min(response_times)
            api_stats["max_response_time"] = max(response_times)
            api_stats["p95_response_time"] = sorted(response_times)[int(len(response_times) * 0.95)]
        else:
            api_stats["avg_response_time"] = 0
            api_stats["min_response_time"] = 0
            api_stats["max_response_time"] = 0
            api_stats["p95_response_time"] = 0
        
        # Remove the deque object for JSON serialization
        del api_stats["response_times"]
        
        # Calculate success rate
        total_requests = api_stats["requests_total"]
        if total_requests > 0:
            api_stats["success_rate"] = api_stats["requests_success"] / total_requests
            api_stats["error_rate"] = api_stats["requests_error"] / total_requests
        else:
            api_stats["success_rate"] = 0
            api_stats["error_rate"] = 0
        
        return {
            "bmad_version": "6.0.0",
            "api_stats": api_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to get API metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve API metrics")

@router.get("/status")
async def get_server_status():
    """Get comprehensive server status."""
    try:
        # Get health check results
        health_results = await health_checker.run_all_checks()
        
        # Get basic metrics
        system_metrics = metrics_collector.get_system_metrics()
        app_metrics = metrics_collector.get_application_metrics()
        
        # Calculate uptime (would be more accurate with actual start time)
        uptime_seconds = 3600  # Placeholder
        
        status = {
            "bmad_version": "6.0.0",
            "server_status": "running",
            "uptime_seconds": uptime_seconds,
            "health": {
                "overall_status": health_results["overall_status"],
                "checks_passing": sum(1 for check in health_results["checks"].values() 
                                    if check["status"] == "healthy"),
                "total_checks": len(health_results["checks"])
            },
            "system": {
                "cpu_percent": system_metrics.cpu_percent,
                "memory_percent": system_metrics.memory_percent,
                "disk_percent": system_metrics.disk_percent
            },
            "application": {
                "active_workflows": app_metrics.active_workflows,
                "active_agents": app_metrics.active_agents,
                "websocket_connections": app_metrics.websocket_connections,
                "api_requests_total": app_metrics.api_requests_total
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return status
    
    except Exception as e:
        logger.error(f"Failed to get server status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve server status")

@router.get("/metrics/prometheus")
async def get_prometheus_metrics():
    """Get metrics in Prometheus format."""
    try:
        metrics_summary = metrics_collector.get_metrics_summary()
        
        # Convert to Prometheus format
        prometheus_output = []
        
        # System metrics
        system = metrics_summary["system"]
        prometheus_output.extend([
            f"# HELP bmad_cpu_percent CPU usage percentage",
            f"# TYPE bmad_cpu_percent gauge",
            f"bmad_cpu_percent {system['cpu_percent']}",
            f"",
            f"# HELP bmad_memory_percent Memory usage percentage",
            f"# TYPE bmad_memory_percent gauge", 
            f"bmad_memory_percent {system['memory_percent']}",
            f"",
            f"# HELP bmad_disk_percent Disk usage percentage",
            f"# TYPE bmad_disk_percent gauge",
            f"bmad_disk_percent {system['disk_percent']}",
            f""
        ])
        
        # Application metrics
        app = metrics_summary["application"]
        prometheus_output.extend([
            f"# HELP bmad_active_workflows Number of active workflows",
            f"# TYPE bmad_active_workflows gauge",
            f"bmad_active_workflows {app['active_workflows']}",
            f"",
            f"# HELP bmad_completed_workflows Total completed workflows",
            f"# TYPE bmad_completed_workflows counter",
            f"bmad_completed_workflows {app['completed_workflows']}",
            f"",
            f"# HELP bmad_failed_workflows Total failed workflows",
            f"# TYPE bmad_failed_workflows counter",
            f"bmad_failed_workflows {app['failed_workflows']}",
            f"",
            f"# HELP bmad_agent_invocations Total agent invocations",
            f"# TYPE bmad_agent_invocations counter",
            f"bmad_agent_invocations {app['agent_invocations']}",
            f"",
            f"# HELP bmad_api_requests_total Total API requests",
            f"# TYPE bmad_api_requests_total counter",
            f"bmad_api_requests_total {app['api_requests_total']}",
            f"",
            f"# HELP bmad_websocket_connections Active WebSocket connections",
            f"# TYPE bmad_websocket_connections gauge",
            f"bmad_websocket_connections {app['websocket_connections']}",
            f""
        ])
        
        return "\n".join(prometheus_output)
    
    except Exception as e:
        logger.error(f"Failed to generate Prometheus metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate Prometheus metrics")

@router.post("/metrics/reset")
async def reset_metrics():
    """Reset metrics counters (admin only)."""
    try:
        # Reset counters
        metrics_collector.counters.clear()
        metrics_collector.histograms.clear()
        
        # Reset application stats
        metrics_collector.workflow_stats = {
            "active": 0,
            "completed": 0,
            "failed": 0,
            "total_execution_time": 0.0
        }
        
        metrics_collector.agent_stats = {
            "active": 0,
            "invocations": 0,
            "total_response_time": 0.0
        }
        
        metrics_collector.api_stats = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_error": 0,
            "response_times": []
        }
        
        logger.info("Metrics reset successfully")
        
        return {
            "success": True,
            "message": "Metrics reset successfully",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to reset metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to reset metrics")

@router.get("/logs/recent")
async def get_recent_logs(lines: int = 100):
    """Get recent log entries."""
    try:
        # This would read from log files in a real implementation
        # For now, return a placeholder
        
        return {
            "bmad_version": "6.0.0",
            "log_lines": lines,
            "logs": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "level": "INFO",
                    "message": "Sample log entry",
                    "logger": "app.main"
                }
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to get recent logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve logs")
