"""
Test Database Configuration
Provides SQLite-compatible database setup for testing without async issues
"""

import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import logging

logger = logging.getLogger(__name__)

def get_test_database_config():
    """Get test database configuration that works with SQLite"""

    # Use in-memory SQLite for testing
    if os.getenv('TESTING') == 'true':
        # In-memory SQLite database for fast testing
        database_url = "sqlite:///:memory:"

        # Create engine with special SQLite settings
        engine = create_engine(
            database_url,
            connect_args={
                "check_same_thread": False,  # Allow SQLite to work with multiple threads
            },
            poolclass=StaticPool,  # Use static pool for in-memory database
            echo=False  # Set to True for SQL debugging
        )

        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        logger.info("Test database configured with in-memory SQLite")

        return {
            'engine': engine,
            'SessionLocal': SessionLocal,
            'database_url': database_url,
            'is_async': False
        }

    # For non-test environments, use file-based SQLite
    else:
        # Create a temporary SQLite file
        db_file = os.path.join(tempfile.gettempdir(), 'ma_platform_test.db')
        database_url = f"sqlite:///{db_file}"

        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            echo=False
        )

        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        logger.info(f"Test database configured with file: {db_file}")

        return {
            'engine': engine,
            'SessionLocal': SessionLocal,
            'database_url': database_url,
            'is_async': False
        }

def get_test_db_session():
    """Get a test database session"""
    config = get_test_database_config()
    db = config['SessionLocal']()
    try:
        yield db
    finally:
        db.close()

def create_test_tables():
    """Create all tables for testing"""
    try:
        # Import all models to ensure they're registered
        from app.models.base import Base
        from app.models.organization import Organization
        from app.models.deal import Deal, DealParticipant, DealDocument, DealActivity
        from app.models.financial_models import (
            FinancialStatement, CashFlowProjection, FinancialMetric,
            RatioAnalysis, BenchmarkData
        )
        from app.models.documents import GeneratedDocument
        from app.models.market_research import MarketOpportunity

        # Try to import User models if they exist
        try:
            from app.models.user import User, OrganizationMembership
        except ImportError:
            logger.warning("User models not found - skipping user table creation")

        config = get_test_database_config()
        engine = config['engine']

        # Create all tables
        Base.metadata.create_all(bind=engine)

        logger.info("Test database tables created successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to create test tables: {e}")
        return False

# Global test configuration
_test_config = None

def get_test_config():
    """Get or create test configuration"""
    global _test_config
    if _test_config is None:
        _test_config = get_test_database_config()
    return _test_config