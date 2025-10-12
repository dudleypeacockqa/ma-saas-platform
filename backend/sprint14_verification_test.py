"""
Sprint 14 Verification Test - Advanced Workflow Automation & Integration Platform
Comprehensive test suite for all Sprint 14 workflow, integration, automation, and orchestration features
"""

import asyncio
from datetime import datetime
import json
import sys
import os
from collections import defaultdict

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all Sprint 14 modules can be imported"""
    print("Testing Sprint 14 Module Imports...")

    try:
        # Test workflow engine import
        from app.workflows.workflow_engine import get_workflow_engine, NodeType
        print("[PASS] Workflow engine module imported successfully")

        # Test integration hub import
        from app.workflows.integration_hub import get_integration_hub, IntegrationType
        print("[PASS] Integration hub module imported successfully")

        # Test process automation import
        from app.workflows.process_automation import get_process_automation, AutomationType
        print("[PASS] Process automation module imported successfully")

        # Test orchestration platform import
        from app.workflows.orchestration_platform import get_orchestration_platform
        print("[PASS] Orchestration platform module imported successfully")

        return True

    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        return False

def test_service_initialization():
    """Test that all services can be initialized"""
    print("Testing Service Initialization...")

    try:
        from app.workflows.workflow_engine import get_workflow_engine
        from app.workflows.integration_hub import get_integration_hub
        from app.workflows.process_automation import get_process_automation
        from app.workflows.orchestration_platform import get_orchestration_platform

        # Initialize services
        workflow_engine = get_workflow_engine()
        integration_hub = get_integration_hub()
        process_automation = get_process_automation()
        orchestration_platform = get_orchestration_platform()

        # Verify services are not None
        assert workflow_engine is not None, "Workflow engine is None"
        assert integration_hub is not None, "Integration hub is None"
        assert process_automation is not None, "Process automation is None"
        assert orchestration_platform is not None, "Orchestration platform is None"

        print("[PASS] All services initialized successfully")
        return True

    except Exception as e:
        print(f"[FAIL] Service initialization failed: {e}")
        return False

async def test_workflow_engine():
    """Test workflow engine functionality"""
    print("Testing Workflow Engine...")

    try:
        from app.workflows.workflow_engine import get_workflow_engine, NodeType

        engine = get_workflow_engine()

        # Test workflow creation
        workflow_id = await engine.create_workflow(
            name="Test Workflow",
            description="Test workflow for verification"
        )
        assert workflow_id, "Failed to create workflow"

        # Test node addition
        start_node = engine.builder.add_node(
            workflow_id, "Start", NodeType.START
        )
        end_node = engine.builder.add_node(
            workflow_id, "End", NodeType.END
        )
        assert start_node and end_node, "Failed to add nodes"

        # Test node connection
        connection_id = engine.builder.connect_nodes(
            workflow_id, start_node, end_node
        )
        assert connection_id, "Failed to connect nodes"

        # Test workflow validation
        validation = engine.builder.validate_workflow(workflow_id)
        assert validation["valid"], "Workflow validation failed"

        print("[PASS] Workflow engine tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Workflow engine test failed: {e}")
        return False

async def test_integration_hub():
    """Test integration hub functionality"""
    print("Testing Integration Hub...")

    try:
        from app.workflows.integration_hub import (
            get_integration_hub, IntegrationType, AuthType
        )

        hub = get_integration_hub()

        # Test integration creation
        integration_id = await hub.create_integration(
            name="Test Integration",
            description="Test integration for verification",
            integration_type=IntegrationType.REST_API,
            endpoint_url="https://api.example.com",
            auth_type=AuthType.API_KEY,
            auth_config={"api_key": "test_key"}
        )
        assert integration_id, "Failed to create integration"

        # Test getting integrations
        integrations = hub.get_integrations()
        assert len(integrations) > 0, "Failed to get integrations"

        print("[PASS] Integration hub tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Integration hub test failed: {e}")
        return False

async def test_process_automation():
    """Test process automation functionality"""
    print("Testing Process Automation...")

    try:
        from app.workflows.process_automation import (
            get_process_automation, AutomationType, TriggerEvent,
            AutomationCondition, AutomationAction, ActionType
        )

        automation = get_process_automation()

        # Test automation rule creation
        conditions = [
            AutomationCondition(
                field="status",
                operator="eq",
                value="completed"
            )
        ]

        actions = [
            AutomationAction(
                action_id="action_1",
                action_type=ActionType.SEND_EMAIL,
                config={"recipients": ["test@example.com"]}
            )
        ]

        rule_id = await automation.create_automation_rule(
            name="Test Rule",
            description="Test automation rule",
            automation_type=AutomationType.DEAL_LIFECYCLE,
            trigger_event=TriggerEvent.DEAL_STATUS_CHANGED,
            conditions=conditions,
            actions=actions
        )
        assert rule_id, "Failed to create automation rule"

        # Test getting rules
        rules = automation.get_automation_rules()
        assert len(rules) > 0, "Failed to get automation rules"

        print("[PASS] Process automation tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Process automation test failed: {e}")
        return False

async def test_orchestration_platform():
    """Test orchestration platform functionality"""
    print("Testing Orchestration Platform...")

    try:
        from app.workflows.orchestration_platform import (
            get_orchestration_platform, ServiceDefinition, ResourceType
        )

        platform = get_orchestration_platform()

        # Initialize platform
        await platform.initialize_platform()

        # Test service deployment
        service_def = ServiceDefinition(
            service_id="test_service",
            name="Test Service",
            description="Test service for verification",
            image="test:latest",
            resource_requirements={
                ResourceType.CPU.value: 2.0,
                ResourceType.MEMORY.value: 4.0
            }
        )

        instance_ids = await platform.deploy_service(service_def, 2)
        assert len(instance_ids) == 2, "Failed to deploy service instances"

        # Test platform status
        status = platform.get_platform_status()
        assert status["services_managed"] >= 1, "Platform status incorrect"

        print("[PASS] Orchestration platform tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Orchestration platform test failed: {e}")
        return False

def test_api_endpoints():
    """Test that API endpoints module can be imported"""
    print("Testing API Endpoints...")

    try:
        from app.api.v1 import workflow_platform
        assert hasattr(workflow_platform, 'router'), "Workflow platform router not found"
        print("[PASS] Workflow platform API endpoints available")
        return True

    except ImportError as e:
        print(f"[FAIL] API endpoints test failed: {e}")
        return False

async def test_integration():
    """Test integration between all Sprint 14 components"""
    print("Testing Sprint 14 Integration...")

    try:
        # Get all service instances
        from app.workflows import (
            get_workflow_engine, get_integration_hub,
            get_process_automation, get_orchestration_platform
        )

        workflow_engine = get_workflow_engine()
        integration_hub = get_integration_hub()
        process_automation = get_process_automation()
        orchestration_platform = get_orchestration_platform()

        # Test end-to-end workflow
        # 1. Create a workflow
        workflow_id = await workflow_engine.create_workflow(
            "Integration Test Workflow",
            "End-to-end integration test"
        )

        # 2. Create an integration
        from app.workflows.integration_hub import IntegrationType, AuthType
        integration_id = await integration_hub.create_integration(
            "Integration Test API",
            "Test integration",
            IntegrationType.REST_API,
            "https://test.api.com",
            AuthType.NONE
        )

        # 3. Create automation rule
        from app.workflows.process_automation import (
            AutomationType, TriggerEvent, AutomationCondition,
            AutomationAction, ActionType
        )

        rule_id = await process_automation.create_automation_rule(
            "Integration Test Rule",
            "Test rule for integration",
            AutomationType.DEAL_LIFECYCLE,
            TriggerEvent.DEAL_CREATED,
            [],
            [AutomationAction("action_1", ActionType.SEND_EMAIL, {})]
        )

        # 4. Initialize orchestration platform
        await orchestration_platform.initialize_platform()

        # Verify all components are working together
        assert workflow_id and integration_id and rule_id
        assert orchestration_platform.get_platform_status()

        print("[PASS] Sprint 14 integration tests passed")
        return True

    except Exception as e:
        print(f"[FAIL] Integration test failed: {e}")
        return False

async def run_comprehensive_test():
    """Run comprehensive Sprint 14 verification"""
    print("Starting Sprint 14 Comprehensive Verification Test")
    print("=" * 60)

    results = {
        "imports": False,
        "service_init": False,
        "workflow_engine": False,
        "integration_hub": False,
        "process_automation": False,
        "orchestration_platform": False,
        "api_endpoints": False,
        "integration": False
    }

    try:
        # Test imports
        results["imports"] = test_imports()

        # Test service initialization
        results["service_init"] = test_service_initialization()

        # Test individual components
        results["workflow_engine"] = await test_workflow_engine()
        results["integration_hub"] = await test_integration_hub()
        results["process_automation"] = await test_process_automation()
        results["orchestration_platform"] = await test_orchestration_platform()

        # Test API endpoints
        results["api_endpoints"] = test_api_endpoints()

        # Test integration
        results["integration"] = await test_integration()

        # Check overall success
        all_passed = all(results.values())

        print("=" * 60)

        if all_passed:
            print("Sprint 14 Verification COMPLETED SUCCESSFULLY!")
            print("[PASS] All workflow platform components are working correctly")
            print("[PASS] Workflow engine operational")
            print("[PASS] Integration hub functional")
            print("[PASS] Process automation operational")
            print("[PASS] Orchestration platform active")
            print("[PASS] API endpoints integrated")
            print("[PASS] Component integration verified")
            status = "VERIFIED"
        else:
            print("Sprint 14 Verification completed with some issues")
            failed_tests = [test for test, passed in results.items() if not passed]
            print(f"[FAIL] Failed tests: {', '.join(failed_tests)}")
            status = "PARTIALLY_VERIFIED"

        # Generate summary
        summary = {
            "sprint": 14,
            "feature": "Advanced Workflow Automation & Integration Platform",
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "test_results": results,
            "components_tested": [
                "Workflow Engine",
                "Integration Hub",
                "Process Automation",
                "Orchestration Platform",
                "API Endpoints"
            ]
        }

        return summary

    except Exception as e:
        print(f"[FAIL] Sprint 14 Verification FAILED: {str(e)}")
        return {
            "sprint": 14,
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