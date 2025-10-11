"""
Pipeline Analytics API Endpoints
Story 2.3: Pipeline Analytics API - Advanced metrics and insights
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta, date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, case, distinct, extract
from sqlalchemy.orm import selectinload

from app.core.deps import get_db, get_current_user, get_current_tenant
from app.models.deal import Deal

router = APIRouter()


@router.get("/pipeline/velocity")
async def get_pipeline_velocity(
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
    period_days: int = Query(90, description="Period for velocity calculation"),
    group_by: str = Query("month", description="Grouping period: day, week, month"),
) -> Dict[str, Any]:
    """
    Calculate pipeline velocity metrics - how fast deals move through stages.
    Returns average time in each stage and conversion rates.
    """

    cutoff_date = datetime.utcnow() - timedelta(days=period_days)

    # Get all deals in the period
    query = select(Deal).where(
        Deal.organization_id == tenant_id,
        Deal.created_at >= cutoff_date
    )
    result = await db.execute(query)
    deals = result.scalars().all()

    # Calculate stage durations (simplified - would need stage history in production)
    stage_durations = {}
    stage_counts = {}

    for deal in deals:
        stage = deal.stage
        if stage not in stage_durations:
            stage_durations[stage] = []
            stage_counts[stage] = 0

        # Calculate days since creation or last update
        days_in_stage = (deal.updated_at - deal.created_at).days
        stage_durations[stage].append(days_in_stage)
        stage_counts[stage] += 1

    # Calculate averages
    velocity_metrics = {
        "period_days": period_days,
        "stages": {},
        "total_deals": len(deals),
        "avg_cycle_time": 0,
        "fastest_deals": [],
        "slowest_deals": [],
    }

    total_cycle_time = 0
    cycle_times = []

    for stage, durations in stage_durations.items():
        if durations:
            avg_duration = sum(durations) / len(durations)
            velocity_metrics["stages"][stage] = {
                "avg_days": round(avg_duration, 1),
                "deal_count": stage_counts[stage],
                "min_days": min(durations),
                "max_days": max(durations),
            }

            if stage in ['closed_won', 'closed_lost']:
                cycle_times.extend(durations)

    # Calculate overall cycle time
    if cycle_times:
        velocity_metrics["avg_cycle_time"] = round(sum(cycle_times) / len(cycle_times), 1)

        # Find fastest and slowest deals
        sorted_deals = sorted(
            [(d, (d.updated_at - d.created_at).days) for d in deals if d.stage in ['closed_won', 'closed_lost']],
            key=lambda x: x[1]
        )

        if sorted_deals:
            velocity_metrics["fastest_deals"] = [
                {"id": str(d.id), "title": d.title, "days": days}
                for d, days in sorted_deals[:3]
            ]
            velocity_metrics["slowest_deals"] = [
                {"id": str(d.id), "title": d.title, "days": days}
                for d, days in sorted_deals[-3:]
            ]

    return velocity_metrics


@router.get("/pipeline/conversion-funnel")
async def get_conversion_funnel(
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
    period_days: int = Query(90, description="Period for funnel analysis"),
) -> Dict[str, Any]:
    """
    Get conversion funnel showing drop-off rates between stages.
    """

    cutoff_date = datetime.utcnow() - timedelta(days=period_days)

    # Define funnel stages in order
    funnel_stages = [
        'sourcing',
        'initial_review',
        'nda_execution',
        'preliminary_analysis',
        'valuation',
        'due_diligence',
        'negotiation',
        'loi_drafting',
        'documentation',
        'closing',
        'closed_won'
    ]

    # Count deals that reached each stage
    stage_counts = {}

    for stage in funnel_stages:
        count_query = select(func.count(Deal.id)).where(
            Deal.organization_id == tenant_id,
            Deal.created_at >= cutoff_date,
            # In a real system, we'd check if the deal ever reached this stage
            # For now, we count current stage and assume linear progression
            Deal.stage.in_(funnel_stages[funnel_stages.index(stage):])
        )
        result = await db.execute(count_query)
        stage_counts[stage] = result.scalar() or 0

    # Calculate conversion rates
    funnel_data = {
        "period_days": period_days,
        "stages": [],
        "overall_conversion": 0,
    }

    for i, stage in enumerate(funnel_stages):
        stage_data = {
            "stage": stage,
            "count": stage_counts[stage],
            "percentage": 100.0,
            "conversion_rate": 0,
            "drop_off_rate": 0,
        }

        if i == 0 and stage_counts[stage] > 0:
            stage_data["percentage"] = 100.0
        elif i > 0 and stage_counts[funnel_stages[0]] > 0:
            stage_data["percentage"] = (stage_counts[stage] / stage_counts[funnel_stages[0]]) * 100

            if stage_counts[funnel_stages[i-1]] > 0:
                stage_data["conversion_rate"] = (stage_counts[stage] / stage_counts[funnel_stages[i-1]]) * 100
                stage_data["drop_off_rate"] = 100 - stage_data["conversion_rate"]

        funnel_data["stages"].append(stage_data)

    # Overall conversion rate
    if stage_counts['sourcing'] > 0:
        funnel_data["overall_conversion"] = (stage_counts['closed_won'] / stage_counts['sourcing']) * 100

    return funnel_data


@router.get("/pipeline/trends")
async def get_pipeline_trends(
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
    period_days: int = Query(90, description="Period for trend analysis"),
    interval: str = Query("week", description="Interval: day, week, month"),
) -> Dict[str, Any]:
    """
    Get pipeline trends over time - new deals, closures, value changes.
    """

    cutoff_date = datetime.utcnow() - timedelta(days=period_days)

    # Determine grouping based on interval
    if interval == "day":
        date_trunc = func.date_trunc('day', Deal.created_at)
    elif interval == "week":
        date_trunc = func.date_trunc('week', Deal.created_at)
    else:  # month
        date_trunc = func.date_trunc('month', Deal.created_at)

    # Get deal creation trends
    creation_query = select(
        date_trunc.label('period'),
        func.count(Deal.id).label('new_deals'),
        func.sum(Deal.deal_value).label('new_value'),
        func.avg(Deal.probability_of_close).label('avg_probability')
    ).where(
        Deal.organization_id == tenant_id,
        Deal.created_at >= cutoff_date
    ).group_by(date_trunc).order_by(date_trunc)

    result = await db.execute(creation_query)
    creation_trends = result.all()

    # Get closure trends
    closure_query = select(
        date_trunc.label('period'),
        func.count(case((Deal.stage == 'closed_won', 1))).label('wins'),
        func.count(case((Deal.stage == 'closed_lost', 1))).label('losses'),
        func.sum(case((Deal.stage == 'closed_won', Deal.deal_value), else_=0)).label('won_value')
    ).where(
        Deal.organization_id == tenant_id,
        Deal.updated_at >= cutoff_date,
        Deal.stage.in_(['closed_won', 'closed_lost'])
    ).group_by(date_trunc).order_by(date_trunc)

    closure_result = await db.execute(closure_query)
    closure_trends = closure_result.all()

    # Build response
    trends = {
        "period_days": period_days,
        "interval": interval,
        "creation_trends": [],
        "closure_trends": [],
        "summary": {
            "total_new_deals": 0,
            "total_closures": 0,
            "total_won_value": 0,
            "win_rate": 0,
        }
    }

    # Process creation trends
    for trend in creation_trends:
        trends["creation_trends"].append({
            "period": trend.period.isoformat() if trend.period else None,
            "new_deals": trend.new_deals,
            "new_value": float(trend.new_value or 0),
            "avg_probability": float(trend.avg_probability or 0),
        })
        trends["summary"]["total_new_deals"] += trend.new_deals

    # Process closure trends
    total_wins = 0
    total_losses = 0

    for trend in closure_trends:
        trends["closure_trends"].append({
            "period": trend.period.isoformat() if trend.period else None,
            "wins": trend.wins,
            "losses": trend.losses,
            "won_value": float(trend.won_value or 0),
            "win_rate": (trend.wins / (trend.wins + trend.losses) * 100) if (trend.wins + trend.losses) > 0 else 0,
        })
        total_wins += trend.wins
        total_losses += trend.losses
        trends["summary"]["total_won_value"] += float(trend.won_value or 0)

    trends["summary"]["total_closures"] = total_wins + total_losses
    if trends["summary"]["total_closures"] > 0:
        trends["summary"]["win_rate"] = (total_wins / trends["summary"]["total_closures"]) * 100

    return trends


@router.get("/pipeline/performance-by-owner")
async def get_performance_by_owner(
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
    period_days: int = Query(90, description="Period for performance analysis"),
) -> Dict[str, Any]:
    """
    Get pipeline performance metrics grouped by deal owner.
    """

    cutoff_date = datetime.utcnow() - timedelta(days=period_days)

    # Get performance by deal lead
    owner_query = select(
        Deal.deal_lead_id,
        func.count(Deal.id).label('total_deals'),
        func.count(case((Deal.stage == 'closed_won', 1))).label('wins'),
        func.count(case((Deal.stage == 'closed_lost', 1))).label('losses'),
        func.sum(Deal.deal_value).label('total_value'),
        func.sum(case((Deal.stage == 'closed_won', Deal.deal_value), else_=0)).label('won_value'),
        func.avg(Deal.probability_of_close).label('avg_probability'),
        func.avg(extract('epoch', Deal.updated_at - Deal.created_at) / 86400).label('avg_cycle_days')
    ).where(
        Deal.organization_id == tenant_id,
        Deal.created_at >= cutoff_date,
        Deal.deal_lead_id.isnot(None)
    ).group_by(Deal.deal_lead_id)

    result = await db.execute(owner_query)
    owner_performance = result.all()

    # Build response
    performance_data = {
        "period_days": period_days,
        "by_owner": [],
        "top_performers": {
            "by_volume": [],
            "by_value": [],
            "by_win_rate": [],
        }
    }

    owner_metrics = []

    for perf in owner_performance:
        win_rate = 0
        if perf.wins + perf.losses > 0:
            win_rate = (perf.wins / (perf.wins + perf.losses)) * 100

        metrics = {
            "owner_id": str(perf.deal_lead_id) if perf.deal_lead_id else "unassigned",
            "total_deals": perf.total_deals,
            "wins": perf.wins,
            "losses": perf.losses,
            "win_rate": round(win_rate, 1),
            "total_value": float(perf.total_value or 0),
            "won_value": float(perf.won_value or 0),
            "avg_probability": float(perf.avg_probability or 0),
            "avg_cycle_days": round(float(perf.avg_cycle_days or 0), 1),
        }

        performance_data["by_owner"].append(metrics)
        owner_metrics.append(metrics)

    # Identify top performers
    if owner_metrics:
        # Sort by different metrics
        by_volume = sorted(owner_metrics, key=lambda x: x["total_deals"], reverse=True)[:3]
        by_value = sorted(owner_metrics, key=lambda x: x["won_value"], reverse=True)[:3]
        by_win_rate = sorted([m for m in owner_metrics if m["wins"] + m["losses"] >= 3],
                           key=lambda x: x["win_rate"], reverse=True)[:3]

        performance_data["top_performers"]["by_volume"] = by_volume
        performance_data["top_performers"]["by_value"] = by_value
        performance_data["top_performers"]["by_win_rate"] = by_win_rate

    return performance_data


@router.get("/pipeline/health-score")
async def get_pipeline_health_score(
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
) -> Dict[str, Any]:
    """
    Calculate overall pipeline health score based on various metrics.
    """

    # Get current pipeline state
    current_deals_query = select(
        func.count(Deal.id).label('total_active'),
        func.sum(Deal.deal_value).label('total_value'),
        func.avg(Deal.probability_of_close).label('avg_probability'),
        func.count(case((Deal.is_overdue == True, 1))).label('overdue_count'),
        func.count(case((Deal.stage == 'on_hold', 1))).label('on_hold_count')
    ).where(
        Deal.organization_id == tenant_id,
        Deal.is_active == True,
        ~Deal.stage.in_(['closed_won', 'closed_lost'])
    )

    result = await db.execute(current_deals_query)
    current_state = result.one()

    # Get recent performance (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    recent_query = select(
        func.count(case((Deal.stage == 'closed_won', 1))).label('recent_wins'),
        func.count(case((Deal.stage == 'closed_lost', 1))).label('recent_losses'),
        func.count(case((Deal.created_at >= thirty_days_ago, 1))).label('new_deals_30d')
    ).where(
        Deal.organization_id == tenant_id,
        Deal.updated_at >= thirty_days_ago
    )

    recent_result = await db.execute(recent_query)
    recent_performance = recent_result.one()

    # Calculate health score (0-100)
    health_score = 100
    issues = []
    recommendations = []

    # Check pipeline balance
    if current_state.total_active < 10:
        health_score -= 20
        issues.append("Low number of active deals")
        recommendations.append("Focus on lead generation and sourcing")
    elif current_state.total_active > 100:
        health_score -= 10
        issues.append("Pipeline may be overcrowded")
        recommendations.append("Review and qualify deals more strictly")

    # Check win rate
    total_recent_closed = recent_performance.recent_wins + recent_performance.recent_losses
    if total_recent_closed > 0:
        win_rate = (recent_performance.recent_wins / total_recent_closed) * 100
        if win_rate < 20:
            health_score -= 25
            issues.append("Low win rate")
            recommendations.append("Review qualification criteria and sales process")
        elif win_rate < 40:
            health_score -= 10
            issues.append("Below average win rate")
            recommendations.append("Focus on deal quality over quantity")

    # Check overdue deals
    if current_state.total_active > 0:
        overdue_percentage = (current_state.overdue_count / current_state.total_active) * 100
        if overdue_percentage > 20:
            health_score -= 15
            issues.append("High number of overdue deals")
            recommendations.append("Review and update stalled deals")

    # Check new deal flow
    if recent_performance.new_deals_30d < 5:
        health_score -= 15
        issues.append("Low new deal flow")
        recommendations.append("Increase sourcing and prospecting activities")

    # Check on-hold deals
    if current_state.total_active > 0:
        on_hold_percentage = (current_state.on_hold_count / current_state.total_active) * 100
        if on_hold_percentage > 15:
            health_score -= 10
            issues.append("Too many deals on hold")
            recommendations.append("Re-engage or close on-hold deals")

    # Ensure score is within bounds
    health_score = max(0, min(100, health_score))

    # Determine health status
    if health_score >= 80:
        status = "excellent"
        status_color = "success"
    elif health_score >= 60:
        status = "good"
        status_color = "info"
    elif health_score >= 40:
        status = "fair"
        status_color = "warning"
    else:
        status = "needs attention"
        status_color = "error"

    return {
        "health_score": health_score,
        "status": status,
        "status_color": status_color,
        "metrics": {
            "active_deals": current_state.total_active,
            "total_value": float(current_state.total_value or 0),
            "avg_probability": float(current_state.avg_probability or 0),
            "overdue_deals": current_state.overdue_count,
            "on_hold_deals": current_state.on_hold_count,
            "recent_wins": recent_performance.recent_wins,
            "recent_losses": recent_performance.recent_losses,
            "new_deals_30d": recent_performance.new_deals_30d,
        },
        "issues": issues,
        "recommendations": recommendations,
    }