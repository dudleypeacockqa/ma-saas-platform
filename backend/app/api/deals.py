from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

from app.core.database import get_db
from app.models.models import Deal, Task, Document, DealStage, TaskStatus, User
from app.services.tenant_service import get_current_user, require_deal_manager

router = APIRouter()

# Pydantic models
class DealCreate(BaseModel):
    name: str
    description: Optional[str] = None
    target_company: Optional[str] = None
    deal_value: Optional[Decimal] = None
    currency: str = "GBP"
    expected_close_date: Optional[datetime] = None

class DealUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    stage: Optional[DealStage] = None
    target_company: Optional[str] = None
    deal_value: Optional[Decimal] = None
    currency: Optional[str] = None
    expected_close_date: Optional[datetime] = None

class DealResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    stage: str
    target_company: Optional[str]
    deal_value: Optional[Decimal]
    currency: str
    expected_close_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    task_count: int
    document_count: int

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    priority: str = "medium"
    due_date: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    assignee_id: Optional[int] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    due_date: Optional[datetime]
    assignee_name: Optional[str]
    created_at: datetime
    updated_at: datetime

@router.get("/", response_model=List[DealResponse])
async def get_deals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    stage: Optional[DealStage] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all deals for the current user's tenant"""
    query = db.query(Deal).filter(
        Deal.tenant_id == current_user.tenant_id,
        Deal.is_active == True
    )
    
    if stage:
        query = query.filter(Deal.stage == stage)
    
    deals = query.offset(skip).limit(limit).all()
    
    # Add task and document counts
    deal_responses = []
    for deal in deals:
        task_count = db.query(Task).filter(Task.deal_id == deal.id).count()
        document_count = db.query(Document).filter(Document.deal_id == deal.id).count()
        
        deal_responses.append(DealResponse(
            id=deal.id,
            name=deal.name,
            description=deal.description,
            stage=deal.stage.value,
            target_company=deal.target_company,
            deal_value=deal.deal_value,
            currency=deal.currency,
            expected_close_date=deal.expected_close_date,
            created_at=deal.created_at,
            updated_at=deal.updated_at,
            is_active=deal.is_active,
            task_count=task_count,
            document_count=document_count
        ))
    
    return deal_responses

@router.post("/", response_model=DealResponse)
async def create_deal(
    deal_data: DealCreate,
    current_user: User = Depends(require_deal_manager),
    db: Session = Depends(get_db)
):
    """Create a new deal"""
    deal = Deal(
        tenant_id=current_user.tenant_id,
        name=deal_data.name,
        description=deal_data.description,
        target_company=deal_data.target_company,
        deal_value=deal_data.deal_value,
        currency=deal_data.currency,
        expected_close_date=deal_data.expected_close_date
    )
    
    db.add(deal)
    db.commit()
    db.refresh(deal)
    
    return DealResponse(
        id=deal.id,
        name=deal.name,
        description=deal.description,
        stage=deal.stage.value,
        target_company=deal.target_company,
        deal_value=deal.deal_value,
        currency=deal.currency,
        expected_close_date=deal.expected_close_date,
        created_at=deal.created_at,
        updated_at=deal.updated_at,
        is_active=deal.is_active,
        task_count=0,
        document_count=0
    )

@router.get("/{deal_id}", response_model=DealResponse)
async def get_deal(
    deal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific deal"""
    deal = db.query(Deal).filter(
        Deal.id == deal_id,
        Deal.tenant_id == current_user.tenant_id,
        Deal.is_active == True
    ).first()
    
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )
    
    task_count = db.query(Task).filter(Task.deal_id == deal.id).count()
    document_count = db.query(Document).filter(Document.deal_id == deal.id).count()
    
    return DealResponse(
        id=deal.id,
        name=deal.name,
        description=deal.description,
        stage=deal.stage.value,
        target_company=deal.target_company,
        deal_value=deal.deal_value,
        currency=deal.currency,
        expected_close_date=deal.expected_close_date,
        created_at=deal.created_at,
        updated_at=deal.updated_at,
        is_active=deal.is_active,
        task_count=task_count,
        document_count=document_count
    )

@router.put("/{deal_id}", response_model=DealResponse)
async def update_deal(
    deal_id: int,
    deal_data: DealUpdate,
    current_user: User = Depends(require_deal_manager),
    db: Session = Depends(get_db)
):
    """Update a deal"""
    deal = db.query(Deal).filter(
        Deal.id == deal_id,
        Deal.tenant_id == current_user.tenant_id,
        Deal.is_active == True
    ).first()
    
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )
    
    # Update fields
    for field, value in deal_data.dict(exclude_unset=True).items():
        setattr(deal, field, value)
    
    deal.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(deal)
    
    task_count = db.query(Task).filter(Task.deal_id == deal.id).count()
    document_count = db.query(Document).filter(Document.deal_id == deal.id).count()
    
    return DealResponse(
        id=deal.id,
        name=deal.name,
        description=deal.description,
        stage=deal.stage.value,
        target_company=deal.target_company,
        deal_value=deal.deal_value,
        currency=deal.currency,
        expected_close_date=deal.expected_close_date,
        created_at=deal.created_at,
        updated_at=deal.updated_at,
        is_active=deal.is_active,
        task_count=task_count,
        document_count=document_count
    )

@router.delete("/{deal_id}")
async def delete_deal(
    deal_id: int,
    current_user: User = Depends(require_deal_manager),
    db: Session = Depends(get_db)
):
    """Soft delete a deal"""
    deal = db.query(Deal).filter(
        Deal.id == deal_id,
        Deal.tenant_id == current_user.tenant_id,
        Deal.is_active == True
    ).first()
    
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )
    
    deal.is_active = False
    deal.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Deal deleted successfully"}

# Task endpoints for deals
@router.get("/{deal_id}/tasks", response_model=List[TaskResponse])
async def get_deal_tasks(
    deal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all tasks for a specific deal"""
    # Verify deal access
    deal = db.query(Deal).filter(
        Deal.id == deal_id,
        Deal.tenant_id == current_user.tenant_id,
        Deal.is_active == True
    ).first()
    
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )
    
    tasks = db.query(Task).filter(Task.deal_id == deal_id).all()
    
    task_responses = []
    for task in tasks:
        assignee_name = None
        if task.assignee_id:
            assignee = db.query(User).filter(User.id == task.assignee_id).first()
            if assignee:
                assignee_name = assignee.full_name
        
        task_responses.append(TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status.value,
            priority=task.priority,
            due_date=task.due_date,
            assignee_name=assignee_name,
            created_at=task.created_at,
            updated_at=task.updated_at
        ))
    
    return task_responses

@router.post("/{deal_id}/tasks", response_model=TaskResponse)
async def create_deal_task(
    deal_id: int,
    task_data: TaskCreate,
    current_user: User = Depends(require_deal_manager),
    db: Session = Depends(get_db)
):
    """Create a new task for a deal"""
    # Verify deal access
    deal = db.query(Deal).filter(
        Deal.id == deal_id,
        Deal.tenant_id == current_user.tenant_id,
        Deal.is_active == True
    ).first()
    
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )
    
    # Verify assignee belongs to same tenant if specified
    if task_data.assignee_id:
        assignee = db.query(User).filter(
            User.id == task_data.assignee_id,
            User.tenant_id == current_user.tenant_id,
            User.is_active == True
        ).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid assignee"
            )
    
    task = Task(
        deal_id=deal_id,
        title=task_data.title,
        description=task_data.description,
        assignee_id=task_data.assignee_id,
        priority=task_data.priority,
        due_date=task_data.due_date
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    assignee_name = None
    if task.assignee_id:
        assignee = db.query(User).filter(User.id == task.assignee_id).first()
        if assignee:
            assignee_name = assignee.full_name
    
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status.value,
        priority=task.priority,
        due_date=task.due_date,
        assignee_name=assignee_name,
        created_at=task.created_at,
        updated_at=task.updated_at
    )
