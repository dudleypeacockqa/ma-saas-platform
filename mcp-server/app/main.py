"""
BMAD v6 MCP Server - Centralized Model Context Protocol Server
Following BMAD-method v6 specifications for M&A SaaS platform development
"""

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import os
import json
import yaml
import asyncio
from datetime import datetime
import logging

from app.core.config import settings
from app.services.agent_registry import AgentRegistry, BMadAgent
from app.services.workflow_engine import WorkflowEngine, Workflow, WorkflowState
from app.services.security_manager import SecurityManager
from app.services.state_manager import StateManager
from app.services.integration_service import IntegrationService
from app.models.bmad_models import (
    AgentRequest, 
    WorkflowRequest, 
    WorkflowResponse,
    ProjectState,
    ScaleLevel,
    AgentType
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="BMAD v6 MCP Server",
    description="Centralized Model Context Protocol server following BMAD-method v6 specifications for M&A SaaS platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize core services
agent_registry = AgentRegistry()
workflow_engine = WorkflowEngine()
security_manager = SecurityManager()
state_manager = StateManager()
integration_service = IntegrationService(security_manager)

@app.on_event("startup")
async def startup_event():
    """Initialize BMAD v6 MCP Server with core agents and workflows."""
    logger.info("Starting BMAD v6 MCP Server...")
    
    # Load core BMAD v6 agents
    await load_core_agents()
    
    # Load core BMAD v6 workflows
    await load_core_workflows()
    
    # Initialize security manager
    await security_manager.initialize()
    
    # Sync API keys from existing services
    await integration_service.sync_api_keys()
    
    logger.info("BMAD v6 MCP Server startup complete")

async def load_core_agents():
    """Load core BMAD v6 agents following the agent-as-code pattern."""
    
    # BMAD Master Orchestrator
    bmad_master = BMadAgent(
        name="bmad-master",
        description="Master orchestrator for BMAD v6 workflows and agent coordination",
        persona="Strategic orchestrator with deep understanding of BMAD methodology",
        communication_language="English",
        agent_type=AgentType.ORCHESTRATOR,
        capabilities=[
            "workflow_orchestration",
            "agent_coordination", 
            "project_assessment",
            "scale_adaptive_routing"
        ]
    )
    
    # Business Analyst Agent
    analyst = BMadAgent(
        name="analyst",
        description="Business analysis and requirements gathering specialist for M&A projects",
        persona="Strategic business analyst with M&A expertise and market research capabilities",
        communication_language="English",
        agent_type=AgentType.SPECIALIST,
        capabilities=[
            "market_research",
            "business_analysis",
            "requirements_gathering",
            "competitive_analysis"
        ]
    )
    
    # Project Manager Agent
    pm = BMadAgent(
        name="pm",
        description="Project planning and management specialist following BMAD scale-adaptive methodology",
        persona="Experienced project manager with agile and M&A project expertise",
        communication_language="English", 
        agent_type=AgentType.SPECIALIST,
        capabilities=[
            "project_planning",
            "scale_assessment",
            "epic_breakdown",
            "story_creation"
        ]
    )
    
    # Solution Architect Agent
    architect = BMadAgent(
        name="architect",
        description="Technical architecture and solution design specialist",
        persona="Senior solution architect with enterprise M&A platform experience",
        communication_language="English",
        agent_type=AgentType.SPECIALIST, 
        capabilities=[
            "solution_architecture",
            "technical_design",
            "system_integration",
            "technology_selection"
        ]
    )
    
    # Development Agent
    dev = BMadAgent(
        name="dev",
        description="Software development specialist following BMAD v6 implementation patterns",
        persona="Senior full-stack developer with M&A domain expertise",
        communication_language="English",
        agent_type=AgentType.IMPLEMENTER,
        capabilities=[
            "code_implementation",
            "story_development", 
            "technical_review",
            "quality_assurance"
        ]
    )
    
    # M&A Deal Specialist Agent
    ma_specialist = BMadAgent(
        name="ma-specialist",
        description="M&A deal management and analysis specialist",
        persona="M&A expert with deep knowledge of deal structures, valuations, and processes",
        communication_language="English",
        agent_type=AgentType.DOMAIN_EXPERT,
        capabilities=[
            "deal_analysis",
            "valuation_modeling",
            "due_diligence",
            "deal_structuring"
        ]
    )
    
    # Register all agents
    agents = [bmad_master, analyst, pm, architect, dev, ma_specialist]
    for agent in agents:
        await agent_registry.register_agent(agent)
    
    logger.info(f"Loaded {len(agents)} core BMAD v6 agents")

async def load_core_workflows():
    """Load core BMAD v6 workflows following the four-phase methodology."""
    
    # Phase 1: Analysis Workflows
    analysis_workflows = [
        Workflow(
            name="workflow-status",
            description="Universal entry point for checking project status and routing",
            phase=1,
            level_requirement=None,
            steps=[
                "check_existing_status",
                "assess_project_context", 
                "route_to_appropriate_workflow"
            ]
        ),
        Workflow(
            name="brainstorm-project",
            description="Project ideation and concept exploration",
            phase=1,
            level_requirement=None,
            steps=[
                "gather_initial_requirements",
                "explore_solution_concepts",
                "identify_key_stakeholders"
            ]
        ),
        Workflow(
            name="research",
            description="Market research and competitive analysis",
            phase=1, 
            level_requirement=None,
            steps=[
                "define_research_scope",
                "conduct_market_analysis",
                "analyze_competitive_landscape"
            ]
        ),
        Workflow(
            name="product-brief",
            description="Strategic product planning culmination",
            phase=1,
            level_requirement=None,
            steps=[
                "synthesize_analysis_findings",
                "define_product_vision",
                "create_strategic_brief"
            ]
        )
    ]
    
    # Phase 2: Planning Workflows
    planning_workflows = [
        Workflow(
            name="plan-project", 
            description="Scale-adaptive project planning router",
            phase=2,
            level_requirement=None,
            steps=[
                "assess_project_complexity",
                "determine_scale_level",
                "route_to_appropriate_planning"
            ]
        )
    ]
    
    # Phase 3: Solutioning Workflows (Levels 3-4 only)
    solutioning_workflows = [
        Workflow(
            name="solution-architecture",
            description="Create overall system architecture",
            phase=3,
            level_requirement=[3, 4],
            steps=[
                "analyze_requirements",
                "design_system_architecture", 
                "create_technical_specifications"
            ]
        ),
        Workflow(
            name="tech-spec",
            description="Create epic-specific technical specifications (Just-In-Time)",
            phase=3,
            level_requirement=[1, 2, 3, 4],
            steps=[
                "analyze_epic_requirements",
                "design_technical_approach",
                "create_implementation_spec"
            ]
        )
    ]
    
    # Phase 4: Implementation Workflows
    implementation_workflows = [
        Workflow(
            name="create-story",
            description="Draft user story from TODO section",
            phase=4,
            level_requirement=None,
            steps=[
                "read_todo_story",
                "gather_context",
                "draft_detailed_story"
            ]
        ),
        Workflow(
            name="story-ready",
            description="Approve drafted story for development",
            phase=4,
            level_requirement=None,
            steps=[
                "review_story_draft",
                "validate_acceptance_criteria",
                "transition_to_in_progress"
            ]
        ),
        Workflow(
            name="story-context",
            description="Generate expertise injection for story",
            phase=4,
            level_requirement=None,
            steps=[
                "analyze_story_requirements",
                "identify_required_expertise",
                "generate_context_injection"
            ]
        ),
        Workflow(
            name="dev-story",
            description="Implement user story",
            phase=4,
            level_requirement=None,
            steps=[
                "read_story_context",
                "implement_functionality",
                "validate_acceptance_criteria"
            ]
        ),
        Workflow(
            name="story-approved",
            description="Mark story as done after DoD complete",
            phase=4,
            level_requirement=None,
            steps=[
                "validate_definition_of_done",
                "transition_to_done",
                "update_project_status"
            ]
        ),
        Workflow(
            name="retrospective",
            description="Capture epic learnings and improvements",
            phase=4,
            level_requirement=None,
            steps=[
                "gather_epic_feedback",
                "identify_improvements",
                "update_process_knowledge"
            ]
        )
    ]
    
    # M&A Specific Workflows
    ma_workflows = [
        Workflow(
            name="deal-analysis",
            description="Comprehensive M&A deal analysis",
            phase=1,
            level_requirement=None,
            steps=[
                "gather_deal_information",
                "analyze_financial_metrics",
                "assess_strategic_fit"
            ]
        ),
        Workflow(
            name="valuation-modeling",
            description="Create financial valuation models",
            phase=2,
            level_requirement=None,
            steps=[
                "build_dcf_model",
                "create_comparable_analysis",
                "synthesize_valuation_range"
            ]
        )
    ]
    
    # Register all workflows
    all_workflows = (
        analysis_workflows + 
        planning_workflows + 
        solutioning_workflows + 
        implementation_workflows +
        ma_workflows
    )
    
    for workflow in all_workflows:
        await workflow_engine.register_workflow(workflow)
    
    logger.info(f"Loaded {len(all_workflows)} core BMAD v6 workflows")

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with server status."""
    return {
        "message": "BMAD v6 MCP Server",
        "version": "1.0.0",
        "status": "operational",
        "methodology": "BMAD-method v6",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agents_loaded": len(agent_registry.agents),
        "workflows_loaded": len(workflow_engine.workflows),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/agents")
async def list_agents():
    """List all available BMAD v6 agents."""
    agents = await agent_registry.list_agents()
    return {
        "agents": [
            {
                "name": agent.name,
                "description": agent.description,
                "persona": agent.persona,
                "agent_type": agent.agent_type,
                "capabilities": agent.capabilities
            }
            for agent in agents
        ]
    }

@app.get("/api/v1/workflows")
async def list_workflows():
    """List all available BMAD v6 workflows."""
    workflows = await workflow_engine.list_workflows()
    return {
        "workflows": [
            {
                "name": workflow.name,
                "description": workflow.description,
                "phase": workflow.phase,
                "level_requirement": workflow.level_requirement,
                "steps": workflow.steps
            }
            for workflow in workflows
        ]
    }

@app.post("/api/v1/workflow/execute")
async def execute_workflow(
    request: WorkflowRequest,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Execute a BMAD v6 workflow."""
    try:
        # Validate authentication
        await security_manager.validate_token(credentials.credentials)
        
        # Get workflow
        workflow = await workflow_engine.get_workflow(request.workflow_name)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Execute workflow
        result = await workflow_engine.execute_workflow(
            workflow_name=request.workflow_name,
            context=request.context,
            project_id=request.project_id
        )
        
        return WorkflowResponse(
            workflow_name=request.workflow_name,
            status="completed",
            result=result,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Workflow execution error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/project/{project_id}/status")
async def get_project_status(
    project_id: str,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Get current project status following BMAD v6 state machine."""
    try:
        # Validate authentication
        await security_manager.validate_token(credentials.credentials)
        
        # Get project state
        project_state = await state_manager.get_project_state(project_id)
        
        return {
            "project_id": project_id,
            "current_phase": project_state.current_phase,
            "scale_level": project_state.scale_level,
            "backlog": project_state.backlog,
            "todo": project_state.todo,
            "in_progress": project_state.in_progress,
            "done": project_state.done,
            "last_updated": project_state.last_updated
        }
        
    except Exception as e:
        logger.error(f"Project status error: {str(e)}")
        raise HTTPException(status_code=404, detail="Project not found")

