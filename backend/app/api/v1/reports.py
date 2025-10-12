"""
Data Export & Reporting API Endpoints - Sprint 5
Story 5.6: Data Export & Reporting Features
Automated report generation, custom exports, and BI tool integration
"""

import io
import csv
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, Field

from app.core.deps import get_db, get_current_user, get_current_tenant
from app.models.deal import Deal, DealActivity, DealValuation, DealTeamMember
from app.models.documents import Document, DocumentActivity
from app.models.teams import Team, TeamMember, TeamTask
from app.models.negotiations import Negotiation, TermSheet
from app.middleware.permission_middleware import require_permission
from app.core.permissions import ResourceType, Action

router = APIRouter()


# Request Models
class ReportRequest(BaseModel):
    """Base report generation request"""
    report_type: str = Field(..., description="Type of report to generate")
    start_date: Optional[date] = Field(None, description="Start date for report data")
    end_date: Optional[date] = Field(None, description="End date for report data")
    format: str = Field("json", description="Export format: json, csv, excel")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Additional filters")
    include_details: bool = Field(True, description="Include detailed data")


class CustomExportRequest(BaseModel):
    """Custom data export request"""
    data_sources: List[str] = Field(..., description="Data sources to include")
    fields: List[str] = Field(..., description="Specific fields to export")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Data filters")
    format: str = Field("csv", description="Export format")
    email_delivery: bool = Field(False, description="Email report when ready")


class ScheduledReportRequest(BaseModel):
    """Scheduled report configuration"""
    name: str = Field(..., description="Report name")
    report_type: str = Field(..., description="Type of report")
    schedule: str = Field(..., description="Cron schedule expression")
    recipients: List[str] = Field(..., description="Email recipients")
    format: str = Field("pdf", description="Report format")
    active: bool = Field(True, description="Whether schedule is active")


# Response Models
class ReportResponse(BaseModel):
    """Report generation response"""
    report_id: str
    report_type: str
    status: str
    download_url: Optional[str]
    expires_at: Optional[datetime]
    generated_at: datetime
    file_size: Optional[int]


class ExportResponse(BaseModel):
    """Data export response"""
    export_id: str
    status: str
    download_url: Optional[str]
    record_count: int
    file_format: str
    expires_at: Optional[datetime]


# Utility Functions
def deals_to_csv(deals: List[Deal]) -> str:
    """Convert deals data to CSV format"""
    output = io.StringIO()
    writer = csv.writer(output)

    # CSV headers
    headers = [
        'Deal ID', 'Deal Number', 'Title', 'Target Company', 'Deal Type', 'Stage',
        'Priority', 'Deal Value', 'Currency', 'Probability of Close', 'Expected Close Date',
        'Actual Close Date', 'Deal Lead', 'Created Date', 'Last Updated'
    ]
    writer.writerow(headers)

    # Data rows
    for deal in deals:
        writer.writerow([
            str(deal.id),
            deal.deal_number,
            deal.title,
            deal.target_company_name,
            deal.deal_type,
            deal.stage,
            deal.priority,
            float(deal.deal_value) if deal.deal_value else '',
            deal.deal_currency,
            deal.probability_of_close,
            deal.expected_close_date.isoformat() if deal.expected_close_date else '',
            deal.actual_close_date.isoformat() if deal.actual_close_date else '',
            deal.deal_lead_id or '',
            deal.created_at.isoformat(),
            deal.updated_at.isoformat() if deal.updated_at else ''
        ])

    return output.getvalue()


def activities_to_csv(activities: List[DealActivity]) -> str:
    """Convert activities data to CSV format"""
    output = io.StringIO()
    writer = csv.writer(output)

    headers = [
        'Activity ID', 'Deal ID', 'Activity Type', 'Subject', 'Description',
        'Activity Date', 'Created By', 'Participants', 'Outcome'
    ]
    writer.writerow(headers)

    for activity in activities:
        writer.writerow([
            str(activity.id),
            str(activity.deal_id),
            activity.activity_type,
            activity.subject,
            activity.description,
            activity.activity_date.isoformat() if activity.activity_date else '',
            activity.created_by or '',
            ', '.join(activity.participants) if activity.participants else '',
            activity.outcome or ''
        ])

    return output.getvalue()


# Report Generation Endpoints

@router.post("/generate", response_model=ReportResponse)
@require_permission(ResourceType.REPORTS, Action.CREATE)
async def generate_report(
    report_request: ReportRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
) -> ReportResponse:
    """
    Generate a comprehensive report based on request parameters.
    Supports multiple report types and formats.
    """

    # Set default date range if not provided
    end_date = report_request.end_date or date.today()
    start_date = report_request.start_date or (end_date - timedelta(days=90))

    report_id = f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{tenant_id}"

    # Generate report based on type
    if report_request.report_type == "deal_summary":
        data = await generate_deal_summary_report(db, tenant_id, start_date, end_date, report_request.filters)
    elif report_request.report_type == "pipeline_analysis":
        data = await generate_pipeline_analysis_report(db, tenant_id, start_date, end_date)
    elif report_request.report_type == "team_performance":
        data = await generate_team_performance_report(db, tenant_id, start_date, end_date)
    elif report_request.report_type == "financial_summary":
        data = await generate_financial_summary_report(db, tenant_id, start_date, end_date)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported report type: {report_request.report_type}"
        )

    # For this implementation, we'll return the data directly
    # In production, you'd store the report and provide a download URL

    return ReportResponse(
        report_id=report_id,
        report_type=report_request.report_type,
        status="completed",
        download_url=f"/api/v1/reports/{report_id}/download",
        expires_at=datetime.utcnow() + timedelta(hours=24),
        generated_at=datetime.utcnow(),
        file_size=len(str(data))
    )


@router.get("/deals/export")
@require_permission(ResourceType.REPORTS, Action.READ)
async def export_deals(
    format: str = Query("csv", description="Export format: csv, json"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    stage: Optional[str] = Query(None, description="Deal stage filter"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
):
    """
    Export deals data in specified format.
    Supports CSV and JSON formats with filtering.
    """

    # Build query
    query = select(Deal).where(Deal.organization_id == tenant_id)

    if start_date:
        query = query.where(Deal.created_at >= start_date)
    if end_date:
        query = query.where(Deal.created_at <= end_date)
    if stage:
        query = query.where(Deal.stage == stage)

    # Execute query
    result = await db.execute(query)
    deals = result.scalars().all()

    if format.lower() == "csv":
        csv_data = deals_to_csv(deals)

        return StreamingResponse(
            io.StringIO(csv_data),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=deals_export_{date.today()}.csv"}
        )

    elif format.lower() == "json":
        deals_data = [
            {
                "id": str(deal.id),
                "deal_number": deal.deal_number,
                "title": deal.title,
                "target_company": deal.target_company_name,
                "deal_type": deal.deal_type,
                "stage": deal.stage,
                "priority": deal.priority,
                "deal_value": float(deal.deal_value) if deal.deal_value else None,
                "currency": deal.deal_currency,
                "probability_of_close": deal.probability_of_close,
                "expected_close_date": deal.expected_close_date.isoformat() if deal.expected_close_date else None,
                "created_at": deal.created_at.isoformat(),
                "updated_at": deal.updated_at.isoformat() if deal.updated_at else None
            }
            for deal in deals
        ]

        return JSONResponse(
            content={
                "deals": deals_data,
                "total_count": len(deals),
                "exported_at": datetime.utcnow().isoformat()
            },
            headers={"Content-Disposition": f"attachment; filename=deals_export_{date.today()}.json"}
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format}"
        )


@router.get("/activities/export")
@require_permission(ResourceType.REPORTS, Action.READ)
async def export_activities(
    format: str = Query("csv", description="Export format: csv, json"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    activity_type: Optional[str] = Query(None, description="Activity type filter"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
):
    """Export deal activities data"""

    # Build query
    query = select(DealActivity).where(DealActivity.organization_id == tenant_id)

    if start_date:
        query = query.where(DealActivity.activity_date >= start_date)
    if end_date:
        query = query.where(DealActivity.activity_date <= end_date)
    if activity_type:
        query = query.where(DealActivity.activity_type == activity_type)

    # Execute query
    result = await db.execute(query)
    activities = result.scalars().all()

    if format.lower() == "csv":
        csv_data = activities_to_csv(activities)

        return StreamingResponse(
            io.StringIO(csv_data),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=activities_export_{date.today()}.csv"}
        )

    elif format.lower() == "json":
        activities_data = [
            {
                "id": str(activity.id),
                "deal_id": str(activity.deal_id),
                "activity_type": activity.activity_type,
                "subject": activity.subject,
                "description": activity.description,
                "activity_date": activity.activity_date.isoformat() if activity.activity_date else None,
                "created_by": activity.created_by,
                "participants": activity.participants,
                "outcome": activity.outcome
            }
            for activity in activities
        ]

        return JSONResponse(
            content={
                "activities": activities_data,
                "total_count": len(activities),
                "exported_at": datetime.utcnow().isoformat()
            }
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format}"
        )


@router.post("/custom-export", response_model=ExportResponse)
@require_permission(ResourceType.REPORTS, Action.CREATE)
async def create_custom_export(
    export_request: CustomExportRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
) -> ExportResponse:
    """
    Create a custom data export with specified fields and filters.
    Supports complex queries across multiple data sources.
    """

    export_id = f"export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{tenant_id}"

    # Validate data sources
    valid_sources = ['deals', 'activities', 'documents', 'teams', 'negotiations', 'term_sheets']
    invalid_sources = [source for source in export_request.data_sources if source not in valid_sources]

    if invalid_sources:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data sources: {invalid_sources}"
        )

    # For this implementation, we'll simulate the export process
    # In production, you'd execute the custom query and generate the file

    record_count = 0

    # Simulate processing each data source
    for source in export_request.data_sources:
        if source == "deals":
            query = select(func.count(Deal.id)).where(Deal.organization_id == tenant_id)
            result = await db.execute(query)
            record_count += result.scalar() or 0

        elif source == "activities":
            query = select(func.count(DealActivity.id)).where(DealActivity.organization_id == tenant_id)
            result = await db.execute(query)
            record_count += result.scalar() or 0

    return ExportResponse(
        export_id=export_id,
        status="processing",
        download_url=f"/api/v1/reports/exports/{export_id}/download",
        record_count=record_count,
        file_format=export_request.format,
        expires_at=datetime.utcnow() + timedelta(hours=48)
    )


# Report Generation Helper Functions

async def generate_deal_summary_report(
    db: AsyncSession,
    tenant_id: UUID,
    start_date: date,
    end_date: date,
    filters: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate comprehensive deal summary report"""

    query = select(Deal).where(
        Deal.organization_id == tenant_id,
        Deal.created_at >= start_date,
        Deal.created_at <= end_date
    )

    # Apply additional filters
    if filters.get('stage'):
        query = query.where(Deal.stage == filters['stage'])
    if filters.get('deal_type'):
        query = query.where(Deal.deal_type == filters['deal_type'])

    result = await db.execute(query)
    deals = result.scalars().all()

    # Generate summary statistics
    total_deals = len(deals)
    total_value = sum([d.deal_value or 0 for d in deals])
    avg_value = total_value / total_deals if total_deals > 0 else 0

    won_deals = len([d for d in deals if d.stage == 'closed_won'])
    lost_deals = len([d for d in deals if d.stage == 'closed_lost'])
    active_deals = total_deals - won_deals - lost_deals

    return {
        "report_type": "deal_summary",
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "summary": {
            "total_deals": total_deals,
            "total_value": float(total_value),
            "avg_value": float(avg_value),
            "won_deals": won_deals,
            "lost_deals": lost_deals,
            "active_deals": active_deals,
            "win_rate": (won_deals / (won_deals + lost_deals) * 100) if (won_deals + lost_deals) > 0 else 0
        },
        "deals": [
            {
                "id": str(deal.id),
                "title": deal.title,
                "target_company": deal.target_company_name,
                "stage": deal.stage,
                "value": float(deal.deal_value) if deal.deal_value else None,
                "probability": deal.probability_of_close
            }
            for deal in deals
        ]
    }


async def generate_pipeline_analysis_report(
    db: AsyncSession,
    tenant_id: UUID,
    start_date: date,
    end_date: date
) -> Dict[str, Any]:
    """Generate pipeline analysis report"""

    query = select(Deal).where(
        Deal.organization_id == tenant_id,
        Deal.is_active == True
    )

    result = await db.execute(query)
    deals = result.scalars().all()

    # Group by stage
    stage_analysis = {}
    stages = ['sourcing', 'initial_review', 'nda_execution', 'preliminary_analysis',
              'valuation', 'due_diligence', 'negotiation', 'loi_drafting',
              'documentation', 'closing', 'closed_won', 'closed_lost']

    for stage in stages:
        stage_deals = [d for d in deals if d.stage == stage]
        stage_analysis[stage] = {
            "count": len(stage_deals),
            "total_value": float(sum([d.deal_value or 0 for d in stage_deals])),
            "avg_probability": sum([d.probability_of_close or 0 for d in stage_deals]) / len(stage_deals) if stage_deals else 0
        }

    return {
        "report_type": "pipeline_analysis",
        "generated_at": datetime.utcnow().isoformat(),
        "pipeline_overview": {
            "total_active_deals": len(deals),
            "total_pipeline_value": float(sum([d.deal_value or 0 for d in deals]))
        },
        "stage_analysis": stage_analysis
    }


async def generate_team_performance_report(
    db: AsyncSession,
    tenant_id: UUID,
    start_date: date,
    end_date: date
) -> Dict[str, Any]:
    """Generate team performance report"""

    teams_query = select(Team).where(
        Team.organization_id == tenant_id,
        Team.is_active == True
    )

    result = await db.execute(teams_query)
    teams = result.scalars().all()

    team_performance = []

    for team in teams:
        # Get team deals (simplified)
        deals_query = select(Deal).where(
            Deal.organization_id == tenant_id,
            Deal.created_at >= start_date,
            Deal.created_at <= end_date
        )

        deals_result = await db.execute(deals_query)
        deals = deals_result.scalars().all()

        team_performance.append({
            "team_id": str(team.id),
            "team_name": team.name,
            "deals_count": len(deals),
            "total_value": float(sum([d.deal_value or 0 for d in deals])),
            "avg_deal_size": float(sum([d.deal_value or 0 for d in deals]) / len(deals)) if deals else 0
        })

    return {
        "report_type": "team_performance",
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "teams": team_performance
    }


async def generate_financial_summary_report(
    db: AsyncSession,
    tenant_id: UUID,
    start_date: date,
    end_date: date
) -> Dict[str, Any]:
    """Generate financial summary report"""

    # Get deals with financial data
    query = select(Deal).options(
        selectinload(Deal.valuations)
    ).where(
        Deal.organization_id == tenant_id,
        Deal.created_at >= start_date,
        Deal.created_at <= end_date
    )

    result = await db.execute(query)
    deals = result.scalars().all()

    # Financial metrics
    deal_values = [d.deal_value for d in deals if d.deal_value]

    return {
        "report_type": "financial_summary",
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "financial_metrics": {
            "total_deal_value": float(sum(deal_values)) if deal_values else 0,
            "avg_deal_value": float(sum(deal_values) / len(deal_values)) if deal_values else 0,
            "deal_count": len(deals),
            "deals_with_valuation": len([d for d in deals if d.valuations])
        }
    }


@router.get("/templates")
@require_permission(ResourceType.REPORTS, Action.READ)
async def get_report_templates(
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
) -> Dict[str, Any]:
    """
    Get available report templates and their configurations.
    """

    templates = {
        "deal_summary": {
            "name": "Deal Summary Report",
            "description": "Comprehensive overview of deal performance",
            "fields": ["deal_id", "title", "stage", "value", "probability", "close_date"],
            "filters": ["stage", "deal_type", "date_range", "team"]
        },
        "pipeline_analysis": {
            "name": "Pipeline Analysis Report",
            "description": "Detailed analysis of deal pipeline performance",
            "fields": ["stage", "count", "total_value", "avg_time", "conversion_rate"],
            "filters": ["date_range", "deal_type"]
        },
        "team_performance": {
            "name": "Team Performance Report",
            "description": "Team productivity and performance metrics",
            "fields": ["team_name", "deals_count", "total_value", "avg_deal_size"],
            "filters": ["team", "date_range"]
        },
        "financial_summary": {
            "name": "Financial Summary Report",
            "description": "Financial performance and valuation analysis",
            "fields": ["total_value", "avg_value", "valuation_metrics", "roi"],
            "filters": ["date_range", "deal_type", "stage"]
        }
    }

    return {
        "templates": templates,
        "available_formats": ["json", "csv", "excel", "pdf"],
        "max_export_records": 10000
    }