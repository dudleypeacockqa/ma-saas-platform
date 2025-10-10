"""
Database initialization with proper error handling for concurrent deployments
"""
import logging
from sqlalchemy import text, inspect
from sqlalchemy.exc import ProgrammingError, IntegrityError
from typing import Optional

logger = logging.getLogger(__name__)


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

        # First, try to create all tables with checkfirst=True
        # This will skip tables that already exist
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

    Args:
        engine: SQLAlchemy engine

    Returns:
        bool: True if successful, False otherwise
    """
    extensions = ['uuid-ossp', 'vector']

    try:
        with engine.connect() as conn:
            for ext in extensions:
                try:
                    # Use IF NOT EXISTS to avoid errors
                    conn.execute(text(f'CREATE EXTENSION IF NOT EXISTS "{ext}"'))
                    conn.commit()
                    logger.debug(f"Extension {ext} ready")
                except Exception as e:
                    # Some extensions might not be available, log but don't fail
                    logger.warning(f"Could not create extension {ext}: {e}")

        return True

    except Exception as e:
        logger.error(f"Failed to create extensions: {e}")
        return False
