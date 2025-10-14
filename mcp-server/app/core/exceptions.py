"""
BMAD v6 MCP Server Exception Handling
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

class BMadException(Exception):
    """Base exception for BMAD v6 MCP Server."""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ProjectNotFoundException(BMadException):
    """Raised when a project is not found."""
    def __init__(self, project_id: str):
        super().__init__(f"Project not found: {project_id}", "PROJECT_NOT_FOUND")

class WorkflowNotFoundException(BMadException):
    """Raised when a workflow is not found."""
    def __init__(self, workflow_name: str):
        super().__init__(f"Workflow not found: {workflow_name}", "WORKFLOW_NOT_FOUND")

class AgentNotFoundException(BMadException):
    """Raised when an agent is not found."""
    def __init__(self, agent_name: str):
        super().__init__(f"Agent not found: {agent_name}", "AGENT_NOT_FOUND")

class InvalidStateTransitionException(BMadException):
    """Raised when an invalid state transition is attempted."""
    def __init__(self, from_state: str, to_state: str):
        super().__init__(f"Invalid state transition: {from_state} -> {to_state}", "INVALID_STATE_TRANSITION")

class AuthenticationException(BMadException):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_FAILED")

class AuthorizationException(BMadException):
    """Raised when authorization fails."""
    def __init__(self, message: str = "Authorization failed"):
        super().__init__(message, "AUTHORIZATION_FAILED")

class ValidationException(BMadException):
    """Raised when validation fails."""
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message, "VALIDATION_ERROR")

class WorkflowExecutionException(BMadException):
    """Raised when workflow execution fails."""
    def __init__(self, workflow_name: str, error: str):
        super().__init__(f"Workflow execution failed: {workflow_name} - {error}", "WORKFLOW_EXECUTION_FAILED")

class DatabaseException(BMadException):
    """Raised when database operations fail."""
    def __init__(self, operation: str, error: str):
        super().__init__(f"Database operation failed: {operation} - {error}", "DATABASE_ERROR")

class IntegrationException(BMadException):
    """Raised when external service integration fails."""
    def __init__(self, service: str, error: str):
        super().__init__(f"Integration failed: {service} - {error}", "INTEGRATION_ERROR")

async def bmad_exception_handler(request: Request, exc: BMadException) -> JSONResponse:
    """Handle BMAD-specific exceptions."""
    logger.error(f"BMAD Exception: {exc.error_code} - {exc.message}")
    
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": exc.error_code or "BMAD_ERROR",
            "message": exc.message,
            "timestamp": "2024-01-01T00:00:00Z"  # Would use datetime.utcnow().isoformat()
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "timestamp": "2024-01-01T00:00:00Z"  # Would use datetime.utcnow().isoformat()
        }
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    logger.error(f"Unhandled Exception: {type(exc).__name__} - {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "timestamp": "2024-01-01T00:00:00Z"  # Would use datetime.utcnow().isoformat()
        }
    )
