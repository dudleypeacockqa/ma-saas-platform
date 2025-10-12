"""
Process Automation - Sprint 14
Automated business process management, task scheduling, and workflow automation for M&A operations
"""

from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
import json
import uuid
from collections import defaultdict, deque

class AutomationType(Enum):
    DOCUMENT_PROCESSING = "document_processing"
    DEAL_LIFECYCLE = "deal_lifecycle"
    NOTIFICATION = "notification"
    APPROVAL_WORKFLOW = "approval_workflow"
    DATA_SYNC = "data_sync"
    REPORT_GENERATION = "report_generation"
    COMPLIANCE_CHECK = "compliance_check"
    TASK_ASSIGNMENT = "task_assignment"

class TriggerEvent(Enum):
    DEAL_CREATED = "deal_created"
    DEAL_STATUS_CHANGED = "deal_status_changed"
    DOCUMENT_UPLOADED = "document_uploaded"
    APPROVAL_REQUIRED = "approval_required"
    DEADLINE_APPROACHING = "deadline_approaching"
    MILESTONE_REACHED = "milestone_reached"
    DATA_UPDATED = "data_updated"
    SCHEDULED_TIME = "scheduled_time"

class ActionType(Enum):
    SEND_EMAIL = "send_email"
    CREATE_TASK = "create_task"
    UPDATE_STATUS = "update_status"
    GENERATE_REPORT = "generate_report"
    CALL_API = "call_api"
    RUN_WORKFLOW = "run_workflow"
    SEND_NOTIFICATION = "send_notification"
    ASSIGN_USER = "assign_user"

class RuleStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    ERROR = "error"

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"

@dataclass
class AutomationCondition:
    """Condition for automation rule"""
    field: str
    operator: str  # eq, ne, gt, lt, contains, etc.
    value: Any
    condition_type: str = "simple"  # simple, complex, expression

@dataclass
class AutomationAction:
    """Action to execute in automation rule"""
    action_id: str
    action_type: ActionType
    config: Dict[str, Any] = field(default_factory=dict)
    delay: Optional[int] = None  # Delay in seconds
    retry_config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AutomationRule:
    """Automation rule definition"""
    rule_id: str
    name: str
    description: str
    automation_type: AutomationType
    trigger_event: TriggerEvent
    conditions: List[AutomationCondition] = field(default_factory=list)
    actions: List[AutomationAction] = field(default_factory=list)
    status: RuleStatus = RuleStatus.ACTIVE
    priority: int = 1
    execution_count: int = 0
    last_executed: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""

@dataclass
class AutomationExecution:
    """Record of automation rule execution"""
    execution_id: str
    rule_id: str
    trigger_data: Dict[str, Any]
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "running"
    actions_executed: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    execution_log: List[str] = field(default_factory=list)

@dataclass
class ScheduledTask:
    """Scheduled task definition"""
    task_id: str
    name: str
    description: str
    schedule_expression: str  # Cron-like expression
    action_config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    run_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class AutomatedTask:
    """Individual automated task"""
    task_id: str
    title: str
    description: str
    task_type: str
    priority: TaskPriority
    status: TaskStatus
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    automation_rule_id: Optional[str] = None

class ConditionEvaluator:
    """Evaluates automation conditions"""

    def evaluate_conditions(self, conditions: List[AutomationCondition],
                          data: Dict[str, Any]) -> bool:
        """Evaluate all conditions against data"""
        if not conditions:
            return True

        for condition in conditions:
            if not self._evaluate_single_condition(condition, data):
                return False

        return True

    def _evaluate_single_condition(self, condition: AutomationCondition,
                                 data: Dict[str, Any]) -> bool:
        """Evaluate a single condition"""
        field_value = self._get_field_value(data, condition.field)

        if condition.operator == "eq":
            return field_value == condition.value
        elif condition.operator == "ne":
            return field_value != condition.value
        elif condition.operator == "gt":
            return field_value > condition.value
        elif condition.operator == "lt":
            return field_value < condition.value
        elif condition.operator == "gte":
            return field_value >= condition.value
        elif condition.operator == "lte":
            return field_value <= condition.value
        elif condition.operator == "contains":
            return condition.value in str(field_value)
        elif condition.operator == "not_contains":
            return condition.value not in str(field_value)
        elif condition.operator == "in":
            return field_value in condition.value
        elif condition.operator == "not_in":
            return field_value not in condition.value
        elif condition.operator == "exists":
            return field_value is not None
        elif condition.operator == "not_exists":
            return field_value is None

        return False

    def _get_field_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get field value from nested data"""
        keys = field_path.split(".")
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current

class ActionExecutor:
    """Executes automation actions"""

    def __init__(self):
        self.action_handlers = {}
        self._register_default_handlers()

    async def execute_action(self, action: AutomationAction,
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single action"""
        if action.delay:
            await asyncio.sleep(action.delay)

        handler = self.action_handlers.get(action.action_type)
        if not handler:
            raise ValueError(f"No handler for action type: {action.action_type}")

        try:
            result = await handler(action, context)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _register_default_handlers(self):
        """Register default action handlers"""

        async def send_email_handler(action, context):
            config = action.config
            return {
                "email_sent": True,
                "recipients": config.get("recipients", []),
                "subject": config.get("subject", "")
            }

        async def create_task_handler(action, context):
            config = action.config
            return {
                "task_created": True,
                "task_id": f"task_{uuid.uuid4().hex[:8]}",
                "title": config.get("title", ""),
                "assigned_to": config.get("assigned_to")
            }

        async def update_status_handler(action, context):
            config = action.config
            return {
                "status_updated": True,
                "entity_id": config.get("entity_id"),
                "new_status": config.get("status")
            }

        async def send_notification_handler(action, context):
            config = action.config
            return {
                "notification_sent": True,
                "type": config.get("type", "info"),
                "message": config.get("message", "")
            }

        async def call_api_handler(action, context):
            config = action.config
            return {
                "api_called": True,
                "endpoint": config.get("endpoint"),
                "method": config.get("method", "GET")
            }

        self.action_handlers = {
            ActionType.SEND_EMAIL: send_email_handler,
            ActionType.CREATE_TASK: create_task_handler,
            ActionType.UPDATE_STATUS: update_status_handler,
            ActionType.SEND_NOTIFICATION: send_notification_handler,
            ActionType.CALL_API: call_api_handler
        }

class TaskScheduler:
    """Manages scheduled task execution"""

    def __init__(self):
        self.scheduled_tasks = {}
        self.scheduler_running = False
        self.execution_history = deque(maxlen=1000)

    async def create_scheduled_task(self, name: str, description: str,
                                  schedule_expression: str,
                                  action_config: Dict[str, Any]) -> str:
        """Create a new scheduled task"""
        task_id = f"sched_{uuid.uuid4().hex[:8]}"

        task = ScheduledTask(
            task_id=task_id,
            name=name,
            description=description,
            schedule_expression=schedule_expression,
            action_config=action_config,
            next_run=self._calculate_next_run(schedule_expression)
        )

        self.scheduled_tasks[task_id] = task
        return task_id

    def _calculate_next_run(self, schedule_expression: str) -> datetime:
        """Calculate next run time from schedule expression"""
        # Simplified schedule parsing
        # In production, use a proper cron parser
        now = datetime.now()

        if schedule_expression == "daily":
            return now + timedelta(days=1)
        elif schedule_expression == "hourly":
            return now + timedelta(hours=1)
        elif schedule_expression == "weekly":
            return now + timedelta(weeks=1)
        elif schedule_expression.startswith("every_"):
            # e.g., "every_30_minutes"
            parts = schedule_expression.split("_")
            if len(parts) == 3:
                interval = int(parts[1])
                unit = parts[2]
                if unit == "minutes":
                    return now + timedelta(minutes=interval)
                elif unit == "hours":
                    return now + timedelta(hours=interval)

        return now + timedelta(hours=1)  # Default

    async def start_scheduler(self):
        """Start the task scheduler"""
        self.scheduler_running = True

        while self.scheduler_running:
            await self._check_and_execute_tasks()
            await asyncio.sleep(60)  # Check every minute

    async def _check_and_execute_tasks(self):
        """Check and execute due tasks"""
        now = datetime.now()

        for task in self.scheduled_tasks.values():
            if (task.enabled and task.next_run and
                task.next_run <= now):

                await self._execute_scheduled_task(task)

    async def _execute_scheduled_task(self, task: ScheduledTask):
        """Execute a scheduled task"""
        execution_id = f"exec_{uuid.uuid4().hex[:8]}"

        try:
            # Execute the task action
            # This would integrate with ActionExecutor
            result = {"executed": True, "task_id": task.task_id}

            # Update task
            task.last_run = datetime.now()
            task.run_count += 1
            task.next_run = self._calculate_next_run(task.schedule_expression)

            # Log execution
            self.execution_history.append({
                "execution_id": execution_id,
                "task_id": task.task_id,
                "executed_at": task.last_run.isoformat(),
                "result": result
            })

        except Exception as e:
            # Log error
            self.execution_history.append({
                "execution_id": execution_id,
                "task_id": task.task_id,
                "executed_at": datetime.now().isoformat(),
                "error": str(e)
            })

    def stop_scheduler(self):
        """Stop the task scheduler"""
        self.scheduler_running = False

    def get_scheduled_tasks(self) -> List[ScheduledTask]:
        """Get all scheduled tasks"""
        return list(self.scheduled_tasks.values())

class ProcessAutomation:
    """Central process automation engine"""

    def __init__(self):
        self.automation_rules = {}
        self.condition_evaluator = ConditionEvaluator()
        self.action_executor = ActionExecutor()
        self.task_scheduler = TaskScheduler()
        self.automated_tasks = {}
        self.execution_history = deque(maxlen=1000)
        self.automation_stats = {
            "rules_created": 0,
            "executions_total": 0,
            "tasks_automated": 0
        }

    async def create_automation_rule(self, name: str, description: str,
                                   automation_type: AutomationType,
                                   trigger_event: TriggerEvent,
                                   conditions: List[AutomationCondition],
                                   actions: List[AutomationAction]) -> str:
        """Create a new automation rule"""
        rule_id = f"rule_{uuid.uuid4().hex[:8]}"

        rule = AutomationRule(
            rule_id=rule_id,
            name=name,
            description=description,
            automation_type=automation_type,
            trigger_event=trigger_event,
            conditions=conditions,
            actions=actions
        )

        self.automation_rules[rule_id] = rule
        self.automation_stats["rules_created"] += 1

        return rule_id

    async def trigger_automation(self, event: TriggerEvent,
                               event_data: Dict[str, Any]) -> List[str]:
        """Trigger automation rules for an event"""
        executed_rules = []

        # Find matching rules
        matching_rules = [
            rule for rule in self.automation_rules.values()
            if (rule.trigger_event == event and
                rule.status == RuleStatus.ACTIVE)
        ]

        # Sort by priority
        matching_rules.sort(key=lambda r: r.priority, reverse=True)

        for rule in matching_rules:
            # Evaluate conditions
            if self.condition_evaluator.evaluate_conditions(rule.conditions, event_data):
                execution_id = await self._execute_rule(rule, event_data)
                executed_rules.append(execution_id)

        return executed_rules

    async def _execute_rule(self, rule: AutomationRule,
                          trigger_data: Dict[str, Any]) -> str:
        """Execute an automation rule"""
        execution_id = f"exec_{uuid.uuid4().hex[:8]}"

        execution = AutomationExecution(
            execution_id=execution_id,
            rule_id=rule.rule_id,
            trigger_data=trigger_data,
            started_at=datetime.now()
        )

        try:
            # Execute actions sequentially
            for action in rule.actions:
                action_result = await self.action_executor.execute_action(
                    action, {"trigger_data": trigger_data, "rule": rule}
                )

                execution.actions_executed.append(action.action_id)
                execution.execution_log.append(
                    f"Action {action.action_id}: {action_result}"
                )

            execution.status = "completed"
            execution.completed_at = datetime.now()

            # Update rule statistics
            rule.execution_count += 1
            rule.last_executed = datetime.now()

            self.automation_stats["executions_total"] += 1

        except Exception as e:
            execution.status = "failed"
            execution.error_message = str(e)
            execution.completed_at = datetime.now()

        # Store execution record
        self.execution_history.append(execution)

        return execution_id

    async def create_automated_task(self, title: str, description: str,
                                  task_type: str, priority: TaskPriority,
                                  assigned_to: Optional[str] = None,
                                  due_date: Optional[datetime] = None,
                                  automation_rule_id: Optional[str] = None) -> str:
        """Create an automated task"""
        task_id = f"task_{uuid.uuid4().hex[:8]}"

        task = AutomatedTask(
            task_id=task_id,
            title=title,
            description=description,
            task_type=task_type,
            priority=priority,
            status=TaskStatus.PENDING,
            assigned_to=assigned_to,
            due_date=due_date,
            automation_rule_id=automation_rule_id
        )

        self.automated_tasks[task_id] = task
        self.automation_stats["tasks_automated"] += 1

        return task_id

    async def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """Update task status"""
        if task_id in self.automated_tasks:
            task = self.automated_tasks[task_id]
            task.status = status

            if status == TaskStatus.COMPLETED:
                task.completed_at = datetime.now()

            return True
        return False

    def get_automation_rules(self, automation_type: Optional[AutomationType] = None) -> List[AutomationRule]:
        """Get automation rules"""
        rules = list(self.automation_rules.values())

        if automation_type:
            rules = [r for r in rules if r.automation_type == automation_type]

        return rules

    def get_automated_tasks(self, status: Optional[TaskStatus] = None,
                          assigned_to: Optional[str] = None) -> List[AutomatedTask]:
        """Get automated tasks"""
        tasks = list(self.automated_tasks.values())

        if status:
            tasks = [t for t in tasks if t.status == status]

        if assigned_to:
            tasks = [t for t in tasks if t.assigned_to == assigned_to]

        return tasks

    def get_execution_history(self, rule_id: Optional[str] = None) -> List[AutomationExecution]:
        """Get execution history"""
        history = list(self.execution_history)

        if rule_id:
            history = [e for e in history if e.rule_id == rule_id]

        return history

    def get_automation_stats(self) -> Dict[str, Any]:
        """Get automation statistics"""
        return {
            **self.automation_stats,
            "active_rules": len([r for r in self.automation_rules.values()
                               if r.status == RuleStatus.ACTIVE]),
            "pending_tasks": len([t for t in self.automated_tasks.values()
                                if t.status == TaskStatus.PENDING]),
            "scheduled_tasks": len(self.task_scheduler.scheduled_tasks)
        }

    async def start_automation_engine(self):
        """Start the automation engine"""
        # Start task scheduler
        await self.task_scheduler.start_scheduler()

# Singleton instance
_process_automation_instance: Optional[ProcessAutomation] = None

def get_process_automation() -> ProcessAutomation:
    """Get the singleton Process Automation instance"""
    global _process_automation_instance
    if _process_automation_instance is None:
        _process_automation_instance = ProcessAutomation()
    return _process_automation_instance