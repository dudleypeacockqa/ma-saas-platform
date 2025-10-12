"""
Advanced Task Management and Workflow Automation
Real-time task orchestration for M&A workflows
"""

from typing import Dict, List, Optional, Any, Set
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from pydantic import BaseModel
import asyncio
import json
from sqlalchemy.orm import Session

from ..models.user import OrganizationRole
from .websocket_manager import WebSocketManager
from .notifications import NotificationService, NotificationType


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class TaskPriority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WorkflowTrigger(str, Enum):
    """Workflow automation triggers"""
    DEAL_CREATED = "deal_created"
    DEAL_STAGE_CHANGED = "deal_stage_changed"
    DOCUMENT_UPLOADED = "document_uploaded"
    DOCUMENT_APPROVED = "document_approved"
    TEAM_ASSIGNED = "team_assigned"
    DEADLINE_APPROACHING = "deadline_approaching"
    VALUATION_COMPLETED = "valuation_completed"
    DUE_DILIGENCE_STARTED = "due_diligence_started"
    NEGOTIATION_INITIATED = "negotiation_initiated"
    TERM_SHEET_SIGNED = "term_sheet_signed"
    INTEGRATION_PLANNING_STARTED = "integration_planning_started"


class TaskType(str, Enum):
    """Types of automated tasks"""
    NOTIFICATION = "notification"
    DOCUMENT_GENERATION = "document_generation"
    TEAM_ASSIGNMENT = "team_assignment"
    DEADLINE_CREATION = "deadline_creation"
    APPROVAL_REQUEST = "approval_request"
    DATA_ANALYSIS = "data_analysis"
    COMPLIANCE_CHECK = "compliance_check"
    INTEGRATION_SYNC = "integration_sync"
    REPORT_GENERATION = "report_generation"
    CALENDAR_EVENT = "calendar_event"


@dataclass
class TaskDefinition:
    """Definition of an automated task"""
    id: str
    name: str
    description: str
    task_type: TaskType
    priority: TaskPriority
    estimated_duration: timedelta
    dependencies: List[str] = field(default_factory=list)
    required_roles: List[OrganizationRole] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 3
    timeout: timedelta = field(default_factory=lambda: timedelta(hours=1))


@dataclass
class TaskInstance:
    """Instance of an executing task"""
    id: str
    definition_id: str
    workflow_id: str
    deal_id: Optional[str]
    organization_id: str
    assigned_to: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    progress: int = 0  # 0-100
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_attempts: int = 0
    context: Dict[str, Any] = field(default_factory=dict)


class WorkflowTemplate:
    """Template for automated workflows"""

    def __init__(self, id: str, name: str, description: str, trigger: WorkflowTrigger):
        self.id = id
        self.name = name
        self.description = description
        self.trigger = trigger
        self.tasks: List[TaskDefinition] = []
        self.conditions: Dict[str, Any] = {}
        self.variables: Dict[str, Any] = {}

    def add_task(self, task: TaskDefinition):
        """Add a task to the workflow"""
        self.tasks.append(task)

    def set_condition(self, key: str, value: Any):
        """Set a condition for workflow execution"""
        self.conditions[key] = value


class TaskAutomationEngine:
    """Core engine for task automation and workflow orchestration"""

    def __init__(self, websocket_manager: WebSocketManager, notification_service: NotificationService):
        self.websocket_manager = websocket_manager
        self.notification_service = notification_service
        self.workflow_templates: Dict[str, WorkflowTemplate] = {}
        self.active_workflows: Dict[str, List[TaskInstance]] = {}
        self.task_definitions: Dict[str, TaskDefinition] = {}
        self.running_tasks: Dict[str, TaskInstance] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.is_running = False

        # Initialize default workflow templates
        self._initialize_default_workflows()

    def _initialize_default_workflows(self):
        """Initialize default M&A workflow templates"""

        # Deal Creation Workflow
        deal_workflow = WorkflowTemplate(
            "deal_creation_workflow",
            "New Deal Setup",
            "Automated tasks when a new deal is created",
            WorkflowTrigger.DEAL_CREATED
        )

        # Task 1: Create initial due diligence checklist
        deal_workflow.add_task(TaskDefinition(
            "create_dd_checklist",
            "Create Due Diligence Checklist",
            "Generate initial due diligence checklist based on deal type",
            TaskType.DOCUMENT_GENERATION,
            TaskPriority.HIGH,
            timedelta(minutes=15),
            required_roles=[OrganizationRole.DIRECTOR, OrganizationRole.SENIOR_ASSOCIATE]
        ))

        # Task 2: Assign deal team
        deal_workflow.add_task(TaskDefinition(
            "assign_deal_team",
            "Assign Deal Team",
            "Automatically assign team members based on expertise and availability",
            TaskType.TEAM_ASSIGNMENT,
            TaskPriority.HIGH,
            timedelta(minutes=30),
            dependencies=["create_dd_checklist"],
            required_roles=[OrganizationRole.PARTNER, OrganizationRole.DIRECTOR]
        ))

        # Task 3: Send notifications
        deal_workflow.add_task(TaskDefinition(
            "notify_stakeholders",
            "Notify Stakeholders",
            "Send notifications to relevant team members and stakeholders",
            TaskType.NOTIFICATION,
            TaskPriority.MEDIUM,
            timedelta(minutes=5),
            dependencies=["assign_deal_team"]
        ))

        self.workflow_templates[deal_workflow.id] = deal_workflow

        # Due Diligence Workflow
        dd_workflow = WorkflowTemplate(
            "due_diligence_workflow",
            "Due Diligence Process",
            "Automated due diligence workflow management",
            WorkflowTrigger.DUE_DILIGENCE_STARTED
        )

        dd_workflow.add_task(TaskDefinition(
            "setup_data_room",
            "Setup Virtual Data Room",
            "Create and configure virtual data room structure",
            TaskType.DOCUMENT_GENERATION,
            TaskPriority.HIGH,
            timedelta(hours=1),
            required_roles=[OrganizationRole.SENIOR_ASSOCIATE, OrganizationRole.ASSOCIATE]
        ))

        dd_workflow.add_task(TaskDefinition(
            "schedule_management_presentations",
            "Schedule Management Presentations",
            "Create calendar events for management presentations",
            TaskType.CALENDAR_EVENT,
            TaskPriority.MEDIUM,
            timedelta(minutes=30),
            dependencies=["setup_data_room"]
        ))

        self.workflow_templates[dd_workflow.id] = dd_workflow

        # Document Approval Workflow
        approval_workflow = WorkflowTemplate(
            "document_approval_workflow",
            "Document Approval Process",
            "Automated document review and approval workflow",
            WorkflowTrigger.DOCUMENT_UPLOADED
        )

        approval_workflow.add_task(TaskDefinition(
            "compliance_check",
            "Compliance Review",
            "Automated compliance and risk assessment",
            TaskType.COMPLIANCE_CHECK,
            TaskPriority.HIGH,
            timedelta(minutes=45),
            required_roles=[OrganizationRole.DIRECTOR, OrganizationRole.PARTNER]
        ))

        approval_workflow.add_task(TaskDefinition(
            "request_approvals",
            "Request Document Approval",
            "Send approval requests to designated reviewers",
            TaskType.APPROVAL_REQUEST,
            TaskPriority.MEDIUM,
            timedelta(minutes=10),
            dependencies=["compliance_check"]
        ))

        self.workflow_templates[approval_workflow.id] = approval_workflow

    async def start_engine(self):
        """Start the task automation engine"""
        self.is_running = True
        # Start background task processor
        asyncio.create_task(self._process_task_queue())

    async def stop_engine(self):
        """Stop the task automation engine"""
        self.is_running = False

    async def trigger_workflow(
        self,
        trigger: WorkflowTrigger,
        context: Dict[str, Any],
        organization_id: str,
        deal_id: Optional[str] = None
    ) -> Optional[str]:
        """Trigger a workflow based on an event"""

        # Find matching workflow templates
        matching_workflows = [
            template for template in self.workflow_templates.values()
            if template.trigger == trigger
        ]

        if not matching_workflows:
            return None

        # For now, use the first matching workflow
        # In a full implementation, you'd have logic to select the best workflow
        workflow_template = matching_workflows[0]

        # Create workflow instance
        workflow_id = f"{workflow_template.id}_{datetime.utcnow().timestamp()}"

        # Create task instances
        task_instances = []
        for task_def in workflow_template.tasks:
            task_instance = TaskInstance(
                id=f"{task_def.id}_{workflow_id}",
                definition_id=task_def.id,
                workflow_id=workflow_id,
                deal_id=deal_id,
                organization_id=organization_id,
                assigned_to=None,  # Will be assigned during execution
                status=TaskStatus.PENDING,
                priority=task_def.priority,
                created_at=datetime.utcnow(),
                context=context
            )
            task_instances.append(task_instance)

        self.active_workflows[workflow_id] = task_instances

        # Queue initial tasks (those without dependencies)
        for task in task_instances:
            task_def = next(t for t in workflow_template.tasks if t.id == task.definition_id)
            if not task_def.dependencies:
                await self.task_queue.put(task)

        # Send real-time notification about workflow start
        await self._notify_workflow_started(workflow_id, workflow_template.name, organization_id)

        return workflow_id

    async def _process_task_queue(self):
        """Background task to process the task queue"""
        while self.is_running:
            try:
                # Get task from queue with timeout
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                await self._execute_task(task)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Error processing task queue: {e}")

    async def _execute_task(self, task: TaskInstance):
        """Execute a single task"""
        try:
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.utcnow()
            self.running_tasks[task.id] = task

            # Send real-time update
            await self._send_task_update(task)

            # Get task definition
            workflow_template = next(
                t for t in self.workflow_templates.values()
                if any(td.id == task.definition_id for td in t.tasks)
            )
            task_def = next(t for t in workflow_template.tasks if t.id == task.definition_id)

            # Execute based on task type
            result = await self._execute_task_by_type(task, task_def)

            # Mark as completed
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.progress = 100
            task.result = result

            # Send completion notification
            await self._send_task_update(task)

            # Check for dependent tasks to queue
            await self._queue_dependent_tasks(task)

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.retry_attempts += 1

            # Retry if under limit
            if task.retry_attempts < 3:
                task.status = TaskStatus.PENDING
                await asyncio.sleep(60)  # Wait before retry
                await self.task_queue.put(task)

            await self._send_task_update(task)

        finally:
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]

    async def _execute_task_by_type(self, task: TaskInstance, task_def: TaskDefinition) -> Dict[str, Any]:
        """Execute task based on its type"""

        if task_def.task_type == TaskType.NOTIFICATION:
            return await self._execute_notification_task(task, task_def)
        elif task_def.task_type == TaskType.DOCUMENT_GENERATION:
            return await self._execute_document_generation_task(task, task_def)
        elif task_def.task_type == TaskType.TEAM_ASSIGNMENT:
            return await self._execute_team_assignment_task(task, task_def)
        elif task_def.task_type == TaskType.DEADLINE_CREATION:
            return await self._execute_deadline_creation_task(task, task_def)
        elif task_def.task_type == TaskType.APPROVAL_REQUEST:
            return await self._execute_approval_request_task(task, task_def)
        elif task_def.task_type == TaskType.COMPLIANCE_CHECK:
            return await self._execute_compliance_check_task(task, task_def)
        elif task_def.task_type == TaskType.CALENDAR_EVENT:
            return await self._execute_calendar_event_task(task, task_def)
        else:
            return {"status": "not_implemented", "task_type": task_def.task_type}

    async def _execute_notification_task(self, task: TaskInstance, task_def: TaskDefinition) -> Dict[str, Any]:
        """Execute notification task"""
        # Create notification based on context
        notification_type = NotificationType.WORKFLOW_UPDATED

        # Send to organization members
        await self.websocket_manager.broadcast_to_organization(
            task.organization_id,
            {
                "type": "workflow_notification",
                "workflow_id": task.workflow_id,
                "task_name": task_def.name,
                "message": f"Workflow task '{task_def.name}' has been completed"
            }
        )

        return {"notifications_sent": True, "type": "workflow_notification"}

    async def _execute_document_generation_task(self, task: TaskInstance, task_def: TaskDefinition) -> Dict[str, Any]:
        """Execute document generation task"""
        # Simulate document generation
        await asyncio.sleep(2)  # Simulate processing time

        document_name = f"{task_def.name}_{task.deal_id}_{datetime.utcnow().strftime('%Y%m%d')}"

        return {
            "document_generated": True,
            "document_name": document_name,
            "template_used": task_def.name.lower().replace(" ", "_")
        }

    async def _execute_team_assignment_task(self, task: TaskInstance, task_def: TaskDefinition) -> Dict[str, Any]:
        """Execute team assignment task"""
        # In a real implementation, this would integrate with user management
        # to find available team members with appropriate skills

        suggested_roles = task_def.required_roles or [OrganizationRole.ASSOCIATE]

        return {
            "team_assigned": True,
            "suggested_roles": [role.value for role in suggested_roles],
            "assignment_criteria": "expertise_and_availability"
        }

    async def _execute_deadline_creation_task(self, task: TaskInstance, task_def: TaskDefinition) -> Dict[str, Any]:
        """Execute deadline creation task"""
        # Create deadlines based on deal timeline
        deadline_date = datetime.utcnow() + timedelta(days=30)  # Default 30 days

        return {
            "deadline_created": True,
            "deadline_date": deadline_date.isoformat(),
            "milestone": task_def.name
        }

    async def _execute_approval_request_task(self, task: TaskInstance, task_def: TaskDefinition) -> Dict[str, Any]:
        """Execute approval request task"""
        # Send approval requests to designated approvers
        approval_roles = [OrganizationRole.PARTNER, OrganizationRole.MANAGING_PARTNER]

        return {
            "approval_requests_sent": True,
            "approver_roles": [role.value for role in approval_roles],
            "approval_type": "document_review"
        }

    async def _execute_compliance_check_task(self, task: TaskInstance, task_def: TaskDefinition) -> Dict[str, Any]:
        """Execute compliance check task"""
        # Simulate compliance analysis
        await asyncio.sleep(3)  # Simulate analysis time

        compliance_score = 85  # Simulated score

        return {
            "compliance_check_completed": True,
            "compliance_score": compliance_score,
            "risk_level": "medium" if compliance_score < 90 else "low",
            "recommendations": ["Review section 3.2", "Update disclosure statement"]
        }

    async def _execute_calendar_event_task(self, task: TaskInstance, task_def: TaskDefinition) -> Dict[str, Any]:
        """Execute calendar event task"""
        # Create calendar events for management presentations, meetings, etc.
        event_date = datetime.utcnow() + timedelta(days=7)  # Schedule for next week

        return {
            "calendar_event_created": True,
            "event_date": event_date.isoformat(),
            "event_type": "management_presentation",
            "duration_hours": 2
        }

    async def _queue_dependent_tasks(self, completed_task: TaskInstance):
        """Queue tasks that depend on the completed task"""
        workflow_tasks = self.active_workflows.get(completed_task.workflow_id, [])

        # Find workflow template
        workflow_template = next(
            t for t in self.workflow_templates.values()
            if any(td.id == completed_task.definition_id for td in t.tasks)
        )

        for task in workflow_tasks:
            if task.status == TaskStatus.PENDING:
                task_def = next(t for t in workflow_template.tasks if t.id == task.definition_id)

                # Check if all dependencies are completed
                dependencies_completed = True
                for dep_id in task_def.dependencies:
                    dep_task = next((t for t in workflow_tasks if t.definition_id == dep_id), None)
                    if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                        dependencies_completed = False
                        break

                if dependencies_completed:
                    await self.task_queue.put(task)

    async def _send_task_update(self, task: TaskInstance):
        """Send real-time task update via WebSocket"""
        update_message = {
            "type": "task_update",
            "task_id": task.id,
            "workflow_id": task.workflow_id,
            "status": task.status,
            "progress": task.progress,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "error": task.error
        }

        await self.websocket_manager.broadcast_to_organization(
            task.organization_id,
            update_message
        )

    async def _notify_workflow_started(self, workflow_id: str, workflow_name: str, organization_id: str):
        """Send notification when workflow starts"""
        message = {
            "type": "workflow_started",
            "workflow_id": workflow_id,
            "workflow_name": workflow_name,
            "started_at": datetime.utcnow().isoformat()
        }

        await self.websocket_manager.broadcast_to_organization(organization_id, message)

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a workflow"""
        if workflow_id not in self.active_workflows:
            return None

        tasks = self.active_workflows[workflow_id]

        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
        failed_tasks = len([t for t in tasks if t.status == TaskStatus.FAILED])

        overall_progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        return {
            "workflow_id": workflow_id,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "progress": overall_progress,
            "status": "completed" if completed_tasks == total_tasks else "in_progress",
            "tasks": [
                {
                    "id": task.id,
                    "name": task.definition_id,
                    "status": task.status,
                    "progress": task.progress,
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None
                }
                for task in tasks
            ]
        }

    def get_organization_workflows(self, organization_id: str) -> List[Dict[str, Any]]:
        """Get all workflows for an organization"""
        org_workflows = []

        for workflow_id, tasks in self.active_workflows.items():
            if tasks and tasks[0].organization_id == organization_id:
                status = self.get_workflow_status(workflow_id)
                if status:
                    org_workflows.append(status)

        return org_workflows

# Global task automation engine instance
task_engine: Optional[TaskAutomationEngine] = None

def get_task_engine() -> TaskAutomationEngine:
    """Get the global task automation engine instance"""
    global task_engine
    if task_engine is None:
        from .websocket_manager import get_websocket_manager
        from .notifications import get_notification_service

        task_engine = TaskAutomationEngine(
            get_websocket_manager(),
            get_notification_service()
        )
    return task_engine