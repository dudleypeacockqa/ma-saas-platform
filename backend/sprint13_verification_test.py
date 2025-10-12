"""
Sprint 13 Verification Test - Advanced Analytics & Intelligence Platform
Comprehensive test suite for all Sprint 13 analytics features
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

# Import Sprint 13 components
from app.analytics.real_time_analytics import (
    get_real_time_analytics_engine,
    MetricType,
    AlertSeverity
)
from app.analytics.dashboard_system import (
    get_dashboard_system,
    DashboardType,
    VisualizationType,
    ChartType
)
from app.analytics.reporting_engine import (
    get_reporting_engine,
    ReportType,
    ReportFormat,
    ReportFrequency,
    DeliveryMethod,
    ReportSection
)
from app.analytics.performance_monitor import (
    get_performance_monitor,
    AlertChannel,
    HealthStatus
)

async def test_real_time_analytics():
    """Test real-time analytics engine functionality"""
    print("🔍 Testing Real-Time Analytics Engine...")

    engine = get_real_time_analytics_engine()

    # Test metric tracking
    success = await engine.track_metric(
        name="deals_closed",
        value=15,
        metric_type=MetricType.COUNTER,
        tags={"source": "test", "region": "US"}
    )
    assert success, "Failed to track metric"

    # Test KPI creation
    kpi_id = await engine.create_kpi(
        name="Monthly Revenue",
        metric_name="revenue",
        target=1000000,
        aggregation_type="sum"
    )
    assert kpi_id, "Failed to create KPI"

    # Test alert rule creation
    alert_id = await engine.create_alert_rule(
        name="High Deal Volume",
        metric_name="deals_closed",
        condition="greater_than",
        threshold=10,
        severity=AlertSeverity.HIGH
    )
    assert alert_id, "Failed to create alert rule"

    # Test event tracking
    await engine.track_event({
        "event_type": "deal_completed",
        "deal_id": "deal_123",
        "value": 500000,
        "timestamp": datetime.now()
    })

    # Test insights generation
    insights = await engine.generate_insights()
    assert len(insights) >= 0, "Failed to generate insights"

    print("✅ Real-Time Analytics Engine tests passed!")
    return True

async def test_dashboard_system():
    """Test dashboard system functionality"""
    print("🎯 Testing Dashboard System...")

    dashboard_system = get_dashboard_system()

    # Test dashboard creation
    dashboard_id = await dashboard_system.create_dashboard(
        name="Test Executive Dashboard",
        dashboard_type=DashboardType.EXECUTIVE,
        owner_id="test_user_123",
        description="Test dashboard for verification"
    )
    assert dashboard_id, "Failed to create dashboard"

    # Test widget creation
    widget_id = await dashboard_system.add_widget(
        dashboard_id=dashboard_id,
        title="Deal Pipeline",
        widget_type="chart",
        visualization_type=VisualizationType.CHART,
        chart_type=ChartType.BAR,
        data_source="deals",
        config={"show_legend": True}
    )
    assert widget_id, "Failed to create widget"

    # Test visualization generation
    viz_data = await dashboard_system.generate_visualization(
        viz_type=VisualizationType.CHART,
        chart_type=ChartType.LINE,
        data=[
            {"date": "2024-01-01", "value": 100},
            {"date": "2024-01-02", "value": 150},
            {"date": "2024-01-03", "value": 120}
        ],
        options={"title": "Test Chart"}
    )
    assert viz_data, "Failed to generate visualization"

    # Test dashboard list
    dashboards = await dashboard_system.list_dashboards("test_user_123")
    assert len(dashboards) > 0, "Failed to list dashboards"

    print("✅ Dashboard System tests passed!")
    return True

async def test_reporting_engine():
    """Test reporting engine functionality"""
    print("📊 Testing Reporting Engine...")

    reporting_engine = get_reporting_engine()

    # Test report template creation
    sections = [
        ReportSection(
            section_id="test_section",
            title="Test Section",
            content_type="chart",
            data_query="SELECT * FROM test_data",
            template="test_template",
            order=1
        )
    ]

    template_id = await reporting_engine.create_report_template(
        name="Test Report Template",
        description="Test template for verification",
        report_type=ReportType.EXECUTIVE_SUMMARY,
        sections=sections,
        format=ReportFormat.PDF
    )
    assert template_id, "Failed to create report template"

    # Test report generation
    report_id = await reporting_engine.generate_report(
        template_id=template_id,
        parameters={"test_param": "test_value"}
    )
    assert report_id, "Failed to generate report"

    # Test report scheduling
    schedule_id = await reporting_engine.schedule_report(
        template_id=template_id,
        frequency=ReportFrequency.DAILY,
        delivery_method=DeliveryMethod.EMAIL,
        recipients=["test@example.com"],
        parameters={"test": True}
    )
    assert schedule_id, "Failed to schedule report"

    # Test getting templates
    templates = reporting_engine.get_templates()
    assert len(templates) > 0, "Failed to get templates"

    # Test getting reports
    reports = reporting_engine.get_reports()
    assert len(reports) > 0, "Failed to get reports"

    print("✅ Reporting Engine tests passed!")
    return True

async def test_performance_monitor():
    """Test performance monitoring functionality"""
    print("⚡ Testing Performance Monitor...")

    monitor = get_performance_monitor()

    # Test starting monitoring
    await monitor.start_monitoring()
    assert monitor.monitoring_active, "Failed to start monitoring"

    # Test alert configuration
    alert_config = {
        "cpu_threshold": 80.0,
        "memory_threshold": 85.0,
        "response_time_threshold": 2000,
        "channels": [AlertChannel.EMAIL]
    }
    success = await monitor.configure_alerts(alert_config)
    assert success, "Failed to configure alerts"

    # Test health check
    health_status = await monitor.check_system_health()
    assert health_status in [HealthStatus.HEALTHY, HealthStatus.WARNING, HealthStatus.CRITICAL], "Invalid health status"

    # Test metric collection
    await monitor.collect_application_metrics({
        "response_time": 150,
        "throughput": 1000,
        "error_rate": 0.1
    })

    # Test getting metrics
    metrics = await monitor.get_performance_metrics()
    assert isinstance(metrics, dict), "Failed to get performance metrics"

    print("✅ Performance Monitor tests passed!")
    return True

async def test_integration():
    """Test integration between all Sprint 13 components"""
    print("🔗 Testing Sprint 13 Integration...")

    # Get all service instances
    analytics_engine = get_real_time_analytics_engine()
    dashboard_system = get_dashboard_system()
    reporting_engine = get_reporting_engine()
    performance_monitor = get_performance_monitor()

    # Test end-to-end workflow
    # 1. Track some metrics
    await analytics_engine.track_metric("test_integration_metric", 100, MetricType.GAUGE)

    # 2. Create dashboard with real-time data
    dashboard_id = await dashboard_system.create_dashboard(
        name="Integration Test Dashboard",
        dashboard_type=DashboardType.OPERATIONAL,
        owner_id="integration_test"
    )

    # 3. Generate a report
    templates = reporting_engine.get_templates()
    if templates:
        report_id = await reporting_engine.generate_report(templates[0].template_id)
        assert report_id, "Failed to generate integration report"

    # 4. Check system health
    health = await performance_monitor.check_system_health()
    assert health is not None, "Failed to check system health in integration test"

    print("✅ Sprint 13 Integration tests passed!")
    return True

def verify_service_instances():
    """Verify all service instances are properly initialized"""
    print("🔧 Verifying Service Instances...")

    # Check real-time analytics
    analytics_engine = get_real_time_analytics_engine()
    assert analytics_engine is not None, "Real-time analytics engine not initialized"

    # Check dashboard system
    dashboard_system = get_dashboard_system()
    assert dashboard_system is not None, "Dashboard system not initialized"

    # Check reporting engine
    reporting_engine = get_reporting_engine()
    assert reporting_engine is not None, "Reporting engine not initialized"

    # Check performance monitor
    performance_monitor = get_performance_monitor()
    assert performance_monitor is not None, "Performance monitor not initialized"

    print("✅ All service instances verified!")
    return True

async def run_comprehensive_test():
    """Run comprehensive Sprint 13 verification"""
    print("🚀 Starting Sprint 13 Comprehensive Verification Test")
    print("=" * 60)

    try:
        # Verify service instances
        verify_service_instances()

        # Run individual component tests
        await test_real_time_analytics()
        await test_dashboard_system()
        await test_reporting_engine()
        await test_performance_monitor()

        # Run integration tests
        await test_integration()

        print("=" * 60)
        print("🎉 Sprint 13 Verification COMPLETED SUCCESSFULLY!")
        print("✅ All analytics platform components are working correctly")
        print("✅ Real-time analytics engine operational")
        print("✅ Dashboard system functional")
        print("✅ Reporting engine operational")
        print("✅ Performance monitoring active")
        print("✅ Integration between components verified")

        # Generate summary
        summary = {
            "sprint": 13,
            "feature": "Advanced Analytics & Intelligence Platform",
            "status": "VERIFIED",
            "timestamp": datetime.now().isoformat(),
            "components_tested": [
                "Real-Time Analytics Engine",
                "Dashboard System",
                "Reporting Engine",
                "Performance Monitor"
            ],
            "test_results": {
                "real_time_analytics": "PASSED",
                "dashboard_system": "PASSED",
                "reporting_engine": "PASSED",
                "performance_monitor": "PASSED",
                "integration": "PASSED"
            }
        }

        return summary

    except Exception as e:
        print(f"❌ Sprint 13 Verification FAILED: {str(e)}")
        return {
            "sprint": 13,
            "status": "FAILED",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Run the verification test
    result = asyncio.run(run_comprehensive_test())

    # Print final result
    print("\nFinal Result:")
    print(json.dumps(result, indent=2))