from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Enum as SQLEnum, Integer, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import BaseModel, SoftDeleteMixin


class IntegrationApproach(str, enum.Enum):
    ABSORPTION = "absorption"  # Full integration into acquiring company
    PRESERVATION = "preservation"  # Keep target company independent
    SYMBIOSIS = "symbiosis"  # Best of both organizations
    TRANSFORMATION = "transformation"  # Create new combined entity


class IntegrationStatus(str, enum.Enum):
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    DELAYED = "delayed"


class MilestoneType(str, enum.Enum):
    PRE_CLOSING = "pre_closing"
    DAY_1 = "day_1"
    DAY_30 = "day_30"
    DAY_100 = "day_100"
    YEAR_1 = "year_1"
    YEAR_2 = "year_2"


class MilestoneStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    AT_RISK = "at_risk"
    DELAYED = "delayed"


class SynergyType(str, enum.Enum):
    REVENUE = "revenue"
    COST = "cost"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    STRATEGIC = "strategic"


class SynergyStatus(str, enum.Enum):
    IDENTIFIED = "identified"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    REALIZED = "realized"
    AT_RISK = "at_risk"
    NOT_ACHIEVED = "not_achieved"


class WorkstreamType(str, enum.Enum):
    IT_SYSTEMS = "it_systems"
    HR_ORGANIZATION = "hr_organization"
    FINANCE_ACCOUNTING = "finance_accounting"
    OPERATIONS = "operations"
    SALES_MARKETING = "sales_marketing"
    LEGAL_COMPLIANCE = "legal_compliance"
    CUSTOMER_INTEGRATION = "customer_integration"
    SUPPLIER_INTEGRATION = "supplier_integration"
    FACILITIES = "facilities"
    COMMUNICATIONS = "communications"


class TaskPriority(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ChangeType(str, enum.Enum):
    ORGANIZATIONAL = "organizational"
    PROCESS = "process"
    TECHNOLOGY = "technology"
    CULTURAL = "cultural"
    LEADERSHIP = "leadership"


class RiskLevel(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskStatus(str, enum.Enum):
    IDENTIFIED = "identified"
    ASSESSED = "assessed"
    MITIGATING = "mitigating"
    MONITORING = "monitoring"
    CLOSED = "closed"


class DocumentType(str, enum.Enum):
    PLAYBOOK = "playbook"
    COMMUNICATION = "communication"
    TRAINING = "training"
    POLICY = "policy"
    PROCEDURE = "procedure"
    TEMPLATE = "template"
    REPORT = "report"


class IntegrationProject(BaseModel, SoftDeleteMixin):
    """Master integration project tracking for post-acquisition integration"""
    __tablename__ = "integration_projects"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)
    deal_id = Column(UUID(as_uuid=False), ForeignKey("deals.id"), nullable=False, unique=True, index=True)

    # Project metadata
    project_name = Column(String(300), nullable=False)
    project_code = Column(String(50), unique=True, index=True)
    integration_approach = Column(SQLEnum(IntegrationApproach), nullable=False)
    status = Column(SQLEnum(IntegrationStatus), default=IntegrationStatus.PLANNING, index=True)

    # Timeline
    start_date = Column(DateTime, nullable=False)
    target_completion_date = Column(DateTime, nullable=False)
    actual_completion_date = Column(DateTime)

    # Leadership
    integration_lead_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    steering_committee = Column(JSON)  # List of {user_id, name, role}

    # Targets and metrics
    target_synergies = Column(Numeric(20, 2))  # Total target synergy value
    realized_synergies = Column(Numeric(20, 2), default=0)  # Actual realized synergies
    integration_budget = Column(Numeric(20, 2))
    actual_integration_cost = Column(Numeric(20, 2), default=0)

    # Progress tracking
    overall_progress_percent = Column(Integer, default=0)
    milestones_completed = Column(Integer, default=0)
    milestones_total = Column(Integer, default=0)

    # Risk and status
    overall_health_score = Column(Integer)  # 0-100 score
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.MEDIUM)

    # Notes and learnings
    executive_summary = Column(Text)
    key_challenges = Column(JSON)  # List of challenges encountered
    lessons_learned = Column(JSON)  # List of lessons
    success_factors = Column(JSON)  # List of success factors

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    deal = relationship("Deal")
    integration_lead = relationship("User", foreign_keys=[integration_lead_user_id])
    milestones = relationship("IntegrationMilestone", back_populates="project", cascade="all, delete-orphan")
    synergies = relationship("SynergyOpportunity", back_populates="project", cascade="all, delete-orphan")
    workstreams = relationship("IntegrationWorkstream", back_populates="project", cascade="all, delete-orphan")
    risks = relationship("IntegrationRisk", back_populates="project", cascade="all, delete-orphan")


class IntegrationMilestone(BaseModel, SoftDeleteMixin):
    """Key milestones in the integration timeline (Day 1, Day 30, Day 100, etc.)"""
    __tablename__ = "integration_milestones"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=False), ForeignKey("integration_projects.id"), nullable=False, index=True)

    # Milestone details
    milestone_name = Column(String(200), nullable=False)
    milestone_type = Column(SQLEnum(MilestoneType), nullable=False, index=True)
    description = Column(Text)

    # Timeline
    target_date = Column(DateTime, nullable=False)
    actual_date = Column(DateTime)

    # Status
    status = Column(SQLEnum(MilestoneStatus), default=MilestoneStatus.NOT_STARTED, index=True)
    completion_percent = Column(Integer, default=0)

    # Deliverables and success criteria
    key_deliverables = Column(JSON)  # List of deliverable items
    success_criteria = Column(JSON)  # List of criteria to meet
    deliverables_completed = Column(JSON)  # List of completed deliverables with dates

    # Ownership
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    stakeholders = Column(JSON)  # List of {user_id, name, role}

    # Notes
    notes = Column(Text)
    issues = Column(JSON)  # List of issues encountered

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    project = relationship("IntegrationProject", back_populates="milestones")
    owner = relationship("User", foreign_keys=[owner_user_id])


class SynergyOpportunity(BaseModel, SoftDeleteMixin):
    """Synergy opportunities and realization tracking"""
    __tablename__ = "synergy_opportunities"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=False), ForeignKey("integration_projects.id"), nullable=False, index=True)

    # Synergy details
    synergy_name = Column(String(300), nullable=False)
    synergy_type = Column(SQLEnum(SynergyType), nullable=False, index=True)
    description = Column(Text)

    # Financial impact
    target_value = Column(Numeric(20, 2), nullable=False)  # Expected synergy value
    realized_value = Column(Numeric(20, 2), default=0)  # Actual realized value
    currency = Column(String(3), default="USD")

    # Timeline
    target_realization_date = Column(DateTime, nullable=False)
    actual_realization_date = Column(DateTime)
    realization_period_months = Column(Integer)  # Time to fully realize

    # Status
    status = Column(SQLEnum(SynergyStatus), default=SynergyStatus.IDENTIFIED, index=True)
    confidence_level = Column(Integer)  # 0-100 confidence in realization

    # Implementation
    implementation_plan = Column(Text)
    dependencies = Column(JSON)  # List of dependencies
    initiatives = Column(JSON)  # Related change initiatives

    # Ownership
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    responsible_team = Column(String(200))

    # Tracking
    monthly_tracking = Column(JSON)  # {month: value_realized} for trend tracking
    risk_factors = Column(JSON)  # Risks to realization

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    project = relationship("IntegrationProject", back_populates="synergies")
    owner = relationship("User", foreign_keys=[owner_user_id])


class IntegrationWorkstream(BaseModel, SoftDeleteMixin):
    """Functional workstreams for integration (IT, HR, Finance, Operations, etc.)"""
    __tablename__ = "integration_workstreams"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=False), ForeignKey("integration_projects.id"), nullable=False, index=True)

    # Workstream details
    workstream_name = Column(String(200), nullable=False)
    workstream_type = Column(SQLEnum(WorkstreamType), nullable=False, index=True)
    description = Column(Text)

    # Leadership
    lead_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    team_members = Column(JSON)  # List of {user_id, name, role}

    # Status
    status = Column(SQLEnum(IntegrationStatus), default=IntegrationStatus.PLANNING, index=True)
    completion_percent = Column(Integer, default=0)

    # Objectives and deliverables
    objectives = Column(JSON)  # List of workstream objectives
    key_deliverables = Column(JSON)  # List of deliverables

    # Timeline
    start_date = Column(DateTime)
    target_completion_date = Column(DateTime)
    actual_completion_date = Column(DateTime)

    # Budget
    budget_allocated = Column(Numeric(15, 2))
    actual_spend = Column(Numeric(15, 2), default=0)

    # Progress tracking
    tasks_total = Column(Integer, default=0)
    tasks_completed = Column(Integer, default=0)

    # RAG status (Red/Amber/Green)
    health_status = Column(String(20))  # "green", "amber", "red"
    status_notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    project = relationship("IntegrationProject", back_populates="workstreams")
    lead = relationship("User", foreign_keys=[lead_user_id])
    tasks = relationship("IntegrationTask", back_populates="workstream", cascade="all, delete-orphan")


class IntegrationTask(BaseModel, SoftDeleteMixin):
    """Individual tasks within integration workstreams"""
    __tablename__ = "integration_tasks"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)
    workstream_id = Column(UUID(as_uuid=False), ForeignKey("integration_workstreams.id"), nullable=False, index=True)

    # Task details
    task_name = Column(String(300), nullable=False)
    description = Column(Text)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM, index=True)

    # Assignment
    assigned_to_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    assigned_team = Column(String(200))

    # Status
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.NOT_STARTED, index=True)
    completion_percent = Column(Integer, default=0)

    # Timeline
    planned_start_date = Column(DateTime)
    planned_end_date = Column(DateTime)
    actual_start_date = Column(DateTime)
    actual_end_date = Column(DateTime)

    # Dependencies
    predecessor_tasks = Column(JSON)  # List of task IDs that must complete first
    blocked_by = Column(String(500))  # Description of blockers

    # Effort tracking
    estimated_hours = Column(Integer)
    actual_hours = Column(Integer)

    # Success criteria
    acceptance_criteria = Column(JSON)  # List of criteria
    deliverables = Column(JSON)  # List of deliverable items

    # Notes
    notes = Column(Text)
    updates = Column(JSON)  # List of {date, update, user_id}

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    workstream = relationship("IntegrationWorkstream", back_populates="tasks")
    assigned_to = relationship("User", foreign_keys=[assigned_to_user_id])


class CulturalAssessment(BaseModel, SoftDeleteMixin):
    """Cultural assessment and integration planning"""
    __tablename__ = "cultural_assessments"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=False), ForeignKey("integration_projects.id"), nullable=False, index=True)

    # Assessment details
    assessment_name = Column(String(200), nullable=False)
    assessment_date = Column(DateTime, nullable=False)
    conducted_by = Column(String(200))  # Consultant or team

    # Culture profiles
    acquiring_company_profile = Column(JSON)  # Cultural attributes
    target_company_profile = Column(JSON)  # Cultural attributes

    # Analysis
    cultural_alignment_score = Column(Integer)  # 0-100 score
    key_differences = Column(JSON)  # List of major differences
    integration_challenges = Column(JSON)  # Anticipated challenges

    # Integration strategy
    recommended_approach = Column(Text)
    retention_strategy = Column(Text)
    communication_strategy = Column(Text)

    # Action items
    quick_wins = Column(JSON)  # Early cultural integration wins
    long_term_initiatives = Column(JSON)  # Long-term cultural work

    # Employee feedback
    employee_sentiment_scores = Column(JSON)  # {category: score}
    key_concerns = Column(JSON)  # Employee concerns
    success_indicators = Column(JSON)  # Indicators of cultural integration

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    project = relationship("IntegrationProject")


class ChangeInitiative(BaseModel, SoftDeleteMixin):
    """Change management initiatives for integration"""
    __tablename__ = "change_initiatives"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=False), ForeignKey("integration_projects.id"), nullable=False, index=True)

    # Initiative details
    initiative_name = Column(String(300), nullable=False)
    change_type = Column(SQLEnum(ChangeType), nullable=False, index=True)
    description = Column(Text)

    # Impact assessment
    impacted_employees_count = Column(Integer)
    impacted_departments = Column(JSON)  # List of departments
    change_magnitude = Column(String(20))  # "low", "medium", "high"

    # Strategy
    communication_plan = Column(Text)
    training_plan = Column(Text)
    support_resources = Column(JSON)  # Available support resources

    # Timeline
    announcement_date = Column(DateTime)
    training_start_date = Column(DateTime)
    go_live_date = Column(DateTime)
    stabilization_date = Column(DateTime)

    # Status
    status = Column(SQLEnum(IntegrationStatus), default=IntegrationStatus.PLANNING)
    readiness_score = Column(Integer)  # 0-100 organizational readiness

    # Stakeholder management
    sponsors = Column(JSON)  # Executive sponsors
    change_champions = Column(JSON)  # Champions in the organization
    resistance_points = Column(JSON)  # Areas of resistance

    # Metrics
    adoption_metrics = Column(JSON)  # Adoption tracking
    feedback_summary = Column(JSON)  # Employee feedback

    # Owner
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    project = relationship("IntegrationProject")
    owner = relationship("User", foreign_keys=[owner_user_id])


class PerformanceMetric(BaseModel, SoftDeleteMixin):
    """KPIs and performance metrics for integration success"""
    __tablename__ = "performance_metrics"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=False), ForeignKey("integration_projects.id"), nullable=False, index=True)

    # Metric details
    metric_name = Column(String(200), nullable=False)
    metric_category = Column(String(100), index=True)  # "financial", "operational", "customer", "employee"
    description = Column(Text)

    # Targets
    baseline_value = Column(Numeric(20, 4))
    target_value = Column(Numeric(20, 4), nullable=False)
    current_value = Column(Numeric(20, 4))

    # Units and frequency
    unit_of_measure = Column(String(50))  # "$", "%", "days", "count", etc.
    measurement_frequency = Column(String(50))  # "daily", "weekly", "monthly"

    # Targets by period
    day_30_target = Column(Numeric(20, 4))
    day_100_target = Column(Numeric(20, 4))
    year_1_target = Column(Numeric(20, 4))

    # Status
    is_on_track = Column(Boolean, default=True)
    variance_from_target = Column(Numeric(10, 2))  # Percentage variance

    # Historical tracking
    historical_values = Column(JSON)  # {date: value} time series

    # Ownership
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_measured_at = Column(DateTime)

    # Relationships
    organization = relationship("Organization")
    project = relationship("IntegrationProject")
    owner = relationship("User", foreign_keys=[owner_user_id])


class IntegrationRisk(BaseModel, SoftDeleteMixin):
    """Risk identification and mitigation for integration"""
    __tablename__ = "integration_risks"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=False), ForeignKey("integration_projects.id"), nullable=False, index=True)

    # Risk details
    risk_name = Column(String(300), nullable=False)
    description = Column(Text)
    category = Column(String(100), index=True)  # "financial", "operational", "people", "technology", etc.

    # Assessment
    probability = Column(String(20))  # "very_low", "low", "medium", "high", "very_high"
    impact = Column(String(20))  # "very_low", "low", "medium", "high", "very_high"
    risk_level = Column(SQLEnum(RiskLevel), nullable=False, index=True)
    risk_score = Column(Integer)  # Calculated from probability x impact

    # Impact details
    potential_impact = Column(Text)
    financial_impact = Column(Numeric(20, 2))  # Estimated cost if occurs

    # Mitigation
    mitigation_strategy = Column(Text)
    contingency_plan = Column(Text)
    mitigation_actions = Column(JSON)  # List of specific actions

    # Status
    status = Column(SQLEnum(RiskStatus), default=RiskStatus.IDENTIFIED, index=True)
    is_active = Column(Boolean, default=True)

    # Ownership
    owner_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))

    # Monitoring
    trigger_events = Column(JSON)  # Events that would trigger this risk
    monitoring_frequency = Column(String(50))  # How often to review
    last_reviewed_date = Column(DateTime)
    next_review_date = Column(DateTime)

    # Resolution
    closed_date = Column(DateTime)
    resolution_notes = Column(Text)

    # Notes
    notes = Column(Text)
    updates = Column(JSON)  # List of {date, update, user_id}

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    project = relationship("IntegrationProject", back_populates="risks")
    owner = relationship("User", foreign_keys=[owner_user_id])


class IntegrationDocument(BaseModel, SoftDeleteMixin):
    """Integration playbooks, communications, and knowledge base"""
    __tablename__ = "integration_documents"

    organization_id = Column(UUID(as_uuid=False), ForeignKey("organizations.id"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=False), ForeignKey("integration_projects.id"), nullable=False, index=True)

    # Document details
    document_name = Column(String(300), nullable=False)
    document_type = Column(SQLEnum(DocumentType), nullable=False, index=True)
    description = Column(Text)

    # Content
    content = Column(Text)  # Document content or summary
    file_url = Column(String(1000))  # Link to actual file in storage
    file_size_bytes = Column(Integer)
    file_format = Column(String(50))  # "pdf", "docx", "xlsx", etc.

    # Versioning
    version = Column(String(20), default="1.0")
    is_latest_version = Column(Boolean, default=True)
    supersedes_document_id = Column(UUID(as_uuid=False))  # Previous version

    # Classification
    tags = Column(JSON)  # List of tags for categorization
    workstream_type = Column(SQLEnum(WorkstreamType))  # Related workstream

    # Access control
    is_confidential = Column(Boolean, default=False)
    access_level = Column(String(50))  # "public", "team", "leadership", "restricted"

    # Metadata
    author_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    approved_by_user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    approval_date = Column(DateTime)

    # Usage tracking
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime)

    # Notes
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)

    # Relationships
    organization = relationship("Organization")
    project = relationship("IntegrationProject")
    author = relationship("User", foreign_keys=[author_user_id])
    approved_by = relationship("User", foreign_keys=[approved_by_user_id])
