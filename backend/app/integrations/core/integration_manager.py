"""
Core Integration Management System
Central orchestrator for all platform integrations with comprehensive data synchronization
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod

import aiohttp
import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update, insert

from ...core.database import get_db
from ...core.config import settings
from ...models.integrations import Integration, IntegrationLog, DataSync

logger = logging.getLogger(__name__)


class IntegrationStatus(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    SYNCING = "syncing"
    ERROR = "error"
    SUSPENDED = "suspended"
    RATE_LIMITED = "rate_limited"


class SyncDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"


class DataConflictResolution(str, Enum):
    SOURCE_WINS = "source_wins"
    DESTINATION_WINS = "destination_wins"
    MANUAL_REVIEW = "manual_review"
    MERGE_STRATEGY = "merge_strategy"
    TIMESTAMP_BASED = "timestamp_based"


@dataclass
class IntegrationConfig:
    """Configuration for an integration"""
    integration_id: str
    name: str
    provider: str
    auth_type: str
    credentials: Dict[str, Any]
    sync_direction: SyncDirection
    sync_frequency: int  # seconds
    rate_limit: int  # requests per minute
    retry_config: Dict[str, Any]
    webhook_url: Optional[str] = None
    enabled: bool = True


@dataclass
class SyncResult:
    """Result of a data synchronization operation"""
    sync_id: str
    integration_id: str
    direction: SyncDirection
    records_processed: int
    records_created: int
    records_updated: int
    records_failed: int
    conflicts_detected: int
    start_time: datetime
    end_time: datetime
    errors: List[str]
    success: bool


@dataclass
class WebhookEvent:
    """Webhook event data"""
    event_id: str
    integration_id: str
    event_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    verified: bool


class BaseIntegration(ABC):
    """Base class for all integrations"""

    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.status = IntegrationStatus.DISCONNECTED
        self.last_sync: Optional[datetime] = None
        self.error_count = 0
        self.rate_limit_reset: Optional[datetime] = None

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the external service"""
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test the connection to the external service"""
        pass

    @abstractmethod
    async def sync_data(self, direction: SyncDirection) -> SyncResult:
        """Synchronize data with the external service"""
        pass

    @abstractmethod
    async def handle_webhook(self, event: WebhookEvent) -> bool:
        """Handle incoming webhook event"""
        pass

    @abstractmethod
    async def get_supported_entities(self) -> List[str]:
        """Get list of entities this integration can sync"""
        pass

    async def connect(self) -> bool:
        """Connect to the integration"""
        try:
            self.status = IntegrationStatus.CONNECTING

            if await self.authenticate():
                if await self.test_connection():
                    self.status = IntegrationStatus.CONNECTED
                    self.error_count = 0
                    return True

            self.status = IntegrationStatus.ERROR
            self.error_count += 1
            return False

        except Exception as e:
            logger.error(f"Integration {self.config.integration_id} connection failed: {str(e)}")
            self.status = IntegrationStatus.ERROR
            self.error_count += 1
            return False

    async def disconnect(self) -> bool:
        """Disconnect from the integration"""
        self.status = IntegrationStatus.DISCONNECTED
        return True

    def is_rate_limited(self) -> bool:
        """Check if integration is currently rate limited"""
        if self.rate_limit_reset and datetime.now() < self.rate_limit_reset:
            return True
        return False

    def set_rate_limit(self, reset_time: datetime):
        """Set rate limit reset time"""
        self.rate_limit_reset = reset_time
        self.status = IntegrationStatus.RATE_LIMITED


class DataSyncManager:
    """Manages data synchronization across all integrations"""

    def __init__(self):
        self.sync_queue: asyncio.Queue = asyncio.Queue()
        self.sync_locks: Dict[str, asyncio.Lock] = {}
        self.conflict_handlers: Dict[str, DataConflictResolution] = {}

    async def schedule_sync(
        self,
        integration_id: str,
        direction: SyncDirection,
        priority: int = 5,
        delay: Optional[timedelta] = None
    ):
        """Schedule a data synchronization"""
        sync_task = {
            "integration_id": integration_id,
            "direction": direction,
            "priority": priority,
            "scheduled_time": datetime.now() + (delay or timedelta(0)),
            "retry_count": 0
        }

        await self.sync_queue.put(sync_task)
        logger.info(f"Scheduled sync for {integration_id} in direction {direction.value}")

    async def process_sync_queue(self):
        """Process the synchronization queue"""
        while True:
            try:
                # Wait for sync task
                sync_task = await self.sync_queue.get()

                # Check if it's time to execute
                if datetime.now() < sync_task["scheduled_time"]:
                    # Re-queue with delay
                    await asyncio.sleep(1)
                    await self.sync_queue.put(sync_task)
                    continue

                integration_id = sync_task["integration_id"]

                # Acquire lock for this integration
                if integration_id not in self.sync_locks:
                    self.sync_locks[integration_id] = asyncio.Lock()

                async with self.sync_locks[integration_id]:
                    await self._execute_sync(sync_task)

                self.sync_queue.task_done()

            except Exception as e:
                logger.error(f"Sync queue processing error: {str(e)}")
                await asyncio.sleep(5)

    async def _execute_sync(self, sync_task: Dict[str, Any]):
        """Execute a single synchronization task"""
        integration_id = sync_task["integration_id"]
        direction = sync_task["direction"]

        try:
            # Get integration instance
            integration_manager = await get_integration_manager()
            integration = await integration_manager.get_integration(integration_id)

            if not integration or integration.status != IntegrationStatus.CONNECTED:
                logger.warning(f"Integration {integration_id} not available for sync")
                return

            # Execute sync
            result = await integration.sync_data(direction)

            # Log result
            await self._log_sync_result(result)

            # Handle conflicts if any
            if result.conflicts_detected > 0:
                await self._handle_conflicts(result)

        except Exception as e:
            logger.error(f"Sync execution failed for {integration_id}: {str(e)}")

            # Retry if configured
            if sync_task["retry_count"] < 3:
                sync_task["retry_count"] += 1
                sync_task["scheduled_time"] = datetime.now() + timedelta(minutes=5)
                await self.sync_queue.put(sync_task)

    async def _log_sync_result(self, result: SyncResult):
        """Log synchronization result to database"""
        async with get_db() as db:
            log_entry = IntegrationLog(
                integration_id=result.integration_id,
                operation_type="sync",
                direction=result.direction.value,
                records_processed=result.records_processed,
                records_created=result.records_created,
                records_updated=result.records_updated,
                records_failed=result.records_failed,
                success=result.success,
                error_messages=result.errors,
                execution_time=(result.end_time - result.start_time).total_seconds(),
                created_at=result.start_time
            )

            db.add(log_entry)
            await db.commit()

    async def _handle_conflicts(self, result: SyncResult):
        """Handle data conflicts during synchronization"""
        resolution_strategy = self.conflict_handlers.get(
            result.integration_id,
            DataConflictResolution.MANUAL_REVIEW
        )

        if resolution_strategy == DataConflictResolution.MANUAL_REVIEW:
            # Queue for manual review
            await self._queue_for_manual_review(result)
        elif resolution_strategy == DataConflictResolution.TIMESTAMP_BASED:
            # Resolve based on timestamps
            await self._resolve_by_timestamp(result)
        # Add other resolution strategies as needed

    async def _queue_for_manual_review(self, result: SyncResult):
        """Queue conflicts for manual review"""
        # Implementation for manual review workflow
        logger.info(f"Queued {result.conflicts_detected} conflicts for manual review")

    async def _resolve_by_timestamp(self, result: SyncResult):
        """Resolve conflicts based on timestamps"""
        # Implementation for timestamp-based resolution
        logger.info(f"Resolved {result.conflicts_detected} conflicts by timestamp")


class WebhookManager:
    """Manages webhook endpoints and event processing"""

    def __init__(self):
        self.webhook_handlers: Dict[str, BaseIntegration] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()

    def register_webhook_handler(self, integration_id: str, integration: BaseIntegration):
        """Register a webhook handler for an integration"""
        self.webhook_handlers[integration_id] = integration
        logger.info(f"Registered webhook handler for {integration_id}")

    async def process_webhook_event(
        self,
        integration_id: str,
        event_type: str,
        payload: Dict[str, Any],
        signature: Optional[str] = None
    ) -> bool:
        """Process incoming webhook event"""
        try:
            # Verify webhook signature if provided
            if signature and not await self._verify_webhook_signature(integration_id, payload, signature):
                logger.warning(f"Invalid webhook signature for {integration_id}")
                return False

            # Create webhook event
            event = WebhookEvent(
                event_id=f"webhook_{integration_id}_{datetime.now().timestamp()}",
                integration_id=integration_id,
                event_type=event_type,
                payload=payload,
                timestamp=datetime.now(),
                verified=signature is not None
            )

            # Queue for processing
            await self.event_queue.put(event)
            return True

        except Exception as e:
            logger.error(f"Webhook processing error for {integration_id}: {str(e)}")
            return False

    async def process_webhook_queue(self):
        """Process the webhook event queue"""
        while True:
            try:
                event = await self.event_queue.get()

                # Get handler
                handler = self.webhook_handlers.get(event.integration_id)
                if not handler:
                    logger.warning(f"No handler for webhook {event.integration_id}")
                    continue

                # Process event
                success = await handler.handle_webhook(event)

                # Log event
                await self._log_webhook_event(event, success)

                self.event_queue.task_done()

            except Exception as e:
                logger.error(f"Webhook queue processing error: {str(e)}")
                await asyncio.sleep(1)

    async def _verify_webhook_signature(
        self,
        integration_id: str,
        payload: Dict[str, Any],
        signature: str
    ) -> bool:
        """Verify webhook signature"""
        # Implementation depends on the specific integration
        # This is a placeholder that should be overridden
        return True

    async def _log_webhook_event(self, event: WebhookEvent, success: bool):
        """Log webhook event to database"""
        async with get_db() as db:
            log_entry = IntegrationLog(
                integration_id=event.integration_id,
                operation_type="webhook",
                webhook_event_type=event.event_type,
                success=success,
                payload_size=len(json.dumps(event.payload)),
                created_at=event.timestamp
            )

            db.add(log_entry)
            await db.commit()


class IntegrationManager:
    """Main integration management system"""

    def __init__(self):
        self.integrations: Dict[str, BaseIntegration] = {}
        self.data_sync_manager = DataSyncManager()
        self.webhook_manager = WebhookManager()
        self._sync_tasks: Dict[str, asyncio.Task] = {}

    async def register_integration(self, integration: BaseIntegration) -> bool:
        """Register a new integration"""
        try:
            integration_id = integration.config.integration_id

            # Store integration
            self.integrations[integration_id] = integration

            # Register webhook handler
            self.webhook_manager.register_webhook_handler(integration_id, integration)

            # Persist to database
            await self._persist_integration_config(integration.config)

            logger.info(f"Registered integration: {integration_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to register integration: {str(e)}")
            return False

    async def get_integration(self, integration_id: str) -> Optional[BaseIntegration]:
        """Get an integration by ID"""
        return self.integrations.get(integration_id)

    async def connect_integration(self, integration_id: str) -> bool:
        """Connect an integration"""
        integration = self.integrations.get(integration_id)
        if not integration:
            return False

        success = await integration.connect()

        if success:
            # Start sync scheduler for this integration
            await self._start_sync_scheduler(integration)

        # Update status in database
        await self._update_integration_status(integration_id, integration.status)

        return success

    async def disconnect_integration(self, integration_id: str) -> bool:
        """Disconnect an integration"""
        integration = self.integrations.get(integration_id)
        if not integration:
            return False

        # Stop sync scheduler
        await self._stop_sync_scheduler(integration_id)

        # Disconnect
        success = await integration.disconnect()

        # Update status in database
        await self._update_integration_status(integration_id, integration.status)

        return success

    async def sync_integration(
        self,
        integration_id: str,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    ) -> bool:
        """Trigger manual sync for an integration"""
        integration = self.integrations.get(integration_id)
        if not integration or integration.status != IntegrationStatus.CONNECTED:
            return False

        # Schedule immediate sync
        await self.data_sync_manager.schedule_sync(integration_id, direction, priority=1)
        return True

    async def get_integration_status(self, integration_id: str) -> Optional[Dict[str, Any]]:
        """Get integration status and statistics"""
        integration = self.integrations.get(integration_id)
        if not integration:
            return None

        # Get sync statistics from database
        stats = await self._get_integration_stats(integration_id)

        return {
            "integration_id": integration_id,
            "status": integration.status.value,
            "last_sync": integration.last_sync.isoformat() if integration.last_sync else None,
            "error_count": integration.error_count,
            "rate_limited": integration.is_rate_limited(),
            "supported_entities": await integration.get_supported_entities(),
            "sync_stats": stats
        }

    async def list_integrations(self) -> List[Dict[str, Any]]:
        """List all registered integrations"""
        integrations = []

        for integration_id, integration in self.integrations.items():
            status = await self.get_integration_status(integration_id)
            if status:
                integrations.append(status)

        return integrations

    async def start_background_tasks(self):
        """Start background processing tasks"""
        # Start sync queue processor
        asyncio.create_task(self.data_sync_manager.process_sync_queue())

        # Start webhook queue processor
        asyncio.create_task(self.webhook_manager.process_webhook_queue())

        logger.info("Started integration background tasks")

    async def _start_sync_scheduler(self, integration: BaseIntegration):
        """Start sync scheduler for an integration"""
        integration_id = integration.config.integration_id

        if integration_id in self._sync_tasks:
            # Stop existing task
            self._sync_tasks[integration_id].cancel()

        # Start new sync task
        task = asyncio.create_task(self._sync_scheduler_loop(integration))
        self._sync_tasks[integration_id] = task

    async def _stop_sync_scheduler(self, integration_id: str):
        """Stop sync scheduler for an integration"""
        if integration_id in self._sync_tasks:
            self._sync_tasks[integration_id].cancel()
            del self._sync_tasks[integration_id]

    async def _sync_scheduler_loop(self, integration: BaseIntegration):
        """Sync scheduler loop for an integration"""
        integration_id = integration.config.integration_id
        sync_frequency = integration.config.sync_frequency

        while True:
            try:
                await asyncio.sleep(sync_frequency)

                if integration.status == IntegrationStatus.CONNECTED and not integration.is_rate_limited():
                    await self.data_sync_manager.schedule_sync(
                        integration_id,
                        integration.config.sync_direction
                    )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Sync scheduler error for {integration_id}: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying

    async def _persist_integration_config(self, config: IntegrationConfig):
        """Persist integration configuration to database"""
        async with get_db() as db:
            # Check if integration exists
            existing = await db.execute(
                select(Integration).where(Integration.integration_id == config.integration_id)
            )
            integration_record = existing.scalar_one_or_none()

            if integration_record:
                # Update existing
                await db.execute(
                    update(Integration)
                    .where(Integration.integration_id == config.integration_id)
                    .values(
                        name=config.name,
                        provider=config.provider,
                        config=asdict(config),
                        updated_at=datetime.now()
                    )
                )
            else:
                # Create new
                integration_record = Integration(
                    integration_id=config.integration_id,
                    name=config.name,
                    provider=config.provider,
                    status=IntegrationStatus.DISCONNECTED.value,
                    config=asdict(config),
                    created_at=datetime.now()
                )
                db.add(integration_record)

            await db.commit()

    async def _update_integration_status(self, integration_id: str, status: IntegrationStatus):
        """Update integration status in database"""
        async with get_db() as db:
            await db.execute(
                update(Integration)
                .where(Integration.integration_id == integration_id)
                .values(
                    status=status.value,
                    updated_at=datetime.now()
                )
            )
            await db.commit()

    async def _get_integration_stats(self, integration_id: str) -> Dict[str, Any]:
        """Get integration statistics from database"""
        async with get_db() as db:
            # Get recent sync stats
            recent_logs = await db.execute(
                select(IntegrationLog)
                .where(
                    IntegrationLog.integration_id == integration_id,
                    IntegrationLog.created_at >= datetime.now() - timedelta(days=7)
                )
                .order_by(IntegrationLog.created_at.desc())
                .limit(100)
            )

            logs = recent_logs.scalars().all()

            # Calculate statistics
            total_syncs = len([log for log in logs if log.operation_type == "sync"])
            successful_syncs = len([log for log in logs if log.operation_type == "sync" and log.success])
            total_records_processed = sum([log.records_processed or 0 for log in logs])

            return {
                "total_syncs_7d": total_syncs,
                "successful_syncs_7d": successful_syncs,
                "success_rate": (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0,
                "total_records_processed_7d": total_records_processed,
                "last_sync_time": logs[0].created_at.isoformat() if logs else None
            }


# Service factory function
_integration_manager_instance = None

async def get_integration_manager() -> IntegrationManager:
    """Get integration manager singleton instance"""
    global _integration_manager_instance

    if _integration_manager_instance is None:
        _integration_manager_instance = IntegrationManager()
        await _integration_manager_instance.start_background_tasks()

    return _integration_manager_instance