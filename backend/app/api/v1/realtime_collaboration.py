"""
Real-Time Collaboration API
WebSocket and HTTP endpoints for real-time collaboration features
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query, status
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import json

from app.auth.clerk_auth import ClerkUser, get_current_user
from app.auth.tenant_isolation import TenantAwareQuery, get_tenant_query
from app.core.permissions import PermissionChecker, ResourceType, Action
from app.realtime.websocket_manager import websocket_manager, RealtimeMessage, MessageType
from app.realtime.notifications import notification_service, NotificationType, NotificationPriority
from app.realtime.collaboration import document_manager, DocumentOperation, CursorPosition, OperationType, CursorType
from app.realtime.task_automation import get_task_engine, WorkflowTrigger, TaskStatus, TaskPriority

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    organization_id: str = Query(...),
    token: str = Query(...)  # Auth token for WebSocket
):
    """WebSocket endpoint for real-time collaboration"""

    try:
        # TODO: Validate auth token here
        # For now, we'll accept the connection with basic validation

        # Connect user to WebSocket manager
        connection_id = await websocket_manager.connect(
            websocket=websocket,
            user_id=user_id,
            organization_id=organization_id,
            user_info={"connected_at": datetime.utcnow().isoformat()}
        )

        try:
            while True:
                # Wait for messages from client
                raw_message = await websocket.receive_text()

                # Handle the message
                await websocket_manager.handle_message(connection_id, raw_message)

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user {user_id}")

        except Exception as e:
            logger.error(f"WebSocket error for user {user_id}: {str(e)}")

    except Exception as e:
        logger.error(f"WebSocket connection failed for user {user_id}: {str(e)}")
        await websocket.close(code=1000)

    finally:
        # Clean up connection
        if 'connection_id' in locals():
            await websocket_manager.disconnect(connection_id)


@router.get("/online-users")
async def get_online_users(
    current_user: ClerkUser = Depends(get_current_user)
):
    """Get list of online users in organization"""

    try:
        online_users = websocket_manager.get_online_users(current_user.organization_id)

        return {
            "online_users": online_users,
            "total_count": len(online_users),
            "metadata": {
                "organization_id": current_user.organization_id,
                "retrieved_at": datetime.utcnow().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Failed to get online users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve online users"
        )


@router.get("/notifications")
async def get_user_notifications(
    include_read: bool = Query(False),
    limit: int = Query(50, le=100),
    current_user: ClerkUser = Depends(get_current_user)
):
    """Get user notifications"""

    try:
        notifications = await notification_service.get_user_notifications(
            user_id=current_user.user_id,
            include_read=include_read,
            limit=limit
        )

        # Convert notifications to dict format
        notification_data = []
        for notif in notifications:
            notification_data.append({
                "id": notif.id,
                "type": notif.type.value,
                "priority": notif.priority.value,
                "title": notif.title,
                "message": notif.message,
                "sender_id": notif.sender_id,
                "related_entity_type": notif.related_entity_type,
                "related_entity_id": notif.related_entity_id,
                "action_url": notif.action_url,
                "action_text": notif.action_text,
                "data": notif.data,
                "created_at": notif.created_at.isoformat(),
                "read_at": notif.read_at.isoformat() if notif.read_at else None,
                "expires_at": notif.expires_at.isoformat() if notif.expires_at else None,
                "is_read": notif.is_read,
                "is_dismissed": notif.is_dismissed
            })

        return {
            "notifications": notification_data,
            "total_count": len(notification_data),
            "unread_count": await notification_service.get_unread_count(current_user.user_id),
            "metadata": {
                "user_id": current_user.user_id,
                "include_read": include_read,
                "limit": limit,
                "retrieved_at": datetime.utcnow().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"Failed to get user notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notifications"
        )


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: ClerkUser = Depends(get_current_user)
):
    """Mark notification as read"""

    try:
        success = await notification_service.mark_notification_read(
            notification_id=notification_id,
            user_id=current_user.user_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )

        return {
            "status": "success",
            "notification_id": notification_id,
            "marked_read_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to mark notification as read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notification as read"
        )


@router.post("/notifications/{notification_id}/dismiss")
async def dismiss_notification(
    notification_id: str,
    current_user: ClerkUser = Depends(get_current_user)
):
    """Dismiss notification"""

    try:
        success = await notification_service.dismiss_notification(
            notification_id=notification_id,
            user_id=current_user.user_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )

        return {
            "status": "success",
            "notification_id": notification_id,
            "dismissed_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to dismiss notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to dismiss notification"
        )


@router.post("/documents/{document_id}/collaborate")
async def join_document_collaboration(
    document_id: str,
    current_user: ClerkUser = Depends(get_current_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query)
):
    """Join document collaboration session"""

    try:
        # Check if document exists and user has access
        document = tenant_query.get_by_id("documents", document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Check permissions
        if not PermissionChecker.has_permission(
            current_user.organization_role,
            ResourceType.DOCUMENTS,
            Action.READ
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access document"
            )

        # Join document collaboration
        doc_state = await document_manager.join_document(
            document_id=document_id,
            user_id=current_user.user_id,
            user_info={
                "email": current_user.email,
                "role": current_user.organization_role.value
            },
            organization_id=current_user.organization_id
        )

        # Get current collaborators
        collaborators = await document_manager.get_document_collaborators(document_id)

        return {
            "status": "joined",
            "document_id": document_id,
            "document_state": {
                "version": doc_state.version,
                "content_length": len(doc_state.content),
                "last_modified": doc_state.last_modified.isoformat(),
                "locked_by": doc_state.locked_by,
                "locked_at": doc_state.locked_at.isoformat() if doc_state.locked_at else None
            },
            "collaborators": collaborators,
            "websocket_channel": f"doc_{document_id}",
            "joined_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to join document collaboration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to join document collaboration"
        )


@router.post("/documents/{document_id}/leave")
async def leave_document_collaboration(
    document_id: str,
    current_user: ClerkUser = Depends(get_current_user)
):
    """Leave document collaboration session"""

    try:
        await document_manager.leave_document(document_id, current_user.user_id)

        return {
            "status": "left",
            "document_id": document_id,
            "user_id": current_user.user_id,
            "left_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to leave document collaboration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to leave document collaboration"
        )


@router.post("/documents/{document_id}/lock")
async def lock_document(
    document_id: str,
    current_user: ClerkUser = Depends(get_current_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query)
):
    """Lock document for exclusive editing"""

    try:
        # Check document access
        document = tenant_query.get_by_id("documents", document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Check permissions
        if not PermissionChecker.has_permission(
            current_user.organization_role,
            ResourceType.DOCUMENTS,
            Action.UPDATE
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to lock document"
            )

        # Lock document
        success = await document_manager.lock_document(document_id, current_user.user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document is already locked by another user"
            )

        return {
            "status": "locked",
            "document_id": document_id,
            "locked_by": current_user.user_id,
            "locked_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to lock document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to lock document"
        )


@router.post("/documents/{document_id}/unlock")
async def unlock_document(
    document_id: str,
    current_user: ClerkUser = Depends(get_current_user)
):
    """Unlock document"""

    try:
        success = await document_manager.unlock_document(document_id, current_user.user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to unlock this document"
            )

        return {
            "status": "unlocked",
            "document_id": document_id,
            "unlocked_by": current_user.user_id,
            "unlocked_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to unlock document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unlock document"
        )


@router.get("/documents/{document_id}/collaborators")
async def get_document_collaborators(
    document_id: str,
    current_user: ClerkUser = Depends(get_current_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query)
):
    """Get list of document collaborators"""

    try:
        # Check document access
        document = tenant_query.get_by_id("documents", document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Check permissions
        if not PermissionChecker.has_permission(
            current_user.organization_role,
            ResourceType.DOCUMENTS,
            Action.READ
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view document collaborators"
            )

        collaborators = await document_manager.get_document_collaborators(document_id)

        return {
            "document_id": document_id,
            "collaborators": collaborators,
            "total_count": len(collaborators),
            "retrieved_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document collaborators: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document collaborators"
        )


@router.post("/channels/{channel}/join")
async def join_channel(
    channel: str,
    current_user: ClerkUser = Depends(get_current_user)
):
    """Join a real-time channel"""

    try:
        # Validate channel access based on channel type
        if channel.startswith("deal_"):
            deal_id = channel.replace("deal_", "")
            # TODO: Check if user has access to this deal
        elif channel.startswith("doc_"):
            doc_id = channel.replace("doc_", "")
            # TODO: Check if user has access to this document
        elif channel.startswith("team_"):
            team_id = channel.replace("team_", "")
            # TODO: Check if user is member of this team

        # For now, we'll return the channel info
        # The actual WebSocket channel joining happens via WebSocket messages

        return {
            "status": "ready_to_join",
            "channel": channel,
            "user_id": current_user.user_id,
            "message": f"Ready to join channel {channel} via WebSocket",
            "websocket_url": f"/api/v1/collaboration/ws/{current_user.user_id}",
            "instructions": "Send a DOCUMENT_JOIN or DEAL_JOIN message via WebSocket to join the channel"
        }

    except Exception as e:
        logger.error(f"Failed to prepare channel join: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to prepare channel join"
        )


@router.get("/channels/{channel}/members")
async def get_channel_members(
    channel: str,
    current_user: ClerkUser = Depends(get_current_user)
):
    """Get members of a real-time channel"""

    try:
        members = websocket_manager.get_channel_members(channel)

        return {
            "channel": channel,
            "members": members,
            "total_count": len(members),
            "retrieved_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get channel members: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve channel members"
        )


@router.post("/notifications/send")
async def send_notification(
    notification_data: Dict[str, Any],
    current_user: ClerkUser = Depends(get_current_user)
):
    """Send a custom notification"""

    try:
        # Check permissions to send notifications
        if not PermissionChecker.has_permission(
            current_user.organization_role,
            ResourceType.COMMUNICATIONS,
            Action.CREATE
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to send notifications"
            )

        # Validate required fields
        required_fields = ["type", "recipient_id", "title", "message"]
        for field in required_fields:
            if field not in notification_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )

        # Create notification
        notification = await notification_service.create_notification(
            notification_type=NotificationType(notification_data["type"]),
            recipient_id=notification_data["recipient_id"],
            organization_id=current_user.organization_id,
            data=notification_data.get("data", {}),
            sender_id=current_user.user_id,
            custom_title=notification_data["title"],
            custom_message=notification_data["message"],
            custom_priority=NotificationPriority(notification_data.get("priority", "medium")),
            related_entity_type=notification_data.get("related_entity_type"),
            related_entity_id=notification_data.get("related_entity_id"),
            action_url=notification_data.get("action_url"),
            expires_in_hours=notification_data.get("expires_in_hours")
        )

        return {
            "status": "sent",
            "notification_id": notification.id,
            "recipient_id": notification.recipient_id,
            "sent_at": notification.created_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send notification"
        )


# Task Automation Endpoints

@router.post("/workflows/trigger")
async def trigger_workflow(
    workflow_data: Dict[str, Any],
    current_user: ClerkUser = Depends(get_current_user)
):
    """Trigger a workflow based on an event"""

    try:
        # Check permissions
        if not PermissionChecker.has_permission(
            current_user.organization_role,
            ResourceType.ADMIN,
            Action.CREATE
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to trigger workflows"
            )

        # Validate required fields
        if "trigger" not in workflow_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required field: trigger"
            )

        # Get task engine
        task_engine = get_task_engine()

        # Start the engine if not running
        if not task_engine.is_running:
            await task_engine.start_engine()

        # Trigger workflow
        workflow_id = await task_engine.trigger_workflow(
            trigger=WorkflowTrigger(workflow_data["trigger"]),
            context=workflow_data.get("context", {}),
            organization_id=current_user.organization_id,
            deal_id=workflow_data.get("deal_id")
        )

        if not workflow_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No workflow found for trigger: {workflow_data['trigger']}"
            )

        return {
            "status": "triggered",
            "workflow_id": workflow_id,
            "trigger": workflow_data["trigger"],
            "organization_id": current_user.organization_id,
            "triggered_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to trigger workflow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger workflow"
        )


@router.get("/workflows")
async def get_organization_workflows(
    current_user: ClerkUser = Depends(get_current_user)
):
    """Get all workflows for the current organization"""

    try:
        # Check permissions
        if not PermissionChecker.has_permission(
            current_user.organization_role,
            ResourceType.ADMIN,
            Action.READ
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view workflows"
            )

        task_engine = get_task_engine()
        workflows = task_engine.get_organization_workflows(current_user.organization_id)

        return {
            "organization_id": current_user.organization_id,
            "workflows": workflows,
            "total_count": len(workflows),
            "retrieved_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflows: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve workflows"
        )


@router.get("/workflows/{workflow_id}")
async def get_workflow_status(
    workflow_id: str,
    current_user: ClerkUser = Depends(get_current_user)
):
    """Get status of a specific workflow"""

    try:
        # Check permissions
        if not PermissionChecker.has_permission(
            current_user.organization_role,
            ResourceType.ADMIN,
            Action.READ
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view workflow status"
            )

        task_engine = get_task_engine()
        workflow_status = task_engine.get_workflow_status(workflow_id)

        if not workflow_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )

        return workflow_status

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve workflow status"
        )


@router.get("/workflows/templates")
async def get_workflow_templates(
    current_user: ClerkUser = Depends(get_current_user)
):
    """Get available workflow templates"""

    try:
        # Check permissions
        if not PermissionChecker.has_permission(
            current_user.organization_role,
            ResourceType.ADMIN,
            Action.READ
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view workflow templates"
            )

        task_engine = get_task_engine()
        templates = []

        for template_id, template in task_engine.workflow_templates.items():
            templates.append({
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "trigger": template.trigger,
                "task_count": len(template.tasks),
                "tasks": [
                    {
                        "id": task.id,
                        "name": task.name,
                        "description": task.description,
                        "type": task.task_type,
                        "priority": task.priority,
                        "estimated_duration": str(task.estimated_duration)
                    }
                    for task in template.tasks
                ]
            })

        return {
            "templates": templates,
            "total_count": len(templates),
            "retrieved_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve workflow templates"
        )


@router.get("/health")
async def collaboration_health():
    """Health check for collaboration services"""

    try:
        # Get basic stats
        online_users_count = sum(
            len(connections) for connections in websocket_manager.user_connections.values()
        )
        active_channels_count = len(websocket_manager.channel_subscriptions)
        active_documents_count = len(document_manager.documents)

        # Check task engine
        task_engine = get_task_engine()
        active_workflows_count = len(task_engine.active_workflows)
        running_tasks_count = len(task_engine.running_tasks)

        return {
            "status": "healthy",
            "services": {
                "websocket_manager": "operational",
                "notification_service": "operational",
                "document_manager": "operational",
                "task_automation_engine": "operational" if task_engine.is_running else "standby"
            },
            "statistics": {
                "online_users": online_users_count,
                "active_channels": active_channels_count,
                "collaborative_documents": active_documents_count,
                "total_connections": len(websocket_manager.connections),
                "active_workflows": active_workflows_count,
                "running_tasks": running_tasks_count,
                "workflow_templates": len(task_engine.workflow_templates)
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }