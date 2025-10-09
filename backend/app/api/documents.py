"""
Document Management API endpoints for M&A SaaS Platform
Advanced document handling with versioning, approvals, and e-signature integration
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, date
from decimal import Decimal

from app.core.database import get_db
from app.models.documents import (
    Document, DocumentApproval, DocumentSignature, DocumentActivity,
    DocumentTemplate, DocumentComparison,
    DocumentCategory, DocumentStatus, ApprovalStatus, SignatureStatus, AccessLevel
)
from app.auth.clerk_auth import get_current_user, get_current_organization_user

router = APIRouter(prefix="/api/documents", tags=["documents"])


# Pydantic Schemas

class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: DocumentCategory
    document_type: Optional[str] = None
    access_level: AccessLevel = AccessLevel.TEAM
    is_confidential: bool = True
    requires_approval: bool = False
    requires_signature: bool = False
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None
    due_date: Optional[date] = None


class DocumentCreate(DocumentBase):
    negotiation_id: Optional[str] = None
    deal_id: Optional[str] = None
    term_sheet_id: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_metadata: Optional[Dict[str, Any]] = None


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[DocumentCategory] = None
    document_type: Optional[str] = None
    status: Optional[DocumentStatus] = None
    access_level: Optional[AccessLevel] = None
    is_confidential: Optional[bool] = None
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None
    due_date: Optional[date] = None
    tags: Optional[List[str]] = None
    custom_metadata: Optional[Dict[str, Any]] = None
    version_notes: Optional[str] = None


class DocumentResponse(DocumentBase):
    id: str
    negotiation_id: Optional[str] = None
    deal_id: Optional[str] = None
    term_sheet_id: Optional[str] = None
    file_name: str
    original_file_name: Optional[str] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    version_number: int
    is_current_version: bool
    parent_document_id: Optional[str] = None
    version_notes: Optional[str] = None
    status: DocumentStatus
    workflow_stage: Optional[str] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    key_terms_extracted: Optional[List[str]] = None
    content_summary: Optional[str] = None
    tags: List[str]
    custom_metadata: Dict[str, Any]
    view_count: int
    download_count: int
    last_viewed_date: Optional[datetime] = None
    last_downloaded_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApprovalBase(BaseModel):
    approver_id: str
    approval_level: int = 1
    role_required: Optional[str] = None
    due_date: Optional[datetime] = None


class ApprovalCreate(ApprovalBase):
    pass


class ApprovalUpdate(BaseModel):
    status: ApprovalStatus
    comments: Optional[str] = None
    conditions: Optional[str] = None
    rejection_reason: Optional[str] = None


class ApprovalResponse(ApprovalBase):
    id: str
    document_id: str
    status: ApprovalStatus
    requested_date: datetime
    response_date: Optional[datetime] = None
    comments: Optional[str] = None
    conditions: Optional[str] = None
    rejection_reason: Optional[str] = None
    delegated_to_id: Optional[str] = None
    delegation_reason: Optional[str] = None
    reminder_sent_count: int
    last_reminder_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SignatureBase(BaseModel):
    signer_name: str
    signer_email: str
    signer_title: Optional[str] = None
    signer_company: Optional[str] = None
    signer_role: Optional[str] = None
    signature_order: int = 1


class SignatureCreate(SignatureBase):
    signer_id: Optional[str] = None


class SignatureUpdate(BaseModel):
    status: SignatureStatus
    decline_reason: Optional[str] = None


class SignatureResponse(SignatureBase):
    id: str
    document_id: str
    signer_id: Optional[str] = None
    status: SignatureStatus
    external_signature_id: Optional[str] = None
    signature_platform: Optional[str] = None
    signature_url: Optional[str] = None
    sent_date: Optional[datetime] = None
    viewed_date: Optional[datetime] = None
    signed_date: Optional[datetime] = None
    declined_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    signature_hash: Optional[str] = None
    ip_address: Optional[str] = None
    authentication_method: Optional[str] = None
    certificate_id: Optional[str] = None
    reminder_count: int
    last_reminder_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: DocumentCategory
    document_type: Optional[str] = None
    is_public: bool = False


class TemplateCreate(TemplateBase):
    template_content: str
    merge_fields: Optional[List[Dict[str, Any]]] = None
    default_values: Optional[Dict[str, Any]] = None
    default_approval_workflow: Optional[List[Dict[str, Any]]] = None
    default_signature_workflow: Optional[List[Dict[str, Any]]] = None
    requires_approval: bool = False
    requires_signature: bool = False
    tags: Optional[List[str]] = None
    industry: Optional[str] = None
    jurisdiction: Optional[str] = None


class TemplateResponse(TemplateBase):
    id: str
    organization_id: str
    template_content: str
    merge_fields: List[Dict[str, Any]]
    default_values: Dict[str, Any]
    is_active: bool
    version: str
    usage_count: int
    last_used_date: Optional[datetime] = None
    default_approval_workflow: List[Dict[str, Any]]
    default_signature_workflow: List[Dict[str, Any]]
    requires_approval: bool
    requires_signature: bool
    tags: List[str]
    industry: Optional[str] = None
    jurisdiction: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ComparisonRequest(BaseModel):
    revised_document_id: str
    comparison_type: str = "version"


class ActivityResponse(BaseModel):
    id: str
    document_id: str
    user_id: Optional[str] = None
    activity_type: str
    activity_date: datetime
    description: Optional[str] = None
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    class Config:
        from_attributes = True


# Document Endpoints

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document_data: DocumentCreate,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Create a new document with file upload."""
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is required"
        )

    # In production, you would upload to cloud storage
    # For now, we'll simulate the file handling
    file_path = f"/uploads/{current_user['organization_id']}/{file.filename}"
    file_url = f"/api/documents/files/{current_user['organization_id']}/{file.filename}"

    document = Document(
        organization_id=current_user["organization_id"],
        title=document_data.title,
        description=document_data.description,
        category=document_data.category,
        document_type=document_data.document_type,
        negotiation_id=document_data.negotiation_id,
        deal_id=document_data.deal_id,
        term_sheet_id=document_data.term_sheet_id,
        file_name=file.filename,
        original_file_name=file.filename,
        file_path=file_path,
        file_url=file_url,
        file_size=file.size if hasattr(file, 'size') else None,
        mime_type=file.content_type,
        access_level=document_data.access_level,
        is_confidential=document_data.is_confidential,
        requires_approval=document_data.requires_approval,
        requires_signature=document_data.requires_signature,
        effective_date=document_data.effective_date,
        expiration_date=document_data.expiration_date,
        due_date=document_data.due_date,
        tags=document_data.tags or [],
        custom_metadata=document_data.custom_metadata or {},
        created_by=current_user["id"]
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # Log activity
    activity = DocumentActivity(
        organization_id=current_user["organization_id"],
        document_id=document.id,
        user_id=current_user["id"],
        activity_type="created",
        description=f"Document '{document.title}' created",
        created_by=current_user["id"]
    )
    db.add(activity)
    db.commit()

    return document


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    negotiation_id: Optional[str] = None,
    deal_id: Optional[str] = None,
    category: Optional[DocumentCategory] = None,
    status_filter: Optional[DocumentStatus] = None,
    current_versions_only: bool = True,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """List documents with optional filters."""
    query = (
        db.query(Document)
        .filter(Document.organization_id == current_user["organization_id"])
        .order_by(Document.created_at.desc())
    )

    if negotiation_id:
        query = query.filter(Document.negotiation_id == negotiation_id)

    if deal_id:
        query = query.filter(Document.deal_id == deal_id)

    if category:
        query = query.filter(Document.category == category)

    if status_filter:
        query = query.filter(Document.status == status_filter)

    if current_versions_only:
        query = query.filter(Document.is_current_version == True)

    documents = query.offset(offset).limit(limit).all()
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Get a specific document."""
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.organization_id == current_user["organization_id"]
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Update view count and last viewed date
    document.view_count += 1
    document.last_viewed_date = datetime.utcnow()

    # Log activity
    activity = DocumentActivity(
        organization_id=current_user["organization_id"],
        document_id=document.id,
        user_id=current_user["id"],
        activity_type="viewed",
        description=f"Document '{document.title}' viewed",
        created_by=current_user["id"]
    )
    db.add(activity)
    db.commit()

    return document


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    updates: DocumentUpdate,
    create_new_version: bool = False,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Update a document with optional versioning."""
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.organization_id == current_user["organization_id"]
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    if create_new_version:
        # Create new version
        new_document = Document(
            organization_id=document.organization_id,
            title=document.title,
            description=document.description,
            category=document.category,
            document_type=document.document_type,
            negotiation_id=document.negotiation_id,
            deal_id=document.deal_id,
            term_sheet_id=document.term_sheet_id,
            file_name=document.file_name,
            original_file_name=document.original_file_name,
            file_path=document.file_path,
            file_url=document.file_url,
            file_size=document.file_size,
            mime_type=document.mime_type,
            version_number=document.version_number + 1,
            is_current_version=True,
            parent_document_id=document.id,
            version_notes=updates.version_notes,
            status=document.status,
            access_level=document.access_level,
            is_confidential=document.is_confidential,
            requires_approval=document.requires_approval,
            requires_signature=document.requires_signature,
            effective_date=document.effective_date,
            expiration_date=document.expiration_date,
            due_date=document.due_date,
            tags=document.tags,
            custom_metadata=document.custom_metadata,
            created_by=current_user["id"]
        )

        # Apply updates to new version
        for field, value in updates.model_dump(exclude_unset=True).items():
            if hasattr(new_document, field) and field != 'version_notes':
                setattr(new_document, field, value)

        # Mark old version as not current
        document.is_current_version = False

        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        # Log activity
        activity = DocumentActivity(
            organization_id=current_user["organization_id"],
            document_id=new_document.id,
            user_id=current_user["id"],
            activity_type="version_created",
            description=f"New version {new_document.version_number} created",
            created_by=current_user["id"]
        )
        db.add(activity)
        db.commit()

        return new_document
    else:
        # Update existing document
        for field, value in updates.model_dump(exclude_unset=True).items():
            if hasattr(document, field) and field != 'version_notes':
                setattr(document, field, value)

        document.updated_by = current_user["id"]
        db.commit()
        db.refresh(document)

        # Log activity
        activity = DocumentActivity(
            organization_id=current_user["organization_id"],
            document_id=document.id,
            user_id=current_user["id"],
            activity_type="updated",
            description=f"Document '{document.title}' updated",
            created_by=current_user["id"]
        )
        db.add(activity)
        db.commit()

        return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Soft delete a document."""
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.organization_id == current_user["organization_id"]
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Soft delete
    document.soft_delete(current_user["id"])

    # Log activity
    activity = DocumentActivity(
        organization_id=current_user["organization_id"],
        document_id=document.id,
        user_id=current_user["id"],
        activity_type="deleted",
        description=f"Document '{document.title}' deleted",
        created_by=current_user["id"]
    )
    db.add(activity)
    db.commit()


@router.get("/{document_id}/versions", response_model=List[DocumentResponse])
async def get_document_versions(
    document_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Get all versions of a document."""
    # Find the root document
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.organization_id == current_user["organization_id"]
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Get all versions
    versions = []

    # Find root document (no parent)
    root_doc = document
    while root_doc.parent_document_id:
        root_doc = (
            db.query(Document)
            .filter(Document.id == root_doc.parent_document_id)
            .first()
        )
        if not root_doc:
            break

    # Collect all versions starting from root
    def collect_versions(doc):
        versions.append(doc)
        children = (
            db.query(Document)
            .filter(Document.parent_document_id == doc.id)
            .order_by(Document.version_number)
            .all()
        )
        for child in children:
            collect_versions(child)

    collect_versions(root_doc)
    return sorted(versions, key=lambda x: x.version_number)


# Approval Endpoints

@router.post("/{document_id}/approvals", response_model=ApprovalResponse, status_code=status.HTTP_201_CREATED)
async def request_approval(
    document_id: str,
    approval_data: ApprovalCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Request approval for a document."""
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.organization_id == current_user["organization_id"]
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    approval = DocumentApproval(
        organization_id=current_user["organization_id"],
        document_id=document_id,
        **approval_data.model_dump(),
        created_by=current_user["id"]
    )

    db.add(approval)

    # Update document status
    if document.status == DocumentStatus.DRAFT:
        document.status = DocumentStatus.PENDING_APPROVAL

    db.commit()
    db.refresh(approval)

    return approval


@router.get("/{document_id}/approvals", response_model=List[ApprovalResponse])
async def list_approvals(
    document_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """List approvals for a document."""
    approvals = (
        db.query(DocumentApproval)
        .filter(
            DocumentApproval.document_id == document_id,
            DocumentApproval.organization_id == current_user["organization_id"]
        )
        .order_by(DocumentApproval.approval_level)
        .all()
    )

    return approvals


@router.patch("/{document_id}/approvals/{approval_id}", response_model=ApprovalResponse)
async def respond_to_approval(
    document_id: str,
    approval_id: str,
    response: ApprovalUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Respond to an approval request."""
    approval = (
        db.query(DocumentApproval)
        .filter(
            DocumentApproval.id == approval_id,
            DocumentApproval.document_id == document_id,
            DocumentApproval.organization_id == current_user["organization_id"]
        )
        .first()
    )

    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )

    # Check if current user is the approver
    if approval.approver_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to respond to this approval"
        )

    # Update approval
    approval.status = response.status
    approval.comments = response.comments
    approval.conditions = response.conditions
    approval.rejection_reason = response.rejection_reason
    approval.response_date = datetime.utcnow()
    approval.updated_by = current_user["id"]

    # Update document status based on approval result
    document = approval.document
    if response.status == ApprovalStatus.APPROVED:
        # Check if all approvals are complete
        all_approvals = (
            db.query(DocumentApproval)
            .filter(DocumentApproval.document_id == document_id)
            .all()
        )

        if all(a.status == ApprovalStatus.APPROVED for a in all_approvals):
            document.status = DocumentStatus.APPROVED
            if document.requires_signature:
                document.status = DocumentStatus.READY_FOR_SIGNATURE

    elif response.status == ApprovalStatus.REJECTED:
        document.status = DocumentStatus.IN_REVIEW

    db.commit()
    db.refresh(approval)

    return approval


# Signature Endpoints

@router.post("/{document_id}/signatures", response_model=SignatureResponse, status_code=status.HTTP_201_CREATED)
async def request_signature(
    document_id: str,
    signature_data: SignatureCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Request signature for a document."""
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.organization_id == current_user["organization_id"]
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    signature = DocumentSignature(
        organization_id=current_user["organization_id"],
        document_id=document_id,
        **signature_data.model_dump(),
        status=SignatureStatus.PENDING,
        created_by=current_user["id"]
    )

    db.add(signature)

    # Update document status
    if document.status in [DocumentStatus.APPROVED, DocumentStatus.READY_FOR_SIGNATURE]:
        document.status = DocumentStatus.IN_SIGNATURE

    db.commit()
    db.refresh(signature)

    return signature


@router.get("/{document_id}/signatures", response_model=List[SignatureResponse])
async def list_signatures(
    document_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """List signatures for a document."""
    signatures = (
        db.query(DocumentSignature)
        .filter(
            DocumentSignature.document_id == document_id,
            DocumentSignature.organization_id == current_user["organization_id"]
        )
        .order_by(DocumentSignature.signature_order)
        .all()
    )

    return signatures


@router.patch("/{document_id}/signatures/{signature_id}", response_model=SignatureResponse)
async def update_signature_status(
    document_id: str,
    signature_id: str,
    update: SignatureUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Update signature status."""
    signature = (
        db.query(DocumentSignature)
        .filter(
            DocumentSignature.id == signature_id,
            DocumentSignature.document_id == document_id,
            DocumentSignature.organization_id == current_user["organization_id"]
        )
        .first()
    )

    if not signature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signature not found"
        )

    # Update signature
    signature.status = update.status
    if update.decline_reason:
        signature.decline_reason = update.decline_reason

    if update.status == SignatureStatus.COMPLETED:
        signature.signed_date = datetime.utcnow()
    elif update.status == SignatureStatus.DECLINED:
        signature.declined_date = datetime.utcnow()

    # Check if all signatures are complete
    document = signature.document
    all_signatures = (
        db.query(DocumentSignature)
        .filter(DocumentSignature.document_id == document_id)
        .all()
    )

    completed_signatures = [s for s in all_signatures if s.status == SignatureStatus.COMPLETED]

    if len(completed_signatures) == len(all_signatures):
        document.status = DocumentStatus.FULLY_EXECUTED
    elif len(completed_signatures) > 0:
        document.status = DocumentStatus.PARTIALLY_SIGNED

    signature.updated_by = current_user["id"]
    db.commit()
    db.refresh(signature)

    return signature


# Template Endpoints

@router.post("/templates", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Create a new document template."""
    template = DocumentTemplate(
        organization_id=current_user["organization_id"],
        **template_data.model_dump(),
        created_by=current_user["id"]
    )

    db.add(template)
    db.commit()
    db.refresh(template)

    return template


@router.get("/templates", response_model=List[TemplateResponse])
async def list_templates(
    category: Optional[DocumentCategory] = None,
    is_active: bool = True,
    include_public: bool = True,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """List document templates."""
    query = db.query(DocumentTemplate)

    if include_public:
        query = query.filter(
            (DocumentTemplate.organization_id == current_user["organization_id"]) |
            (DocumentTemplate.is_public == True)
        )
    else:
        query = query.filter(DocumentTemplate.organization_id == current_user["organization_id"])

    if category:
        query = query.filter(DocumentTemplate.category == category)

    if is_active is not None:
        query = query.filter(DocumentTemplate.is_active == is_active)

    templates = query.order_by(DocumentTemplate.usage_count.desc()).all()
    return templates


# Comparison and Analysis

@router.post("/{document_id}/compare")
async def compare_documents(
    document_id: str,
    comparison_request: ComparisonRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Compare two documents."""
    # Create comparison record
    comparison = DocumentComparison(
        organization_id=current_user["organization_id"],
        original_document_id=document_id,
        revised_document_id=comparison_request.revised_document_id,
        comparison_type=comparison_request.comparison_type,
        # In production, this would run actual document comparison
        changes_detected=True,
        change_count=5,
        changes_summary="5 changes detected including text modifications and formatting updates",
        detailed_changes=[
            {
                "type": "text_change",
                "location": "paragraph 3",
                "old_text": "original text",
                "new_text": "revised text"
            }
        ],
        additions_count=2,
        deletions_count=1,
        modifications_count=2,
        created_by=current_user["id"]
    )

    db.add(comparison)
    db.commit()
    db.refresh(comparison)

    return {
        "comparison_id": comparison.id,
        "changes_detected": comparison.changes_detected,
        "change_count": comparison.change_count,
        "changes_summary": comparison.changes_summary,
        "detailed_changes": comparison.detailed_changes,
        "comparison_date": comparison.comparison_date.isoformat()
    }


@router.get("/{document_id}/activity", response_model=List[ActivityResponse])
async def get_document_activity(
    document_id: str,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Get activity log for a document."""
    activities = (
        db.query(DocumentActivity)
        .filter(
            DocumentActivity.document_id == document_id,
            DocumentActivity.organization_id == current_user["organization_id"]
        )
        .order_by(DocumentActivity.activity_date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return activities


@router.post("/{document_id}/download")
async def download_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_organization_user)
):
    """Download a document (track download activity)."""
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.organization_id == current_user["organization_id"]
        )
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Update download count
    document.download_count += 1
    document.last_downloaded_date = datetime.utcnow()

    # Log activity
    activity = DocumentActivity(
        organization_id=current_user["organization_id"],
        document_id=document.id,
        user_id=current_user["id"],
        activity_type="downloaded",
        description=f"Document '{document.title}' downloaded",
        created_by=current_user["id"]
    )
    db.add(activity)
    db.commit()

    return {
        "download_url": document.file_url,
        "file_name": document.file_name,
        "file_size": document.file_size,
        "mime_type": document.mime_type
    }