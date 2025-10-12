"""
Sprint 10 Verification Test Suite
Test enterprise features: integrations, admin, performance, and business intelligence
"""

import asyncio
import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.enterprise import (
    get_integrations_hub, get_enterprise_admin_service,
    get_performance_manager, get_business_intelligence_service,
    IntegrationProvider, MetricType, DashboardWidget, ReportFormat
)


class Sprint10Verifier:
    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.organization_id = "test_org_sprint10"
        self.user_id = "test_user_sprint10"

    async def run_all_tests(self):
        """Run all Sprint 10 verification tests"""
        print("Starting Sprint 10 Enterprise Features Verification")
        print("=" * 60)

        test_suites = [
            ("Integrations Hub Tests", self.test_integrations_hub),
            ("Enterprise Admin Tests", self.test_enterprise_admin),
            ("Performance Layer Tests", self.test_performance_layer),
            ("Business Intelligence Tests", self.test_business_intelligence)
        ]

        total_tests = 0
        passed_tests = 0

        for suite_name, test_function in test_suites:
            print(f"\n{suite_name}")
            print("-" * 40)

            suite_results = await test_function()

            for result in suite_results:
                total_tests += 1
                status = "PASS" if result["passed"] else "FAIL"
                print(f"{status} {result['name']}")
                if not result["passed"]:
                    print(f"   Error: {result.get('error', 'Unknown error')}")
                else:
                    passed_tests += 1

        print(f"\nSprint 10 Verification Summary")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        if passed_tests == total_tests:
            print("\nSprint 10 Enterprise Features: ALL TESTS PASSED!")
            print("Advanced integrations and enterprise features are fully operational")
        else:
            print(f"\n{total_tests - passed_tests} tests failed - review required")

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "all_passed": passed_tests == total_tests
        }

    async def test_integrations_hub(self) -> List[Dict[str, Any]]:
        """Test Integrations Hub functionality"""
        results = []
        hub = get_integrations_hub()

        # Test 1: Configure Salesforce integration
        try:
            integration_id = await hub.configure_integration(
                provider=IntegrationProvider.SALESFORCE,
                organization_id=self.organization_id,
                config={
                    "client_id": "test_client_id",
                    "client_secret": "test_client_secret",
                    "sandbox": True
                }
            )
            results.append({
                "name": "Configure Salesforce Integration",
                "passed": bool(integration_id),
                "data": {"integration_id": integration_id}
            })
        except Exception as e:
            results.append({
                "name": "Configure Salesforce Integration",
                "passed": False,
                "error": str(e)
            })

        # Test 2: List active integrations
        try:
            integrations = hub.list_integrations(self.organization_id)
            results.append({
                "name": "List Active Integrations",
                "passed": isinstance(integrations, list),
                "data": {"count": len(integrations)}
            })
        except Exception as e:
            results.append({
                "name": "List Active Integrations",
                "passed": False,
                "error": str(e)
            })

        # Test 3: Configure HubSpot integration
        try:
            hubspot_id = await hub.configure_integration(
                provider=IntegrationProvider.HUBSPOT,
                organization_id=self.organization_id,
                config={
                    "api_key": "test_api_key",
                    "portal_id": "12345"
                }
            )
            results.append({
                "name": "Configure HubSpot Integration",
                "passed": bool(hubspot_id),
                "data": {"integration_id": hubspot_id}
            })
        except Exception as e:
            results.append({
                "name": "Configure HubSpot Integration",
                "passed": False,
                "error": str(e)
            })

        # Test 4: Check integration health
        try:
            if results[0]["passed"]:
                health = hub.check_integration_health(
                    results[0]["data"]["integration_id"],
                    self.organization_id
                )
                results.append({
                    "name": "Check Integration Health",
                    "passed": "status" in health,
                    "data": health
                })
            else:
                results.append({
                    "name": "Check Integration Health",
                    "passed": False,
                    "error": "No integration to check"
                })
        except Exception as e:
            results.append({
                "name": "Check Integration Health",
                "passed": False,
                "error": str(e)
            })

        return results

    async def test_enterprise_admin(self) -> List[Dict[str, Any]]:
        """Test Enterprise Administration functionality"""
        results = []
        admin_service = get_enterprise_admin_service()

        # Test 1: Record audit event
        try:
            event_id = admin_service.compliance_manager.record_audit_event(
                event_type="user_login",
                user_id=self.user_id,
                organization_id=self.organization_id,
                resource_type="user",
                resource_id=self.user_id,
                action="login",
                details={"ip_address": "192.168.1.100", "user_agent": "Test Agent"}
            )
            results.append({
                "name": "Record Audit Event",
                "passed": bool(event_id),
                "data": {"event_id": event_id}
            })
        except Exception as e:
            results.append({
                "name": "Record Audit Event",
                "passed": False,
                "error": str(e)
            })

        # Test 2: Generate compliance report
        try:
            report_id = admin_service.compliance_manager.generate_compliance_report(
                organization_id=self.organization_id,
                framework="SOX",
                period_start=datetime.utcnow() - timedelta(days=30),
                period_end=datetime.utcnow()
            )
            results.append({
                "name": "Generate Compliance Report",
                "passed": bool(report_id),
                "data": {"report_id": report_id}
            })
        except Exception as e:
            results.append({
                "name": "Generate Compliance Report",
                "passed": False,
                "error": str(e)
            })

        # Test 3: Get audit trail
        try:
            trail = admin_service.compliance_manager.get_audit_trail(
                organization_id=self.organization_id,
                start_date=datetime.utcnow() - timedelta(days=7),
                end_date=datetime.utcnow()
            )
            results.append({
                "name": "Get Audit Trail",
                "passed": isinstance(trail, list),
                "data": {"events_count": len(trail)}
            })
        except Exception as e:
            results.append({
                "name": "Get Audit Trail",
                "passed": False,
                "error": str(e)
            })

        # Test 4: Configure white-label
        try:
            config_id = admin_service.configure_white_label(
                organization_id=self.organization_id,
                branding={
                    "logo_url": "https://example.com/logo.png",
                    "primary_color": "#007bff",
                    "company_name": "Test Corp"
                },
                domain="test.example.com",
                features={"custom_domain": True, "sso": True}
            )
            results.append({
                "name": "Configure White Label",
                "passed": bool(config_id),
                "data": {"config_id": config_id}
            })
        except Exception as e:
            results.append({
                "name": "Configure White Label",
                "passed": False,
                "error": str(e)
            })

        return results

    async def test_performance_layer(self) -> List[Dict[str, Any]]:
        """Test Performance Layer functionality"""
        results = []
        performance_manager = get_performance_manager()

        # Test 1: Cache operations
        try:
            # Set cache value
            performance_manager.cache_manager.set("test_key", "test_value", ttl=300)

            # Get cache value
            value = performance_manager.cache_manager.get("test_key")

            results.append({
                "name": "Cache Set/Get Operations",
                "passed": value == "test_value",
                "data": {"cached_value": value}
            })
        except Exception as e:
            results.append({
                "name": "Cache Set/Get Operations",
                "passed": False,
                "error": str(e)
            })

        # Test 2: Cache statistics
        try:
            stats = performance_manager.cache_manager.get_cache_stats()
            results.append({
                "name": "Get Cache Statistics",
                "passed": isinstance(stats, dict) and "hit_rate" in stats,
                "data": stats
            })
        except Exception as e:
            results.append({
                "name": "Get Cache Statistics",
                "passed": False,
                "error": str(e)
            })

        # Test 3: Queue task management
        try:
            task_id = performance_manager.queue_manager.add_task(
                task_type="test_task",
                payload={"data": "test_payload"},
                priority="high",
                organization_id=self.organization_id
            )
            results.append({
                "name": "Add Queue Task",
                "passed": bool(task_id),
                "data": {"task_id": task_id}
            })
        except Exception as e:
            results.append({
                "name": "Add Queue Task",
                "passed": False,
                "error": str(e)
            })

        # Test 4: Queue statistics
        try:
            queue_stats = performance_manager.queue_manager.get_queue_stats()
            results.append({
                "name": "Get Queue Statistics",
                "passed": isinstance(queue_stats, dict) and "total_tasks" in queue_stats,
                "data": queue_stats
            })
        except Exception as e:
            results.append({
                "name": "Get Queue Statistics",
                "passed": False,
                "error": str(e)
            })

        # Test 5: Performance metrics
        try:
            metrics = performance_manager.get_performance_metrics(self.organization_id)
            results.append({
                "name": "Get Performance Metrics",
                "passed": isinstance(metrics, list),
                "data": {"metrics_count": len(metrics)}
            })
        except Exception as e:
            results.append({
                "name": "Get Performance Metrics",
                "passed": False,
                "error": str(e)
            })

        return results

    async def test_business_intelligence(self) -> List[Dict[str, Any]]:
        """Test Business Intelligence functionality"""
        results = []
        bi_service = get_business_intelligence_service()

        # Test 1: Track business metric
        try:
            metric_id = bi_service.track_business_metric(
                name="total_revenue",
                value=125000.50,
                unit="USD",
                metric_type=MetricType.FINANCIAL,
                organization_id=self.organization_id,
                target_value=150000.00,
                metadata={"source": "sales_system", "quarter": "Q4"}
            )
            results.append({
                "name": "Track Business Metric",
                "passed": bool(metric_id),
                "data": {"metric_id": metric_id}
            })
        except Exception as e:
            results.append({
                "name": "Track Business Metric",
                "passed": False,
                "error": str(e)
            })

        # Test 2: Get metrics summary
        try:
            summary = bi_service.get_metrics_summary(
                organization_id=self.organization_id,
                metric_types=[MetricType.FINANCIAL],
                period_days=30
            )
            results.append({
                "name": "Get Metrics Summary",
                "passed": isinstance(summary, dict) and "metrics" in summary,
                "data": {"total_metrics": summary.get("summary", {}).get("total_metrics", 0)}
            })
        except Exception as e:
            results.append({
                "name": "Get Metrics Summary",
                "passed": False,
                "error": str(e)
            })

        # Test 3: Create executive dashboard
        try:
            dashboard_id = bi_service.executive_dashboard.create_dashboard(
                name="Executive Dashboard Test",
                organization_id=self.organization_id,
                user_id=self.user_id,
                template_type="executive"
            )
            results.append({
                "name": "Create Executive Dashboard",
                "passed": bool(dashboard_id),
                "data": {"dashboard_id": dashboard_id}
            })
        except Exception as e:
            results.append({
                "name": "Create Executive Dashboard",
                "passed": False,
                "error": str(e)
            })

        # Test 4: Generate executive report
        try:
            report_id = bi_service.generate_executive_report(
                organization_id=self.organization_id,
                report_type="monthly",
                period_start=datetime.utcnow() - timedelta(days=30),
                period_end=datetime.utcnow(),
                user_id=self.user_id,
                format=ReportFormat.PDF
            )
            results.append({
                "name": "Generate Executive Report",
                "passed": bool(report_id),
                "data": {"report_id": report_id}
            })
        except Exception as e:
            results.append({
                "name": "Generate Executive Report",
                "passed": False,
                "error": str(e)
            })

        # Test 5: Predictive analysis
        try:
            analysis = bi_service.create_predictive_analysis(
                organization_id=self.organization_id,
                analysis_type="revenue_forecast",
                data_points=[
                    {"period": "2024-01", "value": 100000},
                    {"period": "2024-02", "value": 110000},
                    {"period": "2024-03", "value": 125000}
                ],
                forecast_periods=6
            )
            results.append({
                "name": "Create Predictive Analysis",
                "passed": isinstance(analysis, dict) and "predictions" in analysis,
                "data": {"forecast_periods": len(analysis.get("predictions", []))}
            })
        except Exception as e:
            results.append({
                "name": "Create Predictive Analysis",
                "passed": False,
                "error": str(e)
            })

        # Test 6: Data warehouse operations
        try:
            # Connect data source
            success = bi_service.data_warehouse.connect_data_source(
                source_name="test_database",
                connection_config={
                    "host": "localhost",
                    "database": "test_db",
                    "type": "postgresql"
                }
            )

            # Schedule ETL job
            job_id = bi_service.data_warehouse.schedule_etl_job(
                job_name="test_etl",
                source_name="test_database",
                target_schema="analytics",
                schedule="daily",
                transformation_rules=[{"type": "aggregate", "field": "revenue"}]
            )

            results.append({
                "name": "Data Warehouse Operations",
                "passed": success and bool(job_id),
                "data": {"job_id": job_id, "connected": success}
            })
        except Exception as e:
            results.append({
                "name": "Data Warehouse Operations",
                "passed": False,
                "error": str(e)
            })

        return results


async def main():
    """Main verification function"""
    verifier = Sprint10Verifier()
    results = await verifier.run_all_tests()

    # Save results to file
    with open("sprint10_verification_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.utcnow().isoformat(),
            "sprint": "Sprint 10 - Enterprise Features",
            "results": results,
            "test_details": verifier.test_results
        }, f, indent=2)

    return results["all_passed"]


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)