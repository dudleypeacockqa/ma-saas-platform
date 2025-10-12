"""
Sprint 11 Verification Test Suite
Test global operations: market intelligence, global ops, deal matching, and regulatory automation
"""

import sys
import os
from datetime import datetime
from decimal import Decimal

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))


def test_global_ops_imports():
    """Test that all global ops modules can be imported"""
    try:
        from app.global_ops import (
            get_market_intelligence_engine, get_global_operations_hub,
            get_deal_matching_engine, get_regulatory_automation_engine
        )
        print("PASS - Global operations modules imported successfully")
        return True
    except Exception as e:
        print(f"FAIL - Import failed: {e}")
        return False


def test_service_initialization():
    """Test that all global ops services can be initialized"""
    try:
        from app.global_ops import (
            get_market_intelligence_engine, get_global_operations_hub,
            get_deal_matching_engine, get_regulatory_automation_engine
        )

        # Initialize all services
        market_intel = get_market_intelligence_engine()
        global_ops = get_global_operations_hub()
        deal_matching = get_deal_matching_engine()
        regulatory = get_regulatory_automation_engine()

        print("PASS - All global operations services initialized successfully")
        return True
    except Exception as e:
        print(f"FAIL - Service initialization failed: {e}")
        return False


def test_market_intelligence():
    """Test market intelligence functionality"""
    try:
        from app.global_ops import (
            get_market_intelligence_engine, MarketSector, GeographicRegion
        )

        engine = get_market_intelligence_engine()

        # Test competitive landscape
        landscape = engine.get_competitive_landscape(
            MarketSector.TECHNOLOGY,
            GeographicRegion.NORTH_AMERICA
        )

        if hasattr(landscape, 'market_leaders') and hasattr(landscape, 'market_concentration'):
            print("PASS - Market intelligence competitive landscape works")
        else:
            print("FAIL - Market intelligence missing expected attributes")
            return False

        # Test market insights
        insights = engine.get_market_insights(
            MarketSector.TECHNOLOGY,
            GeographicRegion.NORTH_AMERICA
        )

        if isinstance(insights, dict) and "market_summary" in insights:
            print("PASS - Market intelligence insights work")
        else:
            print("FAIL - Market intelligence insights missing expected data")
            return False

        return True
    except Exception as e:
        print(f"FAIL - Market intelligence test failed: {e}")
        return False


def test_global_operations():
    """Test global operations functionality"""
    try:
        from app.global_ops import (
            get_global_operations_hub, Currency, Jurisdiction
        )

        hub = get_global_operations_hub()

        # Test currency conversion
        conversion = hub.currency_manager.convert_currency(
            Decimal('1000.00'),
            Currency.USD,
            Currency.EUR
        )

        if hasattr(conversion, 'converted_amount') and hasattr(conversion, 'exchange_rate'):
            print("PASS - Global operations currency conversion works")
        else:
            print("FAIL - Global operations currency conversion missing attributes")
            return False

        # Test tax implications
        tax_implications = hub.regulatory_manager.get_tax_implications(
            Decimal('100000000'),  # $100M deal
            Jurisdiction.UNITED_STATES,
            Jurisdiction.UNITED_KINGDOM,
            "asset_acquisition"
        )

        if isinstance(tax_implications, dict) and "tax_breakdown" in tax_implications:
            print("PASS - Global operations tax implications work")
        else:
            print("FAIL - Global operations tax implications missing expected data")
            return False

        return True
    except Exception as e:
        print(f"FAIL - Global operations test failed: {e}")
        return False


def test_deal_matching():
    """Test deal matching functionality"""
    try:
        from app.global_ops import get_deal_matching_engine
        from app.global_ops.deal_matching import CompanyProfile, DealType

        engine = get_deal_matching_engine()

        # Create test company profiles
        buyer_profile = CompanyProfile(
            company_id="buyer_test_123",
            name="Test Buyer Corp",
            industry_sector="technology",
            geographic_regions=["north_america"],
            revenue=1000000000.0,
            employees=5000,
            valuation=5000000000.0,
            growth_rate=15.0,
            technology_stack=["python", "react", "aws"],
            market_position="market_leader",
            financial_health_score=0.8,
            strategic_priorities=["market_expansion", "technology_acquisition"],
            available_for=[DealType.ACQUISITION],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        seller_profile = CompanyProfile(
            company_id="seller_test_456",
            name="Test Target Inc",
            industry_sector="technology",
            geographic_regions=["europe"],
            revenue=200000000.0,
            employees=1000,
            valuation=800000000.0,
            growth_rate=25.0,
            technology_stack=["python", "vue", "azure"],
            market_position="niche_player",
            financial_health_score=0.7,
            strategic_priorities=["growth", "scale"],
            available_for=[DealType.ACQUISITION],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Add profiles
        engine.add_company_profile(buyer_profile)
        engine.add_company_profile(seller_profile)

        # Test finding matches
        matches = engine.find_matches(
            buyer_id="buyer_test_123",
            deal_type=DealType.ACQUISITION,
            min_score_threshold=0.5,
            max_results=5
        )

        if isinstance(matches, list):
            print("PASS - Deal matching find matches works")
        else:
            print("FAIL - Deal matching find matches failed")
            return False

        # Test strategic fit analysis
        if len(matches) > 0 or True:  # Test even if no matches found
            fit_analysis = engine.analyze_strategic_fit(
                "buyer_test_123",
                "seller_test_456"
            )

            if hasattr(fit_analysis, 'strategic_alignment_score') and hasattr(fit_analysis, 'overall_recommendation'):
                print("PASS - Deal matching strategic fit analysis works")
            else:
                print("FAIL - Deal matching strategic fit analysis missing attributes")
                return False

        return True
    except Exception as e:
        print(f"FAIL - Deal matching test failed: {e}")
        return False


def test_regulatory_automation():
    """Test regulatory automation functionality"""
    try:
        from app.global_ops import (
            get_regulatory_automation_engine, RegulatoryFramework
        )

        engine = get_regulatory_automation_engine()

        # Test regulatory requirements analysis
        deal_characteristics = {
            "deal_value": 500000000,  # $500M
            "industry_sectors": ["technology"],
            "jurisdictions": ["US", "EU"],
            "foreign_involvement": True
        }

        analysis = engine.analyze_regulatory_requirements(
            "test_deal_789",
            deal_characteristics
        )

        if isinstance(analysis, dict) and "applicable_rules" in analysis:
            print("PASS - Regulatory automation requirements analysis works")
        else:
            print("FAIL - Regulatory automation requirements analysis missing expected data")
            return False

        # Test compliance assessment
        assessment = engine.compliance_tracker.create_compliance_assessment(
            "test_deal_789",
            RegulatoryFramework.ANTITRUST,
            "US",
            deal_characteristics
        )

        if hasattr(assessment, 'compliance_status') and hasattr(assessment, 'risk_level'):
            print("PASS - Regulatory automation compliance assessment works")
        else:
            print("FAIL - Regulatory automation compliance assessment missing attributes")
            return False

        # Test risk assessment
        risk_assessment = engine.risk_monitor.perform_risk_assessment(
            "test_deal_789",
            [RegulatoryFramework.ANTITRUST, RegulatoryFramework.FOREIGN_INVESTMENT],
            deal_characteristics
        )

        if hasattr(risk_assessment, 'overall_risk_score') and hasattr(risk_assessment, 'critical_risks'):
            print("PASS - Regulatory automation risk assessment works")
        else:
            print("FAIL - Regulatory automation risk assessment missing attributes")
            return False

        return True
    except Exception as e:
        print(f"FAIL - Regulatory automation test failed: {e}")
        return False


def test_api_endpoints():
    """Test that API endpoints can be imported"""
    try:
        from app.api.v1 import global_ops
        if hasattr(global_ops, 'router'):
            print("PASS - Global operations API endpoints available")
            return True
        else:
            print("FAIL - Global operations API router not found")
            return False
    except Exception as e:
        print(f"FAIL - API endpoints test failed: {e}")
        return False


def test_enums_and_types():
    """Test that all enums and types are properly defined"""
    try:
        from app.global_ops import (
            MarketSector, GeographicRegion, Currency, Jurisdiction,
            DealType, MatchingCriteria, RegulatoryFramework
        )

        # Test that enums have expected values
        assert MarketSector.TECHNOLOGY
        assert GeographicRegion.NORTH_AMERICA
        assert Currency.USD
        assert Jurisdiction.UNITED_STATES
        assert DealType.ACQUISITION
        assert MatchingCriteria.STRATEGIC_FIT
        assert RegulatoryFramework.ANTITRUST

        print("PASS - All enums and types properly defined")
        return True
    except Exception as e:
        print(f"FAIL - Enums and types test failed: {e}")
        return False


def main():
    """Run all Sprint 11 verification tests"""
    print("Sprint 11 Global Operations - Verification Tests")
    print("=" * 55)

    tests = [
        ("Import Test", test_global_ops_imports),
        ("Service Initialization", test_service_initialization),
        ("Market Intelligence", test_market_intelligence),
        ("Global Operations", test_global_operations),
        ("Deal Matching", test_deal_matching),
        ("Regulatory Automation", test_regulatory_automation),
        ("API Endpoints", test_api_endpoints),
        ("Enums and Types", test_enums_and_types)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1

    print(f"\nSummary:")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("\nSprint 11 Global Operations: ALL TESTS PASSED!")
        print("Advanced market intelligence and global operations are fully operational")
        return True
    else:
        print(f"\n{total - passed} tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)