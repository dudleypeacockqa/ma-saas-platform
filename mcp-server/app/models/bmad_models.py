"""
BMAD v6 Data Models
Pydantic models for BMAD-method v6 MCP server
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

class ScaleLevel(int, Enum):
    """BMAD v6 Scale-Adaptive levels."""
    ATOMIC = 0      # Single atomic change
    SMALL = 1       # 1-10 stories, 1 epic
    MEDIUM = 2      # 5-15 stories, 1-2 epics
    LARGE = 3       # 12-40 stories, 2-5 epics
    ENTERPRISE = 4  # 40+ stories, 5+ epics

class ProjectPhase(int, Enum):
    """BMAD v6 Four-phase methodology."""
    ANALYSIS = 1        # Optional discovery and requirements
    PLANNING = 2        # Required scale-adaptive planning
    SOLUTIONING = 3     # Architecture (Levels 3-4 only)
    IMPLEMENTATION = 4  # Iterative development

class StoryState(str, Enum):
    """BMAD v6 Story state machine."""
    BACKLOG = "BACKLOG"
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

class StoryStatus(str, Enum):
    """BMAD v6 Story file status values."""
    DRAFT = "Draft"
    READY = "Ready"
    IN_REVIEW = "In Review"
    DONE = "Done"

class AgentType(str, Enum):
    """BMAD v6 Agent types."""
    ORCHESTRATOR = "orchestrator"
    SPECIALIST = "specialist"
    IMPLEMENTER = "implementer"
    DOMAIN_EXPERT = "domain_expert"

# Request/Response Models

class AgentRequest(BaseModel):
    """Request to invoke a BMAD v6 agent."""
    agent_name: str = Field(..., description="Name of the agent to invoke")
    prompt: str = Field(..., description="Prompt or instruction for the agent")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Additional context")
    project_id: Optional[str] = Field(default=None, description="Project identifier")

class WorkflowRequest(BaseModel):
    """Request to execute a BMAD v6 workflow."""
    workflow_name: str = Field(..., description="Name of the workflow to execute")
    context: Dict[str, Any] = Field(default={}, description="Workflow context and parameters")
    project_id: str = Field(..., description="Project identifier")

class WorkflowResponse(BaseModel):
    """Response from workflow execution."""
    workflow_name: str
    status: str
    result: Dict[str, Any]
    timestamp: datetime

# Core BMAD Models

class Story(BaseModel):
    """BMAD v6 User Story."""
    id: str
    title: str
    description: str
    acceptance_criteria: List[str]
    epic_id: Optional[str] = None
    status: StoryStatus = StoryStatus.DRAFT
    state: StoryState = StoryState.BACKLOG
    points: Optional[int] = None
    assignee: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Epic(BaseModel):
    """BMAD v6 Epic."""
    id: str
    title: str
    description: str
    stories: List[str] = Field(default=[], description="List of story IDs")
    status: str = "PLANNED"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProjectState(BaseModel):
    """BMAD v6 Project state tracking."""
    project_id: str
    current_phase: ProjectPhase
    scale_level: ScaleLevel
    
    # Phase 4 Implementation state machine
    backlog: List[str] = Field(default=[], description="Ordered list of story IDs to be drafted")
    todo: Optional[str] = Field(default=None, description="Single story ID that needs drafting")
    in_progress: Optional[str] = Field(default=None, description="Single story ID being developed")
    done: List[str] = Field(default=[], description="Completed story IDs with dates")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class WorkflowState(BaseModel):
    """State of a workflow execution."""
    workflow_id: str
    workflow_name: str
    project_id: str
    status: str  # "running", "completed", "failed", "paused"
    current_step: int = 0
    context: Dict[str, Any] = {}
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

# Agent Models

class AgentCapability(BaseModel):
    """BMAD v6 Agent capability definition."""
    name: str
    description: str
    parameters: Dict[str, Any] = {}

class AgentConfiguration(BaseModel):
    """BMAD v6 Agent configuration (agent-as-code)."""
    name: str
    description: str
    author: str = "BMad Core"
    communication_language: str = "English"
    persona: str
    agent_type: AgentType
    capabilities: List[str] = []
    
    # Agent behavior configuration
    temperature: float = 0.7
    max_tokens: int = 4000
    system_prompt: Optional[str] = None
    
    # Workflow integration
    preferred_workflows: List[str] = []
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Workflow Models

class WorkflowStep(BaseModel):
    """Individual step in a BMAD v6 workflow."""
    name: str
    description: str
    agent_name: Optional[str] = None
    action: str
    parameters: Dict[str, Any] = {}
    conditions: List[str] = []

class WorkflowDefinition(BaseModel):
    """BMAD v6 Workflow definition."""
    name: str
    description: str
    author: str = "BMad Core"
    phase: ProjectPhase
    level_requirement: Optional[List[ScaleLevel]] = None
    
    steps: List[WorkflowStep]
    
    # Workflow metadata
    template: bool = False
    web_bundle: bool = False
    instructions_path: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

# M&A Specific Models

class Deal(BaseModel):
    """M&A Deal representation."""
    id: str
    name: str
    target_company: str
    deal_type: str  # "acquisition", "merger", "joint_venture"
    deal_value: Optional[float] = None
    currency: str = "GBP"
    status: str = "PIPELINE"  # "PIPELINE", "DUE_DILIGENCE", "NEGOTIATION", "CLOSED"
    
    # Financial metrics
    revenue: Optional[float] = None
    ebitda: Optional[float] = None
    multiple: Optional[float] = None
    
    # Key dates
    initial_contact: Optional[datetime] = None
    loi_signed: Optional[datetime] = None
    due_diligence_start: Optional[datetime] = None
    expected_close: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ValuationModel(BaseModel):
    """Financial valuation model for M&A deals."""
    deal_id: str
    model_type: str  # "DCF", "COMPARABLE", "PRECEDENT"
    
    # DCF specific
    discount_rate: Optional[float] = None
    terminal_growth_rate: Optional[float] = None
    
    # Comparable specific
    revenue_multiple: Optional[float] = None
    ebitda_multiple: Optional[float] = None
    
    # Results
    enterprise_value: Optional[float] = None
    equity_value: Optional[float] = None
    value_per_share: Optional[float] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

# API Response Models

class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool = True
    message: str = "Success"
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    error: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
