"""
Real-Time Analytics Engine - Sprint 13
Advanced real-time analytics, metrics processing, and event streaming for M&A platform
"""

from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
import json
from collections import defaultdict, deque
import statistics

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    SET = "set"

class AggregationType(Enum):
    SUM = "sum"
    AVERAGE = "average"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    PERCENTILE = "percentile"
    RATE = "rate"
    DELTA = "delta"

class EventType(Enum):
    USER_ACTION = "user_action"
    DEAL_EVENT = "deal_event"
    SYSTEM_EVENT = "system_event"
    API_CALL = "api_call"
    AI_PREDICTION = "ai_prediction"
    DOCUMENT_PROCESSED = "document_processed"
    RECOMMENDATION_GENERATED = "recommendation_generated"
    ALERT_TRIGGERED = "alert_triggered"

class TimeWindow(Enum):
    MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    HOUR = "1h"
    DAY = "1d"
    WEEK = "1w"
    MONTH = "1M"

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Metric:
    """Individual metric data point"""
    name: str
    value: Union[int, float]
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class Event:
    """Real-time event data"""
    event_id: str
    event_type: EventType
    source: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AggregatedMetric:
    """Aggregated metric result"""
    name: str
    aggregation: AggregationType
    value: Union[int, float]
    time_window: TimeWindow
    start_time: datetime
    end_time: datetime
    sample_count: int
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class Alert:
    """System alert"""
    alert_id: str
    title: str
    description: str
    severity: AlertSeverity
    metric_name: str
    threshold_value: Union[int, float]
    actual_value: Union[int, float]
    condition: str
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    resolved: bool = False

@dataclass
class AnalyticsQuery:
    """Analytics query parameters"""
    metric_names: List[str]
    aggregations: List[AggregationType]
    time_window: TimeWindow
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    tags: Dict[str, str] = field(default_factory=dict)
    group_by: List[str] = field(default_factory=list)

@dataclass
class KPI:
    """Key Performance Indicator"""
    name: str
    description: str
    current_value: Union[int, float]
    target_value: Union[int, float]
    unit: str
    trend: str  # up, down, stable
    change_percentage: float
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class RealtimeInsight:
    """Real-time business insight"""
    insight_id: str
    title: str
    description: str
    impact_level: str  # high, medium, low
    confidence_score: float
    recommended_actions: List[str]
    related_metrics: List[str]
    timestamp: datetime = field(default_factory=datetime.now)

class MetricProcessor:
    """Processes and aggregates metrics in real-time"""

    def __init__(self):
        self.metrics_buffer = defaultdict(deque)
        self.aggregation_functions = {
            AggregationType.SUM: sum,
            AggregationType.AVERAGE: statistics.mean,
            AggregationType.COUNT: len,
            AggregationType.MIN: min,
            AggregationType.MAX: max,
        }
        self.processing_stats = {
            "metrics_processed": 0,
            "aggregations_computed": 0,
            "alerts_generated": 0
        }

    def process_metric(self, metric: Metric) -> bool:
        """Process a single metric"""
        try:
            # Store metric in time-series buffer
            self.metrics_buffer[metric.name].append(metric)

            # Keep only recent metrics (last hour)
            cutoff_time = datetime.now() - timedelta(hours=1)
            while (self.metrics_buffer[metric.name] and
                   self.metrics_buffer[metric.name][0].timestamp < cutoff_time):
                self.metrics_buffer[metric.name].popleft()

            self.processing_stats["metrics_processed"] += 1
            return True

        except Exception:
            return False

    def aggregate_metrics(self, query: AnalyticsQuery) -> List[AggregatedMetric]:
        """Aggregate metrics based on query parameters"""
        results = []

        for metric_name in query.metric_names:
            if metric_name not in self.metrics_buffer:
                continue

            # Filter metrics by time window
            metrics = self._filter_by_time_window(
                self.metrics_buffer[metric_name],
                query.time_window,
                query.start_time,
                query.end_time
            )

            if not metrics:
                continue

            # Apply aggregations
            for aggregation in query.aggregations:
                aggregated_value = self._apply_aggregation(metrics, aggregation)

                result = AggregatedMetric(
                    name=metric_name,
                    aggregation=aggregation,
                    value=aggregated_value,
                    time_window=query.time_window,
                    start_time=query.start_time or metrics[0].timestamp,
                    end_time=query.end_time or metrics[-1].timestamp,
                    sample_count=len(metrics),
                    tags=query.tags
                )
                results.append(result)

        self.processing_stats["aggregations_computed"] += len(results)
        return results

    def _filter_by_time_window(self, metrics: deque, time_window: TimeWindow,
                              start_time: Optional[datetime],
                              end_time: Optional[datetime]) -> List[Metric]:
        """Filter metrics by time window"""
        now = datetime.now()

        if not start_time:
            window_duration = self._get_window_duration(time_window)
            start_time = now - window_duration

        if not end_time:
            end_time = now

        return [m for m in metrics
                if start_time <= m.timestamp <= end_time]

    def _get_window_duration(self, time_window: TimeWindow) -> timedelta:
        """Get timedelta for time window"""
        window_map = {
            TimeWindow.MINUTE: timedelta(minutes=1),
            TimeWindow.FIVE_MINUTES: timedelta(minutes=5),
            TimeWindow.FIFTEEN_MINUTES: timedelta(minutes=15),
            TimeWindow.HOUR: timedelta(hours=1),
            TimeWindow.DAY: timedelta(days=1),
            TimeWindow.WEEK: timedelta(weeks=1),
            TimeWindow.MONTH: timedelta(days=30)
        }
        return window_map.get(time_window, timedelta(hours=1))

    def _apply_aggregation(self, metrics: List[Metric],
                          aggregation: AggregationType) -> float:
        """Apply aggregation function to metrics"""
        values = [m.value for m in metrics]

        if aggregation in self.aggregation_functions:
            return self.aggregation_functions[aggregation](values)
        elif aggregation == AggregationType.PERCENTILE:
            return statistics.quantiles(values, n=100)[94]  # 95th percentile
        elif aggregation == AggregationType.RATE:
            if len(values) < 2:
                return 0.0
            time_diff = (metrics[-1].timestamp - metrics[0].timestamp).total_seconds()
            return len(values) / max(time_diff, 1.0)
        elif aggregation == AggregationType.DELTA:
            if len(values) < 2:
                return 0.0
            return values[-1] - values[0]

        return 0.0

class EventStream:
    """Manages real-time event streaming and processing"""

    def __init__(self):
        self.event_buffer = deque(maxlen=10000)
        self.event_handlers = defaultdict(list)
        self.event_stats = {
            "events_received": 0,
            "events_processed": 0,
            "handlers_executed": 0
        }

    def emit_event(self, event: Event) -> bool:
        """Emit a real-time event"""
        try:
            self.event_buffer.append(event)
            self.event_stats["events_received"] += 1

            # Process event handlers
            self._process_event_handlers(event)

            return True

        except Exception:
            return False

    def subscribe(self, event_type: EventType, handler: Callable[[Event], None]):
        """Subscribe to events of a specific type"""
        self.event_handlers[event_type].append(handler)

    def get_recent_events(self, limit: int = 100,
                         event_type: Optional[EventType] = None) -> List[Event]:
        """Get recent events"""
        events = list(self.event_buffer)

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return events[-limit:]

    def _process_event_handlers(self, event: Event):
        """Process registered event handlers"""
        handlers = self.event_handlers.get(event.event_type, [])

        for handler in handlers:
            try:
                handler(event)
                self.event_stats["handlers_executed"] += 1
            except Exception:
                pass  # Log error in production

        self.event_stats["events_processed"] += 1

class RealTimeAnalyticsEngine:
    """Central real-time analytics engine"""

    def __init__(self):
        self.metric_processor = MetricProcessor()
        self.event_stream = EventStream()
        self.kpis = {}
        self.alerts = []
        self.insights = []
        self.alert_rules = []

        # Initialize real-time processing
        self._setup_event_handlers()
        self._initialize_kpis()

    async def track_metric(self, name: str, value: Union[int, float],
                          metric_type: MetricType = MetricType.GAUGE,
                          tags: Optional[Dict[str, str]] = None) -> bool:
        """Track a real-time metric"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            tags=tags or {}
        )

        return self.metric_processor.process_metric(metric)

    async def emit_event(self, event_type: EventType, source: str,
                        data: Dict[str, Any], user_id: Optional[str] = None) -> str:
        """Emit a real-time event"""
        event_id = f"evt_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        event = Event(
            event_id=event_id,
            event_type=event_type,
            source=source,
            data=data,
            user_id=user_id
        )

        self.event_stream.emit_event(event)
        return event_id

    async def query_metrics(self, query: AnalyticsQuery) -> List[AggregatedMetric]:
        """Query aggregated metrics"""
        return self.metric_processor.aggregate_metrics(query)

    async def get_realtime_kpis(self) -> List[KPI]:
        """Get current KPI values"""
        # Update KPIs with latest data
        await self._update_kpis()
        return list(self.kpis.values())

    async def get_realtime_insights(self, limit: int = 10) -> List[RealtimeInsight]:
        """Get real-time business insights"""
        # Generate new insights based on recent data
        await self._generate_insights()
        return self.insights[-limit:]

    async def get_active_alerts(self) -> List[Alert]:
        """Get active alerts"""
        return [alert for alert in self.alerts if not alert.resolved]

    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False

    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                return True
        return False

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get real-time processing statistics"""
        return {
            "metrics": self.metric_processor.processing_stats,
            "events": self.event_stream.event_stats,
            "kpis_tracked": len(self.kpis),
            "active_alerts": len([a for a in self.alerts if not a.resolved]),
            "insights_generated": len(self.insights)
        }

    def _setup_event_handlers(self):
        """Setup event handlers for real-time processing"""

        def handle_deal_event(event: Event):
            """Handle deal-related events"""
            if event.data.get("action") == "created":
                asyncio.create_task(self.track_metric("deals.created", 1, MetricType.COUNTER))
            elif event.data.get("action") == "completed":
                asyncio.create_task(self.track_metric("deals.completed", 1, MetricType.COUNTER))

        def handle_user_action(event: Event):
            """Handle user action events"""
            asyncio.create_task(self.track_metric("user.actions", 1, MetricType.COUNTER))

            # Track user engagement
            if event.user_id:
                asyncio.create_task(self.track_metric(
                    "user.engagement",
                    1,
                    MetricType.COUNTER,
                    {"user_id": event.user_id}
                ))

        def handle_api_call(event: Event):
            """Handle API call events"""
            endpoint = event.data.get("endpoint", "unknown")
            response_time = event.data.get("response_time", 0)

            asyncio.create_task(self.track_metric("api.calls", 1, MetricType.COUNTER))
            asyncio.create_task(self.track_metric("api.response_time", response_time, MetricType.TIMER))

        # Subscribe to event types
        self.event_stream.subscribe(EventType.DEAL_EVENT, handle_deal_event)
        self.event_stream.subscribe(EventType.USER_ACTION, handle_user_action)
        self.event_stream.subscribe(EventType.API_CALL, handle_api_call)

    def _initialize_kpis(self):
        """Initialize key performance indicators"""
        self.kpis = {
            "total_deals": KPI(
                name="total_deals",
                description="Total number of deals in the system",
                current_value=0,
                target_value=1000,
                unit="deals",
                trend="up",
                change_percentage=0.0
            ),
            "active_users": KPI(
                name="active_users",
                description="Number of active users in the last 24 hours",
                current_value=0,
                target_value=500,
                unit="users",
                trend="stable",
                change_percentage=0.0
            ),
            "ai_predictions": KPI(
                name="ai_predictions",
                description="AI predictions generated today",
                current_value=0,
                target_value=100,
                unit="predictions",
                trend="up",
                change_percentage=0.0
            ),
            "avg_response_time": KPI(
                name="avg_response_time",
                description="Average API response time",
                current_value=0,
                target_value=200,
                unit="ms",
                trend="stable",
                change_percentage=0.0
            ),
            "system_uptime": KPI(
                name="system_uptime",
                description="System uptime percentage",
                current_value=99.9,
                target_value=99.9,
                unit="%",
                trend="stable",
                change_percentage=0.0
            )
        }

    async def _update_kpis(self):
        """Update KPI values with latest data"""
        # Simulate KPI updates with real-time data
        # In production, this would query actual metrics

        # Update deals KPI
        if "total_deals" in self.kpis:
            self.kpis["total_deals"].current_value += 1
            self.kpis["total_deals"].last_updated = datetime.now()

        # Update active users
        if "active_users" in self.kpis:
            self.kpis["active_users"].current_value = 245
            self.kpis["active_users"].change_percentage = 5.2

        # Update AI predictions
        if "ai_predictions" in self.kpis:
            self.kpis["ai_predictions"].current_value += 2
            self.kpis["ai_predictions"].trend = "up"

    async def _generate_insights(self):
        """Generate real-time business insights"""
        # Generate insights based on current data patterns
        now = datetime.now()

        # Example insights generation
        if len(self.insights) < 5:  # Limit insights
            insight = RealtimeInsight(
                insight_id=f"insight_{now.strftime('%Y%m%d_%H%M%S')}",
                title="Deal Activity Increasing",
                description="Deal creation rate has increased by 15% in the last hour, indicating strong market activity",
                impact_level="medium",
                confidence_score=0.87,
                recommended_actions=[
                    "Monitor capacity for increased deal processing",
                    "Review staffing for due diligence teams",
                    "Prepare additional AI prediction resources"
                ],
                related_metrics=["deals.created", "user.actions"]
            )
            self.insights.append(insight)

# Singleton instance
_real_time_analytics_engine_instance: Optional[RealTimeAnalyticsEngine] = None

def get_real_time_analytics_engine() -> RealTimeAnalyticsEngine:
    """Get the singleton Real-Time Analytics Engine instance"""
    global _real_time_analytics_engine_instance
    if _real_time_analytics_engine_instance is None:
        _real_time_analytics_engine_instance = RealTimeAnalyticsEngine()
    return _real_time_analytics_engine_instance