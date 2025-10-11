"""
Security utilities and permission management
"""

from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User, OrganizationMembership
from app.models.organization import Organization


class PermissionChecker:
    """
    Permission checker for role-based access control
    """

    # Define role hierarchy and permissions
    ROLE_HIERARCHY = {
        "owner": 4,
        "admin": 3,
        "member": 2,
        "viewer": 1
    }

    RESOURCE_PERMISSIONS = {
        # Deal permissions
        "deals": {
            "create": ["owner", "admin", "member"],
            "read": ["owner", "admin", "member", "viewer"],
            "update": ["owner", "admin", "member"],
            "delete": ["owner", "admin"]
        },
        # Document permissions
        "documents": {
            "create": ["owner", "admin", "member"],
            "read": ["owner", "admin", "member", "viewer"],
            "update": ["owner", "admin", "member"],
            "delete": ["owner", "admin"]
        },
        # Team permissions
        "teams": {
            "create": ["owner", "admin"],
            "read": ["owner", "admin", "member", "viewer"],
            "update": ["owner", "admin"],
            "delete": ["owner"]
        },
        # Organization settings permissions
        "organization_settings": {
            "create": ["owner"],
            "read": ["owner", "admin"],
            "update": ["owner", "admin"],
            "delete": ["owner"]
        },
        # User management permissions
        "users": {
            "create": ["owner", "admin"],
            "read": ["owner", "admin", "member", "viewer"],
            "update": ["owner", "admin"],
            "delete": ["owner"]
        },
        # Analytics permissions
        "analytics": {
            "read": ["owner", "admin", "member", "viewer"],
            "export": ["owner", "admin", "member"]
        }
    }

    @classmethod
    def check_permission(
        cls,
        user: User,
        organization: Organization,
        resource: str,
        action: str
    ) -> bool:
        """
        Check if a user has permission to perform an action on a resource

        Args:
            user: The user to check permissions for
            organization: The organization context
            resource: The resource type (e.g., 'deals', 'documents')
            action: The action to perform (e.g., 'create', 'read', 'update', 'delete')

        Returns:
            True if the user has permission

        Raises:
            HTTPException: If the user doesn't have permission
        """
        # Get user's membership in the organization
        membership = cls._get_membership(user, organization)

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this organization"
            )

        # Check if resource and action are defined
        if resource not in cls.RESOURCE_PERMISSIONS:
            # Default to most restrictive for undefined resources
            allowed_roles = ["owner"]
        elif action not in cls.RESOURCE_PERMISSIONS[resource]:
            # Default to most restrictive for undefined actions
            allowed_roles = ["owner"]
        else:
            allowed_roles = cls.RESOURCE_PERMISSIONS[resource][action]

        # Check if user's role is in allowed roles
        if membership.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Your role '{membership.role}' doesn't have permission to {action} {resource}"
            )

        return True

    @classmethod
    def has_permission(
        cls,
        user: User,
        organization: Organization,
        resource: str,
        action: str
    ) -> bool:
        """
        Check if a user has permission (returns bool without raising exception)
        """
        try:
            cls.check_permission(user, organization, resource, action)
            return True
        except HTTPException:
            return False

    @classmethod
    def check_role_hierarchy(
        cls,
        user: User,
        organization: Organization,
        target_user: User
    ) -> bool:
        """
        Check if a user can manage another user based on role hierarchy

        Args:
            user: The user performing the action
            organization: The organization context
            target_user: The user being managed

        Returns:
            True if the user can manage the target user

        Raises:
            HTTPException: If the user cannot manage the target user
        """
        user_membership = cls._get_membership(user, organization)
        target_membership = cls._get_membership(target_user, organization)

        if not user_membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this organization"
            )

        if not target_membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target user is not a member of this organization"
            )

        user_level = cls.ROLE_HIERARCHY.get(user_membership.role, 0)
        target_level = cls.ROLE_HIERARCHY.get(target_membership.role, 0)

        # Can only manage users with lower or equal role level
        # (except owners can manage other owners)
        if user_level < target_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cannot manage users with role '{target_membership.role}' as a '{user_membership.role}'"
            )

        return True

    @staticmethod
    def _get_membership(
        user: User,
        organization: Organization
    ) -> Optional[OrganizationMembership]:
        """
        Get a user's membership in an organization
        """
        for membership in user.organization_memberships:
            if membership.organization_id == organization.id and membership.is_active:
                return membership
        return None


def check_permission(
    user: User,
    organization: Organization,
    resource: str,
    action: str
) -> bool:
    """
    Convenience function to check permissions
    """
    return PermissionChecker.check_permission(user, organization, resource, action)


def has_permission(
    user: User,
    organization: Organization,
    resource: str,
    action: str
) -> bool:
    """
    Convenience function to check permissions without raising exceptions
    """
    return PermissionChecker.has_permission(user, organization, resource, action)


def is_organization_owner(
    user: User,
    organization: Organization
) -> bool:
    """
    Check if a user is an owner of the organization
    """
    membership = PermissionChecker._get_membership(user, organization)
    return membership and membership.role == "owner"


def is_organization_admin(
    user: User,
    organization: Organization
) -> bool:
    """
    Check if a user is an admin or owner of the organization
    """
    membership = PermissionChecker._get_membership(user, organization)
    return membership and membership.role in ["owner", "admin"]


def can_manage_deals(
    user: User,
    organization: Organization
) -> bool:
    """
    Check if a user can manage deals (create, update, delete)
    """
    membership = PermissionChecker._get_membership(user, organization)
    return membership and membership.role in ["owner", "admin", "member"]


def can_view_sensitive_data(
    user: User,
    organization: Organization
) -> bool:
    """
    Check if a user can view sensitive financial data
    """
    membership = PermissionChecker._get_membership(user, organization)
    return membership and membership.role in ["owner", "admin", "member"]