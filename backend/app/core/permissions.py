"""
M&A Platform Permission System
Comprehensive role-based access control for M&A workflows
"""

from typing import Dict, List, Set, Union, Optional
from enum import Enum
from ..models.user import OrganizationRole


class ResourceType(str, Enum):
    """Types of resources that can be protected"""
    DEALS = "deals"
    DOCUMENTS = "documents"
    ANALYTICS = "analytics"
    REPORTS = "reports"
    ADMIN = "admin"
    TEAMS = "teams"
    COMMUNICATIONS = "communications"
    FINANCIAL_MODELS = "financial_models"
    CLIENTS = "clients"


class Action(str, Enum):
    """Actions that can be performed on resources"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    ASSIGN = "assign"
    SHARE = "share"
    EXPORT = "export"
    APPROVE = "approve"
    MANAGE = "manage"
    VIEW_SENSITIVE = "view_sensitive"


# M&A Platform Permission Matrix
# Format: {ResourceType: {Action: [allowed_roles]}}
PERMISSION_MATRIX: Dict[ResourceType, Dict[Action, List[OrganizationRole]]] = {

    ResourceType.DEALS: {
        Action.CREATE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR
        ],
        Action.READ: [
            # All roles can read deals they're assigned to
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR,
            OrganizationRole.SENIOR_ASSOCIATE,
            OrganizationRole.ASSOCIATE,
            OrganizationRole.ANALYST,
            OrganizationRole.CLIENT,
            OrganizationRole.EXTERNAL_ADVISOR
        ],
        Action.UPDATE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR,
            OrganizationRole.SENIOR_ASSOCIATE
        ],
        Action.DELETE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER
        ],
        Action.ASSIGN: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR
        ],
        Action.APPROVE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER
        ]
    },

    ResourceType.DOCUMENTS: {
        Action.CREATE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR,
            OrganizationRole.SENIOR_ASSOCIATE,
            OrganizationRole.ASSOCIATE,
            OrganizationRole.ANALYST
        ],
        Action.READ: [
            # All team members can read documents they have access to
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR,
            OrganizationRole.SENIOR_ASSOCIATE,
            OrganizationRole.ASSOCIATE,
            OrganizationRole.ANALYST,
            OrganizationRole.CLIENT,
            OrganizationRole.EXTERNAL_ADVISOR
        ],
        Action.UPDATE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR,
            OrganizationRole.SENIOR_ASSOCIATE,
            OrganizationRole.ASSOCIATE
        ],
        Action.DELETE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR
        ],
        Action.SHARE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR,
            OrganizationRole.SENIOR_ASSOCIATE
        ],
        Action.VIEW_SENSITIVE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR
        ]
    },

    ResourceType.ANALYTICS: {
        Action.READ: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR,
            OrganizationRole.SENIOR_ASSOCIATE
        ],
        Action.EXPORT: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR
        ],
        Action.VIEW_SENSITIVE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER
        ]
    },

    ResourceType.REPORTS: {
        Action.CREATE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR,
            OrganizationRole.SENIOR_ASSOCIATE
        ],
        Action.READ: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR,
            OrganizationRole.SENIOR_ASSOCIATE,
            OrganizationRole.ASSOCIATE
        ],
        Action.EXPORT: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR
        ],
        Action.SHARE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR
        ]
    },

    ResourceType.ADMIN: {
        Action.MANAGE: [
            OrganizationRole.MANAGING_PARTNER,
            # Legacy admin roles for backward compatibility
            OrganizationRole.ADMIN,
            OrganizationRole.OWNER
        ],
        Action.READ: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.ADMIN,
            OrganizationRole.OWNER
        ],
        Action.CREATE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.ADMIN,
            OrganizationRole.OWNER
        ]
    },

    ResourceType.TEAMS: {
        Action.CREATE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR
        ],
        Action.READ: [
            # All roles can view team information
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR,
            OrganizationRole.SENIOR_ASSOCIATE,
            OrganizationRole.ASSOCIATE,
            OrganizationRole.ANALYST,
            OrganizationRole.CLIENT
        ],
        Action.MANAGE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR
        ],
        Action.ASSIGN: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR
        ]
    },

    ResourceType.FINANCIAL_MODELS: {
        Action.CREATE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR,
            OrganizationRole.SENIOR_ASSOCIATE
        ],
        Action.READ: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR,
            OrganizationRole.SENIOR_ASSOCIATE,
            OrganizationRole.ASSOCIATE,
            OrganizationRole.ANALYST
        ],
        Action.UPDATE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR,
            OrganizationRole.SENIOR_ASSOCIATE
        ],
        Action.APPROVE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER
        ]
    },

    ResourceType.CLIENTS: {
        Action.CREATE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER
        ],
        Action.READ: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR,
            OrganizationRole.SENIOR_ASSOCIATE
        ],
        Action.UPDATE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR
        ],
        Action.MANAGE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER
        ]
    },

    ResourceType.COMMUNICATIONS: {
        Action.CREATE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR,
            OrganizationRole.SENIOR_ASSOCIATE,
            OrganizationRole.ASSOCIATE
        ],
        Action.READ: [
            # All team members can read communications they have access to
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR,
            OrganizationRole.SENIOR_ASSOCIATE,
            OrganizationRole.ASSOCIATE,
            OrganizationRole.ANALYST,
            OrganizationRole.CLIENT,
            OrganizationRole.EXTERNAL_ADVISOR
        ],
        Action.UPDATE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR,
            OrganizationRole.SENIOR_ASSOCIATE
        ],
        Action.DELETE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR
        ],
        Action.SHARE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR,
            OrganizationRole.SENIOR_ASSOCIATE,
            OrganizationRole.ASSOCIATE
        ],
        Action.MANAGE: [
            OrganizationRole.MANAGING_PARTNER,
            OrganizationRole.PARTNER,
            OrganizationRole.DIRECTOR
        ]
    }
}


class PermissionChecker:
    """Service class for checking M&A platform permissions"""

    @staticmethod
    def has_permission(
        user_role: OrganizationRole,
        resource_type: ResourceType,
        action: Action,
        context: Optional[Dict] = None
    ) -> bool:
        """
        Check if a user role has permission to perform an action on a resource

        Args:
            user_role: The user's role in the organization
            resource_type: Type of resource being accessed
            action: Action being performed
            context: Additional context for permission checking (e.g., deal assignment)

        Returns:
            True if permission is granted, False otherwise
        """
        # Check if resource type exists in permission matrix
        if resource_type not in PERMISSION_MATRIX:
            return False

        # Check if action exists for the resource type
        if action not in PERMISSION_MATRIX[resource_type]:
            return False

        # Check if user role is in allowed roles
        allowed_roles = PERMISSION_MATRIX[resource_type][action]

        # Handle legacy role mappings
        if user_role in allowed_roles:
            return True

        # Special permission logic based on context
        if context:
            return PermissionChecker._check_contextual_permission(
                user_role, resource_type, action, context
            )

        return False

    @staticmethod
    def _check_contextual_permission(
        user_role: OrganizationRole,
        resource_type: ResourceType,
        action: Action,
        context: Dict
    ) -> bool:
        """
        Check permissions based on specific context (e.g., deal team membership)
        """
        # Deal team members have special access to their assigned deals
        if context.get('is_team_member'):
            if resource_type == ResourceType.DEALS and action == Action.READ:
                return True
            if resource_type == ResourceType.DOCUMENTS and action in [Action.READ, Action.CREATE]:
                return True

        # Deal leads have elevated permissions
        if context.get('is_deal_lead'):
            if resource_type == ResourceType.DEALS and action in [Action.READ, Action.UPDATE]:
                return True
            if resource_type == ResourceType.TEAMS and action in [Action.READ, Action.ASSIGN]:
                return True

        # Client-specific permissions
        if user_role == OrganizationRole.CLIENT:
            # Clients can only access their own deals and documents
            if context.get('is_client_deal') and resource_type == ResourceType.DEALS:
                return action == Action.READ
            if context.get('is_client_document') and resource_type == ResourceType.DOCUMENTS:
                return action in [Action.READ, Action.CREATE]

        return False

    @staticmethod
    def get_allowed_actions(
        user_role: OrganizationRole,
        resource_type: ResourceType,
        context: Optional[Dict] = None
    ) -> List[Action]:
        """
        Get all actions a user role can perform on a resource type
        """
        allowed_actions = []

        if resource_type not in PERMISSION_MATRIX:
            return allowed_actions

        for action, allowed_roles in PERMISSION_MATRIX[resource_type].items():
            if PermissionChecker.has_permission(user_role, resource_type, action, context):
                allowed_actions.append(action)

        return allowed_actions

    @staticmethod
    def get_role_hierarchy() -> Dict[OrganizationRole, int]:
        """
        Return role hierarchy for permission inheritance
        Higher numbers indicate higher authority
        """
        return {
            OrganizationRole.CLIENT: 1,
            OrganizationRole.EXTERNAL_ADVISOR: 1,
            OrganizationRole.ANALYST: 2,
            OrganizationRole.ASSOCIATE: 3,
            OrganizationRole.SENIOR_ASSOCIATE: 4,
            OrganizationRole.DIRECTOR: 5,
            OrganizationRole.PARTNER: 6,
            OrganizationRole.MANAGING_PARTNER: 7,
            # Legacy roles
            OrganizationRole.VIEWER: 1,
            OrganizationRole.MEMBER: 3,
            OrganizationRole.MANAGER: 5,
            OrganizationRole.ADMIN: 6,
            OrganizationRole.OWNER: 7
        }

    @staticmethod
    def can_manage_user(manager_role: OrganizationRole, target_role: OrganizationRole) -> bool:
        """
        Check if a user with manager_role can manage a user with target_role
        """
        hierarchy = PermissionChecker.get_role_hierarchy()
        manager_level = hierarchy.get(manager_role, 0)
        target_level = hierarchy.get(target_role, 0)

        # Can only manage users at same or lower level
        return manager_level >= target_level


# Convenience functions for common permission checks
def can_create_deal(user_role: OrganizationRole) -> bool:
    """Check if user can create deals"""
    return PermissionChecker.has_permission(user_role, ResourceType.DEALS, Action.CREATE)


def can_view_analytics(user_role: OrganizationRole) -> bool:
    """Check if user can view analytics"""
    return PermissionChecker.has_permission(user_role, ResourceType.ANALYTICS, Action.READ)


def can_manage_organization(user_role: OrganizationRole) -> bool:
    """Check if user can manage organization settings"""
    return PermissionChecker.has_permission(user_role, ResourceType.ADMIN, Action.MANAGE)


def is_senior_role(user_role: OrganizationRole) -> bool:
    """Check if user has senior-level permissions"""
    senior_roles = [
        OrganizationRole.MANAGING_PARTNER,
        OrganizationRole.PARTNER,
        OrganizationRole.DIRECTOR,
        OrganizationRole.ADMIN,
        OrganizationRole.OWNER
    ]
    return user_role in senior_roles