"""
Mobile-Optimized API Endpoints
Lightweight, mobile-first API endpoints for PWA and mobile apps
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import json

from app.auth.clerk_auth import ClerkUser, get_current_user
from app.auth.tenant_isolation import TenantAwareQuery, get_tenant_query
from app.core.permissions import PermissionChecker, ResourceType, Action
from app.mobile.pwa_service import get_pwa_service, PWANotification, PWAManifestGenerator
from app.mobile.offline_sync import get_offline_sync_service, SyncOperation, ConflictResolution

logger = logging.getLogger(__name__)

router = APIRouter()


# PWA Endpoints

@router.get("/manifest.json")
async def get_pwa_manifest():
    """Get PWA manifest.json"""

    manifest_generator = PWAManifestGenerator()
    manifest = manifest_generator.generate_manifest(
        app_name="M&A Platform",
        app_short_name="M&A Platform",
        app_description="Professional M&A Deal Management Platform",
        theme_color="#1a365d",
        background_color="#ffffff"
    )

    return JSONResponse(
        content=manifest,
        headers={
            "Content-Type": "application/manifest+json",
            "Cache-Control": "public, max-age=3600"
        }
    )


@router.get("/service-worker.js")
async def get_service_worker():
    """Get PWA service worker"""

    manifest_generator = PWAManifestGenerator()
    service_worker_code = manifest_generator.generate_service_worker()

    return Response(
        content=service_worker_code,
        media_type="application/javascript",
        headers={
            "Cache-Control": "public, max-age=3600",
            "Service-Worker-Allowed": "/"
        }
    )


@router.post("/pwa/subscribe")
async def subscribe_to_push_notifications(
    subscription_data: Dict[str, Any],
    current_user: ClerkUser = Depends(get_current_user)
):
    """Subscribe to PWA push notifications"""

    try:
        pwa_service = get_pwa_service()

        success = await pwa_service.register_subscription(
            user_id=current_user.user_id,
            organization_id=current_user.organization_id,
            subscription_data=subscription_data
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to register push subscription"
            )

        return {
            "status": "subscribed",
            "user_id": current_user.user_id,
            "subscribed_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to subscribe to push notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to subscribe to push notifications"
        )


@router.delete("/pwa/subscribe")
async def unsubscribe_from_push_notifications(
    current_user: ClerkUser = Depends(get_current_user)
):
    """Unsubscribe from PWA push notifications"""

    try:
        pwa_service = get_pwa_service()

        success = await pwa_service.unregister_subscription(
            user_id=current_user.user_id,
            organization_id=current_user.organization_id
        )

        return {
            "status": "unsubscribed" if success else "not_found",
            "user_id": current_user.user_id,
            "unsubscribed_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to unsubscribe from push notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unsubscribe from push notifications"
        )


@router.post("/pwa/test-notification")
async def send_test_notification(
    current_user: ClerkUser = Depends(get_current_user)
):
    """Send a test push notification"""

    try:
        # Check permissions
        if not PermissionChecker.has_permission(
            current_user.organization_role,
            ResourceType.ADMIN,
            Action.CREATE
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to send test notifications"
            )

        pwa_service = get_pwa_service()

        test_notification = PWANotification(
            title="Test Notification",
            body="This is a test notification from M&A Platform",
            icon="/static/icons/icon-192x192.png",
            badge="/static/icons/badge.png",
            tag="test_notification",
            data={
                "type": "test",
                "url": "/dashboard",
                "timestamp": datetime.utcnow().isoformat()
            },
            actions=[
                {
                    "action": "open",
                    "title": "Open App",
                    "icon": "/static/icons/open.png"
                }
            ],
            timestamp=datetime.utcnow()
        )

        success = await pwa_service.send_notification(
            user_id=current_user.user_id,
            organization_id=current_user.organization_id,
            notification=test_notification
        )

        return {
            "status": "sent" if success else "failed",
            "notification_title": test_notification.title,
            "sent_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send test notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send test notification"
        )


# Mobile-Optimized Data Endpoints

@router.get("/dashboard/summary")
async def get_mobile_dashboard_summary(
    current_user: ClerkUser = Depends(get_current_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query)
):
    """Get mobile-optimized dashboard summary"""

    try:
        # Get essential dashboard data with minimal payload
        summary = {
            "user": {
                "name": current_user.email.split("@")[0],  # Simple name from email
                "role": current_user.organization_role.value,
                "organization_id": current_user.organization_id
            },
            "stats": {
                "active_deals": 5,  # Mock data - would query actual database
                "pending_approvals": 2,
                "unread_notifications": 3,
                "recent_activity_count": 8
            },
            "quick_actions": [
                {
                    "id": "new_deal",
                    "title": "New Deal",
                    "icon": "plus-circle",
                    "url": "/deals/new",
                    "enabled": PermissionChecker.has_permission(
                        current_user.organization_role,
                        ResourceType.DEALS,
                        Action.CREATE
                    )
                },
                {
                    "id": "view_documents",
                    "title": "Documents",
                    "icon": "document",
                    "url": "/documents",
                    "enabled": True
                },
                {
                    "id": "notifications",
                    "title": "Notifications",
                    "icon": "bell",
                    "url": "/notifications",
                    "enabled": True
                },
                {
                    "id": "analytics",
                    "title": "Analytics",
                    "icon": "chart-bar",
                    "url": "/analytics",
                    "enabled": PermissionChecker.has_permission(
                        current_user.organization_role,
                        ResourceType.ANALYTICS,
                        Action.READ
                    )
                }
            ],
            "recent_deals": [
                {
                    "id": "deal-1",
                    "title": "TechCorp Acquisition",
                    "status": "due_diligence",
                    "last_activity": "2 hours ago",
                    "priority": "high"
                },
                {
                    "id": "deal-2",
                    "title": "RetailChain Merger",
                    "status": "negotiation",
                    "last_activity": "1 day ago",
                    "priority": "medium"
                }
            ],
            "pending_tasks": [
                {
                    "id": "task-1",
                    "title": "Review financial statements",
                    "deal_id": "deal-1",
                    "due_date": "2024-01-15",
                    "priority": "high"
                },
                {
                    "id": "task-2",
                    "title": "Schedule management meeting",
                    "deal_id": "deal-2",
                    "due_date": "2024-01-16",
                    "priority": "medium"
                }
            ],
            "generated_at": datetime.utcnow().isoformat()
        }

        return summary

    except Exception as e:
        logger.error(f"Failed to get mobile dashboard summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard summary"
        )


@router.get("/deals/mobile")
async def get_mobile_deals_list(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    status: Optional[str] = Query(None),
    current_user: ClerkUser = Depends(get_current_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query)
):
    """Get mobile-optimized deals list"""

    try:
        # Check permissions
        if not PermissionChecker.has_permission(
            current_user.organization_role,
            ResourceType.DEALS,
            Action.READ
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view deals"
            )

        # Mock mobile-optimized deals data
        deals = []
        for i in range(1, limit + 1):
            deals.append({
                "id": f"deal-{i}",
                "title": f"Deal {i}",
                "status": status or "active",
                "value": f"${i * 10}M",
                "last_activity": f"{i} hours ago",
                "priority": "high" if i % 3 == 0 else "medium",
                "progress": min(100, i * 10),
                "team_size": i % 5 + 2
            })

        return {
            "deals": deals,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_pages": 5,  # Mock total
                "total_count": 48,  # Mock total
                "has_next": page < 5,
                "has_prev": page > 1
            },
            "filters": {
                "status": status,
                "available_statuses": ["active", "due_diligence", "negotiation", "closed"]
            },
            "retrieved_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get mobile deals list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve deals list"
        )


@router.get("/deals/{deal_id}/mobile")
async def get_mobile_deal_details(
    deal_id: str,
    current_user: ClerkUser = Depends(get_current_user),
    tenant_query: TenantAwareQuery = Depends(get_tenant_query)
):
    """Get mobile-optimized deal details"""

    try:
        # Check permissions
        if not PermissionChecker.has_permission(
            current_user.organization_role,
            ResourceType.DEALS,
            Action.READ
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view deal details"
            )

        # Mock mobile-optimized deal details
        deal_details = {
            "id": deal_id,
            "title": "TechCorp Acquisition",
            "status": "due_diligence",
            "value": "$250M",
            "currency": "USD",
            "target_company": "TechCorp Inc.",
            "acquirer": "MegaCorp Ltd.",
            "progress": 65,
            "priority": "high",
            "created_date": "2024-01-01",
            "target_close_date": "2024-06-30",
            "last_activity": {
                "action": "Document uploaded",
                "user": "John Smith",
                "timestamp": "2 hours ago"
            },
            "key_metrics": {
                "documents": 45,
                "tasks_completed": 18,
                "tasks_pending": 7,
                "team_members": 12
            },
            "next_actions": [
                {
                    "id": "action-1",
                    "title": "Review financial statements",
                    "due_date": "2024-01-15",
                    "assigned_to": "Jane Doe",
                    "priority": "high"
                },
                {
                    "id": "action-2",
                    "title": "Legal review completion",
                    "due_date": "2024-01-18",
                    "assigned_to": "Legal Team",
                    "priority": "medium"
                }
            ],
            "recent_documents": [
                {
                    "id": "doc-1",
                    "name": "Financial Statements Q3",
                    "type": "pdf",
                    "size": "2.4MB",
                    "uploaded_by": "John Smith",
                    "uploaded_at": "2024-01-10"
                },
                {
                    "id": "doc-2",
                    "name": "Legal Opinion",
                    "type": "docx",
                    "size": "856KB",
                    "uploaded_by": "Legal Team",
                    "uploaded_at": "2024-01-09"
                }
            ],
            "team_members": [
                {
                    "id": "user-1",
                    "name": "John Smith",
                    "role": "Deal Lead",
                    "status": "online"
                },
                {
                    "id": "user-2",
                    "name": "Jane Doe",
                    "role": "Financial Analyst",
                    "status": "away"
                }
            ],
            "permissions": {
                "can_edit": PermissionChecker.has_permission(
                    current_user.organization_role,
                    ResourceType.DEALS,
                    Action.UPDATE
                ),
                "can_delete": PermissionChecker.has_permission(
                    current_user.organization_role,
                    ResourceType.DEALS,
                    Action.DELETE
                ),
                "can_assign": PermissionChecker.has_permission(
                    current_user.organization_role,
                    ResourceType.DEALS,
                    Action.ASSIGN
                )
            }
        }

        return deal_details

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get mobile deal details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve deal details"
        )


# Offline Sync Endpoints

@router.post("/sync/queue")
async def queue_sync_item(
    sync_data: Dict[str, Any],
    current_user: ClerkUser = Depends(get_current_user)
):
    """Queue an item for offline synchronization"""

    try:
        sync_service = get_offline_sync_service()

        # Validate required fields
        required_fields = ["entity_type", "entity_id", "operation", "data"]
        for field in required_fields:
            if field not in sync_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )

        sync_id = await sync_service.create_sync_item(
            entity_type=sync_data["entity_type"],
            entity_id=sync_data["entity_id"],
            operation=SyncOperation(sync_data["operation"]),
            data=sync_data["data"],
            user_id=current_user.user_id,
            organization_id=current_user.organization_id,
            client_timestamp=datetime.fromisoformat(sync_data.get("client_timestamp", datetime.utcnow().isoformat()))
        )

        return {
            "status": "queued",
            "sync_id": sync_id,
            "queued_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to queue sync item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue sync item"
        )


@router.get("/sync/pending")
async def get_pending_sync_items(
    current_user: ClerkUser = Depends(get_current_user)
):
    """Get pending sync items for current user"""

    try:
        sync_service = get_offline_sync_service()

        pending_items = await sync_service.get_pending_sync_items(
            user_id=current_user.user_id,
            organization_id=current_user.organization_id
        )

        return {
            "pending_items": pending_items,
            "total_count": len(pending_items),
            "retrieved_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get pending sync items: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pending sync items"
        )


@router.get("/sync/conflicts")
async def get_sync_conflicts(
    current_user: ClerkUser = Depends(get_current_user)
):
    """Get sync conflicts for current user"""

    try:
        sync_service = get_offline_sync_service()

        conflicts = await sync_service.get_sync_conflicts(
            user_id=current_user.user_id,
            organization_id=current_user.organization_id
        )

        return {
            "conflicts": conflicts,
            "total_count": len(conflicts),
            "retrieved_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get sync conflicts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sync conflicts"
        )


@router.post("/sync/conflicts/{conflict_id}/resolve")
async def resolve_sync_conflict(
    conflict_id: str,
    resolution_data: Dict[str, Any],
    current_user: ClerkUser = Depends(get_current_user)
):
    """Resolve a sync conflict"""

    try:
        if "resolution_strategy" not in resolution_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required field: resolution_strategy"
            )

        sync_service = get_offline_sync_service()

        success = await sync_service.resolve_conflict(
            conflict_id=conflict_id,
            resolution_strategy=ConflictResolution(resolution_data["resolution_strategy"]),
            resolved_data=resolution_data.get("resolved_data")
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conflict not found or resolution failed"
            )

        return {
            "status": "resolved",
            "conflict_id": conflict_id,
            "resolution_strategy": resolution_data["resolution_strategy"],
            "resolved_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve sync conflict: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve sync conflict"
        )


@router.post("/sync/full")
async def perform_full_sync(
    current_user: ClerkUser = Depends(get_current_user)
):
    """Perform full synchronization"""

    try:
        sync_service = get_offline_sync_service()

        sync_result = await sync_service.perform_full_sync(
            user_id=current_user.user_id,
            organization_id=current_user.organization_id
        )

        return {
            "status": "completed",
            **sync_result
        }

    except Exception as e:
        logger.error(f"Failed to perform full sync: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform full synchronization"
        )


# Mobile Performance & Health

@router.get("/mobile/health")
async def mobile_health_check():
    """Health check for mobile services"""

    try:
        pwa_service = get_pwa_service()
        sync_service = get_offline_sync_service()

        return {
            "status": "healthy",
            "services": {
                "pwa_service": "operational",
                "offline_sync": "operational" if sync_service.is_running else "standby",
                "push_notifications": "operational"
            },
            "statistics": {
                "total_subscriptions": len(pwa_service.subscriptions),
                "active_sync_workers": len(sync_service.sync_workers),
                "pending_sync_items": len(sync_service.pending_sync_items),
                "sync_conflicts": len(sync_service.sync_conflicts)
            },
            "features": {
                "offline_support": True,
                "push_notifications": True,
                "background_sync": True,
                "home_screen_install": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Mobile health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }