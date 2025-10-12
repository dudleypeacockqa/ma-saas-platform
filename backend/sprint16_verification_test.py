"""
Sprint 16 Verification Test - Advanced Deal Intelligence & Transaction Orchestration Platform
Comprehensive test suite for all Sprint 16 deal intelligence, orchestration, analytics, and due diligence features
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
    """Test that all Sprint 16 modules can be imported"""
    print("Testing Sprint 16 Module Imports...")

    try:
        # Test deal intelligence import
        from app.deal_intelligence.deal_intelligence_engine import get_deal_intelligence_engine
        print("[PASS] Deal intelligence engine module imported successfully")

        # Test transaction orchestration import
        from app.deal_intelligence.transaction_orchestration import get_transaction_orchestrator
        print("[PASS] Transaction orchestration module imported successfully")

        # Test predictive analytics import
        from app.deal_intelligence.predictive_analytics import get_predictive_analytics
        print("[PASS] Predictive analytics module imported successfully")

        # Test due diligence automation import
        from app.deal_intelligence.due_diligence_automation import get_due_diligence_automation
        print("[PASS] Due diligence automation module imported successfully")

        return True

    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        return False

def test_service_initialization():
    """Test that all services can be initialized"""
    print("Testing Service Initialization...")

    try:
        from app.deal_intelligence import (
            get_deal_intelligence_engine, get_transaction_orchestrator,
            get_predictive_analytics, get_due_diligence_automation
        )

        # Initialize services
        deal_intelligence = get_deal_intelligence_engine()
        transaction_orchestrator = get_transaction_orchestrator()
        predictive_analytics = get_predictive_analytics()
        due_diligence_automation = get_due_diligence_automation()

        # Verify services are not None
        assert deal_intelligence is not None, "Deal intelligence engine is None"
        assert transaction_orchestrator is not None, "Transaction orchestrator is None"
        assert predictive_analytics is not None, "Predictive analytics is None"
        assert due_diligence_automation is not None, "Due diligence automation is None"

        print("[PASS] All services initialized successfully")
        return True

    except Exception as e:
        print(f"[FAIL] Service initialization failed: {e}")
        return False

async def test_deal_intelligence_engine():
    """Test deal intelligence engine functionality"""
    print("Testing Deal Intelligence Engine...")

    try:
        from app.deal_intelligence.deal_intelligence_engine import (
            get_deal_intelligence_engine, DealProfile, DealType, IndustryVertical, DealStage
        )

        engine = get_deal_intelligence_engine()

        # Test deal profile creation
        deal_profile = DealProfile(
            deal_id="test_deal_001",
            deal_type=DealType.ACQUISITION,
            target_company="Test Target Corp",
            acquirer_company="Test Acquirer Inc",
            industry=IndustryVertical.TECHNOLOGY,
            deal_value=250000000.0,
            currency="USD",
            stage=DealStage.PRELIMINARY_DUE_DILIGENCE,
            key_metrics={
                "revenue": 50000000,
                "ebitda": 12500000,
                "growth_rate": 0.15,
                "market_position": 0.8
            },
            strategic_rationale="Technology platform acquisition for market expansion"
        )

        # Test deal opportunity analysis
        analysis_result = await engine.analyze_deal_opportunity(deal_profile)
        assert "deal_id" in analysis_result, "Analysis result missing deal_id"
        assert "deal_score" in analysis_result, "Analysis result missing deal_score"
        assert "market_context" in analysis_result, "Analysis result missing market_context"

        # Verify deal score components
        deal_score = analysis_result["deal_score"]
        assert "overall_score" in deal_score, "Deal score missing overall_score"
        assert "financial_score" in deal_score, "Deal score missing financial_score"
        assert "strategic_score" in deal_score, "Deal score missing strategic_score"
        assert "execution_score" in deal_score, "Deal score missing execution_score"
        assert "risk_score" in deal_score, "Deal score missing risk_score"
        assert "market_score" in deal_score, "Deal score missing market_score"

        # Verify market context
        market_context = analysis_result["market_context"]
        assert "industry" in market_context, "Market context missing industry"
        assert "market_size" in market_context, "Market context missing market_size"
        assert "growth_rate" in market_context, "Market context missing growth_rate"

        print("[PASS] Deal intelligence engine tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Deal intelligence engine test failed: {e}")
        return False

async def test_transaction_orchestration():
    """Test transaction orchestration functionality"""
    print("Testing Transaction Orchestration...")

    try:
        from app.deal_intelligence.transaction_orchestration import (
            get_transaction_orchestrator, StakeholderRole
        )

        orchestrator = get_transaction_orchestrator()

        # Test workflow template creation
        template_created = orchestrator.workflow_engine.create_workflow_template(
            template_id="test_template_001",
            name="Test Acquisition Workflow",
            deal_type="acquisition"
        )
        assert template_created, "Failed to create workflow template"

        # Test workflow creation from template
        workflow_id = orchestrator.workflow_engine.create_workflow_from_template(
            deal_id="test_deal_001",
            template_id="test_template_001"
        )
        assert workflow_id, "Failed to create workflow from template"

        # Test stakeholder assignments
        stakeholder_assignments = {
            "deal_lead": "john.smith@company.com",
            "legal_counsel": "jane.doe@lawfirm.com",
            "financial_advisor": "mike.johnson@advisory.com"
        }

        workflow_started = orchestrator.workflow_engine.start_workflow(
            workflow_id, stakeholder_assignments
        )
        assert workflow_started, "Failed to start workflow"

        # Test workflow status retrieval
        status = orchestrator.workflow_engine.get_workflow_status(workflow_id)
        assert status, "Failed to get workflow status"
        assert "workflow_id" in status, "Status missing workflow_id"
        assert "overall_progress" in status, "Status missing overall_progress"

        # Test active tasks retrieval
        active_tasks = orchestrator.workflow_engine.get_active_tasks()
        assert isinstance(active_tasks, list), "Active tasks should be a list"

        # Test collaboration hub
        meeting_id = orchestrator.collaboration_hub.schedule_stakeholder_meeting(
            workflow_id=workflow_id,
            participants=["john.smith@company.com", "jane.doe@lawfirm.com"],
            subject="Initial Due Diligence Meeting",
            agenda="Review deal structure and timeline",
            scheduled_at=datetime.now() + timedelta(days=1)
        )
        assert meeting_id, "Failed to schedule stakeholder meeting"

        print("[PASS] Transaction orchestration tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Transaction orchestration test failed: {e}")
        return False

async def test_predictive_analytics():
    """Test predictive analytics functionality"""
    print("Testing Predictive Analytics...")

    try:
        from app.deal_intelligence.predictive_analytics import (
            get_predictive_analytics, PredictionType, ForecastHorizon
        )

        analytics = get_predictive_analytics()

        # Test prediction model creation
        model_created = analytics.deal_forecasting.create_prediction_model(
            model_id="test_model_001",
            name="Test Deal Success Model",
            prediction_type=PredictionType.DEAL_SUCCESS
        )
        assert model_created, "Failed to create prediction model"

        # Test model training with sample data
        training_data = [
            {
                "deal_value": 100000000,
                "industry": "technology",
                "revenue": 25000000,
                "ebitda": 7500000,
                "growth_rate": 0.20,
                "outcome": "success"
            },
            {
                "deal_value": 500000000,
                "industry": "healthcare",
                "revenue": 80000000,
                "ebitda": 16000000,
                "growth_rate": 0.12,
                "outcome": "success"
            }
        ]

        training_success = analytics.deal_forecasting.train_model(
            model_id="test_model_001",
            training_data=training_data
        )
        assert training_success, "Failed to train prediction model"

        # Test deal prediction
        deal_data = {
            "deal_value": 200000000,
            "industry": "technology",
            "revenue": 40000000,
            "ebitda": 10000000,
            "growth_rate": 0.18,
            "market_position": 0.75
        }

        prediction = analytics.deal_forecasting.predict_deal_outcome(
            deal_id="test_deal_002",
            deal_data=deal_data,
            prediction_type=PredictionType.DEAL_SUCCESS
        )

        assert prediction.prediction_id, "Prediction missing prediction_id"
        assert prediction.predicted_outcome, "Prediction missing predicted_outcome"
        assert prediction.confidence_score > 0, "Prediction missing valid confidence_score"

        # Test market forecasting
        market_forecast = analytics.market_forecasting.generate_market_forecast(
            industry="technology",
            region="global",
            horizon=ForecastHorizon.MEDIUM_TERM
        )

        assert market_forecast.forecast_id, "Market forecast missing forecast_id"
        assert market_forecast.predictions, "Market forecast missing predictions"
        assert market_forecast.confidence_intervals, "Market forecast missing confidence_intervals"

        # Test portfolio optimization
        portfolio_data = {
            "deals": {
                "deal_001": {
                    "industry": "technology",
                    "deal_value": 100000000,
                    "risk_score": 45,
                    "expected_return": 0.15
                },
                "deal_002": {
                    "industry": "healthcare",
                    "deal_value": 200000000,
                    "risk_score": 35,
                    "expected_return": 0.12
                }
            }
        }

        optimization = analytics.portfolio_optimizer.optimize_deal_portfolio(
            portfolio_data=portfolio_data,
            constraints={"max_single_position": 0.4},
            optimization_objective="sharpe_ratio"
        )

        assert optimization.optimization_id, "Optimization missing optimization_id"
        assert optimization.portfolio_composition, "Optimization missing portfolio_composition"
        assert optimization.expected_return > 0, "Optimization missing valid expected_return"

        print("[PASS] Predictive analytics tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Predictive analytics test failed: {e}")
        return False

async def test_due_diligence_automation():
    """Test due diligence automation functionality"""
    print("Testing Due Diligence Automation...")

    try:
        from app.deal_intelligence.due_diligence_automation import (
            get_due_diligence_automation, DocumentType, DataRoomAccess, DataRoomUser,
            DocumentMetadata, QAItem, ReviewPriority
        )

        dd_automation = get_due_diligence_automation()

        # Test analysis models initialization
        models_initialized = dd_automation.document_analysis_engine.initialize_analysis_models()
        assert models_initialized, "Failed to initialize analysis models"

        # Test data room creation
        data_room_created = dd_automation.data_room_manager.create_data_room(
            data_room_id="test_dataroom_001",
            name="Test Deal Data Room",
            deal_id="test_deal_001",
            administrator="admin@company.com"
        )
        assert data_room_created, "Failed to create data room"

        # Test user addition to data room
        test_user = DataRoomUser(
            user_id="test_user_001",
            name="Test User",
            organization="Test Organization",
            email="testuser@company.com",
            access_level=DataRoomAccess.READ_ONLY,
            permitted_folders=["01_Executive_Summary", "02_Corporate_Information"],
            access_granted_date=datetime.now()
        )

        user_added = dd_automation.data_room_manager.add_user("test_dataroom_001", test_user)
        assert user_added, "Failed to add user to data room"

        # Test document metadata creation
        doc_metadata = DocumentMetadata(
            document_id="test_doc_001",
            filename="test_financial_statement.pdf",
            document_type=DocumentType.FINANCIAL_STATEMENT,
            file_size=1024000,
            upload_date=datetime.now(),
            uploaded_by="test_user_001",
            tags=["financial", "quarterly", "2023"]
        )

        # Add admin user first for upload permissions
        admin_user = DataRoomUser(
            user_id="admin@company.com",
            name="Admin User",
            organization="Company",
            email="admin@company.com",
            access_level=DataRoomAccess.ADMIN,
            permitted_folders=[],
            access_granted_date=datetime.now()
        )
        dd_automation.data_room_manager.add_user("test_dataroom_001", admin_user)

        # Test document upload
        doc_uploaded = dd_automation.data_room_manager.upload_document(
            data_room_id="test_dataroom_001",
            user_id="admin@company.com",  # Admin can upload
            document_metadata=doc_metadata,
            folder_path="03_Financial_Information"
        )
        assert doc_uploaded, "Failed to upload document"

        # Test document analysis
        sample_document_content = """
        Financial Statement for Q3 2023
        Revenue: $50,000,000
        EBITDA: $12,500,000
        Net Income: $8,000,000
        Total Assets: $200,000,000
        Total Liabilities: $80,000,000
        Cash Flow from Operations: $15,000,000
        """

        analysis = dd_automation.document_analysis_engine.analyze_document(
            document_id="test_doc_001",
            document_content=sample_document_content,
            document_type=DocumentType.FINANCIAL_STATEMENT,
            analysis_types=["financial_analysis", "risk_assessment"]
        )

        assert analysis.analysis_id, "Analysis missing analysis_id"
        assert analysis.confidence_score > 0, "Analysis missing valid confidence_score"
        assert len(analysis.key_findings) > 0, "Analysis missing key_findings"

        # Test Q&A automation
        qa_item = QAItem(
            qa_id="test_qa_001",
            question="What is the company's revenue growth rate?",
            category="Financial",
            priority=ReviewPriority.HIGH,
            status="pending"
        )

        qa_created = dd_automation.qa_automation_engine.create_qa_item(qa_item)
        assert qa_created, "Failed to create Q&A item"

        # Test automated response generation
        auto_response = dd_automation.qa_automation_engine.generate_automated_response(
            qa_id="test_qa_001",
            document_analyses=[analysis]
        )
        assert auto_response, "Failed to generate automated response"

        # Test data room analytics
        analytics = dd_automation.data_room_manager.get_data_room_analytics("test_dataroom_001")
        assert analytics, "Failed to get data room analytics"
        assert "total_documents" in analytics, "Analytics missing total_documents"

        print("[PASS] Due diligence automation tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Due diligence automation test failed: {e}")
        return False

def test_api_endpoints():
    """Test that API endpoints module can be imported"""
    print("Testing API Endpoints...")

    try:
        from app.api.v1 import deal_intelligence_platform
        assert hasattr(deal_intelligence_platform, 'router'), "Deal intelligence platform router not found"
        print("[PASS] Deal intelligence platform API endpoints available")
        return True

    except ImportError as e:
        print(f"[FAIL] API endpoints test failed: {e}")
        return False

async def test_integration():
    """Test integration between all Sprint 16 components"""
    print("Testing Sprint 16 Integration...")

    try:
        # Get all service instances
        from app.deal_intelligence import (
            get_deal_intelligence_engine, get_transaction_orchestrator,
            get_predictive_analytics, get_due_diligence_automation
        )

        deal_intelligence = get_deal_intelligence_engine()
        transaction_orchestrator = get_transaction_orchestrator()
        predictive_analytics = get_predictive_analytics()
        due_diligence_automation = get_due_diligence_automation()

        # Test end-to-end deal intelligence workflow
        from app.deal_intelligence.deal_intelligence_engine import (
            DealProfile, DealType, IndustryVertical
        )

        # 1. Create deal profile and analyze opportunity
        deal_profile = DealProfile(
            deal_id="integration_deal_001",
            deal_type=DealType.ACQUISITION,
            target_company="Integration Target",
            acquirer_company="Integration Acquirer",
            industry=IndustryVertical.TECHNOLOGY,
            deal_value=500000000.0,
            key_metrics={
                "revenue": 100000000,
                "ebitda": 25000000,
                "growth_rate": 0.20
            }
        )

        deal_analysis = await deal_intelligence.analyze_deal_opportunity(deal_profile)
        assert deal_analysis, "Failed to analyze deal opportunity"

        # 2. Create transaction workflow
        workflow_result = await transaction_orchestrator.orchestrate_transaction(
            deal_id="integration_deal_001",
            deal_type="acquisition",
            stakeholder_assignments={
                "deal_lead": "integration_lead@company.com",
                "legal_counsel": "integration_legal@lawfirm.com"
            }
        )
        assert workflow_result["workflow_id"], "Failed to create workflow"

        # 3. Create prediction models for comprehensive analysis
        from app.deal_intelligence.predictive_analytics import PredictionType

        # Create required models
        predictive_analytics.deal_forecasting.create_prediction_model(
            "valuation_model", "Valuation Model", PredictionType.VALUATION_ACCURACY
        )
        predictive_analytics.deal_forecasting.create_prediction_model(
            "integration_model", "Integration Model", PredictionType.INTEGRATION_SUCCESS
        )

        # Generate predictions
        prediction_analysis = await predictive_analytics.comprehensive_deal_analysis(
            deal_id="integration_deal_001",
            deal_data={
                "deal_value": 500000000,
                "industry": "technology",
                "revenue": 100000000,
                "ebitda": 25000000,
                "growth_rate": 0.20
            }
        )
        assert prediction_analysis, "Failed to generate predictions"

        # 4. Initialize due diligence process
        dd_initialization = await due_diligence_automation.initialize_due_diligence_process(
            deal_id="integration_deal_001",
            data_room_config={
                "administrator": "integration_admin@company.com",
                "users": [
                    {
                        "user_id": "integration_user_001",
                        "name": "Integration User",
                        "organization": "Test Org",
                        "email": "user@company.com",
                        "access_level": "read_only",
                        "permitted_folders": ["01_Executive_Summary"]
                    }
                ]
            }
        )
        assert dd_initialization["data_room_created"], "Failed to initialize due diligence"

        # Verify all components worked together
        assert deal_analysis and workflow_result and prediction_analysis and dd_initialization

        print("[PASS] Sprint 16 integration tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Integration test failed: {e}")
        return False

async def run_comprehensive_test():
    """Run comprehensive Sprint 16 verification"""
    print("Starting Sprint 16 Comprehensive Verification Test")
    print("=" * 60)

    results = {
        "imports": False,
        "service_init": False,
        "deal_intelligence": False,
        "transaction_orchestration": False,
        "predictive_analytics": False,
        "due_diligence_automation": False,
        "api_endpoints": False,
        "integration": False
    }

    try:
        # Test imports
        results["imports"] = test_imports()

        # Test service initialization
        results["service_init"] = test_service_initialization()

        # Test individual components
        results["deal_intelligence"] = await test_deal_intelligence_engine()
        results["transaction_orchestration"] = await test_transaction_orchestration()
        results["predictive_analytics"] = await test_predictive_analytics()
        results["due_diligence_automation"] = await test_due_diligence_automation()

        # Test API endpoints
        results["api_endpoints"] = test_api_endpoints()

        # Test integration
        results["integration"] = await test_integration()

        # Check overall success
        all_passed = all(results.values())

        print("=" * 60)

        if all_passed:
            print("Sprint 16 Verification COMPLETED SUCCESSFULLY!")
            print("[PASS] All deal intelligence platform components are working correctly")
            print("[PASS] Deal intelligence engine operational")
            print("[PASS] Transaction orchestration system functional")
            print("[PASS] Predictive analytics platform active")
            print("[PASS] Due diligence automation operational")
            print("[PASS] API endpoints integrated")
            print("[PASS] Component integration verified")
            status = "VERIFIED"
        else:
            print("Sprint 16 Verification completed with some issues")
            failed_tests = [test for test, passed in results.items() if not passed]
            print(f"[FAIL] Failed tests: {', '.join(failed_tests)}")
            status = "PARTIALLY_VERIFIED"

        # Generate summary
        summary = {
            "sprint": 16,
            "feature": "Advanced Deal Intelligence & Transaction Orchestration Platform",
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "test_results": results,
            "components_tested": [
                "Deal Intelligence Engine",
                "Transaction Orchestration Hub",
                "Predictive Analytics & Forecasting",
                "Due Diligence Automation",
                "API Endpoints"
            ]
        }

        return summary

    except Exception as e:
        print(f"[FAIL] Sprint 16 Verification FAILED: {str(e)}")
        return {
            "sprint": 16,
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