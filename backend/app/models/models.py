"""
Legacy models.py - DEPRECATED
This file now re-exports models from the new modular structure to maintain backwards compatibility.
New code should import directly from app.models.user, app.models.organization, etc.
"""
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

# Import the unified Base from base.py
from .base import Base

# Re-export enums for backwards compatibility
class SubscriptionPlan(enum.Enum):
    SOLO = "solo"
    GROWTH = "growth"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class TaskStatus(enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    BLOCKED = "blocked"

class UserRole(enum.Enum):
    MASTER_ADMIN = "master_admin"
    TENANT_ADMIN = "tenant_admin"
    DEAL_MANAGER = "deal_manager"
    ANALYST = "analyst"
    VIEWER = "viewer"

# Re-export models from new structure for backwards compatibility
from .organization import Organization as Tenant  # Legacy name
from .user import User  # Already correct name

# NOTE: Task, Document, AuditLog models were in the old models.py
# but are not migrated yet. They can be added to separate modules as needed.
# For now, legacy code using these will need to be updated.

__all__ = [
    'Base',
    'Tenant',
    'User',
    'SubscriptionPlan',
    'TaskStatus',
    'UserRole',
]
