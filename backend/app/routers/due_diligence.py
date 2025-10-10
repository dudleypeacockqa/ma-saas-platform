"""
Due Diligence API Router
Handles checklist management, document requests, reviews, and risk assessments
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
import json

from app.core.database import get_db
from app.auth.clerk_auth import get_current_user, ClerkUser, require_role
from app.auth.tenant_isolation import get_tenant_db
from app.models.due_diligence import (
    DueDiligenceChecklist,
    DueDiligenceItem,
    DueDiligenceProcess,
    DocumentRequest,
    DueDiligenceDocument,
    DocumentReview,
    RiskAssessment,
    DocumentCategory,
    DocumentStatus,
    RiskLevel,
    ChecklistType
)
from app.models.deal import Deal
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/due-diligence", tags=["due-diligence"])

# Pydantic Models
class ChecklistTemplateCreate(BaseModel):
    name: str
    description: Optional[str]
    checklist_type: ChecklistType
    industry: Optional[str]
    categories: List[str] = []
    items: List[Dict[str, Any]] = []

class ChecklistItemCreate(BaseModel):
    category: DocumentCategory
    title: str
    description: Optional[str]
    is_required: bool = True
    document_types: List[str] = []
    validation_rules: Dict[str, Any] = {}
    review_guidelines: Optional[str]
    risk_weight: float = 1.0
    critical_item: bool = False

class ProcessCreate(BaseModel):
    deal_id: UUID
    checklist_id: UUID
    name: str
    target_completion_date: Optional[datetime]
    lead_reviewer_id: Optional[str]
    assigned_team: List[str] = []
    notes: Optional[str]

class DocumentRequestCreate(BaseModel):
    title: str
    description: Optional[str]
    category: DocumentCategory
    priority: str = "normal"
    due_date: Optional[datetime]
    checklist_item_id: Optional[UUID]

class DocumentReviewCreate(BaseModel):
    document_id: UUID
    status: DocumentStatus
    risk_level: RiskLevel = RiskLevel.LOW
    confidence_score: Optional[float]
    findings: Optional[str]
    issues_identified: List[str] = []
    recommendations: Optional[str]
    action_items: List[str] = []
    requires_follow_up: bool = False
    is_blocking: bool = False
    escalation_required: bool = False

class RiskAssessmentCreate(BaseModel):
    financial_risk: float = 0.0
    legal_risk: float = 0.0
    operational_risk: float = 0.0
    market_risk: float = 0.0
    regulatory_risk: float = 0.0
    reputation_risk: float = 0.0
    confidence_level: Optional[float]
    key_risks: List[Dict[str, Any]] = []
    mitigation_strategies: List[Dict[str, Any]] = []
    recommendations: Optional[str]
    deal_recommendation: Optional[str]
    conditions: List[str] = []
    price_adjustment_recommendation: Optional[float]

# Checklist Template Endpoints
@router.get("/templates")
async def get_checklist_templates(
    checklist_type: Optional[ChecklistType] = None,
    industry: Optional[str] = None,
    is_template: bool = True,
    user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_tenant_db)
):
    """Get available checklist templates"""
    query = db.query(DueDiligenceChecklist).filter(
        DueDiligenceChecklist.is_template == is_template,
        DueDiligenceChecklist.is_active == True
    )

    if checklist_type:
        query = query.filter(DueDiligenceChecklist.checklist_type == checklist_type)
    if industry:
        query = query.filter(DueDiligenceChecklist.industry == industry)

    templates = query.order_by(desc(DueDiligenceChecklist.usage_count)).all()
    return templates

@router.post("/templates")
@require_role(["owner", "admin", "manager"])
async def create_checklist_template(
    template: ChecklistTemplateCreate,
    user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_tenant_db)
):
    """Create a new checklist template"""
    checklist = DueDiligenceChecklist(
        organization_id=user.org_id,
        name=template.name,
        description=template.description,
        checklist_type=template.checklist_type,
        industry=template.industry,
        categories=template.categories,
        is_template=True
    )
    db.add(checklist)
    db.flush()

    # Add checklist items
    for idx, item_data in enumerate(template.items):
        item = DueDiligenceItem(
            organization_id=user.org_id,
            checklist_id=checklist.id,
            category=item_data.get("category"),
            title=item_data.get("title"),
            description=item_data.get("description"),
            is_required=item_data.get("is_required", True),
            order_index=idx,
            document_types=item_data.get("document_types", []),
            validation_rules=item_data.get("validation_rules", {}),
            review_guidelines=item_data.get("review_guidelines"),
            risk_weight=item_data.get("risk_weight", 1.0),
            critical_item=item_data.get("critical_item", False)
        )
        db.add(item)

    db.commit()
    db.refresh(checklist)
    return checklist

# Due Diligence Process Endpoints
@router.post("/processes")
@require_role(["owner", "admin", "manager"])
async def create_due_diligence_process(
    process_data: ProcessCreate,
    user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_tenant_db)
):
    """Start a new due diligence process for a deal"""
    # Verify deal exists and user has access
    deal = db.query(Deal).filter(Deal.id == process_data.deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    # Verify checklist exists
    checklist = db.query(DueDiligenceChecklist).filter(
        DueDiligenceChecklist.id == process_data.checklist_id
    ).first()
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist template not found")

    # Create process
    process = DueDiligenceProcess(
        organization_id=user.org_id,
        deal_id=process_data.deal_id,
        checklist_id=process_data.checklist_id,
        name=process_data.name,
        target_completion_date=process_data.target_completion_date,
        lead_reviewer_id=process_data.lead_reviewer_id or user.user_id,
        assigned_team=process_data.assigned_team,
        notes=process_data.notes
    )
    db.add(process)
    db.flush()

    # Create document requests from checklist items
    checklist_items = db.query(DueDiligenceItem).filter(
        DueDiligenceItem.checklist_id == checklist.id
    ).order_by(DueDiligenceItem.order_index).all()

    for item in checklist_items:
        request = DocumentRequest(
            organization_id=user.org_id,
            process_id=process.id,
            checklist_item_id=item.id,
            title=item.title,
            description=item.description,
            category=item.category,
            status=DocumentStatus.NOT_REQUESTED,
            priority="high" if item.critical_item else "normal"
        )
        db.add(request)

    # Update checklist usage
    checklist.usage_count += 1
    checklist.last_used_at = datetime.utcnow()

    db.commit()
    db.refresh(process)
    return process

@router.get("/processes/{process_id}")
async def get_due_diligence_process(
    process_id: UUID,
    user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_tenant_db)
):
    """Get due diligence process details"""
    process = db.query(DueDiligenceProcess).filter(
        DueDiligenceProcess.id == process_id
    ).first()

    if not process:
        raise HTTPException(status_code=404, detail="Process not found")

    # Calculate completion percentage
    total_requests = db.query(func.count(DocumentRequest.id)).filter(
        DocumentRequest.process_id == process_id
    ).scalar()

    completed_requests = db.query(func.count(DocumentRequest.id)).filter(
        DocumentRequest.process_id == process_id,
        DocumentRequest.status.in_([DocumentStatus.APPROVED, DocumentStatus.REVIEWED])
    ).scalar()

    process.completion_percentage = (completed_requests / total_requests * 100) if total_requests > 0 else 0

    return process

@router.get("/processes/{process_id}/status")
async def get_process_status(
    process_id: UUID,
    user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_tenant_db)
):
    """Get detailed status of due diligence process"""
    # Get process
    process = db.query(DueDiligenceProcess).filter(
        DueDiligenceProcess.id == process_id
    ).first()

    if not process:
        raise HTTPException(status_code=404, detail="Process not found")

    # Get status counts
    status_counts = db.query(
        DocumentRequest.status,
        func.count(DocumentRequest.id).label("count")
    ).filter(
        DocumentRequest.process_id == process_id
    ).group_by(DocumentRequest.status).all()

    # Get category progress
    category_progress = db.query(
        DocumentRequest.category,
        func.count(DocumentRequest.id).label("total"),
        func.sum(
            func.case(
                (DocumentRequest.status.in_([DocumentStatus.APPROVED, DocumentStatus.REVIEWED]), 1),
                else_=0
            )
        ).label("completed")
    ).filter(
        DocumentRequest.process_id == process_id
    ).group_by(DocumentRequest.category).all()

    # Get critical items status
    critical_items = db.query(DocumentRequest).join(
        DueDiligenceItem
    ).filter(
        DocumentRequest.process_id == process_id,
        DueDiligenceItem.critical_item == True
    ).all()

    return {
        "process_id": process_id,
        "overall_completion": process.completion_percentage,
        "status_distribution": {str(s.status): s.count for s in status_counts},
        "category_progress": [
            {
                "category": str(cat.category),
                "total": cat.total,
                "completed": cat.completed or 0,
                "percentage": ((cat.completed or 0) / cat.total * 100) if cat.total > 0 else 0
            }
            for cat in category_progress
        ],
        "critical_items": [
            {
                "id": str(item.id),
                "title": item.title,
                "status": str(item.status),
                "is_blocking": item.status in [DocumentStatus.NOT_REQUESTED, DocumentStatus.REJECTED]
            }
            for item in critical_items
        ],
        "risk_level": str(process.risk_level),
        "risk_score": process.overall_risk_score
    }

# Document Request Endpoints
@router.get("/processes/{process_id}/requests")
async def get_document_requests(
    process_id: UUID,
    category: Optional[DocumentCategory] = None,
    status: Optional[DocumentStatus] = None,
    priority: Optional[str] = None,
    user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_tenant_db)
):
    """Get document requests for a process"""
    query = db.query(DocumentRequest).filter(
        DocumentRequest.process_id == process_id
    )

    if category:
        query = query.filter(DocumentRequest.category == category)
    if status:
        query = query.filter(DocumentRequest.status == status)
    if priority:
        query = query.filter(DocumentRequest.priority == priority)

    requests = query.order_by(
        DocumentRequest.priority.desc(),
        DocumentRequest.due_date
    ).all()

    return requests

@router.post("/processes/{process_id}/requests")
@require_role(["owner", "admin", "manager"])
async def create_document_request(
    process_id: UUID,
    request_data: DocumentRequestCreate,
    user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_tenant_db)
):
    """Create a new document request"""
    # Verify process exists
    process = db.query(DueDiligenceProcess).filter(
        DueDiligenceProcess.id == process_id
    ).first()
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")

    request = DocumentRequest(
        organization_id=user.org_id,
        process_id=process_id,
        title=request_data.title,
        description=request_data.description,
        category=request_data.category,
        priority=request_data.priority,
        due_date=request_data.due_date,
        checklist_item_id=request_data.checklist_item_id,
        status=DocumentStatus.REQUESTED,
        requested_date=datetime.utcnow(),
        requested_by=user.user_id
    )

    db.add(request)
    db.commit()
    db.refresh(request)
    return request

@router.patch("/requests/{request_id}/status")
@require_role(["owner", "admin", "manager", "member"])
async def update_request_status(
    request_id: UUID,
    status: DocumentStatus,
    notes: Optional[str] = None,
    user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_tenant_db)
):
    """Update document request status"""
    request = db.query(DocumentRequest).filter(
        DocumentRequest.id == request_id
    ).first()

    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    request.status = status
    if notes:
        request.response_notes = notes

    if status in [DocumentStatus.APPROVED, DocumentStatus.REVIEWED]:
        request.fulfilled_date = datetime.utcnow()

    db.commit()
    db.refresh(request)
    return request

# Document Upload Endpoints
@router.post("/processes/{process_id}/documents")
@require_role(["owner", "admin", "manager", "member"])
async def upload_document(
    process_id: UUID,
    request_id: Optional[UUID] = None,
    category: DocumentCategory = Query(...),
    file: UploadFile = File(...),
    description: Optional[str] = None,
    tags: Optional[str] = None,  # Comma-separated tags
    user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_tenant_db)
):
    """Upload a document for due diligence"""
    # Verify process exists
    process = db.query(DueDiligenceProcess).filter(
        DueDiligenceProcess.id == process_id
    ).first()
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")

    # Save file (mock implementation - replace with actual file storage)
    file_path = f"/uploads/due_diligence/{process_id}/{file.filename}"

    # Create document record
    document = DueDiligenceDocument(
        organization_id=user.org_id,
        process_id=process_id,
        request_id=request_id,
        name=file.filename,
        file_path=file_path,
        file_size=file.size,
        file_type=file.filename.split('.')[-1] if '.' in file.filename else None,
        mime_type=file.content_type,
        category=category,
        uploaded_by=user.user_id,
        description=description,
        tags=tags.split(',') if tags else [],
        review_status=DocumentStatus.UPLOADED
    )

    db.add(document)

    # Update request status if linked
    if request_id:
        request = db.query(DocumentRequest).filter(
            DocumentRequest.id == request_id
        ).first()
        if request:
            request.status = DocumentStatus.UPLOADED

    db.commit()
    db.refresh(document)
    return document

@router.get("/processes/{process_id}/documents")
async def get_documents(
    process_id: UUID,
    category: Optional[DocumentCategory] = None,
    status: Optional[DocumentStatus] = None,
    user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_tenant_db)
):
    """Get documents for a process"""
    query = db.query(DueDiligenceDocument).filter(
        DueDiligenceDocument.process_id == process_id,
        DueDiligenceDocument.is_latest == True
    )

    if category:
        query = query.filter(DueDiligenceDocument.category == category)
    if status:
        query = query.filter(DueDiligenceDocument.review_status == status)

    documents = query.order_by(desc(DueDiligenceDocument.uploaded_at)).all()
    return documents

# Document Review Endpoints
@router.post("/documents/{document_id}/reviews")
@require_role(["owner", "admin", "manager", "member"])
async def create_document_review(
    document_id: UUID,
    review_data: DocumentReviewCreate,
    user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_tenant_db)
):
    """Create a review for a document"""
    # Verify document exists
    document = db.query(DueDiligenceDocument).filter(
        DueDiligenceDocument.id == document_id
    ).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    review = DocumentReview(
        organization_id=user.org_id,
        document_id=document_id,
        process_id=document.process_id,
        reviewer_id=user.user_id,
        reviewer_name=user.user_id,  # Should be replaced with actual name
        status=review_data.status,
        risk_level=review_data.risk_level,
        confidence_score=review_data.confidence_score,
        findings=review_data.findings,
        issues_identified=review_data.issues_identified,
        recommendations=review_data.recommendations,
        action_items=review_data.action_items,
        requires_follow_up=review_data.requires_follow_up,
        is_blocking=review_data.is_blocking,
        escalation_required=review_data.escalation_required,
        review_type="initial"
    )

    db.add(review)

    # Update document status
    document.review_status = review_data.status
    document.reviewed_by = user.user_id
    document.reviewed_at = datetime.utcnow()

    # Calculate risk score based on reviews
    all_reviews = db.query(DocumentReview).filter(
        DocumentReview.document_id == document_id
    ).all()

    if all_reviews:
        risk_scores = {
            RiskLevel.CRITICAL: 100,
            RiskLevel.HIGH: 75,
            RiskLevel.MEDIUM: 50,
            RiskLevel.LOW: 25,
            RiskLevel.NONE: 0
        }
        avg_risk = sum(risk_scores.get(r.risk_level, 0) for r in all_reviews) / len(all_reviews)
        document.risk_score = avg_risk

    db.commit()
    db.refresh(review)
    return review

@router.get("/documents/{document_id}/reviews")
async def get_document_reviews(
    document_id: UUID,
    user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_tenant_db)
):
    """Get all reviews for a document"""
    reviews = db.query(DocumentReview).filter(
        DocumentReview.document_id == document_id
    ).order_by(desc(DocumentReview.review_date)).all()
    return reviews

# Risk Assessment Endpoints
@router.post("/processes/{process_id}/risk-assessment")
@require_role(["owner", "admin", "manager"])
async def create_risk_assessment(
    process_id: UUID,
    assessment_data: RiskAssessmentCreate,
    user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_tenant_db)
):
    """Create a risk assessment for the due diligence process"""
    # Verify process exists
    process = db.query(DueDiligenceProcess).filter(
        DueDiligenceProcess.id == process_id
    ).first()
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")

    # Calculate overall risk score
    risk_components = [
        assessment_data.financial_risk,
        assessment_data.legal_risk,
        assessment_data.operational_risk,
        assessment_data.market_risk,
        assessment_data.regulatory_risk,
        assessment_data.reputation_risk
    ]
    overall_risk = sum(risk_components) / len(risk_components)

    # Determine risk level
    if overall_risk >= 75:
        risk_level = RiskLevel.CRITICAL
    elif overall_risk >= 50:
        risk_level = RiskLevel.HIGH
    elif overall_risk >= 25:
        risk_level = RiskLevel.MEDIUM
    else:
        risk_level = RiskLevel.LOW

    assessment = RiskAssessment(
        organization_id=user.org_id,
        process_id=process_id,
        assessor_id=user.user_id,
        financial_risk=assessment_data.financial_risk,
        legal_risk=assessment_data.legal_risk,
        operational_risk=assessment_data.operational_risk,
        market_risk=assessment_data.market_risk,
        regulatory_risk=assessment_data.regulatory_risk,
        reputation_risk=assessment_data.reputation_risk,
        overall_risk_score=overall_risk,
        risk_level=risk_level,
        confidence_level=assessment_data.confidence_level,
        key_risks=assessment_data.key_risks,
        mitigation_strategies=assessment_data.mitigation_strategies,
        recommendations=assessment_data.recommendations,
        deal_recommendation=assessment_data.deal_recommendation,
        conditions=assessment_data.conditions,
        price_adjustment_recommendation=assessment_data.price_adjustment_recommendation
    )

    db.add(assessment)

    # Update process risk scores
    process.overall_risk_score = overall_risk
    process.risk_level = risk_level
    process.risk_factors = {
        "financial": assessment_data.financial_risk,
        "legal": assessment_data.legal_risk,
        "operational": assessment_data.operational_risk,
        "market": assessment_data.market_risk,
        "regulatory": assessment_data.regulatory_risk,
        "reputation": assessment_data.reputation_risk
    }

    db.commit()
    db.refresh(assessment)
    return assessment

@router.get("/processes/{process_id}/risk-assessment")
async def get_risk_assessment(
    process_id: UUID,
    user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_tenant_db)
):
    """Get the latest risk assessment for a process"""
    assessment = db.query(RiskAssessment).filter(
        RiskAssessment.process_id == process_id
    ).order_by(desc(RiskAssessment.assessment_date)).first()

    if not assessment:
        raise HTTPException(status_code=404, detail="No risk assessment found")

    return assessment

# Analytics Endpoints
@router.get("/analytics/overview")
async def get_due_diligence_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_tenant_db)
):
    """Get due diligence analytics overview"""
    query = db.query(DueDiligenceProcess)

    if start_date:
        query = query.filter(DueDiligenceProcess.start_date >= start_date)
    if end_date:
        query = query.filter(DueDiligenceProcess.start_date <= end_date)

    total_processes = query.count()

    # Average completion time
    completed_processes = query.filter(
        DueDiligenceProcess.actual_completion_date.isnot(None)
    ).all()

    if completed_processes:
        avg_days = sum(
            (p.actual_completion_date - p.start_date).days
            for p in completed_processes
        ) / len(completed_processes)
    else:
        avg_days = 0

    # Risk distribution
    risk_distribution = db.query(
        DueDiligenceProcess.risk_level,
        func.count(DueDiligenceProcess.id).label("count")
    ).group_by(DueDiligenceProcess.risk_level).all()

    # Document statistics
    total_documents = db.query(func.count(DueDiligenceDocument.id)).scalar()

    document_status = db.query(
        DueDiligenceDocument.review_status,
        func.count(DueDiligenceDocument.id).label("count")
    ).group_by(DueDiligenceDocument.review_status).all()

    return {
        "total_processes": total_processes,
        "completed_processes": len(completed_processes),
        "average_completion_days": round(avg_days, 1),
        "risk_distribution": {str(r.risk_level): r.count for r in risk_distribution},
        "total_documents": total_documents,
        "document_status": {str(s.review_status): s.count for s in document_status},
        "in_progress_processes": total_processes - len(completed_processes)
    }