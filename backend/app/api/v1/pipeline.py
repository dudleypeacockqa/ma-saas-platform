"""
Pipeline Board API Endpoints
Story 2.1: Pipeline Board Backend - Stage management and real-time updates
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, case, distinct
from sqlalchemy.orm import selectinload

from app.core.deps import get_db, get_current_user, get_current_tenant
from app.models.deal import Deal
from app.schemas.deal import DealStageUpdate, DealResponse

router = APIRouter()


# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, tenant_id: str):
        await websocket.accept()
        if tenant_id not in self.active_connections:
            self.active_connections[tenant_id] = []
        self.active_connections[tenant_id].append(websocket)

    def disconnect(self, websocket: WebSocket, tenant_id: str):
        if tenant_id in self.active_connections:
            self.active_connections[tenant_id].remove(websocket)
            if not self.active_connections[tenant_id]:
                del self.active_connections[tenant_id]

    async def broadcast_to_tenant(self, message: dict, tenant_id: str):
        if tenant_id in self.active_connections:
            for connection in self.active_connections[tenant_id]:
                try:
                    await connection.send_json(message)
                except:
                    # Remove dead connections
                    self.disconnect(connection, tenant_id)


manager = ConnectionManager()


@router.get("/board", response_model=Dict[str, List[DealResponse]])
async def get_pipeline_board(
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
    include_closed: bool = Query(False, description="Include closed deals"),
    assigned_to: Optional[UUID] = Query(None, description="Filter by assigned user"),
    priority: Optional[List[str]] = Query(None, description="Filter by priority"),
    days_back: Optional[int] = Query(30, description="Days of history to include"),
) -> Dict[str, List[DealResponse]]:
    """
    Get all deals organized by pipeline stage for Kanban board view.
    Returns a dictionary with stages as keys and lists of deals as values.
    """

    # Build base query
    query = select(Deal).where(
        Deal.organization_id == tenant_id,
        Deal.is_active == True
    )

    # Apply filters
    if not include_closed:
        query = query.where(
            ~Deal.stage.in_(['closed_won', 'closed_lost'])
        )

    if assigned_to:
        query = query.where(
            or_(
                Deal.deal_lead_id == assigned_to,
                Deal.sponsor_id == assigned_to
            )
        )

    if priority:
        query = query.where(Deal.priority.in_(priority))

    if days_back:
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        query = query.where(
            or_(
                Deal.updated_at >= cutoff_date,
                Deal.stage.in_(['sourcing', 'initial_review', 'nda_execution'])
            )
        )

    # Order by priority and updated date
    priority_order = case(
        (Deal.priority == 'critical', 1),
        (Deal.priority == 'high', 2),
        (Deal.priority == 'medium', 3),
        (Deal.priority == 'low', 4),
        else_=5
    )

    query = query.order_by(priority_order, Deal.updated_at.desc())

    # Execute query
    result = await db.execute(query)
    deals = result.scalars().all()

    # Organize by stage
    pipeline_board = {
        'sourcing': [],
        'initial_review': [],
        'nda_execution': [],
        'preliminary_analysis': [],
        'valuation': [],
        'due_diligence': [],
        'negotiation': [],
        'loi_drafting': [],
        'documentation': [],
        'closing': [],
        'closed_won': [],
        'closed_lost': [],
        'on_hold': []
    }

    for deal in deals:
        deal_dict = DealResponse.model_validate(deal)
        pipeline_board[deal.stage].append(deal_dict)

    return pipeline_board


@router.post("/board/move", response_model=DealResponse)
async def move_deal_stage(
    deal_id: UUID,
    stage_update: DealStageUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
) -> DealResponse:
    """
    Move a deal to a different stage in the pipeline.
    Broadcasts the change to all connected clients for real-time updates.
    """

    # Get the deal
    query = select(Deal).where(
        Deal.id == deal_id,
        Deal.organization_id == tenant_id
    )
    result = await db.execute(query)
    deal = result.scalar_one_or_none()

    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )

    # Store old stage for logging
    old_stage = deal.stage

    # Update deal stage
    deal.stage = stage_update.stage
    if stage_update.probability_of_close is not None:
        deal.probability_of_close = stage_update.probability_of_close

    # Update timestamps based on stage
    if stage_update.stage == 'closed_won':
        deal.actual_close_date = datetime.utcnow().date()
        if not deal.probability_of_close or deal.probability_of_close < 100:
            deal.probability_of_close = 100
    elif stage_update.stage == 'closed_lost':
        deal.actual_close_date = datetime.utcnow().date()
        deal.probability_of_close = 0

    # Update modified metadata
    deal.updated_at = datetime.utcnow()
    deal.updated_by = UUID(current_user.get('id', str(tenant_id)))

    # Save changes
    await db.commit()
    await db.refresh(deal)

    # Prepare response
    response = DealResponse.model_validate(deal)

    # Broadcast update to all connected clients in the same tenant
    await manager.broadcast_to_tenant(
        {
            "type": "stage_change",
            "deal_id": str(deal_id),
            "old_stage": old_stage,
            "new_stage": stage_update.stage,
            "deal": response.model_dump(mode='json'),
            "user": current_user.get('email'),
            "timestamp": datetime.utcnow().isoformat()
        },
        str(tenant_id)
    )

    return response


@router.get("/board/statistics")
async def get_pipeline_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
    period_days: int = Query(30, description="Period for statistics in days"),
) -> Dict[str, Any]:
    """
    Get pipeline statistics including conversion rates, velocity, and bottlenecks.
    """

    cutoff_date = datetime.utcnow() - timedelta(days=period_days)

    # Count deals by stage
    stage_counts_query = select(
        Deal.stage,
        func.count(Deal.id).label('count'),
        func.avg(Deal.probability_of_close).label('avg_probability'),
        func.sum(Deal.deal_value).label('total_value')
    ).where(
        Deal.organization_id == tenant_id,
        Deal.is_active == True,
        Deal.created_at >= cutoff_date
    ).group_by(Deal.stage)

    result = await db.execute(stage_counts_query)
    stage_stats = result.all()

    # Calculate average time in each stage
    # This would require stage history tracking - simplified for now
    velocity_query = select(
        func.avg(
            func.extract('epoch', Deal.updated_at - Deal.created_at) / 86400
        ).label('avg_days_in_pipeline'),
        func.count(
            case((Deal.stage == 'closed_won', 1))
        ).label('wins'),
        func.count(
            case((Deal.stage == 'closed_lost', 1))
        ).label('losses')
    ).where(
        Deal.organization_id == tenant_id,
        Deal.created_at >= cutoff_date
    )

    velocity_result = await db.execute(velocity_query)
    velocity_stats = velocity_result.one()

    # Build statistics response
    statistics = {
        "period_days": period_days,
        "stages": {},
        "conversion_rate": 0,
        "avg_days_in_pipeline": float(velocity_stats.avg_days_in_pipeline or 0),
        "total_deals": 0,
        "total_value": 0,
        "bottlenecks": []
    }

    total_deals = 0
    for stage_stat in stage_stats:
        statistics["stages"][stage_stat.stage] = {
            "count": stage_stat.count,
            "avg_probability": float(stage_stat.avg_probability or 0),
            "total_value": float(stage_stat.total_value or 0)
        }
        total_deals += stage_stat.count
        statistics["total_value"] += float(stage_stat.total_value or 0)

    statistics["total_deals"] = total_deals

    # Calculate conversion rate
    if velocity_stats.wins + velocity_stats.losses > 0:
        statistics["conversion_rate"] = (
            velocity_stats.wins / (velocity_stats.wins + velocity_stats.losses) * 100
        )

    # Identify bottlenecks (stages with high deal counts)
    avg_deals_per_stage = total_deals / len(statistics["stages"]) if statistics["stages"] else 0
    for stage, stats in statistics["stages"].items():
        if stats["count"] > avg_deals_per_stage * 1.5:
            statistics["bottlenecks"].append({
                "stage": stage,
                "count": stats["count"],
                "severity": "high" if stats["count"] > avg_deals_per_stage * 2 else "medium"
            })

    return statistics


@router.websocket("/board/ws/{tenant_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    WebSocket endpoint for real-time pipeline updates.
    Clients connect to receive live updates when deals move between stages.
    """
    await manager.connect(websocket, tenant_id)

    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "tenant_id": tenant_id,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_json()

            # Handle ping/pong for connection health
            if data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, tenant_id)
        # Notify other clients about disconnection if needed
    except Exception as e:
        manager.disconnect(websocket, tenant_id)
        print(f"WebSocket error: {e}")


@router.post("/board/bulk-move")
async def bulk_move_deals(
    deal_ids: List[UUID],
    target_stage: str,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant),
) -> Dict[str, Any]:
    """
    Move multiple deals to the same stage at once.
    Useful for bulk operations and cleanup.
    """

    # Validate stage
    valid_stages = [
        'sourcing', 'initial_review', 'nda_execution', 'preliminary_analysis',
        'valuation', 'due_diligence', 'negotiation', 'loi_drafting',
        'documentation', 'closing', 'closed_won', 'closed_lost', 'on_hold'
    ]

    if target_stage not in valid_stages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid stage: {target_stage}"
        )

    # Get all deals
    query = select(Deal).where(
        Deal.id.in_(deal_ids),
        Deal.organization_id == tenant_id
    )
    result = await db.execute(query)
    deals = result.scalars().all()

    if not deals:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No deals found"
        )

    # Update all deals
    updated_deals = []
    for deal in deals:
        old_stage = deal.stage
        deal.stage = target_stage
        deal.updated_at = datetime.utcnow()
        deal.updated_by = UUID(current_user.get('id', str(tenant_id)))

        updated_deals.append({
            "id": str(deal.id),
            "title": deal.title,
            "old_stage": old_stage,
            "new_stage": target_stage
        })

    # Save changes
    await db.commit()

    # Broadcast bulk update
    await manager.broadcast_to_tenant(
        {
            "type": "bulk_stage_change",
            "deals": updated_deals,
            "user": current_user.get('email'),
            "timestamp": datetime.utcnow().isoformat()
        },
        str(tenant_id)
    )

    return {
        "success": True,
        "updated_count": len(updated_deals),
        "deals": updated_deals
    }