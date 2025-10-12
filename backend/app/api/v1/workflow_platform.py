"""
Workflow Platform API - Sprint 14
RESTful API endpoints for workflow automation, integration management, and orchestration platform
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from app.workflows import (
    get_workflow_engine,
    get_integration_hub,
    get_process_automation,
    get_orchestration_platform
)
from app.workflows.workflow_engine import NodeType, TriggerType, WorkflowStatus
from app.workflows.integration_hub import IntegrationType, AuthType, SyncDirection
from app.workflows.process_automation import AutomationType, TriggerEvent, ActionType, TaskPriority
from app.workflows.orchestration_platform import ScalingType, LoadBalancingStrategy

router = APIRouter()

# Request/Response Models
class WorkflowCreateRequest(BaseModel):
    name: str
    description: str = ""

class NodeCreateRequest(BaseModel):
    name: str
    node_type: str
    config: Dict[str, Any] = {}
    position: Dict[str, float] = {"x": 0, "y": 0}

class ConnectionCreateRequest(BaseModel):
    from_node: str
    to_node: str
    condition: Optional[str] = None
    label: str = ""

class WorkflowExecuteRequest(BaseModel):
    context: Dict[str, Any] = {}

class IntegrationCreateRequest(BaseModel):
    name: str
    description: str
    integration_type: str
    endpoint_url: str
    auth_type: str
    auth_config: Dict[str, Any] = {}

class SyncCreateRequest(BaseModel):
    integration_id: str
    name: str
    direction: str
    source_endpoint: str
    target_endpoint: str
    mappings: List[Dict[str, Any]] = []

class AutomationRuleRequest(BaseModel):
    name: str
    description: str
    automation_type: str
    trigger_event: str
    conditions: List[Dict[str, Any]] = []
    actions: List[Dict[str, Any]] = []

class ServiceDeployRequest(BaseModel):
    name: str
    description: str
    image: str
    instance_count: int = 1
    resource_requirements: Dict[str, Any] = {}

# =============================================================================
# WORKFLOW ENGINE ENDPOINTS
# =============================================================================

@router.post("/workflows",
             summary="Create Workflow",
             description="Create a new workflow definition")
async def create_workflow(request: WorkflowCreateRequest) -> Dict[str, Any]:
    """Create a new workflow"""
    workflow_engine = get_workflow_engine()

    workflow_id = await workflow_engine.create_workflow(
        name=request.name,
        description=request.description
    )

    return {
        "success": True,
        "workflow_id": workflow_id,
        "message": "Workflow created successfully"
    }

@router.get("/workflows",
            summary="List Workflows",
            description="Get all workflow definitions")
async def list_workflows() -> Dict[str, Any]:
    """List all workflows"""
    workflow_engine = get_workflow_engine()
    workflows = workflow_engine.get_workflows()

    return {
        "success": True,
        "workflows": workflows,
        "count": len(workflows)
    }

@router.get("/workflows/{workflow_id}",
            summary="Get Workflow",
            description="Get workflow definition by ID")
async def get_workflow(workflow_id: str) -> Dict[str, Any]:
    """Get specific workflow"""
    workflow_engine = get_workflow_engine()
    workflow = workflow_engine.builder.export_workflow(workflow_id)

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return {
        "success": True,
        "workflow": workflow
    }

@router.post("/workflows/{workflow_id}/nodes",
             summary="Add Node",
             description="Add a node to workflow")
async def add_workflow_node(workflow_id: str, request: NodeCreateRequest) -> Dict[str, Any]:
    """Add a node to workflow"""
    workflow_engine = get_workflow_engine()

    try:
        node_type = NodeType(request.node_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid node type")

    node_id = workflow_engine.builder.add_node(
        workflow_id=workflow_id,
        name=request.name,
        node_type=node_type,
        config=request.config,
        position=request.position
    )

    return {
        "success": True,
        "node_id": node_id,
        "message": "Node added successfully"
    }

@router.post("/workflows/{workflow_id}/connections",
             summary="Connect Nodes",
             description="Connect two nodes in workflow")
async def connect_workflow_nodes(workflow_id: str, request: ConnectionCreateRequest) -> Dict[str, Any]:
    """Connect workflow nodes"""
    workflow_engine = get_workflow_engine()

    connection_id = workflow_engine.builder.connect_nodes(
        workflow_id=workflow_id,
        from_node=request.from_node,
        to_node=request.to_node,
        condition=request.condition,
        label=request.label
    )

    return {
        "success": True,
        "connection_id": connection_id,
        "message": "Nodes connected successfully"
    }

@router.post("/workflows/{workflow_id}/execute",
             summary="Execute Workflow",
             description="Execute a workflow with context data")
async def execute_workflow(workflow_id: str, request: WorkflowExecuteRequest) -> Dict[str, Any]:
    """Execute a workflow"""
    workflow_engine = get_workflow_engine()

    try:
        instance_id = await workflow_engine.execute_workflow(
            workflow_id=workflow_id,
            context=request.context
        )

        return {
            "success": True,
            "instance_id": instance_id,
            "message": "Workflow execution started"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/workflows/instances",
            summary="List Workflow Instances",
            description="Get workflow execution instances")
async def list_workflow_instances(status: Optional[str] = Query(None)) -> Dict[str, Any]:
    """List workflow instances"""
    workflow_engine = get_workflow_engine()

    workflow_status = None
    if status:
        try:
            workflow_status = WorkflowStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")

    instances = workflow_engine.get_instances(workflow_status)

    return {
        "success": True,
        "instances": [
            {
                "instance_id": i.instance_id,
                "workflow_id": i.workflow_id,
                "status": i.status.value,
                "started_at": i.started_at.isoformat(),
                "completed_at": i.completed_at.isoformat() if i.completed_at else None,
                "current_nodes": i.current_nodes,
                "completed_nodes": i.completed_nodes
            }
            for i in instances
        ],
        "count": len(instances)
    }

@router.get("/workflows/stats",
            summary="Workflow Statistics",
            description="Get workflow engine statistics")
async def get_workflow_stats() -> Dict[str, Any]:
    """Get workflow statistics"""
    workflow_engine = get_workflow_engine()
    stats = workflow_engine.get_workflow_stats()

    return {
        "success": True,
        "statistics": stats
    }

# =============================================================================
# INTEGRATION HUB ENDPOINTS
# =============================================================================

@router.post("/integrations",
             summary="Create Integration",
             description="Create a new external system integration")
async def create_integration(request: IntegrationCreateRequest) -> Dict[str, Any]:
    """Create a new integration"""
    integration_hub = get_integration_hub()

    try:
        integration_type = IntegrationType(request.integration_type)
        auth_type = AuthType(request.auth_type)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid integration or auth type")

    integration_id = await integration_hub.create_integration(
        name=request.name,
        description=request.description,
        integration_type=integration_type,
        endpoint_url=request.endpoint_url,
        auth_type=auth_type,
        auth_config=request.auth_config
    )

    return {
        "success": True,
        "integration_id": integration_id,
        "message": "Integration created successfully"
    }

@router.get("/integrations",
            summary="List Integrations",
            description="Get all configured integrations")
async def list_integrations() -> Dict[str, Any]:
    """List all integrations"""
    integration_hub = get_integration_hub()
    integrations = integration_hub.get_integrations()

    return {
        "success": True,
        "integrations": [
            {
                "integration_id": i.integration_id,
                "name": i.name,
                "description": i.description,
                "integration_type": i.integration_type.value,
                "auth_type": i.auth_type.value,
                "endpoint_url": i.endpoint_url,
                "created_at": i.created_at.isoformat()
            }
            for i in integrations
        ],
        "count": len(integrations)
    }

@router.post("/integrations/{integration_id}/test",
             summary="Test Integration",
             description="Test integration connection")
async def test_integration(integration_id: str) -> Dict[str, Any]:
    """Test integration connection"""
    integration_hub = get_integration_hub()

    result = await integration_hub.test_integration(integration_id)

    return {
        "success": result["success"],
        "test_result": result
    }

@router.post("/integrations/sync",
             summary="Create Data Sync",
             description="Create data synchronization configuration")
async def create_sync(request: SyncCreateRequest) -> Dict[str, Any]:
    """Create data synchronization"""
    integration_hub = get_integration_hub()

    try:
        direction = SyncDirection(request.direction)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid sync direction")

    # Convert mappings to DataMapping objects (simplified)
    from app.workflows.integration_hub import DataMapping
    mappings = [
        DataMapping(
            mapping_id=f"map_{i}",
            source_field=m.get("source_field", ""),
            target_field=m.get("target_field", ""),
            transformation=m.get("transformation"),
            default_value=m.get("default_value"),
            required=m.get("required", False)
        )
        for i, m in enumerate(request.mappings)
    ]

    sync_id = await integration_hub.create_sync(
        integration_id=request.integration_id,
        name=request.name,
        direction=direction,
        source_endpoint=request.source_endpoint,
        target_endpoint=request.target_endpoint,
        mappings=mappings
    )

    return {
        "success": True,
        "sync_id": sync_id,
        "message": "Data sync created successfully"
    }

@router.post("/integrations/sync/{sync_id}/execute",
             summary="Execute Sync",
             description="Execute data synchronization")
async def execute_sync(sync_id: str) -> Dict[str, Any]:
    """Execute data synchronization"""
    integration_hub = get_integration_hub()

    try:
        execution_id = await integration_hub.execute_sync(sync_id)

        return {
            "success": True,
            "execution_id": execution_id,
            "message": "Sync execution started"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/integrations/sync/executions",
            summary="List Sync Executions",
            description="Get sync execution history")
async def list_sync_executions(sync_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    """List sync executions"""
    integration_hub = get_integration_hub()
    executions = integration_hub.get_sync_executions(sync_id)

    return {
        "success": True,
        "executions": [
            {
                "execution_id": e.execution_id,
                "sync_id": e.sync_id,
                "status": e.status.value,
                "started_at": e.started_at.isoformat(),
                "completed_at": e.completed_at.isoformat() if e.completed_at else None,
                "records_processed": e.records_processed,
                "records_success": e.records_success,
                "records_failed": e.records_failed,
                "error_message": e.error_message
            }
            for e in executions
        ],
        "count": len(executions)
    }

@router.get("/integrations/stats",
            summary="Integration Statistics",
            description="Get integration hub statistics")
async def get_integration_stats() -> Dict[str, Any]:
    """Get integration statistics"""
    integration_hub = get_integration_hub()
    stats = integration_hub.get_integration_stats()

    return {
        "success": True,
        "statistics": stats
    }

# =============================================================================
# PROCESS AUTOMATION ENDPOINTS
# =============================================================================

@router.post("/automation/rules",
             summary="Create Automation Rule",
             description="Create a new automation rule")
async def create_automation_rule(request: AutomationRuleRequest) -> Dict[str, Any]:
    """Create automation rule"""
    process_automation = get_process_automation()

    try:
        automation_type = AutomationType(request.automation_type)
        trigger_event = TriggerEvent(request.trigger_event)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid automation or trigger type")

    # Convert conditions and actions (simplified)
    from app.workflows.process_automation import AutomationCondition, AutomationAction

    conditions = [
        AutomationCondition(
            field=c.get("field", ""),
            operator=c.get("operator", "eq"),
            value=c.get("value")
        )
        for c in request.conditions
    ]

    actions = [
        AutomationAction(
            action_id=f"action_{i}",
            action_type=ActionType(a.get("action_type", "send_email")),
            config=a.get("config", {})
        )
        for i, a in enumerate(request.actions)
    ]

    rule_id = await process_automation.create_automation_rule(
        name=request.name,
        description=request.description,
        automation_type=automation_type,
        trigger_event=trigger_event,
        conditions=conditions,
        actions=actions
    )

    return {
        "success": True,
        "rule_id": rule_id,
        "message": "Automation rule created successfully"
    }

@router.get("/automation/rules",
            summary="List Automation Rules",
            description="Get all automation rules")
async def list_automation_rules(automation_type: Optional[str] = Query(None)) -> Dict[str, Any]:
    """List automation rules"""
    process_automation = get_process_automation()

    automation_type_enum = None
    if automation_type:
        try:
            automation_type_enum = AutomationType(automation_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid automation type")

    rules = process_automation.get_automation_rules(automation_type_enum)

    return {
        "success": True,
        "rules": [
            {
                "rule_id": r.rule_id,
                "name": r.name,
                "description": r.description,
                "automation_type": r.automation_type.value,
                "trigger_event": r.trigger_event.value,
                "status": r.status.value,
                "execution_count": r.execution_count,
                "last_executed": r.last_executed.isoformat() if r.last_executed else None,
                "created_at": r.created_at.isoformat()
            }
            for r in rules
        ],
        "count": len(rules)
    }

@router.post("/automation/trigger",
             summary="Trigger Automation",
             description="Manually trigger automation for an event")
async def trigger_automation(
    event: str = Body(...),
    event_data: Dict[str, Any] = Body(...)
) -> Dict[str, Any]:
    """Trigger automation"""
    process_automation = get_process_automation()

    try:
        trigger_event = TriggerEvent(event)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid trigger event")

    executed_rules = await process_automation.trigger_automation(trigger_event, event_data)

    return {
        "success": True,
        "executed_rules": executed_rules,
        "count": len(executed_rules),
        "message": f"Triggered {len(executed_rules)} automation rules"
    }

@router.get("/automation/tasks",
            summary="List Automated Tasks",
            description="Get automated tasks")
async def list_automated_tasks(
    status: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """List automated tasks"""
    process_automation = get_process_automation()

    task_status = None
    if status:
        try:
            from app.workflows.process_automation import TaskStatus
            task_status = TaskStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid task status")

    tasks = process_automation.get_automated_tasks(task_status, assigned_to)

    return {
        "success": True,
        "tasks": [
            {
                "task_id": t.task_id,
                "title": t.title,
                "description": t.description,
                "task_type": t.task_type,
                "priority": t.priority.value,
                "status": t.status.value,
                "assigned_to": t.assigned_to,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "created_at": t.created_at.isoformat(),
                "completed_at": t.completed_at.isoformat() if t.completed_at else None
            }
            for t in tasks
        ],
        "count": len(tasks)
    }

@router.get("/automation/stats",
            summary="Automation Statistics",
            description="Get process automation statistics")
async def get_automation_stats() -> Dict[str, Any]:
    """Get automation statistics"""
    process_automation = get_process_automation()
    stats = process_automation.get_automation_stats()

    return {
        "success": True,
        "statistics": stats
    }

# =============================================================================
# ORCHESTRATION PLATFORM ENDPOINTS
# =============================================================================

@router.post("/orchestration/services",
             summary="Deploy Service",
             description="Deploy a new service to the platform")
async def deploy_service(request: ServiceDeployRequest) -> Dict[str, Any]:
    """Deploy a service"""
    orchestration_platform = get_orchestration_platform()

    # Create service definition
    from app.workflows.orchestration_platform import ServiceDefinition

    service_def = ServiceDefinition(
        service_id=f"svc_{request.name.lower()}",
        name=request.name,
        description=request.description,
        image=request.image,
        resource_requirements=request.resource_requirements
    )

    instance_ids = await orchestration_platform.deploy_service(
        service_def, request.instance_count
    )

    return {
        "success": True,
        "service_id": service_def.service_id,
        "instance_ids": instance_ids,
        "message": f"Service deployed with {len(instance_ids)} instances"
    }

@router.post("/orchestration/services/{service_name}/scale",
             summary="Scale Service",
             description="Scale service to target instance count")
async def scale_service(
    service_name: str,
    target_instances: int = Body(...)
) -> Dict[str, Any]:
    """Scale a service"""
    orchestration_platform = get_orchestration_platform()

    success = await orchestration_platform.scale_service(service_name, target_instances)

    return {
        "success": success,
        "message": f"Service {'scaled' if success else 'scaling failed'} to {target_instances} instances"
    }

@router.get("/orchestration/services",
            summary="List Services",
            description="Get all deployed services")
async def list_services() -> Dict[str, Any]:
    """List deployed services"""
    orchestration_platform = get_orchestration_platform()

    # Get service topology
    topology = orchestration_platform.service_mesh.get_service_topology()

    return {
        "success": True,
        "services": topology["topology"],
        "total_services": topology["services"],
        "total_instances": topology["instances"]
    }

@router.get("/orchestration/resources",
            summary="Resource Utilization",
            description="Get current resource utilization")
async def get_resource_utilization() -> Dict[str, Any]:
    """Get resource utilization"""
    orchestration_platform = get_orchestration_platform()

    utilization = orchestration_platform.resource_manager.get_resource_utilization()

    return {
        "success": True,
        "resource_utilization": utilization
    }

@router.post("/orchestration/tasks",
             summary="Submit Distributed Task",
             description="Submit a task for distributed execution")
async def submit_distributed_task(
    name: str = Body(...),
    task_type: str = Body(...),
    payload: Dict[str, Any] = Body(...),
    priority: str = Body("medium")
) -> Dict[str, Any]:
    """Submit distributed task"""
    orchestration_platform = get_orchestration_platform()

    try:
        from app.workflows.orchestration_platform import TaskPriority
        task_priority = TaskPriority(priority.upper())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task priority")

    task_id = await orchestration_platform.task_distributor.submit_task(
        name=name,
        task_type=task_type,
        payload=payload,
        priority=task_priority
    )

    return {
        "success": True,
        "task_id": task_id,
        "message": "Task submitted for execution"
    }

@router.get("/orchestration/tasks/{task_id}",
            summary="Get Task Status",
            description="Get status of a distributed task")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get task status"""
    orchestration_platform = get_orchestration_platform()

    task = orchestration_platform.task_distributor.get_task_status(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "success": True,
        "task": {
            "task_id": task.task_id,
            "name": task.name,
            "task_type": task.task_type,
            "priority": task.priority.name,
            "status": task.status.value,
            "assigned_instance": task.assigned_instance,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "result": task.result,
            "error_message": task.error_message
        }
    }

@router.get("/orchestration/status",
            summary="Platform Status",
            description="Get overall orchestration platform status")
async def get_platform_status() -> Dict[str, Any]:
    """Get platform status"""
    orchestration_platform = get_orchestration_platform()

    status = orchestration_platform.get_platform_status()

    return {
        "success": True,
        "platform_status": status
    }

# =============================================================================
# GENERAL WORKFLOW PLATFORM ENDPOINTS
# =============================================================================

@router.get("/platform/health",
            summary="Platform Health",
            description="Get overall workflow platform health")
async def get_platform_health() -> Dict[str, Any]:
    """Get platform health"""
    workflow_engine = get_workflow_engine()
    integration_hub = get_integration_hub()
    process_automation = get_process_automation()
    orchestration_platform = get_orchestration_platform()

    return {
        "success": True,
        "platform_health": {
            "workflow_engine": {
                "status": "operational",
                "statistics": workflow_engine.get_workflow_stats()
            },
            "integration_hub": {
                "status": "operational",
                "statistics": integration_hub.get_integration_stats()
            },
            "process_automation": {
                "status": "operational",
                "statistics": process_automation.get_automation_stats()
            },
            "orchestration_platform": {
                "status": "operational",
                "system_metrics": orchestration_platform.health_monitor.get_current_metrics()
            }
        },
        "overall_status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/platform/stats",
            summary="Platform Statistics",
            description="Get comprehensive platform statistics")
async def get_platform_stats() -> Dict[str, Any]:
    """Get comprehensive platform statistics"""
    workflow_engine = get_workflow_engine()
    integration_hub = get_integration_hub()
    process_automation = get_process_automation()
    orchestration_platform = get_orchestration_platform()

    return {
        "success": True,
        "platform_statistics": {
            "workflows": workflow_engine.get_workflow_stats(),
            "integrations": integration_hub.get_integration_stats(),
            "automation": process_automation.get_automation_stats(),
            "orchestration": orchestration_platform.get_platform_status()
        },
        "summary": {
            "total_workflows": workflow_engine.get_workflow_stats()["total_workflows"],
            "total_integrations": integration_hub.get_integration_stats()["active_integrations"],
            "total_automation_rules": process_automation.get_automation_stats()["active_rules"],
            "total_services": orchestration_platform.get_platform_status()["services_managed"]
        }
    }