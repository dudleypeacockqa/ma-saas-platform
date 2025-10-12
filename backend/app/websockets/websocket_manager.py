"""
WebSocket Manager for Real-time Communication
Handles connection management, room management, and event broadcasting
"""

import asyncio
import json
from typing import Dict, Set, List, Optional, Any
from datetime import datetime
import logging
from dataclasses import dataclass, asdict

import socketio
from fastapi import HTTPException

logger = logging.getLogger(__name__)


@dataclass
class NotificationData:
    """Notification data structure"""
    id: str
    type: str  # 'deal_update', 'pipeline_change', 'ai_analysis', 'comment', 'mention', 'system'
    title: str
    message: str
    deal_id: Optional[str] = None
    user_id: Optional[str] = None
    organization_id: str = ""
    timestamp: str = ""
    data: Optional[Dict[str, Any]] = None
    read: bool = False
    priority: str = "medium"  # 'low', 'medium', 'high'

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UserSession:
    """User session information"""
    user_id: str
    organization_id: str
    session_id: str
    connected_at: datetime
    last_seen: datetime
    joined_deals: Set[str]

    def __post_init__(self):
        if isinstance(self.joined_deals, list):
            self.joined_deals = set(self.joined_deals)


class WebSocketManager:
    """Manages WebSocket connections and real-time communication"""

    def __init__(self):
        # Socket.IO server instance
        self.sio = socketio.AsyncServer(
            cors_allowed_origins="*",
            logger=True,
            engineio_logger=True,
            async_mode='asgi'
        )

        # Connection tracking
        self.active_sessions: Dict[str, UserSession] = {}  # session_id -> UserSession
        self.user_sessions: Dict[str, Set[str]] = {}  # user_id -> set of session_ids
        self.organization_sessions: Dict[str, Set[str]] = {}  # org_id -> set of session_ids
        self.deal_rooms: Dict[str, Set[str]] = {}  # deal_id -> set of session_ids

        # Event handlers
        self.setup_event_handlers()

    def setup_event_handlers(self):
        """Setup Socket.IO event handlers"""

        @self.sio.event
        async def connect(sid: str, environ: dict, auth: dict):
            """Handle client connection"""
            try:
                # Extract authentication data
                token = auth.get('token')
                organization_id = auth.get('organizationId')

                if not token or not organization_id:
                    logger.warning(f"Connection rejected for {sid}: Missing auth data")
                    await self.sio.disconnect(sid)
                    return

                # TODO: Validate token and get user info
                # For now, we'll extract user_id from token or use a mock
                user_id = self._extract_user_id_from_token(token)

                if not user_id:
                    logger.warning(f"Connection rejected for {sid}: Invalid token")
                    await self.sio.disconnect(sid)
                    return

                # Create user session
                session = UserSession(
                    user_id=user_id,
                    organization_id=organization_id,
                    session_id=sid,
                    connected_at=datetime.now(),
                    last_seen=datetime.now(),
                    joined_deals=set()
                )

                # Store session
                self.active_sessions[sid] = session

                # Track user sessions
                if user_id not in self.user_sessions:
                    self.user_sessions[user_id] = set()
                self.user_sessions[user_id].add(sid)

                # Track organization sessions
                if organization_id not in self.organization_sessions:
                    self.organization_sessions[organization_id] = set()
                self.organization_sessions[organization_id].add(sid)

                logger.info(f"User {user_id} connected with session {sid}")

                # Send connection confirmation
                await self.sio.emit('connection_status', {'status': 'connected'}, room=sid)

            except Exception as e:
                logger.error(f"Error handling connection for {sid}: {e}")
                await self.sio.disconnect(sid)

        @self.sio.event
        async def disconnect(sid: str):
            """Handle client disconnection"""
            try:
                session = self.active_sessions.get(sid)
                if not session:
                    return

                user_id = session.user_id
                organization_id = session.organization_id

                # Remove from deal rooms
                for deal_id in session.joined_deals:
                    if deal_id in self.deal_rooms:
                        self.deal_rooms[deal_id].discard(sid)
                        if not self.deal_rooms[deal_id]:
                            del self.deal_rooms[deal_id]

                # Remove from tracking
                self.active_sessions.pop(sid, None)

                if user_id in self.user_sessions:
                    self.user_sessions[user_id].discard(sid)
                    if not self.user_sessions[user_id]:
                        del self.user_sessions[user_id]

                if organization_id in self.organization_sessions:
                    self.organization_sessions[organization_id].discard(sid)
                    if not self.organization_sessions[organization_id]:
                        del self.organization_sessions[organization_id]

                logger.info(f"User {user_id} disconnected (session {sid})")

            except Exception as e:
                logger.error(f"Error handling disconnection for {sid}: {e}")

        @self.sio.event
        async def join_deal(sid: str, deal_id: str):
            """Handle user joining a deal room"""
            try:
                session = self.active_sessions.get(sid)
                if not session:
                    return

                # Add to deal room
                if deal_id not in self.deal_rooms:
                    self.deal_rooms[deal_id] = set()
                self.deal_rooms[deal_id].add(sid)

                # Track in session
                session.joined_deals.add(deal_id)
                session.last_seen = datetime.now()

                logger.info(f"User {session.user_id} joined deal room {deal_id}")

                # Notify others in the room
                await self.sio.emit(
                    'user_activity',
                    {
                        'user_id': session.user_id,
                        'activity': 'joined_deal',
                        'deal_id': deal_id,
                        'timestamp': datetime.now().isoformat()
                    },
                    room=deal_id,
                    skip_sid=sid
                )

            except Exception as e:
                logger.error(f"Error joining deal room for {sid}: {e}")

        @self.sio.event
        async def leave_deal(sid: str, deal_id: str):
            """Handle user leaving a deal room"""
            try:
                session = self.active_sessions.get(sid)
                if not session:
                    return

                # Remove from deal room
                if deal_id in self.deal_rooms:
                    self.deal_rooms[deal_id].discard(sid)
                    if not self.deal_rooms[deal_id]:
                        del self.deal_rooms[deal_id]

                # Remove from session
                session.joined_deals.discard(deal_id)
                session.last_seen = datetime.now()

                logger.info(f"User {session.user_id} left deal room {deal_id}")

                # Notify others in the room
                await self.sio.emit(
                    'user_activity',
                    {
                        'user_id': session.user_id,
                        'activity': 'left_deal',
                        'deal_id': deal_id,
                        'timestamp': datetime.now().isoformat()
                    },
                    room=deal_id,
                    skip_sid=sid
                )

            except Exception as e:
                logger.error(f"Error leaving deal room for {sid}: {e}")

        @self.sio.event
        async def mark_notification_read(sid: str, notification_id: str):
            """Handle marking notification as read"""
            try:
                session = self.active_sessions.get(sid)
                if not session:
                    return

                session.last_seen = datetime.now()

                # TODO: Update notification in database
                logger.info(f"Notification {notification_id} marked as read by {session.user_id}")

            except Exception as e:
                logger.error(f"Error marking notification read for {sid}: {e}")

        @self.sio.event
        async def user_typing(sid: str, data: dict):
            """Handle typing indicator"""
            try:
                session = self.active_sessions.get(sid)
                if not session:
                    return

                deal_id = data.get('dealId')
                is_typing = data.get('isTyping', False)

                if not deal_id:
                    return

                session.last_seen = datetime.now()

                # Broadcast typing indicator to deal room
                await self.sio.emit(
                    'user_typing',
                    {
                        'user_id': session.user_id,
                        'deal_id': deal_id,
                        'is_typing': is_typing,
                        'timestamp': datetime.now().isoformat()
                    },
                    room=deal_id,
                    skip_sid=sid
                )

            except Exception as e:
                logger.error(f"Error handling typing indicator for {sid}: {e}")

    def _extract_user_id_from_token(self, token: str) -> Optional[str]:
        """Extract user ID from JWT token"""
        # TODO: Implement proper JWT validation
        # For now, return a mock user ID
        return f"user_{hash(token) % 10000}"

    async def send_notification(self, notification: NotificationData, target_user_ids: Optional[List[str]] = None):
        """Send notification to specific users or organization"""
        try:
            notification_dict = notification.to_dict()

            if target_user_ids:
                # Send to specific users
                for user_id in target_user_ids:
                    await self._send_to_user(user_id, 'notification', notification_dict)
            else:
                # Send to entire organization
                await self._send_to_organization(notification.organization_id, 'notification', notification_dict)

            logger.info(f"Notification {notification.id} sent successfully")

        except Exception as e:
            logger.error(f"Error sending notification {notification.id}: {e}")

    async def broadcast_deal_update(self, deal_id: str, updates: Dict[str, Any], user_id: Optional[str] = None):
        """Broadcast deal update to all users in deal room"""
        try:
            if deal_id not in self.deal_rooms:
                return

            data = {
                'deal_id': deal_id,
                'updates': updates,
                'updated_by': user_id,
                'timestamp': datetime.now().isoformat()
            }

            await self.sio.emit('deal_updated', data, room=deal_id)
            logger.info(f"Deal update broadcasted for deal {deal_id}")

        except Exception as e:
            logger.error(f"Error broadcasting deal update for {deal_id}: {e}")

    async def broadcast_pipeline_change(self, deal_id: str, old_stage: str, new_stage: str, user_id: Optional[str] = None):
        """Broadcast pipeline stage change"""
        try:
            # Send to deal room
            if deal_id in self.deal_rooms:
                data = {
                    'deal_id': deal_id,
                    'old_stage': old_stage,
                    'new_stage': new_stage,
                    'changed_by': user_id,
                    'timestamp': datetime.now().isoformat()
                }

                await self.sio.emit('pipeline_changed', data, room=deal_id)

            # Also send notification to organization
            if user_id:
                session = self._get_user_session(user_id)
                if session:
                    notification = NotificationData(
                        id=f"pipeline_{deal_id}_{datetime.now().timestamp()}",
                        type="pipeline_change",
                        title="Pipeline Update",
                        message=f"Deal moved from {old_stage} to {new_stage}",
                        deal_id=deal_id,
                        user_id=user_id,
                        organization_id=session.organization_id,
                        priority="medium"
                    )

                    await self._send_to_organization(session.organization_id, 'notification', notification.to_dict())

            logger.info(f"Pipeline change broadcasted for deal {deal_id}")

        except Exception as e:
            logger.error(f"Error broadcasting pipeline change for {deal_id}: {e}")

    async def broadcast_ai_analysis_complete(self, deal_id: str, analysis: Dict[str, Any], organization_id: str):
        """Broadcast AI analysis completion"""
        try:
            # Send to deal room
            if deal_id in self.deal_rooms:
                data = {
                    'deal_id': deal_id,
                    'analysis': analysis,
                    'timestamp': datetime.now().isoformat()
                }

                await self.sio.emit('ai_analysis_complete', data, room=deal_id)

            # Send notification to organization
            notification = NotificationData(
                id=f"ai_analysis_{deal_id}_{datetime.now().timestamp()}",
                type="ai_analysis",
                title="AI Analysis Complete",
                message="New AI insights are available for your deal",
                deal_id=deal_id,
                organization_id=organization_id,
                priority="medium",
                data={"analysis_summary": analysis.get("summary", "")}
            )

            await self._send_to_organization(organization_id, 'notification', notification.to_dict())

            logger.info(f"AI analysis completion broadcasted for deal {deal_id}")

        except Exception as e:
            logger.error(f"Error broadcasting AI analysis completion for {deal_id}: {e}")

    async def _send_to_user(self, user_id: str, event: str, data: Any):
        """Send event to all sessions of a specific user"""
        if user_id in self.user_sessions:
            for session_id in self.user_sessions[user_id]:
                await self.sio.emit(event, data, room=session_id)

    async def _send_to_organization(self, organization_id: str, event: str, data: Any):
        """Send event to all users in an organization"""
        if organization_id in self.organization_sessions:
            for session_id in self.organization_sessions[organization_id]:
                await self.sio.emit(event, data, room=session_id)

    def _get_user_session(self, user_id: str) -> Optional[UserSession]:
        """Get a user session by user ID"""
        if user_id in self.user_sessions:
            session_ids = self.user_sessions[user_id]
            if session_ids:
                # Return first active session
                session_id = next(iter(session_ids))
                return self.active_sessions.get(session_id)
        return None

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics"""
        return {
            "active_sessions": len(self.active_sessions),
            "unique_users": len(self.user_sessions),
            "organizations": len(self.organization_sessions),
            "deal_rooms": len(self.deal_rooms),
            "deals_with_active_users": {
                deal_id: len(sessions) for deal_id, sessions in self.deal_rooms.items()
            }
        }

    def get_user_activity(self, organization_id: str) -> List[Dict[str, Any]]:
        """Get active users for an organization"""
        activity = []

        if organization_id in self.organization_sessions:
            for session_id in self.organization_sessions[organization_id]:
                session = self.active_sessions.get(session_id)
                if session:
                    activity.append({
                        "user_id": session.user_id,
                        "connected_at": session.connected_at.isoformat(),
                        "last_seen": session.last_seen.isoformat(),
                        "joined_deals": list(session.joined_deals)
                    })

        return activity

    async def cleanup_inactive_sessions(self, timeout_minutes: int = 30):
        """Clean up inactive sessions"""
        try:
            current_time = datetime.now()
            inactive_sessions = []

            for session_id, session in self.active_sessions.items():
                if (current_time - session.last_seen).total_seconds() > (timeout_minutes * 60):
                    inactive_sessions.append(session_id)

            for session_id in inactive_sessions:
                await self.sio.disconnect(session_id)

            if inactive_sessions:
                logger.info(f"Cleaned up {len(inactive_sessions)} inactive sessions")

        except Exception as e:
            logger.error(f"Error cleaning up inactive sessions: {e}")


# Global WebSocket manager instance
websocket_manager = WebSocketManager()

# Export the manager and Socket.IO app
__all__ = ['websocket_manager', 'WebSocketManager', 'NotificationData']