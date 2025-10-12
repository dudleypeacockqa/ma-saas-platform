"""
Database initialization with proper error handling for concurrent deployments
"""
import logging
from sqlalchemy import text, inspect, event
from sqlalchemy.schema import DDL
from sqlalchemy.exc import ProgrammingError, IntegrityError
from typing import Optional

logger = logging.getLogger(__name__)


def _enable_if_not_exists_for_indexes(engine):
    """
    Monkey-patch SQLAlchemy to use IF NOT EXISTS for index creation.

    This prevents "already exists" errors when multiple app instances
    start concurrently and try to create the same indexes.

    PostgreSQL supports IF NOT EXISTS for indexes starting from version 9.5.
    """
    @event.listens_for(engine, "before_cursor_execute", retval=True)
    def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
        # Intercept CREATE INDEX statements and add IF NOT EXISTS
        if statement.strip().upper().startswith("CREATE INDEX"):
            # Check if IF NOT EXISTS is already present
            if "IF NOT EXISTS" not in statement.upper():
                # Insert IF NOT EXISTS after CREATE INDEX
                statement = statement.replace("CREATE INDEX", "CREATE INDEX IF NOT EXISTS", 1)
                logger.debug(f"Modified index creation to use IF NOT EXISTS")

        return statement, params


def init_database(engine, metadata) -> bool:
    """
    Initialize database tables and indexes safely.

    Handles race conditions when multiple app instances start simultaneously.
    Uses IF NOT EXISTS where possible to prevent duplicate object errors.

    Args:
        engine: SQLAlchemy engine
        metadata: SQLAlchemy metadata object

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("Initializing database schema...")

        # Enable IF NOT EXISTS for index creation to prevent race condition errors
        _enable_if_not_exists_for_indexes(engine)

        # Create all tables with checkfirst=True
        # This will skip tables that already exist
        # The event listener will modify CREATE INDEX statements to use IF NOT EXISTS
        metadata.create_all(bind=engine, checkfirst=True)

        logger.info(f"Database schema initialized ({len(metadata.tables)} tables defined)")
        return True

    except Exception as e:
        error_msg = str(e).lower()

        # Handle expected duplicate errors from race conditions
        if 'already exists' in error_msg or 'duplicate' in error_msg:
            logger.info("Database objects already exist (expected in concurrent deployments)")
            logger.debug(f"Creation skipped: {e}")
            return True

        # Handle other database errors
        logger.error(f"Failed to initialize database schema: {e}")
        logger.warning("Application will continue, but database operations may fail")
        return False


def verify_critical_tables(engine, required_tables: list[str]) -> bool:
    """
    Verify that critical tables exist in the database.

    Args:
        engine: SQLAlchemy engine
        required_tables: List of table names that must exist

    Returns:
        bool: True if all required tables exist, False otherwise
    """
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        missing_tables = [table for table in required_tables if table not in existing_tables]

        if missing_tables:
            logger.error(f"Critical tables missing: {missing_tables}")
            return False

        logger.info(f"All {len(required_tables)} critical tables verified")
        return True

    except Exception as e:
        logger.error(f"Failed to verify critical tables: {e}")
        return False


def create_extensions(engine) -> bool:
    """
    Create required PostgreSQL extensions if they don't exist.
    Uses synchronous database operations only.

    Args:
        engine: SQLAlchemy sync engine

    Returns:
        bool: True if successful, False otherwise
    """
    extensions = ['uuid-ossp']  # Removed 'vector' as it might not be available

    try:
        # Use a transaction to ensure consistency
        with engine.begin() as conn:
            for ext in extensions:
                try:
                    # Use IF NOT EXISTS to avoid errors
                    conn.execute(text(f'CREATE EXTENSION IF NOT EXISTS "{ext}"'))
                    logger.debug(f"Extension {ext} ready")
                except Exception as e:
                    # Some extensions might not be available, log but don't fail
                    logger.warning(f"Could not create extension {ext}: {e}")

        logger.info(f"Database extensions setup completed")
        return True

    except Exception as e:
        logger.error(f"Failed to create extensions: {e}")
        return False
