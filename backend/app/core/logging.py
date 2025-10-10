"""Logging configuration for production environment"""

import logging
import sys
import structlog
from structlog.stdlib import LoggerFactory
from typing import Any, Dict

from app.core.config import settings


def setup_logging() -> None:
    """Configure structured logging for the application"""

    # Set log level based on environment
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Configure stdlib logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level
    )

    # Configure structlog
    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # Add development processors
    if settings.DEBUG:
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        # Production processors
        processors.extend([
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer()
        ])

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True
    )


def get_logger(name: str) -> Any:
    """Get a configured logger instance"""
    return structlog.get_logger(name)


class RequestLogger:
    """Middleware for logging HTTP requests and responses"""

    def __init__(self, logger: Any = None):
        self.logger = logger or get_logger(__name__)

    async def log_request(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: bytes = None
    ) -> None:
        """Log incoming request details"""
        self.logger.info(
            "Request received",
            method=method,
            path=path,
            user_agent=headers.get("user-agent"),
            content_length=headers.get("content-length"),
            environment=settings.ENVIRONMENT
        )

        if settings.DEBUG and body:
            self.logger.debug(
                "Request body",
                body=body[:1000].decode("utf-8", errors="ignore")
            )

    async def log_response(
        self,
        status_code: int,
        duration_ms: float,
        path: str
    ) -> None:
        """Log response details"""
        log_method = self.logger.info if status_code < 400 else self.logger.error

        log_method(
            "Response sent",
            status_code=status_code,
            duration_ms=round(duration_ms, 2),
            path=path
        )


class AuditLogger:
    """Service for audit logging critical operations"""

    def __init__(self):
        self.logger = get_logger("audit")

    async def log_authentication(
        self,
        user_id: str,
        action: str,
        success: bool,
        ip_address: str = None,
        metadata: Dict[str, Any] = None
    ) -> None:
        """Log authentication events"""
        self.logger.info(
            "Authentication event",
            user_id=user_id,
            action=action,
            success=success,
            ip_address=ip_address,
            metadata=metadata or {}
        )

    async def log_data_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        organization_id: str = None
    ) -> None:
        """Log data access events"""
        self.logger.info(
            "Data access",
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            organization_id=organization_id
        )

    async def log_payment_event(
        self,
        organization_id: str,
        event_type: str,
        amount: float = None,
        currency: str = "USD",
        metadata: Dict[str, Any] = None
    ) -> None:
        """Log payment-related events"""
        self.logger.info(
            "Payment event",
            organization_id=organization_id,
            event_type=event_type,
            amount=amount,
            currency=currency,
            metadata=metadata or {}
        )

    async def log_ai_usage(
        self,
        user_id: str,
        operation: str,
        tokens_used: int = None,
        cost: float = None,
        metadata: Dict[str, Any] = None
    ) -> None:
        """Log AI service usage"""
        self.logger.info(
            "AI usage",
            user_id=user_id,
            operation=operation,
            tokens_used=tokens_used,
            estimated_cost=cost,
            metadata=metadata or {}
        )


# Create global instances
request_logger = RequestLogger()
audit_logger = AuditLogger()