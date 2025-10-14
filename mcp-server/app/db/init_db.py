"""
BMAD v6 MCP Server Database Initialization
"""

from sqlalchemy.orm import Session
from app.db.session import engine
from app.db.base import Base
from app.db.models import *
import logging

logger = logging.getLogger(__name__)

def init_db() -> None:
    """Initialize database tables."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise

def get_db():
    """Dependency to get database session."""
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
