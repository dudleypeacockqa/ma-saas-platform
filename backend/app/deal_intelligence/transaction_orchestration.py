"""
Transaction Orchestration Hub - Advanced workflow orchestration and collaboration
Manages complex M&A transaction workflows with multi-party coordination
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json
import uuid
from abc import ABC, abstractmethod

# Data Models and Enums
class WorkflowStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class StakeholderRole(Enum):
    DEAL_LEAD = "deal_lead"
    INVESTMENT_COMMITTEE = "investment_committee"
    LEGAL_COUNSEL = "legal_counsel"
    TAX_ADVISOR = "tax_advisor"
    FINANCIAL_ADVISOR = "financial_advisor"
    INTEGRATION_LEAD = "integration_lead"
    COMPLIANCE_OFFICER = "compliance_officer"
    BOARD_MEMBER = "board_member"

class CommunicationChannel(Enum):
    EMAIL = "email"
    VIDEO_CONFERENCE = "video_conference"
    DOCUMENT_SHARING = "document_sharing"
    INSTANT_MESSAGE = "instant_message"
    PROJECT_PORTAL = "project_portal"

@dataclass
class WorkflowTask:
    """Individual task within a workflow"""
    task_id: str
    name: str
    description: str
    assignee: str
    stakeholder_role: StakeholderRole
    priority: TaskPriority
    status: TaskStatus = TaskStatus.PENDING
    due_date: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    completion_percentage: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

@dataclass
class WorkflowStage:
    """Stage in the transaction workflow"""
    stage_id: str
    name: str
    description: str
    tasks: List[WorkflowTask] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    estimated_duration_days: int = 30
    status: WorkflowStatus = WorkflowStatus.DRAFT

@dataclass
class TransactionWorkflow:
    """Complete transaction workflow definition"""
    workflow_id: str
    deal_id: str
    name: str
    description: str
    stages: List[WorkflowStage] = field(default_factory=list)
    stakeholders: Dict[str, StakeholderRole] = field(default_factory=dict)
    status: WorkflowStatus = WorkflowStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    expected_completion: Optional[datetime] = None
    actual_completion: Optional[datetime] = None

@dataclass
class CollaborationEvent:
    """Collaboration and communication event"""
    event_id: str
    workflow_id: str
    event_type: CommunicationChannel
    participants: List[str]
    subject: str
    content: str
    attachments: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None

class WorkflowEngine:
    """Advanced workflow orchestration engine"""

    def __init__(self):
        self.workflows = {}
        self.workflow_templates = {}
        self.active_workflows = set()
        self.task_dependencies = defaultdict(set)
        self.workflow_metrics = defaultdict(dict)

    def create_workflow_template(self, template_id: str, name: str,
                                deal_type: str) -> bool:
        """Create reusable workflow template"""
        try:
            template = {
                "template_id": template_id,
                "name": name,
                "deal_type": deal_type,
                "stages": self._get_default_stages(deal_type),
                "estimated_duration": self._estimate_template_duration(deal_type),
                "created_at": datetime.now()
            }
            self.workflow_templates[template_id] = template
            return True
        except Exception:
            return False

    def create_workflow_from_template(self, deal_id: str, template_id: str,
                                    customizations: Optional[Dict[str, Any]] = None) -> str:
        """Create workflow instance from template"""
        if template_id not in self.workflow_templates:
            raise ValueError(f"Template {template_id} not found")

        template = self.workflow_templates[template_id]
        workflow_id = str(uuid.uuid4())

        # Create workflow stages from template
        stages = []
        for stage_def in template["stages"]:
            stage = WorkflowStage(
                stage_id=str(uuid.uuid4()),
                name=stage_def["name"],
                description=stage_def["description"],
                estimated_duration_days=stage_def["duration"]
            )

            # Create tasks for each stage
            for task_def in stage_def["tasks"]:
                task = WorkflowTask(
                    task_id=str(uuid.uuid4()),
                    name=task_def["name"],
                    description=task_def["description"],
                    assignee="",  # To be assigned
                    stakeholder_role=StakeholderRole(task_def["role"]),
                    priority=TaskPriority(task_def["priority"]),
                    estimated_hours=task_def["hours"],
                    deliverables=task_def["deliverables"]
                )
                stage.tasks.append(task)

            stages.append(stage)

        # Apply customizations if provided
        if customizations:
            stages = self._apply_customizations(stages, customizations)

        workflow = TransactionWorkflow(
            workflow_id=workflow_id,
            deal_id=deal_id,
            name=f"{template['name']} - {deal_id}",
            description=f"Workflow for deal {deal_id}",
            stages=stages
        )

        self.workflows[workflow_id] = workflow
        return workflow_id

    def start_workflow(self, workflow_id: str, stakeholder_assignments: Dict[str, str]) -> bool:
        """Start workflow execution"""
        if workflow_id not in self.workflows:
            return False

        workflow = self.workflows[workflow_id]
        workflow.status = WorkflowStatus.ACTIVE
        workflow.started_at = datetime.now()

        # Assign stakeholders to tasks
        self._assign_stakeholders(workflow, stakeholder_assignments)

        # Calculate expected completion
        total_duration = sum(stage.estimated_duration_days for stage in workflow.stages)
        workflow.expected_completion = datetime.now() + timedelta(days=total_duration)

        # Initialize first stage
        if workflow.stages:
            workflow.stages[0].status = WorkflowStatus.ACTIVE
            self._initialize_stage_tasks(workflow.stages[0])

        self.active_workflows.add(workflow_id)
        return True

    def update_task_progress(self, workflow_id: str, task_id: str,
                           status: TaskStatus, completion_percentage: float = 0,
                           actual_hours: float = 0) -> bool:
        """Update task progress and status"""
        if workflow_id not in self.workflows:
            return False

        workflow = self.workflows[workflow_id]

        # Find and update task
        for stage in workflow.stages:
            for task in stage.tasks:
                if task.task_id == task_id:
                    task.status = status
                    task.completion_percentage = completion_percentage
                    task.actual_hours = actual_hours

                    if status == TaskStatus.COMPLETED:
                        task.completed_at = datetime.now()
                        task.completion_percentage = 100.0

                    # Check if stage is complete
                    self._check_stage_completion(workflow, stage)
                    return True

        return False

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get comprehensive workflow status"""
        if workflow_id not in self.workflows:
            return {}

        workflow = self.workflows[workflow_id]

        # Calculate overall progress
        total_tasks = sum(len(stage.tasks) for stage in workflow.stages)
        completed_tasks = sum(
            1 for stage in workflow.stages
            for task in stage.tasks
            if task.status == TaskStatus.COMPLETED
        )

        overall_progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        # Get current stage
        current_stage = None
        for stage in workflow.stages:
            if stage.status == WorkflowStatus.ACTIVE:
                current_stage = stage
                break

        # Calculate metrics
        metrics = self._calculate_workflow_metrics(workflow)

        return {
            "workflow_id": workflow_id,
            "deal_id": workflow.deal_id,
            "name": workflow.name,
            "status": workflow.status.value,
            "overall_progress": round(overall_progress, 2),
            "current_stage": current_stage.name if current_stage else None,
            "total_stages": len(workflow.stages),
            "completed_stages": sum(1 for s in workflow.stages if s.status == WorkflowStatus.COMPLETED),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "expected_completion": workflow.expected_completion.isoformat() if workflow.expected_completion else None,
            "metrics": metrics
        }

    def get_active_tasks(self, assignee: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get active tasks, optionally filtered by assignee"""
        active_tasks = []

        for workflow_id in self.active_workflows:
            workflow = self.workflows[workflow_id]
            for stage in workflow.stages:
                if stage.status == WorkflowStatus.ACTIVE:
                    for task in stage.tasks:
                        if task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
                            if assignee is None or task.assignee == assignee:
                                active_tasks.append({
                                    "task_id": task.task_id,
                                    "workflow_id": workflow_id,
                                    "deal_id": workflow.deal_id,
                                    "name": task.name,
                                    "description": task.description,
                                    "assignee": task.assignee,
                                    "role": task.stakeholder_role.value,
                                    "priority": task.priority.value,
                                    "status": task.status.value,
                                    "due_date": task.due_date.isoformat() if task.due_date else None,
                                    "completion_percentage": task.completion_percentage,
                                    "estimated_hours": task.estimated_hours,
                                    "actual_hours": task.actual_hours
                                })

        # Sort by priority and due date
        active_tasks.sort(key=lambda x: (
            self._priority_sort_key(x["priority"]),
            x["due_date"] or "9999-12-31"
        ))

        return active_tasks

    def _get_default_stages(self, deal_type: str) -> List[Dict[str, Any]]:
        """Get default stages for deal type"""
        base_stages = [
            {
                "name": "Deal Origination & Initial Screening",
                "description": "Initial deal identification and preliminary assessment",
                "duration": 14,
                "tasks": [
                    {
                        "name": "Market opportunity analysis",
                        "description": "Analyze market opportunity and competitive landscape",
                        "role": "deal_lead",
                        "priority": "high",
                        "hours": 16,
                        "deliverables": ["Market analysis report"]
                    },
                    {
                        "name": "Initial financial screening",
                        "description": "Preliminary financial assessment",
                        "role": "financial_advisor",
                        "priority": "high",
                        "hours": 12,
                        "deliverables": ["Financial screening memo"]
                    }
                ]
            },
            {
                "name": "Preliminary Due Diligence",
                "description": "High-level due diligence and initial valuation",
                "duration": 21,
                "tasks": [
                    {
                        "name": "Business model analysis",
                        "description": "Detailed analysis of target's business model",
                        "role": "deal_lead",
                        "priority": "high",
                        "hours": 24,
                        "deliverables": ["Business model assessment"]
                    },
                    {
                        "name": "Legal structure review",
                        "description": "Review of legal structure and potential issues",
                        "role": "legal_counsel",
                        "priority": "medium",
                        "hours": 16,
                        "deliverables": ["Legal structure memo"]
                    }
                ]
            },
            {
                "name": "Formal Due Diligence",
                "description": "Comprehensive due diligence across all areas",
                "duration": 45,
                "tasks": [
                    {
                        "name": "Financial due diligence",
                        "description": "Comprehensive financial analysis",
                        "role": "financial_advisor",
                        "priority": "critical",
                        "hours": 80,
                        "deliverables": ["Financial DD report", "Quality of earnings analysis"]
                    },
                    {
                        "name": "Commercial due diligence",
                        "description": "Market and commercial viability assessment",
                        "role": "deal_lead",
                        "priority": "high",
                        "hours": 60,
                        "deliverables": ["Commercial DD report"]
                    },
                    {
                        "name": "Legal due diligence",
                        "description": "Comprehensive legal review",
                        "role": "legal_counsel",
                        "priority": "critical",
                        "hours": 70,
                        "deliverables": ["Legal DD report", "Risk matrix"]
                    }
                ]
            },
            {
                "name": "Valuation & Structuring",
                "description": "Deal valuation and structure optimization",
                "duration": 21,
                "tasks": [
                    {
                        "name": "Valuation modeling",
                        "description": "Build comprehensive valuation models",
                        "role": "financial_advisor",
                        "priority": "critical",
                        "hours": 40,
                        "deliverables": ["Valuation model", "Sensitivity analysis"]
                    },
                    {
                        "name": "Deal structure optimization",
                        "description": "Optimize transaction structure",
                        "role": "tax_advisor",
                        "priority": "high",
                        "hours": 24,
                        "deliverables": ["Structure recommendation"]
                    }
                ]
            },
            {
                "name": "Negotiation & Documentation",
                "description": "Term negotiation and legal documentation",
                "duration": 30,
                "tasks": [
                    {
                        "name": "Term sheet negotiation",
                        "description": "Negotiate key deal terms",
                        "role": "deal_lead",
                        "priority": "critical",
                        "hours": 32,
                        "deliverables": ["Executed term sheet"]
                    },
                    {
                        "name": "Legal documentation",
                        "description": "Draft and negotiate definitive agreements",
                        "role": "legal_counsel",
                        "priority": "critical",
                        "hours": 60,
                        "deliverables": ["Purchase agreement", "Disclosure schedules"]
                    }
                ]
            },
            {
                "name": "Closing & Integration Planning",
                "description": "Transaction closing and integration preparation",
                "duration": 14,
                "tasks": [
                    {
                        "name": "Closing coordination",
                        "description": "Coordinate transaction closing",
                        "role": "deal_lead",
                        "priority": "critical",
                        "hours": 20,
                        "deliverables": ["Closing checklist", "Closing memorandum"]
                    },
                    {
                        "name": "Integration planning",
                        "description": "Develop post-close integration plan",
                        "role": "integration_lead",
                        "priority": "high",
                        "hours": 40,
                        "deliverables": ["Integration plan", "Day 1 readiness assessment"]
                    }
                ]
            }
        ]

        return base_stages

    def _estimate_template_duration(self, deal_type: str) -> int:
        """Estimate total template duration"""
        # Deal type specific adjustments
        base_duration = 145  # days

        duration_adjustments = {
            "asset_purchase": -30,
            "acquisition": 0,
            "merger": 45,
            "joint_venture": -15
        }

        return base_duration + duration_adjustments.get(deal_type, 0)

    def _apply_customizations(self, stages: List[WorkflowStage],
                            customizations: Dict[str, Any]) -> List[WorkflowStage]:
        """Apply workflow customizations"""
        # Apply customizations like additional tasks, modified timelines, etc.
        if "additional_tasks" in customizations:
            for task_def in customizations["additional_tasks"]:
                # Add to appropriate stage
                stage_name = task_def.get("stage", "Formal Due Diligence")
                for stage in stages:
                    if stage.name == stage_name:
                        task = WorkflowTask(
                            task_id=str(uuid.uuid4()),
                            name=task_def["name"],
                            description=task_def["description"],
                            assignee="",
                            stakeholder_role=StakeholderRole(task_def["role"]),
                            priority=TaskPriority(task_def["priority"]),
                            estimated_hours=task_def.get("hours", 8)
                        )
                        stage.tasks.append(task)
                        break

        return stages

    def _assign_stakeholders(self, workflow: TransactionWorkflow,
                           assignments: Dict[str, str]) -> None:
        """Assign stakeholders to workflow tasks"""
        # assignments maps role -> person_id
        for stage in workflow.stages:
            for task in stage.tasks:
                role_key = task.stakeholder_role.value
                if role_key in assignments:
                    task.assignee = assignments[role_key]

        workflow.stakeholders = assignments

    def _initialize_stage_tasks(self, stage: WorkflowStage) -> None:
        """Initialize tasks for an active stage"""
        for task in stage.tasks:
            if not task.dependencies:  # No dependencies, can start immediately
                task.status = TaskStatus.PENDING
                # Set due date based on stage timeline
                task.due_date = datetime.now() + timedelta(days=stage.estimated_duration_days)

    def _check_stage_completion(self, workflow: TransactionWorkflow,
                              stage: WorkflowStage) -> None:
        """Check if stage is complete and advance workflow"""
        # Check if all tasks in stage are complete
        all_complete = all(task.status == TaskStatus.COMPLETED for task in stage.tasks)

        if all_complete:
            stage.status = WorkflowStatus.COMPLETED

            # Find next stage to activate
            current_stage_index = workflow.stages.index(stage)
            if current_stage_index + 1 < len(workflow.stages):
                next_stage = workflow.stages[current_stage_index + 1]
                next_stage.status = WorkflowStatus.ACTIVE
                self._initialize_stage_tasks(next_stage)
            else:
                # All stages complete
                workflow.status = WorkflowStatus.COMPLETED
                workflow.actual_completion = datetime.now()
                if workflow.workflow_id in self.active_workflows:
                    self.active_workflows.remove(workflow.workflow_id)

    def _calculate_workflow_metrics(self, workflow: TransactionWorkflow) -> Dict[str, Any]:
        """Calculate workflow performance metrics"""
        if not workflow.started_at:
            return {}

        # Time metrics
        elapsed_days = (datetime.now() - workflow.started_at).days
        expected_days = (workflow.expected_completion - workflow.started_at).days if workflow.expected_completion else 0

        # Progress metrics
        total_hours_estimated = sum(
            task.estimated_hours
            for stage in workflow.stages
            for task in stage.tasks
        )
        total_hours_actual = sum(
            task.actual_hours
            for stage in workflow.stages
            for task in stage.tasks
        )

        # Efficiency metrics
        schedule_variance = elapsed_days - expected_days if expected_days > 0 else 0
        effort_variance = total_hours_actual - total_hours_estimated if total_hours_estimated > 0 else 0

        return {
            "elapsed_days": elapsed_days,
            "expected_days": expected_days,
            "schedule_variance_days": schedule_variance,
            "total_estimated_hours": total_hours_estimated,
            "total_actual_hours": total_hours_actual,
            "effort_variance_hours": effort_variance,
            "efficiency_ratio": total_hours_estimated / total_hours_actual if total_hours_actual > 0 else 0
        }

    def _priority_sort_key(self, priority: str) -> int:
        """Get sort key for priority"""
        priority_map = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        return priority_map.get(priority, 2)

class CollaborationHub:
    """Advanced collaboration and communication management"""

    def __init__(self):
        self.events = defaultdict(list)
        self.communication_threads = defaultdict(list)
        self.stakeholder_profiles = {}
        self.notification_preferences = defaultdict(dict)

    def create_collaboration_event(self, workflow_id: str, event_type: CommunicationChannel,
                                 participants: List[str], subject: str, content: str,
                                 scheduled_at: Optional[datetime] = None,
                                 attachments: Optional[List[str]] = None) -> str:
        """Create collaboration event"""
        event_id = str(uuid.uuid4())

        event = CollaborationEvent(
            event_id=event_id,
            workflow_id=workflow_id,
            event_type=event_type,
            participants=participants,
            subject=subject,
            content=content,
            scheduled_at=scheduled_at,
            attachments=attachments or []
        )

        self.events[workflow_id].append(event)
        return event_id

    def schedule_stakeholder_meeting(self, workflow_id: str, participants: List[str],
                                   subject: str, agenda: str,
                                   scheduled_at: datetime) -> str:
        """Schedule stakeholder meeting"""
        return self.create_collaboration_event(
            workflow_id=workflow_id,
            event_type=CommunicationChannel.VIDEO_CONFERENCE,
            participants=participants,
            subject=subject,
            content=agenda,
            scheduled_at=scheduled_at
        )

    def create_document_sharing_event(self, workflow_id: str, participants: List[str],
                                    document_name: str, document_path: str,
                                    message: str = "") -> str:
        """Create document sharing event"""
        return self.create_collaboration_event(
            workflow_id=workflow_id,
            event_type=CommunicationChannel.DOCUMENT_SHARING,
            participants=participants,
            subject=f"Document Shared: {document_name}",
            content=message,
            attachments=[document_path]
        )

    def get_workflow_communications(self, workflow_id: str,
                                  event_type: Optional[CommunicationChannel] = None) -> List[Dict[str, Any]]:
        """Get communication history for workflow"""
        events = self.events.get(workflow_id, [])

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return [
            {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "participants": event.participants,
                "subject": event.subject,
                "content": event.content,
                "created_at": event.created_at.isoformat(),
                "scheduled_at": event.scheduled_at.isoformat() if event.scheduled_at else None,
                "attachments": event.attachments
            }
            for event in sorted(events, key=lambda x: x.created_at, reverse=True)
        ]

    def get_stakeholder_activity(self, stakeholder_id: str,
                               days_back: int = 30) -> Dict[str, Any]:
        """Get stakeholder activity summary"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        activity_summary = {
            "stakeholder_id": stakeholder_id,
            "period_days": days_back,
            "events_participated": 0,
            "meetings_attended": 0,
            "documents_shared": 0,
            "workflows_active": set(),
            "recent_events": []
        }

        for workflow_id, events in self.events.items():
            for event in events:
                if (stakeholder_id in event.participants and
                    event.created_at >= cutoff_date):

                    activity_summary["events_participated"] += 1
                    activity_summary["workflows_active"].add(workflow_id)

                    if event.event_type == CommunicationChannel.VIDEO_CONFERENCE:
                        activity_summary["meetings_attended"] += 1
                    elif event.event_type == CommunicationChannel.DOCUMENT_SHARING:
                        activity_summary["documents_shared"] += 1

                    activity_summary["recent_events"].append({
                        "workflow_id": workflow_id,
                        "event_type": event.event_type.value,
                        "subject": event.subject,
                        "created_at": event.created_at.isoformat()
                    })

        activity_summary["workflows_active"] = len(activity_summary["workflows_active"])
        activity_summary["recent_events"] = sorted(
            activity_summary["recent_events"],
            key=lambda x: x["created_at"],
            reverse=True
        )[:10]  # Last 10 events

        return activity_summary

class TransactionOrchestrator:
    """Main transaction orchestration hub"""

    def __init__(self):
        self.workflow_engine = WorkflowEngine()
        self.collaboration_hub = CollaborationHub()
        self.orchestration_metrics = defaultdict(dict)

    async def orchestrate_transaction(self, deal_id: str, deal_type: str,
                                    stakeholder_assignments: Dict[str, str],
                                    customizations: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Orchestrate complete transaction workflow"""

        # Create workflow from template
        template_id = f"standard_{deal_type}"
        if template_id not in self.workflow_engine.workflow_templates:
            # Create standard template if it doesn't exist
            self.workflow_engine.create_workflow_template(template_id, f"Standard {deal_type.title()}", deal_type)

        workflow_id = self.workflow_engine.create_workflow_from_template(
            deal_id, template_id, customizations
        )

        # Start workflow
        workflow_started = self.workflow_engine.start_workflow(workflow_id, stakeholder_assignments)

        if not workflow_started:
            raise RuntimeError("Failed to start workflow")

        # Create initial collaboration events
        await self._setup_initial_collaboration(workflow_id, stakeholder_assignments)

        # Get initial status
        status = self.workflow_engine.get_workflow_status(workflow_id)

        return {
            "workflow_id": workflow_id,
            "orchestration_status": "initiated",
            "workflow_status": status,
            "initial_tasks": self.workflow_engine.get_active_tasks(),
            "collaboration_setup": "completed"
        }

    async def get_orchestration_dashboard(self, stakeholder_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive orchestration dashboard"""

        # Get all active workflows
        active_workflows = []
        for workflow_id in self.workflow_engine.active_workflows:
            status = self.workflow_engine.get_workflow_status(workflow_id)
            active_workflows.append(status)

        # Get active tasks
        active_tasks = self.workflow_engine.get_active_tasks(stakeholder_id)

        # Get collaboration summary
        collaboration_summary = self._get_collaboration_summary(stakeholder_id)

        # Calculate performance metrics
        performance_metrics = self._calculate_orchestration_metrics()

        return {
            "dashboard_timestamp": datetime.now().isoformat(),
            "stakeholder_id": stakeholder_id,
            "active_workflows": active_workflows,
            "active_tasks_count": len(active_tasks),
            "active_tasks": active_tasks[:10],  # Top 10 tasks
            "collaboration_summary": collaboration_summary,
            "performance_metrics": performance_metrics,
            "alerts": self._get_workflow_alerts()
        }

    async def update_workflow_progress(self, workflow_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update workflow progress with multiple task updates"""

        results = []
        for task_update in updates.get("task_updates", []):
            success = self.workflow_engine.update_task_progress(
                workflow_id=workflow_id,
                task_id=task_update["task_id"],
                status=TaskStatus(task_update["status"]),
                completion_percentage=task_update.get("completion_percentage", 0),
                actual_hours=task_update.get("actual_hours", 0)
            )
            results.append({
                "task_id": task_update["task_id"],
                "update_success": success
            })

        # Create progress update communication
        if updates.get("progress_message"):
            self.collaboration_hub.create_collaboration_event(
                workflow_id=workflow_id,
                event_type=CommunicationChannel.PROJECT_PORTAL,
                participants=updates.get("notify_stakeholders", []),
                subject="Workflow Progress Update",
                content=updates["progress_message"]
            )

        updated_status = self.workflow_engine.get_workflow_status(workflow_id)

        return {
            "workflow_id": workflow_id,
            "update_results": results,
            "updated_status": updated_status
        }

    async def _setup_initial_collaboration(self, workflow_id: str,
                                         stakeholders: Dict[str, str]) -> None:
        """Setup initial collaboration structure"""

        # Create kickoff meeting
        all_participants = list(stakeholders.values())
        self.collaboration_hub.schedule_stakeholder_meeting(
            workflow_id=workflow_id,
            participants=all_participants,
            subject="Transaction Kickoff Meeting",
            agenda="Review transaction overview, timeline, and stakeholder responsibilities",
            scheduled_at=datetime.now() + timedelta(days=2)
        )

        # Create initial project communication
        self.collaboration_hub.create_collaboration_event(
            workflow_id=workflow_id,
            event_type=CommunicationChannel.PROJECT_PORTAL,
            participants=all_participants,
            subject="Transaction Workflow Initiated",
            content="Transaction workflow has been initiated. Please review assigned tasks and timeline."
        )

    def _get_collaboration_summary(self, stakeholder_id: Optional[str]) -> Dict[str, Any]:
        """Get collaboration activity summary"""
        if stakeholder_id:
            return self.collaboration_hub.get_stakeholder_activity(stakeholder_id)
        else:
            # Global collaboration summary
            total_events = sum(len(events) for events in self.collaboration_hub.events.values())
            active_workflows = len(self.workflow_engine.active_workflows)

            return {
                "total_collaboration_events": total_events,
                "active_workflows": active_workflows,
                "recent_activity": "summary"  # Would contain actual summary
            }

    def _calculate_orchestration_metrics(self) -> Dict[str, Any]:
        """Calculate overall orchestration performance metrics"""

        total_workflows = len(self.workflow_engine.workflows)
        active_workflows = len(self.workflow_engine.active_workflows)
        completed_workflows = sum(
            1 for w in self.workflow_engine.workflows.values()
            if w.status == WorkflowStatus.COMPLETED
        )

        # Calculate average completion time for completed workflows
        completed_durations = []
        for workflow in self.workflow_engine.workflows.values():
            if workflow.status == WorkflowStatus.COMPLETED and workflow.started_at and workflow.actual_completion:
                duration = (workflow.actual_completion - workflow.started_at).days
                completed_durations.append(duration)

        avg_completion_days = sum(completed_durations) / len(completed_durations) if completed_durations else 0

        return {
            "total_workflows": total_workflows,
            "active_workflows": active_workflows,
            "completed_workflows": completed_workflows,
            "completion_rate": completed_workflows / total_workflows if total_workflows > 0 else 0,
            "average_completion_days": round(avg_completion_days, 1),
            "orchestration_efficiency": self._calculate_efficiency_score()
        }

    def _calculate_efficiency_score(self) -> float:
        """Calculate orchestration efficiency score"""
        # Simplified efficiency calculation
        base_score = 75.0

        # Adjust based on workflow completion rates, on-time delivery, etc.
        # This would be more sophisticated in a real implementation

        return base_score

    def _get_workflow_alerts(self) -> List[Dict[str, Any]]:
        """Get workflow alerts and notifications"""
        alerts = []

        for workflow_id in self.workflow_engine.active_workflows:
            workflow = self.workflow_engine.workflows[workflow_id]

            # Check for overdue tasks
            for stage in workflow.stages:
                if stage.status == WorkflowStatus.ACTIVE:
                    for task in stage.tasks:
                        if (task.due_date and task.due_date < datetime.now() and
                            task.status != TaskStatus.COMPLETED):
                            alerts.append({
                                "type": "overdue_task",
                                "severity": "high",
                                "workflow_id": workflow_id,
                                "task_id": task.task_id,
                                "message": f"Task '{task.name}' is overdue",
                                "assignee": task.assignee
                            })

            # Check for workflow delays
            if (workflow.expected_completion and
                workflow.expected_completion < datetime.now() and
                workflow.status == WorkflowStatus.ACTIVE):
                alerts.append({
                    "type": "workflow_delay",
                    "severity": "medium",
                    "workflow_id": workflow_id,
                    "message": f"Workflow '{workflow.name}' is behind schedule"
                })

        return alerts

# Service instance management
_transaction_orchestrator_instance = None

def get_transaction_orchestrator() -> TransactionOrchestrator:
    """Get singleton transaction orchestrator instance"""
    global _transaction_orchestrator_instance
    if _transaction_orchestrator_instance is None:
        _transaction_orchestrator_instance = TransactionOrchestrator()
    return _transaction_orchestrator_instance