"""
Analytics Models for Performance Tracking and Business Intelligence
Handles metrics collection, aggregation, reporting, and alerting
"""
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime,
    ForeignKey, JSON, Enum as SQLEnum, UniqueConstraint, Index,
    Numeric, Date, Time
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from datetime import datetime, date, time
import enum
from app.models.base import BaseModel, UUIDPrimaryKeyMixin, TimestampMixin, TenantModel

class MetricType(str, enum.Enum):
    """Types of business metrics"""
    # Revenue Metrics
    MRR = "mrr"  # Monthly Recurring Revenue
    ARR = "arr"  # Annual Recurring Revenue
    REVENUE = "revenue"
    GROSS_MARGIN = "gross_margin"
    LTV = "ltv"  # Customer Lifetime Value
    CAC = "cac"  # Customer Acquisition Cost

    # Customer Metrics
    SUBSCRIBERS = "subscribers"
    CHURN_RATE = "churn_rate"
    RETENTION_RATE = "retention_rate"
    NPS = "nps"  # Net Promoter Score
    ACTIVATION_RATE = "activation_rate"

    # Deal Metrics
    DEAL_PIPELINE_VALUE = "deal_pipeline_value"
    DEAL_WIN_RATE = "deal_win_rate"
    DEAL_VELOCITY = "deal_velocity"
    DEAL_COUNT = "deal_count"
    AVG_DEAL_SIZE = "avg_deal_size"

    # Content Metrics
    PODCAST_DOWNLOADS = "podcast_downloads"
    PODCAST_LISTENERS = "podcast_listeners"
    BLOG_VIEWS = "blog_views"
    CONTENT_ENGAGEMENT = "content_engagement"
    SOCIAL_REACH = "social_reach"

    # Operational Metrics
    PLATFORM_UPTIME = "platform_uptime"
    API_RESPONSE_TIME = "api_response_time"
    ERROR_RATE = "error_rate"
    ACTIVE_USERS = "active_users"
    FEATURE_ADOPTION = "feature_adoption"

class AggregationPeriod(str, enum.Enum):
    """Time periods for metric aggregation"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class AlertSeverity(str, enum.Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ComparisonOperator(str, enum.Enum):
    """Operators for alert conditions"""
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    GREATER_EQUAL = "gte"
    LESS_EQUAL = "lte"
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    PERCENT_CHANGE = "percent_change"

class MetricSnapshot(BaseModel, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Time-series storage for raw metric data
    Captures point-in-time metric values for historical analysis
    """
    __tablename__ = "metric_snapshots"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    metric_type = Column(SQLEnum(MetricType), nullable=False, index=True)
    metric_value = Column(Numeric(20, 4), nullable=False)

    # Temporal attributes
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    date = Column(Date, nullable=False, index=True)
    hour = Column(Integer)  # 0-23

    # Dimensions for filtering and grouping
    dimensions = Column(JSONB, default={})  # e.g., {"product": "premium", "region": "US"}
    tags = Column(ARRAY(String), default=[])

    # Additional context
    metadata = Column(JSONB, default={})
    source = Column(String(50))  # e.g., "api", "batch_job", "webhook"

    # Relationships
    organization = relationship("Organization", back_populates="metric_snapshots")

    # Indexes for common queries
    __table_args__ = (
        Index("idx_metric_snapshots_org_type_date", "organization_id", "metric_type", "date"),
        Index("idx_metric_snapshots_timestamp", "timestamp"),
        Index("idx_metric_snapshots_dimensions", "dimensions", postgresql_using="gin"),
    )

class AggregatedMetric(BaseModel, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Pre-computed aggregated metrics for fast querying
    Stores rolled-up data at various time granularities
    """
    __tablename__ = "aggregated_metrics"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    metric_type = Column(SQLEnum(MetricType), nullable=False, index=True)
    period = Column(SQLEnum(AggregationPeriod), nullable=False, index=True)

    # Time window for aggregation
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False)

    # Aggregated values
    sum_value = Column(Numeric(20, 4))
    avg_value = Column(Numeric(20, 4))
    min_value = Column(Numeric(20, 4))
    max_value = Column(Numeric(20, 4))
    count = Column(Integer, default=0)

    # Statistical measures
    std_deviation = Column(Numeric(20, 4))
    percentile_25 = Column(Numeric(20, 4))
    percentile_50 = Column(Numeric(20, 4))  # median
    percentile_75 = Column(Numeric(20, 4))
    percentile_95 = Column(Numeric(20, 4))

    # Period-over-period comparisons
    previous_period_value = Column(Numeric(20, 4))
    period_change = Column(Numeric(20, 4))  # Absolute change
    period_change_percent = Column(Numeric(10, 2))  # Percentage change

    # Year-over-year comparisons
    year_ago_value = Column(Numeric(20, 4))
    yoy_change = Column(Numeric(20, 4))
    yoy_change_percent = Column(Numeric(10, 2))

    # Dimensions and metadata
    dimensions = Column(JSONB, default={})
    metadata = Column(JSONB, default={})

    # Relationships
    organization = relationship("Organization", back_populates="aggregated_metrics")

    # Unique constraint to prevent duplicates
    __table_args__ = (
        UniqueConstraint(
            "organization_id", "metric_type", "period", "period_start", "dimensions",
            name="uq_aggregated_metrics"
        ),
        Index("idx_aggregated_metrics_lookup", "organization_id", "metric_type", "period", "period_start"),
    )

class ReportConfiguration(TenantModel):
    """
    Custom report configurations for organizations
    Defines saved reports, dashboards, and scheduled deliveries
    """
    __tablename__ = "report_configurations"

    name = Column(String(255), nullable=False)
    description = Column(Text)
    report_type = Column(String(50), nullable=False)  # "dashboard", "report", "export"

    # Report definition
    metrics = Column(JSONB, nullable=False)  # List of metrics to include
    filters = Column(JSONB, default={})  # Filter conditions
    groupings = Column(ARRAY(String), default=[])  # Dimensions to group by
    time_range = Column(JSONB)  # e.g., {"type": "relative", "value": "last_30_days"}

    # Visualization settings
    chart_configs = Column(JSONB, default=[])  # Chart type, colors, etc.
    layout = Column(JSONB)  # Dashboard layout configuration

    # Scheduling
    is_scheduled = Column(Boolean, default=False)
    schedule_cron = Column(String(100))  # Cron expression for scheduling
    recipients = Column(ARRAY(String), default=[])  # Email addresses
    delivery_format = Column(String(20))  # "pdf", "excel", "csv", "inline"
    last_generated = Column(DateTime(timezone=True))
    next_run = Column(DateTime(timezone=True))

    # Access control
    is_public = Column(Boolean, default=False)
    shared_with = Column(ARRAY(UUID(as_uuid=True)), default=[])  # User IDs

    # Performance optimization
    is_cached = Column(Boolean, default=True)
    cache_duration = Column(Integer, default=3600)  # Seconds

    # Metadata
    tags = Column(ARRAY(String), default=[])
    metadata = Column(JSONB, default={})

class AlertConfiguration(TenantModel):
    """
    Alert rules and notification settings
    Monitors metrics and triggers notifications based on conditions
    """
    __tablename__ = "alert_configurations"

    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    severity = Column(SQLEnum(AlertSeverity), nullable=False, default=AlertSeverity.WARNING)

    # Alert condition
    metric_type = Column(SQLEnum(MetricType), nullable=False)
    operator = Column(SQLEnum(ComparisonOperator), nullable=False)
    threshold_value = Column(Numeric(20, 4), nullable=False)

    # Additional conditions
    dimensions_filter = Column(JSONB, default={})  # Filter metrics by dimensions
    time_window = Column(Integer, default=3600)  # Seconds to evaluate
    min_occurrences = Column(Integer, default=1)  # Min times condition must be met

    # Notification settings
    notification_channels = Column(ARRAY(String), default=["email"])  # email, slack, webhook
    recipients = Column(JSONB, default={})  # Channel-specific recipients
    notification_template = Column(Text)  # Custom message template

    # Rate limiting
    cooldown_period = Column(Integer, default=3600)  # Seconds between alerts
    max_alerts_per_day = Column(Integer, default=10)

    # Alert history
    last_triggered = Column(DateTime(timezone=True))
    trigger_count = Column(Integer, default=0)
    last_value = Column(Numeric(20, 4))

    # Metadata
    tags = Column(ARRAY(String), default=[])
    metadata = Column(JSONB, default={})

class AlertHistory(BaseModel, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Historical record of triggered alerts
    Tracks alert occurrences for analysis and debugging
    """
    __tablename__ = "alert_history"

    alert_configuration_id = Column(UUID(as_uuid=True), ForeignKey("alert_configurations.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)

    # Alert details
    triggered_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    severity = Column(SQLEnum(AlertSeverity), nullable=False)
    metric_type = Column(SQLEnum(MetricType), nullable=False)
    metric_value = Column(Numeric(20, 4), nullable=False)
    threshold_value = Column(Numeric(20, 4), nullable=False)

    # Notification details
    notifications_sent = Column(JSONB, default={})  # Which channels were notified
    notification_status = Column(String(20))  # "sent", "failed", "suppressed"
    suppression_reason = Column(String(255))  # If alert was suppressed

    # Context
    dimensions = Column(JSONB, default={})
    metadata = Column(JSONB, default={})

    # Resolution tracking
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(UUID(as_uuid=True))
    acknowledged_at = Column(DateTime(timezone=True))
    resolution_notes = Column(Text)

    # Relationships
    alert_configuration = relationship("AlertConfiguration")
    organization = relationship("Organization")

    # Indexes
    __table_args__ = (
        Index("idx_alert_history_org_time", "organization_id", "triggered_at"),
        Index("idx_alert_history_config", "alert_configuration_id"),
    )

class AnalyticsSession(BaseModel, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Track user analytics sessions for usage analytics
    Helps understand how users interact with analytics features
    """
    __tablename__ = "analytics_sessions"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)

    # Session details
    session_start = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    session_end = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)

    # Activity tracking
    reports_viewed = Column(ARRAY(UUID(as_uuid=True)), default=[])
    metrics_accessed = Column(ARRAY(String), default=[])
    exports_created = Column(Integer, default=0)
    filters_applied = Column(JSONB, default={})

    # Performance metrics
    queries_executed = Column(Integer, default=0)
    avg_query_time_ms = Column(Float)
    errors_encountered = Column(Integer, default=0)

    # User behavior
    interaction_count = Column(Integer, default=0)
    deepest_drill_level = Column(Integer, default=0)
    features_used = Column(ARRAY(String), default=[])

    # Metadata
    user_agent = Column(String(500))
    ip_address = Column(String(45))
    metadata = Column(JSONB, default={})

    # Relationships
    user = relationship("User")
    organization = relationship("Organization")

class BusinessGoal(TenantModel):
    """
    Track progress toward business goals
    Links metrics to strategic objectives
    """
    __tablename__ = "business_goals"

    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(50))  # "revenue", "growth", "efficiency", etc.

    # Goal parameters
    metric_type = Column(SQLEnum(MetricType), nullable=False)
    target_value = Column(Numeric(20, 4), nullable=False)
    current_value = Column(Numeric(20, 4))
    baseline_value = Column(Numeric(20, 4))

    # Timeline
    start_date = Column(Date, nullable=False)
    target_date = Column(Date, nullable=False)

    # Progress tracking
    progress_percent = Column(Numeric(5, 2))
    is_on_track = Column(Boolean)
    days_remaining = Column(Integer)
    projected_completion = Column(Date)

    # Status
    status = Column(String(20), default="active")  # active, completed, missed, paused
    completed_at = Column(DateTime(timezone=True))

    # Milestones
    milestones = Column(JSONB, default=[])  # List of intermediate targets
    milestone_progress = Column(JSONB, default={})

    # Related items
    related_deals = Column(ARRAY(UUID(as_uuid=True)), default=[])
    related_campaigns = Column(ARRAY(UUID(as_uuid=True)), default=[])
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Metadata
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    tags = Column(ARRAY(String), default=[])
    metadata = Column(JSONB, default={})

    # Relationships
    owner = relationship("User")