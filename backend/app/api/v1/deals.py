"""
Deal API endpoints with CRUD operations and multi-tenant support.
Story 1.1: Deal Creation API - Endpoint Implementation
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import (
    get_current_user,
    get_db,
    require_permission,
    get_current_tenant
)
from app.core.security import verify_tenant_access
from app.models.deal import Deal, DealTeamMember
from app.schemas.deal import (
    DealCreate,
    DealUpdate,
    DealResponse,
    DealListResponse,
    DealFilters,
    DealStageUpdate,
    DealBulkOperation,
    DealStatistics
)
from app.services.deal import DealService
from app.services.activity import ActivityService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/deals", tags=["deals"])


@router.post("/", response_model=DealResponse, status_code=status.HTTP_201_CREATED)
async def create_deal(
    deal_data: DealCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant)
) -> DealResponse:
    """
    Create a new deal with the provided information.

    Requires authentication and tenant context.
    """
    try:
        # Initialize service
        deal_service = DealService(db)

        # Generate deal number
        deal_number = await deal_service.generate_deal_number(tenant_id)

        # Create deal instance
        deal = Deal(
            **deal_data.model_dump(exclude_unset=True),
            deal_number=deal_number,
            organization_id=tenant_id,
            created_by=current_user["id"],
            updated_by=current_user["id"]
        )

        # Save to database
        db.add(deal)
        await db.commit()
        await db.refresh(deal)

        # Log activity
        activity_service = ActivityService(db)
        await activity_service.log_activity(
            deal_id=deal.id,
            activity_type="deal_created",
            subject=f"Deal '{deal.title}' created",
            description=f"New deal created in stage {deal.stage}",
            user_id=current_user["id"]
        )

        # Return response
        return DealResponse.model_validate(deal)

    except Exception as e:
        logger.error(f"Error creating deal: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create deal: {str(e)}"
        )


@router.get("/", response_model=DealListResponse)
async def list_deals(
    filters: DealFilters = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant)
) -> DealListResponse:
    """
    List deals with filtering, sorting, and pagination.

    Returns only deals the current user has access to view.
    """
    try:
        # Build query
        query = select(Deal).where(
            and_(
                Deal.organization_id == tenant_id,
                Deal.is_deleted == False
            )
        )

        # Apply filters
        if filters.stage:
            query = query.where(Deal.stage.in_(filters.stage))

        if filters.priority:
            query = query.where(Deal.priority.in_(filters.priority))

        if filters.deal_type:
            query = query.where(Deal.deal_type.in_(filters.deal_type))

        if filters.min_value is not None:
            query = query.where(Deal.deal_value >= filters.min_value)

        if filters.max_value is not None:
            query = query.where(Deal.deal_value <= filters.max_value)

        if filters.deal_lead_id:
            query = query.where(Deal.deal_lead_id == filters.deal_lead_id)

        if filters.is_active is not None:
            query = query.where(Deal.is_active == filters.is_active)

        if filters.expected_close_date_from:
            query = query.where(Deal.expected_close_date >= filters.expected_close_date_from)

        if filters.expected_close_date_to:
            query = query.where(Deal.expected_close_date <= filters.expected_close_date_to)

        if filters.probability_min is not None:
            query = query.where(Deal.probability_of_close >= filters.probability_min)

        if filters.probability_max is not None:
            query = query.where(Deal.probability_of_close <= filters.probability_max)

        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    Deal.title.ilike(search_term),
                    Deal.target_company_name.ilike(search_term),
                    Deal.code_name.ilike(search_term)
                )
            )

        if filters.tags:
            query = query.where(Deal.tags.overlap(filters.tags))

        # Count total before pagination
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply sorting
        sort_column = getattr(Deal, filters.sort_by, Deal.created_at)
        if filters.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)

        # Apply pagination
        offset = (filters.page - 1) * filters.per_page
        query = query.limit(filters.per_page).offset(offset)

        # Include relationships
        query = query.options(
            selectinload(Deal.deal_lead),
            selectinload(Deal.sponsor),
            selectinload(Deal.team_members)
        )

        # Execute query
        result = await db.execute(query)
        deals = result.scalars().all()

        # Build response
        response_deals = []
        for deal in deals:
            deal_dict = DealResponse.model_validate(deal)
            deal_dict.team_members_count = await db.scalar(
                select(func.count(DealTeamMember.id)).where(
                    and_(
                        DealTeamMember.deal_id == deal.id,
                        DealTeamMember.is_active == True
                    )
                )
            )
            response_deals.append(deal_dict)

        return DealListResponse(
            data=response_deals,
            pagination={
                "page": filters.page,
                "per_page": filters.per_page,
                "total": total,
                "pages": (total + filters.per_page - 1) // filters.per_page
            },
            filters=filters.model_dump(exclude_unset=True)
        )

    except Exception as e:
        logger.error(f"Error listing deals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list deals: {str(e)}"
        )


@router.get("/{deal_id}", response_model=DealResponse)
async def get_deal(
    deal_id: UUID = Path(..., description="Deal ID"),
    include: Optional[List[str]] = Query(None, description="Include related data"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant)
) -> DealResponse:
    """
    Get a specific deal by ID with optional related data.

    Includes team members, activities, and documents if requested.
    """
    try:
        # Build query with relationships
        query = select(Deal).where(
            and_(
                Deal.id == deal_id,
                Deal.organization_id == tenant_id,
                Deal.is_deleted == False
            )
        )

        # Optionally include relationships
        if include:
            if "team" in include:
                query = query.options(selectinload(Deal.team_members))
            if "activities" in include:
                query = query.options(selectinload(Deal.activities))
            if "documents" in include:
                query = query.options(selectinload(Deal.documents))

        result = await db.execute(query)
        deal = result.scalar_one_or_none()

        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deal {deal_id} not found"
            )

        # Check user has access
        if not await verify_tenant_access(current_user["id"], deal.organization_id, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this deal"
            )

        # Build response
        response = DealResponse.model_validate(deal)

        # Add counts
        response.team_members_count = len(deal.team_members) if hasattr(deal, 'team_members') else 0
        response.activities_count = len(deal.activities) if hasattr(deal, 'activities') else 0
        response.documents_count = len(deal.documents) if hasattr(deal, 'documents') else 0

        # Add related data if requested
        if include:
            if "team" in include and hasattr(deal, 'team_members'):
                response.team_members = [tm.to_dict() for tm in deal.team_members]
            if "activities" in include and hasattr(deal, 'activities'):
                response.recent_activities = [
                    activity.to_dict() for activity in deal.activities[:10]
                ]

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting deal {deal_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get deal: {str(e)}"
        )


@router.patch("/{deal_id}", response_model=DealResponse)
async def update_deal(
    deal_id: UUID = Path(..., description="Deal ID"),
    deal_update: DealUpdate = ...,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant)
) -> DealResponse:
    """
    Update an existing deal with partial data.

    Only updates provided fields, maintains version control.
    """
    try:
        # Get existing deal
        query = select(Deal).where(
            and_(
                Deal.id == deal_id,
                Deal.organization_id == tenant_id,
                Deal.is_deleted == False
            )
        )
        result = await db.execute(query)
        deal = result.scalar_one_or_none()

        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deal {deal_id} not found"
            )

        # Track old stage for activity logging
        old_stage = deal.stage

        # Update fields
        update_data = deal_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(deal, field, value)

        # Update metadata
        deal.updated_at = datetime.utcnow()
        deal.updated_by = current_user["id"]

        # Save changes
        await db.commit()
        await db.refresh(deal)

        # Log stage change activity if applicable
        if old_stage != deal.stage:
            activity_service = ActivityService(db)
            await activity_service.log_activity(
                deal_id=deal.id,
                activity_type="stage_change",
                subject=f"Stage changed from {old_stage} to {deal.stage}",
                description=f"Deal moved to {deal.stage} stage",
                user_id=current_user["id"]
            )

        return DealResponse.model_validate(deal)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating deal {deal_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update deal: {str(e)}"
        )


@router.delete("/{deal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deal(
    deal_id: UUID = Path(..., description="Deal ID"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_permission("deals.delete")),
    tenant_id: UUID = Depends(get_current_tenant)
) -> None:
    """
    Soft delete a deal (marks as deleted, doesn't remove from database).

    Requires deals.delete permission.
    """
    try:
        # Get deal
        query = select(Deal).where(
            and_(
                Deal.id == deal_id,
                Deal.organization_id == tenant_id,
                Deal.is_deleted == False
            )
        )
        result = await db.execute(query)
        deal = result.scalar_one_or_none()

        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deal {deal_id} not found"
            )

        # Soft delete
        deal.is_deleted = True
        deal.deleted_at = datetime.utcnow()
        deal.deleted_by = current_user["id"]

        await db.commit()

        # Log activity
        activity_service = ActivityService(db)
        await activity_service.log_activity(
            deal_id=deal.id,
            activity_type="deal_deleted",
            subject=f"Deal '{deal.title}' deleted",
            description="Deal marked as deleted",
            user_id=current_user["id"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting deal {deal_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete deal: {str(e)}"
        )


@router.put("/{deal_id}/stage", response_model=DealResponse)
async def update_deal_stage(
    deal_id: UUID = Path(..., description="Deal ID"),
    stage_update: DealStageUpdate = ...,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant)
) -> DealResponse:
    """
    Update deal stage with tracking and validation.

    Logs stage change in activity history.
    """
    try:
        # Get deal
        query = select(Deal).where(
            and_(
                Deal.id == deal_id,
                Deal.organization_id == tenant_id,
                Deal.is_deleted == False
            )
        )
        result = await db.execute(query)
        deal = result.scalar_one_or_none()

        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deal {deal_id} not found"
            )

        old_stage = deal.stage

        # Update stage
        deal.stage = stage_update.stage
        if stage_update.probability_of_close is not None:
            deal.probability_of_close = stage_update.probability_of_close

        # Track actual close date for closed stages
        if stage_update.stage in ["closed_won", "closed_lost"]:
            deal.actual_close_date = datetime.utcnow().date()

        deal.updated_at = datetime.utcnow()
        deal.updated_by = current_user["id"]

        await db.commit()
        await db.refresh(deal)

        # Log activity
        activity_service = ActivityService(db)
        await activity_service.log_activity(
            deal_id=deal.id,
            activity_type="stage_change",
            subject=f"Stage changed from {old_stage} to {stage_update.stage}",
            description=stage_update.reason or f"Deal moved to {stage_update.stage} stage",
            user_id=current_user["id"]
        )

        return DealResponse.model_validate(deal)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating deal stage {deal_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update deal stage: {str(e)}"
        )


@router.post("/bulk", response_model=Dict[str, Any])
async def bulk_deal_operations(
    bulk_operation: DealBulkOperation,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant)
) -> Dict[str, Any]:
    """
    Perform bulk operations on multiple deals.

    Supports update, delete, archive, and stage_change operations.
    """
    try:
        success_ids = []
        failed_ids = []

        for deal_id in bulk_operation.deal_ids:
            try:
                # Get deal
                query = select(Deal).where(
                    and_(
                        Deal.id == deal_id,
                        Deal.organization_id == tenant_id,
                        Deal.is_deleted == False
                    )
                )
                result = await db.execute(query)
                deal = result.scalar_one_or_none()

                if not deal:
                    failed_ids.append({"id": str(deal_id), "error": "Not found"})
                    continue

                # Perform operation
                if bulk_operation.operation == "update":
                    for field, value in bulk_operation.data.items():
                        setattr(deal, field, value)

                elif bulk_operation.operation == "delete":
                    deal.is_deleted = True
                    deal.deleted_at = datetime.utcnow()
                    deal.deleted_by = current_user["id"]

                elif bulk_operation.operation == "archive":
                    deal.is_active = False

                elif bulk_operation.operation == "stage_change":
                    deal.stage = bulk_operation.data.get("stage")
                    if "probability_of_close" in bulk_operation.data:
                        deal.probability_of_close = bulk_operation.data["probability_of_close"]

                deal.updated_at = datetime.utcnow()
                deal.updated_by = current_user["id"]

                success_ids.append(str(deal_id))

            except Exception as e:
                failed_ids.append({"id": str(deal_id), "error": str(e)})

        await db.commit()

        return {
            "operation": bulk_operation.operation,
            "total": len(bulk_operation.deal_ids),
            "success": success_ids,
            "failed": failed_ids
        }

    except Exception as e:
        logger.error(f"Error in bulk operation: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk operation failed: {str(e)}"
        )


@router.get("/statistics", response_model=DealStatistics)
async def get_deal_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tenant_id: UUID = Depends(get_current_tenant)
) -> DealStatistics:
    """
    Get aggregated statistics for deals.

    Returns counts, values, and conversion metrics.
    """
    try:
        deal_service = DealService(db)
        stats = await deal_service.get_statistics(tenant_id)
        return DealStatistics.model_validate(stats)

    except Exception as e:
        logger.error(f"Error getting deal statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )