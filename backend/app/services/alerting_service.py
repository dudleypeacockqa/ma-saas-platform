"""
Alerting Service
Alert rules, notification delivery, and incident management
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Types of alerts"""
    INTEGRATION_DOWN = "integration_down"
    INTEGRATION_DEGRADED = "integration_degraded"
    SYNC_FAILED = "sync_failed"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    API_ERROR = "api_error"
    WORKFLOW_FAILED = "workflow_failed"
    QUOTA_EXCEEDED = "quota_exceeded"
    HIGH_ERROR_RATE = "high_error_rate"
    SLOW_RESPONSE = "slow_response"


class NotificationChannel(str, Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    IN_APP = "in_app"
    SMS = "sms"


class AlertingService:
    """
    Service for managing alerts and notifications
    """

    def __init__(self, db: Session):
        self.db = db
        self.alert_rules: Dict[str, Dict[str, Any]] = self._load_default_rules()

    def _load_default_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load default alert rules"""
        return {
            "integration_down": {
                "type": AlertType.INTEGRATION_DOWN,
                "severity": AlertSeverity.CRITICAL,
                "threshold": 1,  # Alert immediately
                "window_minutes": 5,
                "notification_channels": [NotificationChannel.EMAIL, NotificationChannel.IN_APP]
            },
            "integration_degraded": {
                "type": AlertType.INTEGRATION_DEGRADED,
                "severity": AlertSeverity.WARNING,
                "threshold": 3,  # Alert after 3 occurrences
                "window_minutes": 15,
                "notification_channels": [NotificationChannel.IN_APP]
            },
            "sync_failed": {
                "type": AlertType.SYNC_FAILED,
                "severity": AlertSeverity.ERROR,
                "threshold": 2,  # Alert after 2 consecutive failures
                "window_minutes": 30,
                "notification_channels": [NotificationChannel.EMAIL, NotificationChannel.IN_APP]
            },
            "rate_limit_exceeded": {
                "type": AlertType.RATE_LIMIT_EXCEEDED,
                "severity": AlertSeverity.WARNING,
                "threshold": 1,
                "window_minutes": 60,
                "notification_channels": [NotificationChannel.IN_APP]
            },
            "high_error_rate": {
                "type": AlertType.HIGH_ERROR_RATE,
                "severity": AlertSeverity.ERROR,
                "threshold": 10,  # 10% error rate
                "window_minutes": 60,
                "notification_channels": [NotificationChannel.EMAIL, NotificationChannel.SLACK]
            },
            "workflow_failed": {
                "type": AlertType.WORKFLOW_FAILED,
                "severity": AlertSeverity.ERROR,
                "threshold": 1,
                "window_minutes": 5,
                "notification_channels": [NotificationChannel.EMAIL, NotificationChannel.IN_APP]
            }
        }

    async def create_alert(
        self,
        organization_id: str,
        alert_type: AlertType,
        platform_name: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.WARNING,
        alert_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create an alert

        Args:
            organization_id: Organization ID
            alert_type: Type of alert
            platform_name: Platform that triggered the alert
            message: Alert message
            severity: Alert severity
            alert_data: Additional context data

        Returns:
            Created alert details
        """
        from app.models.integrations import IntegrationAlert

        # Check if we should create this alert based on rules
        rule = self.alert_rules.get(alert_type)
        if not rule:
            logger.warning(f"No rule found for alert type: {alert_type}")
            return {"error": "No alert rule configured"}

        # Check for duplicate recent alerts
        since = datetime.utcnow() - timedelta(minutes=rule.get("window_minutes", 60))
        existing_alert = self.db.query(IntegrationAlert).filter(
            IntegrationAlert.organization_id == organization_id,
            IntegrationAlert.platform_name == platform_name,
            IntegrationAlert.alert_type == alert_type,
            IntegrationAlert.is_resolved == False,
            IntegrationAlert.created_at >= since
        ).first()

        if existing_alert:
            logger.info(f"Duplicate alert suppressed for {platform_name}")
            return {
                "suppressed": True,
                "existing_alert_id": existing_alert.id
            }

        # Create alert
        alert = IntegrationAlert(
            organization_id=organization_id,
            platform_name=platform_name,
            alert_type=alert_type,
            severity=severity,
            message=message,
            alert_data=alert_data or {}
        )

        self.db.add(alert)
        self.db.commit()

        # Send notifications
        notification_result = await self._send_notifications(
            alert,
            rule.get("notification_channels", [NotificationChannel.IN_APP])
        )

        alert.notification_sent = notification_result.get("success", False)
        alert.notification_sent_at = datetime.utcnow()
        self.db.commit()

        return {
            "alert_id": alert.id,
            "alert_type": alert_type,
            "severity": severity,
            "created_at": alert.created_at.isoformat(),
            "notification_sent": alert.notification_sent
        }

    async def _send_notifications(
        self,
        alert: Any,
        channels: List[NotificationChannel]
    ) -> Dict[str, Any]:
        """
        Send alert notifications through specified channels

        Args:
            alert: Alert object
            channels: List of notification channels

        Returns:
            Notification delivery result
        """
        results = {}

        for channel in channels:
            try:
                if channel == NotificationChannel.EMAIL:
                    result = await self._send_email_notification(alert)
                    results["email"] = result

                elif channel == NotificationChannel.SLACK:
                    result = await self._send_slack_notification(alert)
                    results["slack"] = result

                elif channel == NotificationChannel.WEBHOOK:
                    result = await self._send_webhook_notification(alert)
                    results["webhook"] = result

                elif channel == NotificationChannel.IN_APP:
                    result = await self._create_in_app_notification(alert)
                    results["in_app"] = result

            except Exception as e:
                logger.error(f"Failed to send {channel} notification: {e}")
                results[channel] = {"success": False, "error": str(e)}

        success = any(result.get("success", False) for result in results.values())

        return {
            "success": success,
            "channels": results
        }

    async def _send_email_notification(self, alert: Any) -> Dict[str, bool]:
        """Send email notification"""
        # TODO: Implement email sending
        # For now, just log
        logger.info(f"Email notification for alert {alert.id}: {alert.message}")
        return {"success": True, "channel": "email"}

    async def _send_slack_notification(self, alert: Any) -> Dict[str, bool]:
        """Send Slack notification"""
        # TODO: Implement Slack webhook
        logger.info(f"Slack notification for alert {alert.id}: {alert.message}")
        return {"success": True, "channel": "slack"}

    async def _send_webhook_notification(self, alert: Any) -> Dict[str, bool]:
        """Send webhook notification"""
        # TODO: Implement webhook delivery
        logger.info(f"Webhook notification for alert {alert.id}: {alert.message}")
        return {"success": True, "channel": "webhook"}

    async def _create_in_app_notification(self, alert: Any) -> Dict[str, bool]:
        """Create in-app notification"""
        # In-app notifications are handled by the alert record itself
        logger.info(f"In-app notification for alert {alert.id}: {alert.message}")
        return {"success": True, "channel": "in_app"}

    async def resolve_alert(
        self,
        alert_id: int,
        resolution_notes: Optional[str] = None
    ) -> bool:
        """
        Resolve an alert

        Args:
            alert_id: Alert ID
            resolution_notes: Notes about how the issue was resolved

        Returns:
            True if alert was resolved
        """
        from app.models.integrations import IntegrationAlert

        alert = self.db.query(IntegrationAlert).filter(
            IntegrationAlert.id == alert_id
        ).first()

        if not alert:
            return False

        alert.is_resolved = True
        alert.resolved_at = datetime.utcnow()
        alert.resolution_notes = resolution_notes

        self.db.commit()

        logger.info(f"Alert {alert_id} resolved")
        return True

    async def get_active_alerts(
        self,
        organization_id: str,
        severity: Optional[AlertSeverity] = None,
        platform_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get active (unresolved) alerts

        Args:
            organization_id: Organization ID
            severity: Optional severity filter
            platform_name: Optional platform filter

        Returns:
            List of active alerts
        """
        from app.models.integrations import IntegrationAlert

        query = self.db.query(IntegrationAlert).filter(
            IntegrationAlert.organization_id == organization_id,
            IntegrationAlert.is_resolved == False
        )

        if severity:
            query = query.filter(IntegrationAlert.severity == severity)

        if platform_name:
            query = query.filter(IntegrationAlert.platform_name == platform_name)

        alerts = query.order_by(IntegrationAlert.created_at.desc()).all()

        return [
            {
                "id": alert.id,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "platform_name": alert.platform_name,
                "message": alert.message,
                "created_at": alert.created_at.isoformat(),
                "alert_data": alert.alert_data
            }
            for alert in alerts
        ]

    async def get_alert_summary(
        self,
        organization_id: str,
        period_days: int = 7
    ) -> Dict[str, Any]:
        """
        Get alert summary for a time period

        Args:
            organization_id: Organization ID
            period_days: Number of days to analyze

        Returns:
            Alert summary statistics
        """
        from app.models.integrations import IntegrationAlert

        since = datetime.utcnow() - timedelta(days=period_days)

        alerts = self.db.query(IntegrationAlert).filter(
            IntegrationAlert.organization_id == organization_id,
            IntegrationAlert.created_at >= since
        ).all()

        total = len(alerts)
        resolved = sum(1 for alert in alerts if alert.is_resolved)
        active = total - resolved

        by_severity = {
            "critical": sum(1 for alert in alerts if alert.severity == AlertSeverity.CRITICAL),
            "error": sum(1 for alert in alerts if alert.severity == AlertSeverity.ERROR),
            "warning": sum(1 for alert in alerts if alert.severity == AlertSeverity.WARNING),
            "info": sum(1 for alert in alerts if alert.severity == AlertSeverity.INFO)
        }

        by_type = {}
        for alert in alerts:
            alert_type = alert.alert_type
            by_type[alert_type] = by_type.get(alert_type, 0) + 1

        return {
            "period_days": period_days,
            "total_alerts": total,
            "active_alerts": active,
            "resolved_alerts": resolved,
            "by_severity": by_severity,
            "by_type": by_type,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def check_and_create_alerts(
        self,
        organization_id: str
    ) -> List[Dict[str, Any]]:
        """
        Check monitoring data and create alerts based on rules

        Args:
            organization_id: Organization ID

        Returns:
            List of created alerts
        """
        from app.models.integrations import PlatformIntegration
        from app.services.monitoring_service import MonitoringService

        created_alerts = []

        # Get monitoring service
        monitoring = MonitoringService(self.db)

        # Check health of all integrations
        health_status = await monitoring.check_all_integrations(organization_id)

        # Create alerts for down integrations
        for down_integration in health_status.get("down", []):
            alert = await self.create_alert(
                organization_id=organization_id,
                alert_type=AlertType.INTEGRATION_DOWN,
                platform_name=down_integration["platform_name"],
                message=f"Integration {down_integration['platform_name']} is down",
                severity=AlertSeverity.CRITICAL,
                alert_data=down_integration
            )
            if not alert.get("suppressed"):
                created_alerts.append(alert)

        # Create alerts for degraded integrations
        for degraded_integration in health_status.get("degraded", []):
            alert = await self.create_alert(
                organization_id=organization_id,
                alert_type=AlertType.INTEGRATION_DEGRADED,
                platform_name=degraded_integration["platform_name"],
                message=f"Integration {degraded_integration['platform_name']} is degraded",
                severity=AlertSeverity.WARNING,
                alert_data=degraded_integration
            )
            if not alert.get("suppressed"):
                created_alerts.append(alert)

        return created_alerts


# Singleton instance
_alerting_service: Optional[AlertingService] = None


def get_alerting_service(db: Session) -> AlertingService:
    """Get or create alerting service instance"""
    global _alerting_service
    if _alerting_service is None:
        _alerting_service = AlertingService(db)
    return _alerting_service
