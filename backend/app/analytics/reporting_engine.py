"""
Reporting Engine - Sprint 13
Advanced automated reporting, template management, and report generation for M&A platform
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import json

class ReportType(Enum):
    EXECUTIVE_SUMMARY = "executive_summary"
    FINANCIAL_ANALYSIS = "financial_analysis"
    DEAL_PIPELINE = "deal_pipeline"
    PERFORMANCE_METRICS = "performance_metrics"
    USER_ACTIVITY = "user_activity"
    AI_INSIGHTS = "ai_insights"
    MARKET_INTELLIGENCE = "market_intelligence"
    COMPLIANCE = "compliance"
    CUSTOM = "custom"

class ReportFormat(Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    HTML = "html"
    POWERPOINT = "powerpoint"

class ReportFrequency(Enum):
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    ON_DEMAND = "on_demand"

class DeliveryMethod(Enum):
    EMAIL = "email"
    DASHBOARD = "dashboard"
    API = "api"
    FILE_SYSTEM = "file_system"
    CLOUD_STORAGE = "cloud_storage"

class ReportStatus(Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    SCHEDULED = "scheduled"

@dataclass
class ReportSection:
    """Individual section within a report"""
    section_id: str
    title: str
    content_type: str  # chart, table, text, image
    data_query: str
    template: str
    order: int
    options: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ReportTemplate:
    """Report template definition"""
    template_id: str
    name: str
    description: str
    report_type: ReportType
    sections: List[ReportSection]
    format: ReportFormat
    style_config: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class ReportSchedule:
    """Report generation schedule"""
    schedule_id: str
    report_template_id: str
    frequency: ReportFrequency
    delivery_method: DeliveryMethod
    recipients: List[str]
    parameters: Dict[str, Any] = field(default_factory=dict)
    next_run: Optional[datetime] = None
    is_active: bool = True
    created_by: str = ""

@dataclass
class GeneratedReport:
    """Generated report instance"""
    report_id: str
    template_id: str
    title: str
    generated_at: datetime
    status: ReportStatus
    format: ReportFormat
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    generation_time: Optional[float] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

@dataclass
class ReportData:
    """Data for report generation"""
    section_id: str
    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

class TemplateManager:
    """Manages report templates and their lifecycle"""

    def __init__(self):
        self.templates = {}
        self._initialize_default_templates()

    def create_template(self, name: str, description: str, report_type: ReportType,
                       sections: List[ReportSection], format: ReportFormat) -> str:
        """Create a new report template"""
        template_id = f"tmpl_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        template = ReportTemplate(
            template_id=template_id,
            name=name,
            description=description,
            report_type=report_type,
            sections=sections,
            format=format
        )

        self.templates[template_id] = template
        return template_id

    def get_template(self, template_id: str) -> Optional[ReportTemplate]:
        """Get template by ID"""
        return self.templates.get(template_id)

    def list_templates(self, report_type: Optional[ReportType] = None) -> List[ReportTemplate]:
        """List available templates"""
        templates = list(self.templates.values())

        if report_type:
            templates = [t for t in templates if t.report_type == report_type]

        return templates

    def update_template(self, template_id: str, updates: Dict[str, Any]) -> bool:
        """Update template configuration"""
        if template_id not in self.templates:
            return False

        template = self.templates[template_id]
        for key, value in updates.items():
            if hasattr(template, key):
                setattr(template, key, value)

        template.updated_at = datetime.now()
        return True

    def _initialize_default_templates(self):
        """Initialize default report templates"""

        # Executive Summary Template
        exec_sections = [
            ReportSection(
                section_id="exec_kpis",
                title="Key Performance Indicators",
                content_type="chart",
                data_query="SELECT * FROM kpi_summary",
                template="kpi_grid",
                order=1
            ),
            ReportSection(
                section_id="exec_deals",
                title="Deal Pipeline Overview",
                content_type="chart",
                data_query="SELECT * FROM deal_pipeline",
                template="pipeline_chart",
                order=2
            ),
            ReportSection(
                section_id="exec_insights",
                title="AI-Generated Insights",
                content_type="text",
                data_query="SELECT * FROM ai_insights",
                template="insights_list",
                order=3
            )
        ]

        self.create_template(
            name="Executive Summary",
            description="High-level executive overview with KPIs and insights",
            report_type=ReportType.EXECUTIVE_SUMMARY,
            sections=exec_sections,
            format=ReportFormat.PDF
        )

        # Financial Analysis Template
        financial_sections = [
            ReportSection(
                section_id="fin_metrics",
                title="Financial Metrics",
                content_type="table",
                data_query="SELECT * FROM financial_metrics",
                template="financial_table",
                order=1
            ),
            ReportSection(
                section_id="fin_trends",
                title="Revenue Trends",
                content_type="chart",
                data_query="SELECT * FROM revenue_trends",
                template="trend_chart",
                order=2
            ),
            ReportSection(
                section_id="fin_analysis",
                title="Financial Analysis",
                content_type="text",
                data_query="SELECT * FROM financial_analysis",
                template="analysis_text",
                order=3
            )
        ]

        self.create_template(
            name="Financial Analysis Report",
            description="Comprehensive financial metrics and analysis",
            report_type=ReportType.FINANCIAL_ANALYSIS,
            sections=financial_sections,
            format=ReportFormat.EXCEL
        )

class ReportGenerator:
    """Generates reports from templates and data"""

    def __init__(self):
        self.generation_queue = []
        self.active_generations = {}
        self.completed_reports = {}
        self.generation_stats = {
            "reports_generated": 0,
            "total_generation_time": 0.0,
            "failed_generations": 0
        }

    async def generate_report(self, template_id: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Generate a report from template"""
        report_id = f"rpt_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Create report instance
        report = GeneratedReport(
            report_id=report_id,
            template_id=template_id,
            title=f"Report {report_id}",
            generated_at=datetime.now(),
            status=ReportStatus.GENERATING,
            format=ReportFormat.PDF,  # Default
            parameters=parameters or {}
        )

        self.active_generations[report_id] = report

        try:
            # Simulate report generation
            start_time = datetime.now()

            # Generate report content
            report_content = await self._generate_report_content(template_id, parameters or {})

            # Generate file
            file_path = await self._generate_report_file(report, report_content)

            # Update report status
            generation_time = (datetime.now() - start_time).total_seconds()
            report.status = ReportStatus.COMPLETED
            report.file_path = file_path
            report.generation_time = generation_time
            report.file_size = len(str(report_content))  # Simplified

            # Move to completed reports
            self.completed_reports[report_id] = report
            del self.active_generations[report_id]

            # Update stats
            self.generation_stats["reports_generated"] += 1
            self.generation_stats["total_generation_time"] += generation_time

            return report_id

        except Exception as e:
            # Handle generation failure
            report.status = ReportStatus.FAILED
            report.error_message = str(e)
            self.completed_reports[report_id] = report
            del self.active_generations[report_id]
            self.generation_stats["failed_generations"] += 1

            return report_id

    async def _generate_report_content(self, template_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report content from template"""
        # Simulate data fetching and processing
        content = {
            "title": f"Generated Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "sections": [],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "template_id": template_id,
                "parameters": parameters
            }
        }

        # Simulate section generation
        sections = [
            {
                "title": "Executive Summary",
                "content": "This report provides comprehensive insights into current M&A activities...",
                "charts": ["kpi_overview", "deal_pipeline"],
                "data": {"total_deals": 150, "active_deals": 45, "completed_deals": 105}
            },
            {
                "title": "Key Metrics",
                "content": "Performance metrics for the current period...",
                "tables": ["financial_summary", "performance_metrics"],
                "data": {"revenue": 2500000, "growth_rate": 15.5, "success_rate": 87.3}
            },
            {
                "title": "AI Insights",
                "content": "AI-generated insights and recommendations...",
                "insights": [
                    "Deal completion rate increased by 12% this quarter",
                    "Technology sector shows highest growth potential",
                    "Recommend focusing on mid-market opportunities"
                ]
            }
        ]

        content["sections"] = sections
        return content

    async def _generate_report_file(self, report: GeneratedReport, content: Dict[str, Any]) -> str:
        """Generate report file in specified format"""
        # Simulate file generation
        file_name = f"{report.report_id}.{report.format.value}"
        file_path = f"/reports/{file_name}"

        # In production, this would generate actual files
        # For now, we'll just simulate the process

        return file_path

    def get_report(self, report_id: str) -> Optional[GeneratedReport]:
        """Get generated report by ID"""
        if report_id in self.completed_reports:
            return self.completed_reports[report_id]
        elif report_id in self.active_generations:
            return self.active_generations[report_id]
        return None

    def list_reports(self, limit: int = 50) -> List[GeneratedReport]:
        """List generated reports"""
        all_reports = list(self.completed_reports.values()) + list(self.active_generations.values())
        return sorted(all_reports, key=lambda r: r.generated_at, reverse=True)[:limit]

    def get_generation_stats(self) -> Dict[str, Any]:
        """Get report generation statistics"""
        avg_generation_time = 0
        if self.generation_stats["reports_generated"] > 0:
            avg_generation_time = (
                self.generation_stats["total_generation_time"] /
                self.generation_stats["reports_generated"]
            )

        return {
            **self.generation_stats,
            "average_generation_time": avg_generation_time,
            "active_generations": len(self.active_generations),
            "completed_reports": len(self.completed_reports)
        }

class ReportingEngine:
    """Central reporting engine coordinating all reporting operations"""

    def __init__(self):
        self.template_manager = TemplateManager()
        self.report_generator = ReportGenerator()
        self.schedules = {}
        self.delivery_queue = []
        self.reporting_stats = {
            "templates_created": 0,
            "reports_scheduled": 0,
            "reports_delivered": 0
        }

    async def create_report_template(self, name: str, description: str,
                                   report_type: ReportType, sections: List[ReportSection],
                                   format: ReportFormat) -> str:
        """Create a new report template"""
        template_id = self.template_manager.create_template(
            name, description, report_type, sections, format
        )
        self.reporting_stats["templates_created"] += 1
        return template_id

    async def generate_report(self, template_id: str,
                            parameters: Optional[Dict[str, Any]] = None) -> str:
        """Generate a report from template"""
        return await self.report_generator.generate_report(template_id, parameters)

    async def schedule_report(self, template_id: str, frequency: ReportFrequency,
                            delivery_method: DeliveryMethod, recipients: List[str],
                            parameters: Optional[Dict[str, Any]] = None) -> str:
        """Schedule recurring report generation"""
        schedule_id = f"sched_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Calculate next run time
        next_run = self._calculate_next_run(frequency)

        schedule = ReportSchedule(
            schedule_id=schedule_id,
            report_template_id=template_id,
            frequency=frequency,
            delivery_method=delivery_method,
            recipients=recipients,
            parameters=parameters or {},
            next_run=next_run
        )

        self.schedules[schedule_id] = schedule
        self.reporting_stats["reports_scheduled"] += 1
        return schedule_id

    async def process_scheduled_reports(self):
        """Process scheduled reports that are due"""
        now = datetime.now()

        for schedule in self.schedules.values():
            if (schedule.is_active and schedule.next_run and
                schedule.next_run <= now):

                # Generate report
                report_id = await self.generate_report(
                    schedule.report_template_id,
                    schedule.parameters
                )

                # Queue for delivery
                await self._queue_for_delivery(report_id, schedule)

                # Update next run time
                schedule.next_run = self._calculate_next_run(schedule.frequency)

    async def _queue_for_delivery(self, report_id: str, schedule: ReportSchedule):
        """Queue report for delivery"""
        delivery_item = {
            "report_id": report_id,
            "schedule_id": schedule.schedule_id,
            "delivery_method": schedule.delivery_method,
            "recipients": schedule.recipients,
            "queued_at": datetime.now()
        }

        self.delivery_queue.append(delivery_item)

    def _calculate_next_run(self, frequency: ReportFrequency) -> datetime:
        """Calculate next run time based on frequency"""
        now = datetime.now()

        if frequency == ReportFrequency.HOURLY:
            return now + timedelta(hours=1)
        elif frequency == ReportFrequency.DAILY:
            return now + timedelta(days=1)
        elif frequency == ReportFrequency.WEEKLY:
            return now + timedelta(weeks=1)
        elif frequency == ReportFrequency.MONTHLY:
            return now + timedelta(days=30)
        elif frequency == ReportFrequency.QUARTERLY:
            return now + timedelta(days=90)
        elif frequency == ReportFrequency.ANNUALLY:
            return now + timedelta(days=365)

        return now + timedelta(hours=1)  # Default

    def get_templates(self, report_type: Optional[ReportType] = None) -> List[ReportTemplate]:
        """Get available report templates"""
        return self.template_manager.list_templates(report_type)

    def get_reports(self, limit: int = 50) -> List[GeneratedReport]:
        """Get generated reports"""
        return self.report_generator.list_reports(limit)

    def get_schedules(self) -> List[ReportSchedule]:
        """Get report schedules"""
        return list(self.schedules.values())

    def get_reporting_stats(self) -> Dict[str, Any]:
        """Get comprehensive reporting statistics"""
        generator_stats = self.report_generator.get_generation_stats()

        return {
            **self.reporting_stats,
            **generator_stats,
            "active_schedules": len([s for s in self.schedules.values() if s.is_active]),
            "pending_deliveries": len(self.delivery_queue),
            "total_templates": len(self.template_manager.templates)
        }

# Singleton instance
_reporting_engine_instance: Optional[ReportingEngine] = None

def get_reporting_engine() -> ReportingEngine:
    """Get the singleton Reporting Engine instance"""
    global _reporting_engine_instance
    if _reporting_engine_instance is None:
        _reporting_engine_instance = ReportingEngine()
    return _reporting_engine_instance