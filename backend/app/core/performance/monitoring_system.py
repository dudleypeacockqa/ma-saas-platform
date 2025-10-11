"""
Enterprise Monitoring and Alerting System
Real-time monitoring with proactive incident response
"""

from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
from collections import deque
import statistics
from prometheus_client import Counter, Gauge, Histogram, Summary
import structlog

logger = structlog.get_logger()


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"  # Urgent attention needed
    MEDIUM = "medium"  # Should be addressed soon
    LOW = "low"  # Informational
    INFO = "info"  # FYI only


class MetricType(Enum):
    """Types of metrics to monitor"""
    SYSTEM = "system"
    APPLICATION = "application"
    BUSINESS = "business"
    SECURITY = "security"
    CUSTOM = "custom"


@dataclass
class Alert:
    """Alert definition"""
    id: str
    severity: AlertSeverity
    title: str
    description: str
    metric: str
    threshold: float
    current_value: float
    timestamp: datetime
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    actions_taken: List[str] = None


@dataclass
class MetricThreshold:
    """Metric threshold configuration"""
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    comparison: str  # "gt", "lt", "eq"
    duration: int  # seconds before triggering
    auto_resolve: bool = True
    escalation_policy: Optional[str] = None


# Prometheus metrics
alert_total = Counter('monitoring_alerts_total', 'Total alerts triggered', ['severity', 'type'])
alert_response_time = Histogram('monitoring_alert_response_seconds', 'Alert response time')
active_alerts = Gauge('monitoring_active_alerts', 'Currently active alerts', ['severity'])
metric_values = Gauge('monitoring_metric_values', 'Current metric values', ['metric'])
incident_duration = Summary('monitoring_incident_duration_seconds', 'Incident duration')


class MonitoringSystem:
    """Comprehensive monitoring system"""

    def __init__(self, redis_client, notification_service):
        self.redis = redis_client
        self.notification = notification_service
        self.metrics_buffer = {}
        self.alert_history = deque(maxlen=1000)
        self.active_alerts = {}
        self.thresholds = self._initialize_thresholds()
        self.anomaly_detector = AnomalyDetector()
        self.incident_manager = IncidentManager(notification_service)

    def _initialize_thresholds(self) -> Dict[str, MetricThreshold]:
        """Initialize monitoring thresholds"""

        return {
            "cpu_usage": MetricThreshold(
                metric_name="cpu_usage",
                warning_threshold=70,
                critical_threshold=90,
                comparison="gt",
                duration=120,
                escalation_policy="ops_team"
            ),
            "memory_usage": MetricThreshold(
                metric_name="memory_usage",
                warning_threshold=80,
                critical_threshold=95,
                comparison="gt",
                duration=180,
                escalation_policy="ops_team"
            ),
            "response_time_p95": MetricThreshold(
                metric_name="response_time_p95",
                warning_threshold=200,
                critical_threshold=500,
                comparison="gt",
                duration=60,
                escalation_policy="dev_team"
            ),
            "error_rate": MetricThreshold(
                metric_name="error_rate",
                warning_threshold=0.01,
                critical_threshold=0.05,
                comparison="gt",
                duration=60,
                escalation_policy="dev_team"
            ),
            "database_connections": MetricThreshold(
                metric_name="database_connections",
                warning_threshold=80,
                critical_threshold=95,
                comparison="gt",
                duration=30,
                escalation_policy="ops_team"
            ),
            "queue_depth": MetricThreshold(
                metric_name="queue_depth",
                warning_threshold=1000,
                critical_threshold=5000,
                comparison="gt",
                duration=60,
                escalation_policy="dev_team"
            ),
            "disk_usage": MetricThreshold(
                metric_name="disk_usage",
                warning_threshold=80,
                critical_threshold=90,
                comparison="gt",
                duration=300,
                escalation_policy="ops_team"
            ),
            "api_availability": MetricThreshold(
                metric_name="api_availability",
                warning_threshold=99.9,
                critical_threshold=99.5,
                comparison="lt",
                duration=60,
                escalation_policy="dev_team"
            ),
            "payment_success_rate": MetricThreshold(
                metric_name="payment_success_rate",
                warning_threshold=98,
                critical_threshold=95,
                comparison="lt",
                duration=300,
                escalation_policy="business_team"
            ),
            "active_users": MetricThreshold(
                metric_name="active_users",
                warning_threshold=10000,
                critical_threshold=15000,
                comparison="gt",
                duration=60,
                escalation_policy="ops_team"
            )
        }

    async def start_monitoring(self) -> None:
        """Start monitoring system"""

        logger.info("monitoring_system_started")

        # Start monitoring tasks
        tasks = [
            self._collect_metrics(),
            self._evaluate_thresholds(),
            self._detect_anomalies(),
            self._process_alerts(),
            self._generate_reports()
        ]

        await asyncio.gather(*tasks)

    async def _collect_metrics(self) -> None:
        """Continuously collect metrics"""

        while True:
            try:
                # Collect system metrics
                system_metrics = await self._collect_system_metrics()
                await self._store_metrics(MetricType.SYSTEM, system_metrics)

                # Collect application metrics
                app_metrics = await self._collect_application_metrics()
                await self._store_metrics(MetricType.APPLICATION, app_metrics)

                # Collect business metrics
                business_metrics = await self._collect_business_metrics()
                await self._store_metrics(MetricType.BUSINESS, business_metrics)

                # Update Prometheus metrics
                for name, value in {**system_metrics, **app_metrics, **business_metrics}.items():
                    metric_values.labels(metric=name).set(value)

                await asyncio.sleep(10)  # Collect every 10 seconds

            except Exception as e:
                logger.error("metrics_collection_error", error=str(e))
                await asyncio.sleep(30)

    async def _collect_system_metrics(self) -> Dict[str, float]:
        """Collect system-level metrics"""

        import psutil

        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()

        return {
            "cpu_usage": cpu,
            "memory_usage": memory.percent,
            "disk_usage": disk.percent,
            "network_in": network.bytes_recv / 1024 / 1024,  # MB
            "network_out": network.bytes_sent / 1024 / 1024,  # MB
            "open_files": len(psutil.Process().open_files()),
            "thread_count": psutil.Process().num_threads()
        }

    async def _collect_application_metrics(self) -> Dict[str, float]:
        """Collect application-level metrics"""

        metrics = {}

        # API metrics
        response_times = await self.redis.lrange("api:response_times", 0, 100)
        if response_times:
            times = [float(t) for t in response_times]
            metrics["response_time_p50"] = statistics.median(times)
            metrics["response_time_p95"] = statistics.quantiles(times, n=20)[18]  # 95th percentile
            metrics["response_time_p99"] = statistics.quantiles(times, n=100)[98]  # 99th percentile

        # Error rate
        errors = await self.redis.get("api:errors:count") or 0
        total = await self.redis.get("api:requests:count") or 1
        metrics["error_rate"] = float(errors) / float(total)

        # Database metrics
        db_connections = await self.redis.get("db:active_connections") or 0
        metrics["database_connections"] = float(db_connections)

        # Queue metrics
        queue_depth = await self.redis.llen("task_queue") or 0
        metrics["queue_depth"] = float(queue_depth)

        # Cache metrics
        cache_hits = await self.redis.get("cache:hits") or 0
        cache_misses = await self.redis.get("cache:misses") or 0
        total_cache = float(cache_hits) + float(cache_misses)
        metrics["cache_hit_rate"] = float(cache_hits) / total_cache if total_cache > 0 else 0

        # API availability (simplified)
        uptime = await self.redis.get("api:uptime") or 100
        metrics["api_availability"] = float(uptime)

        return metrics

    async def _collect_business_metrics(self) -> Dict[str, float]:
        """Collect business-level metrics"""

        metrics = {}

        # User metrics
        active_users = await self.redis.scard("active_users") or 0
        metrics["active_users"] = float(active_users)

        # Revenue metrics
        mrr = await self.redis.get("metrics:mrr") or 0
        metrics["mrr"] = float(mrr)

        # Payment metrics
        payment_success = await self.redis.get("payments:success") or 0
        payment_total = await self.redis.get("payments:total") or 1
        metrics["payment_success_rate"] = (float(payment_success) / float(payment_total)) * 100

        # Conversion metrics
        trials = await self.redis.get("trials:active") or 0
        conversions = await self.redis.get("trials:converted") or 0
        metrics["trial_conversion_rate"] = (float(conversions) / float(trials)) * 100 if trials else 0

        return metrics

    async def _store_metrics(
        self,
        metric_type: MetricType,
        metrics: Dict[str, float]
    ) -> None:
        """Store metrics in time-series format"""

        timestamp = datetime.utcnow()

        for name, value in metrics.items():
            # Store in buffer
            if name not in self.metrics_buffer:
                self.metrics_buffer[name] = deque(maxlen=1000)

            self.metrics_buffer[name].append({
                "timestamp": timestamp,
                "value": value,
                "type": metric_type.value
            })

            # Store in Redis for persistence
            await self.redis.zadd(
                f"metrics:{name}",
                {f"{timestamp.isoformat()}:{value}": timestamp.timestamp()}
            )

            # Trim old data (keep last 24 hours)
            cutoff = (timestamp - timedelta(days=1)).timestamp()
            await self.redis.zremrangebyscore(f"metrics:{name}", 0, cutoff)

    async def _evaluate_thresholds(self) -> None:
        """Evaluate metric thresholds and trigger alerts"""

        while True:
            try:
                for name, threshold in self.thresholds.items():
                    # Get current metric value
                    current_value = await self._get_current_metric_value(name)

                    if current_value is None:
                        continue

                    # Check threshold
                    should_alert = False
                    severity = AlertSeverity.INFO

                    if threshold.comparison == "gt":
                        if current_value > threshold.critical_threshold:
                            should_alert = True
                            severity = AlertSeverity.CRITICAL
                        elif current_value > threshold.warning_threshold:
                            should_alert = True
                            severity = AlertSeverity.HIGH
                    elif threshold.comparison == "lt":
                        if current_value < threshold.critical_threshold:
                            should_alert = True
                            severity = AlertSeverity.CRITICAL
                        elif current_value < threshold.warning_threshold:
                            should_alert = True
                            severity = AlertSeverity.HIGH

                    if should_alert:
                        await self._trigger_alert(
                            metric=name,
                            value=current_value,
                            threshold=threshold,
                            severity=severity
                        )
                    else:
                        # Check if we should resolve existing alert
                        await self._check_alert_resolution(name, current_value)

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error("threshold_evaluation_error", error=str(e))
                await asyncio.sleep(60)

    async def _get_current_metric_value(self, metric_name: str) -> Optional[float]:
        """Get current value for metric"""

        if metric_name in self.metrics_buffer:
            recent_values = list(self.metrics_buffer[metric_name])
            if recent_values:
                return recent_values[-1]["value"]

        # Try to get from Redis
        value = await self.redis.get(f"metric:current:{metric_name}")
        return float(value) if value else None

    async def _trigger_alert(
        self,
        metric: str,
        value: float,
        threshold: MetricThreshold,
        severity: AlertSeverity
    ) -> None:
        """Trigger an alert"""

        # Check if alert already exists
        alert_key = f"{metric}:{severity.value}"
        if alert_key in self.active_alerts:
            # Update existing alert
            self.active_alerts[alert_key].current_value = value
            return

        # Create new alert
        alert = Alert(
            id=f"alert_{datetime.utcnow().timestamp()}",
            severity=severity,
            title=f"{metric.replace('_', ' ').title()} Alert",
            description=f"{metric} is {value:.2f}, threshold is {threshold.warning_threshold if severity == AlertSeverity.HIGH else threshold.critical_threshold}",
            metric=metric,
            threshold=threshold.warning_threshold if severity == AlertSeverity.HIGH else threshold.critical_threshold,
            current_value=value,
            timestamp=datetime.utcnow()
        )

        # Store alert
        self.active_alerts[alert_key] = alert
        self.alert_history.append(alert)

        # Update metrics
        alert_total.labels(severity=severity.value, type=metric).inc()
        active_alerts.labels(severity=severity.value).inc()

        # Send notification
        await self.notification.send_alert(alert)

        # Create incident if critical
        if severity == AlertSeverity.CRITICAL:
            await self.incident_manager.create_incident(alert)

        logger.warning("alert_triggered",
                      metric=metric,
                      value=value,
                      severity=severity.value)

    async def _check_alert_resolution(self, metric: str, current_value: float) -> None:
        """Check if an alert should be resolved"""

        resolved_keys = []

        for alert_key, alert in self.active_alerts.items():
            if alert.metric == metric and not alert.resolved:
                threshold = self.thresholds[metric]

                # Check if value is back to normal
                is_resolved = False

                if threshold.comparison == "gt":
                    is_resolved = current_value < threshold.warning_threshold * 0.9
                elif threshold.comparison == "lt":
                    is_resolved = current_value > threshold.warning_threshold * 1.1

                if is_resolved:
                    alert.resolved = True
                    alert.resolution_time = datetime.utcnow()
                    resolved_keys.append(alert_key)

                    # Update metrics
                    active_alerts.labels(severity=alert.severity.value).dec()

                    # Calculate incident duration
                    duration = (alert.resolution_time - alert.timestamp).total_seconds()
                    incident_duration.observe(duration)

                    # Send resolution notification
                    await self.notification.send_resolution(alert)

                    logger.info("alert_resolved",
                              metric=metric,
                              duration=duration)

        # Remove resolved alerts
        for key in resolved_keys:
            del self.active_alerts[key]

    async def _detect_anomalies(self) -> None:
        """Detect anomalies using ML"""

        while True:
            try:
                for metric_name, values in self.metrics_buffer.items():
                    if len(values) >= 100:  # Need enough data
                        # Detect anomalies
                        anomalies = await self.anomaly_detector.detect(
                            metric_name,
                            list(values)
                        )

                        for anomaly in anomalies:
                            await self._trigger_anomaly_alert(metric_name, anomaly)

                await asyncio.sleep(300)  # Every 5 minutes

            except Exception as e:
                logger.error("anomaly_detection_error", error=str(e))
                await asyncio.sleep(600)

    async def _trigger_anomaly_alert(self, metric: str, anomaly: Dict[str, Any]) -> None:
        """Trigger alert for detected anomaly"""

        alert = Alert(
            id=f"anomaly_{datetime.utcnow().timestamp()}",
            severity=AlertSeverity.MEDIUM,
            title=f"Anomaly Detected: {metric}",
            description=f"Unusual pattern detected in {metric}: {anomaly['description']}",
            metric=metric,
            threshold=anomaly.get("expected_value", 0),
            current_value=anomaly.get("actual_value", 0),
            timestamp=datetime.utcnow()
        )

        await self.notification.send_alert(alert)

    async def _process_alerts(self) -> None:
        """Process and manage alerts"""

        while True:
            try:
                # Check for alert escalation
                for alert in self.active_alerts.values():
                    if not alert.resolved:
                        age = (datetime.utcnow() - alert.timestamp).total_seconds()

                        # Escalate if unresolved for too long
                        if age > 1800 and alert.severity != AlertSeverity.CRITICAL:  # 30 minutes
                            await self.incident_manager.escalate(alert)

                # Clean up old resolved alerts
                cutoff = datetime.utcnow() - timedelta(hours=24)
                self.alert_history = deque(
                    [a for a in self.alert_history if a.timestamp > cutoff],
                    maxlen=1000
                )

                await asyncio.sleep(60)  # Every minute

            except Exception as e:
                logger.error("alert_processing_error", error=str(e))
                await asyncio.sleep(120)

    async def _generate_reports(self) -> None:
        """Generate monitoring reports"""

        while True:
            try:
                # Generate hourly summary
                await self._generate_hourly_summary()

                # Generate daily report at midnight
                if datetime.utcnow().hour == 0:
                    await self._generate_daily_report()

                await asyncio.sleep(3600)  # Every hour

            except Exception as e:
                logger.error("report_generation_error", error=str(e))
                await asyncio.sleep(3600)

    async def _generate_hourly_summary(self) -> Dict[str, Any]:
        """Generate hourly monitoring summary"""

        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "active_alerts": len(self.active_alerts),
            "alerts_triggered": len([a for a in self.alert_history if
                                    (datetime.utcnow() - a.timestamp).total_seconds() < 3600]),
            "system_health": await self._calculate_system_health(),
            "key_metrics": await self._get_key_metrics()
        }

        # Store summary
        await self.redis.set(
            f"monitoring:summary:{datetime.utcnow().hour}",
            str(summary),
            ex=86400  # Keep for 24 hours
        )

        return summary

    async def _generate_daily_report(self) -> None:
        """Generate daily monitoring report"""

        report = {
            "date": datetime.utcnow().date().isoformat(),
            "total_alerts": len(self.alert_history),
            "critical_alerts": len([a for a in self.alert_history if a.severity == AlertSeverity.CRITICAL]),
            "average_resolution_time": self._calculate_avg_resolution_time(),
            "system_availability": await self._calculate_availability(),
            "top_issues": self._identify_top_issues()
        }

        # Send report
        await self.notification.send_daily_report(report)

    async def _calculate_system_health(self) -> float:
        """Calculate overall system health score"""

        health_score = 100.0

        # Deduct for active alerts
        for alert in self.active_alerts.values():
            if alert.severity == AlertSeverity.CRITICAL:
                health_score -= 30
            elif alert.severity == AlertSeverity.HIGH:
                health_score -= 15
            elif alert.severity == AlertSeverity.MEDIUM:
                health_score -= 5

        # Deduct for high resource usage
        cpu = await self._get_current_metric_value("cpu_usage") or 0
        if cpu > 80:
            health_score -= 10

        memory = await self._get_current_metric_value("memory_usage") or 0
        if memory > 85:
            health_score -= 10

        return max(0, health_score)

    async def _get_key_metrics(self) -> Dict[str, float]:
        """Get current key metrics"""

        metrics = {}

        for key in ["cpu_usage", "memory_usage", "response_time_p95", "error_rate", "active_users"]:
            value = await self._get_current_metric_value(key)
            if value is not None:
                metrics[key] = value

        return metrics

    def _calculate_avg_resolution_time(self) -> float:
        """Calculate average alert resolution time"""

        resolved_alerts = [a for a in self.alert_history if a.resolved]

        if not resolved_alerts:
            return 0

        total_time = sum(
            (a.resolution_time - a.timestamp).total_seconds()
            for a in resolved_alerts
        )

        return total_time / len(resolved_alerts)

    async def _calculate_availability(self) -> float:
        """Calculate system availability percentage"""

        # Get downtime from Redis
        downtime = await self.redis.get("system:downtime:seconds") or 0
        total_time = 86400  # 24 hours in seconds

        availability = ((total_time - float(downtime)) / total_time) * 100

        return availability

    def _identify_top_issues(self) -> List[Dict[str, Any]]:
        """Identify top recurring issues"""

        issue_counts = {}

        for alert in self.alert_history:
            key = f"{alert.metric}:{alert.severity.value}"
            issue_counts[key] = issue_counts.get(key, 0) + 1

        # Sort by frequency
        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return [
            {"issue": issue[0], "count": issue[1]}
            for issue in top_issues
        ]


class AnomalyDetector:
    """Machine learning based anomaly detection"""

    def __init__(self):
        self.models = {}
        self.threshold_multiplier = 3  # Standard deviations

    async def detect(
        self,
        metric_name: str,
        data_points: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in metric data"""

        if len(data_points) < 30:
            return []

        anomalies = []

        # Extract values
        values = [dp["value"] for dp in data_points]

        # Calculate statistics
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)

        # Simple statistical anomaly detection
        for i, dp in enumerate(data_points[-10:]):  # Check last 10 points
            z_score = abs((dp["value"] - mean) / stdev) if stdev > 0 else 0

            if z_score > self.threshold_multiplier:
                anomalies.append({
                    "timestamp": dp["timestamp"],
                    "actual_value": dp["value"],
                    "expected_value": mean,
                    "z_score": z_score,
                    "description": f"Value deviates {z_score:.1f} standard deviations from mean"
                })

        # Detect trend anomalies
        if len(values) >= 50:
            trend_anomalies = self._detect_trend_anomalies(values)
            anomalies.extend(trend_anomalies)

        return anomalies

    def _detect_trend_anomalies(self, values: List[float]) -> List[Dict[str, Any]]:
        """Detect anomalies in trends"""

        anomalies = []

        # Calculate moving average
        window_size = 10
        moving_avg = []

        for i in range(window_size, len(values)):
            window = values[i-window_size:i]
            moving_avg.append(statistics.mean(window))

        # Check for sudden trend changes
        if len(moving_avg) >= 2:
            for i in range(1, len(moving_avg)):
                change = abs(moving_avg[i] - moving_avg[i-1])
                avg_change = statistics.mean([abs(moving_avg[j] - moving_avg[j-1])
                                             for j in range(1, len(moving_avg))])

                if change > avg_change * 5:  # 5x average change
                    anomalies.append({
                        "timestamp": datetime.utcnow(),
                        "actual_value": moving_avg[i],
                        "expected_value": moving_avg[i-1],
                        "description": "Sudden trend change detected"
                    })

        return anomalies


class IncidentManager:
    """Incident management system"""

    def __init__(self, notification_service):
        self.notification = notification_service
        self.incidents = {}
        self.escalation_chains = {
            "ops_team": ["ops-lead", "cto"],
            "dev_team": ["tech-lead", "cto"],
            "business_team": ["product-manager", "ceo"]
        }

    async def create_incident(self, alert: Alert) -> str:
        """Create new incident from alert"""

        incident_id = f"INC{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        incident = {
            "id": incident_id,
            "alert": alert,
            "status": "open",
            "created_at": datetime.utcnow(),
            "assigned_to": self._get_assignee(alert),
            "updates": [],
            "resolution": None
        }

        self.incidents[incident_id] = incident

        # Send incident notification
        await self.notification.send_incident(incident)

        logger.info("incident_created", incident_id=incident_id, severity=alert.severity.value)

        return incident_id

    async def escalate(self, alert: Alert) -> None:
        """Escalate unresolved alert"""

        escalation_chain = self.escalation_chains.get(
            self.thresholds[alert.metric].escalation_policy,
            ["cto"]
        )

        for contact in escalation_chain:
            await self.notification.send_escalation(alert, contact)

        logger.warning("alert_escalated", alert_id=alert.id, metric=alert.metric)

    def _get_assignee(self, alert: Alert) -> str:
        """Get incident assignee based on alert"""

        if "database" in alert.metric or "cpu" in alert.metric or "memory" in alert.metric:
            return "ops-team"
        elif "api" in alert.metric or "error" in alert.metric:
            return "dev-team"
        elif "payment" in alert.metric or "conversion" in alert.metric:
            return "business-team"
        else:
            return "ops-team"  # Default


class NotificationService:
    """Multi-channel notification service"""

    def __init__(self):
        self.channels = ["email", "slack", "pagerduty", "webhook"]

    async def send_alert(self, alert: Alert) -> None:
        """Send alert notification"""

        message = f"""
        🚨 ALERT: {alert.title}
        Severity: {alert.severity.value.upper()}
        Metric: {alert.metric}
        Current Value: {alert.current_value:.2f}
        Threshold: {alert.threshold:.2f}
        Time: {alert.timestamp.isoformat()}
        """

        # Send to appropriate channels based on severity
        if alert.severity == AlertSeverity.CRITICAL:
            await self._send_to_all_channels(message)
        elif alert.severity == AlertSeverity.HIGH:
            await self._send_to_channels(["slack", "email"], message)
        else:
            await self._send_to_channels(["slack"], message)

    async def send_resolution(self, alert: Alert) -> None:
        """Send alert resolution notification"""

        duration = (alert.resolution_time - alert.timestamp).total_seconds() / 60

        message = f"""
        ✅ RESOLVED: {alert.title}
        Duration: {duration:.1f} minutes
        Metric: {alert.metric}
        Current Value: {alert.current_value:.2f}
        """

        await self._send_to_channels(["slack"], message)

    async def send_incident(self, incident: Dict[str, Any]) -> None:
        """Send incident notification"""

        message = f"""
        🔥 INCIDENT CREATED: {incident['id']}
        Alert: {incident['alert'].title}
        Severity: {incident['alert'].severity.value.upper()}
        Assigned To: {incident['assigned_to']}
        """

        await self._send_to_channels(["slack", "pagerduty"], message)

    async def send_escalation(self, alert: Alert, contact: str) -> None:
        """Send escalation notification"""

        message = f"""
        ⚠️ ESCALATION: {alert.title}
        Unresolved for: {(datetime.utcnow() - alert.timestamp).total_seconds() / 60:.1f} minutes
        Contact: {contact}
        Action Required: Immediate attention needed
        """

        await self._send_to_channels(["pagerduty", "email"], message)

    async def send_daily_report(self, report: Dict[str, Any]) -> None:
        """Send daily monitoring report"""

        message = f"""
        📊 Daily Monitoring Report - {report['date']}
        Total Alerts: {report['total_alerts']}
        Critical Alerts: {report['critical_alerts']}
        Avg Resolution Time: {report['average_resolution_time']:.1f} seconds
        System Availability: {report['system_availability']:.2f}%
        """

        await self._send_to_channels(["email"], message)

    async def _send_to_all_channels(self, message: str) -> None:
        """Send to all notification channels"""

        for channel in self.channels:
            await self._send_to_channel(channel, message)

    async def _send_to_channels(self, channels: List[str], message: str) -> None:
        """Send to specific channels"""

        for channel in channels:
            await self._send_to_channel(channel, message)

    async def _send_to_channel(self, channel: str, message: str) -> None:
        """Send to individual channel"""

        # In production, implement actual channel integrations
        logger.info(f"notification_sent", channel=channel, message=message[:100])

        # Simulate sending
        await asyncio.sleep(0.1)