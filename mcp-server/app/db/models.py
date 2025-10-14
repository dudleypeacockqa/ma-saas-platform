"""
BMAD v6 MCP Server SQLAlchemy ORM Models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.db.base import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    current_phase = Column(Integer, default=1)  # 1=Analysis, 2=Planning, 3=Solutioning, 4=Implementation
    scale_level = Column(Integer, default=1)    # 0=Atomic, 1=Small, 2=Medium, 3=Large, 4=Enterprise
    
    # BMAD v6 State Machine
    backlog = Column(JSON, default=list)        # List of story IDs
    todo = Column(String, nullable=True)        # Single story ID
    in_progress = Column(String, nullable=True) # Single story ID
    done = Column(JSON, default=list)           # List of completed story IDs with timestamps
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    stories = relationship("Story", back_populates="project")
    epics = relationship("Epic", back_populates="project")
    deals = relationship("Deal", back_populates="project")

class Story(Base):
    __tablename__ = "stories"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    acceptance_criteria = Column(JSON, default=list)
    epic_id = Column(String, ForeignKey("epics.id"), nullable=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    
    # BMAD v6 Story Status
    status = Column(String, default="Draft")  # Draft, Ready, In Review, Done
    state = Column(String, default="BACKLOG") # BACKLOG, TODO, IN_PROGRESS, DONE
    points = Column(Integer, nullable=True)
    assignee = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="stories")
    epic = relationship("Epic", back_populates="stories")

class Epic(Base):
    __tablename__ = "epics"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    status = Column(String, default="PLANNED")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="epics")
    stories = relationship("Story", back_populates="epic")

class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id = Column(String, primary_key=True, index=True)
    workflow_name = Column(String, nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    status = Column(String, default="running")  # running, completed, failed, paused
    current_step = Column(Integer, default=0)
    context = Column(JSON, default=dict)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    
    # Metadata
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

class AgentConfiguration(Base):
    __tablename__ = "agent_configurations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text)
    author = Column(String, default="BMad Core")
    communication_language = Column(String, default="English")
    persona = Column(Text)
    agent_type = Column(String, nullable=False)  # orchestrator, specialist, implementer, domain_expert
    capabilities = Column(JSON, default=list)
    
    # Agent behavior configuration
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=4000)
    system_prompt = Column(Text, nullable=True)
    
    # Workflow integration
    preferred_workflows = Column(JSON, default=list)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Deal(Base):
    __tablename__ = "deals"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    target_company = Column(String, nullable=False)
    deal_type = Column(String, nullable=False)  # acquisition, merger, joint_venture
    deal_value = Column(Float, nullable=True)
    currency = Column(String, default="GBP")
    status = Column(String, default="PIPELINE")  # PIPELINE, DUE_DILIGENCE, NEGOTIATION, CLOSED
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    
    # Financial metrics
    revenue = Column(Float, nullable=True)
    ebitda = Column(Float, nullable=True)
    multiple = Column(Float, nullable=True)
    
    # Key dates
    initial_contact = Column(DateTime(timezone=True), nullable=True)
    loi_signed = Column(DateTime(timezone=True), nullable=True)
    due_diligence_start = Column(DateTime(timezone=True), nullable=True)
    expected_close = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="deals")
    valuations = relationship("ValuationModel", back_populates="deal")

class ValuationModel(Base):
    __tablename__ = "valuation_models"

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(String, ForeignKey("deals.id"), nullable=False)
    model_type = Column(String, nullable=False)  # DCF, COMPARABLE, PRECEDENT
    
    # DCF specific
    discount_rate = Column(Float, nullable=True)
    terminal_growth_rate = Column(Float, nullable=True)
    
    # Comparable specific
    revenue_multiple = Column(Float, nullable=True)
    ebitda_multiple = Column(Float, nullable=True)
    
    # Results
    enterprise_value = Column(Float, nullable=True)
    equity_value = Column(Float, nullable=True)
    value_per_share = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    deal = relationship("Deal", back_populates="valuations")

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, unique=True, nullable=False, index=True)
    encrypted_key = Column(Text, nullable=False)
    key_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False)
    user_id = Column(String, nullable=True)
    resource_type = Column(String, nullable=True)
    resource_id = Column(String, nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String, nullable=True)
    
    # Metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
