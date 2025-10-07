"""
Integration Monitoring Service
System health monitoring, performance metrics, and uptime tracking
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import func

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


class MetricType(str, Enum):
    """Types of metrics to track"""
    RESPONSE_TIME = "response_time"
    SUCCESS_RATE = "success_rate"
    ERROR_RATE = "error_rate"
    UPTIME = "uptime"
    API_CALLS = "api_calls"
    SYNC_PERFORMANCE = "sync_performance"


class MonitoringService:
    """
    Service for monitoring integration health and performance
    """

    def __init__(self, db: Session):
        self.db = db
        self.health_check_tasks: Dict[str, asyncio.Task] = {}

    async def check_integration_health(
        self,
        organization_id: str,
        platform_name: str
    ) -> Dict[str, Any]:
        """
        Check health of a specific integration

        Returns:
            Health check result with status and metrics
        """
        from app.models.integrations import PlatformIntegration, IntegrationHealthCheck
        from app.agents.integration_agent import get_integration_agent

        # Get integration
        integration = self.db.query(PlatformIntegration).filter(
            PlatformIntegration.organization_id == organization_id,
            PlatformIntegration.platform_name == platform_name,
            PlatformIntegration.is_active == True
        ).first()

        if not integration:
            return {
                "platform_name": platform_name,
                "status": HealthStatus.UNKNOWN,
                "error": "Integration not found or not active"
            }

        start_time = datetime.utcnow()

        try:
            # Get integration agent
            agent = get_integration_agent(organization_id)

            # Test connection
            is_connected = agent.is_platform_connected(platform_name)

            if is_connected:
                # Perform deeper health check
                status_info = agent.get_platform_status(platform_name)

                response_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

                # Create health check record
                health_check = IntegrationHealthCheck(
                    integration_id=integration.id,
                    check_type="ping",
                    is_healthy=True,
                    response_time_ms=response_time_ms,
                    status_code=200
                )
                self.db.add(health_check)

                # Update integration health status
                integration.health_status = "HEALTHY"
                integration.last_health_check_at = datetime.utcnow()
                integration.last_successful_request_at = datetime.utcnow()

                self.db.commit()

                return {
                    "platform_name": platform_name,
                    "status": HealthStatus.HEALTHY,
                    "response_time_ms": response_time_ms,
                    "connection_status": status_info.get("connection_status"),
                    "last_sync": status_info.get("last_sync"),
                    "timestamp": datetime.utcnow().isoformat()
                }

            else:
                # Connection test failed
                health_check = IntegrationHealthCheck(
                    integration_id=integration.id,
                    check_type="ping",
                    is_healthy=False,
                    error_message="Connection test failed"
                )
                self.db.add(health_check)

                integration.health_status = "DOWN"
                integration.last_health_check_at = datetime.utcnow()
                integration.last_failed_request_at = datetime.utcnow()

                self.db.commit()

                return {
                    "platform_name": platform_name,
                    "status": HealthStatus.DOWN,
                    "error": "Connection test failed",
                    "timestamp": datetime.utcnow().isoformat()
                }

        except Exception as e:
            logger.error(f"Health check failed for {platform_name}: {e}")

            # Record failed health check
            health_check = IntegrationHealthCheck(
                integration_id=integration.id,
                check_type="ping",
                is_healthy=False,
                error_message=str(e)
            )
            self.db.add(health_check)

            integration.health_status = "DOWN"
            integration.last_error_message = str(e)
            integration.last_error_at = datetime.utcnow()

            self.db.commit()

            return {
                "platform_name": platform_name,
                "status": HealthStatus.DOWN,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def check_all_integrations(
        self,
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Check health of all integrations for an organization

        Returns:
            Summary of all integration health statuses
        """
        from app.models.integrations import PlatformIntegration

        # Get all active integrations
        integrations = self.db.query(PlatformIntegration).filter(
            PlatformIntegration.organization_id == organization_id,
            PlatformIntegration.is_active == True
        ).all()

        # Check health of each integration concurrently
        health_checks = []
        for integration in integrations:
            check = self.check_integration_health(
                organization_id,
                integration.platform_name
            )
            health_checks.append(check)

        results = await asyncio.gather(*health_checks, return_exceptions=True)

        # Categorize results
        healthy = []
        degraded = []
        down = []
        errors = []

        for result in results:
            if isinstance(result, Exception):
                errors.append(str(result))
                continue

            status = result.get("status")
            if status == HealthStatus.HEALTHY:
                healthy.append(result)
            elif status == HealthStatus.DEGRADED:
                degraded.append(result)
            elif status == HealthStatus.DOWN:
                down.append(result)

        return {
            "organization_id": organization_id,
            "total_integrations": len(integrations),
            "healthy_count": len(healthy),
            "degraded_count": len(degraded),
            "down_count": len(down),
            "error_count": len(errors),
            "overall_status": self._calculate_overall_status(len(healthy), len(degraded), len(down)),
            "healthy": healthy,
            "degraded": degraded,
            "down": down,
            "errors": errors,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _calculate_overall_status(
        self,
        healthy_count: int,
        degraded_count: int,
        down_count: int
    ) -> HealthStatus:
        """Calculate overall system health status"""
        total = healthy_count + degraded_count + down_count

        if total == 0:
            return HealthStatus.UNKNOWN

        if down_count == 0 and degraded_count == 0:
            return HealthStatus.HEALTHY

        if down_count > total / 2:
            return HealthStatus.DOWN

        return HealthStatus.DEGRADED

    async def get_integration_metrics(
        self,
        organization_id: str,
        platform_name: str,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get performance metrics for an integration

        Args:
            organization_id: Organization ID
            platform_name: Platform name
            period_days: Number of days to analyze

        Returns:
            Performance metrics including uptime, response times, error rates
        """
        from app.models.integrations import (
            PlatformIntegration,
            IntegrationHealthCheck,
            DataSyncJob,
            IntegrationEvent
        )

        since = datetime.utcnow() - timedelta(days=period_days)

        # Get integration
        integration = self.db.query(PlatformIntegration).filter(
            PlatformIntegration.organization_id == organization_id,
            PlatformIntegration.platform_name == platform_name
        ).first()

        if not integration:
            return {"error": "Integration not found"}

        # Get health checks
        health_checks = self.db.query(IntegrationHealthCheck).filter(
            IntegrationHealthCheck.integration_id == integration.id,
            IntegrationHealthCheck.check_time >= since
        ).all()

        # Calculate uptime
        total_checks = len(health_checks)
        successful_checks = sum(1 for check in health_checks if check.is_healthy)
        uptime_percentage = (successful_checks / total_checks * 100) if total_checks > 0 else 0

        # Calculate average response time
        response_times = [check.response_time_ms for check in health_checks if check.response_time_ms]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        # Get sync job metrics
        sync_jobs = self.db.query(DataSyncJob).filter(
            DataSyncJob.integration_id == integration.id,
            DataSyncJob.started_at >= since
        ).all()

        total_syncs = len(sync_jobs)
        successful_syncs = sum(1 for job in sync_jobs if job.status == "completed")
        failed_syncs = sum(1 for job in sync_jobs if job.status == "failed")

        # Get event metrics
        events = self.db.query(IntegrationEvent).filter(
            IntegrationEvent.integration_id == integration.id,
            IntegrationEvent.triggered_at >= since
        ).all()

        total_events = len(events)
        successful_events = sum(1 for event in events if event.status == "completed")
        failed_events = sum(1 for event in events if event.status == "failed")

        return {
            "platform_name": platform_name,
            "period_days": period_days,
            "uptime": {
                "percentage": round(uptime_percentage, 2),
                "total_checks": total_checks,
                "successful_checks": successful_checks,
                "failed_checks": total_checks - successful_checks
            },
            "performance": {
                "avg_response_time_ms": round(avg_response_time, 2),
                "min_response_time_ms": min(response_times) if response_times else 0,
                "max_response_time_ms": max(response_times) if response_times else 0
            },
            "sync_jobs": {
                "total": total_syncs,
                "successful": successful_syncs,
                "failed": failed_syncs,
                "success_rate": round((successful_syncs / total_syncs * 100) if total_syncs > 0 else 0, 2)
            },
            "events": {
                "total": total_events,
                "successful": successful_events,
                "failed": failed_events,
                "error_rate": round((failed_events / total_events * 100) if total_events > 0 else 0, 2)
            },
            "current_status": integration.health_status,
            "last_check": integration.last_health_check_at.isoformat() if integration.last_health_check_at else None,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def start_continuous_monitoring(
        self,
        organization_id: str,
        check_interval_minutes: int = 5
    ):
        """
        Start continuous health monitoring for all integrations

        Args:
            organization_id: Organization ID
            check_interval_minutes: Interval between health checks
        """
        async def monitoring_loop():
            while True:
                try:
                    await asyncio.sleep(check_interval_minutes * 60)
                    result = await self.check_all_integrations(organization_id)
                    logger.info(f"Health check completed for org {organization_id}: {result['overall_status']}")

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Monitoring error for org {organization_id}: {e}")

        # Cancel existing task if any
        task_key = f"monitor_{organization_id}"
        if task_key in self.health_check_tasks:
            self.health_check_tasks[task_key].cancel()

        # Start new monitoring task
        task = asyncio.create_task(monitoring_loop())
        self.health_check_tasks[task_key] = task

    def stop_continuous_monitoring(self, organization_id: str):
        """Stop continuous monitoring for an organization"""
        task_key = f"monitor_{organization_id}"
        if task_key in self.health_check_tasks:
            self.health_check_tasks[task_key].cancel()
            del self.health_check_tasks[task_key]

    def get_system_overview(self) -> Dict[str, Any]:
        """Get overall system health overview across all organizations"""
        from app.models.integrations import PlatformIntegration

        # Get all active integrations
        total_integrations = self.db.query(PlatformIntegration).filter(
            PlatformIntegration.is_active == True
        ).count()

        healthy = self.db.query(PlatformIntegration).filter(
            PlatformIntegration.is_active == True,
            PlatformIntegration.health_status == "HEALTHY"
        ).count()

        degraded = self.db.query(PlatformIntegration).filter(
            PlatformIntegration.is_active == True,
            PlatformIntegration.health_status == "DEGRADED"
        ).count()

        down = self.db.query(PlatformIntegration).filter(
            PlatformIntegration.is_active == True,
            PlatformIntegration.health_status == "DOWN"
        ).count()

        return {
            "total_integrations": total_integrations,
            "healthy": healthy,
            "degraded": degraded,
            "down": down,
            "overall_health_percentage": round((healthy / total_integrations * 100) if total_integrations > 0 else 0, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
