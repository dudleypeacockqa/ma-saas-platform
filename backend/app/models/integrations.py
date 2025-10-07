"""
Multi-Platform Integration Models
Manages all external platform connections, data synchronization, and workflow automation
"""
from sqlalchemy import (
    Column, String, Text, Integer, Boolean, DateTime, Float,
    ForeignKey, JSON, Enum as SQLEnum, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import BaseModel, SoftDeleteMixin


class PlatformCategory(str, enum.Enum):
    """Categories of platform integrations"""
    AUTHENTICATION = "authentication"
    PAYMENT = "payment"
    PODCAST = "podcast"
    SOCIAL_MEDIA = "social_media"
    CRM = "crm"
    EMAIL_MARKETING = "email_marketing"
    ANALYTICS = "analytics"
    FILE_STORAGE = "file_storage"
    COMMUNICATION = "communication"
    DATA_SOURCE = "data_source"


class IntegrationStatus(str, enum.Enum):
    """Health status of integrations"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    CONFIGURING = "configuring"
    TESTING = "testing"
    DISABLED = "disabled"


class PlatformIntegration(BaseModel, SoftDeleteMixin):
    """
    Platform integration configuration and status tracking
    Central registry for all external service connections
    """
    __tablename__ = "platform_integrations"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Platform Identification
    platform_name = Column(String(100), nullable=False, index=True)  # clerk, stripe, buzzsprout, etc
    platform_category = Column(SQLEnum(PlatformCategory), nullable=False, index=True)
    display_name = Column(String(200))
    description = Column(Text)
    logo_url = Column(String(500))

    # Configuration
    is_active = Column(Boolean, default=False, index=True)
    is_configured = Column(Boolean, default=False)
    api_endpoint = Column(String(1000))
    api_version = Column(String(50))

    # Credentials (Encrypted)
    credentials = Column(JSON, comment="Encrypted API keys, tokens, etc")
    oauth_config = Column(JSON, comment="OAuth flow configuration")
    webhook_secret = Column(String(500))

    # Rate Limiting
    rate_limit_per_hour = Column(Integer, default=1000)
    rate_limit_per_day = Column(Integer)
    current_hour_requests = Column(Integer, default=0)
    current_day_requests = Column(Integer, default=0)
    rate_limit_reset_at = Column(DateTime)

    # Synchronization
    last_sync_at = Column(DateTime)
    next_sync_at = Column(DateTime)
    sync_frequency_minutes = Column(Integer, default=60)
    auto_sync_enabled = Column(Boolean, default=True)

    # Health Monitoring
    health_status = Column(SQLEnum(IntegrationStatus), default=IntegrationStatus.CONFIGURING, index=True)
    last_health_check_at = Column(DateTime)
    last_successful_request_at = Column(DateTime)
    last_failed_request_at = Column(DateTime)

    # Error Tracking
    error_count_24h = Column(Integer, default=0)
    error_count_total = Column(Integer, default=0)
    last_error_message = Column(Text)
    last_error_at = Column(DateTime)

    # Performance Metrics
    average_response_time_ms = Column(Float)
    success_rate_percentage = Column(Float)
    uptime_percentage_30d = Column(Float)

    # Quota Management
    api_quota_limit = Column(Integer, comment="API calls allowed per period")
    api_quota_remaining = Column(Integer)
    api_quota_reset_at = Column(DateTime)

    # Configuration Settings
    configuration = Column(JSON, comment="Platform-specific settings")
    feature_flags = Column(JSON, comment="Enabled/disabled features")

    # Metadata
    metadata = Column(JSON)
    tags = Column(ARRAY(String))

    # Relationships
    organization = relationship("Organization")
    events = relationship("IntegrationEvent", back_populates="integration")
    sync_jobs = relationship("DataSyncJob", back_populates="integration")
    health_checks = relationship("IntegrationHealthCheck", back_populates="integration")

    __table_args__ = (
        UniqueConstraint('organization_id', 'platform_name', name='uq_org_platform'),
        Index('ix_integration_health_status', 'health_status', 'is_active'),
    )


class IntegrationEvent(BaseModel):
    """
    Log of all integration events (API calls, webhooks, syncs)
    """
    __tablename__ = "integration_events"

    integration_id = Column(UUID(as_uuid=False), ForeignKey("platform_integrations.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Event Details
    event_type = Column(String(100), nullable=False, index=True)  # webhook, api_call, sync, error, health_check
    event_source = Column(String(200))  # Where the event originated
    event_destination = Column(String(200))  # Target of the event

    # Event Data
    event_data = Column(JSON)
    request_payload = Column(JSON)
    response_payload = Column(JSON)

    # Processing
    status = Column(String(50), nullable=False, default="pending", index=True)  # pending, processing, completed, failed
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # Timing
    triggered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processing_started_at = Column(DateTime)
    processed_at = Column(DateTime)
    execution_time_ms = Column(Integer)

    # Error Handling
    error_message = Column(Text)
    error_stack_trace = Column(Text)
    error_code = Column(String(50))

    # HTTP Details (for API calls)
    http_method = Column(String(10))
    http_status_code = Column(Integer)
    request_headers = Column(JSON)
    response_headers = Column(JSON)

    # Metadata
    metadata = Column(JSON)

    # Relationships
    integration = relationship("PlatformIntegration", back_populates="events")
    organization = relationship("Organization")

    __table_args__ = (
        Index('ix_event_status_time', 'status', 'triggered_at'),
        Index('ix_event_type_integration', 'event_type', 'integration_id'),
    )


class DataSyncJob(BaseModel):
    """
    Data synchronization job tracking
    Manages data flow between platforms and local database
    """
    __tablename__ = "data_sync_jobs"

    integration_id = Column(UUID(as_uuid=False), ForeignKey("platform_integrations.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Sync Configuration
    sync_type = Column(String(50), nullable=False)  # full, incremental, delta
    entity_type = Column(String(100), nullable=False, index=True)  # users, deals, episodes, analytics
    sync_direction = Column(String(20), nullable=False)  # inbound, outbound, bidirectional

    # Sync Results
    records_synced = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    records_created = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_deleted = Column(Integer, default=0)

    # Timing
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)

    # Status
    status = Column(String(50), nullable=False, default="running", index=True)  # running, completed, failed, cancelled
    progress_percentage = Column(Integer, default=0)

    # Error Tracking
    error_log = Column(JSON, comment="Array of error messages")
    failed_records = Column(JSON, comment="Records that failed to sync")

    # Data Snapshot
    data_snapshot = Column(JSON, comment="Sample of synced data for debugging")
    conflict_resolution_log = Column(JSON, comment="How conflicts were resolved")

    # Metadata
    configuration = Column(JSON, comment="Sync-specific settings")
    metadata = Column(JSON)

    # Relationships
    integration = relationship("PlatformIntegration", back_populates="sync_jobs")
    organization = relationship("Organization")

    __table_args__ = (
        Index('ix_sync_status_date', 'status', 'started_at'),
    )


class WorkflowAutomation(BaseModel, SoftDeleteMixin):
    """
    Automated workflow definitions
    Trigger-action sequences across platforms
    """
    __tablename__ = "workflow_automations"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)
    created_by = Column(UUID(as_uuid=False), ForeignKey("users.id"))

    # Workflow Details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # marketing, content, deals, analytics

    # Trigger Configuration
    trigger_type = Column(String(100), nullable=False, index=True)  # webhook, schedule, api_call, manual, event
    trigger_config = Column(JSON, nullable=False, comment="Trigger-specific configuration")
    trigger_conditions = Column(JSON, comment="Conditions that must be met")

    # Actions
    actions = Column(JSON, nullable=False, comment="Array of action steps to execute")
    action_count = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_paused = Column(Boolean, default=False)

    # Execution Tracking
    execution_count = Column(Integer, default=0)
    successful_executions = Column(Integer, default=0)
    failed_executions = Column(Integer, default=0)

    # Timing
    last_executed_at = Column(DateTime)
    next_execution_at = Column(DateTime)
    last_success_at = Column(DateTime)
    last_failure_at = Column(DateTime)

    # Performance
    success_rate = Column(Float)
    average_duration_ms = Column(Integer)
    last_execution_duration_ms = Column(Integer)

    # Error Handling
    error_handling_strategy = Column(String(50), default="retry")  # retry, skip, pause, notify
    max_retries = Column(Integer, default=3)
    retry_delay_seconds = Column(Integer, default=60)

    # Scheduling (for scheduled triggers)
    schedule_cron = Column(String(100), comment="Cron expression for scheduled workflows")
    schedule_timezone = Column(String(50), default="UTC")

    # Metadata
    metadata = Column(JSON)
    tags = Column(ARRAY(String))

    # Relationships
    organization = relationship("Organization")
    executions = relationship("WorkflowExecution", back_populates="workflow")

    __table_args__ = (
        Index('ix_workflow_active_trigger', 'is_active', 'trigger_type'),
    )


class WorkflowExecution(BaseModel):
    """
    Individual workflow execution log
    """
    __tablename__ = "workflow_executions"

    workflow_id = Column(UUID(as_uuid=False), ForeignKey("workflow_automations.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Execution Details
    triggered_by = Column(String(100))  # user, system, webhook, schedule
    trigger_data = Column(JSON, comment="Data that triggered the workflow")

    # Status
    status = Column(String(50), nullable=False, default="running", index=True)
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer)

    # Timing
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    duration_ms = Column(Integer)

    # Results
    action_results = Column(JSON, comment="Results of each action step")
    output_data = Column(JSON, comment="Final output of the workflow")

    # Error Tracking
    error_step = Column(Integer)
    error_message = Column(Text)
    error_details = Column(JSON)

    # Metadata
    metadata = Column(JSON)

    # Relationships
    workflow = relationship("WorkflowAutomation", back_populates="executions")
    organization = relationship("Organization")

    __table_args__ = (
        Index('ix_execution_workflow_time', 'workflow_id', 'started_at'),
    )


class APIGatewayLog(BaseModel):
    """
    Comprehensive logging for all API requests through the gateway
    """
    __tablename__ = "api_gateway_logs"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), index=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), index=True)

    # Request Details
    request_id = Column(String(100), unique=True, nullable=False, index=True)
    request_path = Column(String(500), nullable=False)
    request_method = Column(String(10), nullable=False)
    request_query_params = Column(JSON)
    request_body = Column(JSON)

    # Routing
    target_service = Column(String(100), index=True)  # Which backend service handled this
    target_endpoint = Column(String(500))

    # Response
    status_code = Column(Integer, index=True)
    response_time_ms = Column(Integer, index=True)
    response_body = Column(JSON)

    # Headers
    request_headers = Column(JSON)
    response_headers = Column(JSON)

    # Client Information
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    referer = Column(String(500))

    # Error Details
    error_message = Column(Text)
    error_type = Column(String(100))

    # Rate Limiting
    rate_limit_hit = Column(Boolean, default=False)
    rate_limit_remaining = Column(Integer)

    # Metadata
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    organization = relationship("Organization")
    user = relationship("User")

    __table_args__ = (
        Index('ix_gateway_log_time_service', 'created_at', 'target_service'),
        Index('ix_gateway_log_status_time', 'status_code', 'created_at'),
    )


class IntegrationHealthCheck(BaseModel):
    """
    Regular health check results for integrations
    """
    __tablename__ = "integration_health_checks"

    integration_id = Column(UUID(as_uuid=False), ForeignKey("platform_integrations.id"), nullable=False, index=True)

    # Check Details
    check_time = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    check_type = Column(String(50), default="ping")  # ping, api_call, deep_check

    # Results
    is_healthy = Column(Boolean, nullable=False, index=True)
    response_time_ms = Column(Integer)
    status_code = Column(Integer)

    # API Quota
    api_quota_remaining = Column(Integer)
    api_quota_limit = Column(Integer)
    rate_limit_reset_at = Column(DateTime)

    # Error Details
    error_message = Column(Text)
    error_code = Column(String(50))

    # Additional Metrics
    latency_p50 = Column(Integer, comment="50th percentile latency")
    latency_p95 = Column(Integer, comment="95th percentile latency")
    latency_p99 = Column(Integer, comment="99th percentile latency")

    # Metadata
    check_details = Column(JSON)

    # Relationships
    integration = relationship("PlatformIntegration", back_populates="health_checks")

    __table_args__ = (
        Index('ix_health_check_time', 'integration_id', 'check_time'),
    )


class WebhookEndpoint(BaseModel, SoftDeleteMixin):
    """
    Registered webhook endpoints from external platforms
    """
    __tablename__ = "webhook_endpoints"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)
    integration_id = Column(UUID(as_uuid=False), ForeignKey("platform_integrations.id"), index=True)

    # Endpoint Details
    platform_name = Column(String(100), nullable=False, index=True)
    endpoint_url = Column(String(1000), nullable=False, unique=True)
    event_types = Column(ARRAY(String), comment="Webhook event types to listen for")

    # Security
    secret_key = Column(String(500))
    signature_header = Column(String(100))  # e.g., "X-Stripe-Signature"
    verification_method = Column(String(50))  # hmac_sha256, basic_auth, etc

    # Status
    is_active = Column(Boolean, default=True, index=True)
    last_webhook_at = Column(DateTime)
    total_webhooks_received = Column(Integer, default=0)
    successful_webhooks = Column(Integer, default=0)
    failed_webhooks = Column(Integer, default=0)

    # Metadata
    metadata = Column(JSON)

    # Relationships
    organization = relationship("Organization")
    integration = relationship("PlatformIntegration")

    def __repr__(self):
        return f"<WebhookEndpoint {self.platform_name}>"
