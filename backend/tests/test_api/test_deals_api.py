"""
Integration tests for Deals API endpoints
"""

import pytest
from fastapi import status


@pytest.mark.integration
@pytest.mark.api
class TestDealsAPI:
    """Test suite for Deals API endpoints"""

    def test_create_deal(self, client, auth_headers, organization_factory, user_factory):
        """Test creating a new deal via API"""
        org = organization_factory()
        user = user_factory(organization_id=org.id)

        deal_data = {
            "title": "API Test Deal",
            "deal_type": "acquisition",
            "stage": "sourcing",
            "priority": "high",
            "target_company_name": "Target Corp",
            "target_industry": "Technology",
            "deal_currency": "USD",
            "probability_of_close": 70,
        }

        response = client.post(
            "/api/deals/",
            json=deal_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "API Test Deal"
        assert data["deal_type"] == "acquisition"
        assert data["stage"] == "sourcing"
        assert "id" in data

    def test_get_deals_list(self, client, auth_headers, deal_factory):
        """Test retrieving list of deals"""
        # Create test deals
        deal_factory(title="Deal 1")
        deal_factory(title="Deal 2")
        deal_factory(title="Deal 3")

        response = client.get(
            "/api/deals/",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert len(data["data"]) >= 3

    def test_get_single_deal(self, client, auth_headers, deal_factory):
        """Test retrieving a single deal by ID"""
        deal = deal_factory(title="Single Deal Test")

        response = client.get(
            f"/api/deals/{deal.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == deal.id
        assert data["title"] == "Single Deal Test"

    def test_update_deal(self, client, auth_headers, deal_factory):
        """Test updating an existing deal"""
        deal = deal_factory(title="Original Title", probability_of_close=50)

        update_data = {
            "title": "Updated Title",
            "probability_of_close": 75,
            "stage": "due_diligence",
        }

        response = client.patch(
            f"/api/deals/{deal.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["probability_of_close"] == 75
        assert data["stage"] == "due_diligence"

    def test_delete_deal(self, client, auth_headers, deal_factory):
        """Test deleting a deal"""
        deal = deal_factory(title="Deal to Delete")

        response = client.delete(
            f"/api/deals/{deal.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        get_response = client.get(
            f"/api/deals/{deal.id}",
            headers=auth_headers,
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_filter_deals_by_stage(self, client, auth_headers, deal_factory):
        """Test filtering deals by stage"""
        deal_factory(title="Sourcing Deal", stage="sourcing")
        deal_factory(title="DD Deal", stage="due_diligence")
        deal_factory(title="Closing Deal", stage="closing")

        response = client.get(
            "/api/deals/",
            params={"stage": ["due_diligence", "closing"]},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        stages = [deal["stage"] for deal in data["data"]]
        assert "sourcing" not in stages
        assert "due_diligence" in stages or "closing" in stages

    def test_filter_deals_by_priority(self, client, auth_headers, deal_factory):
        """Test filtering deals by priority"""
        deal_factory(title="Critical Deal", priority="critical")
        deal_factory(title="High Deal", priority="high")
        deal_factory(title="Low Deal", priority="low")

        response = client.get(
            "/api/deals/",
            params={"priority": ["critical", "high"]},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        priorities = [deal["priority"] for deal in data["data"]]
        assert "low" not in priorities

    def test_search_deals(self, client, auth_headers, deal_factory):
        """Test searching deals by text"""
        deal_factory(title="Technology Acquisition", target_company_name="TechCorp")
        deal_factory(title="Healthcare Merger", target_company_name="HealthInc")

        response = client.get(
            "/api/deals/",
            params={"search": "Technology"},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) >= 1
        assert any("Technology" in deal["title"] for deal in data["data"])

    def test_pagination(self, client, auth_headers, deal_factory):
        """Test pagination of deals list"""
        # Create 15 deals
        for i in range(15):
            deal_factory(title=f"Deal {i+1}")

        # Get first page
        response = client.get(
            "/api/deals/",
            params={"page": 1, "per_page": 5},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "pagination" in data
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["per_page"] == 5
        assert len(data["data"]) == 5

        # Get second page
        response = client.get(
            "/api/deals/",
            params={"page": 2, "per_page": 5},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["pagination"]["page"] == 2
        assert len(data["data"]) == 5

    def test_update_deal_stage(self, client, auth_headers, deal_factory):
        """Test updating deal stage with stage change endpoint"""
        deal = deal_factory(stage="sourcing", probability_of_close=50)

        stage_update = {
            "stage": "due_diligence",
            "reason": "NDA signed, starting due diligence",
            "probability_of_close": 60,
        }

        response = client.post(
            f"/api/deals/{deal.id}/stage",
            json=stage_update,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["stage"] == "due_diligence"
        assert data["probability_of_close"] == 60

    def test_get_deal_statistics(self, client, auth_headers, deal_factory):
        """Test retrieving deal statistics"""
        # Create various deals
        deal_factory(stage="sourcing", priority="high", deal_value=1000000)
        deal_factory(stage="due_diligence", priority="critical", deal_value=2000000)
        deal_factory(stage="closing", priority="medium", deal_value=500000)

        response = client.get(
            "/api/deals/analytics/summary",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_deals" in data
        assert "by_stage" in data
        assert "by_priority" in data
        assert "total_value" in data

    def test_bulk_operation(self, client, auth_headers, deal_factory):
        """Test bulk operations on multiple deals"""
        deal1 = deal_factory(title="Deal 1", priority="low")
        deal2 = deal_factory(title="Deal 2", priority="low")
        deal3 = deal_factory(title="Deal 3", priority="low")

        bulk_data = {
            "operation": "update",
            "deal_ids": [deal1.id, deal2.id, deal3.id],
            "data": {"priority": "high"},
        }

        response = client.post(
            "/api/deals/bulk",
            json=bulk_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify updates
        for deal_id in [deal1.id, deal2.id, deal3.id]:
            get_response = client.get(
                f"/api/deals/{deal_id}",
                headers=auth_headers,
            )
            assert get_response.json()["priority"] == "high"


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.auth
class TestDealsAPIAuth:
    """Test authentication and authorization for Deals API"""

    def test_create_deal_without_auth(self, client):
        """Test that creating a deal without auth fails"""
        deal_data = {
            "title": "Unauthorized Deal",
            "deal_type": "acquisition",
            "stage": "sourcing",
            "target_company_name": "Target",
            "deal_currency": "USD",
            "probability_of_close": 50,
        }

        response = client.post("/api/deals/", json=deal_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_deals_without_auth(self, client):
        """Test that getting deals without auth fails"""
        response = client.get("/api/deals/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_tenant_isolation(self, client, auth_headers, deal_factory, organization_factory):
        """Test that users can only see deals from their organization"""
        # Create deals for two different organizations
        org1 = organization_factory(id="org_1")
        org2 = organization_factory(id="org_2")

        deal1 = deal_factory(organization_id=org1.id, title="Org 1 Deal")
        deal2 = deal_factory(organization_id=org2.id, title="Org 2 Deal")

        # User from org_1 tries to access deals
        headers_org1 = auth_headers.copy()
        headers_org1["X-Organization-ID"] = org1.id

        response = client.get("/api/deals/", headers=headers_org1)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should only see deals from org_1
        deal_ids = [deal["id"] for deal in data["data"]]
        assert deal1.id in deal_ids
        assert deal2.id not in deal_ids


@pytest.mark.integration
@pytest.mark.api
class TestDealsAPIValidation:
    """Test input validation for Deals API"""

    def test_create_deal_missing_required_fields(self, client, auth_headers):
        """Test that creating a deal without required fields fails"""
        incomplete_data = {
            "title": "Incomplete Deal",
            # Missing required fields
        }

        response = client.post(
            "/api/deals/",
            json=incomplete_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_deal_invalid_deal_type(self, client, auth_headers):
        """Test that invalid deal type is rejected"""
        invalid_data = {
            "title": "Invalid Deal",
            "deal_type": "invalid_type",  # Invalid
            "stage": "sourcing",
            "target_company_name": "Target",
            "deal_currency": "USD",
            "probability_of_close": 50,
        }

        response = client.post(
            "/api/deals/",
            json=invalid_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_deal_invalid_probability(self, client, auth_headers):
        """Test that probability outside 0-100 range is rejected"""
        invalid_data = {
            "title": "Invalid Probability",
            "deal_type": "acquisition",
            "stage": "sourcing",
            "target_company_name": "Target",
            "deal_currency": "USD",
            "probability_of_close": 150,  # Invalid
        }

        response = client.post(
            "/api/deals/",
            json=invalid_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
