"""
Enterprise API endpoints - Sprint 10
Advanced integrations and enterprise features for the M&A SaaS platform
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.enterprise import (
    get_integrations_hub, get_enterprise_admin_service,
    get_performance_manager, get_business_intelligence_service,
    IntegrationProvider, MetricType, DashboardWidget, ReportFormat
)

router = APIRouter()


# Integrations Hub Endpoints
@router.post("/integrations/configure")
async def configure_integration(
    integration_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Configure new integration"""
    hub = get_integrations_hub()

    provider = IntegrationProvider(integration_data.get("provider"))
    config = integration_data.get("config", {})

    result = await hub.configure_integration(
        provider=provider,
        organization_id=current_user.organization_id,
        config=config
    )

    return {"integration_id": result, "status": "configured"}


@router.get("/integrations")
async def list_integrations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List active integrations"""
    hub = get_integrations_hub()
    integrations = hub.list_integrations(current_user.organization_id)
    return {"integrations": integrations}


@router.post("/integrations/{integration_id}/sync")
async def sync_integration(
    integration_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync data with integration"""
    hub = get_integrations_hub()

    # Add sync task to background
    background_tasks.add_task(
        hub.sync_integration,
        integration_id,
        current_user.organization_id
    )

    return {"message": "Sync initiated", "integration_id": integration_id}


@router.delete("/integrations/{integration_id}")
async def remove_integration(
    integration_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove integration"""
    hub = get_integrations_hub()

    success = hub.remove_integration(integration_id, current_user.organization_id)
    if not success:
        raise HTTPException(status_code=404, detail="Integration not found")

    return {"message": "Integration removed"}


@router.get("/integrations/{integration_id}/health")
async def check_integration_health(
    integration_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check integration health status"""
    hub = get_integrations_hub()

    health = hub.check_integration_health(integration_id, current_user.organization_id)
    return health


# Enterprise Administration Endpoints
@router.post("/admin/audit-events")
async def record_audit_event(
    event_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record audit event"""
    admin_service = get_enterprise_admin_service()

    event_id = admin_service.compliance_manager.record_audit_event(
        event_type=event_data.get("event_type"),
        user_id=str(current_user.id),
        organization_id=current_user.organization_id,
        resource_type=event_data.get("resource_type"),
        resource_id=event_data.get("resource_id"),
        action=event_data.get("action"),
        details=event_data.get("details", {})
    )

    return {"audit_event_id": event_id}


@router.get("/admin/audit-trail")
async def get_audit_trail(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    event_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audit trail"""
    admin_service = get_enterprise_admin_service()

    trail = admin_service.compliance_manager.get_audit_trail(
        organization_id=current_user.organization_id,
        start_date=start_date,
        end_date=end_date,
        event_type=event_type,
        resource_type=resource_type
    )

    return {"audit_trail": trail}


@router.post("/admin/compliance-report")
async def generate_compliance_report(
    report_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate compliance report"""
    admin_service = get_enterprise_admin_service()

    report_id = admin_service.compliance_manager.generate_compliance_report(
        organization_id=current_user.organization_id,
        framework=report_data.get("framework"),
        period_start=datetime.fromisoformat(report_data.get("period_start")),
        period_end=datetime.fromisoformat(report_data.get("period_end"))
    )

    return {"report_id": report_id}


@router.get("/admin/compliance-report/{report_id}")
async def get_compliance_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get compliance report"""
    admin_service = get_enterprise_admin_service()

    report = admin_service.compliance_manager.get_compliance_report(
        report_id,
        current_user.organization_id
    )

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return report


@router.post("/admin/white-label/configure")
async def configure_white_label(
    config_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Configure white-label settings"""
    admin_service = get_enterprise_admin_service()

    config_id = admin_service.configure_white_label(
        organization_id=current_user.organization_id,
        branding=config_data.get("branding", {}),
        domain=config_data.get("domain"),
        features=config_data.get("features", {})
    )

    return {"config_id": config_id}


@router.get("/admin/white-label")
async def get_white_label_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get white-label configuration"""
    admin_service = get_enterprise_admin_service()

    config = admin_service.get_white_label_config(current_user.organization_id)
    return config


# Performance Management Endpoints
@router.get("/performance/cache/stats")
async def get_cache_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get cache performance statistics"""
    performance_manager = get_performance_manager()

    stats = performance_manager.cache_manager.get_cache_stats()
    return stats


@router.post("/performance/cache/clear")
async def clear_cache(
    cache_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear cache entries"""
    performance_manager = get_performance_manager()

    if cache_data.get("pattern"):
        cleared = performance_manager.cache_manager.clear_pattern(
            cache_data["pattern"]
        )
    else:
        cleared = performance_manager.cache_manager.clear_all()

    return {"cleared_entries": cleared}


@router.get("/performance/queue/stats")
async def get_queue_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get queue performance statistics"""
    performance_manager = get_performance_manager()

    stats = performance_manager.queue_manager.get_queue_stats()
    return stats


@router.post("/performance/queue/add-task")
async def add_queue_task(
    task_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add task to processing queue"""
    performance_manager = get_performance_manager()

    task_id = performance_manager.queue_manager.add_task(
        task_type=task_data.get("task_type"),
        payload=task_data.get("payload", {}),
        priority=task_data.get("priority", "normal"),
        organization_id=current_user.organization_id
    )

    return {"task_id": task_id}


@router.get("/performance/queue/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get task status"""
    performance_manager = get_performance_manager()

    status = performance_manager.queue_manager.get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")

    return status


@router.get("/performance/metrics")
async def get_performance_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get performance metrics"""
    performance_manager = get_performance_manager()

    metrics = performance_manager.get_performance_metrics(current_user.organization_id)
    return metrics


# Business Intelligence Endpoints
@router.post("/bi/metrics")
async def track_business_metric(
    metric_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track business metric"""
    bi_service = get_business_intelligence_service()

    metric_id = bi_service.track_business_metric(
        name=metric_data.get("name"),
        value=metric_data.get("value"),
        unit=metric_data.get("unit"),
        metric_type=MetricType(metric_data.get("metric_type")),
        organization_id=current_user.organization_id,
        target_value=metric_data.get("target_value"),
        metadata=metric_data.get("metadata", {})
    )

    return {"metric_id": metric_id}


@router.get("/bi/metrics/summary")
async def get_metrics_summary(
    metric_types: Optional[List[str]] = None,
    period_days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get business metrics summary"""
    bi_service = get_business_intelligence_service()

    types = [MetricType(t) for t in metric_types] if metric_types else None

    summary = bi_service.get_metrics_summary(
        organization_id=current_user.organization_id,
        metric_types=types,
        period_days=period_days
    )

    return summary


@router.post("/bi/dashboards")
async def create_dashboard(
    dashboard_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create executive dashboard"""
    bi_service = get_business_intelligence_service()

    dashboard_id = bi_service.executive_dashboard.create_dashboard(
        name=dashboard_data.get("name"),
        organization_id=current_user.organization_id,
        user_id=str(current_user.id),
        template_type=dashboard_data.get("template_type", "executive")
    )

    return {"dashboard_id": dashboard_id}


@router.get("/bi/dashboards/{dashboard_id}")
async def get_dashboard(
    dashboard_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard with data"""
    bi_service = get_business_intelligence_service()

    dashboard = bi_service.executive_dashboard.get_dashboard_data(dashboard_id)

    if "error" in dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    return dashboard


@router.post("/bi/dashboards/{dashboard_id}/widgets")
async def add_dashboard_widget(
    dashboard_id: str,
    widget_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add widget to dashboard"""
    bi_service = get_business_intelligence_service()

    widget_id = bi_service.executive_dashboard.add_widget(
        dashboard_id=dashboard_id,
        widget_type=DashboardWidget(widget_data.get("widget_type")),
        title=widget_data.get("title"),
        data_source=widget_data.get("data_source"),
        configuration=widget_data.get("configuration", {})
    )

    return {"widget_id": widget_id}


@router.post("/bi/reports")
async def generate_executive_report(
    report_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate executive report"""
    bi_service = get_business_intelligence_service()

    report_id = bi_service.generate_executive_report(
        organization_id=current_user.organization_id,
        report_type=report_data.get("report_type"),
        period_start=datetime.fromisoformat(report_data.get("period_start")),
        period_end=datetime.fromisoformat(report_data.get("period_end")),
        user_id=str(current_user.id),
        format=ReportFormat(report_data.get("format", "pdf"))
    )

    return {"report_id": report_id}


@router.get("/bi/reports/{report_id}")
async def get_executive_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get executive report"""
    bi_service = get_business_intelligence_service()

    report = bi_service.get_report(report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return report


@router.post("/bi/predictive-analysis")
async def create_predictive_analysis(
    analysis_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create predictive analysis"""
    bi_service = get_business_intelligence_service()

    analysis = bi_service.create_predictive_analysis(
        organization_id=current_user.organization_id,
        analysis_type=analysis_data.get("analysis_type"),
        data_points=analysis_data.get("data_points", []),
        forecast_periods=analysis_data.get("forecast_periods", 12)
    )

    return analysis


# Data Warehouse Endpoints
@router.post("/bi/warehouse/connect")
async def connect_data_source(
    connection_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Connect external data source"""
    bi_service = get_business_intelligence_service()

    success = bi_service.data_warehouse.connect_data_source(
        source_name=connection_data.get("source_name"),
        connection_config=connection_data.get("config", {})
    )

    return {"success": success, "source_name": connection_data.get("source_name")}


@router.post("/bi/warehouse/etl-jobs")
async def schedule_etl_job(
    job_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Schedule ETL job"""
    bi_service = get_business_intelligence_service()

    job_id = bi_service.data_warehouse.schedule_etl_job(
        job_name=job_data.get("job_name"),
        source_name=job_data.get("source_name"),
        target_schema=job_data.get("target_schema"),
        schedule=job_data.get("schedule"),
        transformation_rules=job_data.get("transformation_rules", [])
    )

    return {"job_id": job_id}


@router.post("/bi/warehouse/etl-jobs/{job_id}/execute")
async def execute_etl_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute ETL job"""
    bi_service = get_business_intelligence_service()

    result = bi_service.data_warehouse.execute_etl_job(job_id)
    return result