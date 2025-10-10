"""
Data Synchronization Engine
Real-time data sync across platforms with conflict resolution and data validation
"""

import os
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import asyncio
import hashlib
import json
from enum import Enum
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class SyncStrategy(str, Enum):
    """Data synchronization strategies"""
    FULL = "full"  # Complete data sync
    INCREMENTAL = "incremental"  # Only changes since last sync
    DELTA = "delta"  # Bidirectional conflict resolution
    MIRROR = "mirror"  # One-way mirror (source overwrites destination)


class ConflictResolution(str, Enum):
    """Conflict resolution strategies"""
    SOURCE_WINS = "source_wins"  # Source platform data takes precedence
    DESTINATION_WINS = "destination_wins"  # Destination keeps its data
    NEWEST_WINS = "newest_wins"  # Most recently updated wins
    MANUAL = "manual"  # Requires manual resolution
    MERGE = "merge"  # Attempt intelligent merge


class SyncDirection(str, Enum):
    """Synchronization direction"""
    INBOUND = "inbound"  # External platform → Our database
    OUTBOUND = "outbound"  # Our database → External platform
    BIDIRECTIONAL = "bidirectional"  # Both directions


class DataValidator:
    """Validates and transforms data for synchronization"""

    @staticmethod
    def validate_required_fields(
        data: Dict[str, Any],
        required_fields: List[str]
    ) -> tuple[bool, List[str]]:
        """Check if required fields are present"""
        missing_fields = [field for field in required_fields if field not in data]
        return len(missing_fields) == 0, missing_fields

    @staticmethod
    def sanitize_data(data: Dict[str, Any], allowed_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Remove unwanted fields and sanitize data"""
        if allowed_fields:
            return {k: v for k, v in data.items() if k in allowed_fields}
        return data

    @staticmethod
    def transform_field(value: Any, transform_type: str) -> Any:
        """Apply transformation to a field value"""
        transformations = {
            "lowercase": lambda x: str(x).lower() if x else x,
            "uppercase": lambda x: str(x).upper() if x else x,
            "trim": lambda x: str(x).strip() if x else x,
            "int": lambda x: int(x) if x is not None else None,
            "float": lambda x: float(x) if x is not None else None,
            "bool": lambda x: bool(x) if x is not None else None,
            "json": lambda x: json.loads(x) if isinstance(x, str) else x,
            "string": lambda x: str(x) if x is not None else None
        }

        transform_func = transformations.get(transform_type)
        if transform_func:
            try:
                return transform_func(value)
            except Exception as e:
                logger.error(f"Transform error ({transform_type}): {e}")
                return value

        return value


class ConflictResolver:
    """Resolves data conflicts during synchronization"""

    @staticmethod
    def resolve_conflict(
        source_data: Dict[str, Any],
        destination_data: Dict[str, Any],
        strategy: ConflictResolution,
        timestamp_field: str = "updated_at"
    ) -> Dict[str, Any]:
        """Resolve conflict between source and destination data"""

        if strategy == ConflictResolution.SOURCE_WINS:
            return source_data

        elif strategy == ConflictResolution.DESTINATION_WINS:
            return destination_data

        elif strategy == ConflictResolution.NEWEST_WINS:
            source_time = source_data.get(timestamp_field)
            dest_time = destination_data.get(timestamp_field)

            if source_time and dest_time:
                if isinstance(source_time, str):
                    source_time = datetime.fromisoformat(source_time.replace('Z', '+00:00'))
                if isinstance(dest_time, str):
                    dest_time = datetime.fromisoformat(dest_time.replace('Z', '+00:00'))

                return source_data if source_time > dest_time else destination_data

            return source_data

        elif strategy == ConflictResolution.MERGE:
            # Intelligent merge: take non-null values from both
            merged = {**destination_data}

            for key, value in source_data.items():
                if value is not None:
                    if key not in merged or merged[key] is None:
                        merged[key] = value
                    elif key == timestamp_field:
                        # For timestamp, take the newer one
                        if source_data.get(key) > merged.get(key, datetime.min):
                            merged[key] = value

            return merged

        else:  # MANUAL
            # Return both for manual resolution
            return {
                "conflict": True,
                "source": source_data,
                "destination": destination_data,
                "requires_manual_resolution": True
            }

    @staticmethod
    def detect_conflicts(
        source_data: Dict[str, Any],
        destination_data: Dict[str, Any],
        key_fields: List[str]
    ) -> List[str]:
        """Detect which fields have conflicts"""
        conflicts = []

        for field in key_fields:
            source_val = source_data.get(field)
            dest_val = destination_data.get(field)

            if source_val != dest_val:
                conflicts.append(field)

        return conflicts


class SyncEngine:
    """
    Main synchronization engine
    Handles data sync across platforms with validation and conflict resolution
    """

    def __init__(self, db: Session):
        self.db = db
        self.validator = DataValidator()
        self.resolver = ConflictResolver()

    async def sync_data(
        self,
        source_data: List[Dict[str, Any]],
        destination_getter: Callable,
        destination_setter: Callable,
        entity_type: str,
        strategy: SyncStrategy = SyncStrategy.INCREMENTAL,
        conflict_resolution: ConflictResolution = ConflictResolution.NEWEST_WINS,
        id_field: str = "id",
        timestamp_field: str = "updated_at",
        required_fields: Optional[List[str]] = None,
        field_mappings: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Synchronize data from source to destination

        Args:
            source_data: List of records from source platform
            destination_getter: Function to get existing records
            destination_setter: Function to create/update records
            entity_type: Type of entity being synced
            strategy: Sync strategy to use
            conflict_resolution: How to resolve conflicts
            id_field: Field name for unique identifier
            timestamp_field: Field name for last update timestamp
            required_fields: List of required field names
            field_mappings: Map source fields to destination fields

        Returns:
            Sync result summary
        """
        created = 0
        updated = 0
        failed = 0
        skipped = 0
        conflicts = []
        errors = []

        try:
            # Get existing destination data
            existing_data = await destination_getter()
            existing_map = {record.get(id_field): record for record in existing_data}

            for source_record in source_data:
                try:
                    # Apply field mappings if provided
                    if field_mappings:
                        source_record = self._apply_field_mappings(source_record, field_mappings)

                    # Validate required fields
                    if required_fields:
                        is_valid, missing = self.validator.validate_required_fields(
                            source_record,
                            required_fields
                        )
                        if not is_valid:
                            errors.append(f"Missing fields {missing} in record {source_record.get(id_field)}")
                            failed += 1
                            continue

                    record_id = source_record.get(id_field)

                    if record_id in existing_map:
                        # Record exists - check for conflicts
                        existing_record = existing_map[record_id]

                        conflict_fields = self.resolver.detect_conflicts(
                            source_record,
                            existing_record,
                            list(source_record.keys())
                        )

                        if conflict_fields:
                            # Resolve conflict
                            resolved = self.resolver.resolve_conflict(
                                source_record,
                                existing_record,
                                conflict_resolution,
                                timestamp_field
                            )

                            if resolved.get("conflict"):
                                # Manual resolution required
                                conflicts.append(resolved)
                                skipped += 1
                                continue

                            # Update with resolved data
                            await destination_setter(record_id, resolved, is_update=True)
                            updated += 1
                        else:
                            # No conflicts, update if strategy allows
                            if strategy != SyncStrategy.MIRROR or source_record != existing_record:
                                await destination_setter(record_id, source_record, is_update=True)
                                updated += 1
                            else:
                                skipped += 1

                    else:
                        # New record - create it
                        await destination_setter(None, source_record, is_update=False)
                        created += 1

                except Exception as e:
                    logger.error(f"Error syncing record {source_record.get(id_field)}: {e}")
                    errors.append(str(e))
                    failed += 1

        except Exception as e:
            logger.error(f"Sync engine error: {e}")
            errors.append(f"Engine error: {str(e)}")

        return {
            "entity_type": entity_type,
            "strategy": strategy.value,
            "records_processed": len(source_data),
            "created": created,
            "updated": updated,
            "failed": failed,
            "skipped": skipped,
            "conflicts_requiring_manual_resolution": len(conflicts),
            "conflicts": conflicts,
            "errors": errors,
            "success": failed == 0 and len(conflicts) == 0,
            "synced_at": datetime.utcnow().isoformat()
        }

    def _apply_field_mappings(
        self,
        data: Dict[str, Any],
        mappings: Dict[str, str]
    ) -> Dict[str, Any]:
        """Apply field name mappings"""
        mapped_data = {}

        for source_field, dest_field in mappings.items():
            if source_field in data:
                mapped_data[dest_field] = data[source_field]

        # Include unmapped fields
        for key, value in data.items():
            if key not in mappings and key not in mapped_data:
                mapped_data[key] = value

        return mapped_data

    async def bidirectional_sync(
        self,
        platform_a_data: List[Dict[str, Any]],
        platform_b_data: List[Dict[str, Any]],
        platform_a_setter: Callable,
        platform_b_setter: Callable,
        entity_type: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform bidirectional synchronization between two platforms

        Returns:
            Combined sync results for both directions
        """
        # Sync A → B
        result_a_to_b = await self.sync_data(
            source_data=platform_a_data,
            destination_getter=lambda: platform_b_data,
            destination_setter=platform_b_setter,
            entity_type=entity_type,
            **kwargs
        )

        # Sync B → A
        result_b_to_a = await self.sync_data(
            source_data=platform_b_data,
            destination_getter=lambda: platform_a_data,
            destination_setter=platform_a_setter,
            entity_type=entity_type,
            **kwargs
        )

        return {
            "entity_type": entity_type,
            "sync_type": "bidirectional",
            "platform_a_to_b": result_a_to_b,
            "platform_b_to_a": result_b_to_a,
            "total_records_synced": result_a_to_b["created"] + result_a_to_b["updated"] +
                                   result_b_to_a["created"] + result_b_to_a["updated"],
            "success": result_a_to_b["success"] and result_b_to_a["success"]
        }

    def calculate_data_hash(self, data: Dict[str, Any], fields: Optional[List[str]] = None) -> str:
        """Calculate hash of data for change detection"""
        if fields:
            data_to_hash = {k: v for k, v in data.items() if k in fields}
        else:
            data_to_hash = data

        # Sort keys for consistent hashing
        sorted_data = json.dumps(data_to_hash, sort_keys=True)
        return hashlib.sha256(sorted_data.encode()).hexdigest()

    async def detect_changes(
        self,
        current_data: List[Dict[str, Any]],
        previous_hashes: Dict[str, str],
        id_field: str = "id",
        hash_fields: Optional[List[str]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Detect changes by comparing data hashes

        Returns:
            Dict with 'added', 'modified', 'unchanged' lists
        """
        added = []
        modified = []
        unchanged = []

        for record in current_data:
            record_id = record.get(id_field)
            current_hash = self.calculate_data_hash(record, hash_fields)

            if record_id not in previous_hashes:
                added.append(record)
            elif previous_hashes[record_id] != current_hash:
                modified.append(record)
            else:
                unchanged.append(record)

        return {
            "added": added,
            "modified": modified,
            "unchanged": unchanged,
            "total_changes": len(added) + len(modified)
        }


class SyncScheduler:
    """Schedule and manage periodic synchronization tasks"""

    def __init__(self):
        self.scheduled_syncs: Dict[str, asyncio.Task] = {}

    async def schedule_sync(
        self,
        sync_id: str,
        sync_func: Callable,
        interval_minutes: int,
        **sync_kwargs
    ):
        """Schedule a recurring sync operation"""
        async def sync_loop():
            while True:
                try:
                    await asyncio.sleep(interval_minutes * 60)
                    result = await sync_func(**sync_kwargs)
                    logger.info(f"Scheduled sync {sync_id} completed: {result}")
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Scheduled sync {sync_id} failed: {e}")

        # Cancel existing task if any
        if sync_id in self.scheduled_syncs:
            self.scheduled_syncs[sync_id].cancel()

        # Start new task
        task = asyncio.create_task(sync_loop())
        self.scheduled_syncs[sync_id] = task

    def cancel_sync(self, sync_id: str) -> bool:
        """Cancel a scheduled sync"""
        if sync_id in self.scheduled_syncs:
            self.scheduled_syncs[sync_id].cancel()
            del self.scheduled_syncs[sync_id]
            return True
        return False

    def cancel_all(self):
        """Cancel all scheduled syncs"""
        for task in self.scheduled_syncs.values():
            task.cancel()
        self.scheduled_syncs.clear()
