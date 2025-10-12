"""
Sprint 15 Verification Test - Advanced Compliance & Risk Management Platform
Comprehensive test suite for all Sprint 15 compliance, risk, audit, and regulatory features
"""

import asyncio
from datetime import datetime, timedelta
import json
import sys
import os
from collections import defaultdict

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all Sprint 15 modules can be imported"""
    print("Testing Sprint 15 Module Imports...")

    try:
        # Test compliance engine import
        from app.compliance.compliance_engine import get_compliance_engine
        print("[PASS] Compliance engine module imported successfully")

        # Test risk assessment import
        from app.compliance.risk_assessment import get_risk_assessment
        print("[PASS] Risk assessment module imported successfully")

        # Test audit governance import
        from app.compliance.audit_governance import get_audit_governance
        print("[PASS] Audit governance module imported successfully")

        # Test regulatory intelligence import
        from app.compliance.regulatory_intelligence import get_regulatory_intelligence
        print("[PASS] Regulatory intelligence module imported successfully")

        return True

    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        return False

def test_service_initialization():
    """Test that all services can be initialized"""
    print("Testing Service Initialization...")

    try:
        from app.compliance.compliance_engine import get_compliance_engine
        from app.compliance.risk_assessment import get_risk_assessment
        from app.compliance.audit_governance import get_audit_governance
        from app.compliance.regulatory_intelligence import get_regulatory_intelligence

        # Initialize services
        compliance_engine = get_compliance_engine()
        risk_assessment = get_risk_assessment()
        audit_governance = get_audit_governance()
        regulatory_intelligence = get_regulatory_intelligence()

        # Verify services are not None
        assert compliance_engine is not None, "Compliance engine is None"
        assert risk_assessment is not None, "Risk assessment is None"
        assert audit_governance is not None, "Audit governance is None"
        assert regulatory_intelligence is not None, "Regulatory intelligence is None"

        print("[PASS] All services initialized successfully")
        return True

    except Exception as e:
        print(f"[FAIL] Service initialization failed: {e}")
        return False

async def test_compliance_engine():
    """Test compliance engine functionality"""
    print("Testing Compliance Engine...")

    try:
        from app.compliance.compliance_engine import (
            get_compliance_engine, ComplianceFrameworkType, PolicyType, ViolationSeverity
        )

        engine = get_compliance_engine()

        # Test framework creation
        framework_id = await engine.create_compliance_framework(
            name="Test Compliance Framework",
            description="Test framework for verification",
            framework_type=ComplianceFrameworkType.SOX,
            jurisdiction="United States"
        )
        assert framework_id, "Failed to create compliance framework"

        # Test policy creation
        policy_id = await engine.create_compliance_policy(
            name="Test Policy",
            description="Test policy for verification",
            policy_type=PolicyType.FINANCIAL_REPORTING,
            framework=ComplianceFrameworkType.SOX
        )
        assert policy_id, "Failed to create compliance policy"

        # Test rule addition
        success = await engine.add_compliance_rule(
            policy_id=policy_id,
            name="Test Rule",
            description="Test compliance rule",
            framework=ComplianceFrameworkType.SOX,
            policy_type=PolicyType.FINANCIAL_REPORTING,
            rule_expression="$status == 'approved'",
            severity=ViolationSeverity.MEDIUM
        )
        assert success, "Failed to add compliance rule"

        # Test entity assessment
        assessment_id = await engine.assess_entity_compliance(
            entity_id="test_entity_123",
            entity_type="deal",
            entity_data={"status": "approved", "amount": 1000000},
            framework=ComplianceFrameworkType.SOX
        )
        assert assessment_id, "Failed to assess entity compliance"

        print("[PASS] Compliance engine tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Compliance engine test failed: {e}")
        return False

async def test_risk_assessment():
    """Test risk assessment functionality"""
    print("Testing Risk Assessment...")

    try:
        from app.compliance.risk_assessment import (
            get_risk_assessment, RiskCategory, MitigationStrategy
        )

        risk_assessment = get_risk_assessment()

        # Test risk model creation
        model_id = risk_assessment.risk_engine.create_risk_model(
            name="Test Risk Model",
            description="Test model for verification",
            category=RiskCategory.FINANCIAL
        )
        assert model_id, "Failed to create risk model"

        # Test risk factor addition
        success = risk_assessment.risk_engine.add_risk_factor(
            model_id=model_id,
            name="Test Factor",
            description="Test risk factor",
            category=RiskCategory.FINANCIAL,
            weight=0.3
        )
        assert success, "Failed to add risk factor"

        # Test risk assessment
        assessment_ids = await risk_assessment.perform_risk_assessment(
            entity_id="test_entity_123",
            entity_type="deal",
            entity_data={"debt_ratio": 0.6, "cash_flow": 1000000},
            model_ids=[model_id]
        )
        assert len(assessment_ids) > 0, "Failed to perform risk assessment"

        # Test mitigation plan creation
        plan_ids = await risk_assessment.create_comprehensive_mitigation_plan(
            assessment_ids=assessment_ids,
            responsible_party="risk_manager"
        )
        assert len(plan_ids) > 0, "Failed to create mitigation plan"

        print("[PASS] Risk assessment tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Risk assessment test failed: {e}")
        return False

async def test_audit_governance():
    """Test audit governance functionality"""
    print("Testing Audit Governance...")

    try:
        from app.compliance.audit_governance import (
            get_audit_governance, EvidenceType, GovernanceFrameworkType
        )

        audit_governance = get_audit_governance()

        # Test audit event logging
        event_id = await audit_governance.log_user_action(
            user_id="test_user_123",
            session_id="session_456",
            action="document_access",
            description="User accessed confidential document",
            entity_id="doc_789",
            entity_type="document"
        )
        assert event_id, "Failed to log audit event"

        # Test evidence preservation
        evidence_id = await audit_governance.preserve_evidence(
            evidence_type=EvidenceType.DOCUMENT,
            title="Test Evidence",
            description="Test evidence for verification",
            collector_id="investigator_123"
        )
        assert evidence_id, "Failed to preserve evidence"

        # Test governance structure creation
        roles_created = audit_governance.create_governance_structure("Test Organization")
        assert len(roles_created) > 0, "Failed to create governance structure"

        # Test audit summary
        summary = audit_governance.get_audit_summary("doc_789", "document")
        assert "entity_id" in summary, "Failed to get audit summary"

        print("[PASS] Audit governance tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Audit governance test failed: {e}")
        return False

async def test_regulatory_intelligence():
    """Test regulatory intelligence functionality"""
    print("Testing Regulatory Intelligence...")

    try:
        from app.compliance.regulatory_intelligence import (
            get_regulatory_intelligence, RegulatoryDomain, Jurisdiction, ComplianceReportType
        )

        regulatory_intelligence = get_regulatory_intelligence()

        # Test regulatory alert subscription
        regulatory_intelligence.subscribe_to_regulatory_alerts(
            user_id="test_user_123",
            domains=[RegulatoryDomain.SECURITIES, RegulatoryDomain.BANKING]
        )

        # Test document analysis
        analysis_id = await regulatory_intelligence.analyze_regulatory_document(
            document_id="test_doc_123",
            document_text="This regulation requires quarterly reporting within 30 days of period end."
        )
        assert analysis_id, "Failed to analyze regulatory document"

        # Test compliance report generation
        report_id = await regulatory_intelligence.generate_compliance_report(
            report_type=ComplianceReportType.QUARTERLY_FILING,
            period_start=datetime.now() - timedelta(days=90),
            period_end=datetime.now(),
            jurisdiction=Jurisdiction.US_FEDERAL,
            domain=RegulatoryDomain.SECURITIES
        )
        assert report_id, "Failed to generate compliance report"

        # Test regulatory calendar
        calendar_data = regulatory_intelligence.get_regulatory_calendar(
            jurisdiction=Jurisdiction.US_FEDERAL,
            days_ahead=30
        )
        assert "jurisdiction" in calendar_data, "Failed to get regulatory calendar"

        print("[PASS] Regulatory intelligence tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Regulatory intelligence test failed: {e}")
        return False

def test_api_endpoints():
    """Test that API endpoints module can be imported"""
    print("Testing API Endpoints...")

    try:
        from app.api.v1 import compliance_platform
        assert hasattr(compliance_platform, 'router'), "Compliance platform router not found"
        print("[PASS] Compliance platform API endpoints available")
        return True

    except ImportError as e:
        print(f"[FAIL] API endpoints test failed: {e}")
        return False

async def test_integration():
    """Test integration between all Sprint 15 components"""
    print("Testing Sprint 15 Integration...")

    try:
        # Get all service instances
        from app.compliance import (
            get_compliance_engine, get_risk_assessment,
            get_audit_governance, get_regulatory_intelligence
        )

        compliance_engine = get_compliance_engine()
        risk_assessment = get_risk_assessment()
        audit_governance = get_audit_governance()
        regulatory_intelligence = get_regulatory_intelligence()

        # Test end-to-end compliance workflow
        # 1. Create compliance framework and policy
        from app.compliance.compliance_engine import ComplianceFrameworkType, PolicyType, ViolationSeverity

        framework_id = await compliance_engine.create_compliance_framework(
            "Integration Test Framework",
            "End-to-end integration test",
            ComplianceFrameworkType.GDPR,
            "European Union"
        )

        policy_id = await compliance_engine.create_compliance_policy(
            "Integration Test Policy",
            "Test policy for integration",
            PolicyType.DATA_PROTECTION,
            ComplianceFrameworkType.GDPR
        )

        # 2. Perform risk assessment
        from app.compliance.risk_assessment import RiskCategory

        model_id = risk_assessment.risk_engine.create_risk_model(
            "Integration Risk Model",
            "Risk model for integration test",
            RiskCategory.REGULATORY
        )

        assessment_ids = await risk_assessment.perform_risk_assessment(
            entity_id="integration_entity_123",
            entity_type="organization",
            entity_data={"data_volume": 1000000, "geographic_reach": "global"},
            model_ids=[model_id]
        )

        # 3. Log audit events
        audit_event_id = await audit_governance.log_user_action(
            user_id="integration_user",
            session_id="integration_session",
            action="compliance_assessment",
            description="Integration test compliance assessment",
            entity_id="integration_entity_123",
            entity_type="organization"
        )

        # 4. Generate regulatory report
        from app.compliance.regulatory_intelligence import ComplianceReportType, Jurisdiction, RegulatoryDomain

        report_id = await regulatory_intelligence.generate_compliance_report(
            ComplianceReportType.COMPLIANCE_CERTIFICATE,
            datetime.now() - timedelta(days=30),
            datetime.now(),
            Jurisdiction.EU,
            RegulatoryDomain.DATA_PROTECTION
        )

        # Verify all components worked together
        assert framework_id and policy_id and assessment_ids and audit_event_id and report_id

        print("[PASS] Sprint 15 integration tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Integration test failed: {e}")
        return False

async def run_comprehensive_test():
    """Run comprehensive Sprint 15 verification"""
    print("Starting Sprint 15 Comprehensive Verification Test")
    print("=" * 60)

    results = {
        "imports": False,
        "service_init": False,
        "compliance_engine": False,
        "risk_assessment": False,
        "audit_governance": False,
        "regulatory_intelligence": False,
        "api_endpoints": False,
        "integration": False
    }

    try:
        # Test imports
        results["imports"] = test_imports()

        # Test service initialization
        results["service_init"] = test_service_initialization()

        # Test individual components
        results["compliance_engine"] = await test_compliance_engine()
        results["risk_assessment"] = await test_risk_assessment()
        results["audit_governance"] = await test_audit_governance()
        results["regulatory_intelligence"] = await test_regulatory_intelligence()

        # Test API endpoints
        results["api_endpoints"] = test_api_endpoints()

        # Test integration
        results["integration"] = await test_integration()

        # Check overall success
        all_passed = all(results.values())

        print("=" * 60)

        if all_passed:
            print("Sprint 15 Verification COMPLETED SUCCESSFULLY!")
            print("[PASS] All compliance platform components are working correctly")
            print("[PASS] Compliance engine operational")
            print("[PASS] Risk assessment framework functional")
            print("[PASS] Audit governance system operational")
            print("[PASS] Regulatory intelligence platform active")
            print("[PASS] API endpoints integrated")
            print("[PASS] Component integration verified")
            status = "VERIFIED"
        else:
            print("Sprint 15 Verification completed with some issues")
            failed_tests = [test for test, passed in results.items() if not passed]
            print(f"[FAIL] Failed tests: {', '.join(failed_tests)}")
            status = "PARTIALLY_VERIFIED"

        # Generate summary
        summary = {
            "sprint": 15,
            "feature": "Advanced Compliance & Risk Management Platform",
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "test_results": results,
            "components_tested": [
                "Compliance Engine",
                "Risk Assessment Framework",
                "Audit & Governance",
                "Regulatory Intelligence",
                "API Endpoints"
            ]
        }

        return summary

    except Exception as e:
        print(f"[FAIL] Sprint 15 Verification FAILED: {str(e)}")
        return {
            "sprint": 15,
            "status": "FAILED",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "test_results": results
        }

if __name__ == "__main__":
    # Run the verification test
    result = asyncio.run(run_comprehensive_test())

    # Print final result
    print("\nFinal Result:")
    print(json.dumps(result, indent=2))