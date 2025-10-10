"""
Term Sheet API endpoints for M&A SaaS Platform
Comprehensive API for managing term sheets with templates and collaboration features
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, date
from decimal import Decimal

from app.core.database import get_db
from app.models.negotiations import (
    TermSheet, TermSheetTemplate,
    TermSheetStatus, DealStructureType
)
from app.services.term_sheet_service import TermSheetService
from app.auth.clerk_auth import get_current_user, get_current_organization_user

router = APIRouter(prefix="/api/term-sheets", tags=["term-sheets"])


# Pydantic Schemas for Templates

class TermSheetTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    industry: Optional[str] = None
    deal_type: Optional[DealStructureType] = None
    category: Optional[str] = None
    is_public: bool = False


class TermSheetTemplateCreate(TermSheetTemplateBase):
    template_structure: Dict[str, Any]
    default_values: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None


class TermSheetTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    deal_type: Optional[DealStructureType] = None
    template_structure: Optional[Dict[str, Any]] = None
    default_values: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class TermSheetTemplateResponse(TermSheetTemplateBase):
    id: str
    organization_id: str
    template_structure: Dict[str, Any]
    default_values: Dict[str, Any]
    validation_rules: Dict[str, Any]
    usage_count: int
    last_used_date: Optional[datetime] = None
    is_active: bool
    version: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Pydantic Schemas for Term Sheets

class TermSheetBase(BaseModel):
    title: str
    purchase_price: Optional[Decimal] = None
    currency: str = "USD"
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None


class TermSheetCreate(TermSheetBase):
    negotiation_id: str
    template_id: Optional[str] = None
    custom_terms: Optional[Dict[str, Any]] = None


class TermSheetCreateFromTemplate(BaseModel):
    negotiation_id: str
    template_id: str
    title: str
    custom_terms: Optional[Dict[str, Any]] = None
    purchase_price: Optional[Decimal] = None
    currency: str = "USD"
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None


class TermSheetUpdate(BaseModel):
    title: Optional[str] = None
    terms: Optional[Dict[str, Any]] = None
    purchase_price: Optional[Decimal] = None
    currency: Optional[str] = None
    cash_consideration: Optional[Decimal] = None
    stock_consideration: Optional[Decimal] = None
    earnout_amount: Optional[Decimal] = None
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None
    status: Optional[TermSheetStatus] = None
    notes: Optional[str] = None
    create_new_version: bool = False
    change_summary: Optional[str] = None


class TermSheetResponse(TermSheetBase):
    id: str
    negotiation_id: str
    template_id: Optional[str] = None
    version: str
    status: TermSheetStatus
    terms: Dict[str, Any]
    cash_consideration: Optional[Decimal] = None
    stock_consideration: Optional[Decimal] = None
    earnout_amount: Optional[Decimal] = None
    submitted_for_approval: bool
    approval_workflow: List
    document_url: Optional[str] = None
    document_version: int
    signature_status: str
    previous_version_id: Optional[str] = None
    change_summary: Optional[str] = None
    custom_fields: Dict[str, Any]
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CollaborationRequest(BaseModel):
    field_path: str
    new_value: Any
    comment: Optional[str] = None


class ComparisonRequest(BaseModel):
    term_sheet2_id: str


class ValidationRequest(BaseModel):
    run_business_logic_validation: bool = True
    run_template_validation: bool = True


class AnalyticsRequest(BaseModel):
    negotiation_id: Optional[str] = None
    days_back: int = 90


# Template Endpoints

@router.post("/templates", response_model=TermSheetTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TermSheetTemplateCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Create a new term sheet template."""
    service = TermSheetService(db)
    template = service.create_template(
        organization_id=current_user["organization_id"],
        created_by_id=current_user["id"],
        **template_data.model_dump()
    )
    return template


@router.get("/templates", response_model=List[TermSheetTemplateResponse])
async def list_templates(
    industry: Optional[str] = None,
    deal_type: Optional[DealStructureType] = None,
    category: Optional[str] = None,
    include_public: bool = True,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """List available term sheet templates."""
    service = TermSheetService(db)
    templates = service.list_templates(
        organization_id=current_user["organization_id"],
        industry=industry,
        deal_type=deal_type,
        category=category,
        include_public=include_public
    )
    return templates


@router.get("/templates/{template_id}", response_model=TermSheetTemplateResponse)
async def get_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Get a specific term sheet template."""
    service = TermSheetService(db)
    template = service.get_template_by_id(
        template_id,
        current_user["organization_id"]
    )
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    return template


@router.patch("/templates/{template_id}", response_model=TermSheetTemplateResponse)
async def update_template(
    template_id: str,
    updates: TermSheetTemplateUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Update a term sheet template."""
    template = (
        db.query(TermSheetTemplate)
        .filter(
            TermSheetTemplate.id == template_id,
            TermSheetTemplate.organization_id == current_user["organization_id"]
        )
        .first()
    )

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Update fields
    for field, value in updates.model_dump(exclude_unset=True).items():
        if hasattr(template, field):
            setattr(template, field, value)

    template.updated_by = current_user["id"]
    db.commit()
    db.refresh(template)

    return template


# Term Sheet Endpoints

@router.post("/", response_model=TermSheetResponse, status_code=status.HTTP_201_CREATED)
async def create_term_sheet(
    term_sheet_data: TermSheetCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Create a new term sheet."""
    service = TermSheetService(db)

    # Extract terms from custom_terms or create empty dict
    terms = term_sheet_data.custom_terms or {}

    term_sheet = service.create_term_sheet_from_template(
        negotiation_id=term_sheet_data.negotiation_id,
        template_id=term_sheet_data.template_id,
        title=term_sheet_data.title,
        custom_terms=terms,
        purchase_price=term_sheet_data.purchase_price,
        currency=term_sheet_data.currency,
        effective_date=term_sheet_data.effective_date,
        expiration_date=term_sheet_data.expiration_date,
        created_by_id=current_user["id"]
    ) if term_sheet_data.template_id else service.create_term_sheet_from_template(
        negotiation_id=term_sheet_data.negotiation_id,
        template_id=None,
        title=term_sheet_data.title,
        custom_terms=terms,
        purchase_price=term_sheet_data.purchase_price,
        currency=term_sheet_data.currency,
        effective_date=term_sheet_data.effective_date,
        expiration_date=term_sheet_data.expiration_date,
        created_by_id=current_user["id"]
    )

    return term_sheet


@router.post("/from-template", response_model=TermSheetResponse, status_code=status.HTTP_201_CREATED)
async def create_term_sheet_from_template(
    request: TermSheetCreateFromTemplate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Create a term sheet from a template."""
    service = TermSheetService(db)
    term_sheet = service.create_term_sheet_from_template(
        negotiation_id=request.negotiation_id,
        template_id=request.template_id,
        title=request.title,
        custom_terms=request.custom_terms,
        purchase_price=request.purchase_price,
        currency=request.currency,
        effective_date=request.effective_date,
        expiration_date=request.expiration_date,
        created_by_id=current_user["id"]
    )
    return term_sheet


@router.get("/", response_model=List[TermSheetResponse])
async def list_term_sheets(
    negotiation_id: Optional[str] = None,
    status_filter: Optional[TermSheetStatus] = None,
    current_versions_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """List term sheets with optional filters."""
    query = (
        db.query(TermSheet)
        .filter(TermSheet.organization_id == current_user["organization_id"])
        .order_by(TermSheet.created_at.desc())
    )

    if negotiation_id:
        query = query.filter(TermSheet.negotiation_id == negotiation_id)

    if status_filter:
        query = query.filter(TermSheet.status == status_filter)

    if current_versions_only:
        # Get current versions by finding term sheets that are not superseded
        query = query.filter(
            ~db.query(TermSheet.id)
            .filter(TermSheet.previous_version_id == TermSheet.id)
            .exists()
        )

    term_sheets = query.offset(offset).limit(limit).all()
    return term_sheets


@router.get("/{term_sheet_id}", response_model=TermSheetResponse)
async def get_term_sheet(
    term_sheet_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Get a specific term sheet."""
    term_sheet = (
        db.query(TermSheet)
        .filter(
            TermSheet.id == term_sheet_id,
            TermSheet.organization_id == current_user["organization_id"]
        )
        .first()
    )

    if not term_sheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Term sheet not found"
        )

    return term_sheet


@router.patch("/{term_sheet_id}", response_model=TermSheetResponse)
async def update_term_sheet(
    term_sheet_id: str,
    updates: TermSheetUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Update a term sheet with optional versioning."""
    service = TermSheetService(db)
    try:
        term_sheet = service.update_term_sheet(
            term_sheet_id=term_sheet_id,
            organization_id=current_user["organization_id"],
            updates=updates.model_dump(exclude_unset=True),
            create_new_version=updates.create_new_version,
            change_summary=updates.change_summary,
            updated_by_id=current_user["id"]
        )
        return term_sheet
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/{term_sheet_id}/versions", response_model=List[TermSheetResponse])
async def get_term_sheet_versions(
    term_sheet_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Get all versions of a term sheet."""
    # Find the root term sheet (no previous version)
    root_term_sheet = (
        db.query(TermSheet)
        .filter(
            TermSheet.id == term_sheet_id,
            TermSheet.organization_id == current_user["organization_id"]
        )
        .first()
    )

    if not root_term_sheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Term sheet not found"
        )

    # Get all versions in the chain
    versions = []
    current = root_term_sheet

    # Go backwards to find root
    while current.previous_version_id:
        previous = (
            db.query(TermSheet)
            .filter(TermSheet.id == current.previous_version_id)
            .first()
        )
        if previous:
            current = previous
        else:
            break

    # Now go forward to collect all versions
    versions.append(current)
    while True:
        next_version = (
            db.query(TermSheet)
            .filter(TermSheet.previous_version_id == current.id)
            .first()
        )
        if next_version:
            versions.append(next_version)
            current = next_version
        else:
            break

    return versions


# Collaboration Endpoints

@router.post("/{term_sheet_id}/collaborate")
async def collaborate_on_term_sheet(
    term_sheet_id: str,
    collaboration_request: CollaborationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Real-time collaboration on term sheet fields."""
    service = TermSheetService(db)
    try:
        change_record = service.collaborate_on_term_sheet(
            term_sheet_id=term_sheet_id,
            organization_id=current_user["organization_id"],
            field_path=collaboration_request.field_path,
            new_value=collaboration_request.new_value,
            user_id=current_user["id"],
            comment=collaboration_request.comment
        )
        return {
            "status": "success",
            "change_record": change_record,
            "message": "Field updated successfully"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/{term_sheet_id}/collaboration-history")
async def get_collaboration_history(
    term_sheet_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Get collaboration history for a term sheet."""
    term_sheet = (
        db.query(TermSheet)
        .filter(
            TermSheet.id == term_sheet_id,
            TermSheet.organization_id == current_user["organization_id"]
        )
        .first()
    )

    if not term_sheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Term sheet not found"
        )

    collaboration_history = term_sheet.custom_fields.get('collaboration_history', [])

    return {
        "term_sheet_id": term_sheet_id,
        "collaboration_history": collaboration_history,
        "total_changes": len(collaboration_history)
    }


# Comparison and Analysis Endpoints

@router.post("/{term_sheet_id}/compare")
async def compare_term_sheets(
    term_sheet_id: str,
    comparison_request: ComparisonRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Compare two term sheets."""
    service = TermSheetService(db)
    try:
        comparison = service.compare_term_sheets(
            term_sheet1_id=term_sheet_id,
            term_sheet2_id=comparison_request.term_sheet2_id,
            organization_id=current_user["organization_id"]
        )
        return comparison
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{term_sheet_id}/validate")
async def validate_term_sheet(
    term_sheet_id: str,
    validation_request: ValidationRequest = ValidationRequest(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Validate a term sheet."""
    service = TermSheetService(db)
    try:
        validation_results = service.validate_term_sheet(
            term_sheet_id=term_sheet_id,
            organization_id=current_user["organization_id"]
        )
        return validation_results
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/analytics")
async def get_term_sheet_analytics(
    analytics_request: AnalyticsRequest = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Get term sheet analytics."""
    service = TermSheetService(db)
    analytics = service.get_term_sheet_analytics(
        organization_id=current_user["organization_id"],
        negotiation_id=analytics_request.negotiation_id,
        days_back=analytics_request.days_back
    )
    return analytics


# Workflow Endpoints

@router.post("/{term_sheet_id}/submit-for-approval")
async def submit_for_approval(
    term_sheet_id: str,
    approval_workflow: List[Dict[str, str]] = [],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Submit term sheet for approval."""
    term_sheet = (
        db.query(TermSheet)
        .filter(
            TermSheet.id == term_sheet_id,
            TermSheet.organization_id == current_user["organization_id"]
        )
        .first()
    )

    if not term_sheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Term sheet not found"
        )

    if term_sheet.submitted_for_approval:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Term sheet already submitted for approval"
        )

    # Update term sheet status
    term_sheet.submitted_for_approval = True
    term_sheet.status = TermSheetStatus.PENDING_APPROVAL
    term_sheet.approval_workflow = approval_workflow
    term_sheet.updated_by = current_user["id"]

    db.commit()

    return {
        "status": "success",
        "message": "Term sheet submitted for approval",
        "approval_workflow": approval_workflow
    }


@router.post("/{term_sheet_id}/approve")
async def approve_term_sheet(
    term_sheet_id: str,
    approval_comments: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Approve a term sheet."""
    term_sheet = (
        db.query(TermSheet)
        .filter(
            TermSheet.id == term_sheet_id,
            TermSheet.organization_id == current_user["organization_id"]
        )
        .first()
    )

    if not term_sheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Term sheet not found"
        )

    # Add approver to approved_by list
    if not term_sheet.approved_by:
        term_sheet.approved_by = []

    approval_record = {
        "user_id": current_user["id"],
        "approved_at": datetime.utcnow().isoformat(),
        "comments": approval_comments
    }

    term_sheet.approved_by.append(approval_record)

    # Check if all required approvals are received
    # (Simplified logic - in production would be more sophisticated)
    required_approvals = len(term_sheet.approval_workflow)
    received_approvals = len(term_sheet.approved_by)

    if received_approvals >= required_approvals:
        term_sheet.status = TermSheetStatus.APPROVED

    term_sheet.updated_by = current_user["id"]
    db.commit()

    return {
        "status": "success",
        "message": "Term sheet approved",
        "approval_status": term_sheet.status.value,
        "approvals_received": received_approvals,
        "approvals_required": required_approvals
    }


@router.post("/{term_sheet_id}/generate-document")
async def generate_document(
    term_sheet_id: str,
    document_format: str = "pdf",
    include_signature_fields: bool = True,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Generate a document from the term sheet."""
    term_sheet = (
        db.query(TermSheet)
        .filter(
            TermSheet.id == term_sheet_id,
            TermSheet.organization_id == current_user["organization_id"]
        )
        .first()
    )

    if not term_sheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Term sheet not found"
        )

    # This would integrate with a document generation service
    # For now, we'll simulate the process
    document_url = f"/documents/term-sheet-{term_sheet_id}-v{term_sheet.version}.{document_format}"

    # Update term sheet with document info
    term_sheet.document_url = document_url
    term_sheet.document_version += 1

    if include_signature_fields:
        term_sheet.signature_status = "ready_for_signature"

    term_sheet.updated_by = current_user["id"]
    db.commit()

    return {
        "status": "success",
        "message": "Document generated successfully",
        "document_url": document_url,
        "document_format": document_format,
        "signature_ready": include_signature_fields
    }