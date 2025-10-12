"""
Sentry integration for error tracking and performance monitoring
"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging
import os
from typing import Optional

from app.core.config import settings


def init_sentry():
    """
    Initialize Sentry SDK for error tracking and performance monitoring
    """
    sentry_dsn = os.getenv("SENTRY_DSN")

    if not sentry_dsn:
        logging.info("Sentry DSN not configured. Skipping Sentry initialization.")
        return

    # Determine environment
    environment = os.getenv("ENVIRONMENT", "development")

    # Initialize Sentry
    sentry_sdk.init(
        dsn=sentry_dsn,
        # Set environment (production, staging, development)
        environment=environment,

        # Release version (use git commit hash or version number)
        release=os.getenv("GIT_COMMIT_SHA", "unknown"),

        # Enable integrations
        integrations=[
            # FastAPI integration for request/response tracking
            FastApiIntegration(
                transaction_style="url",  # Group transactions by URL pattern
            ),

            # SQLAlchemy integration for database query tracking
            SqlalchemyIntegration(),

            # Redis integration for cache tracking
            RedisIntegration(),

            # Logging integration
            LoggingIntegration(
                level=logging.INFO,  # Capture info and above as breadcrumbs
                event_level=logging.ERROR,  # Send errors and above as events
            ),
        ],

        # Performance monitoring
        traces_sample_rate=get_traces_sample_rate(environment),

        # Profiling (CPU and memory usage)
        profiles_sample_rate=get_profiles_sample_rate(environment),

        # Error sampling
        sample_rate=1.0,  # Capture 100% of errors

        # Maximum breadcrumbs
        max_breadcrumbs=50,

        # Attach stack traces to logs
        attach_stacktrace=True,

        # Send default PII (Personally Identifiable Information)
        send_default_pii=False,  # Disable for privacy

        # Debug mode (only in development)
        debug=environment == "development",

        # Before send hook for filtering/modifying events
        before_send=before_send_hook,

        # Before send transaction hook
        before_send_transaction=before_send_transaction_hook,
    )

    logging.info(f"Sentry initialized for environment: {environment}")


def get_traces_sample_rate(environment: str) -> float:
    """
    Get performance tracing sample rate based on environment

    Args:
        environment: Current environment (production, staging, development)

    Returns:
        Sample rate (0.0 to 1.0)
    """
    rates = {
        "production": 0.1,  # Sample 10% of transactions in production
        "staging": 0.5,     # Sample 50% in staging
        "development": 1.0,  # Sample 100% in development
    }
    return rates.get(environment, 0.1)


def get_profiles_sample_rate(environment: str) -> float:
    """
    Get profiling sample rate based on environment

    Args:
        environment: Current environment (production, staging, development)

    Returns:
        Sample rate (0.0 to 1.0)
    """
    rates = {
        "production": 0.01,  # Profile 1% of transactions in production
        "staging": 0.1,      # Profile 10% in staging
        "development": 0.5,   # Profile 50% in development
    }
    return rates.get(environment, 0.01)


def before_send_hook(event, hint):
    """
    Hook called before sending events to Sentry
    Use this to filter or modify events

    Args:
        event: Sentry event dictionary
        hint: Additional context about the event

    Returns:
        Modified event or None to drop the event
    """
    # Filter out specific exceptions if needed
    if "exc_info" in hint:
        exc_type, exc_value, tb = hint["exc_info"]

        # Don't send 404 errors
        if "404" in str(exc_value):
            return None

        # Don't send validation errors (they're expected)
        if "ValidationError" in str(exc_type):
            return None

    # Remove sensitive data from event
    if "request" in event:
        # Remove authorization headers
        if "headers" in event["request"]:
            if "Authorization" in event["request"]["headers"]:
                event["request"]["headers"]["Authorization"] = "[Filtered]"
            if "X-API-Key" in event["request"]["headers"]:
                event["request"]["headers"]["X-API-Key"] = "[Filtered]"

        # Remove sensitive query parameters
        if "query_string" in event["request"]:
            sensitive_params = ["api_key", "token", "password", "secret"]
            for param in sensitive_params:
                if param in event["request"]["query_string"]:
                    event["request"]["query_string"] = event["request"]["query_string"].replace(
                        param, "[Filtered]"
                    )

    return event


def before_send_transaction_hook(event, hint):
    """
    Hook called before sending transactions to Sentry
    Use this to filter or modify transaction events

    Args:
        event: Sentry transaction event
        hint: Additional context

    Returns:
        Modified event or None to drop the event
    """
    # Don't send health check transactions
    if event.get("transaction") == "/health":
        return None

    # Don't send static file transactions
    if event.get("transaction", "").startswith("/static/"):
        return None

    return event


def set_user_context(user_id: str, email: Optional[str] = None, organization_id: Optional[str] = None):
    """
    Set user context for Sentry events

    Args:
        user_id: User ID
        email: User email (optional)
        organization_id: Organization/tenant ID (optional)
    """
    sentry_sdk.set_user({
        "id": user_id,
        "email": email,
        "organization_id": organization_id,
    })


def set_context(key: str, data: dict):
    """
    Set custom context for Sentry events

    Args:
        key: Context key
        data: Context data dictionary
    """
    sentry_sdk.set_context(key, data)


def add_breadcrumb(message: str, category: str = "default", level: str = "info", data: Optional[dict] = None):
    """
    Add a breadcrumb to the current scope

    Args:
        message: Breadcrumb message
        category: Category (e.g., "auth", "db", "api")
        level: Level (debug, info, warning, error, critical)
        data: Additional data dictionary
    """
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {},
    )


def capture_exception(exception: Exception, **kwargs):
    """
    Manually capture an exception

    Args:
        exception: Exception to capture
        **kwargs: Additional context
    """
    sentry_sdk.capture_exception(exception, **kwargs)


def capture_message(message: str, level: str = "info", **kwargs):
    """
    Manually capture a message

    Args:
        message: Message to capture
        level: Level (debug, info, warning, error, fatal)
        **kwargs: Additional context
    """
    sentry_sdk.capture_message(message, level=level, **kwargs)


def start_transaction(name: str, op: str):
    """
    Start a new transaction for performance monitoring

    Args:
        name: Transaction name
        op: Operation type (e.g., "http.server", "db.query")

    Returns:
        Transaction context manager
    """
    return sentry_sdk.start_transaction(name=name, op=op)


def start_span(op: str, description: Optional[str] = None):
    """
    Start a new span within a transaction

    Args:
        op: Operation type
        description: Span description

    Returns:
        Span context manager
    """
    return sentry_sdk.start_span(op=op, description=description)


# ============================================================================
# DECORATORS
# ============================================================================

def monitor_performance(op: str = "function"):
    """
    Decorator to monitor function performance

    Args:
        op: Operation type for span

    Example:
        @monitor_performance(op="service.create_deal")
        def create_deal(...):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with start_span(op=op, description=func.__name__):
                return func(*args, **kwargs)
        return wrapper
    return decorator


async def monitor_async_performance(op: str = "async.function"):
    """
    Decorator to monitor async function performance

    Args:
        op: Operation type for span

    Example:
        @monitor_async_performance(op="service.fetch_data")
        async def fetch_data(...):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            with start_span(op=op, description=func.__name__):
                return await func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
# In main.py:
from app.core.sentry import init_sentry

@app.on_event("startup")
async def startup():
    init_sentry()

# In route handlers:
from app.core.sentry import set_user_context, add_breadcrumb, capture_exception

@app.get("/api/deals")
async def get_deals(current_user = Depends(get_current_user)):
    # Set user context
    set_user_context(
        user_id=current_user.id,
        email=current_user.email,
        organization_id=current_user.organization_id
    )

    # Add breadcrumb
    add_breadcrumb(
        message="Fetching deals",
        category="api",
        data={"organization_id": current_user.organization_id}
    )

    try:
        # Your code here
        pass
    except Exception as e:
        # Capture exception
        capture_exception(e)
        raise

# Performance monitoring:
from app.core.sentry import start_transaction, start_span

with start_transaction(name="process_deal", op="task"):
    with start_span(op="db.query", description="fetch deal"):
        deal = db.query(Deal).filter_by(id=deal_id).first()

    with start_span(op="service.calculate", description="calculate valuation"):
        valuation = calculate_valuation(deal)

    with start_span(op="db.insert", description="save valuation"):
        db.add(valuation)
        db.commit()
"""
