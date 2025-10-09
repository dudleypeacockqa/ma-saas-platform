"""
Post-Acquisition Integration Planning Models
Manages the critical 100-day integration process and 24-month value creation timeline
"""
from sqlalchemy import (
    Column, String, Text, Integer, Boolean, DateTime, Float, Date,
    ForeignKey, JSON, Enum as SQLEnum, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import BaseModel, SoftDeleteMixin


class IntegrationApproach(str, enum.Enum):
    """Integration strategy approaches"""
    ABSORPTION = "absorption"  # Fully absorb target into acquirer
    PRESERVATION = "preservation"  # Keep target independent
    SYMBIOSIS = "symbiosis"  # Blend both organizations
    BEST_OF_BREED = "best_of_breed"  # Take best from each


class SynergyType(str, enum.Enum):
    """Types of synergies to capture"""
    REVENUE = "revenue"
    COST = "cost"
    OPERATIONAL = "operational"
    TECHNOLOGY = "technology"
    MARKET = "market"


class IntegrationPhase(str, enum.Enum):
    """Key integration timeline phases"""
    PRE_CLOSING = "pre_closing"
    DAY_1 = "day_1"
    DAY_30 = "day_30"
    DAY_100 = "day_100"
    MONTH_6 = "month_6"
    MONTH_12 = "month_12"
    MONTH_24 = "month_24"


class WorkstreamType(str, enum.Enum):
    """Functional integration workstreams"""
    OPERATIONS = "operations"
    FINANCE = "finance"
    HR = "hr"
    IT = "it"
    SALES = "sales"
    MARKETING = "marketing"
    LEGAL = "legal"
    FACILITIES = "facilities"


class TaskStatus(str, enum.Enum):
    """Task completion status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    AT_RISK = "at_risk"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RiskSeverity(str, enum.Enum):
    """Risk severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssuePriority(str, enum.Enum):
    """Issue priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class CommunicationStatus(str, enum.Enum):
    """Stakeholder communication status"""
    PLANNED = "planned"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    FEEDBACK_RECEIVED = "feedback_received"


class IntegrationPlan(BaseModel, SoftDeleteMixin):
    """
    Master integration plan for post-acquisition integration
    Links to closed deals and manages entire integration lifecycle
    """
    __tablename__ = "integration_plans"

    deal_id = Column(UUID(as_uuid=False), ForeignKey("deals.id"), nullable=False, unique=True, index=True)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Plan Details
    plan_name = Column(String(255), nullable=False)
    description = Column(Text)
    integration_approach = Column(SQLEnum(IntegrationApproach), nullable=False, index=True)

    # Timeline
    start_date = Column(Date, nullable=False)
    target_completion_date = Column(Date, nullable=False)
    actual_completion_date = Column(Date)

    # Team
    integration_lead_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    executive_sponsor_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    core_team_member_ids = Column(ARRAY(String), comment="Array of user IDs")

    # Budget
    total_budget = Column(Float)
    budget_spent = Column(Float, default=0.0)
    budget_remaining = Column(Float)

    # Progress Tracking
    overall_progress_percentage = Column(Integer, default=0, index=True)
    milestones_completed = Column(Integer, default=0)
    milestones_total = Column(Integer, default=0)
    tasks_completed = Column(Integer, default=0)
    tasks_total = Column(Integer, default=0)

    # Status
    current_phase = Column(SQLEnum(IntegrationPhase), default=IntegrationPhase.PRE_CLOSING, index=True)
    is_on_track = Column(Boolean, default=True, index=True)
    health_status = Column(String(50), default="green")  # green, yellow, red

    # Synergy Targets
    total_synergy_target = Column(Float, comment="Total expected synergy value")
    synergy_realized = Column(Float, default=0.0)
    synergy_capture_rate = Column(Float, comment="Percentage of synergies realized")

    # Key Dates
    day_1_date = Column(Date)
    day_30_date = Column(Date)
    day_100_date = Column(Date)

    # Cultural Integration
    cultural_compatibility_score = Column(Integer, comment="Score 1-100")
    employee_retention_target = Column(Float, comment="Target retention percentage")
    employee_retention_actual = Column(Float)

    # Metadata
    meta_data = Column(JSON)
    tags = Column(ARRAY(String))

    # Relationships
    deal = relationship("Deal")
    organization = relationship("Organization")
    integration_lead = relationship("User", foreign_keys=[integration_lead_id])
    executive_sponsor = relationship("User", foreign_keys=[executive_sponsor_id])
    milestones = relationship("IntegrationMilestone", back_populates="plan")
    synergies = relationship("SynergyOpportunity", back_populates="plan")
    workstreams = relationship("IntegrationWorkstream", back_populates="plan")
    risks = relationship("IntegrationRisk", back_populates="plan")
    kpis = relationship("IntegrationKPI", back_populates="plan")
    issues = relationship("IntegrationIssue", back_populates="plan")
    cultural_assessments = relationship("CulturalAssessment", back_populates="plan")
    change_initiatives = relationship("ChangeInitiative", back_populates="plan")
    stakeholder_engagements = relationship("StakeholderEngagement", back_populates="plan")

    __table_args__ = (
        Index('ix_integration_plan_status', 'is_on_track', 'current_phase'),
    )


class IntegrationMilestone(BaseModel):
    """
    Key milestones in integration timeline
    Day 1, Day 30, Day 100, and longer-term milestones
    """
    __tablename__ = "integration_milestones"

    plan_id = Column(UUID(as_uuid=False), ForeignKey("integration_plans.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Milestone Details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    phase = Column(SQLEnum(IntegrationPhase), nullable=False, index=True)

    # Timeline
    target_date = Column(Date, nullable=False, index=True)
    actual_completion_date = Column(Date)

    # Status
    is_completed = Column(Boolean, default=False, index=True)
    completion_percentage = Column(Integer, default=0)

    # Dependencies
    depends_on_milestone_ids = Column(ARRAY(String), comment="Array of milestone IDs")
    blocking_milestone_ids = Column(ARRAY(String), comment="Milestones blocked by this one")

    # Deliverables
    deliverables = Column(JSON, comment="List of expected deliverables")
    deliverables_completed = Column(Integer, default=0)
    deliverables_total = Column(Integer, default=0)

    # Success Criteria
    success_criteria = Column(JSON, comment="Criteria for milestone completion")
    success_criteria_met = Column(Boolean, default=False)

    # Metadata
    meta_data = Column(JSON)

    # Relationships
    plan = relationship("IntegrationPlan", back_populates="milestones")
    organization = relationship("Organization")
    tasks = relationship("IntegrationTask", back_populates="milestone")

    __table_args__ = (
        Index('ix_milestone_phase_status', 'phase', 'is_completed'),
    )


class SynergyOpportunity(BaseModel, SoftDeleteMixin):
    """
    Identified synergy opportunities and their tracking
    Revenue, cost, operational, technology, and market synergies
    """
    __tablename__ = "synergy_opportunities"

    plan_id = Column(UUID(as_uuid=False), ForeignKey("integration_plans.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Synergy Details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    synergy_type = Column(SQLEnum(SynergyType), nullable=False, index=True)
    category = Column(String(100), index=True)  # e.g., "headcount reduction", "revenue cross-sell"

    # Financial Impact
    target_value = Column(Float, nullable=False, comment="Expected synergy value")
    probability_percentage = Column(Integer, default=100, comment="Probability of realization")
    probability_weighted_value = Column(Float, comment="Target * probability")

    # Timeline
    realization_start_date = Column(Date)
    full_run_rate_date = Column(Date, comment="Date when full synergy is realized")

    # Tracking
    identified_date = Column(Date, default=datetime.utcnow)
    owner_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    status = Column(String(50), default="identified", index=True)  # identified, approved, in_progress, realized, cancelled

    # Implementation Plan
    implementation_steps = Column(JSON, comment="Steps to realize synergy")
    required_investment = Column(Float, comment="Upfront cost to realize synergy")
    payback_period_months = Column(Integer)

    # Dependencies
    depends_on_synergies = Column(ARRAY(String), comment="Synergy IDs this depends on")
    workstream_id = Column(UUID(as_uuid=False), ForeignKey("integration_workstreams.id"))

    # Metadata
    meta_data = Column(JSON)
    tags = Column(ARRAY(String))

    # Relationships
    plan = relationship("IntegrationPlan", back_populates="synergies")
    organization = relationship("Organization")
    owner = relationship("User")
    workstream = relationship("IntegrationWorkstream")
    realizations = relationship("SynergyRealization", back_populates="synergy")

    __table_args__ = (
        Index('ix_synergy_type_status', 'synergy_type', 'status'),
    )


class IntegrationWorkstream(BaseModel, SoftDeleteMixin):
    """
    Functional workstreams for integration
    Operations, Finance, HR, IT, Sales, Marketing, Legal, Facilities
    """
    __tablename__ = "integration_workstreams"

    plan_id = Column(UUID(as_uuid=False), ForeignKey("integration_plans.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Workstream Details
    name = Column(String(255), nullable=False)
    workstream_type = Column(SQLEnum(WorkstreamType), nullable=False, index=True)
    description = Column(Text)

    # Team
    workstream_lead_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    team_member_ids = Column(ARRAY(String), comment="Array of user IDs")

    # Progress
    progress_percentage = Column(Integer, default=0, index=True)
    status = Column(String(50), default="active", index=True)  # active, on_hold, completed
    health_status = Column(String(50), default="green")  # green, yellow, red

    # Timeline
    start_date = Column(Date)
    target_completion_date = Column(Date)
    actual_completion_date = Column(Date)

    # Budget
    allocated_budget = Column(Float)
    spent_budget = Column(Float, default=0.0)

    # Metrics
    tasks_completed = Column(Integer, default=0)
    tasks_total = Column(Integer, default=0)
    risks_count = Column(Integer, default=0)
    issues_count = Column(Integer, default=0)

    # Key Objectives
    objectives = Column(JSON, comment="Workstream objectives and success criteria")

    # Metadata
    meta_data = Column(JSON)

    # Relationships
    plan = relationship("IntegrationPlan", back_populates="workstreams")
    organization = relationship("Organization")
    workstream_lead = relationship("User")
    tasks = relationship("IntegrationTask", back_populates="workstream")

    __table_args__ = (
        Index('ix_workstream_type_status', 'workstream_type', 'status'),
    )


class IntegrationTask(BaseModel, SoftDeleteMixin):
    """
    Detailed integration tasks and action items
    Granular tracking with dependencies and assignments
    """
    __tablename__ = "integration_tasks"

    plan_id = Column(UUID(as_uuid=False), ForeignKey("integration_plans.id"), nullable=False, index=True)
    milestone_id = Column(UUID(as_uuid=False), ForeignKey("integration_milestones.id"), index=True)
    workstream_id = Column(UUID(as_uuid=False), ForeignKey("integration_workstreams.id"), index=True)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Task Details
    title = Column(String(500), nullable=False)
    description = Column(Text)
    priority = Column(SQLEnum(IssuePriority), default=IssuePriority.MEDIUM, index=True)

    # Assignment
    assigned_to_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    assigned_by_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))

    # Timeline
    due_date = Column(Date, index=True)
    completed_date = Column(Date)
    estimated_hours = Column(Float)
    actual_hours = Column(Float)

    # Status
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.NOT_STARTED, nullable=False, index=True)
    completion_percentage = Column(Integer, default=0)

    # Dependencies
    depends_on_task_ids = Column(ARRAY(String), comment="Task IDs this depends on")
    blocking_task_ids = Column(ARRAY(String), comment="Tasks blocked by this one")

    # Integration
    is_critical_path = Column(Boolean, default=False, index=True)
    is_day_1_critical = Column(Boolean, default=False)

    # Notes and Attachments
    notes = Column(Text)
    attachments = Column(JSON, comment="File attachments")

    # Metadata
    meta_data = Column(JSON)
    tags = Column(ARRAY(String))

    # Relationships
    plan = relationship("IntegrationPlan")
    milestone = relationship("IntegrationMilestone", back_populates="tasks")
    workstream = relationship("IntegrationWorkstream", back_populates="tasks")
    organization = relationship("Organization")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    assigned_by = relationship("User", foreign_keys=[assigned_by_id])

    __table_args__ = (
        Index('ix_task_status_due_date', 'status', 'due_date'),
        Index('ix_task_critical_path', 'is_critical_path', 'status'),
    )


class SynergyRealization(BaseModel):
    """
    Actual synergy realization tracking
    Compares actuals vs. targets on periodic basis
    """
    __tablename__ = "synergy_realizations"

    synergy_id = Column(UUID(as_uuid=False), ForeignKey("synergy_opportunities.id"), nullable=False, index=True)
    plan_id = Column(UUID(as_uuid=False), ForeignKey("integration_plans.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Period
    reporting_period = Column(String(20), nullable=False, index=True)  # "2024-Q1", "2024-06", etc.
    period_start_date = Column(Date, nullable=False)
    period_end_date = Column(Date, nullable=False)

    # Financial Impact
    target_value = Column(Float, nullable=False, comment="Expected value for this period")
    actual_value = Column(Float, comment="Actual realized value")
    variance = Column(Float, comment="Actual - Target")
    variance_percentage = Column(Float)

    # Run Rate
    run_rate_value = Column(Float, comment="Annualized run-rate impact")
    cumulative_value = Column(Float, comment="Total value realized to date")

    # Status
    realization_status = Column(String(50), default="on_track", index=True)  # on_track, at_risk, off_track, exceeded

    # Evidence and Notes
    evidence_description = Column(Text, comment="How synergy was measured/verified")
    supporting_data = Column(JSON, comment="Supporting metrics and calculations")
    notes = Column(Text)

    # Reporting
    reported_by_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    reported_date = Column(DateTime, default=datetime.utcnow)
    verified = Column(Boolean, default=False)
    verified_by_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    verified_date = Column(DateTime)

    # Metadata
    meta_data = Column(JSON)

    # Relationships
    synergy = relationship("SynergyOpportunity", back_populates="realizations")
    plan = relationship("IntegrationPlan")
    organization = relationship("Organization")
    reported_by = relationship("User", foreign_keys=[reported_by_id])
    verified_by = relationship("User", foreign_keys=[verified_by_id])

    __table_args__ = (
        Index('ix_realization_period', 'reporting_period', 'synergy_id'),
        UniqueConstraint('synergy_id', 'reporting_period', name='uq_synergy_period'),
    )


class CulturalAssessment(BaseModel):
    """
    Cultural compatibility and integration assessment
    Tracks cultural fit and change management needs
    """
    __tablename__ = "cultural_assessments"

    plan_id = Column(UUID(as_uuid=False), ForeignKey("integration_plans.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Assessment Details
    assessment_name = Column(String(255), nullable=False)
    assessment_date = Column(Date, nullable=False)
    conducted_by_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))

    # Cultural Dimensions
    leadership_style_score = Column(Integer, comment="Score 1-100")
    decision_making_score = Column(Integer)
    communication_style_score = Column(Integer)
    work_life_balance_score = Column(Integer)
    innovation_score = Column(Integer)
    risk_tolerance_score = Column(Integer)
    collaboration_score = Column(Integer)
    hierarchy_score = Column(Integer)

    # Overall Compatibility
    overall_compatibility_score = Column(Integer, comment="Composite score 1-100")
    compatibility_level = Column(String(50))  # high, medium, low

    # Cultural Gaps
    identified_gaps = Column(JSON, comment="List of cultural gaps and conflicts")
    gap_severity = Column(String(50))  # low, medium, high, critical

    # Recommendations
    integration_recommendations = Column(JSON, comment="Recommended integration approaches")
    change_initiatives_needed = Column(JSON, comment="Required change management initiatives")

    # Employee Sentiment
    acquirer_sentiment_score = Column(Integer, comment="Acquirer employee sentiment 1-100")
    target_sentiment_score = Column(Integer, comment="Target employee sentiment 1-100")

    # Survey Data
    survey_responses = Column(Integer, comment="Number of survey responses")
    survey_response_rate = Column(Float, comment="Percentage of employees who responded")

    # Key Findings
    key_strengths = Column(JSON, comment="Cultural strengths to preserve")
    key_risks = Column(JSON, comment="Cultural risks to address")

    # Metadata
    meta_data = Column(JSON)

    # Relationships
    plan = relationship("IntegrationPlan", back_populates="cultural_assessments")
    organization = relationship("Organization")
    conducted_by = relationship("User")

    __table_args__ = (
        Index('ix_cultural_assessment_date', 'plan_id', 'assessment_date'),
    )


class ChangeInitiative(BaseModel, SoftDeleteMixin):
    """
    Change management initiatives and programs
    Manages organizational change during integration
    """
    __tablename__ = "change_initiatives"

    plan_id = Column(UUID(as_uuid=False), ForeignKey("integration_plans.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Initiative Details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    initiative_type = Column(String(100), index=True)  # communication, training, culture, process, technology

    # Scope
    target_audience = Column(String(200))  # "all_employees", "target_only", "acquirer_only", "leadership"
    impacted_employee_count = Column(Integer)

    # Timeline
    start_date = Column(Date)
    end_date = Column(Date)

    # Status
    status = Column(String(50), default="planned", index=True)  # planned, in_progress, completed, cancelled
    progress_percentage = Column(Integer, default=0)

    # Leadership
    initiative_lead_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    executive_sponsor_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))

    # Activities
    planned_activities = Column(JSON, comment="List of planned activities")
    completed_activities = Column(Integer, default=0)
    total_activities = Column(Integer, default=0)

    # Communication Plan
    communication_channels = Column(ARRAY(String), comment="email, town_hall, intranet, etc.")
    communication_frequency = Column(String(50))  # daily, weekly, biweekly, monthly

    # Training
    training_modules = Column(JSON, comment="Training programs and materials")
    employees_trained = Column(Integer, default=0)
    training_completion_rate = Column(Float)

    # Effectiveness Metrics
    adoption_rate = Column(Float, comment="Percentage adoption")
    satisfaction_score = Column(Integer, comment="Employee satisfaction 1-100")
    feedback_summary = Column(Text)

    # Budget
    allocated_budget = Column(Float)
    spent_budget = Column(Float, default=0.0)

    # Metadata
    meta_data = Column(JSON)

    # Relationships
    plan = relationship("IntegrationPlan", back_populates="change_initiatives")
    organization = relationship("Organization")
    initiative_lead = relationship("User", foreign_keys=[initiative_lead_id])
    executive_sponsor = relationship("User", foreign_keys=[executive_sponsor_id])

    __table_args__ = (
        Index('ix_change_initiative_type_status', 'initiative_type', 'status'),
    )


class IntegrationRisk(BaseModel, SoftDeleteMixin):
    """
    Integration risk tracking and mitigation
    Identifies and monitors risks throughout integration
    """
    __tablename__ = "integration_risks"

    plan_id = Column(UUID(as_uuid=False), ForeignKey("integration_plans.id"), nullable=False, index=True)
    workstream_id = Column(UUID(as_uuid=False), ForeignKey("integration_workstreams.id"), index=True)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Risk Details
    title = Column(String(500), nullable=False)
    description = Column(Text)
    category = Column(String(100), index=True)  # operational, financial, cultural, technology, market

    # Assessment
    severity = Column(SQLEnum(RiskSeverity), nullable=False, index=True)
    probability = Column(Integer, comment="Probability percentage 0-100")
    impact_score = Column(Integer, comment="Impact score 1-10")
    risk_score = Column(Float, comment="Probability * Impact")

    # Status
    status = Column(String(50), default="identified", index=True)  # identified, assessing, mitigating, closed, realized

    # Ownership
    risk_owner_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    identified_by_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    identified_date = Column(Date, default=datetime.utcnow)

    # Mitigation
    mitigation_plan = Column(Text)
    mitigation_actions = Column(JSON, comment="List of mitigation actions")
    mitigation_owner_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    mitigation_deadline = Column(Date)
    mitigation_budget = Column(Float)

    # Contingency
    contingency_plan = Column(Text, comment="Backup plan if risk is realized")

    # Tracking
    last_reviewed_date = Column(Date)
    next_review_date = Column(Date)
    review_frequency_days = Column(Integer, default=7)

    # Resolution
    resolution_date = Column(Date)
    resolution_notes = Column(Text)
    actual_impact = Column(Text, comment="Actual impact if risk was realized")

    # Metadata
    meta_data = Column(JSON)
    tags = Column(ARRAY(String))

    # Relationships
    plan = relationship("IntegrationPlan", back_populates="risks")
    workstream = relationship("IntegrationWorkstream")
    organization = relationship("Organization")
    risk_owner = relationship("User", foreign_keys=[risk_owner_id])
    identified_by = relationship("User", foreign_keys=[identified_by_id])
    mitigation_owner = relationship("User", foreign_keys=[mitigation_owner_id])

    __table_args__ = (
        Index('ix_risk_severity_status', 'severity', 'status'),
    )


class IntegrationKPI(BaseModel):
    """
    Key Performance Indicators for integration success
    Tracks metrics across all dimensions of integration
    """
    __tablename__ = "integration_kpis"

    plan_id = Column(UUID(as_uuid=False), ForeignKey("integration_plans.id"), nullable=False, index=True)
    workstream_id = Column(UUID(as_uuid=False), ForeignKey("integration_workstreams.id"), index=True)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # KPI Details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100), index=True)  # financial, operational, cultural, customer, employee

    # Measurement
    measurement_unit = Column(String(50))  # dollars, percentage, count, days, score
    measurement_frequency = Column(String(50))  # daily, weekly, monthly, quarterly

    # Values
    baseline_value = Column(Float, comment="Starting value")
    target_value = Column(Float, nullable=False, comment="Goal value")
    current_value = Column(Float, comment="Latest measured value")

    # Threshold
    threshold_green = Column(Float, comment="Green status threshold")
    threshold_yellow = Column(Float, comment="Yellow status threshold")
    threshold_red = Column(Float, comment="Red status threshold")

    # Status
    current_status = Column(String(50), default="measuring", index=True)  # measuring, on_track, at_risk, off_track
    health_indicator = Column(String(50), default="green")  # green, yellow, red

    # Ownership
    owner_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))

    # Timeline
    start_date = Column(Date)
    target_date = Column(Date)

    # Trend Analysis
    trend_direction = Column(String(50))  # improving, stable, declining
    variance_from_target = Column(Float, comment="Current - Target")
    variance_percentage = Column(Float)

    # Historical Data
    historical_values = Column(JSON, comment="Time series of measurements")
    last_measured_date = Column(Date)
    next_measurement_date = Column(Date)

    # Metadata
    calculation_method = Column(Text, comment="How this KPI is calculated")
    data_source = Column(String(200))
    meta_data = Column(JSON)

    # Relationships
    plan = relationship("IntegrationPlan", back_populates="kpis")
    workstream = relationship("IntegrationWorkstream")
    organization = relationship("Organization")
    owner = relationship("User")

    __table_args__ = (
        Index('ix_kpi_category_status', 'category', 'current_status'),
    )


class IntegrationIssue(BaseModel, SoftDeleteMixin):
    """
    Issues and blockers requiring resolution
    Tracks problems that arise during integration
    """
    __tablename__ = "integration_issues"

    plan_id = Column(UUID(as_uuid=False), ForeignKey("integration_plans.id"), nullable=False, index=True)
    workstream_id = Column(UUID(as_uuid=False), ForeignKey("integration_workstreams.id"), index=True)
    related_task_id = Column(UUID(as_uuid=False), ForeignKey("integration_tasks.id"), index=True)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Issue Details
    title = Column(String(500), nullable=False)
    description = Column(Text)
    issue_type = Column(String(100), index=True)  # blocker, dependency, resource, technical, communication

    # Priority and Severity
    priority = Column(SQLEnum(IssuePriority), default=IssuePriority.MEDIUM, nullable=False, index=True)
    impact_level = Column(String(50))  # low, medium, high, critical

    # Status
    status = Column(String(50), default="open", index=True)  # open, in_progress, resolved, closed, escalated

    # Assignment
    reported_by_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    assigned_to_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    escalated_to_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))

    # Timeline
    reported_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_date = Column(Date)
    resolved_date = Column(DateTime)

    # Resolution
    resolution_description = Column(Text)
    resolution_approach = Column(String(200))
    lessons_learned = Column(Text)

    # Impact
    impacted_tasks = Column(ARRAY(String), comment="Task IDs impacted by this issue")
    impacted_milestones = Column(ARRAY(String), comment="Milestone IDs impacted")
    delay_days = Column(Integer, comment="Days of delay caused")
    cost_impact = Column(Float, comment="Financial impact")

    # Communication
    escalation_history = Column(JSON, comment="Escalation timeline")
    stakeholder_notifications = Column(JSON, comment="Who was notified")

    # Metadata
    meta_data = Column(JSON)
    tags = Column(ARRAY(String))

    # Relationships
    plan = relationship("IntegrationPlan", back_populates="issues")
    workstream = relationship("IntegrationWorkstream")
    related_task = relationship("IntegrationTask")
    organization = relationship("Organization")
    reported_by = relationship("User", foreign_keys=[reported_by_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    escalated_to = relationship("User", foreign_keys=[escalated_to_id])

    __table_args__ = (
        Index('ix_issue_priority_status', 'priority', 'status'),
    )


class StakeholderEngagement(BaseModel):
    """
    Stakeholder communication and engagement tracking
    Ensures all stakeholders are informed and engaged
    """
    __tablename__ = "stakeholder_engagements"

    plan_id = Column(UUID(as_uuid=False), ForeignKey("integration_plans.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)

    # Stakeholder Details
    stakeholder_name = Column(String(255), nullable=False)
    stakeholder_role = Column(String(100))
    stakeholder_type = Column(String(100), index=True)  # employee, customer, investor, partner, regulator
    organization_affiliation = Column(String(100))  # acquirer, target, external

    # Contact Information
    email = Column(String(255))
    phone = Column(String(50))

    # Engagement Level
    influence_level = Column(String(50))  # high, medium, low
    interest_level = Column(String(50))  # high, medium, low
    sentiment = Column(String(50))  # positive, neutral, negative, unknown

    # Communication
    communication_preference = Column(String(100))  # email, phone, in_person, video
    communication_frequency = Column(String(50))  # daily, weekly, biweekly, monthly, quarterly
    last_communication_date = Column(Date)
    next_scheduled_communication = Column(Date)

    # Engagement Activities
    engagement_activities = Column(JSON, comment="List of engagement touchpoints")
    communications_sent = Column(Integer, default=0)
    meetings_held = Column(Integer, default=0)

    # Status
    engagement_status = Column(SQLEnum(CommunicationStatus), default=CommunicationStatus.PLANNED, index=True)

    # Feedback
    feedback_received = Column(JSON, comment="Stakeholder feedback and concerns")
    concerns = Column(JSON, comment="Identified concerns")
    concerns_resolved = Column(Boolean, default=False)

    # Action Items
    action_items = Column(JSON, comment="Follow-up actions from engagement")

    # Ownership
    relationship_owner_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))

    # Metadata
    meta_data = Column(JSON)
    tags = Column(ARRAY(String))

    # Relationships
    plan = relationship("IntegrationPlan", back_populates="stakeholder_engagements")
    organization = relationship("Organization")
    relationship_owner = relationship("User")

    __table_args__ = (
        Index('ix_stakeholder_type_status', 'stakeholder_type', 'engagement_status'),
    )
