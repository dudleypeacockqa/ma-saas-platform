"""
Performance Monitor - Sprint 13
Advanced system health monitoring, performance tracking, and alerting for M&A platform
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
import psutil
import time
from collections import defaultdict, deque

class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class MetricCategory(Enum):
    SYSTEM = "system"
    APPLICATION = "application"
    DATABASE = "database"
    API = "api"
    USER = "user"
    BUSINESS = "business"

class AlertType(Enum):
    THRESHOLD = "threshold"
    ANOMALY = "anomaly"
    TREND = "trend"
    AVAILABILITY = "availability"
    PERFORMANCE = "performance"

class NotificationChannel(Enum):
    EMAIL = "email"
    SLACK = "slack"
    SMS = "sms"
    WEBHOOK = "webhook"
    DASHBOARD = "dashboard"

@dataclass
class HealthCheck:
    """Individual health check definition"""
    check_id: str
    name: str
    description: str
    category: MetricCategory
    check_function: Callable[[], bool]
    threshold: Optional[float] = None
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    interval_seconds: int = 60
    timeout_seconds: int = 30
    enabled: bool = True

@dataclass
class HealthCheckResult:
    """Result of a health check execution"""
    check_id: str
    status: HealthStatus
    value: Optional[float]
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SystemMetrics:
    """System-level performance metrics"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    process_count: int
    load_average: List[float]
    uptime: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ApplicationMetrics:
    """Application-level performance metrics"""
    active_users: int
    request_rate: float
    response_time_avg: float
    response_time_p95: float
    error_rate: float
    queue_size: int
    thread_count: int
    heap_usage: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class AlertRule:
    """Alert rule definition"""
    rule_id: str
    name: str
    description: str
    metric_name: str
    alert_type: AlertType
    condition: str  # e.g., "> 80", "< 10", "anomaly"
    threshold: float
    severity: str
    notification_channels: List[NotificationChannel]
    cooldown_minutes: int = 15
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Alert:
    """Active alert instance"""
    alert_id: str
    rule_id: str
    title: str
    description: str
    severity: str
    metric_name: str
    current_value: float
    threshold_value: float
    status: str  # active, acknowledged, resolved
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None

@dataclass
class PerformanceReport:
    """Performance summary report"""
    report_id: str
    time_period: str
    system_health: HealthStatus
    key_metrics: Dict[str, float]
    trends: Dict[str, str]
    alerts_summary: Dict[str, int]
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.now)

class SystemHealthMonitor:
    """Monitors system-level health and performance"""

    def __init__(self):
        self.health_checks = {}
        self.check_results = defaultdict(deque)
        self.system_metrics_history = deque(maxlen=1440)  # 24 hours of minute data
        self.monitoring_active = False

    def register_health_check(self, health_check: HealthCheck):
        """Register a new health check"""
        self.health_checks[health_check.check_id] = health_check

    def remove_health_check(self, check_id: str) -> bool:
        """Remove a health check"""
        if check_id in self.health_checks:
            del self.health_checks[check_id]
            return True
        return False

    async def start_monitoring(self):
        """Start continuous health monitoring"""
        self.monitoring_active = True

        # Start health check tasks
        tasks = []
        for check in self.health_checks.values():
            if check.enabled:
                task = asyncio.create_task(self._run_health_check_loop(check))
                tasks.append(task)

        # Start system metrics collection
        system_task = asyncio.create_task(self._collect_system_metrics_loop())
        tasks.append(system_task)

        await asyncio.gather(*tasks)

    async def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring_active = False

    async def _run_health_check_loop(self, health_check: HealthCheck):
        """Run health check in a loop"""
        while self.monitoring_active:
            try:
                result = await self._execute_health_check(health_check)
                self.check_results[health_check.check_id].append(result)

                # Keep only recent results (last 24 hours)
                cutoff_time = datetime.now() - timedelta(hours=24)
                while (self.check_results[health_check.check_id] and
                       self.check_results[health_check.check_id][0].timestamp < cutoff_time):
                    self.check_results[health_check.check_id].popleft()

            except Exception as e:
                # Log error and continue
                error_result = HealthCheckResult(
                    check_id=health_check.check_id,
                    status=HealthStatus.UNKNOWN,
                    value=None,
                    message=f"Health check failed: {str(e)}"
                )
                self.check_results[health_check.check_id].append(error_result)

            await asyncio.sleep(health_check.interval_seconds)

    async def _execute_health_check(self, health_check: HealthCheck) -> HealthCheckResult:
        """Execute a single health check"""
        start_time = time.time()

        try:
            # Execute check function with timeout
            result = await asyncio.wait_for(
                asyncio.create_task(asyncio.to_thread(health_check.check_function)),
                timeout=health_check.timeout_seconds
            )

            execution_time = time.time() - start_time

            # Determine status based on result and thresholds
            if isinstance(result, bool):
                status = HealthStatus.HEALTHY if result else HealthStatus.CRITICAL
                value = 1.0 if result else 0.0
                message = "Check passed" if result else "Check failed"
            elif isinstance(result, (int, float)):
                value = float(result)
                status, message = self._evaluate_thresholds(value, health_check)
            else:
                status = HealthStatus.UNKNOWN
                value = None
                message = f"Unexpected result type: {type(result)}"

            return HealthCheckResult(
                check_id=health_check.check_id,
                status=status,
                value=value,
                message=message,
                execution_time=execution_time
            )

        except asyncio.TimeoutError:
            return HealthCheckResult(
                check_id=health_check.check_id,
                status=HealthStatus.CRITICAL,
                value=None,
                message=f"Health check timed out after {health_check.timeout_seconds}s",
                execution_time=health_check.timeout_seconds
            )

    def _evaluate_thresholds(self, value: float, health_check: HealthCheck) -> tuple:
        """Evaluate value against thresholds"""
        if health_check.critical_threshold is not None:
            if value >= health_check.critical_threshold:
                return HealthStatus.CRITICAL, f"Value {value} exceeds critical threshold {health_check.critical_threshold}"

        if health_check.warning_threshold is not None:
            if value >= health_check.warning_threshold:
                return HealthStatus.WARNING, f"Value {value} exceeds warning threshold {health_check.warning_threshold}"

        return HealthStatus.HEALTHY, f"Value {value} is within normal range"

    async def _collect_system_metrics_loop(self):
        """Collect system metrics continuously"""
        while self.monitoring_active:
            try:
                metrics = await self._collect_system_metrics()
                self.system_metrics_history.append(metrics)
            except Exception:
                pass  # Log error in production

            await asyncio.sleep(60)  # Collect every minute

    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        # CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)

        # Memory usage
        memory = psutil.virtual_memory()
        memory_usage = memory.percent

        # Disk usage
        disk = psutil.disk_usage('/')
        disk_usage = (disk.used / disk.total) * 100

        # Network I/O
        network = psutil.net_io_counters()
        network_io = {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
            "packets_sent": network.packets_sent,
            "packets_recv": network.packets_recv
        }

        # Process count
        process_count = len(psutil.pids())

        # Load average (Unix-like systems)
        try:
            load_avg = list(psutil.getloadavg())
        except AttributeError:
            load_avg = [0.0, 0.0, 0.0]  # Windows doesn't have load average

        # System uptime
        uptime = time.time() - psutil.boot_time()

        return SystemMetrics(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            network_io=network_io,
            process_count=process_count,
            load_average=load_avg,
            uptime=uptime
        )

    def get_overall_health(self) -> HealthStatus:
        """Get overall system health status"""
        if not self.check_results:
            return HealthStatus.UNKNOWN

        # Get latest results for each check
        latest_results = []
        for check_id, results in self.check_results.items():
            if results:
                latest_results.append(results[-1])

        if not latest_results:
            return HealthStatus.UNKNOWN

        # Determine overall status
        statuses = [result.status for result in latest_results]

        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        elif HealthStatus.WARNING in statuses:
            return HealthStatus.WARNING
        elif all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN

    def get_latest_metrics(self) -> Optional[SystemMetrics]:
        """Get latest system metrics"""
        return self.system_metrics_history[-1] if self.system_metrics_history else None

class AlertManager:
    """Manages alerts and notifications"""

    def __init__(self):
        self.alert_rules = {}
        self.active_alerts = {}
        self.alert_history = deque(maxlen=10000)
        self.notification_handlers = {}
        self.cooldown_tracker = defaultdict(datetime)

    def add_alert_rule(self, rule: AlertRule):
        """Add a new alert rule"""
        self.alert_rules[rule.rule_id] = rule

    def remove_alert_rule(self, rule_id: str) -> bool:
        """Remove an alert rule"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            return True
        return False

    def register_notification_handler(self, channel: NotificationChannel, handler: Callable):
        """Register notification handler for a channel"""
        self.notification_handlers[channel] = handler

    async def evaluate_metrics(self, metrics: Dict[str, float]):
        """Evaluate metrics against alert rules"""
        current_time = datetime.now()

        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue

            metric_value = metrics.get(rule.metric_name)
            if metric_value is None:
                continue

            # Check if rule should trigger
            should_alert = self._evaluate_rule_condition(rule, metric_value)

            if should_alert:
                # Check cooldown
                last_alert_time = self.cooldown_tracker.get(rule.rule_id)
                if (last_alert_time and
                    current_time - last_alert_time < timedelta(minutes=rule.cooldown_minutes)):
                    continue

                # Create alert
                await self._create_alert(rule, metric_value)
                self.cooldown_tracker[rule.rule_id] = current_time

    def _evaluate_rule_condition(self, rule: AlertRule, value: float) -> bool:
        """Evaluate if rule condition is met"""
        condition = rule.condition.strip()

        if condition.startswith('>'):
            threshold = float(condition[1:].strip())
            return value > threshold
        elif condition.startswith('<'):
            threshold = float(condition[1:].strip())
            return value < threshold
        elif condition.startswith('>='):
            threshold = float(condition[2:].strip())
            return value >= threshold
        elif condition.startswith('<='):
            threshold = float(condition[2:].strip())
            return value <= threshold
        elif condition == 'anomaly':
            # Implement anomaly detection logic
            return self._detect_anomaly(rule.metric_name, value)

        return False

    def _detect_anomaly(self, metric_name: str, value: float) -> bool:
        """Simple anomaly detection"""
        # This is a simplified implementation
        # In production, use more sophisticated anomaly detection
        return False

    async def _create_alert(self, rule: AlertRule, current_value: float):
        """Create and send alert"""
        alert_id = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        alert = Alert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            title=f"Alert: {rule.name}",
            description=rule.description,
            severity=rule.severity,
            metric_name=rule.metric_name,
            current_value=current_value,
            threshold_value=rule.threshold,
            status="active"
        )

        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)

        # Send notifications
        await self._send_notifications(alert, rule)

    async def _send_notifications(self, alert: Alert, rule: AlertRule):
        """Send alert notifications"""
        for channel in rule.notification_channels:
            handler = self.notification_handlers.get(channel)
            if handler:
                try:
                    await handler(alert)
                except Exception:
                    pass  # Log error in production

    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = "acknowledged"
            alert.acknowledged_at = datetime.now()
            alert.acknowledged_by = acknowledged_by
            return True
        return False

    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = "resolved"
            alert.resolved_at = datetime.now()
            del self.active_alerts[alert_id]
            return True
        return False

    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return list(self.active_alerts.values())

    def get_alert_summary(self) -> Dict[str, int]:
        """Get alert summary statistics"""
        active_alerts = self.get_active_alerts()

        summary = {
            "total_active": len(active_alerts),
            "critical": len([a for a in active_alerts if a.severity == "critical"]),
            "warning": len([a for a in active_alerts if a.severity == "warning"]),
            "acknowledged": len([a for a in active_alerts if a.status == "acknowledged"])
        }

        return summary

class PerformanceMonitor:
    """Central performance monitoring system"""

    def __init__(self):
        self.system_monitor = SystemHealthMonitor()
        self.alert_manager = AlertManager()
        self.application_metrics = deque(maxlen=1440)  # 24 hours
        self.monitoring_active = False

        # Initialize default health checks
        self._initialize_default_health_checks()
        self._initialize_default_alert_rules()

    async def start_monitoring(self):
        """Start comprehensive monitoring"""
        self.monitoring_active = True

        # Start system monitoring
        system_task = asyncio.create_task(self.system_monitor.start_monitoring())

        # Start metric evaluation loop
        evaluation_task = asyncio.create_task(self._metric_evaluation_loop())

        await asyncio.gather(system_task, evaluation_task)

    async def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        await self.system_monitor.stop_monitoring()

    async def record_application_metric(self, metrics: ApplicationMetrics):
        """Record application-level metrics"""
        self.application_metrics.append(metrics)

        # Convert to dict for alert evaluation
        metrics_dict = {
            "active_users": metrics.active_users,
            "request_rate": metrics.request_rate,
            "response_time_avg": metrics.response_time_avg,
            "response_time_p95": metrics.response_time_p95,
            "error_rate": metrics.error_rate,
            "queue_size": metrics.queue_size,
            "heap_usage": metrics.heap_usage
        }

        await self.alert_manager.evaluate_metrics(metrics_dict)

    async def _metric_evaluation_loop(self):
        """Continuously evaluate metrics for alerts"""
        while self.monitoring_active:
            try:
                # Get latest system metrics
                system_metrics = self.system_monitor.get_latest_metrics()
                if system_metrics:
                    metrics_dict = {
                        "cpu_usage": system_metrics.cpu_usage,
                        "memory_usage": system_metrics.memory_usage,
                        "disk_usage": system_metrics.disk_usage,
                        "process_count": system_metrics.process_count
                    }
                    await self.alert_manager.evaluate_metrics(metrics_dict)

            except Exception:
                pass  # Log error in production

            await asyncio.sleep(60)  # Evaluate every minute

    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health"""
        overall_health = self.system_monitor.get_overall_health()
        latest_metrics = self.system_monitor.get_latest_metrics()
        active_alerts = self.alert_manager.get_active_alerts()

        return {
            "overall_status": overall_health.value,
            "system_metrics": latest_metrics.__dict__ if latest_metrics else None,
            "active_alerts_count": len(active_alerts),
            "alert_summary": self.alert_manager.get_alert_summary(),
            "last_updated": datetime.now().isoformat()
        }

    def get_performance_report(self, hours: int = 24) -> PerformanceReport:
        """Generate performance report"""
        report_id = f"perf_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Calculate key metrics
        system_metrics = self.system_monitor.get_latest_metrics()
        key_metrics = {}

        if system_metrics:
            key_metrics = {
                "cpu_usage": system_metrics.cpu_usage,
                "memory_usage": system_metrics.memory_usage,
                "disk_usage": system_metrics.disk_usage,
                "uptime": system_metrics.uptime
            }

        # Generate recommendations
        recommendations = self._generate_recommendations(key_metrics)

        return PerformanceReport(
            report_id=report_id,
            time_period=f"Last {hours} hours",
            system_health=self.system_monitor.get_overall_health(),
            key_metrics=key_metrics,
            trends={"cpu": "stable", "memory": "increasing", "disk": "stable"},
            alerts_summary=self.alert_manager.get_alert_summary(),
            recommendations=recommendations
        )

    def _generate_recommendations(self, metrics: Dict[str, float]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []

        cpu_usage = metrics.get("cpu_usage", 0)
        memory_usage = metrics.get("memory_usage", 0)
        disk_usage = metrics.get("disk_usage", 0)

        if cpu_usage > 80:
            recommendations.append("Consider scaling CPU resources or optimizing high-CPU processes")

        if memory_usage > 85:
            recommendations.append("Memory usage is high - consider increasing memory or optimizing memory usage")

        if disk_usage > 90:
            recommendations.append("Disk usage is critical - clean up old files or expand storage")

        if not recommendations:
            recommendations.append("System performance is optimal")

        return recommendations

    def _initialize_default_health_checks(self):
        """Initialize default health checks"""

        def cpu_check():
            return psutil.cpu_percent(interval=1) < 90

        def memory_check():
            return psutil.virtual_memory().percent < 90

        def disk_check():
            return (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100 < 95

        # Register checks
        self.system_monitor.register_health_check(HealthCheck(
            check_id="cpu_usage",
            name="CPU Usage",
            description="Monitor CPU usage percentage",
            category=MetricCategory.SYSTEM,
            check_function=cpu_check,
            warning_threshold=80,
            critical_threshold=90
        ))

        self.system_monitor.register_health_check(HealthCheck(
            check_id="memory_usage",
            name="Memory Usage",
            description="Monitor memory usage percentage",
            category=MetricCategory.SYSTEM,
            check_function=memory_check,
            warning_threshold=80,
            critical_threshold=90
        ))

        self.system_monitor.register_health_check(HealthCheck(
            check_id="disk_usage",
            name="Disk Usage",
            description="Monitor disk usage percentage",
            category=MetricCategory.SYSTEM,
            check_function=disk_check,
            warning_threshold=85,
            critical_threshold=95
        ))

    def _initialize_default_alert_rules(self):
        """Initialize default alert rules"""

        rules = [
            AlertRule(
                rule_id="high_cpu",
                name="High CPU Usage",
                description="CPU usage exceeds 80%",
                metric_name="cpu_usage",
                alert_type=AlertType.THRESHOLD,
                condition="> 80",
                threshold=80,
                severity="warning",
                notification_channels=[NotificationChannel.DASHBOARD]
            ),
            AlertRule(
                rule_id="high_memory",
                name="High Memory Usage",
                description="Memory usage exceeds 85%",
                metric_name="memory_usage",
                alert_type=AlertType.THRESHOLD,
                condition="> 85",
                threshold=85,
                severity="warning",
                notification_channels=[NotificationChannel.DASHBOARD]
            ),
            AlertRule(
                rule_id="critical_disk",
                name="Critical Disk Usage",
                description="Disk usage exceeds 95%",
                metric_name="disk_usage",
                alert_type=AlertType.THRESHOLD,
                condition="> 95",
                threshold=95,
                severity="critical",
                notification_channels=[NotificationChannel.DASHBOARD]
            )
        ]

        for rule in rules:
            self.alert_manager.add_alert_rule(rule)

# Singleton instance
_performance_monitor_instance: Optional[PerformanceMonitor] = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get the singleton Performance Monitor instance"""
    global _performance_monitor_instance
    if _performance_monitor_instance is None:
        _performance_monitor_instance = PerformanceMonitor()
    return _performance_monitor_instance