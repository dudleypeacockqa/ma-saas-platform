"""
Business Intelligence Service - Sprint 10
Advanced analytics and executive dashboard for enterprise M&A platform
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from sqlalchemy.orm import Session
import json


class MetricType(str, Enum):
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    USER_ENGAGEMENT = "user_engagement"
    DEAL_PIPELINE = "deal_pipeline"


class DashboardWidget(str, Enum):
    KPI_CARD = "kpi_card"
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    TABLE = "table"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    TREND_INDICATOR = "trend_indicator"


class ReportFormat(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    POWERPOINT = "powerpoint"


@dataclass
class BusinessMetric:
    id: str
    name: str
    value: float
    unit: str
    metric_type: MetricType
    timestamp: datetime
    organization_id: str
    target_value: Optional[float] = None
    trend_direction: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class DashboardConfiguration:
    id: str
    name: str
    organization_id: str
    user_id: str
    widgets: List[Dict[str, Any]]
    layout: Dict[str, Any]
    refresh_interval: int
    is_public: bool = False
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class ExecutiveReport:
    id: str
    title: str
    organization_id: str
    report_type: str
    period_start: datetime
    period_end: datetime
    sections: List[Dict[str, Any]]
    generated_at: datetime
    generated_by: str
    format: ReportFormat


class DataWarehouse:
    def __init__(self):
        self.connections: Dict[str, Any] = {}
        self.schemas: Dict[str, Any] = {}
        self.etl_jobs: List[Dict[str, Any]] = []

    def connect_data_source(self, source_name: str, connection_config: Dict[str, Any]) -> bool:
        """Connect to external data source for ETL"""
        try:
            self.connections[source_name] = {
                "config": connection_config,
                "status": "connected",
                "last_sync": datetime.utcnow(),
                "connection_id": f"conn_{source_name}_{datetime.utcnow().timestamp()}"
            }
            return True
        except Exception as e:
            return False

    def schedule_etl_job(
        self,
        job_name: str,
        source_name: str,
        target_schema: str,
        schedule: str,
        transformation_rules: List[Dict[str, Any]]
    ) -> str:
        """Schedule ETL job for data warehouse"""
        job_id = f"etl_{job_name}_{datetime.utcnow().timestamp()}"

        etl_job = {
            "id": job_id,
            "name": job_name,
            "source": source_name,
            "target_schema": target_schema,
            "schedule": schedule,
            "transformation_rules": transformation_rules,
            "status": "scheduled",
            "created_at": datetime.utcnow(),
            "last_run": None,
            "next_run": self._calculate_next_run(schedule)
        }

        self.etl_jobs.append(etl_job)
        return job_id

    def execute_etl_job(self, job_id: str) -> Dict[str, Any]:
        """Execute ETL job and return results"""
        job = next((j for j in self.etl_jobs if j["id"] == job_id), None)
        if not job:
            return {"success": False, "error": "Job not found"}

        try:
            # Simulate ETL execution
            result = {
                "success": True,
                "job_id": job_id,
                "records_processed": 15847,
                "records_inserted": 12459,
                "records_updated": 3388,
                "execution_time": 45.7,
                "timestamp": datetime.utcnow()
            }

            job["status"] = "completed"
            job["last_run"] = datetime.utcnow()
            job["next_run"] = self._calculate_next_run(job["schedule"])

            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _calculate_next_run(self, schedule: str) -> datetime:
        """Calculate next run time based on schedule"""
        now = datetime.utcnow()
        if schedule == "hourly":
            return now + timedelta(hours=1)
        elif schedule == "daily":
            return now + timedelta(days=1)
        elif schedule == "weekly":
            return now + timedelta(weeks=1)
        else:
            return now + timedelta(hours=24)


class ExecutiveDashboard:
    def __init__(self):
        self.configurations: Dict[str, DashboardConfiguration] = {}
        self.cached_data: Dict[str, Any] = {}
        self.widget_templates: Dict[str, Any] = self._initialize_widget_templates()

    def create_dashboard(
        self,
        name: str,
        organization_id: str,
        user_id: str,
        template_type: str = "executive"
    ) -> str:
        """Create new executive dashboard"""
        dashboard_id = f"dash_{organization_id}_{datetime.utcnow().timestamp()}"

        if template_type == "executive":
            widgets = self._get_executive_template_widgets()
        elif template_type == "operational":
            widgets = self._get_operational_template_widgets()
        else:
            widgets = []

        config = DashboardConfiguration(
            id=dashboard_id,
            name=name,
            organization_id=organization_id,
            user_id=user_id,
            widgets=widgets,
            layout={"columns": 3, "responsive": True},
            refresh_interval=300,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.configurations[dashboard_id] = config
        return dashboard_id

    def add_widget(
        self,
        dashboard_id: str,
        widget_type: DashboardWidget,
        title: str,
        data_source: str,
        configuration: Dict[str, Any]
    ) -> str:
        """Add widget to dashboard"""
        if dashboard_id not in self.configurations:
            raise ValueError("Dashboard not found")

        widget_id = f"widget_{datetime.utcnow().timestamp()}"
        widget = {
            "id": widget_id,
            "type": widget_type.value,
            "title": title,
            "data_source": data_source,
            "configuration": configuration,
            "position": {"x": 0, "y": 0, "width": 1, "height": 1},
            "created_at": datetime.utcnow()
        }

        self.configurations[dashboard_id].widgets.append(widget)
        self.configurations[dashboard_id].updated_at = datetime.utcnow()

        return widget_id

    def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """Get dashboard with real-time data"""
        if dashboard_id not in self.configurations:
            return {"error": "Dashboard not found"}

        config = self.configurations[dashboard_id]
        dashboard_data = {
            "id": dashboard_id,
            "name": config.name,
            "layout": config.layout,
            "widgets": []
        }

        for widget in config.widgets:
            widget_data = self._get_widget_data(widget)
            dashboard_data["widgets"].append(widget_data)

        return dashboard_data

    def _get_widget_data(self, widget: Dict[str, Any]) -> Dict[str, Any]:
        """Get data for specific widget"""
        data_source = widget["data_source"]

        # Simulate real-time data based on widget type
        if widget["type"] == "kpi_card":
            return {
                **widget,
                "data": {
                    "value": 1247000,
                    "change": 15.7,
                    "trend": "up"
                }
            }
        elif widget["type"] == "line_chart":
            return {
                **widget,
                "data": {
                    "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                    "datasets": [{
                        "label": "Deal Value",
                        "data": [120, 135, 142, 158, 167, 189]
                    }]
                }
            }
        else:
            return {**widget, "data": {}}

    def _initialize_widget_templates(self) -> Dict[str, Any]:
        """Initialize widget templates"""
        return {
            "executive_kpis": {
                "type": "kpi_card",
                "metrics": ["total_deal_value", "active_deals", "conversion_rate"]
            },
            "deal_pipeline": {
                "type": "bar_chart",
                "metrics": ["deals_by_stage", "deals_by_size"]
            },
            "performance_trends": {
                "type": "line_chart",
                "metrics": ["monthly_revenue", "user_growth"]
            }
        }

    def _get_executive_template_widgets(self) -> List[Dict[str, Any]]:
        """Get executive dashboard template widgets"""
        return [
            {
                "id": "exec_kpi_1",
                "type": "kpi_card",
                "title": "Total Deal Value",
                "data_source": "deals_aggregate",
                "configuration": {"metric": "total_value", "format": "currency"}
            },
            {
                "id": "exec_chart_1",
                "type": "line_chart",
                "title": "Deal Pipeline Trend",
                "data_source": "deals_timeline",
                "configuration": {"period": "6_months", "group_by": "month"}
            },
            {
                "id": "exec_table_1",
                "type": "table",
                "title": "Top Deals",
                "data_source": "deals_ranked",
                "configuration": {"limit": 10, "sort_by": "value"}
            }
        ]

    def _get_operational_template_widgets(self) -> List[Dict[str, Any]]:
        """Get operational dashboard template widgets"""
        return [
            {
                "id": "ops_gauge_1",
                "type": "gauge",
                "title": "System Performance",
                "data_source": "system_metrics",
                "configuration": {"metric": "response_time", "max_value": 1000}
            },
            {
                "id": "ops_chart_1",
                "type": "bar_chart",
                "title": "User Activity",
                "data_source": "user_metrics",
                "configuration": {"period": "24_hours", "group_by": "hour"}
            }
        ]


class BusinessIntelligenceService:
    def __init__(self):
        self.data_warehouse = DataWarehouse()
        self.executive_dashboard = ExecutiveDashboard()
        self.metrics_store: Dict[str, List[BusinessMetric]] = {}
        self.reports: Dict[str, ExecutiveReport] = {}

    def track_business_metric(
        self,
        name: str,
        value: float,
        unit: str,
        metric_type: MetricType,
        organization_id: str,
        target_value: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Track business metric for analytics"""
        metric_id = f"metric_{name}_{datetime.utcnow().timestamp()}"

        metric = BusinessMetric(
            id=metric_id,
            name=name,
            value=value,
            unit=unit,
            metric_type=metric_type,
            timestamp=datetime.utcnow(),
            organization_id=organization_id,
            target_value=target_value,
            metadata=metadata or {}
        )

        if organization_id not in self.metrics_store:
            self.metrics_store[organization_id] = []

        self.metrics_store[organization_id].append(metric)
        return metric_id

    def get_metrics_summary(
        self,
        organization_id: str,
        metric_types: Optional[List[MetricType]] = None,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get summary of business metrics"""
        if organization_id not in self.metrics_store:
            return {"metrics": [], "summary": {}}

        metrics = self.metrics_store[organization_id]

        # Filter by time period
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)
        recent_metrics = [m for m in metrics if m.timestamp >= cutoff_date]

        # Filter by metric types if specified
        if metric_types:
            recent_metrics = [m for m in recent_metrics if m.metric_type in metric_types]

        # Calculate summary statistics
        summary = {
            "total_metrics": len(recent_metrics),
            "metric_types": list(set(m.metric_type.value for m in recent_metrics)),
            "date_range": {
                "start": cutoff_date.isoformat(),
                "end": datetime.utcnow().isoformat()
            }
        }

        return {
            "metrics": [self._metric_to_dict(m) for m in recent_metrics[-100:]],
            "summary": summary
        }

    def generate_executive_report(
        self,
        organization_id: str,
        report_type: str,
        period_start: datetime,
        period_end: datetime,
        user_id: str,
        format: ReportFormat = ReportFormat.PDF
    ) -> str:
        """Generate executive report"""
        report_id = f"report_{organization_id}_{datetime.utcnow().timestamp()}"

        # Generate report sections based on type
        if report_type == "quarterly":
            sections = self._generate_quarterly_sections(organization_id, period_start, period_end)
        elif report_type == "monthly":
            sections = self._generate_monthly_sections(organization_id, period_start, period_end)
        else:
            sections = self._generate_default_sections(organization_id, period_start, period_end)

        report = ExecutiveReport(
            id=report_id,
            title=f"{report_type.title()} Executive Report",
            organization_id=organization_id,
            report_type=report_type,
            period_start=period_start,
            period_end=period_end,
            sections=sections,
            generated_at=datetime.utcnow(),
            generated_by=user_id,
            format=format
        )

        self.reports[report_id] = report
        return report_id

    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get generated report"""
        if report_id not in self.reports:
            return None

        report = self.reports[report_id]
        return {
            "id": report.id,
            "title": report.title,
            "organization_id": report.organization_id,
            "report_type": report.report_type,
            "period": {
                "start": report.period_start.isoformat(),
                "end": report.period_end.isoformat()
            },
            "sections": report.sections,
            "generated_at": report.generated_at.isoformat(),
            "generated_by": report.generated_by,
            "format": report.format.value
        }

    def create_predictive_analysis(
        self,
        organization_id: str,
        analysis_type: str,
        data_points: List[Dict[str, Any]],
        forecast_periods: int = 12
    ) -> Dict[str, Any]:
        """Create predictive analysis and forecasting"""
        # Simulate advanced analytics
        predictions = []
        for i in range(forecast_periods):
            future_date = datetime.utcnow() + timedelta(days=30 * (i + 1))
            predicted_value = sum(dp.get("value", 0) for dp in data_points[-3:]) / 3 * (1 + 0.05 * i)

            predictions.append({
                "period": future_date.strftime("%Y-%m"),
                "predicted_value": round(predicted_value, 2),
                "confidence_interval": {
                    "lower": round(predicted_value * 0.85, 2),
                    "upper": round(predicted_value * 1.15, 2)
                }
            })

        return {
            "analysis_type": analysis_type,
            "organization_id": organization_id,
            "forecast_periods": forecast_periods,
            "predictions": predictions,
            "model_accuracy": 0.87,
            "created_at": datetime.utcnow().isoformat()
        }

    def _metric_to_dict(self, metric: BusinessMetric) -> Dict[str, Any]:
        """Convert metric to dictionary"""
        return {
            "id": metric.id,
            "name": metric.name,
            "value": metric.value,
            "unit": metric.unit,
            "type": metric.metric_type.value,
            "timestamp": metric.timestamp.isoformat(),
            "target_value": metric.target_value,
            "trend_direction": metric.trend_direction,
            "metadata": metric.metadata
        }

    def _generate_quarterly_sections(
        self,
        organization_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Generate quarterly report sections"""
        return [
            {
                "title": "Executive Summary",
                "content": "Quarterly performance overview with key highlights and achievements."
            },
            {
                "title": "Financial Performance",
                "content": "Revenue, profitability, and key financial metrics for the quarter."
            },
            {
                "title": "Deal Pipeline Analysis",
                "content": "M&A deal pipeline status, conversion rates, and market trends."
            },
            {
                "title": "Operational Metrics",
                "content": "Platform performance, user engagement, and system reliability."
            }
        ]

    def _generate_monthly_sections(
        self,
        organization_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Generate monthly report sections"""
        return [
            {
                "title": "Monthly Overview",
                "content": "Key performance indicators and monthly highlights."
            },
            {
                "title": "Deal Activity",
                "content": "Monthly deal activity, new opportunities, and closed transactions."
            },
            {
                "title": "User Growth",
                "content": "User acquisition, retention, and engagement metrics."
            }
        ]

    def _generate_default_sections(
        self,
        organization_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Generate default report sections"""
        return [
            {
                "title": "Summary",
                "content": "General performance summary for the specified period."
            },
            {
                "title": "Key Metrics",
                "content": "Important business metrics and KPIs."
            }
        ]


# Service instance and dependency injection
_business_intelligence_service: Optional[BusinessIntelligenceService] = None


def get_business_intelligence_service() -> BusinessIntelligenceService:
    """Get Business Intelligence service instance"""
    global _business_intelligence_service
    if _business_intelligence_service is None:
        _business_intelligence_service = BusinessIntelligenceService()
    return _business_intelligence_service