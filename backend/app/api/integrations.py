"""
Integration API Endpoints
Manage platform integrations, workflows, monitoring, and alerts
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.auth.clerk_auth import ClerkUser, get_current_user, require_admin
from app.agents.integration_agent import get_integration_agent, cleanup_agent
from app.integrations.platform_connectors import PlatformCredentials
from app.services.monitoring_service import MonitoringService
from app.services.alerting_service import get_alerting_service, AlertSeverity, AlertType
from app.services.workflow_engine import get_workflow_engine
from app.models.integrations import PlatformIntegration, WorkflowAutomation

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


# Pydantic Schemas
class ConnectPlatformRequest(BaseModel):
    """Request to connect a platform"""
    platform_name: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    additional_config: Dict[str, Any] = {}


class SyncRequest(BaseModel):
    """Request to sync platform data"""
    platform_name: str
    sync_type: str
    since: Optional[datetime] = None


class CrossPlatformPublishRequest(BaseModel):
    """Request to publish content across platforms"""
    content: str
    platforms: List[str]
    content_type: str = "post"
    metadata: Optional[Dict[str, Any]] = None


class CreateWorkflowRequest(BaseModel):
    """Request to create a workflow"""
    name: str
    description: Optional[str] = None
    trigger_type: str
    trigger_config: Dict[str, Any]
    actions: List[Dict[str, Any]]
    is_active: bool = True


class ExecuteWorkflowRequest(BaseModel):
    """Request to execute a workflow"""
    trigger_data: Optional[Dict[str, Any]] = None


# Endpoints
@router.get("/platforms")
async def list_available_platforms():
    """Get list of available platform integrations"""
    from app.agents.integration_agent import IntegrationAgent

    platforms = []
    for platform_name, connector_class in IntegrationAgent.CONNECTOR_REGISTRY.items():
        platforms.append({
            "name": platform_name,
            "type": connector_class.platform_type if hasattr(connector_class, 'platform_type') else "unknown",
            "description": connector_class.__doc__ or ""
        })

    return {"platforms": platforms}


@router.post("/connect")
async def connect_platform(
    request: ConnectPlatformRequest,
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Connect to a platform"""
    try:
        # Create credentials
        credentials = PlatformCredentials(
            platform_name=request.platform_name,
            api_key=request.api_key,
            api_secret=request.api_secret,
            access_token=request.access_token,
            refresh_token=request.refresh_token,
            additional_config=request.additional_config
        )

        # Get integration agent
        agent = get_integration_agent(current_user.organization_id)

        # Connect platform
        success = await agent.connect_platform(
            platform_name=request.platform_name,
            credentials=credentials,
            **request.additional_config
        )

        if success:
            # Create/update database record
            integration = db.query(PlatformIntegration).filter(
                PlatformIntegration.organization_id == current_user.organization_id,
                PlatformIntegration.platform_name == request.platform_name
            ).first()

            if not integration:
                integration = PlatformIntegration(
                    organization_id=current_user.organization_id,
                    platform_name=request.platform_name,
                    platform_category=request.additional_config.get("category", "social_media"),
                    is_active=True,
                    is_configured=True,
                    connected_at=datetime.utcnow()
                )
                db.add(integration)
            else:
                integration.is_active = True
                integration.is_configured = True
                integration.connected_at = datetime.utcnow()

            db.commit()

            return {
                "success": True,
                "platform_name": request.platform_name,
                "message": f"Successfully connected to {request.platform_name}"
            }

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect to {request.platform_name}"
        )

    except Exception as e:
        logger.error(f"Error connecting platform: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/disconnect/{platform_name}")
async def disconnect_platform(
    platform_name: str,
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Disconnect from a platform"""
    try:
        agent = get_integration_agent(current_user.organization_id)
        success = await agent.disconnect_platform(platform_name)

        if success:
            # Update database record
            integration = db.query(PlatformIntegration).filter(
                PlatformIntegration.organization_id == current_user.organization_id,
                PlatformIntegration.platform_name == platform_name
            ).first()

            if integration:
                integration.is_active = False
                db.commit()

            return {
                "success": True,
                "platform_name": platform_name,
                "message": f"Disconnected from {platform_name}"
            }

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Platform {platform_name} not found"
        )

    except Exception as e:
        logger.error(f"Error disconnecting platform: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/status")
async def get_integrations_status(
    current_user: ClerkUser = Depends(get_current_user)
):
    """Get status of all connected integrations"""
    agent = get_integration_agent(current_user.organization_id)
    status_info = agent.get_platform_status()

    return {
        "organization_id": current_user.organization_id,
        "connected_platforms": agent.get_connected_platforms(),
        "status": status_info
    }


@router.post("/sync")
async def sync_platform(
    request: SyncRequest,
    current_user: ClerkUser = Depends(get_current_user)
):
    """Sync data from a platform"""
    agent = get_integration_agent(current_user.organization_id)

    result = await agent.sync_platform_data(
        platform_name=request.platform_name,
        sync_type=request.sync_type,
        since=request.since
    )

    return result


@router.post("/publish")
async def cross_platform_publish(
    request: CrossPlatformPublishRequest,
    current_user: ClerkUser = Depends(get_current_user)
):
    """Publish content to multiple platforms"""
    agent = get_integration_agent(current_user.organization_id)

    results = await agent.cross_platform_publish(
        content=request.content,
        platforms=request.platforms,
        content_type=request.content_type,
        metadata=request.metadata
    )

    return {
        "success": all(results.values()),
        "platforms": request.platforms,
        "results": results
    }


@router.get("/health")
async def check_health(
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check health of all integrations"""
    monitoring = MonitoringService(db)
    health_status = await monitoring.check_all_integrations(current_user.organization_id)

    return health_status


@router.get("/health/{platform_name}")
async def check_platform_health(
    platform_name: str,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check health of a specific platform"""
    monitoring = MonitoringService(db)
    health_status = await monitoring.check_integration_health(
        current_user.organization_id,
        platform_name
    )

    return health_status


@router.get("/metrics/{platform_name}")
async def get_platform_metrics(
    platform_name: str,
    period_days: int = 30,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get performance metrics for a platform"""
    monitoring = MonitoringService(db)
    metrics = await monitoring.get_integration_metrics(
        current_user.organization_id,
        platform_name,
        period_days
    )

    return metrics


@router.get("/alerts")
async def get_active_alerts(
    severity: Optional[AlertSeverity] = None,
    platform_name: Optional[str] = None,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get active alerts"""
    alerting = get_alerting_service(db)
    alerts = await alerting.get_active_alerts(
        current_user.organization_id,
        severity=severity,
        platform_name=platform_name
    )

    return {"alerts": alerts}


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: int,
    resolution_notes: Optional[str] = None,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resolve an alert"""
    alerting = get_alerting_service(db)
    success = await alerting.resolve_alert(alert_id, resolution_notes)

    if success:
        return {"success": True, "message": "Alert resolved"}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Alert not found"
    )


@router.get("/alerts/summary")
async def get_alert_summary(
    period_days: int = 7,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get alert summary"""
    alerting = get_alerting_service(db)
    summary = await alerting.get_alert_summary(
        current_user.organization_id,
        period_days
    )

    return summary


@router.post("/workflows")
async def create_workflow(
    request: CreateWorkflowRequest,
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new workflow"""
    workflow = WorkflowAutomation(
        organization_id=current_user.organization_id,
        created_by=current_user.user_id,
        name=request.name,
        description=request.description,
        trigger_type=request.trigger_type,
        trigger_config=request.trigger_config,
        actions=request.actions,
        action_count=len(request.actions),
        is_active=request.is_active
    )

    db.add(workflow)
    db.commit()

    return {
        "success": True,
        "workflow_id": workflow.id,
        "message": "Workflow created successfully"
    }


@router.get("/workflows")
async def list_workflows(
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all workflows"""
    workflows = db.query(WorkflowAutomation).filter(
        WorkflowAutomation.organization_id == current_user.organization_id
    ).all()

    return {
        "workflows": [
            {
                "id": wf.id,
                "name": wf.name,
                "description": wf.description,
                "trigger_type": wf.trigger_type,
                "is_active": wf.is_active,
                "execution_count": wf.execution_count,
                "success_rate": wf.success_rate,
                "created_at": wf.created_at.isoformat()
            }
            for wf in workflows
        ]
    }


@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    request: ExecuteWorkflowRequest,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute a workflow"""
    engine = get_workflow_engine(db)

    result = await engine.execute_workflow(
        workflow_id=workflow_id,
        organization_id=current_user.organization_id,
        trigger_data=request.trigger_data
    )

    return result


@router.get("/overview")
async def get_integrations_overview(
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive integrations overview"""
    monitoring = MonitoringService(db)
    alerting = get_alerting_service(db)
    agent = get_integration_agent(current_user.organization_id)

    # Get health status
    health = await monitoring.check_all_integrations(current_user.organization_id)

    # Get alerts
    active_alerts = await alerting.get_active_alerts(current_user.organization_id)

    # Get connected platforms
    connected_platforms = agent.get_connected_platforms()

    return {
        "organization_id": current_user.organization_id,
        "connected_platforms_count": len(connected_platforms),
        "connected_platforms": connected_platforms,
        "health_summary": {
            "overall_status": health.get("overall_status"),
            "healthy": health.get("healthy_count", 0),
            "degraded": health.get("degraded_count", 0),
            "down": health.get("down_count", 0)
        },
        "alerts_summary": {
            "active_alerts": len(active_alerts)
        },
        "timestamp": datetime.utcnow().isoformat()
    }
