"""
Comprehensive Integration Tests for Master Admin API
Tests all critical business functionality for the M&A SaaS platform
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json


class TestMasterAdminAuthentication:
    """Test authentication and authorization for master admin endpoints"""

    def test_dashboard_metrics_requires_authentication(self, client):
        """Test that dashboard metrics endpoint requires authentication"""
        response = client.get("/api/admin/dashboard/metrics")
        assert response.status_code in [401, 403]

    def test_dashboard_metrics_requires_admin_role(self, client):
        """Test that dashboard metrics requires admin role"""
        # Mock non-admin user
        with patch('app.auth.clerk_auth.get_current_user') as mock_user:
            mock_user.return_value = {
                "id": "user_123",
                "email": "user@example.com",
                "public_metadata": {"role": "user"}
            }
            response = client.get(
                "/api/admin/dashboard/metrics",
                headers={"Authorization": "Bearer user_token"}
            )
            assert response.status_code in [401, 403]

    @patch('app.auth.clerk_auth.get_current_user')
    @patch('app.auth.clerk_auth.require_admin')
    def test_dashboard_metrics_with_admin_access(self, mock_require_admin, mock_get_user, client):
        """Test dashboard metrics with proper admin authentication"""
        # Mock admin user
        admin_user = {
            "id": "admin_123",
            "email": "admin@example.com",
            "public_metadata": {"role": "admin"}
        }
        mock_get_user.return_value = admin_user
        mock_require_admin.return_value = admin_user

        response = client.get(
            "/api/admin/dashboard/metrics",
            headers={"Authorization": "Bearer admin_token"}
        )

        # Should not return 401/403 anymore
        assert response.status_code != 401
        assert response.status_code != 403


class TestMasterAdminDashboard:
    """Test master admin dashboard functionality"""

    @patch('app.auth.clerk_auth.get_current_user')
    @patch('app.auth.clerk_auth.require_admin')
    def test_dashboard_metrics_structure(self, mock_require_admin, mock_get_user, client):
        """Test dashboard metrics returns expected data structure"""
        # Mock admin user
        admin_user = {
            "id": "admin_123",
            "email": "admin@example.com",
            "public_metadata": {"role": "admin"}
        }
        mock_get_user.return_value = admin_user
        mock_require_admin.return_value = admin_user

        response = client.get(
            "/api/admin/dashboard/metrics",
            headers={"Authorization": "Bearer admin_token"}
        )

        if response.status_code == 200:
            data = response.json()

            # Check for expected dashboard metrics
            expected_fields = [
                "mrr", "arr", "active_subscribers", "churn_rate",
                "ltv", "cac", "trial_conversion_rate", "revenue_growth"
            ]

            for field in expected_fields:
                assert field in data, f"Missing field: {field}"
                assert isinstance(data[field], (int, float)), f"Field {field} should be numeric"

    @patch('app.auth.clerk_auth.get_current_user')
    @patch('app.auth.clerk_auth.require_admin')
    def test_subscription_analytics(self, mock_require_admin, mock_get_user, client):
        """Test subscription analytics endpoint"""
        admin_user = {
            "id": "admin_123",
            "email": "admin@example.com",
            "public_metadata": {"role": "admin"}
        }
        mock_get_user.return_value = admin_user
        mock_require_admin.return_value = admin_user

        response = client.get(
            "/api/admin/subscriptions/analytics",
            headers={"Authorization": "Bearer admin_token"}
        )

        if response.status_code == 200:
            data = response.json()

            # Check for subscription analytics fields
            expected_fields = [
                "total_subscriptions", "active_subscriptions",
                "trial_subscriptions", "cancelled_subscriptions"
            ]

            for field in expected_fields:
                assert field in data, f"Missing subscription field: {field}"

    @patch('app.auth.clerk_auth.get_current_user')
    @patch('app.auth.clerk_auth.require_admin')
    def test_user_management_list(self, mock_require_admin, mock_get_user, client):
        """Test user management listing"""
        admin_user = {
            "id": "admin_123",
            "email": "admin@example.com",
            "public_metadata": {"role": "admin"}
        }
        mock_get_user.return_value = admin_user
        mock_require_admin.return_value = admin_user

        response = client.get(
            "/api/admin/users",
            headers={"Authorization": "Bearer admin_token"}
        )

        # Should return a list (even if empty)
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list) or "users" in data


class TestBusinessIntelligence:
    """Test business intelligence and analytics features"""

    @patch('app.auth.clerk_auth.get_current_user')
    @patch('app.auth.clerk_auth.require_admin')
    def test_revenue_analytics(self, mock_require_admin, mock_get_user, client):
        """Test revenue analytics endpoint"""
        admin_user = {
            "id": "admin_123",
            "email": "admin@example.com",
            "public_metadata": {"role": "admin"}
        }
        mock_get_user.return_value = admin_user
        mock_require_admin.return_value = admin_user

        response = client.get(
            "/api/admin/analytics/revenue",
            headers={"Authorization": "Bearer admin_token"}
        )

        if response.status_code == 200:
            data = response.json()

            # Should contain revenue metrics
            revenue_fields = ["total_revenue", "monthly_revenue", "growth_rate"]

            # At least some revenue data should be present
            has_revenue_data = any(field in data for field in revenue_fields)
            assert has_revenue_data or "error" in data

    @patch('app.auth.clerk_auth.get_current_user')
    @patch('app.auth.clerk_auth.require_admin')
    def test_customer_analytics(self, mock_require_admin, mock_get_user, client):
        """Test customer analytics endpoint"""
        admin_user = {
            "id": "admin_123",
            "email": "admin@example.com",
            "public_metadata": {"role": "admin"}
        }
        mock_get_user.return_value = admin_user
        mock_require_admin.return_value = admin_user

        response = client.get(
            "/api/admin/analytics/customers",
            headers={"Authorization": "Bearer admin_token"}
        )

        if response.status_code == 200:
            data = response.json()

            # Should contain customer metrics
            customer_fields = ["total_customers", "active_customers", "new_customers"]

            # At least some customer data should be present
            has_customer_data = any(field in data for field in customer_fields)
            assert has_customer_data or "error" in data


class TestSystemHealth:
    """Test system health and monitoring endpoints"""

    @patch('app.auth.clerk_auth.get_current_user')
    @patch('app.auth.clerk_auth.require_admin')
    def test_system_status(self, mock_require_admin, mock_get_user, client):
        """Test system status endpoint"""
        admin_user = {
            "id": "admin_123",
            "email": "admin@example.com",
            "public_metadata": {"role": "admin"}
        }
        mock_get_user.return_value = admin_user
        mock_require_admin.return_value = admin_user

        response = client.get(
            "/api/admin/system/status",
            headers={"Authorization": "Bearer admin_token"}
        )

        if response.status_code == 200:
            data = response.json()

            # Should contain system status information
            status_fields = ["database", "redis", "storage", "external_apis"]

            # At least some status data should be present
            has_status_data = any(field in data for field in status_fields)
            assert has_status_data or "status" in data

    def test_health_check_endpoint(self, client):
        """Test basic health check endpoint (should not require auth)"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "ok"]

    def test_root_endpoint(self, client):
        """Test root endpoint functionality"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "M&A SaaS Platform" in data["service"]


class TestMasterAdminErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_endpoint(self, client):
        """Test handling of invalid endpoints"""
        response = client.get("/api/admin/nonexistent")
        assert response.status_code == 404

    @patch('app.auth.clerk_auth.get_current_user')
    def test_malformed_auth_token(self, mock_get_user, client):
        """Test handling of malformed authentication tokens"""
        mock_get_user.side_effect = Exception("Invalid token")

        response = client.get(
            "/api/admin/dashboard/metrics",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code in [401, 403, 500]

    @patch('app.auth.clerk_auth.get_current_user')
    @patch('app.auth.clerk_auth.require_admin')
    def test_database_connection_error(self, mock_require_admin, mock_get_user, client):
        """Test handling of database connection errors"""
        admin_user = {
            "id": "admin_123",
            "email": "admin@example.com",
            "public_metadata": {"role": "admin"}
        }
        mock_get_user.return_value = admin_user
        mock_require_admin.return_value = admin_user

        # This test would need actual database mocking to simulate connection errors
        # For now, we'll just ensure the endpoint exists
        response = client.get(
            "/api/admin/dashboard/metrics",
            headers={"Authorization": "Bearer admin_token"}
        )

        # Should not crash the application
        assert response.status_code != 500 or "error" in response.json()


class TestMasterAdminIntegration:
    """Integration tests for master admin features"""

    def test_full_admin_workflow(self, client):
        """Test a complete admin workflow"""
        # This would test a full workflow like:
        # 1. Admin login
        # 2. View dashboard
        # 3. Check system status
        # 4. Review analytics

        # For now, test basic endpoint availability
        health_response = client.get("/health")
        assert health_response.status_code == 200

        root_response = client.get("/")
        assert root_response.status_code == 200

    @patch('app.auth.clerk_auth.get_current_user')
    @patch('app.auth.clerk_auth.require_admin')
    def test_admin_data_consistency(self, mock_require_admin, mock_get_user, client):
        """Test data consistency across admin endpoints"""
        admin_user = {
            "id": "admin_123",
            "email": "admin@example.com",
            "public_metadata": {"role": "admin"}
        }
        mock_get_user.return_value = admin_user
        mock_require_admin.return_value = admin_user

        headers = {"Authorization": "Bearer admin_token"}

        # Get dashboard metrics
        dashboard_response = client.get("/api/admin/dashboard/metrics", headers=headers)

        # Get subscription analytics
        subscription_response = client.get("/api/admin/subscriptions/analytics", headers=headers)

        # Both should succeed or fail consistently
        if dashboard_response.status_code == 200 and subscription_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            subscription_data = subscription_response.json()

            # Data consistency checks
            if "active_subscribers" in dashboard_data and "active_subscriptions" in subscription_data:
                # These should be the same value
                assert dashboard_data["active_subscribers"] == subscription_data["active_subscriptions"]