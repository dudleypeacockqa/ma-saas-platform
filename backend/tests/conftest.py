"""
Global pytest configuration and fixtures for M&A SaaS Platform tests
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from datetime import datetime, timedelta
import os
import warnings

from sqlalchemy import create_engine, event
from sqlalchemy.exc import MovedIn20Warning
from pydantic.warnings import PydanticDeprecatedSince20
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Set test environment before importing app
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("FRONTEND_URL", "http://localhost:5173")

from app.core.database import get_db, Base
from app.models.base import Base as ModelsBase
from app.core.config import settings

warnings.filterwarnings("ignore", category=MovedIn20Warning)
warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)

SKIP_APP_IMPORT = os.getenv('PYTEST_SKIP_APP_IMPORT') == '1'

if SKIP_APP_IMPORT:
    from fastapi import FastAPI
    app = FastAPI()
    from app.models import (
        organization,
        user,
    )
else:
    from app.main import app
    from app.models import (
        organization,
        user,
        deal,
        documents,
        opportunities,
        financial_models,
        negotiations,
        teams,
    )


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def engine():
    """Create a test database engine for the entire test session"""
    # Use in-memory SQLite database for tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    tables = []
    if SKIP_APP_IMPORT:
        table_names = ['users', 'organizations', 'organization_memberships', 'permissions']
        tables = [ModelsBase.metadata.tables[name] for name in table_names if name in ModelsBase.metadata.tables]
        ModelsBase.metadata.create_all(bind=engine, tables=tables)
    else:
        ModelsBase.metadata.create_all(bind=engine)

    yield engine

    if SKIP_APP_IMPORT and tables:
        ModelsBase.metadata.drop_all(bind=engine, tables=tables)
    else:
        ModelsBase.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine) -> Generator[Session, None, None]:
    """Create a fresh database session for each test"""
    connection = engine.connect()
    transaction = connection.begin()

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database session override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ============================================================================
# ASYNC FIXTURES
# ============================================================================

# ============================================================================
# AUTHENTICATION FIXTURES
# ============================================================================

@pytest.fixture
def mock_clerk_user():
    """Mock Clerk user data"""
    return {
        "user_id": "user_test123",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "organization_id": "org_test123",
        "organization_role": "admin",
        "email_verified": True,
    }


@pytest.fixture
def auth_headers(mock_clerk_user):
    """Generate authentication headers with mock JWT token"""
    # In real tests, you'd generate a proper JWT token
    # For now, we'll use a mock token
    return {
        "Authorization": "Bearer test_token_123",
        "X-Organization-ID": mock_clerk_user["organization_id"],
    }


@pytest.fixture
def admin_auth_headers(mock_clerk_user):
    """Generate admin authentication headers"""
    admin_user = mock_clerk_user.copy()
    admin_user["organization_role"] = "admin"
    return {
        "Authorization": "Bearer admin_token_123",
        "X-Organization-ID": admin_user["organization_id"],
    }


# ============================================================================
# MODEL FACTORY FIXTURES
# ============================================================================

@pytest.fixture
def organization_factory(db_session):
    """Factory for creating test organizations"""
    from app.models.organization import Organization

    def _create_organization(
        name: str = "Test Organization",
        email: str = "test@testorg.com",
        **kwargs
    ):
        org = Organization(
            id=kwargs.get("id", "org_test123"),
            name=name,
            email=email,
            status=kwargs.get("status", "active"),
            subscription_tier=kwargs.get("subscription_tier", "free"),
            subscription_status=kwargs.get("subscription_status", "active"),
            clerk_organization_id=kwargs.get("clerk_organization_id", "org_clerk123"),
        )
        db_session.add(org)
        db_session.commit()
        db_session.refresh(org)
        return org

    return _create_organization


@pytest.fixture
def user_factory(db_session, organization_factory):
    """Factory for creating test users"""
    from app.models.user import User

    def _create_user(
        email: str = "testuser@example.com",
        organization_id: str = None,
        **kwargs
    ):
        if organization_id is None:
            org = organization_factory()
            organization_id = org.id

        user = User(
            id=kwargs.get("id", "user_test123"),
            email=email,
            first_name=kwargs.get("first_name", "Test"),
            last_name=kwargs.get("last_name", "User"),
            organization_id=organization_id,
            role=kwargs.get("role", "member"),
            is_active=kwargs.get("is_active", True),
            clerk_user_id=kwargs.get("clerk_user_id", "user_clerk123"),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create_user


@pytest.fixture
def deal_factory(db_session, organization_factory, user_factory):
    """Factory for creating test deals"""
    from app.models.deal import Deal

    def _create_deal(
        title: str = "Test Deal",
        organization_id: str = None,
        created_by: str = None,
        **kwargs
    ):
        if organization_id is None:
            org = organization_factory()
            organization_id = org.id

        if created_by is None:
            user = user_factory(organization_id=organization_id)
            created_by = user.id

        deal = Deal(
            organization_id=organization_id,
            title=title,
            deal_type=kwargs.get("deal_type", "acquisition"),
            stage=kwargs.get("stage", "sourcing"),
            priority=kwargs.get("priority", "medium"),
            target_company_name=kwargs.get("target_company_name", "Target Corp"),
            deal_currency=kwargs.get("deal_currency", "USD"),
            probability_of_close=kwargs.get("probability_of_close", 50),
            is_active=kwargs.get("is_active", True),
            is_confidential=kwargs.get("is_confidential", False),
            created_by=created_by,
        )
        db_session.add(deal)
        db_session.commit()
        db_session.refresh(deal)
        return deal

    return _create_deal


@pytest.fixture
def document_factory(db_session, organization_factory, deal_factory):
    """Factory for creating test documents"""
    from app.models.documents import Document

    def _create_document(
        filename: str = "test_document.pdf",
        organization_id: str = None,
        deal_id: str = None,
        **kwargs
    ):
        if organization_id is None:
            org = organization_factory()
            organization_id = org.id

        if deal_id is None and kwargs.get("with_deal", False):
            deal = deal_factory(organization_id=organization_id)
            deal_id = deal.id

        doc = Document(
            organization_id=organization_id,
            deal_id=deal_id,
            filename=filename,
            original_filename=kwargs.get("original_filename", filename),
            file_extension=kwargs.get("file_extension", ".pdf"),
            mime_type=kwargs.get("mime_type", "application/pdf"),
            file_size=kwargs.get("file_size", 1024000),
            document_type=kwargs.get("document_type", "other"),
            status=kwargs.get("status", "active"),
            folder_path=kwargs.get("folder_path", "/"),
            version=kwargs.get("version", 1),
            is_latest_version=kwargs.get("is_latest_version", True),
            is_confidential=kwargs.get("is_confidential", False),
        )
        db_session.add(doc)
        db_session.commit()
        db_session.refresh(doc)
        return doc

    return _create_document


@pytest.fixture
def opportunity_factory(db_session, organization_factory):
    """Factory for creating test opportunities"""
    from app.models.opportunities import Opportunity

    def _create_opportunity(
        company_name: str = "Target Company",
        organization_id: str = None,
        **kwargs
    ):
        if organization_id is None:
            org = organization_factory()
            organization_id = org.id

        opp = Opportunity(
            organization_id=organization_id,
            company_name=company_name,
            industry=kwargs.get("industry", "Technology"),
            country=kwargs.get("country", "USA"),
            status=kwargs.get("status", "identified"),
            source=kwargs.get("source", "manual"),
            strategic_fit_score=kwargs.get("strategic_fit_score", 75.0),
            financial_attractiveness_score=kwargs.get("financial_attractiveness_score", 70.0),
            synergy_potential_score=kwargs.get("synergy_potential_score", 80.0),
            overall_score=kwargs.get("overall_score", 75.0),
            priority=kwargs.get("priority", "medium"),
        )
        db_session.add(opp)
        db_session.commit()
        db_session.refresh(opp)
        return opp

    return _create_opportunity


# ============================================================================
# TIME-BASED FIXTURES
# ============================================================================

@pytest.fixture
def freeze_time():
    """Fixture to freeze time for testing"""
    frozen_time = datetime(2024, 1, 15, 12, 0, 0)
    return frozen_time


@pytest.fixture
def sample_dates():
    """Fixture providing sample dates for testing"""
    base_date = datetime(2024, 1, 1)
    return {
        "past": base_date - timedelta(days=30),
        "present": base_date,
        "future": base_date + timedelta(days=30),
        "far_future": base_date + timedelta(days=90),
    }


# ============================================================================
# MOCK SERVICE FIXTURES
# ============================================================================

@pytest.fixture
def mock_redis():
    """Mock Redis client for caching tests"""
    class MockRedis:
        def __init__(self):
            self.store = {}

        async def get(self, key):
            return self.store.get(key)

        async def set(self, key, value, ex=None):
            self.store[key] = value
            return True

        async def delete(self, key):
            if key in self.store:
                del self.store[key]
            return True

        async def exists(self, key):
            return key in self.store

        async def ping(self):
            return True

    return MockRedis()


@pytest.fixture
def mock_s3_client():
    """Mock S3/R2 client for file storage tests"""
    class MockS3:
        def __init__(self):
            self.buckets = {}

        def upload_fileobj(self, file, bucket, key, **kwargs):
            if bucket not in self.buckets:
                self.buckets[bucket] = {}
            self.buckets[bucket][key] = file.read()
            return True

        def download_fileobj(self, bucket, key, file):
            if bucket in self.buckets and key in self.buckets[bucket]:
                file.write(self.buckets[bucket][key])
                return True
            raise Exception("File not found")

        def generate_presigned_url(self, operation, Params, ExpiresIn=3600):
            return f"https://mock-s3.com/{Params['Bucket']}/{Params['Key']}?expires={ExpiresIn}"

    return MockS3()


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic Claude client for AI tests"""
    class MockAnthropic:
        def __init__(self):
            self.messages = []

        class Messages:
            @staticmethod
            def create(**kwargs):
                class MockMessage:
                    def __init__(self):
                        self.content = [
                            type('Content', (), {'text': 'Mock AI response'})()
                        ]
                return MockMessage()

        messages = Messages()

    return MockAnthropic()


# ============================================================================
# CLEANUP FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def reset_settings():
    """Reset settings after each test"""
    yield
    # Reset any modified settings
    settings.DEBUG = False


@pytest.fixture(autouse=True)
def clear_caches():
    """Clear all caches before each test"""
    yield
    # Clear any in-memory caches here


# ============================================================================
# MARKER UTILITIES
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom settings"""
    config.addinivalue_line(
        "markers", "requires_db: mark test as requiring database connection"
    )
    config.addinivalue_line(
        "markers", "requires_redis: mark test as requiring Redis connection"
    )
    config.addinivalue_line(
        "markers", "requires_s3: mark test as requiring S3/R2 storage"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add unit marker to tests without other markers
        if not any(mark.name in ["integration", "e2e", "slow"] for mark in item.iter_markers()):
            item.add_marker(pytest.mark.unit)
