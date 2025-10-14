"""
BMAD v6 Workflow Engine Service
Implements scale-adaptive workflow orchestration and state machine management
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import logging

from app.models.bmad_models import (
    WorkflowDefinition, 
    WorkflowStep, 
    WorkflowState,
    ProjectPhase,
    ScaleLevel,
    ProjectState,
    StoryState,
    StoryStatus
)

logger = logging.getLogger(__name__)

class Workflow:
    """BMAD v6 Workflow implementation with scale-adaptive routing."""
    
    def __init__(
        self,
        name: str,
        description: str,
        phase: int,
        level_requirement: Optional[List[int]] = None,
        steps: List[str] = None
    ):
        self.name = name
        self.description = description
        self.phase = ProjectPhase(phase)
        self.level_requirement = [ScaleLevel(l) for l in level_requirement] if level_requirement else None
        self.steps = steps or []
        self.created_at = datetime.utcnow()
        
        logger.debug(f"Created workflow: {self.name} (Phase {self.phase.value})")
    
    def can_execute_for_level(self, scale_level: ScaleLevel) -> bool:
        """Check if workflow can execute for given scale level."""
        if self.level_requirement is None:
            return True
        return scale_level in self.level_requirement
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "phase": self.phase.value,
            "level_requirement": [l.value for l in self.level_requirement] if self.level_requirement else None,
            "steps": self.steps,
            "created_at": self.created_at.isoformat()
        }

class WorkflowEngine:
    """BMAD v6 Workflow Engine with scale-adaptive orchestration."""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.active_workflows: Dict[str, WorkflowState] = {}
        self.project_states: Dict[str, ProjectState] = {}
        
        logger.info("Initialized BMAD v6 Workflow Engine")
    
    async def register_workflow(self, workflow: Workflow) -> bool:
        """Register a workflow in the engine."""
        try:
            self.workflows[workflow.name] = workflow
            logger.info(f"Registered workflow: {workflow.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register workflow {workflow.name}: {str(e)}")
            return False
    
    async def get_workflow(self, name: str) -> Optional[Workflow]:
        """Get a workflow by name."""
        return self.workflows.get(name)
    
    async def list_workflows(self) -> List[Workflow]:
        """List all registered workflows."""
        return list(self.workflows.values())
    
    async def assess_project_scale(self, project_context: Dict[str, Any]) -> ScaleLevel:
        """Assess project scale level (0-4) based on context."""
        
        # Extract key indicators from context
        story_count = project_context.get('estimated_stories', 0)
        epic_count = project_context.get('estimated_epics', 0)
        complexity = project_context.get('complexity', 'medium').lower()
        team_size = project_context.get('team_size', 1)
        timeline_weeks = project_context.get('timeline_weeks', 4)
        
        # Scale assessment logic following BMAD v6 specifications
        if story_count <= 1 and epic_count <= 1 and complexity == 'low':
            return ScaleLevel.ATOMIC  # Level 0
        elif story_count <= 10 and epic_count <= 1:
            return ScaleLevel.SMALL   # Level 1
        elif story_count <= 15 and epic_count <= 2:
            return ScaleLevel.MEDIUM  # Level 2
        elif story_count <= 40 and epic_count <= 5:
            return ScaleLevel.LARGE   # Level 3
        else:
            return ScaleLevel.ENTERPRISE  # Level 4
    
    async def route_to_phase(self, scale_level: ScaleLevel, project_type: str = "software") -> ProjectPhase:
        """Route project to appropriate phase based on scale level."""
        
        # BMAD v6 routing logic
        if scale_level in [ScaleLevel.ATOMIC, ScaleLevel.SMALL, ScaleLevel.MEDIUM]:
            # Levels 0-2: Direct to Implementation after Planning
            return ProjectPhase.IMPLEMENTATION
        else:
            # Levels 3-4: Requires Solutioning phase
            return ProjectPhase.SOLUTIONING
    
    async def execute_workflow(
        self, 
        workflow_name: str, 
        context: Dict[str, Any], 
        project_id: str
    ) -> Dict[str, Any]:
        """Execute a BMAD v6 workflow with state management."""
        
        workflow = await self.get_workflow(workflow_name)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_name}")
        
        # Create workflow state
        workflow_id = str(uuid.uuid4())
        workflow_state = WorkflowState(
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            project_id=project_id,
            status="running",
            context=context
        )
        
        self.active_workflows[workflow_id] = workflow_state
        
        try:
            # Execute workflow based on type
            if workflow_name == "workflow-status":
                result = await self._execute_workflow_status(context, project_id)
            elif workflow_name == "plan-project":
                result = await self._execute_plan_project(context, project_id)
            elif workflow_name.startswith("create-story"):
                result = await self._execute_create_story(context, project_id)
            elif workflow_name.startswith("story-ready"):
                result = await self._execute_story_ready(context, project_id)
            elif workflow_name.startswith("dev-story"):
                result = await self._execute_dev_story(context, project_id)
            elif workflow_name.startswith("story-approved"):
                result = await self._execute_story_approved(context, project_id)
            else:
                result = await self._execute_generic_workflow(workflow, context, project_id)
            
            # Update workflow state
            workflow_state.status = "completed"
            workflow_state.result = result
            workflow_state.completed_at = datetime.utcnow()
            
            return result
            
        except Exception as e:
            workflow_state.status = "failed"
            workflow_state.error = str(e)
            logger.error(f"Workflow execution failed: {workflow_name} - {str(e)}")
            raise
    
    async def _execute_workflow_status(self, context: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """Execute workflow-status - universal entry point."""
        
        project_state = await self.get_project_state(project_id)
        
        if not project_state:
            # New project - guide through initial setup
            return {
                "status": "new_project",
                "message": "No existing project state found",
                "recommendations": [
                    "Start with brainstorm-project for ideation",
                    "Or proceed directly to plan-project for planning",
                    "For simple changes, consider tech-spec workflow"
                ],
                "next_workflows": ["brainstorm-project", "plan-project", "tech-spec"]
            }
        
        # Existing project - show current status
        return {
            "status": "existing_project",
            "project_id": project_id,
            "current_phase": project_state.current_phase.value,
            "scale_level": project_state.scale_level.value,
            "implementation_state": {
                "backlog_count": len(project_state.backlog),
                "todo": project_state.todo,
                "in_progress": project_state.in_progress,
                "done_count": len(project_state.done)
            },
            "next_actions": await self._determine_next_actions(project_state)
        }
    
    async def _execute_plan_project(self, context: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """Execute plan-project - scale-adaptive planning router."""
        
        # Assess project scale
        scale_level = await self.assess_project_scale(context)
        
        # Determine next phase
        next_phase = await self.route_to_phase(scale_level)
        
        # Create or update project state
        project_state = ProjectState(
            project_id=project_id,
            current_phase=ProjectPhase.PLANNING,
            scale_level=scale_level
        )
        
        # Generate planning artifacts based on scale level
        planning_result = await self._generate_planning_artifacts(scale_level, context)
        
        # For Levels 0-1, populate Phase 4 state machine directly
        if scale_level in [ScaleLevel.ATOMIC, ScaleLevel.SMALL]:
            project_state.current_phase = ProjectPhase.IMPLEMENTATION
            project_state.backlog = planning_result.get("story_ids", [])
            if project_state.backlog:
                project_state.todo = project_state.backlog.pop(0)
        
        # Save project state
        self.project_states[project_id] = project_state
        
        return {
            "scale_level": scale_level.value,
            "next_phase": next_phase.value,
            "planning_artifacts": planning_result,
            "project_state": project_state.model_dump() if hasattr(project_state, 'model_dump') else project_state.__dict__
        }
    
    async def _execute_create_story(self, context: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """Execute create-story - draft story from TODO section."""
        
        project_state = await self.get_project_state(project_id)
        if not project_state or not project_state.todo:
            raise ValueError("No story in TODO state to draft")
        
        story_id = project_state.todo
        
        # Generate story content
        story_content = await self._generate_story_content(story_id, context, project_state)
        
        return {
            "story_id": story_id,
            "status": "drafted",
            "content": story_content,
            "next_action": "Review story and run story-ready workflow to approve"
        }
    
    async def _execute_story_ready(self, context: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """Execute story-ready - approve story for development."""
        
        project_state = await self.get_project_state(project_id)
        if not project_state or not project_state.todo:
            raise ValueError("No story in TODO state to approve")
        
        # Transition: TODO → IN_PROGRESS, BACKLOG → TODO
        story_id = project_state.todo
        project_state.in_progress = story_id
        
        if project_state.backlog:
            project_state.todo = project_state.backlog.pop(0)
        else:
            project_state.todo = None
        
        project_state.last_updated = datetime.utcnow()
        
        return {
            "story_id": story_id,
            "status": "ready_for_development",
            "state_transition": "TODO → IN_PROGRESS",
            "next_action": "Run dev-story workflow to implement"
        }
    
    async def _execute_dev_story(self, context: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """Execute dev-story - implement user story."""
        
        project_state = await self.get_project_state(project_id)
        if not project_state or not project_state.in_progress:
            raise ValueError("No story in IN_PROGRESS state to implement")
        
        story_id = project_state.in_progress
        
        # Generate implementation guidance
        implementation_guidance = await self._generate_implementation_guidance(story_id, context, project_state)
        
        return {
            "story_id": story_id,
            "status": "implementation_guidance_provided",
            "guidance": implementation_guidance,
            "next_action": "Complete implementation and run story-approved workflow"
        }
    
    async def _execute_story_approved(self, context: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """Execute story-approved - mark story as done."""
        
        project_state = await self.get_project_state(project_id)
        if not project_state or not project_state.in_progress:
            raise ValueError("No story in IN_PROGRESS state to approve")
        
        # Transition: IN_PROGRESS → DONE
        story_id = project_state.in_progress
        project_state.done.append(f"{story_id}:{datetime.utcnow().isoformat()}")
        
        # Move next story if available
        if project_state.todo:
            project_state.in_progress = project_state.todo
            if project_state.backlog:
                project_state.todo = project_state.backlog.pop(0)
            else:
                project_state.todo = None
        else:
            project_state.in_progress = None
        
        project_state.last_updated = datetime.utcnow()
        
        return {
            "story_id": story_id,
            "status": "completed",
            "state_transition": "IN_PROGRESS → DONE",
            "next_action": "Continue with next story or run retrospective if epic complete"
        }
    
    async def _execute_generic_workflow(self, workflow: Workflow, context: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """Execute a generic workflow."""
        
        for step in workflow.steps:
            if step == "error_step":
                raise ValueError("This is a deliberate error for testing.")

        return {
            "workflow": workflow.name,
            "phase": workflow.phase.value,
            "steps_completed": workflow.steps,
            "context": context,
            "message": f"Executed {workflow.name} workflow following BMAD v6 methodology"
        }
    
    async def get_project_state(self, project_id: str) -> Optional[ProjectState]:
        """Get current project state."""
        return self.project_states.get(project_id)
    
    async def _determine_next_actions(self, project_state: ProjectState) -> List[str]:
        """Determine next recommended actions based on project state."""
        
        actions = []
        
        if project_state.current_phase == ProjectPhase.PLANNING:
            if project_state.scale_level in [ScaleLevel.LARGE, ScaleLevel.ENTERPRISE]:
                actions.append("Run solution-architecture workflow")
            else:
                actions.append("Begin implementation phase")
        
        elif project_state.current_phase == ProjectPhase.IMPLEMENTATION:
            if project_state.todo:
                actions.append("Run create-story workflow to draft next story")
            elif project_state.in_progress:
                actions.append("Run dev-story workflow to implement current story")
            elif project_state.backlog:
                actions.append("Run story-ready workflow to approve current story")
            else:
                actions.append("Run retrospective workflow - epic complete")
        
        return actions
    
    async def _generate_planning_artifacts(self, scale_level: ScaleLevel, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate planning artifacts based on scale level."""
        
        artifacts = {
            "scale_level": scale_level.value,
            "artifacts_created": []
        }
        
        if scale_level == ScaleLevel.ATOMIC:
            # Level 0: tech-spec + 1 story
            artifacts["artifacts_created"] = ["tech-spec.md", "story-1.md"]
            artifacts["story_ids"] = ["story-1"]
            
        elif scale_level == ScaleLevel.SMALL:
            # Level 1: tech-spec + epic + 2-3 stories
            artifacts["artifacts_created"] = ["tech-spec.md", "epic-1.md", "story-1.md", "story-2.md", "story-3.md"]
            artifacts["story_ids"] = ["story-1", "story-2", "story-3"]
            
        elif scale_level == ScaleLevel.MEDIUM:
            # Level 2: Focused PRD + tech-spec
            artifacts["artifacts_created"] = ["PRD.md", "tech-spec.md"]
            artifacts["story_ids"] = [f"story-{i}" for i in range(1, 11)]
            
        elif scale_level == ScaleLevel.LARGE:
            # Level 3: Full PRD + solution architecture
            artifacts["artifacts_created"] = ["PRD.md", "solution-architecture.md"]
            artifacts["story_ids"] = [f"story-{i}" for i in range(1, 21)]
            
        elif scale_level == ScaleLevel.ENTERPRISE:
            # Level 4: Comprehensive business case + multi-epic PRD
            artifacts["artifacts_created"] = ["business-case.md", "PRD-multi-epic.md"]
            artifacts["story_ids"] = [f"story-{i}" for i in range(1, 51)]
            
        return artifacts
    
    async def _generate_story_content(self, story_id: str, context: Dict[str, Any], project_state: ProjectState) -> str:
        """Generate story content based on context."""
        return f"# Story: {story_id}\n\nThis is the auto-generated content for the story."
    
    async def _generate_implementation_guidance(self, story_id: str, context: Dict[str, Any], project_state: ProjectState) -> str:
        """Generate implementation guidance for a story."""
        return f"# Implementation Guidance: {story_id}\n\nFollow these steps to implement the story..."
    
    async def create_project_state(self, project_id: str, phase: ProjectPhase, scale_level: ScaleLevel) -> ProjectState:
        """Create and store a new project state."""
        project_state = ProjectState(
            project_id=project_id,
            current_phase=phase,
            scale_level=scale_level
        )
        self.project_states[project_id] = project_state
        return project_state

