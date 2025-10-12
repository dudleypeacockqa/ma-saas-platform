"""
WebSocket Connection Manager
Manages real-time WebSocket connections for collaborative features
"""

import asyncio
import json
import logging
from typing import Dict, List, Set, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from fastapi import WebSocket, WebSocketDisconnect
import uuid

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Types of real-time messages"""
    # Connection management
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    HEARTBEAT = "heartbeat"

    # Chat and messaging
    CHAT_MESSAGE = "chat_message"
    TYPING_START = "typing_start"
    TYPING_STOP = "typing_stop"

    # Document collaboration
    DOCUMENT_JOIN = "document_join"
    DOCUMENT_LEAVE = "document_leave"
    DOCUMENT_EDIT = "document_edit"
    DOCUMENT_CURSOR = "document_cursor"
    DOCUMENT_SELECTION = "document_selection"

    # Deal collaboration
    DEAL_JOIN = "deal_join"
    DEAL_LEAVE = "deal_leave"
    DEAL_UPDATE = "deal_update"
    DEAL_ACTIVITY = "deal_activity"
    DEAL_STATUS_CHANGE = "deal_status_change"

    # Notifications
    NOTIFICATION = "notification"
    ALERT = "alert"
    SYSTEM_MESSAGE = "system_message"

    # Presence
    USER_ONLINE = "user_online"
    USER_OFFLINE = "user_offline"
    USER_STATUS = "user_status"

    # Video/Audio
    VIDEO_CALL_INVITE = "video_call_invite"
    VIDEO_CALL_ACCEPT = "video_call_accept"
    VIDEO_CALL_DECLINE = "video_call_decline"
    VIDEO_CALL_END = "video_call_end"

    # Task management
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_ASSIGNED = "task_assigned"

    # Workflow automation
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_UPDATE = "workflow_update"
    WORKFLOW_COMPLETED = "workflow_completed"
    TASK_COMPLETED = "task_completed"


class UserStatus(str, Enum):
    """User presence status"""
    ONLINE = "online"
    AWAY = "away"
    BUSY = "busy"
    OFFLINE = "offline"


@dataclass
class RealtimeMessage:
    """Real-time message structure"""
    id: str
    type: MessageType
    sender_id: str
    target_id: Optional[str] = None  # Specific user or room
    channel: Optional[str] = None    # Channel/room for group messages
    payload: Dict[str, Any] = None
    timestamp: datetime = None
    organization_id: str = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.payload is None:
            self.payload = {}


@dataclass
class ConnectedUser:
    """Connected user information"""
    user_id: str
    organization_id: str
    websocket: WebSocket
    connection_id: str
    status: UserStatus = UserStatus.ONLINE
    channels: Set[str] = None
    last_activity: datetime = None
    user_info: Dict[str, Any] = None

    def __post_init__(self):
        if self.channels is None:
            self.channels = set()
        if self.last_activity is None:
            self.last_activity = datetime.utcnow()
        if self.user_info is None:
            self.user_info = {}


class WebSocketManager:
    """Manages WebSocket connections and real-time messaging"""

    def __init__(self):
        # Active connections: connection_id -> ConnectedUser
        self.connections: Dict[str, ConnectedUser] = {}

        # User mappings: user_id -> Set[connection_id]
        self.user_connections: Dict[str, Set[str]] = {}

        # Organization mappings: org_id -> Set[connection_id]
        self.organization_connections: Dict[str, Set[str]] = {}

        # Channel subscriptions: channel -> Set[connection_id]
        self.channel_subscriptions: Dict[str, Set[str]] = {}

        # Message history for channels (in-memory cache)
        self.channel_history: Dict[str, List[RealtimeMessage]] = {}

        # Lock for thread-safe operations
        self.lock = asyncio.Lock()

    async def connect(
        self,
        websocket: WebSocket,
        user_id: str,
        organization_id: str,
        user_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """Accept new WebSocket connection"""

        await websocket.accept()
        connection_id = str(uuid.uuid4())

        async with self.lock:
            # Create connected user
            connected_user = ConnectedUser(
                user_id=user_id,
                organization_id=organization_id,
                websocket=websocket,
                connection_id=connection_id,
                user_info=user_info or {}
            )

            # Store connection
            self.connections[connection_id] = connected_user

            # Update user mappings
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)

            # Update organization mappings
            if organization_id not in self.organization_connections:
                self.organization_connections[organization_id] = set()
            self.organization_connections[organization_id].add(connection_id)

            logger.info(f"User {user_id} connected with connection {connection_id}")

            # Send welcome message
            await self.send_to_connection(connection_id, RealtimeMessage(
                id=str(uuid.uuid4()),
                type=MessageType.CONNECT,
                sender_id="system",
                payload={
                    "connection_id": connection_id,
                    "message": "Connected successfully",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ))

            # Notify organization about user coming online
            await self.broadcast_to_organization(
                organization_id,
                RealtimeMessage(
                    id=str(uuid.uuid4()),
                    type=MessageType.USER_ONLINE,
                    sender_id="system",
                    payload={
                        "user_id": user_id,
                        "user_info": user_info,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                ),
                exclude_connections={connection_id}
            )

        return connection_id

    async def disconnect(self, connection_id: str):
        """Handle WebSocket disconnection"""

        async with self.lock:
            if connection_id not in self.connections:
                return

            connected_user = self.connections[connection_id]
            user_id = connected_user.user_id
            organization_id = connected_user.organization_id

            # Remove from channels
            for channel in connected_user.channels.copy():
                await self._leave_channel_internal(connection_id, channel)

            # Remove connection
            del self.connections[connection_id]

            # Update user mappings
            if user_id in self.user_connections:
                self.user_connections[user_id].discard(connection_id)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]

            # Update organization mappings
            if organization_id in self.organization_connections:
                self.organization_connections[organization_id].discard(connection_id)
                if not self.organization_connections[organization_id]:
                    del self.organization_connections[organization_id]

            logger.info(f"User {user_id} disconnected (connection {connection_id})")

            # Check if user is completely offline
            user_still_connected = user_id in self.user_connections

            if not user_still_connected:
                # Notify organization about user going offline
                await self.broadcast_to_organization(
                    organization_id,
                    RealtimeMessage(
                        id=str(uuid.uuid4()),
                        type=MessageType.USER_OFFLINE,
                        sender_id="system",
                        payload={
                            "user_id": user_id,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                )

    async def send_to_connection(self, connection_id: str, message: RealtimeMessage):
        """Send message to specific connection"""

        if connection_id not in self.connections:
            logger.warning(f"Connection {connection_id} not found")
            return False

        connected_user = self.connections[connection_id]

        try:
            # Convert message to dict and send
            message_dict = asdict(message)
            message_dict['timestamp'] = message.timestamp.isoformat()

            await connected_user.websocket.send_text(json.dumps(message_dict))

            # Update last activity
            connected_user.last_activity = datetime.utcnow()

            return True

        except Exception as e:
            logger.error(f"Failed to send message to {connection_id}: {str(e)}")
            # Connection is likely broken, remove it
            await self.disconnect(connection_id)
            return False

    async def send_to_user(self, user_id: str, message: RealtimeMessage):
        """Send message to all connections of a specific user"""

        if user_id not in self.user_connections:
            logger.warning(f"User {user_id} not connected")
            return False

        success_count = 0
        connection_ids = list(self.user_connections[user_id])

        for connection_id in connection_ids:
            if await self.send_to_connection(connection_id, message):
                success_count += 1

        return success_count > 0

    async def broadcast_to_organization(
        self,
        organization_id: str,
        message: RealtimeMessage,
        exclude_connections: Optional[Set[str]] = None
    ):
        """Broadcast message to all users in an organization"""

        if organization_id not in self.organization_connections:
            logger.warning(f"No connections found for organization {organization_id}")
            return 0

        exclude_connections = exclude_connections or set()
        success_count = 0
        connection_ids = list(self.organization_connections[organization_id])

        for connection_id in connection_ids:
            if connection_id not in exclude_connections:
                if await self.send_to_connection(connection_id, message):
                    success_count += 1

        return success_count

    async def broadcast_to_channel(
        self,
        channel: str,
        message: RealtimeMessage,
        exclude_connections: Optional[Set[str]] = None,
        save_to_history: bool = True
    ):
        """Broadcast message to all subscribers of a channel"""

        if channel not in self.channel_subscriptions:
            logger.warning(f"No subscribers found for channel {channel}")
            return 0

        # Save to channel history
        if save_to_history:
            if channel not in self.channel_history:
                self.channel_history[channel] = []

            self.channel_history[channel].append(message)

            # Keep only last 100 messages per channel
            if len(self.channel_history[channel]) > 100:
                self.channel_history[channel] = self.channel_history[channel][-100:]

        exclude_connections = exclude_connections or set()
        success_count = 0
        connection_ids = list(self.channel_subscriptions[channel])

        for connection_id in connection_ids:
            if connection_id not in exclude_connections:
                if await self.send_to_connection(connection_id, message):
                    success_count += 1

        return success_count

    async def join_channel(self, connection_id: str, channel: str):
        """Subscribe connection to a channel"""

        async with self.lock:
            await self._join_channel_internal(connection_id, channel)

    async def _join_channel_internal(self, connection_id: str, channel: str):
        """Internal method to join channel (assumes lock is held)"""

        if connection_id not in self.connections:
            return False

        connected_user = self.connections[connection_id]

        # Add to channel subscriptions
        if channel not in self.channel_subscriptions:
            self.channel_subscriptions[channel] = set()

        self.channel_subscriptions[channel].add(connection_id)
        connected_user.channels.add(channel)

        logger.info(f"Connection {connection_id} joined channel {channel}")

        # Send channel history to new subscriber
        if channel in self.channel_history:
            for historical_message in self.channel_history[channel][-20:]:  # Last 20 messages
                await self.send_to_connection(connection_id, historical_message)

        # Notify channel about new member
        await self.broadcast_to_channel(
            channel,
            RealtimeMessage(
                id=str(uuid.uuid4()),
                type=MessageType.DOCUMENT_JOIN if channel.startswith("doc_") else MessageType.DEAL_JOIN,
                sender_id="system",
                channel=channel,
                payload={
                    "user_id": connected_user.user_id,
                    "user_info": connected_user.user_info,
                    "timestamp": datetime.utcnow().isoformat()
                }
            ),
            exclude_connections={connection_id},
            save_to_history=False
        )

        return True

    async def leave_channel(self, connection_id: str, channel: str):
        """Unsubscribe connection from a channel"""

        async with self.lock:
            await self._leave_channel_internal(connection_id, channel)

    async def _leave_channel_internal(self, connection_id: str, channel: str):
        """Internal method to leave channel (assumes lock is held)"""

        if connection_id not in self.connections:
            return False

        connected_user = self.connections[connection_id]

        # Remove from channel subscriptions
        if channel in self.channel_subscriptions:
            self.channel_subscriptions[channel].discard(connection_id)
            if not self.channel_subscriptions[channel]:
                del self.channel_subscriptions[channel]

        connected_user.channels.discard(channel)

        logger.info(f"Connection {connection_id} left channel {channel}")

        # Notify channel about member leaving
        if channel in self.channel_subscriptions:
            await self.broadcast_to_channel(
                channel,
                RealtimeMessage(
                    id=str(uuid.uuid4()),
                    type=MessageType.DOCUMENT_LEAVE if channel.startswith("doc_") else MessageType.DEAL_LEAVE,
                    sender_id="system",
                    channel=channel,
                    payload={
                        "user_id": connected_user.user_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                ),
                save_to_history=False
            )

        return True

    async def handle_message(self, connection_id: str, raw_message: str):
        """Handle incoming WebSocket message"""

        if connection_id not in self.connections:
            return

        connected_user = self.connections[connection_id]

        try:
            # Parse message
            message_data = json.loads(raw_message)

            message = RealtimeMessage(
                id=message_data.get('id', str(uuid.uuid4())),
                type=MessageType(message_data['type']),
                sender_id=connected_user.user_id,
                target_id=message_data.get('target_id'),
                channel=message_data.get('channel'),
                payload=message_data.get('payload', {}),
                organization_id=connected_user.organization_id
            )

            # Update user activity
            connected_user.last_activity = datetime.utcnow()

            # Route message based on type
            await self._route_message(connection_id, message)

        except Exception as e:
            logger.error(f"Failed to handle message from {connection_id}: {str(e)}")

            # Send error response
            await self.send_to_connection(connection_id, RealtimeMessage(
                id=str(uuid.uuid4()),
                type=MessageType.SYSTEM_MESSAGE,
                sender_id="system",
                payload={
                    "error": "Failed to process message",
                    "details": str(e)
                }
            ))

    async def _route_message(self, connection_id: str, message: RealtimeMessage):
        """Route message based on its type"""

        connected_user = self.connections[connection_id]

        if message.type == MessageType.HEARTBEAT:
            # Respond to heartbeat
            await self.send_to_connection(connection_id, RealtimeMessage(
                id=str(uuid.uuid4()),
                type=MessageType.HEARTBEAT,
                sender_id="system",
                payload={"timestamp": datetime.utcnow().isoformat()}
            ))

        elif message.type == MessageType.CHAT_MESSAGE:
            # Handle chat message
            if message.channel:
                await self.broadcast_to_channel(message.channel, message)
            elif message.target_id:
                await self.send_to_user(message.target_id, message)

        elif message.type in [MessageType.TYPING_START, MessageType.TYPING_STOP]:
            # Handle typing indicators
            if message.channel:
                await self.broadcast_to_channel(
                    message.channel,
                    message,
                    exclude_connections={connection_id},
                    save_to_history=False
                )

        elif message.type == MessageType.DOCUMENT_JOIN:
            # Join document collaboration
            if message.channel:
                await self.join_channel(connection_id, message.channel)

        elif message.type == MessageType.DOCUMENT_LEAVE:
            # Leave document collaboration
            if message.channel:
                await self.leave_channel(connection_id, message.channel)

        elif message.type in [MessageType.DOCUMENT_EDIT, MessageType.DOCUMENT_CURSOR, MessageType.DOCUMENT_SELECTION]:
            # Handle document collaboration
            if message.channel:
                await self.broadcast_to_channel(
                    message.channel,
                    message,
                    exclude_connections={connection_id}
                )

        elif message.type == MessageType.DEAL_JOIN:
            # Join deal collaboration
            if message.channel:
                await self.join_channel(connection_id, message.channel)

        elif message.type == MessageType.DEAL_LEAVE:
            # Leave deal collaboration
            if message.channel:
                await self.leave_channel(connection_id, message.channel)

        elif message.type in [MessageType.DEAL_UPDATE, MessageType.DEAL_ACTIVITY, MessageType.DEAL_STATUS_CHANGE]:
            # Handle deal updates
            if message.channel:
                await self.broadcast_to_channel(message.channel, message)
            else:
                # Broadcast to organization
                await self.broadcast_to_organization(
                    connected_user.organization_id,
                    message,
                    exclude_connections={connection_id}
                )

        elif message.type == MessageType.USER_STATUS:
            # Update user status
            new_status = message.payload.get('status')
            if new_status and new_status in [s.value for s in UserStatus]:
                connected_user.status = UserStatus(new_status)

                # Broadcast status change to organization
                await self.broadcast_to_organization(
                    connected_user.organization_id,
                    RealtimeMessage(
                        id=str(uuid.uuid4()),
                        type=MessageType.USER_STATUS,
                        sender_id="system",
                        payload={
                            "user_id": connected_user.user_id,
                            "status": new_status,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    ),
                    exclude_connections={connection_id}
                )

        elif message.type in [MessageType.VIDEO_CALL_INVITE, MessageType.VIDEO_CALL_ACCEPT,
                               MessageType.VIDEO_CALL_DECLINE, MessageType.VIDEO_CALL_END]:
            # Handle video call messages
            if message.target_id:
                await self.send_to_user(message.target_id, message)

        elif message.type in [MessageType.TASK_CREATED, MessageType.TASK_UPDATED,
                               MessageType.TASK_ASSIGNED, MessageType.TASK_COMPLETED]:
            # Handle task management messages
            if message.channel:
                await self.broadcast_to_channel(message.channel, message)
            else:
                await self.broadcast_to_organization(
                    connected_user.organization_id,
                    message,
                    exclude_connections={connection_id}
                )

    def get_online_users(self, organization_id: str) -> List[Dict[str, Any]]:
        """Get list of online users in an organization"""

        online_users = []
        seen_users = set()

        if organization_id in self.organization_connections:
            for connection_id in self.organization_connections[organization_id]:
                if connection_id in self.connections:
                    connected_user = self.connections[connection_id]

                    if connected_user.user_id not in seen_users:
                        seen_users.add(connected_user.user_id)
                        online_users.append({
                            "user_id": connected_user.user_id,
                            "status": connected_user.status.value,
                            "last_activity": connected_user.last_activity.isoformat(),
                            "user_info": connected_user.user_info,
                            "channels": list(connected_user.channels)
                        })

        return online_users

    def get_channel_members(self, channel: str) -> List[Dict[str, Any]]:
        """Get list of members in a channel"""

        members = []

        if channel in self.channel_subscriptions:
            for connection_id in self.channel_subscriptions[channel]:
                if connection_id in self.connections:
                    connected_user = self.connections[connection_id]
                    members.append({
                        "user_id": connected_user.user_id,
                        "user_info": connected_user.user_info,
                        "status": connected_user.status.value,
                        "last_activity": connected_user.last_activity.isoformat()
                    })

        return members

    async def cleanup_stale_connections(self, max_idle_minutes: int = 30):
        """Remove stale connections that haven't been active"""

        cutoff_time = datetime.utcnow().timestamp() - (max_idle_minutes * 60)
        stale_connections = []

        async with self.lock:
            for connection_id, connected_user in self.connections.items():
                if connected_user.last_activity.timestamp() < cutoff_time:
                    stale_connections.append(connection_id)

            for connection_id in stale_connections:
                logger.info(f"Removing stale connection {connection_id}")
                await self.disconnect(connection_id)

        return len(stale_connections)


# Global WebSocket manager instance
websocket_manager = WebSocketManager()

def get_websocket_manager() -> WebSocketManager:
    """Get the global WebSocket manager instance"""
    return websocket_manager