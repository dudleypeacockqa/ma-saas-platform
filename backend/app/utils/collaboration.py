"""
Collaboration Utilities
Core utilities for team collaboration, communication, and coordination
"""
import asyncio
import json
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime, timedelta, date
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import logging

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    """Types of notifications"""
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    TASK_OVERDUE = "task_overdue"
    MEETING_SCHEDULED = "meeting_scheduled"
    MEETING_REMINDER = "meeting_reminder"
    TEAM_MEMBER_ADDED = "team_member_added"
    TEAM_MEMBER_REMOVED = "team_member_removed"
    MESSAGE_RECEIVED = "message_received"
    DOCUMENT_SHARED = "document_shared"
    DEADLINE_APPROACHING = "deadline_approaching"
    MILESTONE_ACHIEVED = "milestone_achieved"
    WORKFLOW_STATUS_CHANGE = "workflow_status_change"


class CommunicationChannel(str, Enum):
    """Communication channels"""
    EMAIL = "email"
    IN_APP = "in_app"
    SLACK = "slack"
    TEAMS = "teams"
    SMS = "sms"
    PUSH = "push"


@dataclass
class NotificationData:
    """Notification data structure"""
    recipient_id: str
    notification_type: NotificationType
    title: str
    message: str
    data: Dict[str, Any]
    channels: List[CommunicationChannel]
    priority: str = "normal"  # low, normal, high, urgent
    scheduled_for: Optional[datetime] = None
    expires_at: Optional[datetime] = None


@dataclass
class MeetingInvite:
    """Meeting invitation data"""
    meeting_id: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    organizer_email: str
    attendee_emails: List[str]
    location: Optional[str] = None
    meeting_url: Optional[str] = None
    calendar_event_data: Optional[Dict[str, Any]] = None


@dataclass
class DocumentCollaboration:
    """Document collaboration metadata"""
    document_id: str
    document_name: str
    shared_with: List[str]
    permissions: Dict[str, str]  # user_id -> permission_level
    collaboration_features: Dict[str, bool]
    version_tracking: bool = True
    real_time_editing: bool = False


class CollaborationManager:
    """Manager for team collaboration features"""

    def __init__(self):
        self.notification_queue = []
        self.active_collaborations = {}
        self.meeting_scheduler = MeetingScheduler()
        self.document_manager = DocumentCollaborationManager()

    async def notify_team_members(
        self,
        team_id: str,
        notification: NotificationData,
        exclude_user_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Send notifications to all team members

        Args:
            team_id: Team ID
            notification: Notification data
            exclude_user_ids: User IDs to exclude from notification

        Returns:
            Notification delivery results
        """
        try:
            # This would integrate with your team member lookup
            # team_members = await get_team_members(team_id)

            delivery_results = {
                "sent": 0,
                "failed": 0,
                "skipped": 0,
                "details": []
            }

            # Mock implementation - replace with actual team member lookup
            mock_team_members = ["user1", "user2", "user3"]

            for member_id in mock_team_members:
                if exclude_user_ids and member_id in exclude_user_ids:
                    delivery_results["skipped"] += 1
                    continue

                # Clone notification for each recipient
                member_notification = NotificationData(
                    recipient_id=member_id,
                    notification_type=notification.notification_type,
                    title=notification.title,
                    message=notification.message,
                    data=notification.data,
                    channels=notification.channels,
                    priority=notification.priority,
                    scheduled_for=notification.scheduled_for,
                    expires_at=notification.expires_at
                )

                result = await self._send_notification(member_notification)
                if result["success"]:
                    delivery_results["sent"] += 1
                else:
                    delivery_results["failed"] += 1

                delivery_results["details"].append({
                    "user_id": member_id,
                    "result": result
                })

            return delivery_results

        except Exception as e:
            logger.error(f"Error notifying team members: {str(e)}")
            return {"error": str(e)}

    async def _send_notification(self, notification: NotificationData) -> Dict[str, Any]:
        """
        Send individual notification through specified channels

        Args:
            notification: Notification data

        Returns:
            Delivery result
        """
        results = []

        for channel in notification.channels:
            try:
                if channel == CommunicationChannel.EMAIL:
                    result = await self._send_email_notification(notification)
                elif channel == CommunicationChannel.IN_APP:
                    result = await self._send_in_app_notification(notification)
                elif channel == CommunicationChannel.SLACK:
                    result = await self._send_slack_notification(notification)
                elif channel == CommunicationChannel.TEAMS:
                    result = await self._send_teams_notification(notification)
                elif channel == CommunicationChannel.SMS:
                    result = await self._send_sms_notification(notification)
                elif channel == CommunicationChannel.PUSH:
                    result = await self._send_push_notification(notification)
                else:
                    result = {"success": False, "error": f"Unknown channel: {channel}"}

                results.append({"channel": channel, "result": result})

            except Exception as e:
                results.append({
                    "channel": channel,
                    "result": {"success": False, "error": str(e)}
                })

        # Overall success if at least one channel succeeded
        success = any(r["result"]["success"] for r in results)

        return {
            "success": success,
            "channels": results,
            "notification_id": f"{notification.recipient_id}_{datetime.utcnow().timestamp()}"
        }

    async def _send_email_notification(self, notification: NotificationData) -> Dict[str, Any]:
        """Send email notification"""
        try:
            # Mock email sending - replace with actual email service
            logger.info(f"Sending email to {notification.recipient_id}: {notification.title}")

            # Simulate email sending delay
            await asyncio.sleep(0.1)

            return {"success": True, "message_id": f"email_{datetime.utcnow().timestamp()}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _send_in_app_notification(self, notification: NotificationData) -> Dict[str, Any]:
        """Send in-app notification"""
        try:
            # Store notification in database for in-app display
            notification_record = {
                "recipient_id": notification.recipient_id,
                "type": notification.notification_type,
                "title": notification.title,
                "message": notification.message,
                "data": notification.data,
                "priority": notification.priority,
                "created_at": datetime.utcnow(),
                "read": False
            }

            # Mock storage - replace with actual database storage
            logger.info(f"Storing in-app notification: {notification_record}")

            return {"success": True, "notification_id": f"app_{datetime.utcnow().timestamp()}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _send_slack_notification(self, notification: NotificationData) -> Dict[str, Any]:
        """Send Slack notification"""
        try:
            # Mock Slack integration - replace with actual Slack API
            slack_message = {
                "text": notification.title,
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{notification.title}*\n{notification.message}"
                        }
                    }
                ]
            }

            logger.info(f"Sending Slack message: {slack_message}")

            return {"success": True, "ts": datetime.utcnow().timestamp()}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _send_teams_notification(self, notification: NotificationData) -> Dict[str, Any]:
        """Send Microsoft Teams notification"""
        try:
            # Mock Teams integration - replace with actual Teams API
            teams_message = {
                "title": notification.title,
                "text": notification.message,
                "themeColor": "0078D4"
            }

            logger.info(f"Sending Teams message: {teams_message}")

            return {"success": True, "message_id": f"teams_{datetime.utcnow().timestamp()}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _send_sms_notification(self, notification: NotificationData) -> Dict[str, Any]:
        """Send SMS notification"""
        try:
            # Mock SMS integration - replace with actual SMS service (Twilio, etc.)
            sms_message = f"{notification.title}: {notification.message}"

            logger.info(f"Sending SMS: {sms_message}")

            return {"success": True, "message_sid": f"sms_{datetime.utcnow().timestamp()}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _send_push_notification(self, notification: NotificationData) -> Dict[str, Any]:
        """Send push notification"""
        try:
            # Mock push notification - replace with actual push service
            push_payload = {
                "title": notification.title,
                "body": notification.message,
                "data": notification.data
            }

            logger.info(f"Sending push notification: {push_payload}")

            return {"success": True, "notification_id": f"push_{datetime.utcnow().timestamp()}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_task_assignment_notification(
        self,
        task_title: str,
        assigned_to: str,
        assigned_by: str,
        due_date: Optional[datetime] = None,
        task_id: str = None
    ) -> NotificationData:
        """Create notification for task assignment"""

        message = f"You have been assigned a new task: {task_title}"
        if due_date:
            message += f" (Due: {due_date.strftime('%Y-%m-%d %H:%M')})"

        return NotificationData(
            recipient_id=assigned_to,
            notification_type=NotificationType.TASK_ASSIGNED,
            title="New Task Assignment",
            message=message,
            data={
                "task_id": task_id,
                "task_title": task_title,
                "assigned_by": assigned_by,
                "due_date": due_date.isoformat() if due_date else None
            },
            channels=[CommunicationChannel.EMAIL, CommunicationChannel.IN_APP],
            priority="normal"
        )

    def create_meeting_reminder_notification(
        self,
        meeting_title: str,
        start_time: datetime,
        meeting_url: Optional[str] = None,
        meeting_id: str = None
    ) -> NotificationData:
        """Create notification for meeting reminder"""

        time_until = start_time - datetime.utcnow()
        if time_until.total_seconds() > 3600:  # More than 1 hour
            reminder_text = f"starts in {int(time_until.total_seconds() // 3600)} hours"
        else:
            reminder_text = f"starts in {int(time_until.total_seconds() // 60)} minutes"

        message = f"Meeting '{meeting_title}' {reminder_text}"

        return NotificationData(
            recipient_id="",  # Will be set per recipient
            notification_type=NotificationType.MEETING_REMINDER,
            title="Meeting Reminder",
            message=message,
            data={
                "meeting_id": meeting_id,
                "meeting_title": meeting_title,
                "start_time": start_time.isoformat(),
                "meeting_url": meeting_url
            },
            channels=[CommunicationChannel.EMAIL, CommunicationChannel.IN_APP, CommunicationChannel.PUSH],
            priority="high"
        )


class MeetingScheduler:
    """Utility for meeting scheduling and calendar integration"""

    def __init__(self):
        self.calendar_integrations = {
            "outlook": False,
            "google": False,
            "apple": False
        }

    def find_optimal_meeting_time(
        self,
        participant_ids: List[str],
        duration_minutes: int,
        preferred_start_time: Optional[datetime] = None,
        preferred_end_time: Optional[datetime] = None,
        timezone: str = "UTC"
    ) -> List[Dict[str, Any]]:
        """
        Find optimal meeting times based on participant availability

        Args:
            participant_ids: List of participant user IDs
            duration_minutes: Meeting duration in minutes
            preferred_start_time: Earliest possible start time
            preferred_end_time: Latest possible end time
            timezone: Timezone for the meeting

        Returns:
            List of suggested meeting times with availability scores
        """
        # Mock implementation - replace with actual calendar integration
        suggested_times = []

        base_time = preferred_start_time or datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0)

        for i in range(5):  # Suggest 5 time slots
            slot_start = base_time + timedelta(hours=i * 2)
            slot_end = slot_start + timedelta(minutes=duration_minutes)

            # Mock availability calculation
            availability_score = max(0.5, 1.0 - (i * 0.1))  # Decreasing availability

            suggested_times.append({
                "start_time": slot_start,
                "end_time": slot_end,
                "availability_score": availability_score,
                "available_participants": len(participant_ids) - i,
                "conflicts": i,
                "timezone": timezone
            })

        return sorted(suggested_times, key=lambda x: x["availability_score"], reverse=True)

    async def schedule_meeting(
        self,
        meeting_data: MeetingInvite,
        send_invites: bool = True
    ) -> Dict[str, Any]:
        """
        Schedule a meeting and send calendar invites

        Args:
            meeting_data: Meeting information
            send_invites: Whether to send calendar invites

        Returns:
            Meeting scheduling result
        """
        try:
            # Create calendar event
            calendar_event = self._create_calendar_event(meeting_data)

            if send_invites:
                invite_results = await self._send_calendar_invites(meeting_data)
            else:
                invite_results = {"sent": 0, "failed": 0}

            return {
                "success": True,
                "meeting_id": meeting_data.meeting_id,
                "calendar_event_id": calendar_event["event_id"],
                "invites_sent": invite_results["sent"],
                "invites_failed": invite_results["failed"]
            }

        except Exception as e:
            logger.error(f"Error scheduling meeting: {str(e)}")
            return {"success": False, "error": str(e)}

    def _create_calendar_event(self, meeting_data: MeetingInvite) -> Dict[str, Any]:
        """Create calendar event (mock implementation)"""
        event = {
            "event_id": f"cal_{meeting_data.meeting_id}",
            "title": meeting_data.title,
            "description": meeting_data.description,
            "start": meeting_data.start_time.isoformat(),
            "end": meeting_data.end_time.isoformat(),
            "location": meeting_data.location or meeting_data.meeting_url,
            "attendees": meeting_data.attendee_emails,
            "organizer": meeting_data.organizer_email
        }

        logger.info(f"Created calendar event: {event}")
        return event

    async def _send_calendar_invites(self, meeting_data: MeetingInvite) -> Dict[str, int]:
        """Send calendar invitations (mock implementation)"""
        results = {"sent": 0, "failed": 0}

        for attendee_email in meeting_data.attendee_emails:
            try:
                # Mock sending invite
                logger.info(f"Sending calendar invite to {attendee_email}")
                await asyncio.sleep(0.05)  # Simulate network delay
                results["sent"] += 1
            except Exception as e:
                logger.error(f"Failed to send invite to {attendee_email}: {str(e)}")
                results["failed"] += 1

        return results


class DocumentCollaborationManager:
    """Manager for document collaboration features"""

    def __init__(self):
        self.active_sessions = {}
        self.version_history = {}

    def start_collaboration_session(
        self,
        document_id: str,
        user_id: str,
        permissions: str = "read"
    ) -> Dict[str, Any]:
        """
        Start a document collaboration session

        Args:
            document_id: Document ID
            user_id: User starting the session
            permissions: User permissions (read, write, admin)

        Returns:
            Session information
        """
        session_id = f"{document_id}_{user_id}_{datetime.utcnow().timestamp()}"

        if document_id not in self.active_sessions:
            self.active_sessions[document_id] = {}

        self.active_sessions[document_id][user_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "permissions": permissions,
            "started_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "cursor_position": None,
            "selected_text": None
        }

        return {
            "session_id": session_id,
            "document_id": document_id,
            "active_collaborators": len(self.active_sessions[document_id]),
            "your_permissions": permissions
        }

    def update_cursor_position(
        self,
        document_id: str,
        user_id: str,
        position: Dict[str, Any]
    ) -> bool:
        """Update user's cursor position in document"""
        if (document_id in self.active_sessions and
            user_id in self.active_sessions[document_id]):

            self.active_sessions[document_id][user_id]["cursor_position"] = position
            self.active_sessions[document_id][user_id]["last_activity"] = datetime.utcnow()
            return True

        return False

    def get_active_collaborators(self, document_id: str) -> List[Dict[str, Any]]:
        """Get list of active collaborators for a document"""
        if document_id not in self.active_sessions:
            return []

        collaborators = []
        current_time = datetime.utcnow()

        for user_id, session in self.active_sessions[document_id].items():
            # Consider active if last activity was within 5 minutes
            if (current_time - session["last_activity"]).seconds < 300:
                collaborators.append({
                    "user_id": user_id,
                    "permissions": session["permissions"],
                    "cursor_position": session["cursor_position"],
                    "last_activity": session["last_activity"]
                })

        return collaborators

    def track_document_change(
        self,
        document_id: str,
        user_id: str,
        change_type: str,
        change_data: Dict[str, Any]
    ) -> str:
        """Track document changes for version history"""

        change_id = f"{document_id}_{datetime.utcnow().timestamp()}"

        if document_id not in self.version_history:
            self.version_history[document_id] = []

        change_record = {
            "change_id": change_id,
            "user_id": user_id,
            "change_type": change_type,
            "change_data": change_data,
            "timestamp": datetime.utcnow(),
            "version": len(self.version_history[document_id]) + 1
        }

        self.version_history[document_id].append(change_record)

        return change_id


class WorkflowAutomationHelper:
    """Helper for workflow automation and triggers"""

    def __init__(self):
        self.automation_rules = {}
        self.active_workflows = {}

    def create_automation_rule(
        self,
        rule_name: str,
        trigger_conditions: Dict[str, Any],
        actions: List[Dict[str, Any]],
        enabled: bool = True
    ) -> str:
        """
        Create an automation rule

        Args:
            rule_name: Name of the automation rule
            trigger_conditions: Conditions that trigger the automation
            actions: Actions to execute when triggered
            enabled: Whether the rule is active

        Returns:
            Rule ID
        """
        rule_id = f"rule_{datetime.utcnow().timestamp()}"

        self.automation_rules[rule_id] = {
            "rule_id": rule_id,
            "name": rule_name,
            "trigger_conditions": trigger_conditions,
            "actions": actions,
            "enabled": enabled,
            "created_at": datetime.utcnow(),
            "last_triggered": None,
            "trigger_count": 0
        }

        return rule_id

    async def evaluate_triggers(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Evaluate automation triggers and execute actions

        Args:
            event_type: Type of event that occurred
            event_data: Event data

        Returns:
            List of executed actions and results
        """
        executed_actions = []

        for rule_id, rule in self.automation_rules.items():
            if not rule["enabled"]:
                continue

            if self._matches_trigger_conditions(event_type, event_data, rule["trigger_conditions"]):
                # Execute actions for this rule
                for action in rule["actions"]:
                    result = await self._execute_action(action, event_data)
                    executed_actions.append({
                        "rule_id": rule_id,
                        "rule_name": rule["name"],
                        "action": action,
                        "result": result
                    })

                # Update rule statistics
                rule["last_triggered"] = datetime.utcnow()
                rule["trigger_count"] += 1

        return executed_actions

    def _matches_trigger_conditions(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        conditions: Dict[str, Any]
    ) -> bool:
        """Check if event matches trigger conditions"""

        # Check event type
        if "event_type" in conditions and conditions["event_type"] != event_type:
            return False

        # Check field conditions
        for field, expected_value in conditions.get("fields", {}).items():
            if field not in event_data:
                return False

            actual_value = event_data[field]

            # Handle different comparison types
            if isinstance(expected_value, dict) and "operator" in expected_value:
                operator = expected_value["operator"]
                value = expected_value["value"]

                if operator == "equals" and actual_value != value:
                    return False
                elif operator == "not_equals" and actual_value == value:
                    return False
                elif operator == "greater_than" and actual_value <= value:
                    return False
                elif operator == "less_than" and actual_value >= value:
                    return False
                elif operator == "contains" and value not in str(actual_value):
                    return False
            else:
                # Direct comparison
                if actual_value != expected_value:
                    return False

        return True

    async def _execute_action(
        self,
        action: Dict[str, Any],
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute an automation action"""

        action_type = action.get("type")
        action_params = action.get("parameters", {})

        try:
            if action_type == "send_notification":
                # Send notification action
                result = await self._send_automation_notification(action_params, event_data)

            elif action_type == "create_task":
                # Create task action
                result = await self._create_automation_task(action_params, event_data)

            elif action_type == "update_status":
                # Update status action
                result = await self._update_automation_status(action_params, event_data)

            elif action_type == "schedule_meeting":
                # Schedule meeting action
                result = await self._schedule_automation_meeting(action_params, event_data)

            elif action_type == "webhook":
                # Webhook action
                result = await self._execute_webhook(action_params, event_data)

            else:
                result = {"success": False, "error": f"Unknown action type: {action_type}"}

            return {"success": True, "action_type": action_type, "result": result}

        except Exception as e:
            logger.error(f"Error executing action {action_type}: {str(e)}")
            return {"success": False, "action_type": action_type, "error": str(e)}

    async def _send_automation_notification(
        self,
        params: Dict[str, Any],
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send notification as part of automation"""
        # Mock implementation
        logger.info(f"Automation notification: {params}")
        return {"notification_sent": True}

    async def _create_automation_task(
        self,
        params: Dict[str, Any],
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create task as part of automation"""
        # Mock implementation
        task_data = {
            "title": params.get("title", "Automated Task"),
            "description": params.get("description", ""),
            "assigned_to": params.get("assigned_to"),
            "due_date": params.get("due_date"),
            "created_by_automation": True
        }

        logger.info(f"Automation task created: {task_data}")
        return {"task_created": True, "task_data": task_data}

    async def _update_automation_status(
        self,
        params: Dict[str, Any],
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update status as part of automation"""
        # Mock implementation
        logger.info(f"Automation status update: {params}")
        return {"status_updated": True}

    async def _schedule_automation_meeting(
        self,
        params: Dict[str, Any],
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Schedule meeting as part of automation"""
        # Mock implementation
        logger.info(f"Automation meeting scheduled: {params}")
        return {"meeting_scheduled": True}

    async def _execute_webhook(
        self,
        params: Dict[str, Any],
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute webhook as part of automation"""
        # Mock implementation
        logger.info(f"Automation webhook executed: {params}")
        return {"webhook_executed": True}


class AnalyticsHelper:
    """Helper for collaboration analytics and reporting"""

    def __init__(self):
        self.metrics_cache = {}

    def calculate_team_collaboration_score(
        self,
        team_id: str,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate team collaboration effectiveness score

        Args:
            team_id: Team ID
            period_days: Analysis period in days

        Returns:
            Collaboration score and metrics
        """
        # Mock implementation - replace with actual data analysis
        base_score = 75.0

        metrics = {
            "communication_frequency": 8.2,  # messages per day
            "response_time_avg": 2.3,        # hours
            "meeting_attendance_rate": 0.87,  # 87%
            "document_collaboration_rate": 0.65,  # 65%
            "task_collaboration_rate": 0.72,      # 72%
            "cross_functional_interactions": 15,   # interactions
            "knowledge_sharing_score": 0.78       # 78%
        }

        # Calculate weighted score
        weights = {
            "communication_frequency": 0.15,
            "response_time_avg": 0.20,
            "meeting_attendance_rate": 0.15,
            "document_collaboration_rate": 0.20,
            "task_collaboration_rate": 0.15,
            "knowledge_sharing_score": 0.15
        }

        collaboration_score = base_score
        for metric, value in metrics.items():
            if metric in weights:
                # Normalize and apply weight
                normalized_value = min(value, 1.0) if value <= 1.0 else min(value / 10, 1.0)
                collaboration_score += (normalized_value * weights[metric] * 25)

        return {
            "team_id": team_id,
            "period_days": period_days,
            "collaboration_score": round(collaboration_score, 2),
            "grade": self._score_to_grade(collaboration_score),
            "metrics": metrics,
            "recommendations": self._generate_collaboration_recommendations(metrics)
        }

    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "C+"
        elif score >= 65:
            return "C"
        else:
            return "D"

    def _generate_collaboration_recommendations(
        self,
        metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on metrics"""
        recommendations = []

        if metrics["response_time_avg"] > 4:
            recommendations.append("Consider setting communication response time expectations")

        if metrics["meeting_attendance_rate"] < 0.8:
            recommendations.append("Review meeting scheduling and importance communication")

        if metrics["document_collaboration_rate"] < 0.6:
            recommendations.append("Encourage more collaborative document editing")

        if metrics["knowledge_sharing_score"] < 0.7:
            recommendations.append("Implement knowledge sharing sessions or documentation practices")

        if not recommendations:
            recommendations.append("Team collaboration is performing well across all metrics")

        return recommendations


# Export main classes for easy import
__all__ = [
    "CollaborationManager",
    "MeetingScheduler",
    "DocumentCollaborationManager",
    "WorkflowAutomationHelper",
    "AnalyticsHelper",
    "NotificationData",
    "MeetingInvite",
    "DocumentCollaboration",
    "NotificationType",
    "CommunicationChannel"
]