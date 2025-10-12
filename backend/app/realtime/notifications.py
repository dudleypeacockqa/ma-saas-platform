"""
Real-Time Notification System
Advanced notification management with real-time delivery
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import text

from .websocket_manager import websocket_manager, RealtimeMessage, MessageType

logger = logging.getLogger(__name__)


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class NotificationType(str, Enum):
    """Types of notifications"""
    # Deal notifications
    DEAL_CREATED = "deal_created"
    DEAL_UPDATED = "deal_updated"
    DEAL_STATUS_CHANGED = "deal_status_changed"
    DEAL_ASSIGNED = "deal_assigned"
    DEAL_DEADLINE_APPROACHING = "deal_deadline_approaching"

    # Document notifications
    DOCUMENT_UPLOADED = "document_uploaded"
    DOCUMENT_SHARED = "document_shared"
    DOCUMENT_APPROVED = "document_approved"
    DOCUMENT_REJECTED = "document_rejected"
    DOCUMENT_EXPIRED = "document_expired"

    # Team notifications
    TEAM_MEMBER_ADDED = "team_member_added"
    TEAM_MEMBER_REMOVED = "team_member_removed"
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    TASK_OVERDUE = "task_overdue"

    # Communication notifications
    MESSAGE_RECEIVED = "message_received"
    MENTION_RECEIVED = "mention_received"
    VIDEO_CALL_INVITE = "video_call_invite"
    VIDEO_CALL_MISSED = "video_call_missed"

    # System notifications
    SYSTEM_MAINTENANCE = "system_maintenance"
    SECURITY_ALERT = "security_alert"
    FEATURE_ANNOUNCEMENT = "feature_announcement"
    SUBSCRIPTION_EXPIRING = "subscription_expiring"

    # AI notifications
    AI_INSIGHT_GENERATED = "ai_insight_generated"

    # Workflow notifications
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_UPDATED = "workflow_updated"
    WORKFLOW_COMPLETED = "workflow_completed"
    DEAL_RISK_DETECTED = "deal_risk_detected"
    OPPORTUNITY_IDENTIFIED = "opportunity_identified"
    PERFORMANCE_ALERT = "performance_alert"


@dataclass
class Notification:
    """Notification data structure"""
    id: str
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    recipient_id: str
    organization_id: str
    sender_id: Optional[str] = None
    related_entity_type: Optional[str] = None  # e.g., "deal", "document"
    related_entity_id: Optional[str] = None
    action_url: Optional[str] = None
    action_text: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    read_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_read: bool = False
    is_dismissed: bool = False

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.data is None:
            self.data = {}


class NotificationService:
    """Service for managing notifications"""

    def __init__(self):
        self.notification_cache: Dict[str, List[Notification]] = {}  # user_id -> notifications
        self.notification_templates = self._initialize_templates()

    def _initialize_templates(self) -> Dict[NotificationType, Dict[str, Any]]:
        """Initialize notification templates"""
        return {
            NotificationType.DEAL_CREATED: {
                "title": "New Deal Created",
                "message": "A new deal '{deal_title}' has been created",
                "priority": NotificationPriority.MEDIUM,
                "action_text": "View Deal"
            },
            NotificationType.DEAL_UPDATED: {
                "title": "Deal Updated",
                "message": "Deal '{deal_title}' has been updated",
                "priority": NotificationPriority.LOW,
                "action_text": "View Changes"
            },
            NotificationType.DEAL_STATUS_CHANGED: {
                "title": "Deal Status Changed",
                "message": "Deal '{deal_title}' status changed to {new_status}",
                "priority": NotificationPriority.MEDIUM,
                "action_text": "View Deal"
            },
            NotificationType.DEAL_ASSIGNED: {
                "title": "Deal Assigned",
                "message": "You have been assigned to deal '{deal_title}'",
                "priority": NotificationPriority.HIGH,
                "action_text": "View Deal"
            },
            NotificationType.DEAL_DEADLINE_APPROACHING: {
                "title": "Deal Deadline Approaching",
                "message": "Deal '{deal_title}' deadline is approaching ({days_left} days left)",
                "priority": NotificationPriority.HIGH,
                "action_text": "View Deal"
            },
            NotificationType.DOCUMENT_UPLOADED: {
                "title": "Document Uploaded",
                "message": "New document '{document_name}' uploaded to deal '{deal_title}'",
                "priority": NotificationPriority.MEDIUM,
                "action_text": "View Document"
            },
            NotificationType.DOCUMENT_SHARED: {
                "title": "Document Shared",
                "message": "Document '{document_name}' has been shared with you",
                "priority": NotificationPriority.MEDIUM,
                "action_text": "View Document"
            },
            NotificationType.DOCUMENT_APPROVED: {
                "title": "Document Approved",
                "message": "Document '{document_name}' has been approved",
                "priority": NotificationPriority.MEDIUM,
                "action_text": "View Document"
            },
            NotificationType.DOCUMENT_REJECTED: {
                "title": "Document Rejected",
                "message": "Document '{document_name}' has been rejected: {reason}",
                "priority": NotificationPriority.HIGH,
                "action_text": "View Document"
            },
            NotificationType.TASK_ASSIGNED: {
                "title": "Task Assigned",
                "message": "You have been assigned a new task: '{task_title}'",
                "priority": NotificationPriority.HIGH,
                "action_text": "View Task"
            },
            NotificationType.TASK_COMPLETED: {
                "title": "Task Completed",
                "message": "Task '{task_title}' has been completed by {completed_by}",
                "priority": NotificationPriority.MEDIUM,
                "action_text": "View Task"
            },
            NotificationType.TASK_OVERDUE: {
                "title": "Task Overdue",
                "message": "Task '{task_title}' is now overdue",
                "priority": NotificationPriority.URGENT,
                "action_text": "View Task"
            },
            NotificationType.MESSAGE_RECEIVED: {
                "title": "New Message",
                "message": "New message from {sender_name}",
                "priority": NotificationPriority.MEDIUM,
                "action_text": "View Message"
            },
            NotificationType.MENTION_RECEIVED: {
                "title": "You Were Mentioned",
                "message": "{sender_name} mentioned you in {context}",
                "priority": NotificationPriority.HIGH,
                "action_text": "View Message"
            },
            NotificationType.VIDEO_CALL_INVITE: {
                "title": "Video Call Invitation",
                "message": "{caller_name} is inviting you to a video call",
                "priority": NotificationPriority.URGENT,
                "action_text": "Join Call"
            },
            NotificationType.AI_INSIGHT_GENERATED: {
                "title": "New AI Insight",
                "message": "AI has generated a new insight: {insight_title}",
                "priority": NotificationPriority.MEDIUM,
                "action_text": "View Insight"
            },
            NotificationType.DEAL_RISK_DETECTED: {
                "title": "Deal Risk Detected",
                "message": "AI has detected a {risk_level} risk in deal '{deal_title}'",
                "priority": NotificationPriority.HIGH,
                "action_text": "View Analysis"
            },
            NotificationType.OPPORTUNITY_IDENTIFIED: {
                "title": "Opportunity Identified",
                "message": "AI has identified a new opportunity: {opportunity_title}",
                "priority": NotificationPriority.MEDIUM,
                "action_text": "View Opportunity"
            },
            NotificationType.SECURITY_ALERT: {
                "title": "Security Alert",
                "message": "Security alert: {alert_message}",
                "priority": NotificationPriority.URGENT,
                "action_text": "Review Alert"
            }
        }

    async def create_notification(
        self,
        notification_type: NotificationType,
        recipient_id: str,
        organization_id: str,
        data: Dict[str, Any],
        sender_id: Optional[str] = None,
        custom_title: Optional[str] = None,
        custom_message: Optional[str] = None,
        custom_priority: Optional[NotificationPriority] = None,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[str] = None,
        action_url: Optional[str] = None,
        expires_in_hours: Optional[int] = None
    ) -> Notification:
        """Create and send a notification"""

        # Get template
        template = self.notification_templates.get(notification_type, {})

        # Format title and message
        title = custom_title or template.get("title", "Notification")
        message = custom_message or template.get("message", "You have a new notification")

        # Replace placeholders in title and message
        try:
            title = title.format(**data)
            message = message.format(**data)
        except KeyError as e:
            logger.warning(f"Missing data key for notification template: {e}")

        # Create notification
        notification = Notification(
            id=f"notif_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{recipient_id}",
            type=notification_type,
            priority=custom_priority or template.get("priority", NotificationPriority.MEDIUM),
            title=title,
            message=message,
            recipient_id=recipient_id,
            organization_id=organization_id,
            sender_id=sender_id,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            action_url=action_url or self._generate_action_url(notification_type, related_entity_type, related_entity_id),
            action_text=template.get("action_text"),
            data=data,
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours) if expires_in_hours else None
        )

        # Cache notification
        if recipient_id not in self.notification_cache:
            self.notification_cache[recipient_id] = []

        self.notification_cache[recipient_id].append(notification)

        # Keep only last 100 notifications per user
        if len(self.notification_cache[recipient_id]) > 100:
            self.notification_cache[recipient_id] = self.notification_cache[recipient_id][-100:]

        # Send real-time notification
        await self._send_realtime_notification(notification)

        logger.info(f"Created notification {notification.id} for user {recipient_id}")
        return notification

    async def _send_realtime_notification(self, notification: Notification):
        """Send notification via WebSocket"""

        realtime_message = RealtimeMessage(
            id=notification.id,
            type=MessageType.NOTIFICATION,
            sender_id=notification.sender_id or "system",
            target_id=notification.recipient_id,
            payload={
                "notification_id": notification.id,
                "type": notification.type.value,
                "priority": notification.priority.value,
                "title": notification.title,
                "message": notification.message,
                "action_url": notification.action_url,
                "action_text": notification.action_text,
                "related_entity_type": notification.related_entity_type,
                "related_entity_id": notification.related_entity_id,
                "data": notification.data,
                "created_at": notification.created_at.isoformat(),
                "expires_at": notification.expires_at.isoformat() if notification.expires_at else None
            },
            organization_id=notification.organization_id
        )

        await websocket_manager.send_to_user(notification.recipient_id, realtime_message)

    def _generate_action_url(
        self,
        notification_type: NotificationType,
        entity_type: Optional[str],
        entity_id: Optional[str]
    ) -> Optional[str]:
        """Generate action URL based on notification type and entity"""

        if not entity_type or not entity_id:
            return None

        url_map = {
            "deal": f"/deals/{entity_id}",
            "document": f"/documents/{entity_id}",
            "task": f"/tasks/{entity_id}",
            "team": f"/teams/{entity_id}",
            "insight": f"/analytics/insights/{entity_id}"
        }

        return url_map.get(entity_type)

    async def get_user_notifications(
        self,
        user_id: str,
        include_read: bool = True,
        limit: int = 50
    ) -> List[Notification]:
        """Get notifications for a user"""

        if user_id not in self.notification_cache:
            return []

        notifications = self.notification_cache[user_id]

        # Filter based on read status
        if not include_read:
            notifications = [n for n in notifications if not n.is_read]

        # Filter expired notifications
        current_time = datetime.utcnow()
        notifications = [
            n for n in notifications
            if not n.expires_at or n.expires_at > current_time
        ]

        # Sort by creation time (newest first) and limit
        notifications.sort(key=lambda x: x.created_at, reverse=True)

        return notifications[:limit]

    async def mark_notification_read(self, notification_id: str, user_id: str) -> bool:
        """Mark a notification as read"""

        if user_id not in self.notification_cache:
            return False

        for notification in self.notification_cache[user_id]:
            if notification.id == notification_id:
                notification.is_read = True
                notification.read_at = datetime.utcnow()
                logger.info(f"Marked notification {notification_id} as read for user {user_id}")
                return True

        return False

    async def dismiss_notification(self, notification_id: str, user_id: str) -> bool:
        """Dismiss a notification"""

        if user_id not in self.notification_cache:
            return False

        for i, notification in enumerate(self.notification_cache[user_id]):
            if notification.id == notification_id:
                notification.is_dismissed = True
                logger.info(f"Dismissed notification {notification_id} for user {user_id}")
                return True

        return False

    async def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications for a user"""

        if user_id not in self.notification_cache:
            return 0

        current_time = datetime.utcnow()
        unread_count = 0

        for notification in self.notification_cache[user_id]:
            if (not notification.is_read and
                not notification.is_dismissed and
                (not notification.expires_at or notification.expires_at > current_time)):
                unread_count += 1

        return unread_count

    async def cleanup_expired_notifications(self):
        """Remove expired notifications from cache"""

        current_time = datetime.utcnow()
        cleaned_count = 0

        for user_id in list(self.notification_cache.keys()):
            original_count = len(self.notification_cache[user_id])

            # Remove expired notifications
            self.notification_cache[user_id] = [
                n for n in self.notification_cache[user_id]
                if not n.expires_at or n.expires_at > current_time
            ]

            cleaned_count += original_count - len(self.notification_cache[user_id])

            # Remove empty user caches
            if not self.notification_cache[user_id]:
                del self.notification_cache[user_id]

        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} expired notifications")

        return cleaned_count

    # Convenience methods for common notification types

    async def notify_deal_created(
        self,
        deal_id: str,
        deal_title: str,
        recipient_id: str,
        organization_id: str,
        creator_id: str
    ):
        """Notify about new deal creation"""
        await self.create_notification(
            NotificationType.DEAL_CREATED,
            recipient_id,
            organization_id,
            {"deal_title": deal_title},
            sender_id=creator_id,
            related_entity_type="deal",
            related_entity_id=deal_id
        )

    async def notify_deal_assigned(
        self,
        deal_id: str,
        deal_title: str,
        recipient_id: str,
        organization_id: str,
        assigner_id: str
    ):
        """Notify about deal assignment"""
        await self.create_notification(
            NotificationType.DEAL_ASSIGNED,
            recipient_id,
            organization_id,
            {"deal_title": deal_title},
            sender_id=assigner_id,
            related_entity_type="deal",
            related_entity_id=deal_id
        )

    async def notify_document_shared(
        self,
        document_id: str,
        document_name: str,
        recipient_id: str,
        organization_id: str,
        sharer_id: str
    ):
        """Notify about document sharing"""
        await self.create_notification(
            NotificationType.DOCUMENT_SHARED,
            recipient_id,
            organization_id,
            {"document_name": document_name},
            sender_id=sharer_id,
            related_entity_type="document",
            related_entity_id=document_id
        )

    async def notify_task_assigned(
        self,
        task_id: str,
        task_title: str,
        recipient_id: str,
        organization_id: str,
        assigner_id: str
    ):
        """Notify about task assignment"""
        await self.create_notification(
            NotificationType.TASK_ASSIGNED,
            recipient_id,
            organization_id,
            {"task_title": task_title},
            sender_id=assigner_id,
            related_entity_type="task",
            related_entity_id=task_id
        )

    async def notify_ai_insight(
        self,
        insight_id: str,
        insight_title: str,
        recipient_id: str,
        organization_id: str
    ):
        """Notify about AI-generated insight"""
        await self.create_notification(
            NotificationType.AI_INSIGHT_GENERATED,
            recipient_id,
            organization_id,
            {"insight_title": insight_title},
            related_entity_type="insight",
            related_entity_id=insight_id
        )

    async def notify_deal_risk(
        self,
        deal_id: str,
        deal_title: str,
        risk_level: str,
        recipient_id: str,
        organization_id: str
    ):
        """Notify about deal risk detection"""
        await self.create_notification(
            NotificationType.DEAL_RISK_DETECTED,
            recipient_id,
            organization_id,
            {"deal_title": deal_title, "risk_level": risk_level},
            custom_priority=NotificationPriority.HIGH,
            related_entity_type="deal",
            related_entity_id=deal_id
        )

    async def notify_video_call_invite(
        self,
        call_id: str,
        caller_name: str,
        recipient_id: str,
        organization_id: str,
        caller_id: str
    ):
        """Notify about video call invitation"""
        await self.create_notification(
            NotificationType.VIDEO_CALL_INVITE,
            recipient_id,
            organization_id,
            {"caller_name": caller_name},
            sender_id=caller_id,
            custom_priority=NotificationPriority.URGENT,
            related_entity_type="call",
            related_entity_id=call_id,
            expires_in_hours=1  # Call invitations expire quickly
        )


# Global notification service instance
notification_service = NotificationService()

def get_notification_service() -> NotificationService:
    """Get the global notification service instance"""
    return notification_service