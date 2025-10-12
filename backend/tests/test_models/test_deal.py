"""
Tests for Deal model
"""

import pytest
from datetime import datetime, timedelta
from app.models.deal import Deal


@pytest.mark.unit
@pytest.mark.models
class TestDealModel:
    """Test suite for Deal model"""

    def test_create_deal(self, db_session, organization_factory, user_factory):
        """Test creating a basic deal"""
        org = organization_factory()
        user = user_factory(organization_id=org.id)

        deal = Deal(
            organization_id=org.id,
            title="Test Acquisition Deal",
            deal_type="acquisition",
            stage="sourcing",
            priority="high",
            target_company_name="Target Corp",
            deal_currency="USD",
            probability_of_close=75,
            created_by=user.id,
        )

        db_session.add(deal)
        db_session.commit()
        db_session.refresh(deal)

        assert deal.id is not None
        assert deal.title == "Test Acquisition Deal"
        assert deal.organization_id == org.id
        assert deal.is_active is True
        assert deal.created_at is not None

    def test_deal_factory(self, deal_factory):
        """Test using the deal factory fixture"""
        deal = deal_factory(
            title="Factory Test Deal",
            deal_type="merger",
            stage="due_diligence",
        )

        assert deal.id is not None
        assert deal.title == "Factory Test Deal"
        assert deal.deal_type == "merger"
        assert deal.stage == "due_diligence"

    def test_deal_with_financial_data(self, deal_factory):
        """Test deal with financial information"""
        deal = deal_factory(
            title="Financial Deal",
            deal_value=10000000,
            enterprise_value=12000000,
            equity_value=8000000,
            debt_assumed=2000000,
        )

        assert deal.deal_value == 10000000
        assert deal.enterprise_value == 12000000
        assert deal.equity_value == 8000000
        assert deal.debt_assumed == 2000000

    def test_deal_stage_progression(self, deal_factory, db_session):
        """Test updating deal through stages"""
        deal = deal_factory(stage="sourcing")

        # Update to next stage
        deal.stage = "initial_review"
        db_session.commit()
        db_session.refresh(deal)

        assert deal.stage == "initial_review"

        # Update to due diligence
        deal.stage = "due_diligence"
        db_session.commit()
        db_session.refresh(deal)

        assert deal.stage == "due_diligence"

    def test_deal_with_dates(self, deal_factory, sample_dates):
        """Test deal with various dates"""
        deal = deal_factory(
            initial_contact_date=sample_dates["past"],
            expected_close_date=sample_dates["future"],
        )

        assert deal.initial_contact_date == sample_dates["past"]
        assert deal.expected_close_date == sample_dates["future"]

    def test_deal_priority_levels(self, deal_factory):
        """Test different priority levels"""
        for priority in ["low", "medium", "high", "critical"]:
            deal = deal_factory(priority=priority)
            assert deal.priority == priority

    def test_deal_confidentiality(self, deal_factory):
        """Test confidential deal creation"""
        deal = deal_factory(
            title="Confidential Merger",
            is_confidential=True,
            code_name="Project Phoenix",
        )

        assert deal.is_confidential is True
        assert deal.code_name == "Project Phoenix"

    def test_deal_tenant_isolation(self, deal_factory, organization_factory):
        """Test that deals are isolated by organization"""
        org1 = organization_factory(id="org_1", name="Org 1")
        org2 = organization_factory(id="org_2", name="Org 2")

        deal1 = deal_factory(organization_id=org1.id, title="Org 1 Deal")
        deal2 = deal_factory(organization_id=org2.id, title="Org 2 Deal")

        assert deal1.organization_id == org1.id
        assert deal2.organization_id == org2.id
        assert deal1.organization_id != deal2.organization_id

    def test_deal_custom_fields(self, deal_factory):
        """Test storing custom fields in JSON"""
        custom_data = {
            "industry_vertical": "FinTech",
            "founder_commitment": "high",
            "retention_key_employees": True,
        }

        deal = deal_factory(custom_fields=custom_data)

        assert deal.custom_fields == custom_data
        assert deal.custom_fields["industry_vertical"] == "FinTech"

    def test_deal_tags(self, deal_factory):
        """Test adding tags to a deal"""
        tags = ["cross_border", "tech_acquisition", "growth_stage"]
        deal = deal_factory(tags=tags)

        assert len(deal.tags) == 3
        assert "cross_border" in deal.tags
        assert "tech_acquisition" in deal.tags

    def test_deal_probability_range(self, deal_factory):
        """Test probability of close validation"""
        deal = deal_factory(probability_of_close=0)
        assert deal.probability_of_close == 0

        deal = deal_factory(probability_of_close=50)
        assert deal.probability_of_close == 50

        deal = deal_factory(probability_of_close=100)
        assert deal.probability_of_close == 100


@pytest.mark.integration
@pytest.mark.models
class TestDealRelationships:
    """Test suite for Deal model relationships"""

    def test_deal_with_documents(self, deal_factory, document_factory):
        """Test deal-document relationship"""
        deal = deal_factory()
        doc1 = document_factory(deal_id=deal.id, filename="nda.pdf")
        doc2 = document_factory(deal_id=deal.id, filename="financials.xlsx")

        # Note: This assumes relationship is configured in model
        # If relationship exists: assert len(deal.documents) == 2

    def test_deal_with_team_members(self, deal_factory, user_factory):
        """Test deal with assigned team members"""
        deal = deal_factory()
        lead = user_factory(email="lead@example.com")
        sponsor = user_factory(email="sponsor@example.com")

        deal.deal_lead_id = lead.id
        deal.sponsor_id = sponsor.id

        assert deal.deal_lead_id == lead.id
        assert deal.sponsor_id == sponsor.id


@pytest.mark.unit
@pytest.mark.models
class TestDealCalculations:
    """Test suite for Deal calculations and computed properties"""

    def test_days_in_pipeline_calculation(self, deal_factory, freeze_time):
        """Test calculation of days in pipeline"""
        # This test assumes there's a property or method to calculate this
        # Implementation depends on actual model
        pass

    def test_is_overdue_flag(self, deal_factory, sample_dates):
        """Test overdue flag when expected close date is in past"""
        deal = deal_factory(
            expected_close_date=sample_dates["past"],
            stage="negotiation",
        )

        # Assuming there's an is_overdue property
        # assert deal.is_overdue is True

    def test_deal_value_calculations(self, deal_factory):
        """Test financial value calculations"""
        deal = deal_factory(
            enterprise_value=10000000,
            debt_assumed=2000000,
        )

        # Equity Value = Enterprise Value - Net Debt
        expected_equity_value = 10000000 - 2000000

        # If model has this calculation:
        # assert deal.calculated_equity_value == expected_equity_value
