"""
BMAD v6 MCP Server Main API Tests
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
from datetime import datetime
import asyncio

from app.main import app
from app.db.base import Base
from app.db.init_db import get_db
from app.services.security_manager import SecurityManager

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as client:
        yield client

# Test fixtures
@pytest.fixture
def test_token():
    """Generate test JWT token."""
    security_manager = SecurityManager()
    return asyncio.run(security_manager.generate_token("test_user", ["read", "write"]))

@pytest.fixture
def test_project_data():
    """Test project data."""
    return {
        "project_id": "test-project-001",
        "name": "Test M&A Project",
        "description": "Test project for BMAD v6 MCP server",
        "estimated_stories": 15,
        "estimated_epics": 3,
        "complexity": "medium",
        "team_size": 5,
        "timeline_weeks": 8
    }

class TestMainEndpoints:
    """Test main API endpoints."""
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "BMAD v6 MCP Server"

    def test_health_check(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

class TestWorkflowExecution:
    """Test workflow execution endpoints."""
    
    def test_execute_workflow_status(self, client: TestClient, test_token: str):
        """Test workflow-status execution."""
        headers = {"Authorization": f"Bearer {test_token}"}
        payload = {
            "workflow_name": "workflow-status",
            "context": {},
            "project_id": "test-project-001"
        }
        
        response = client.post("/api/v1/workflow/execute", headers=headers, json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["workflow_name"] == "workflow-status"

