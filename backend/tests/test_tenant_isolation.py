"""Tests for multi-tenant data isolation"""

import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session
from uuid import uuid4

from app.core.tenant_isolation import (
    TenantValidator,
    TenantAwareSession,
    TenantIsolationError,
    TenantSecurityAuditor,
    validate_tenant_config
)
from app.models.base import Base


class MockModel(Base):
    """Mock model for testing"""
    __tablename__ = "mock_model"

    id = "test_id"
    organization_id = "test_org"
    name = "test_name"


class TestTenantValidator:
    """Test suite for TenantValidator"""

    def test_validator_initialization(self):
        """Test validator initializes correctly"""
        org_id = str(uuid4())
        user_id = str(uuid4())

        validator = TenantValidator(org_id, user_id)

        assert validator.organization_id == org_id
        assert validator.user_id == user_id
        assert validator._validated == False

    def test_validate_access_without_org_id(self):
        """Test validation fails for models without organization_id"""
        validator = TenantValidator("org1", "user1")

        class BadModel:
            pass

        with pytest.raises(TenantIsolationError):
            validator.validate_access(BadModel, "resource_id")

    def test_filter_query_applies_organization_filter(self):
        """Test query filtering applies organization constraint"""
        org_id = str(uuid4())
        validator = TenantValidator(org_id, "user1")

        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)

        result = validator.filter_query(mock_query, MockModel)

        mock_query.filter.assert_called_once()
        assert result == mock_query

    def test_validate_create_enforces_organization(self):
        """Test creation validation enforces correct organization"""
        org_id = str(uuid4())
        validator = TenantValidator(org_id, "user1")

        # Valid instance
        valid_instance = Mock()
        valid_instance.organization_id = org_id
        validator.validate_create(valid_instance)  # Should not raise

        # Invalid instance
        invalid_instance = Mock()
        invalid_instance.organization_id = "different_org"

        with pytest.raises(TenantIsolationError):
            validator.validate_create(invalid_instance)

    def test_validate_update_prevents_org_change(self):
        """Test update validation prevents organization changes"""
        org_id = str(uuid4())
        validator = TenantValidator(org_id, "user1")

        instance = Mock()
        instance.organization_id = org_id

        # Valid update
        validator.validate_update(instance, {"name": "new_name"})

        # Invalid update - changing organization
        with pytest.raises(TenantIsolationError):
            validator.validate_update(instance, {"organization_id": "different_org"})

        # Invalid update - wrong organization
        wrong_instance = Mock()
        wrong_instance.organization_id = "different_org"

        with pytest.raises(TenantIsolationError):
            validator.validate_update(wrong_instance, {"name": "new_name"})


class TestTenantAwareSession:
    """Test suite for TenantAwareSession"""

    def test_session_initialization(self):
        """Test tenant-aware session initializes correctly"""
        mock_session = Mock(spec=Session)
        validator = TenantValidator("org1", "user1")

        tenant_session = TenantAwareSession(mock_session, validator)

        assert tenant_session.session == mock_session
        assert tenant_session.validator == validator

    def test_query_applies_tenant_filter(self):
        """Test query method applies tenant filtering"""
        mock_session = Mock(spec=Session)
        mock_query = Mock()
        mock_session.query = Mock(return_value=mock_query)

        validator = TenantValidator("org1", "user1")
        tenant_session = TenantAwareSession(mock_session, validator)

        result = tenant_session.query(MockModel)

        mock_session.query.assert_called_once_with(MockModel)

    def test_add_validates_organization(self):
        """Test add method validates organization"""
        mock_session = Mock(spec=Session)
        validator = TenantValidator("org1", "user1")
        tenant_session = TenantAwareSession(mock_session, validator)

        # Valid instance
        valid_instance = Mock()
        valid_instance.organization_id = "org1"

        tenant_session.add(valid_instance)
        mock_session.add.assert_called_once_with(valid_instance)

        # Invalid instance
        invalid_instance = Mock()
        invalid_instance.organization_id = "org2"

        with pytest.raises(TenantIsolationError):
            tenant_session.add(invalid_instance)

    def test_delete_validates_organization(self):
        """Test delete method validates organization"""
        mock_session = Mock(spec=Session)
        validator = TenantValidator("org1", "user1")
        tenant_session = TenantAwareSession(mock_session, validator)

        # Valid instance
        valid_instance = Mock()
        valid_instance.organization_id = "org1"

        tenant_session.delete(valid_instance)
        mock_session.delete.assert_called_once_with(valid_instance)

        # Invalid instance
        invalid_instance = Mock()
        invalid_instance.organization_id = "org2"

        with pytest.raises(TenantIsolationError):
            tenant_session.delete(invalid_instance)


class TestTenantSecurityAuditor:
    """Test suite for TenantSecurityAuditor"""

    def test_auditor_initialization(self):
        """Test auditor initializes correctly"""
        mock_db = Mock(spec=Session)
        auditor = TenantSecurityAuditor(mock_db)

        assert auditor.db == mock_db
        assert auditor.violations == []

    def test_audit_model_detects_missing_org_id(self):
        """Test audit detects models without organization_id"""
        mock_db = Mock(spec=Session)
        auditor = TenantSecurityAuditor(mock_db)

        class NoOrgModel:
            __name__ = "NoOrgModel"

        violations = auditor.audit_model(NoOrgModel)

        assert len(violations) == 1
        assert violations[0]["issue"] == "Missing organization_id field"
        assert violations[0]["severity"] == "HIGH"

    def test_audit_model_detects_missing_index(self):
        """Test audit detects missing indexes on organization_id"""
        mock_db = Mock(spec=Session)
        auditor = TenantSecurityAuditor(mock_db)

        class ModelWithoutIndex:
            __name__ = "ModelWithoutIndex"
            organization_id = "test"
            __table__ = Mock()
            __table__.indexes = []

        violations = auditor.audit_model(ModelWithoutIndex)

        assert any(v["issue"] == "Missing index on organization_id" for v in violations)

    def test_test_isolation(self):
        """Test isolation testing functionality"""
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_db.query = Mock(return_value=mock_query)

        auditor = TenantSecurityAuditor(mock_db)

        result = auditor.test_isolation(MockModel, "org1", "org2")

        assert result == True  # Simplified test


class TestValidateTenantConfig:
    """Test suite for configuration validation"""

    def test_validate_config_returns_report(self):
        """Test configuration validation returns proper report"""
        report = validate_tenant_config()

        assert "status" in report
        assert "checks" in report
        assert "warnings" in report
        assert "errors" in report

        assert isinstance(report["checks"], list)
        assert len(report["checks"]) > 0

    def test_validate_config_checks_requirements(self):
        """Test validation checks all requirements"""
        report = validate_tenant_config()

        check_names = [check["name"] for check in report["checks"]]

        assert "Multi-tenant mode enabled" in check_names
        assert "Organization ID required" in check_names
        assert "Audit logging enabled" in check_names


@pytest.mark.integration
class TestTenantIsolationIntegration:
    """Integration tests for tenant isolation"""

    @pytest.fixture
    def db_session(self):
        """Create a test database session"""
        # This would be a real test database in production
        return Mock(spec=Session)

    def test_cross_tenant_data_leak_prevented(self, db_session):
        """Test that data cannot leak between tenants"""
        org1_id = str(uuid4())
        org2_id = str(uuid4())

        # Create validators for different organizations
        validator1 = TenantValidator(org1_id, "user1")
        validator2 = TenantValidator(org2_id, "user2")

        # Create sessions for each organization
        session1 = TenantAwareSession(db_session, validator1)
        session2 = TenantAwareSession(db_session, validator2)

        # Attempt to access data from wrong organization
        instance = Mock()
        instance.organization_id = org1_id

        # Session 1 should work
        session1.add(instance)  # Should succeed

        # Session 2 should fail
        with pytest.raises(TenantIsolationError):
            session2.delete(instance)  # Should fail

    def test_audit_report_generation(self, db_session):
        """Test complete audit report generation"""
        auditor = TenantSecurityAuditor(db_session)

        # Mock Base.__subclasses__ for testing
        original_subclasses = Base.__subclasses__
        Base.__subclasses__ = Mock(return_value=[MockModel])

        try:
            report = auditor.audit_all_models()

            assert "total_models" in report
            assert "compliant_models" in report
            assert "violations" in report
            assert "summary" in report

            assert report["total_models"] >= 1

        finally:
            Base.__subclasses__ = original_subclasses


if __name__ == "__main__":
    pytest.main([__file__, "-v"])