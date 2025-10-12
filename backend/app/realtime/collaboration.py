"""
Real-Time Document Collaboration System
Operational Transformation (OT) for collaborative document editing
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from .websocket_manager import websocket_manager, RealtimeMessage, MessageType

logger = logging.getLogger(__name__)


class OperationType(str, Enum):
    """Document operation types"""
    INSERT = "insert"
    DELETE = "delete"
    RETAIN = "retain"
    FORMAT = "format"


class CursorType(str, Enum):
    """Cursor types for collaborative editing"""
    SELECTION = "selection"
    CURSOR = "cursor"


@dataclass
class DocumentOperation:
    """Document operation for operational transformation"""
    id: str
    type: OperationType
    position: int
    content: Optional[str] = None
    length: Optional[int] = None
    attributes: Optional[Dict[str, Any]] = None
    user_id: str = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class CursorPosition:
    """User cursor position in document"""
    user_id: str
    document_id: str
    type: CursorType
    start_position: int
    end_position: Optional[int] = None
    user_info: Optional[Dict[str, Any]] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.end_position is None:
            self.end_position = self.start_position


@dataclass
class DocumentState:
    """Current state of a collaborative document"""
    document_id: str
    content: str
    version: int
    operations: List[DocumentOperation]
    active_users: Dict[str, Dict[str, Any]]
    cursors: Dict[str, CursorPosition]
    last_modified: datetime
    locked_by: Optional[str] = None
    locked_at: Optional[datetime] = None

    def __post_init__(self):
        if self.operations is None:
            self.operations = []
        if self.active_users is None:
            self.active_users = {}
        if self.cursors is None:
            self.cursors = {}


class OperationalTransform:
    """Operational Transformation engine for conflict resolution"""

    @staticmethod
    def transform_operation(op1: DocumentOperation, op2: DocumentOperation) -> Tuple[DocumentOperation, DocumentOperation]:
        """Transform two concurrent operations for conflict resolution"""

        # Create copies to avoid modifying originals
        transformed_op1 = DocumentOperation(
            id=op1.id,
            type=op1.type,
            position=op1.position,
            content=op1.content,
            length=op1.length,
            attributes=op1.attributes,
            user_id=op1.user_id,
            timestamp=op1.timestamp
        )

        transformed_op2 = DocumentOperation(
            id=op2.id,
            type=op2.type,
            position=op2.position,
            content=op2.content,
            length=op2.length,
            attributes=op2.attributes,
            user_id=op2.user_id,
            timestamp=op2.timestamp
        )

        # Transform based on operation types
        if op1.type == OperationType.INSERT and op2.type == OperationType.INSERT:
            # Both insertions
            if op1.position <= op2.position:
                transformed_op2.position += len(op1.content) if op1.content else 0
            else:
                transformed_op1.position += len(op2.content) if op2.content else 0

        elif op1.type == OperationType.INSERT and op2.type == OperationType.DELETE:
            # Insert vs Delete
            if op1.position <= op2.position:
                transformed_op2.position += len(op1.content) if op1.content else 0
            elif op1.position < op2.position + (op2.length or 0):
                # Insert is within delete range
                delete_split = op1.position - op2.position
                transformed_op2.length = delete_split
                # Create second delete operation for remainder if needed

        elif op1.type == OperationType.DELETE and op2.type == OperationType.INSERT:
            # Delete vs Insert
            if op2.position <= op1.position:
                transformed_op1.position += len(op2.content) if op2.content else 0
            elif op2.position < op1.position + (op1.length or 0):
                # Insert is within delete range
                delete_split = op2.position - op1.position
                transformed_op1.length = delete_split

        elif op1.type == OperationType.DELETE and op2.type == OperationType.DELETE:
            # Both deletions
            if op1.position + (op1.length or 0) <= op2.position:
                # op1 is completely before op2
                transformed_op2.position -= op1.length or 0
            elif op2.position + (op2.length or 0) <= op1.position:
                # op2 is completely before op1
                transformed_op1.position -= op2.length or 0
            else:
                # Overlapping deletions - complex case
                # Simplification: adjust lengths based on overlap
                overlap_start = max(op1.position, op2.position)
                overlap_end = min(
                    op1.position + (op1.length or 0),
                    op2.position + (op2.length or 0)
                )
                overlap_length = max(0, overlap_end - overlap_start)

                if op1.position < op2.position:
                    transformed_op1.length = (op1.length or 0) - overlap_length
                    transformed_op2.position = op1.position
                    transformed_op2.length = (op2.length or 0) - overlap_length
                else:
                    transformed_op2.length = (op2.length or 0) - overlap_length
                    transformed_op1.position = op2.position
                    transformed_op1.length = (op1.length or 0) - overlap_length

        return transformed_op1, transformed_op2

    @staticmethod
    def apply_operation(content: str, operation: DocumentOperation) -> str:
        """Apply an operation to document content"""

        if operation.type == OperationType.INSERT:
            if operation.content:
                return (
                    content[:operation.position] +
                    operation.content +
                    content[operation.position:]
                )

        elif operation.type == OperationType.DELETE:
            if operation.length:
                return (
                    content[:operation.position] +
                    content[operation.position + operation.length:]
                )

        elif operation.type == OperationType.RETAIN:
            # Retain operation doesn't change content
            return content

        return content

    @staticmethod
    def transform_cursor_position(cursor: CursorPosition, operation: DocumentOperation) -> CursorPosition:
        """Transform cursor position based on document operation"""

        new_cursor = CursorPosition(
            user_id=cursor.user_id,
            document_id=cursor.document_id,
            type=cursor.type,
            start_position=cursor.start_position,
            end_position=cursor.end_position,
            user_info=cursor.user_info,
            timestamp=datetime.utcnow()
        )

        if operation.type == OperationType.INSERT:
            if operation.position <= cursor.start_position:
                new_cursor.start_position += len(operation.content) if operation.content else 0
            if cursor.end_position and operation.position <= cursor.end_position:
                new_cursor.end_position += len(operation.content) if operation.content else 0

        elif operation.type == OperationType.DELETE:
            delete_end = operation.position + (operation.length or 0)

            if delete_end <= cursor.start_position:
                # Delete is before cursor
                new_cursor.start_position -= operation.length or 0
            elif operation.position < cursor.start_position:
                # Delete overlaps cursor start
                new_cursor.start_position = operation.position

            if cursor.end_position:
                if delete_end <= cursor.end_position:
                    # Delete is before cursor end
                    new_cursor.end_position -= operation.length or 0
                elif operation.position < cursor.end_position:
                    # Delete overlaps cursor end
                    new_cursor.end_position = operation.position

        return new_cursor


class CollaborativeDocumentManager:
    """Manages real-time collaborative document editing"""

    def __init__(self):
        # Document states: document_id -> DocumentState
        self.documents: Dict[str, DocumentState] = {}

        # Operation queues for each document: document_id -> List[DocumentOperation]
        self.operation_queues: Dict[str, List[DocumentOperation]] = {}

        # Lock for thread-safe operations
        self.lock = asyncio.Lock()

    async def join_document(
        self,
        document_id: str,
        user_id: str,
        user_info: Dict[str, Any],
        organization_id: str
    ) -> DocumentState:
        """User joins document collaboration"""

        async with self.lock:
            # Initialize document state if not exists
            if document_id not in self.documents:
                self.documents[document_id] = DocumentState(
                    document_id=document_id,
                    content="",  # Would load from database
                    version=0,
                    operations=[],
                    active_users={},
                    cursors={},
                    last_modified=datetime.utcnow()
                )

            # Add user to active users
            self.documents[document_id].active_users[user_id] = {
                "user_id": user_id,
                "user_info": user_info,
                "joined_at": datetime.utcnow().isoformat(),
                "organization_id": organization_id
            }

            # Join WebSocket channel
            channel = f"doc_{document_id}"
            # Note: This would be called from the WebSocket endpoint
            # await websocket_manager.join_channel(connection_id, channel)

            logger.info(f"User {user_id} joined document {document_id}")

            return self.documents[document_id]

    async def leave_document(self, document_id: str, user_id: str):
        """User leaves document collaboration"""

        async with self.lock:
            if document_id in self.documents:
                # Remove user from active users
                self.documents[document_id].active_users.pop(user_id, None)

                # Remove user's cursor
                self.documents[document_id].cursors.pop(user_id, None)

                # Clean up empty document sessions
                if not self.documents[document_id].active_users:
                    # Save document state to database here
                    del self.documents[document_id]
                    if document_id in self.operation_queues:
                        del self.operation_queues[document_id]

                logger.info(f"User {user_id} left document {document_id}")

    async def apply_operation(
        self,
        document_id: str,
        operation: DocumentOperation,
        user_id: str
    ) -> Optional[DocumentOperation]:
        """Apply operation to document with operational transformation"""

        async with self.lock:
            if document_id not in self.documents:
                logger.warning(f"Document {document_id} not found")
                return None

            doc_state = self.documents[document_id]

            # Initialize operation queue if needed
            if document_id not in self.operation_queues:
                self.operation_queues[document_id] = []

            # Transform operation against pending operations
            transformed_operation = operation
            for pending_op in self.operation_queues[document_id]:
                if pending_op.user_id != user_id:
                    transformed_operation, _ = OperationalTransform.transform_operation(
                        transformed_operation, pending_op
                    )

            # Apply operation to document content
            try:
                new_content = OperationalTransform.apply_operation(
                    doc_state.content, transformed_operation
                )

                # Update document state
                doc_state.content = new_content
                doc_state.version += 1
                doc_state.last_modified = datetime.utcnow()
                doc_state.operations.append(transformed_operation)

                # Keep only last 100 operations
                if len(doc_state.operations) > 100:
                    doc_state.operations = doc_state.operations[-100:]

                # Transform all user cursors
                for cursor_user_id, cursor in doc_state.cursors.items():
                    if cursor_user_id != user_id:
                        doc_state.cursors[cursor_user_id] = OperationalTransform.transform_cursor_position(
                            cursor, transformed_operation
                        )

                # Add to operation queue
                self.operation_queues[document_id].append(transformed_operation)

                # Keep only last 50 operations in queue
                if len(self.operation_queues[document_id]) > 50:
                    self.operation_queues[document_id] = self.operation_queues[document_id][-50:]

                logger.info(f"Applied operation {transformed_operation.id} to document {document_id}")

                # Broadcast operation to other users
                await self._broadcast_operation(document_id, transformed_operation, user_id)

                return transformed_operation

            except Exception as e:
                logger.error(f"Failed to apply operation to document {document_id}: {str(e)}")
                return None

    async def update_cursor(
        self,
        document_id: str,
        cursor: CursorPosition
    ):
        """Update user cursor position"""

        async with self.lock:
            if document_id in self.documents:
                self.documents[document_id].cursors[cursor.user_id] = cursor

                # Broadcast cursor update to other users
                await self._broadcast_cursor_update(document_id, cursor)

    async def _broadcast_operation(
        self,
        document_id: str,
        operation: DocumentOperation,
        sender_user_id: str
    ):
        """Broadcast operation to other document collaborators"""

        channel = f"doc_{document_id}"

        message = RealtimeMessage(
            id=operation.id,
            type=MessageType.DOCUMENT_EDIT,
            sender_id=sender_user_id,
            channel=channel,
            payload={
                "document_id": document_id,
                "operation": {
                    "id": operation.id,
                    "type": operation.type.value,
                    "position": operation.position,
                    "content": operation.content,
                    "length": operation.length,
                    "attributes": operation.attributes,
                    "timestamp": operation.timestamp.isoformat()
                },
                "document_version": self.documents[document_id].version,
                "content_length": len(self.documents[document_id].content)
            }
        )

        await websocket_manager.broadcast_to_channel(
            channel,
            message,
            exclude_connections=set(),  # Would exclude sender's connections
            save_to_history=False
        )

    async def _broadcast_cursor_update(
        self,
        document_id: str,
        cursor: CursorPosition
    ):
        """Broadcast cursor update to other document collaborators"""

        channel = f"doc_{document_id}"

        message = RealtimeMessage(
            id=str(uuid.uuid4()),
            type=MessageType.DOCUMENT_CURSOR,
            sender_id=cursor.user_id,
            channel=channel,
            payload={
                "document_id": document_id,
                "cursor": {
                    "user_id": cursor.user_id,
                    "type": cursor.type.value,
                    "start_position": cursor.start_position,
                    "end_position": cursor.end_position,
                    "user_info": cursor.user_info,
                    "timestamp": cursor.timestamp.isoformat()
                }
            }
        )

        await websocket_manager.broadcast_to_channel(
            channel,
            message,
            exclude_connections=set(),  # Would exclude sender's connections
            save_to_history=False
        )

    async def get_document_state(self, document_id: str) -> Optional[DocumentState]:
        """Get current document state"""

        return self.documents.get(document_id)

    async def lock_document(self, document_id: str, user_id: str) -> bool:
        """Lock document for exclusive editing"""

        async with self.lock:
            if document_id not in self.documents:
                return False

            doc_state = self.documents[document_id]

            if doc_state.locked_by and doc_state.locked_by != user_id:
                return False

            doc_state.locked_by = user_id
            doc_state.locked_at = datetime.utcnow()

            # Broadcast lock status to collaborators
            channel = f"doc_{document_id}"
            message = RealtimeMessage(
                id=str(uuid.uuid4()),
                type=MessageType.SYSTEM_MESSAGE,
                sender_id="system",
                channel=channel,
                payload={
                    "document_id": document_id,
                    "action": "document_locked",
                    "locked_by": user_id,
                    "locked_at": doc_state.locked_at.isoformat()
                }
            )

            await websocket_manager.broadcast_to_channel(channel, message, save_to_history=False)

            logger.info(f"Document {document_id} locked by user {user_id}")
            return True

    async def unlock_document(self, document_id: str, user_id: str) -> bool:
        """Unlock document"""

        async with self.lock:
            if document_id not in self.documents:
                return False

            doc_state = self.documents[document_id]

            if doc_state.locked_by != user_id:
                return False

            doc_state.locked_by = None
            doc_state.locked_at = None

            # Broadcast unlock status to collaborators
            channel = f"doc_{document_id}"
            message = RealtimeMessage(
                id=str(uuid.uuid4()),
                type=MessageType.SYSTEM_MESSAGE,
                sender_id="system",
                channel=channel,
                payload={
                    "document_id": document_id,
                    "action": "document_unlocked",
                    "unlocked_by": user_id,
                    "unlocked_at": datetime.utcnow().isoformat()
                }
            )

            await websocket_manager.broadcast_to_channel(channel, message, save_to_history=False)

            logger.info(f"Document {document_id} unlocked by user {user_id}")
            return True

    async def get_document_collaborators(self, document_id: str) -> List[Dict[str, Any]]:
        """Get list of active collaborators"""

        if document_id not in self.documents:
            return []

        collaborators = []
        doc_state = self.documents[document_id]

        for user_id, user_data in doc_state.active_users.items():
            cursor = doc_state.cursors.get(user_id)
            collaborators.append({
                "user_id": user_id,
                "user_info": user_data.get("user_info", {}),
                "joined_at": user_data.get("joined_at"),
                "cursor": {
                    "start_position": cursor.start_position,
                    "end_position": cursor.end_position,
                    "type": cursor.type.value
                } if cursor else None
            })

        return collaborators

    async def save_document(self, document_id: str) -> bool:
        """Save document to persistent storage"""

        if document_id not in self.documents:
            return False

        doc_state = self.documents[document_id]

        try:
            # Here you would save to database
            # await save_to_database(document_id, doc_state.content, doc_state.version)

            logger.info(f"Saved document {document_id} version {doc_state.version}")
            return True

        except Exception as e:
            logger.error(f"Failed to save document {document_id}: {str(e)}")
            return False


# Global collaborative document manager instance
document_manager = CollaborativeDocumentManager()