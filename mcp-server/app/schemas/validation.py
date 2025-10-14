"""
BMAD v6 MCP Server Validation Schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class ScaleLevelEnum(int, Enum):
    ATOMIC = 0
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    ENTERPRISE = 4

class ProjectPhaseEnum(int, Enum):
    ANALYSIS = 1
    PLANNING = 2
    SOLUTIONING = 3
    IMPLEMENTATION = 4

class StoryStateEnum(str, Enum):
    BACKLOG = "BACKLOG"
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

class StoryStatusEnum(str, Enum):
    DRAFT = "Draft"
    READY = "Ready"
    IN_REVIEW = "In Review"
    DONE = "Done"

class AgentTypeEnum(str, Enum):
    ORCHESTRATOR = "orchestrator"
    SPECIALIST = "specialist"
    IMPLEMENTER = "implementer"
    DOMAIN_EXPERT = "domain_expert"

# Request Validation Schemas

class CreateProjectRequest(BaseModel):
    project_id: str = Field(..., min_length=1, max_length=100, regex=r'^[a-zA-Z0-9\-_]+$')
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    estimated_stories: Optional[int] = Field(None, ge=0, le=1000)
    estimated_epics: Optional[int] = Field(None, ge=0, le=100)
    complexity: Optional[str] = Field("medium", regex=r'^(low|medium|high)$')
    team_size: Optional[int] = Field(1, ge=1, le=50)
    timeline_weeks: Optional[int] = Field(4, ge=1, le=104)

class CreateStoryRequest(BaseModel):
    story_id: str = Field(..., min_length=1, max_length=100, regex=r'^[a-zA-Z0-9\-_]+$')
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    project_id: str = Field(..., min_length=1, max_length=100)
    epic_id: Optional[str] = Field(None, min_length=1, max_length=100)
    acceptance_criteria: List[str] = Field(default=[], max_items=20)
    points: Optional[int] = Field(None, ge=1, le=21)

class CreateDealRequest(BaseModel):
    deal_id: str = Field(..., min_length=1, max_length=100, regex=r'^[a-zA-Z0-9\-_]+$')
    name: str = Field(..., min_length=1, max_length=200)
    target_company: str = Field(..., min_length=1, max_length=200)
    deal_type: str = Field(..., regex=r'^(acquisition|merger|joint_venture)$')
    deal_value: Optional[float] = Field(None, ge=0)
    currency: str = Field("GBP", regex=r'^[A-Z]{3}$')
    project_id: Optional[str] = Field(None, min_length=1, max_length=100)

class WorkflowExecutionRequest(BaseModel):
    workflow_name: str = Field(..., min_length=1, max_length=100)
    project_id: str = Field(..., min_length=1, max_length=100)
    context: Dict[str, Any] = Field(default={})
    
    @validator('workflow_name')
    def validate_workflow_name(cls, v):
        valid_workflows = [
            'workflow-status', 'brainstorm-project', 'research', 'product-brief',
            'plan-project', 'solution-architecture', 'tech-spec',
            'create-story', 'story-ready', 'story-context', 'dev-story', 'story-approved',
            'retrospective', 'deal-analysis', 'valuation-modeling'
        ]
        if v not in valid_workflows:
            raise ValueError(f'Invalid workflow name. Must be one of: {valid_workflows}')
        return v

class AgentInvocationRequest(BaseModel):
    agent_name: str = Field(..., min_length=1, max_length=100)
    prompt: str = Field(..., min_length=1, max_length=5000)
    context: Dict[str, Any] = Field(default={})
    project_id: Optional[str] = Field(None, min_length=1, max_length=100)
    
    @validator('agent_name')
    def validate_agent_name(cls, v):
        valid_agents = ['bmad-master', 'analyst', 'pm', 'architect', 'dev', 'ma-specialist']
        if v not in valid_agents:
            raise ValueError(f'Invalid agent name. Must be one of: {valid_agents}')
        return v

class StateTransitionRequest(BaseModel):
    story_id: str = Field(..., min_length=1, max_length=100)
    from_state: StoryStateEnum
    to_state: StoryStateEnum
    
    @validator('to_state')
    def validate_state_transition(cls, v, values):
        if 'from_state' in values:
            from_state = values['from_state']
            valid_transitions = {
                StoryStateEnum.BACKLOG: [StoryStateEnum.TODO],
                StoryStateEnum.TODO: [StoryStateEnum.IN_PROGRESS],
                StoryStateEnum.IN_PROGRESS: [StoryStateEnum.DONE],
                StoryStateEnum.DONE: []  # No transitions from DONE
            }
            
            if v not in valid_transitions.get(from_state, []):
                raise ValueError(f'Invalid state transition: {from_state} -> {v}')
        return v

class CreateValuationRequest(BaseModel):
    deal_id: str = Field(..., min_length=1, max_length=100)
    model_type: str = Field(..., regex=r'^(DCF|COMPARABLE|PRECEDENT)$')
    discount_rate: Optional[float] = Field(None, ge=0, le=1)
    terminal_growth_rate: Optional[float] = Field(None, ge=0, le=1)
    revenue_multiple: Optional[float] = Field(None, ge=0)
    ebitda_multiple: Optional[float] = Field(None, ge=0)

# Response Validation Schemas

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    current_phase: int
    scale_level: int
    backlog: List[str]
    todo: Optional[str]
    in_progress: Optional[str]
    done: List[str]
    created_at: datetime
    updated_at: datetime

class StoryResponse(BaseModel):
    id: str
    title: str
    description: str
    project_id: str
    epic_id: Optional[str]
    status: str
    state: str
    points: Optional[int]
    assignee: Optional[str]
    acceptance_criteria: List[str]
    created_at: datetime
    updated_at: datetime

class DealResponse(BaseModel):
    id: str
    name: str
    target_company: str
    deal_type: str
    deal_value: Optional[float]
    currency: str
    status: str
    project_id: Optional[str]
    revenue: Optional[float]
    ebitda: Optional[float]
    multiple: Optional[float]
    created_at: datetime
    updated_at: datetime

class WorkflowExecutionResponse(BaseModel):
    workflow_name: str
    project_id: str
    status: str
    result: Dict[str, Any]
    timestamp: datetime

class AgentInvocationResponse(BaseModel):
    agent_name: str
    response: Dict[str, Any]
    timestamp: datetime

class APIResponse(BaseModel):
    success: bool = True
    message: str = "Success"
    data: Optional[Any] = None
    timestamp: datetime

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    message: str
    timestamp: datetime
