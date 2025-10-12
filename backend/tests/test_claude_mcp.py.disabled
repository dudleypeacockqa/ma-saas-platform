"""Tests for Claude MCP Integration Service"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from app.services.claude_mcp import (
    ClaudeMCPService,
    DealAnalysis,
    PartnershipRecommendation
)


@pytest.fixture
def claude_service():
    """Create a Claude MCP service instance for testing"""
    return ClaudeMCPService()


@pytest.fixture
def sample_deal_data():
    """Sample deal data for testing"""
    return {
        "id": "deal-001",
        "name": "TechCorp Acquisition",
        "type": "acquisition",
        "value": 50000000,
        "target": {
            "name": "TechCorp",
            "revenue": 10000000,
            "ebitda": 2000000,
            "employees": 100
        },
        "acquirer": {
            "name": "MegaCorp",
            "revenue": 500000000,
            "ebitda": 100000000
        },
        "terms": {
            "consideration": "cash",
            "earnout": 10000000,
            "escrow": 5000000
        }
    }


@pytest.fixture
def sample_organization_profile():
    """Sample organization profile for partnership identification"""
    return {
        "name": "GrowthCo",
        "industry": "Technology",
        "revenue": 25000000,
        "markets": ["US", "UK", "EU"],
        "capabilities": ["SaaS", "AI/ML", "Cloud"],
        "objectives": ["market_expansion", "technology_acquisition"]
    }


class TestClaudeMCPService:
    """Test suite for Claude MCP Service"""

    @pytest.mark.asyncio
    async def test_deal_analysis(self, claude_service, sample_deal_data):
        """Test deal analysis functionality"""
        with patch.object(claude_service.client.messages, 'create') as mock_create:
            # Mock Claude API response
            mock_response = Mock()
            mock_response.content = [Mock(text='''{
                "confidence_score": 0.85,
                "strategic_value": 0.90,
                "risk_assessment": {
                    "financial_risk": 0.3,
                    "integration_risk": 0.4,
                    "market_risk": 0.2,
                    "regulatory_risk": 0.1,
                    "cultural_risk": 0.35
                },
                "recommendations": [
                    "Strong strategic fit with existing portfolio",
                    "Consider phased integration approach",
                    "Negotiate better earnout terms"
                ],
                "key_insights": [
                    "High revenue synergy potential",
                    "Technology stack highly compatible"
                ],
                "red_flags": [
                    "Customer concentration risk",
                    "Key employee retention concerns"
                ],
                "synergies": [
                    "Cross-selling opportunities",
                    "Operational efficiency gains"
                ],
                "valuation_notes": "Valuation appears fair given market comparables"
            }''')]
            mock_create.return_value = mock_response

            # Perform analysis
            analysis = await claude_service.analyze_deal(sample_deal_data)

            # Assertions
            assert isinstance(analysis, DealAnalysis)
            assert analysis.deal_id == "deal-001"
            assert analysis.confidence_score == 0.85
            assert analysis.strategic_value == 0.90
            assert len(analysis.recommendations) == 3
            assert len(analysis.key_insights) == 2
            assert len(analysis.red_flags) == 2
            assert "financial_risk" in analysis.risk_assessment

    @pytest.mark.asyncio
    async def test_deal_analysis_caching(self, claude_service, sample_deal_data):
        """Test that deal analysis results are cached"""
        with patch.object(claude_service.client.messages, 'create') as mock_create:
            mock_response = Mock()
            mock_response.content = [Mock(text='''{
                "confidence_score": 0.85,
                "strategic_value": 0.90,
                "risk_assessment": {},
                "recommendations": [],
                "key_insights": [],
                "red_flags": [],
                "synergies": [],
                "valuation_notes": ""
            }''')]
            mock_create.return_value = mock_response

            # First call
            analysis1 = await claude_service.analyze_deal(sample_deal_data)
            # Second call (should use cache)
            analysis2 = await claude_service.analyze_deal(sample_deal_data)

            # API should only be called once due to caching
            assert mock_create.call_count == 1
            assert analysis1.confidence_score == analysis2.confidence_score

    @pytest.mark.asyncio
    async def test_partnership_identification(self, claude_service, sample_organization_profile):
        """Test partnership identification functionality"""
        with patch.object(claude_service.client.messages, 'create') as mock_create:
            mock_response = Mock()
            mock_response.content = [Mock(text='''{
                "recommendations": [
                    {
                        "partner_id": "partner-001",
                        "compatibility_score": 0.92,
                        "strategic_fit": 0.88,
                        "influence_score": 0.75,
                        "synergy_areas": ["Technology", "Market Access"],
                        "potential_value": "$10-15M annual revenue",
                        "risk_factors": ["Geographic overlap"],
                        "recommended_actions": ["Initial meeting", "NDA execution"]
                    },
                    {
                        "partner_id": "partner-002",
                        "compatibility_score": 0.85,
                        "strategic_fit": 0.82,
                        "influence_score": 0.70,
                        "synergy_areas": ["Product Portfolio"],
                        "potential_value": "$5-8M annual revenue",
                        "risk_factors": ["Cultural differences"],
                        "recommended_actions": ["Due diligence"]
                    }
                ]
            }''')]
            mock_create.return_value = mock_response

            # Identify partnerships
            recommendations = await claude_service.identify_partnerships(sample_organization_profile)

            # Assertions
            assert len(recommendations) == 2
            assert isinstance(recommendations[0], PartnershipRecommendation)
            assert recommendations[0].partner_id == "partner-001"
            assert recommendations[0].compatibility_score == 0.92
            assert recommendations[0].strategic_fit == 0.88
            assert len(recommendations[0].synergy_areas) == 2
            # Check sorting by compatibility score
            assert recommendations[0].compatibility_score >= recommendations[1].compatibility_score

    @pytest.mark.asyncio
    async def test_strategic_insights_generation(self, claude_service):
        """Test strategic insights generation"""
        ecosystem_data = {
            "market_size": 1000000000,
            "growth_rate": 0.15,
            "competitors": 50,
            "trends": ["AI adoption", "Market consolidation"]
        }

        with patch.object(claude_service.client.messages, 'create') as mock_create:
            mock_response = Mock()
            mock_response.content = [Mock(text='''{
                "market_trends": [
                    {
                        "trend": "AI-driven automation",
                        "impact": "high",
                        "opportunity": "First-mover advantage",
                        "timeframe": "6-12 months"
                    }
                ],
                "opportunities": [
                    {
                        "description": "Market consolidation play",
                        "potential_value": "$50M",
                        "priority": "high",
                        "action_items": ["Identify targets", "Secure funding"]
                    }
                ],
                "threats": [],
                "recommendations": []
            }''')]
            mock_create.return_value = mock_response

            # Generate insights
            insights = await claude_service.generate_strategic_insights(ecosystem_data)

            # Assertions
            assert "market_trends" in insights
            assert len(insights["market_trends"]) == 1
            assert insights["market_trends"][0]["impact"] == "high"
            assert "opportunities" in insights
            assert len(insights["opportunities"]) == 1

    @pytest.mark.asyncio
    async def test_deal_optimization(self, claude_service, sample_deal_data):
        """Test deal structure optimization"""
        optimization_goals = ["tax_efficiency", "risk_mitigation"]

        with patch.object(claude_service.client.messages, 'create') as mock_create:
            mock_response = Mock()
            mock_response.content = [Mock(text='''{
                "optimized_structure": {
                    "deal_type": "asset",
                    "consideration": "mixed",
                    "financing": "senior debt + equity"
                },
                "improvements": [
                    {
                        "area": "Tax Structure",
                        "original": "Stock purchase",
                        "optimized": "Asset purchase with 338(h)(10) election",
                        "benefit": "$2M tax savings"
                    }
                ],
                "estimated_savings": 2000000,
                "risk_reduction": 25,
                "implementation_steps": []
            }''')]
            mock_create.return_value = mock_response

            # Optimize deal
            optimization = await claude_service.optimize_deal_structure(
                sample_deal_data,
                optimization_goals
            )

            # Assertions
            assert "optimized_structure" in optimization
            assert optimization["optimized_structure"]["deal_type"] == "asset"
            assert optimization["estimated_savings"] == 2000000
            assert optimization["risk_reduction"] == 25

    @pytest.mark.asyncio
    async def test_integration_assessment(self, claude_service):
        """Test post-merger integration assessment"""
        acquirer = {"name": "AcquirerCo", "employees": 1000}
        target = {"name": "TargetCo", "employees": 100}

        with patch.object(claude_service.client.messages, 'create') as mock_create:
            mock_response = Mock()
            mock_response.content = [Mock(text='''{
                "readiness_score": 0.75,
                "integration_complexity": "medium",
                "estimated_timeline": "12 months",
                "key_challenges": [
                    {
                        "challenge": "System integration",
                        "severity": "high",
                        "mitigation": "Phased approach",
                        "owner": "CTO"
                    }
                ],
                "success_factors": [],
                "risk_areas": [],
                "action_items": []
            }''')]
            mock_create.return_value = mock_response

            # Assess integration
            assessment = await claude_service.assess_integration_readiness(acquirer, target)

            # Assertions
            assert assessment["readiness_score"] == 0.75
            assert assessment["integration_complexity"] == "medium"
            assert assessment["estimated_timeline"] == "12 months"
            assert len(assessment["key_challenges"]) == 1

    @pytest.mark.asyncio
    async def test_batch_analyze_deals(self, claude_service):
        """Test batch deal analysis"""
        deals = [
            {"id": "deal-001", "value": 10000000},
            {"id": "deal-002", "value": 20000000},
            {"id": "deal-003", "value": 15000000}
        ]

        with patch.object(claude_service, 'analyze_deal') as mock_analyze:
            # Mock individual deal analyses
            mock_analyze.side_effect = [
                DealAnalysis(
                    deal_id=f"deal-00{i+1}",
                    confidence_score=0.8 + i*0.05,
                    strategic_value=0.85,
                    risk_assessment={},
                    recommendations=[],
                    key_insights=[],
                    red_flags=[],
                    synergies=[],
                    valuation_notes="",
                    timestamp=datetime.now()
                )
                for i in range(3)
            ]

            # Perform batch analysis
            results = await claude_service.batch_analyze_deals(deals, batch_size=2)

            # Assertions
            assert len(results) == 3
            assert all(isinstance(r, DealAnalysis) for r in results)
            assert results[0].deal_id == "deal-001"
            assert results[2].confidence_score == 0.90

    @pytest.mark.asyncio
    async def test_error_handling(self, claude_service, sample_deal_data):
        """Test error handling in Claude MCP service"""
        with patch.object(claude_service.client.messages, 'create') as mock_create:
            # Simulate API error
            mock_create.side_effect = Exception("API Error")

            # Should raise exception
            with pytest.raises(Exception) as exc_info:
                await claude_service.analyze_deal(sample_deal_data)

            assert "API Error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fallback_parsing(self, claude_service, sample_deal_data):
        """Test fallback parsing when response is not valid JSON"""
        with patch.object(claude_service.client.messages, 'create') as mock_create:
            # Non-JSON response
            mock_response = Mock()
            mock_response.content = [Mock(text="This is not JSON")]
            mock_create.return_value = mock_response

            # Should still return a DealAnalysis with defaults
            analysis = await claude_service.analyze_deal(sample_deal_data)

            assert isinstance(analysis, DealAnalysis)
            assert analysis.deal_id == "deal-001"
            assert analysis.confidence_score == 0.5  # Default fallback
            assert "parsing_error" in analysis.risk_assessment

    def test_cache_clearing(self, claude_service):
        """Test cache clearing functionality"""
        # Add something to cache
        claude_service._cache["test_key"] = ("test_value", datetime.now())
        assert len(claude_service._cache) == 1

        # Clear cache
        claude_service.clear_cache()
        assert len(claude_service._cache) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])