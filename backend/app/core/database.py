from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Create declarative base for models
Base = declarative_base()

# Database URL - will be configured for Render PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost/ma_saas_db"
)

# Handle Render's postgres:// URL format
# Sync engine uses psycopg, async engine uses asyncpg
SYNC_DATABASE_URL = DATABASE_URL
ASYNC_DATABASE_URL = DATABASE_URL

if SYNC_DATABASE_URL.startswith("postgres://"):
    SYNC_DATABASE_URL = SYNC_DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif SYNC_DATABASE_URL.startswith("postgresql://"):
    SYNC_DATABASE_URL = SYNC_DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

if ASYNC_DATABASE_URL.startswith("postgres://"):
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif ASYNC_DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Sync engine and session
engine = create_engine(SYNC_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async engine and session
async_engine = create_async_engine(ASYNC_DATABASE_URL)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
