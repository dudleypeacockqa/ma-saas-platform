"""
Offline Synchronization Service
Handles offline-first data synchronization for mobile devices
"""

import json
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import hashlib
import uuid

logger = logging.getLogger(__name__)


class SyncOperation(str, Enum):
    """Types of sync operations"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    CONFLICT_RESOLUTION = "conflict_resolution"


class SyncStatus(str, Enum):
    """Sync operation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


class ConflictResolution(str, Enum):
    """Conflict resolution strategies"""
    CLIENT_WINS = "client_wins"
    SERVER_WINS = "server_wins"
    MERGE = "merge"
    MANUAL = "manual"


@dataclass
class SyncItem:
    """Individual item to be synchronized"""
    id: str
    entity_type: str  # deals, documents, users, etc.
    entity_id: str
    operation: SyncOperation
    data: Dict[str, Any]
    client_timestamp: datetime
    server_timestamp: Optional[datetime]
    user_id: str
    organization_id: str
    checksum: str
    version: int
    status: SyncStatus = SyncStatus.PENDING
    retry_count: int = 0
    error_message: Optional[str] = None

    def generate_checksum(self) -> str:
        """Generate checksum for data integrity"""
        data_str = json.dumps(self.data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()


@dataclass
class SyncConflict:
    """Represents a synchronization conflict"""
    id: str
    entity_type: str
    entity_id: str
    client_data: Dict[str, Any]
    server_data: Dict[str, Any]
    client_timestamp: datetime
    server_timestamp: datetime
    user_id: str
    organization_id: str
    resolution_strategy: Optional[ConflictResolution] = None
    resolved_data: Optional[Dict[str, Any]] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class OfflineSyncService:
    """Service for handling offline-first data synchronization"""

    def __init__(self):
        self.pending_sync_items: Dict[str, SyncItem] = {}
        self.sync_conflicts: Dict[str, SyncConflict] = {}
        self.sync_queue: asyncio.Queue = asyncio.Queue()
        self.is_running = False
        self.sync_workers: List[asyncio.Task] = []
        self.last_sync_timestamps: Dict[str, datetime] = {}  # user_id -> last_sync

    async def start_service(self, num_workers: int = 3):
        """Start the offline sync service"""
        self.is_running = True

        # Start sync workers
        for i in range(num_workers):
            worker = asyncio.create_task(self._sync_worker(f"worker-{i}"))
            self.sync_workers.append(worker)

        logger.info(f"Offline sync service started with {num_workers} workers")

    async def stop_service(self):
        """Stop the offline sync service"""
        self.is_running = False

        # Cancel all workers
        for worker in self.sync_workers:
            worker.cancel()

        # Wait for workers to finish
        await asyncio.gather(*self.sync_workers, return_exceptions=True)
        self.sync_workers.clear()

        logger.info("Offline sync service stopped")

    async def queue_sync_item(self, sync_item: SyncItem) -> str:
        """Queue an item for synchronization"""

        # Generate checksum for data integrity
        sync_item.checksum = sync_item.generate_checksum()

        # Store pending sync item
        self.pending_sync_items[sync_item.id] = sync_item

        # Add to sync queue
        await self.sync_queue.put(sync_item)

        logger.info(f"Queued sync item {sync_item.id} for {sync_item.entity_type}")
        return sync_item.id

    async def create_sync_item(
        self,
        entity_type: str,
        entity_id: str,
        operation: SyncOperation,
        data: Dict[str, Any],
        user_id: str,
        organization_id: str,
        client_timestamp: Optional[datetime] = None
    ) -> str:
        """Create and queue a new sync item"""

        sync_item = SyncItem(
            id=str(uuid.uuid4()),
            entity_type=entity_type,
            entity_id=entity_id,
            operation=operation,
            data=data,
            client_timestamp=client_timestamp or datetime.utcnow(),
            server_timestamp=None,
            user_id=user_id,
            organization_id=organization_id,
            checksum="",
            version=1
        )

        return await self.queue_sync_item(sync_item)

    async def _sync_worker(self, worker_id: str):
        """Background worker to process sync queue"""

        logger.info(f"Sync worker {worker_id} started")

        while self.is_running:
            try:
                # Get sync item from queue with timeout
                sync_item = await asyncio.wait_for(self.sync_queue.get(), timeout=1.0)
                await self._process_sync_item(sync_item, worker_id)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Sync worker {worker_id} error: {e}")
                await asyncio.sleep(1)

        logger.info(f"Sync worker {worker_id} stopped")

    async def _process_sync_item(self, sync_item: SyncItem, worker_id: str):
        """Process a single sync item"""

        try:
            sync_item.status = SyncStatus.IN_PROGRESS
            logger.info(f"Worker {worker_id} processing sync item {sync_item.id}")

            # Validate checksum
            current_checksum = sync_item.generate_checksum()
            if current_checksum != sync_item.checksum:
                raise ValueError("Data integrity check failed - checksum mismatch")

            # Process based on operation type
            if sync_item.operation == SyncOperation.CREATE:
                result = await self._sync_create_operation(sync_item)
            elif sync_item.operation == SyncOperation.UPDATE:
                result = await self._sync_update_operation(sync_item)
            elif sync_item.operation == SyncOperation.DELETE:
                result = await self._sync_delete_operation(sync_item)
            else:
                raise ValueError(f"Unknown sync operation: {sync_item.operation}")

            if result.get("conflict"):
                await self._handle_sync_conflict(sync_item, result["server_data"])
            else:
                sync_item.status = SyncStatus.COMPLETED
                sync_item.server_timestamp = datetime.utcnow()

                # Remove from pending items
                if sync_item.id in self.pending_sync_items:
                    del self.pending_sync_items[sync_item.id]

                logger.info(f"Successfully synced item {sync_item.id}")

        except Exception as e:
            sync_item.status = SyncStatus.FAILED
            sync_item.error_message = str(e)
            sync_item.retry_count += 1

            logger.error(f"Failed to sync item {sync_item.id}: {e}")

            # Retry logic
            if sync_item.retry_count < 3:
                sync_item.status = SyncStatus.PENDING
                await asyncio.sleep(2 ** sync_item.retry_count)  # Exponential backoff
                await self.sync_queue.put(sync_item)

    async def _sync_create_operation(self, sync_item: SyncItem) -> Dict[str, Any]:
        """Process CREATE sync operation"""

        # Check if entity already exists on server
        existing_entity = await self._get_server_entity(
            sync_item.entity_type,
            sync_item.entity_id,
            sync_item.organization_id
        )

        if existing_entity:
            # Entity exists - this is a conflict
            return {
                "conflict": True,
                "server_data": existing_entity
            }

        # Create new entity on server
        created_entity = await self._create_server_entity(
            sync_item.entity_type,
            sync_item.data,
            sync_item.organization_id,
            sync_item.user_id
        )

        return {
            "conflict": False,
            "server_data": created_entity
        }

    async def _sync_update_operation(self, sync_item: SyncItem) -> Dict[str, Any]:
        """Process UPDATE sync operation"""

        # Get current server version
        server_entity = await self._get_server_entity(
            sync_item.entity_type,
            sync_item.entity_id,
            sync_item.organization_id
        )

        if not server_entity:
            # Entity doesn't exist - convert to CREATE
            return await self._sync_create_operation(sync_item)

        # Check for conflicts (version comparison)
        server_version = server_entity.get("version", 1)
        if server_version > sync_item.version:
            return {
                "conflict": True,
                "server_data": server_entity
            }

        # Update entity on server
        updated_entity = await self._update_server_entity(
            sync_item.entity_type,
            sync_item.entity_id,
            sync_item.data,
            sync_item.organization_id,
            sync_item.user_id
        )

        return {
            "conflict": False,
            "server_data": updated_entity
        }

    async def _sync_delete_operation(self, sync_item: SyncItem) -> Dict[str, Any]:
        """Process DELETE sync operation"""

        # Check if entity still exists on server
        server_entity = await self._get_server_entity(
            sync_item.entity_type,
            sync_item.entity_id,
            sync_item.organization_id
        )

        if not server_entity:
            # Already deleted - success
            return {"conflict": False, "server_data": None}

        # Delete entity on server
        await self._delete_server_entity(
            sync_item.entity_type,
            sync_item.entity_id,
            sync_item.organization_id,
            sync_item.user_id
        )

        return {"conflict": False, "server_data": None}

    async def _handle_sync_conflict(self, sync_item: SyncItem, server_data: Dict[str, Any]):
        """Handle synchronization conflict"""

        conflict = SyncConflict(
            id=str(uuid.uuid4()),
            entity_type=sync_item.entity_type,
            entity_id=sync_item.entity_id,
            client_data=sync_item.data,
            server_data=server_data,
            client_timestamp=sync_item.client_timestamp,
            server_timestamp=datetime.utcnow(),
            user_id=sync_item.user_id,
            organization_id=sync_item.organization_id
        )

        self.sync_conflicts[conflict.id] = conflict
        sync_item.status = SyncStatus.CONFLICT

        logger.warning(f"Sync conflict detected for {sync_item.entity_type} {sync_item.entity_id}")

    async def resolve_conflict(
        self,
        conflict_id: str,
        resolution_strategy: ConflictResolution,
        resolved_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Resolve a synchronization conflict"""

        if conflict_id not in self.sync_conflicts:
            return False

        conflict = self.sync_conflicts[conflict_id]
        conflict.resolution_strategy = resolution_strategy

        if resolution_strategy == ConflictResolution.CLIENT_WINS:
            conflict.resolved_data = conflict.client_data
        elif resolution_strategy == ConflictResolution.SERVER_WINS:
            conflict.resolved_data = conflict.server_data
        elif resolution_strategy == ConflictResolution.MERGE:
            conflict.resolved_data = self._merge_data(conflict.client_data, conflict.server_data)
        elif resolution_strategy == ConflictResolution.MANUAL:
            if not resolved_data:
                raise ValueError("Manual resolution requires resolved_data")
            conflict.resolved_data = resolved_data

        # Apply resolution
        try:
            await self._update_server_entity(
                conflict.entity_type,
                conflict.entity_id,
                conflict.resolved_data,
                conflict.organization_id,
                conflict.user_id
            )

            # Remove resolved conflict
            del self.sync_conflicts[conflict_id]

            logger.info(f"Resolved conflict {conflict_id} using {resolution_strategy}")
            return True

        except Exception as e:
            logger.error(f"Failed to resolve conflict {conflict_id}: {e}")
            return False

    def _merge_data(self, client_data: Dict[str, Any], server_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge client and server data (simple merge strategy)"""

        merged = server_data.copy()

        for key, value in client_data.items():
            if key not in merged or merged[key] != value:
                # Simple strategy: take client value if different
                # In a real implementation, this would be more sophisticated
                merged[key] = value

        return merged

    async def get_pending_sync_items(self, user_id: str, organization_id: str) -> List[Dict[str, Any]]:
        """Get pending sync items for a user"""

        pending_items = []
        for sync_item in self.pending_sync_items.values():
            if (sync_item.user_id == user_id and
                sync_item.organization_id == organization_id):
                pending_items.append({
                    "id": sync_item.id,
                    "entity_type": sync_item.entity_type,
                    "entity_id": sync_item.entity_id,
                    "operation": sync_item.operation,
                    "status": sync_item.status,
                    "client_timestamp": sync_item.client_timestamp.isoformat(),
                    "retry_count": sync_item.retry_count,
                    "error_message": sync_item.error_message
                })

        return pending_items

    async def get_sync_conflicts(self, user_id: str, organization_id: str) -> List[Dict[str, Any]]:
        """Get sync conflicts for a user"""

        conflicts = []
        for conflict in self.sync_conflicts.values():
            if (conflict.user_id == user_id and
                conflict.organization_id == organization_id):
                conflicts.append({
                    "id": conflict.id,
                    "entity_type": conflict.entity_type,
                    "entity_id": conflict.entity_id,
                    "client_data": conflict.client_data,
                    "server_data": conflict.server_data,
                    "client_timestamp": conflict.client_timestamp.isoformat(),
                    "server_timestamp": conflict.server_timestamp.isoformat(),
                    "created_at": conflict.created_at.isoformat(),
                    "resolution_strategy": conflict.resolution_strategy
                })

        return conflicts

    async def perform_full_sync(self, user_id: str, organization_id: str) -> Dict[str, Any]:
        """Perform full synchronization for a user"""

        start_time = datetime.utcnow()

        # Get last sync timestamp
        last_sync = self.last_sync_timestamps.get(user_id, datetime.min)

        # Get server changes since last sync
        server_changes = await self._get_server_changes_since(
            organization_id, last_sync
        )

        # Process server changes
        applied_changes = 0
        conflicts_created = 0

        for change in server_changes:
            # Check for local conflicts
            if await self._has_local_changes(change["entity_type"], change["entity_id"], user_id):
                # Create conflict
                await self._create_conflict_from_server_change(change, user_id, organization_id)
                conflicts_created += 1
            else:
                # Apply server change locally
                await self._apply_server_change_locally(change, user_id, organization_id)
                applied_changes += 1

        # Update last sync timestamp
        self.last_sync_timestamps[user_id] = start_time

        sync_duration = (datetime.utcnow() - start_time).total_seconds()

        return {
            "sync_completed_at": start_time.isoformat(),
            "duration_seconds": sync_duration,
            "server_changes_applied": applied_changes,
            "conflicts_created": conflicts_created,
            "pending_items": len(await self.get_pending_sync_items(user_id, organization_id)),
            "total_conflicts": len(await self.get_sync_conflicts(user_id, organization_id))
        }

    # Mock server interaction methods (would integrate with actual database)

    async def _get_server_entity(self, entity_type: str, entity_id: str, organization_id: str) -> Optional[Dict[str, Any]]:
        """Get entity from server"""
        # Mock implementation - would query actual database
        await asyncio.sleep(0.1)  # Simulate network delay
        return None

    async def _create_server_entity(self, entity_type: str, data: Dict[str, Any], organization_id: str, user_id: str) -> Dict[str, Any]:
        """Create entity on server"""
        # Mock implementation - would create in actual database
        await asyncio.sleep(0.1)  # Simulate network delay
        return {**data, "id": str(uuid.uuid4()), "version": 1, "created_at": datetime.utcnow().isoformat()}

    async def _update_server_entity(self, entity_type: str, entity_id: str, data: Dict[str, Any], organization_id: str, user_id: str) -> Dict[str, Any]:
        """Update entity on server"""
        # Mock implementation - would update in actual database
        await asyncio.sleep(0.1)  # Simulate network delay
        return {**data, "id": entity_id, "version": data.get("version", 1) + 1, "updated_at": datetime.utcnow().isoformat()}

    async def _delete_server_entity(self, entity_type: str, entity_id: str, organization_id: str, user_id: str):
        """Delete entity on server"""
        # Mock implementation - would delete from actual database
        await asyncio.sleep(0.1)  # Simulate network delay
        pass

    async def _get_server_changes_since(self, organization_id: str, since: datetime) -> List[Dict[str, Any]]:
        """Get server changes since timestamp"""
        # Mock implementation - would query actual database
        await asyncio.sleep(0.1)  # Simulate network delay
        return []

    async def _has_local_changes(self, entity_type: str, entity_id: str, user_id: str) -> bool:
        """Check if entity has pending local changes"""
        # Mock implementation - would check local storage
        return False

    async def _create_conflict_from_server_change(self, change: Dict[str, Any], user_id: str, organization_id: str):
        """Create conflict from server change"""
        # Mock implementation - would create conflict record
        pass

    async def _apply_server_change_locally(self, change: Dict[str, Any], user_id: str, organization_id: str):
        """Apply server change to local storage"""
        # Mock implementation - would update local storage
        pass


# Global offline sync service instance
offline_sync_service: Optional[OfflineSyncService] = None

def get_offline_sync_service() -> OfflineSyncService:
    """Get the global offline sync service instance"""
    global offline_sync_service
    if offline_sync_service is None:
        offline_sync_service = OfflineSyncService()
    return offline_sync_service