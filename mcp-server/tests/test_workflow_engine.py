"""
BMAD v6 MCP Server Workflow Engine Tests
"""

import pytest
import asyncio
from datetime import datetime

from app.services.workflow_engine import WorkflowEngine, Workflow
from app.models.bmad_models import ProjectPhase, ScaleLevel, ProjectState

@pytest.fixture
def workflow_engine():
    """Create workflow engine instance."""
    return WorkflowEngine()

@pytest.fixture
def sample_workflows():
    """Create sample workflows for testing."""
    return [
        Workflow(
            name="test-workflow-1",
            description="Test workflow for analysis phase",
            phase=1,
            level_requirement=None,
            steps=["step1", "step2", "step3"]
        ),
        Workflow(
            name="test-workflow-2",
            description="Test workflow for implementation phase",
            phase=4,
            level_requirement=[2, 3],
            steps=["implement", "test", "deploy"]
        ),
        Workflow(
            name="test-workflow-3",
            description="Test workflow for large projects only",
            phase=3,
            level_requirement=[3, 4],
            steps=["design", "architect", "validate"]
        )
    ]

class TestWorkflowRegistration:
    """Test workflow registration and retrieval."""
    
    @pytest.mark.asyncio
    async def test_register_workflow(self, workflow_engine, sample_workflows):
        """Test workflow registration."""
        workflow = sample_workflows[0]
        
        result = await workflow_engine.register_workflow(workflow)
        assert result is True
        
        retrieved = await workflow_engine.get_workflow(workflow.name)
        assert retrieved is not None
        assert retrieved.name == workflow.name
        assert retrieved.description == workflow.description
    
    @pytest.mark.asyncio
    async def test_list_workflows(self, workflow_engine, sample_workflows):
        """Test listing all workflows."""
        # Register multiple workflows
        for workflow in sample_workflows:
            await workflow_engine.register_workflow(workflow)
        
        workflows = await workflow_engine.list_workflows()
        assert len(workflows) >= len(sample_workflows)
        
        workflow_names = [w.name for w in workflows]
        for sample_workflow in sample_workflows:
            assert sample_workflow.name in workflow_names
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_workflow(self, workflow_engine):
        """Test retrieving non-existent workflow."""
        result = await workflow_engine.get_workflow("nonexistent-workflow")
        assert result is None

class TestScaleAssessment:
    """Test project scale assessment."""
    
    @pytest.mark.asyncio
    async def test_assess_atomic_scale(self, workflow_engine):
        """Test atomic scale assessment."""
        context = {
            "estimated_stories": 1,
            "estimated_epics": 1,
            "complexity": "low",
            "team_size": 1,
            "timeline_weeks": 1
        }
        
        scale = await workflow_engine.assess_project_scale(context)
        assert scale == ScaleLevel.ATOMIC
    
    @pytest.mark.asyncio
    async def test_assess_small_scale(self, workflow_engine):
        """Test small scale assessment."""
        context = {
            "estimated_stories": 5,
            "estimated_epics": 1,
            "complexity": "medium",
            "team_size": 2,
            "timeline_weeks": 4
        }
        
        scale = await workflow_engine.assess_project_scale(context)
        assert scale == ScaleLevel.SMALL

class TestPhaseRouting:
    """Test phase routing logic."""
    
    @pytest.mark.asyncio
    async def test_route_small_project(self, workflow_engine):
        """Test routing for small projects."""
        phase = await workflow_engine.route_to_phase(ScaleLevel.SMALL)
        assert phase == ProjectPhase.IMPLEMENTATION
    
    @pytest.mark.asyncio
    async def test_route_large_project(self, workflow_engine):
        """Test routing for large projects."""
        phase = await workflow_engine.route_to_phase(ScaleLevel.LARGE)
        assert phase == ProjectPhase.SOLUTIONING

class TestWorkflowExecution:
    """Test workflow execution."""
    
    @pytest.mark.asyncio
    async def test_execute_workflow_status(self, workflow_engine):
        """Test workflow-status execution."""
        # Register the workflow first
        workflow = Workflow(
            name="workflow-status",
            description="Universal entry point for checking project status",
            phase=1,
            level_requirement=None,
            steps=["check_status", "assess_context", "route"]
        )
        await workflow_engine.register_workflow(workflow)
        
        result = await workflow_engine.execute_workflow(
            workflow_name="workflow-status",
            context={},
            project_id="test-project-001"
        )
        
        assert result is not None
        assert result["status"] == "new_project"
        assert "recommendations" in result
    
    @pytest.mark.asyncio
    async def test_execute_plan_project(self, workflow_engine):
        """Test plan-project execution."""
        # Register the workflow first
        workflow = Workflow(
            name="plan-project",
            description="Scale-adaptive project planning router",
            phase=2,
            level_requirement=None,
            steps=["assess_scale", "determine_phase", "route"]
        )
        await workflow_engine.register_workflow(workflow)
        
        context = {
            "project_name": "Test Project",
            "estimated_stories": 15,
            "estimated_epics": 3,
            "complexity": "medium",
            "team_size": 5,
            "timeline_weeks": 8
        }
        
        result = await workflow_engine.execute_workflow(
            workflow_name="plan-project",
            context=context,
            project_id="test-project-002"
        )
        
        assert result is not None
        assert "scale_level" in result
        assert "next_phase" in result
        assert "planning_artifacts" in result
    
    @pytest.mark.asyncio
    async def test_execute_nonexistent_workflow(self, workflow_engine):
        """Test execution of non-existent workflow."""
        with pytest.raises(ValueError, match="Workflow not found"):
            await workflow_engine.execute_workflow(
                workflow_name="nonexistent-workflow",
                context={},
                project_id="test-project"
            )

class TestImplementationWorkflows:
    """Test Phase 4 implementation workflows."""
    
    @pytest.mark.asyncio
    async def test_create_story_workflow(self, workflow_engine):
        """Test create-story workflow."""
        project_id = "test-project-create-story"
        project_state = await workflow_engine.create_project_state(
            project_id=project_id,
            phase=ProjectPhase.IMPLEMENTATION,
            scale_level=ScaleLevel.SMALL
        )
        project_state.backlog = ["story-2", "story-3"]
        project_state.todo = "story-1"
        
        workflow = Workflow(
            name="create-story",
            description="Draft user story from TODO section",
            phase=4,
            level_requirement=None,
            steps=["read_todo", "gather_context", "draft_story"]
        )
        await workflow_engine.register_workflow(workflow)
        
        result = await workflow_engine.execute_workflow(
            workflow_name="create-story",
            context={},
            project_id=project_id
        )
        
        assert result is not None
        assert result["story_id"] == "story-1"
        assert result["status"] == "drafted"
    
    @pytest.mark.asyncio
    async def test_story_ready_workflow(self, workflow_engine):
        """Test story-ready workflow."""
        project_id = "test-project-story-ready"
        project_state = await workflow_engine.create_project_state(
            project_id=project_id,
            phase=ProjectPhase.IMPLEMENTATION,
            scale_level=ScaleLevel.SMALL
        )
        project_state.backlog = ["story-2", "story-3"]
        project_state.todo = "story-1"
        
        workflow = Workflow(
            name="story-ready",
            description="Approve drafted story for development",
            phase=4,
            level_requirement=None,
            steps=["review_story", "validate_criteria", "transition"]
        )
        await workflow_engine.register_workflow(workflow)
        
        result = await workflow_engine.execute_workflow(
            workflow_name="story-ready",
            context={"story_id": "story-1"},
            project_id=project_id
        )
        
        assert result is not None
        assert result["status"] == "ready_for_development"
        assert result["state_transition"] == "TODO → IN_PROGRESS"
    
    @pytest.mark.asyncio
    async def test_story_approved_workflow(self, workflow_engine):
        """Test story-approved workflow."""
        project_id = "test-project-story-approved"
        project_state = await workflow_engine.create_project_state(
            project_id=project_id,
            phase=ProjectPhase.IMPLEMENTATION,
            scale_level=ScaleLevel.SMALL
        )
        project_state.in_progress = "story-1"
        project_state.todo = "story-2"
        project_state.backlog = ["story-3"]
        
        workflow = Workflow(
            name="story-approved",
            description="Mark story as done after DoD complete",
            phase=4,
            level_requirement=None,
            steps=["validate_dod", "transition_done", "update_status"]
        )
        await workflow_engine.register_workflow(workflow)
        
        result = await workflow_engine.execute_workflow(
            workflow_name="story-approved",
            context={"story_id": "story-1"},
            project_id=project_id
        )
        
        assert result is not None
        assert result["status"] == "completed"
        assert result["state_transition"] == "IN_PROGRESS → DONE"

class TestErrorHandling:
    """Test workflow engine error handling."""
    
    @pytest.mark.asyncio
    async def test_workflow_execution_error(self, workflow_engine):
        """Test handling of workflow execution errors."""
        workflow = Workflow(
            name="error-workflow",
            description="Workflow that causes errors",
            phase=1,
            level_requirement=None,
            steps=["error_step"]
        )
        await workflow_engine.register_workflow(workflow)
        
        with pytest.raises(ValueError, match="This is a deliberate error for testing."):
            await workflow_engine.execute_workflow(
                workflow_name="error-workflow",
                context={},
                project_id="error-project"
            )

if __name__ == "__main__":
    pytest.main([__file__])

