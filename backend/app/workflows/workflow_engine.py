"""
Workflow Engine - Sprint 14
Advanced workflow design, execution, and management for M&A processes
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

class WorkflowStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class NodeType(Enum):
    START = "start"
    END = "end"
    TASK = "task"
    DECISION = "decision"
    PARALLEL = "parallel"
    MERGE = "merge"
    DELAY = "delay"
    WEBHOOK = "webhook"
    APPROVAL = "approval"
    NOTIFICATION = "notification"

class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WAITING = "waiting"

class TriggerType(Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"
    API = "api"
    WEBHOOK = "webhook"
    FILE_UPLOAD = "file_upload"
    STATUS_CHANGE = "status_change"

@dataclass
class WorkflowNode:
    """Individual node in a workflow"""
    node_id: str
    name: str
    node_type: NodeType
    config: Dict[str, Any] = field(default_factory=dict)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, float] = field(default_factory=dict)

@dataclass
class WorkflowConnection:
    """Connection between workflow nodes"""
    connection_id: str
    from_node: str
    to_node: str
    condition: Optional[str] = None
    label: str = ""

@dataclass
class WorkflowDefinition:
    """Complete workflow definition"""
    workflow_id: str
    name: str
    description: str
    version: str
    nodes: List[WorkflowNode]
    connections: List[WorkflowConnection]
    triggers: List[Dict[str, Any]] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""

@dataclass
class WorkflowInstance:
    """Running instance of a workflow"""
    instance_id: str
    workflow_id: str
    status: WorkflowStatus
    context: Dict[str, Any] = field(default_factory=dict)
    current_nodes: List[str] = field(default_factory=list)
    completed_nodes: List[str] = field(default_factory=list)
    node_executions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    triggered_by: str = ""

@dataclass
class NodeExecution:
    """Execution details for a single node"""
    execution_id: str
    node_id: str
    instance_id: str
    status: ExecutionStatus
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0

class WorkflowBuilder:
    """Visual workflow builder and designer"""

    def __init__(self):
        self.workflows = {}
        self.templates = {}
        self._initialize_templates()

    def create_workflow(self, name: str, description: str = "") -> str:
        """Create a new workflow definition"""
        workflow_id = f"wf_{uuid.uuid4().hex[:8]}"

        workflow = WorkflowDefinition(
            workflow_id=workflow_id,
            name=name,
            description=description,
            version="1.0.0",
            nodes=[],
            connections=[]
        )

        self.workflows[workflow_id] = workflow
        return workflow_id

    def add_node(self, workflow_id: str, name: str, node_type: NodeType,
                 config: Optional[Dict[str, Any]] = None,
                 position: Optional[Dict[str, float]] = None) -> str:
        """Add a node to the workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        node_id = f"node_{uuid.uuid4().hex[:8]}"

        node = WorkflowNode(
            node_id=node_id,
            name=name,
            node_type=node_type,
            config=config or {},
            position=position or {"x": 0, "y": 0}
        )

        self.workflows[workflow_id].nodes.append(node)
        return node_id

    def connect_nodes(self, workflow_id: str, from_node: str, to_node: str,
                     condition: Optional[str] = None, label: str = "") -> str:
        """Connect two nodes in the workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        connection_id = f"conn_{uuid.uuid4().hex[:8]}"

        connection = WorkflowConnection(
            connection_id=connection_id,
            from_node=from_node,
            to_node=to_node,
            condition=condition,
            label=label
        )

        self.workflows[workflow_id].connections.append(connection)
        return connection_id

    def add_trigger(self, workflow_id: str, trigger_type: TriggerType,
                   config: Dict[str, Any]) -> bool:
        """Add a trigger to the workflow"""
        if workflow_id not in self.workflows:
            return False

        trigger = {
            "id": f"trigger_{uuid.uuid4().hex[:8]}",
            "type": trigger_type.value,
            "config": config,
            "enabled": True,
            "created_at": datetime.now().isoformat()
        }

        self.workflows[workflow_id].triggers.append(trigger)
        return True

    def validate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Validate workflow definition"""
        if workflow_id not in self.workflows:
            return {"valid": False, "errors": ["Workflow not found"]}

        workflow = self.workflows[workflow_id]
        errors = []
        warnings = []

        # Check for start and end nodes
        start_nodes = [n for n in workflow.nodes if n.node_type == NodeType.START]
        end_nodes = [n for n in workflow.nodes if n.node_type == NodeType.END]

        if not start_nodes:
            errors.append("Workflow must have at least one START node")
        if not end_nodes:
            warnings.append("Workflow should have at least one END node")

        # Check for orphaned nodes
        connected_nodes = set()
        for conn in workflow.connections:
            connected_nodes.add(conn.from_node)
            connected_nodes.add(conn.to_node)

        all_nodes = {n.node_id for n in workflow.nodes}
        orphaned = all_nodes - connected_nodes - {n.node_id for n in start_nodes}

        if orphaned:
            warnings.append(f"Orphaned nodes found: {list(orphaned)}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def export_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Export workflow definition"""
        if workflow_id not in self.workflows:
            return None

        workflow = self.workflows[workflow_id]

        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "description": workflow.description,
            "version": workflow.version,
            "nodes": [
                {
                    "node_id": n.node_id,
                    "name": n.name,
                    "type": n.node_type.value,
                    "config": n.config,
                    "position": n.position
                }
                for n in workflow.nodes
            ],
            "connections": [
                {
                    "connection_id": c.connection_id,
                    "from_node": c.from_node,
                    "to_node": c.to_node,
                    "condition": c.condition,
                    "label": c.label
                }
                for c in workflow.connections
            ],
            "triggers": workflow.triggers,
            "variables": workflow.variables,
            "settings": workflow.settings,
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat()
        }

    def _initialize_templates(self):
        """Initialize workflow templates"""

        # Deal Processing Template
        self.templates["deal_processing"] = {
            "name": "Deal Processing Workflow",
            "description": "Standard M&A deal processing workflow",
            "nodes": [
                {"name": "Start", "type": "start"},
                {"name": "Document Review", "type": "task"},
                {"name": "Financial Analysis", "type": "task"},
                {"name": "Legal Review", "type": "approval"},
                {"name": "Final Approval", "type": "approval"},
                {"name": "Complete", "type": "end"}
            ]
        }

        # Document Automation Template
        self.templates["document_automation"] = {
            "name": "Document Processing Automation",
            "description": "Automated document processing and routing",
            "nodes": [
                {"name": "Document Upload", "type": "start"},
                {"name": "Document Classification", "type": "task"},
                {"name": "Extract Metadata", "type": "task"},
                {"name": "Route to Team", "type": "decision"},
                {"name": "Notify Stakeholders", "type": "notification"},
                {"name": "Archive", "type": "end"}
            ]
        }

class WorkflowExecutor:
    """Executes workflow instances"""

    def __init__(self):
        self.active_instances = {}
        self.execution_queue = deque()
        self.node_handlers = {}
        self.execution_history = []
        self._register_default_handlers()

    async def start_workflow(self, workflow_definition: WorkflowDefinition,
                           context: Optional[Dict[str, Any]] = None,
                           triggered_by: str = "") -> str:
        """Start a new workflow instance"""
        instance_id = f"inst_{uuid.uuid4().hex[:8]}"

        # Find start nodes
        start_nodes = [n.node_id for n in workflow_definition.nodes
                      if n.node_type == NodeType.START]

        if not start_nodes:
            raise ValueError("Workflow has no start nodes")

        instance = WorkflowInstance(
            instance_id=instance_id,
            workflow_id=workflow_definition.workflow_id,
            status=WorkflowStatus.ACTIVE,
            context=context or {},
            current_nodes=start_nodes,
            triggered_by=triggered_by
        )

        self.active_instances[instance_id] = instance

        # Start executing from start nodes
        for node_id in start_nodes:
            await self._execute_node(instance_id, node_id)

        return instance_id

    async def _execute_node(self, instance_id: str, node_id: str):
        """Execute a single node"""
        if instance_id not in self.active_instances:
            return

        instance = self.active_instances[instance_id]
        workflow_definition = self._get_workflow_definition(instance.workflow_id)

        if not workflow_definition:
            return

        # Find the node
        node = next((n for n in workflow_definition.nodes if n.node_id == node_id), None)
        if not node:
            return

        # Create execution record
        execution_id = f"exec_{uuid.uuid4().hex[:8]}"
        execution = NodeExecution(
            execution_id=execution_id,
            node_id=node_id,
            instance_id=instance_id,
            status=ExecutionStatus.RUNNING
        )

        try:
            # Execute the node based on its type
            handler = self.node_handlers.get(node.node_type)
            if handler:
                result = await handler(node, instance, execution)
                execution.output_data = result or {}
                execution.status = ExecutionStatus.COMPLETED
            else:
                execution.status = ExecutionStatus.SKIPPED

            execution.completed_at = datetime.now()

            # Update instance
            instance.node_executions[node_id] = {
                "execution_id": execution_id,
                "status": execution.status.value,
                "completed_at": execution.completed_at.isoformat(),
                "output_data": execution.output_data
            }

            instance.completed_nodes.append(node_id)
            if node_id in instance.current_nodes:
                instance.current_nodes.remove(node_id)

            # Find next nodes to execute
            await self._process_next_nodes(instance_id, node_id)

        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.now()

            # Mark instance as failed
            instance.status = WorkflowStatus.FAILED
            instance.error_message = str(e)

    async def _process_next_nodes(self, instance_id: str, completed_node_id: str):
        """Process next nodes after a node completes"""
        instance = self.active_instances[instance_id]
        workflow_definition = self._get_workflow_definition(instance.workflow_id)

        if not workflow_definition:
            return

        # Find outgoing connections
        next_connections = [c for c in workflow_definition.connections
                          if c.from_node == completed_node_id]

        for connection in next_connections:
            # Check conditions
            if connection.condition:
                # Evaluate condition (simplified)
                if not self._evaluate_condition(connection.condition, instance.context):
                    continue

            # Add to current nodes and execute
            if connection.to_node not in instance.current_nodes:
                instance.current_nodes.append(connection.to_node)
                await self._execute_node(instance_id, connection.to_node)

        # Check if workflow is complete
        if not instance.current_nodes:
            instance.status = WorkflowStatus.COMPLETED
            instance.completed_at = datetime.now()

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a workflow condition"""
        # Simplified condition evaluation
        # In production, use a proper expression parser
        try:
            # Basic string replacement for context variables
            for key, value in context.items():
                condition = condition.replace(f"${key}", str(value))

            # Safe evaluation for basic conditions
            if "==" in condition or "!=" in condition or ">" in condition or "<" in condition:
                return eval(condition)

            return True
        except:
            return True

    def _get_workflow_definition(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Get workflow definition (placeholder)"""
        # In production, this would fetch from database
        return None

    def _register_default_handlers(self):
        """Register default node handlers"""

        async def start_handler(node, instance, execution):
            return {"started": True, "timestamp": datetime.now().isoformat()}

        async def end_handler(node, instance, execution):
            return {"completed": True, "timestamp": datetime.now().isoformat()}

        async def task_handler(node, instance, execution):
            # Simulate task execution
            await asyncio.sleep(0.1)
            return {"task_completed": True, "result": "success"}

        async def decision_handler(node, instance, execution):
            # Evaluate decision logic
            return {"decision": "proceed", "path": "default"}

        async def notification_handler(node, instance, execution):
            # Send notification
            return {"notification_sent": True, "recipients": node.config.get("recipients", [])}

        self.node_handlers = {
            NodeType.START: start_handler,
            NodeType.END: end_handler,
            NodeType.TASK: task_handler,
            NodeType.DECISION: decision_handler,
            NodeType.NOTIFICATION: notification_handler
        }

    def get_instance(self, instance_id: str) -> Optional[WorkflowInstance]:
        """Get workflow instance"""
        return self.active_instances.get(instance_id)

    def list_instances(self, status: Optional[WorkflowStatus] = None) -> List[WorkflowInstance]:
        """List workflow instances"""
        instances = list(self.active_instances.values())

        if status:
            instances = [i for i in instances if i.status == status]

        return instances

    async def pause_instance(self, instance_id: str) -> bool:
        """Pause a workflow instance"""
        if instance_id in self.active_instances:
            self.active_instances[instance_id].status = WorkflowStatus.PAUSED
            return True
        return False

    async def resume_instance(self, instance_id: str) -> bool:
        """Resume a paused workflow instance"""
        if instance_id in self.active_instances:
            instance = self.active_instances[instance_id]
            if instance.status == WorkflowStatus.PAUSED:
                instance.status = WorkflowStatus.ACTIVE

                # Resume execution of current nodes
                for node_id in instance.current_nodes:
                    await self._execute_node(instance_id, node_id)

                return True
        return False

class WorkflowEngine:
    """Central workflow engine coordinating all workflow operations"""

    def __init__(self):
        self.builder = WorkflowBuilder()
        self.executor = WorkflowExecutor()
        self.workflow_stats = {
            "workflows_created": 0,
            "instances_executed": 0,
            "nodes_processed": 0
        }

    async def create_workflow(self, name: str, description: str = "") -> str:
        """Create a new workflow"""
        workflow_id = self.builder.create_workflow(name, description)
        self.workflow_stats["workflows_created"] += 1
        return workflow_id

    async def execute_workflow(self, workflow_id: str,
                             context: Optional[Dict[str, Any]] = None) -> str:
        """Execute a workflow"""
        workflow_definition = self.builder.workflows.get(workflow_id)
        if not workflow_definition:
            raise ValueError(f"Workflow {workflow_id} not found")

        instance_id = await self.executor.start_workflow(
            workflow_definition, context
        )
        self.workflow_stats["instances_executed"] += 1
        return instance_id

    def get_workflows(self) -> List[Dict[str, Any]]:
        """Get all workflows"""
        return [
            self.builder.export_workflow(wf_id)
            for wf_id in self.builder.workflows.keys()
        ]

    def get_instances(self, status: Optional[WorkflowStatus] = None) -> List[WorkflowInstance]:
        """Get workflow instances"""
        return self.executor.list_instances(status)

    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get workflow statistics"""
        return {
            **self.workflow_stats,
            "active_instances": len([i for i in self.executor.active_instances.values()
                                   if i.status == WorkflowStatus.ACTIVE]),
            "total_workflows": len(self.builder.workflows)
        }

# Singleton instance
_workflow_engine_instance: Optional[WorkflowEngine] = None

def get_workflow_engine() -> WorkflowEngine:
    """Get the singleton Workflow Engine instance"""
    global _workflow_engine_instance
    if _workflow_engine_instance is None:
        _workflow_engine_instance = WorkflowEngine()
    return _workflow_engine_instance