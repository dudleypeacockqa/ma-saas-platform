"""
Permission Middleware for M&A Platform
Provides route-level permission checking based on roles and context
"""

from typing import Optional, Dict, Any, Callable
from fastapi import Request, HTTPException, status, Depends
from functools import wraps
import logging

from ..core.permissions import PermissionChecker, ResourceType, Action
from ..models.user import OrganizationRole
from ..core.deps import get_current_user, get_current_organization

logger = logging.getLogger(__name__)


class PermissionError(HTTPException):
    """Custom exception for permission-related errors"""

    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


def require_permission(
    resource_type: ResourceType,
    action: Action,
    context_loader: Optional[Callable] = None
):
    """
    Decorator to require specific permissions for API endpoints

    Args:
        resource_type: Type of resource being accessed
        action: Action being performed
        context_loader: Optional function to load additional context for permission checking

    Usage:
        @require_permission(ResourceType.DEALS, Action.CREATE)
        async def create_deal(...)

        @require_permission(ResourceType.DOCUMENTS, Action.READ, context_loader=load_deal_context)
        async def get_document(...)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request and dependencies from kwargs
            request = None
            current_user = None
            current_org = None

            # Find request object and dependencies in function arguments
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            # Get user context from request state (set by auth middleware)
            if request and hasattr(request.state, 'user_id'):
                # User is authenticated via middleware
                user_role = getattr(request.state, 'user_role', None)
                organization_id = getattr(request.state, 'organization_id', None)
                user_id = getattr(request.state, 'user_id', None)

                if not user_role:
                    raise PermissionError("User role not found")

                # Convert string role to enum if needed
                if isinstance(user_role, str):
                    try:
                        user_role = OrganizationRole(user_role)
                    except ValueError:
                        raise PermissionError(f"Invalid user role: {user_role}")
            else:
                raise PermissionError("Authentication required")

            # Load additional context if context_loader is provided
            context = {}
            if context_loader:
                try:
                    context = await context_loader(request, user_id, organization_id, *args, **kwargs)
                except Exception as e:
                    logger.error(f"Error loading permission context: {e}")
                    context = {}

            # Check permission
            has_permission = PermissionChecker.has_permission(
                user_role=user_role,
                resource_type=resource_type,
                action=action,
                context=context
            )

            if not has_permission:
                logger.warning(
                    f"Permission denied: user_role={user_role}, "
                    f"resource={resource_type}, action={action}, "
                    f"user_id={user_id}, org_id={organization_id}"
                )
                raise PermissionError(
                    f"Insufficient permissions to {action.value} {resource_type.value}"
                )

            # Permission granted, execute the function
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def require_role(allowed_roles: list[OrganizationRole]):
    """
    Decorator to require specific roles for API endpoints

    Args:
        allowed_roles: List of roles that can access the endpoint

    Usage:
        @require_role([OrganizationRole.MANAGING_PARTNER, OrganizationRole.PARTNER])
        async def admin_endpoint(...)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from arguments
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                raise PermissionError("Request not found")

            # Get user role from request state
            user_role = getattr(request.state, 'user_role', None)
            if not user_role:
                raise PermissionError("User role not found")

            # Convert string role to enum if needed
            if isinstance(user_role, str):
                try:
                    user_role = OrganizationRole(user_role)
                except ValueError:
                    raise PermissionError(f"Invalid user role: {user_role}")

            # Check if user role is in allowed roles
            if user_role not in allowed_roles:
                logger.warning(
                    f"Role access denied: user_role={user_role}, "
                    f"allowed_roles={allowed_roles}"
                )
                raise PermissionError(
                    f"Access denied. Required roles: {[role.value for role in allowed_roles]}"
                )

            return await func(*args, **kwargs)

        return wrapper
    return decorator


def require_senior_role():
    """
    Decorator to require senior-level access (Partner level and above)
    """
    senior_roles = [
        OrganizationRole.MANAGING_PARTNER,
        OrganizationRole.PARTNER,
        OrganizationRole.DIRECTOR,
        OrganizationRole.ADMIN,
        OrganizationRole.OWNER
    ]
    return require_role(senior_roles)


def require_admin_role():
    """
    Decorator to require admin-level access
    """
    admin_roles = [
        OrganizationRole.MANAGING_PARTNER,
        OrganizationRole.ADMIN,
        OrganizationRole.OWNER
    ]
    return require_role(admin_roles)


# Context loaders for common scenarios
async def load_deal_context(request: Request, user_id: str, org_id: str, *args, **kwargs) -> Dict[str, Any]:
    """
    Load deal-specific context for permission checking
    """
    context = {}

    # Extract deal_id from path parameters or query parameters
    deal_id = kwargs.get('deal_id') or request.path_params.get('deal_id')

    if deal_id:
        # TODO: Query database to check if user is team member or deal lead
        # For now, return basic context
        context.update({
            'deal_id': deal_id,
            'is_team_member': False,  # Will be populated from database
            'is_deal_lead': False,    # Will be populated from database
        })

    return context


async def load_document_context(request: Request, user_id: str, org_id: str, *args, **kwargs) -> Dict[str, Any]:
    """
    Load document-specific context for permission checking
    """
    context = {}

    # Extract document_id from path parameters
    document_id = kwargs.get('document_id') or request.path_params.get('document_id')

    if document_id:
        # TODO: Query database to check document access permissions
        context.update({
            'document_id': document_id,
            'is_document_owner': False,      # Will be populated from database
            'document_sensitivity': 'normal'  # Will be populated from database
        })

    return context


async def load_client_context(request: Request, user_id: str, org_id: str, *args, **kwargs) -> Dict[str, Any]:
    """
    Load client-specific context for permission checking
    """
    context = {}

    # Extract client_id from path parameters
    client_id = kwargs.get('client_id') or request.path_params.get('client_id')

    if client_id:
        # TODO: Query database to check if this is the user's client
        context.update({
            'client_id': client_id,
            'is_client_deal': False,     # Will be populated from database
            'is_client_document': False  # Will be populated from database
        })

    return context


# Utility functions for manual permission checking
def check_permission_in_handler(
    request: Request,
    resource_type: ResourceType,
    action: Action,
    context: Optional[Dict] = None
) -> bool:
    """
    Manually check permissions within a handler function
    """
    user_role = getattr(request.state, 'user_role', None)
    if not user_role:
        return False

    if isinstance(user_role, str):
        try:
            user_role = OrganizationRole(user_role)
        except ValueError:
            return False

    return PermissionChecker.has_permission(user_role, resource_type, action, context)


def get_user_permissions(request: Request, resource_type: ResourceType) -> list[Action]:
    """
    Get all actions a user can perform on a resource type
    """
    user_role = getattr(request.state, 'user_role', None)
    if not user_role:
        return []

    if isinstance(user_role, str):
        try:
            user_role = OrganizationRole(user_role)
        except ValueError:
            return []

    return PermissionChecker.get_allowed_actions(user_role, resource_type)