from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import logging

# Import Base from models
from app.models.base import Base

load_dotenv()
logger = logging.getLogger(__name__)

# Database URL - will be configured for Render PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://ma_user:ma_password@localhost:5432/ma_saas_platform"
)

# Handle different URL formats for sync and async connections
def get_sync_database_url(url: str) -> str:
    """Convert database URL for synchronous drivers"""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
    if url.startswith("sqlite+aiosqlite://"):
        return url.replace("sqlite+aiosqlite://", "sqlite://", 1)
    return url

def get_async_database_url(url: str) -> str:
    """Convert database URL for asynchronous drivers"""
    if url.startswith("sqlite://") and not url.startswith("sqlite+aiosqlite://"):
        return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql+psycopg"):
        return url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)
    return url

# Create URLs for both sync and async
SYNC_DATABASE_URL = get_sync_database_url(DATABASE_URL)
ASYNC_DATABASE_URL = get_async_database_url(DATABASE_URL)

logger.info(f"Sync DB URL configured: {SYNC_DATABASE_URL.split('@')[0]}@[HIDDEN]")
logger.info(f"Async DB URL configured: {ASYNC_DATABASE_URL.split('@')[0]}@[HIDDEN]")

# Sync engine and session (for startup, migrations, and non-async operations)
engine = create_engine(
    SYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  # Set to True for SQL debugging
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async engine and session (for async API operations)
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  # Set to True for SQL debugging
)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
