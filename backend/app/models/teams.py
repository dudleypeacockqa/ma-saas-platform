"""
Team and Workflow Management Models for M&A SaaS Platform
Comprehensive models for managing deal teams, workflows, skills, and collaboration
"""

import enum
from datetime import datetime, date, time
from decimal import Decimal
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    Column, String, Text, Integer, Numeric, Date, DateTime, Boolean, Time,
    ForeignKey, Enum, JSON, Index, CheckConstraint, UniqueConstraint, Table
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship, validates

from .base import TenantModel, AuditableMixin, MetadataMixin


class TeamType(enum.Enum):
    """Types of teams"""
    DEAL_TEAM = "deal_team"
    FUNCTIONAL_TEAM = "functional_team"
    PROJECT_TEAM = "project_team"
    ADVISORY_TEAM = "advisory_team"
    EXTERNAL_TEAM = "external_team"


class TeamStatus(enum.Enum):
    """Team lifecycle status"""
    FORMING = "forming"
    ACTIVE = "active"
    PERFORMING = "performing"
    PAUSED = "paused"
    COMPLETED = "completed"
    DISBANDED = "disbanded"


class TeamRole(enum.Enum):
    """Standardized team roles"""
    TEAM_LEAD = "team_lead"
    DEAL_LEAD = "deal_lead"
    PROJECT_MANAGER = "project_manager"
    SENIOR_ANALYST = "senior_analyst"
    ANALYST = "analyst"
    LEGAL_COUNSEL = "legal_counsel"
    FINANCIAL_ADVISOR = "financial_advisor"
    TAX_ADVISOR = "tax_advisor"
    EXTERNAL_ADVISOR = "external_advisor"
    SUBJECT_MATTER_EXPERT = "subject_matter_expert"
    COORDINATOR = "coordinator"
    REVIEWER = "reviewer"
    APPROVER = "approver"
    MEMBER = "member"


class SkillLevel(enum.Enum):
    """Skill proficiency levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"


class TaskStatus(enum.Enum):
    """Task lifecycle status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(enum.Enum):
    """Task priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MeetingType(enum.Enum):
    """Types of meetings"""
    KICKOFF = "kickoff"
    STATUS_UPDATE = "status_update"
    TEAM_STANDUP = "team_standup"
    REVIEW = "review"
    DECISION = "decision"
    BRAINSTORM = "brainstorm"
    TRAINING = "training"
    ONE_ON_ONE = "one_on_one"
    ALL_HANDS = "all_hands"


class MeetingStatus(enum.Enum):
    """Meeting status"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class ChannelType(enum.Enum):
    """Types of team communication channels"""
    GENERAL = "general"
    ANNOUNCEMENTS = "announcements"
    WORK = "work"
    SOCIAL = "social"


class MessageType(enum.Enum):
    """Types of messages in team channels"""
    TEXT = "text"
    FILE = "file"
    IMAGE = "image"
    ANNOUNCEMENT = "announcement"


class PerformanceRating(enum.Enum):
    """Performance rating levels"""
    POOR = "poor"
    BELOW_AVERAGE = "below_average"
    AVERAGE = "average"
    ABOVE_AVERAGE = "above_average"
    EXCELLENT = "excellent"


class Team(TenantModel, AuditableMixin, MetadataMixin):
    """
    Core team model for organizing people around deals, projects, or functions
    """
    __tablename__ = "teams"

    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    team_type = Column(Enum(TeamType), nullable=False, default=TeamType.DEAL_TEAM, index=True)
    status = Column(Enum(TeamStatus), default=TeamStatus.FORMING, index=True)

    # Hierarchy
    parent_team_id = Column(UUID(as_uuid=False), ForeignKey("teams.id"), index=True)
    team_lead_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)

    # Association
    deal_id = Column(UUID(as_uuid=False), ForeignKey("deals.id"), index=True)
    negotiation_id = Column(UUID(as_uuid=False), ForeignKey("negotiations.id"), index=True)

    # Timeline
    start_date = Column(Date, default=date.today)
    target_end_date = Column(Date)
    actual_end_date = Column(Date)

    # Capacity and Budget
    target_team_size = Column(Integer, default=5)
    current_team_size = Column(Integer, default=0)
    budget_allocated = Column(Numeric(20, 2))
    budget_spent = Column(Numeric(20, 2), default=0)

    # Performance Metrics
    completion_percentage = Column(Integer, default=0)
    performance_score = Column(Numeric(5, 2), comment="1-10 performance rating")
    efficiency_rating = Column(Numeric(5, 2), comment="1-10 efficiency rating")

    # Settings
    is_confidential = Column(Boolean, default=True)
    requires_clearance = Column(Boolean, default=False)
    time_zone = Column(String(50), default="UTC")

    # Relationships
    parent_team = relationship("Team", remote_side="Team.id", backref="sub_teams")
    team_lead = relationship("User", foreign_keys=[team_lead_id])
    deal = relationship("Deal", backref="teams")
    negotiation = relationship("Negotiation", backref="teams")
    members = relationship("TeamMember", back_populates="team", lazy="dynamic")
    tasks = relationship("TeamTask", back_populates="team", lazy="dynamic")
    meetings = relationship("TeamMeeting", back_populates="team", lazy="dynamic")
    channels = relationship("TeamChannel", back_populates="team", lazy="dynamic")
    metrics = relationship("TeamMetrics", back_populates="team", lazy="dynamic")

    __table_args__ = (
        CheckConstraint('completion_percentage >= 0 AND completion_percentage <= 100'),
        CheckConstraint('performance_score >= 1 AND performance_score <= 10'),
        CheckConstraint('efficiency_rating >= 1 AND efficiency_rating <= 10'),
        Index('ix_teams_org_type_status', 'organization_id', 'team_type', 'status'),
        Index('ix_teams_deal_id', 'deal_id'),
    )

    @property
    def is_active(self) -> bool:
        """Check if team is currently active"""
        return self.status in [TeamStatus.ACTIVE, TeamStatus.PERFORMING]

    @property
    def days_active(self) -> int:
        """Calculate days team has been active"""
        end_date = self.actual_end_date or date.today()
        return (end_date - self.start_date).days if self.start_date else 0

    @property
    def utilization_rate(self) -> float:
        """Calculate team utilization rate"""
        if self.target_team_size == 0:
            return 0.0
        return (self.current_team_size / self.target_team_size) * 100

    @property
    def budget_utilization(self) -> float:
        """Calculate budget utilization percentage"""
        if not self.budget_allocated or self.budget_allocated == 0:
            return 0.0
        return float((self.budget_spent / self.budget_allocated) * 100)


class TeamMember(TenantModel, AuditableMixin):
    """
    Enhanced team member model with skills, availability, and performance tracking
    """
    __tablename__ = "team_members"

    # Core Relationships
    team_id = Column(UUID(as_uuid=False), ForeignKey("teams.id", ondelete="CASCADE"),
                     nullable=False, index=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)

    # Role and Responsibilities
    role = Column(Enum(TeamRole), nullable=False, index=True)
    custom_role_title = Column(String(200))
    responsibilities = Column(Text)
    decision_authority = Column(JSON, default=list, comment="List of decision areas")

    # Capacity and Allocation
    allocation_percentage = Column(Integer, default=100, comment="Percentage of time allocated")
    hourly_rate = Column(Numeric(10, 2))
    estimated_hours = Column(Integer)
    actual_hours = Column(Integer, default=0)

    # Timeline
    start_date = Column(Date, default=date.today, nullable=False)
    planned_end_date = Column(Date)
    actual_end_date = Column(Date)

    # Status and Performance
    is_active = Column(Boolean, default=True, index=True)
    is_lead = Column(Boolean, default=False)
    performance_rating = Column(Numeric(5, 2), comment="1-10 performance score")
    contribution_score = Column(Numeric(5, 2), comment="1-10 contribution score")

    # Availability
    availability_hours_per_week = Column(Integer, default=40)
    preferred_working_hours = Column(JSON, default=dict, comment="Daily schedule preferences")
    time_zone = Column(String(50))

    # Skills and Expertise
    primary_skills = Column(ARRAY(String(100)), default=list)
    secondary_skills = Column(ARRAY(String(100)), default=list)
    certifications = Column(JSON, default=list)

    # Communication Preferences
    contact_preferences = Column(JSON, default=dict)
    notification_settings = Column(JSON, default=dict)

    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User", backref="team_memberships")
    assigned_tasks = relationship("TeamTask", back_populates="assignee", lazy="dynamic")
    performance_reviews = relationship("PerformanceReview", back_populates="team_member", lazy="dynamic")

    __table_args__ = (
        UniqueConstraint('team_id', 'user_id', name='uq_team_member'),
        CheckConstraint('allocation_percentage >= 0 AND allocation_percentage <= 100'),
        CheckConstraint('performance_rating >= 1 AND performance_rating <= 10'),
        CheckConstraint('contribution_score >= 1 AND contribution_score <= 10'),
        Index('ix_team_members_team_role', 'team_id', 'role'),
        Index('ix_team_members_active', 'is_active'),
    )

    @property
    def is_overallocated(self) -> bool:
        """Check if member is overallocated across teams"""
        # This would need to be calculated across all team memberships
        return self.allocation_percentage > 100

    @property
    def utilization_rate(self) -> float:
        """Calculate utilization rate based on actual vs estimated hours"""
        if not self.estimated_hours or self.estimated_hours == 0:
            return 0.0
        return (self.actual_hours / self.estimated_hours) * 100


class SkillCategory(TenantModel, AuditableMixin):
    """Categories for organizing skills and competencies"""
    __tablename__ = "skill_categories"

    name = Column(String(100), nullable=False)
    description = Column(Text)
    parent_category_id = Column(UUID(as_uuid=False), ForeignKey("skill_categories.id"))
    is_core_competency = Column(Boolean, default=False)
    industry_specific = Column(Boolean, default=False)

    # Relationships
    parent_category = relationship("SkillCategory", remote_side="SkillCategory.id", backref="subcategories")
    skills = relationship("Skill", back_populates="category", lazy="dynamic")

    __table_args__ = (
        Index('ix_skill_categories_name', 'name'),
        Index('ix_skill_categories_core', 'is_core_competency'),
    )


class Skill(TenantModel, AuditableMixin):
    """Individual skills and competencies"""
    __tablename__ = "skills"

    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    category_id = Column(UUID(as_uuid=False), ForeignKey("skill_categories.id"), nullable=False)

    # Skill Properties
    is_technical = Column(Boolean, default=True)
    is_certifiable = Column(Boolean, default=False)
    demand_level = Column(Integer, default=3, comment="1-5 demand rating")
    market_value = Column(Numeric(10, 2), comment="Market rate for this skill")

    # Relationships
    category = relationship("SkillCategory", back_populates="skills")
    user_skills = relationship("UserSkill", back_populates="skill", lazy="dynamic")

    __table_args__ = (
        CheckConstraint('demand_level >= 1 AND demand_level <= 5'),
        Index('ix_skills_category_demand', 'category_id', 'demand_level'),
    )


class UserSkill(TenantModel, AuditableMixin):
    """User skill assessments and certifications"""
    __tablename__ = "user_skills"

    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)
    skill_id = Column(UUID(as_uuid=False), ForeignKey("skills.id"), nullable=False, index=True)

    # Proficiency
    skill_level = Column(Enum(SkillLevel), nullable=False, default=SkillLevel.INTERMEDIATE)
    self_assessment = Column(Enum(SkillLevel))
    manager_assessment = Column(Enum(SkillLevel))
    peer_assessment = Column(Enum(SkillLevel))

    # Evidence
    years_experience = Column(Numeric(4, 1))
    certification_date = Column(Date)
    certification_expiry = Column(Date)
    certification_body = Column(String(200))

    # Validation
    is_verified = Column(Boolean, default=False)
    verified_by_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    verified_date = Column(Date)

    # Usage
    last_used_date = Column(Date)
    proficiency_notes = Column(Text)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="skills")
    skill = relationship("Skill", back_populates="user_skills")
    verified_by = relationship("User", foreign_keys=[verified_by_id])

    __table_args__ = (
        UniqueConstraint('user_id', 'skill_id', name='uq_user_skill'),
        Index('ix_user_skills_level', 'skill_level'),
        Index('ix_user_skills_verified', 'is_verified'),
    )

    @property
    def is_certification_current(self) -> bool:
        """Check if certification is still valid"""
        if not self.certification_expiry:
            return True
        return date.today() <= self.certification_expiry


class ExternalAdvisor(TenantModel, AuditableMixin):
    """External advisors and consultants"""
    __tablename__ = "external_advisors"

    # Contact Information
    name = Column(String(255), nullable=False, index=True)
    title = Column(String(200))
    company = Column(String(255), index=True)
    email = Column(String(255), nullable=False)
    phone = Column(String(50))
    linkedin_url = Column(String(500))

    # Professional Details
    specialization = Column(ARRAY(String(100)), default=list)
    industry_expertise = Column(ARRAY(String(100)), default=list)
    years_experience = Column(Integer)
    previous_deals = Column(Integer, default=0)

    # Engagement
    hourly_rate = Column(Numeric(10, 2))
    preferred_engagement_type = Column(String(50), comment="retainer, hourly, project")
    availability_status = Column(String(50), default="available")
    security_clearance = Column(String(50))

    # Performance
    rating = Column(Numeric(3, 1), comment="1-5 rating")
    total_engagements = Column(Integer, default=0)
    successful_engagements = Column(Integer, default=0)
    referral_source = Column(String(200))

    # Current Relationships
    current_teams = relationship("TeamMember",
                                secondary="advisor_team_assignments",
                                lazy="dynamic")

    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5'),
        Index('ix_external_advisors_company', 'company'),
        Index('ix_external_advisors_specialization', 'specialization'),
    )

    @property
    def success_rate(self) -> float:
        """Calculate engagement success rate"""
        if self.total_engagements == 0:
            return 0.0
        return (self.successful_engagements / self.total_engagements) * 100


class TeamTask(TenantModel, AuditableMixin):
    """Enhanced task management with dependencies and workflows"""
    __tablename__ = "team_tasks"

    # Core Information
    team_id = Column(UUID(as_uuid=False), ForeignKey("teams.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)

    # Assignment
    assignee_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), index=True)
    reviewer_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))

    # Status and Priority
    status = Column(Enum(TaskStatus), default=TaskStatus.NOT_STARTED, index=True)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, index=True)

    # Timeline
    start_date = Column(Date)
    due_date = Column(Date, index=True)
    completed_date = Column(Date)
    estimated_hours = Column(Numeric(6, 2))
    actual_hours = Column(Numeric(6, 2))

    # Dependencies
    depends_on = Column(ARRAY(UUID(as_uuid=False)), default=list,
                       comment="Array of task IDs this task depends on")
    blocks_tasks = Column(ARRAY(UUID(as_uuid=False)), default=list,
                         comment="Array of task IDs blocked by this task")

    # Work Breakdown
    completion_percentage = Column(Integer, default=0)
    deliverables = Column(JSON, default=list)
    acceptance_criteria = Column(Text)

    # Quality and Review
    quality_score = Column(Numeric(3, 1), comment="1-5 quality rating")
    review_notes = Column(Text)
    rework_count = Column(Integer, default=0)

    # External References
    deal_id = Column(UUID(as_uuid=False), ForeignKey("deals.id"), index=True)
    negotiation_id = Column(UUID(as_uuid=False), ForeignKey("negotiations.id"))
    document_id = Column(UUID(as_uuid=False), ForeignKey("documents.id"))

    # Relationships
    team = relationship("Team", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assignee_id], backref="assigned_team_tasks")
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    deal = relationship("Deal", backref="team_tasks")
    subtasks = relationship("TaskSubtask", back_populates="parent_task", lazy="dynamic")
    time_logs = relationship("TaskTimeLog", back_populates="task", lazy="dynamic")

    __table_args__ = (
        CheckConstraint('completion_percentage >= 0 AND completion_percentage <= 100'),
        CheckConstraint('quality_score >= 1 AND quality_score <= 5'),
        Index('ix_team_tasks_team_status', 'team_id', 'status'),
        Index('ix_team_tasks_assignee_due', 'assignee_id', 'due_date'),
        Index('ix_team_tasks_priority_due', 'priority', 'due_date'),
    )

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if not self.due_date or self.status == TaskStatus.COMPLETED:
            return False
        return date.today() > self.due_date

    @property
    def days_remaining(self) -> Optional[int]:
        """Calculate days until due date"""
        if not self.due_date:
            return None
        return (self.due_date - date.today()).days

    @property
    def efficiency_score(self) -> Optional[float]:
        """Calculate efficiency based on estimated vs actual hours"""
        if not self.estimated_hours or not self.actual_hours:
            return None
        return min(100, (float(self.estimated_hours) / float(self.actual_hours)) * 100)


class TaskSubtask(TenantModel, AuditableMixin):
    """Subtasks for breaking down complex tasks"""
    __tablename__ = "task_subtasks"

    parent_task_id = Column(UUID(as_uuid=False), ForeignKey("team_tasks.id", ondelete="CASCADE"),
                           nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.NOT_STARTED)
    assignee_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    due_date = Column(Date)
    completed_date = Column(Date)
    estimated_hours = Column(Numeric(4, 2))
    actual_hours = Column(Numeric(4, 2))

    # Relationships
    parent_task = relationship("TeamTask", back_populates="subtasks")
    assignee = relationship("User", backref="assigned_subtasks")

    __table_args__ = (
        Index('ix_task_subtasks_parent', 'parent_task_id'),
        Index('ix_task_subtasks_status', 'status'),
    )


class TaskTimeLog(TenantModel, AuditableMixin):
    """Time tracking for tasks"""
    __tablename__ = "task_time_logs"

    task_id = Column(UUID(as_uuid=False), ForeignKey("team_tasks.id", ondelete="CASCADE"),
                     nullable=False, index=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)

    # Time Information
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration_hours = Column(Numeric(6, 2))
    description = Column(Text)

    # Billing
    is_billable = Column(Boolean, default=True)
    hourly_rate = Column(Numeric(10, 2))
    total_cost = Column(Numeric(10, 2))

    # Relationships
    task = relationship("TeamTask", back_populates="time_logs")
    user = relationship("User", backref="time_logs")

    __table_args__ = (
        Index('ix_task_time_logs_task_user', 'task_id', 'user_id'),
        Index('ix_task_time_logs_date', 'start_time'),
    )


class TeamMeeting(TenantModel, AuditableMixin):
    """Team meetings and collaboration sessions"""
    __tablename__ = "team_meetings"

    # Core Information
    team_id = Column(UUID(as_uuid=False), ForeignKey("teams.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    meeting_type = Column(Enum(MeetingType), default=MeetingType.STATUS_UPDATE, index=True)

    # Scheduling
    scheduled_start = Column(DateTime, nullable=False, index=True)
    scheduled_end = Column(DateTime, nullable=False)
    actual_start = Column(DateTime)
    actual_end = Column(DateTime)
    time_zone = Column(String(50), default="UTC")

    # Status and Location
    status = Column(Enum(MeetingStatus), default=MeetingStatus.SCHEDULED, index=True)
    location = Column(String(255))
    meeting_url = Column(String(500), comment="Video conference URL")
    dial_in_info = Column(Text)

    # Organization
    organizer_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    attendees = Column(JSON, default=list, comment="List of attendee user IDs")
    optional_attendees = Column(JSON, default=list)

    # Content
    agenda = Column(Text)
    minutes = Column(Text)
    action_items = Column(JSON, default=list)
    decisions_made = Column(JSON, default=list)

    # Follow-up
    recording_url = Column(String(500))
    shared_documents = Column(JSON, default=list)
    next_meeting_id = Column(UUID(as_uuid=False), ForeignKey("team_meetings.id"))

    # Relationships
    team = relationship("Team", back_populates="meetings")
    organizer = relationship("User", foreign_keys=[organizer_id], backref="organized_meetings")
    next_meeting = relationship("TeamMeeting", remote_side="TeamMeeting.id")

    __table_args__ = (
        Index('ix_team_meetings_team_date', 'team_id', 'scheduled_start'),
        Index('ix_team_meetings_organizer', 'organizer_id'),
    )

    @property
    def duration_minutes(self) -> Optional[int]:
        """Calculate actual meeting duration in minutes"""
        if not self.actual_start or not self.actual_end:
            return None
        return int((self.actual_end - self.actual_start).total_seconds() / 60)

    @property
    def is_upcoming(self) -> bool:
        """Check if meeting is upcoming"""
        return self.status == MeetingStatus.SCHEDULED and self.scheduled_start > datetime.utcnow()


class TeamChannel(TenantModel, AuditableMixin):
    """Communication channels for teams"""
    __tablename__ = "team_channels"

    team_id = Column(UUID(as_uuid=False), ForeignKey("teams.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)

    # Channel Properties
    is_private = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    channel_type = Column(Enum(ChannelType), default=ChannelType.GENERAL)

    # External Integration
    slack_channel_id = Column(String(100))
    teams_channel_id = Column(String(100))
    external_webhook_url = Column(String(500))

    # Moderation
    moderator_ids = Column(JSON, default=list)
    posting_permissions = Column(String(50), default="all", comment="all, leads_only, moderators_only")

    # Relationships
    team = relationship("Team", back_populates="channels")
    messages = relationship("TeamMessage", back_populates="channel", lazy="dynamic")

    __table_args__ = (
        Index('ix_team_channels_team_name', 'team_id', 'name', unique=True),
        Index('ix_team_channels_archived', 'is_archived'),
    )


class TeamMessage(TenantModel, AuditableMixin):
    """Messages in team channels"""
    __tablename__ = "team_messages"

    channel_id = Column(UUID(as_uuid=False), ForeignKey("team_channels.id", ondelete="CASCADE"),
                       nullable=False, index=True)
    sender_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True)

    # Content
    content = Column(Text, nullable=False)
    message_type = Column(Enum(MessageType), default=MessageType.TEXT)

    # Threading
    parent_message_id = Column(UUID(as_uuid=False), ForeignKey("team_messages.id"))
    thread_count = Column(Integer, default=0)

    # Reactions and Engagement
    reactions = Column(JSON, default=dict, comment="Emoji reactions")
    mentions = Column(JSON, default=list, comment="User IDs mentioned")

    # File Attachments
    attachments = Column(JSON, default=list, comment="File attachment metadata")

    # Status
    is_edited = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)
    is_announcement = Column(Boolean, default=False)

    # Relationships
    channel = relationship("TeamChannel", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_team_messages")
    parent_message = relationship("TeamMessage", remote_side="TeamMessage.id", backref="replies")

    __table_args__ = (
        Index('ix_team_messages_channel_created', 'channel_id', 'created_at'),
        Index('ix_team_messages_sender', 'sender_id'),
        Index('ix_team_messages_thread', 'parent_message_id'),
    )


class TeamMetrics(TenantModel, AuditableMixin):
    """Team performance metrics and analytics"""
    __tablename__ = "team_metrics"

    team_id = Column(UUID(as_uuid=False), ForeignKey("teams.id"), nullable=False, index=True)
    metric_date = Column(Date, nullable=False, index=True)
    metric_period = Column(String(20), default="daily", comment="daily, weekly, monthly")

    # Performance Metrics
    tasks_completed = Column(Integer, default=0)
    tasks_overdue = Column(Integer, default=0)
    average_task_completion_time = Column(Numeric(6, 2), comment="Hours")
    team_velocity = Column(Numeric(6, 2), comment="Tasks completed per period")

    # Quality Metrics
    average_quality_score = Column(Numeric(3, 2))
    rework_percentage = Column(Numeric(5, 2))
    customer_satisfaction = Column(Numeric(3, 2))

    # Collaboration Metrics
    meeting_hours = Column(Numeric(6, 2))
    messages_sent = Column(Integer, default=0)
    documents_shared = Column(Integer, default=0)

    # Resource Metrics
    utilization_rate = Column(Numeric(5, 2), comment="Percentage")
    budget_utilization = Column(Numeric(5, 2), comment="Percentage")
    cost_per_deliverable = Column(Numeric(10, 2))

    # Efficiency Metrics
    automation_percentage = Column(Numeric(5, 2))
    process_efficiency = Column(Numeric(5, 2))
    knowledge_sharing_score = Column(Numeric(3, 2))

    # Relationships
    team = relationship("Team", back_populates="metrics")

    __table_args__ = (
        UniqueConstraint('team_id', 'metric_date', 'metric_period', name='uq_team_metrics'),
        Index('ix_team_metrics_team_date', 'team_id', 'metric_date'),
    )


class PerformanceReview(TenantModel, AuditableMixin):
    """Individual performance reviews within teams"""
    __tablename__ = "performance_reviews"

    team_member_id = Column(UUID(as_uuid=False), ForeignKey("team_members.id"),
                           nullable=False, index=True)
    reviewer_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)

    # Review Period
    review_period_start = Column(Date, nullable=False)
    review_period_end = Column(Date, nullable=False)
    review_type = Column(String(50), default="periodic", comment="periodic, project_end, annual")

    # Ratings (1-10 scale)
    technical_performance = Column(Numeric(3, 1))
    collaboration_score = Column(Numeric(3, 1))
    communication_rating = Column(Numeric(3, 1))
    leadership_potential = Column(Numeric(3, 1))
    innovation_score = Column(Numeric(3, 1))
    overall_rating = Column(Numeric(3, 1))

    # Qualitative Feedback
    strengths = Column(Text)
    areas_for_improvement = Column(Text)
    achievements = Column(Text)
    development_goals = Column(Text)

    # Recommendations
    promotion_ready = Column(Boolean, default=False)
    role_change_recommendation = Column(String(200))
    training_recommendations = Column(JSON, default=list)

    # Status
    is_final = Column(Boolean, default=False)
    reviewed_with_member = Column(Boolean, default=False)
    member_acknowledgment = Column(DateTime)

    # Relationships
    team_member = relationship("TeamMember", back_populates="performance_reviews")
    reviewer = relationship("User", backref="conducted_reviews")

    __table_args__ = (
        CheckConstraint('technical_performance >= 1 AND technical_performance <= 10'),
        CheckConstraint('overall_rating >= 1 AND overall_rating <= 10'),
        Index('ix_performance_reviews_member_date', 'team_member_id', 'review_period_end'),
    )


# Association table for external advisors and teams
advisor_team_assignments = Table(
    'advisor_team_assignments',
    TenantModel.metadata,
    Column('advisor_id', UUID(as_uuid=False), ForeignKey('external_advisors.id', ondelete='CASCADE')),
    Column('team_member_id', UUID(as_uuid=False), ForeignKey('team_members.id', ondelete='CASCADE')),
    Column('assignment_date', Date, default=date.today),
    Column('hourly_rate', Numeric(10, 2)),
    UniqueConstraint('advisor_id', 'team_member_id', name='uq_advisor_team_assignment')
)