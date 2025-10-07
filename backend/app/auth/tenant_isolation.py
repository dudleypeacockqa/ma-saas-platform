"""
Tenant Isolation Module
Ensures strict data isolation between organizations in database queries
"""

from typing import Optional, Any, List, Dict, Type
from sqlalchemy import select, and_, or_, Column
from sqlalchemy.orm import Session, Query
from sqlalchemy.ext.declarative import declarative_base
from fastapi import Depends, HTTPException, status
from ..core.database import get_db
from .clerk_auth import ClerkUser, get_current_organization_user
import logging

logger = logging.getLogger(__name__)


class TenantIsolationMixin:
    """
    Mixin for SQLAlchemy models to add tenant isolation
    Models using this mixin must have an organization_id column
    """
    organization_id: Column


class TenantAwareQuery:
    """
    Helper class for building tenant-aware database queries
    Automatically filters queries by organization_id
    """

    def __init__(self, db: Session, organization_id: str):
        self.db = db
        self.organization_id = organization_id

    def query(self, model: Type[TenantIsolationMixin]) -> Query:
        """Create a query filtered by organization_id"""
        if not hasattr(model, 'organization_id'):
            raise ValueError(f"Model {model.__name__} does not have organization_id column")

        return self.db.query(model).filter(
            model.organization_id == self.organization_id
        )

    def get(self, model: Type[TenantIsolationMixin], id: Any) -> Optional[Any]:
        """Get a single record by ID, filtered by organization"""
        return self.query(model).filter(model.id == id).first()

    def get_or_404(self, model: Type[TenantIsolationMixin], id: Any) -> Any:
        """Get a record or raise 404 if not found"""
        record = self.get(model, id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{model.__name__} not found"
            )
        return record

    def list(
        self,
        model: Type[TenantIsolationMixin],
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict] = None
    ) -> List[Any]:
        """List records with pagination and optional filters"""
        query = self.query(model)

        if filters:
            for key, value in filters.items():
                if hasattr(model, key):
                    query = query.filter(getattr(model, key) == value)

        return query.offset(skip).limit(limit).all()

    def count(self, model: Type[TenantIsolationMixin], filters: Optional[Dict] = None) -> int:
        """Count records with optional filters"""
        query = self.query(model)

        if filters:
            for key, value in filters.items():
                if hasattr(model, key):
                    query = query.filter(getattr(model, key) == value)

        return query.count()

    def create(self, model: Type[TenantIsolationMixin], **kwargs) -> Any:
        """Create a new record with organization_id automatically set"""
        kwargs['organization_id'] = self.organization_id
        db_obj = model(**kwargs)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(
        self,
        model: Type[TenantIsolationMixin],
        id: Any,
        **kwargs
    ) -> Optional[Any]:
        """Update a record, ensuring it belongs to the organization"""
        db_obj = self.get_or_404(model, id)

        # Prevent changing organization_id
        if 'organization_id' in kwargs:
            del kwargs['organization_id']

        for key, value in kwargs.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)

        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, model: Type[TenantIsolationMixin], id: Any) -> bool:
        """Delete a record, ensuring it belongs to the organization"""
        db_obj = self.get_or_404(model, id)
        self.db.delete(db_obj)
        self.db.commit()
        return True

    def bulk_create(
        self,
        model: Type[TenantIsolationMixin],
        objects: List[Dict]
    ) -> List[Any]:
        """Bulk create records with organization_id"""
        db_objects = []
        for obj_data in objects:
            obj_data['organization_id'] = self.organization_id
            db_objects.append(model(**obj_data))

        self.db.add_all(db_objects)
        self.db.commit()

        for obj in db_objects:
            self.db.refresh(obj)

        return db_objects

    def exists(self, model: Type[TenantIsolationMixin], **filters) -> bool:
        """Check if a record exists with given filters"""
        query = self.query(model)
        for key, value in filters.items():
            if hasattr(model, key):
                query = query.filter(getattr(model, key) == value)
        return query.first() is not None


class PersonalDataQuery:
    """
    Helper class for personal data that's not tied to organizations
    Used for user's personal workspace when not in an organization context
    """

    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id

    def query(self, model: Any) -> Query:
        """Create a query filtered by user_id"""
        if not hasattr(model, 'user_id'):
            raise ValueError(f"Model {model.__name__} does not have user_id column")

        # For personal data, organization_id should be NULL
        query = self.db.query(model).filter(
            and_(
                model.user_id == self.user_id,
                model.organization_id.is_(None)
            )
        )
        return query

    # Similar methods as TenantAwareQuery but for personal data
    def get(self, model: Any, id: Any) -> Optional[Any]:
        return self.query(model).filter(model.id == id).first()

    def list(self, model: Any, skip: int = 0, limit: int = 100) -> List[Any]:
        return self.query(model).offset(skip).limit(limit).all()

    def create(self, model: Any, **kwargs) -> Any:
        kwargs['user_id'] = self.user_id
        kwargs['organization_id'] = None  # Explicitly set to None for personal data
        db_obj = model(**kwargs)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj


# Dependency functions
def get_tenant_db(
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_organization_user)
) -> Session:
    """
    Dependency that returns a database session with tenant context
    This is a simplified version that just returns the session
    The actual filtering happens in the models/queries
    """
    # Store the organization_id in the session for reference
    db.info = {"organization_id": current_user.organization_id}
    return db


def get_tenant_query(
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_organization_user)
) -> TenantAwareQuery:
    """
    Dependency that provides a TenantAwareQuery instance
    Use this for all organization-scoped data access
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization context required"
        )
    return TenantAwareQuery(db, current_user.organization_id)


def get_personal_query(
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_organization_user)
) -> PersonalDataQuery:
    """
    Dependency that provides a PersonalDataQuery instance
    Use this for personal workspace data
    """
    return PersonalDataQuery(db, current_user.user_id)


def get_flexible_query(
    db: Session = Depends(get_db),
    current_user: ClerkUser = Depends(get_current_organization_user)
) -> TenantAwareQuery | PersonalDataQuery:
    """
    Dependency that provides either TenantAwareQuery or PersonalDataQuery
    based on whether user is in an organization context
    """
    if current_user.organization_id:
        return TenantAwareQuery(db, current_user.organization_id)
    else:
        return PersonalDataQuery(db, current_user.user_id)


# Security validators
def validate_organization_access(
    organization_id: str,
    current_user: ClerkUser = Depends(get_current_organization_user)
) -> None:
    """Validate that user has access to the specified organization"""
    if current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )


def validate_cross_tenant_access(
    source_org_id: str,
    target_org_id: str,
    current_user: ClerkUser = Depends(get_current_organization_user)
) -> None:
    """
    Validate cross-tenant access for special operations
    (e.g., M&A deal between two organizations)
    """
    # Check if user's organization is either source or target
    if current_user.organization_id not in [source_org_id, target_org_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to this cross-organization operation"
        )

    # Additional checks can be added here:
    # - Check if there's an active deal/partnership between orgs
    # - Check user's role/permissions for cross-org operations
    # - Log the cross-tenant access for audit


# Audit logging for tenant operations
class TenantAuditLog:
    """Log tenant-sensitive operations for compliance and security"""

    @staticmethod
    def log_access(
        user_id: str,
        organization_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        db: Session
    ):
        """Log a tenant data access event"""
        # Implementation would depend on your audit log model
        log_entry = {
            "user_id": user_id,
            "organization_id": organization_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action,
            "timestamp": datetime.utcnow()
        }
        logger.info(f"Tenant access: {log_entry}")
        # Save to database audit table if needed

    @staticmethod
    def log_violation(
        user_id: str,
        attempted_org_id: str,
        actual_org_id: str,
        resource_type: str,
        db: Session
    ):
        """Log a tenant isolation violation attempt"""
        log_entry = {
            "user_id": user_id,
            "attempted_org_id": attempted_org_id,
            "actual_org_id": actual_org_id,
            "resource_type": resource_type,
            "timestamp": datetime.utcnow(),
            "severity": "HIGH"
        }
        logger.error(f"Tenant isolation violation: {log_entry}")
        # Save to database and potentially alert administrators


# Example usage in endpoints:
"""
from fastapi import APIRouter, Depends
from .auth.tenant_isolation import get_tenant_query, TenantAwareQuery
from .models import Deal

router = APIRouter()

@router.get("/deals")
async def list_deals(
    tenant_query: TenantAwareQuery = Depends(get_tenant_query),
    skip: int = 0,
    limit: int = 100
):
    # This will only return deals for the user's organization
    deals = tenant_query.list(Deal, skip=skip, limit=limit)
    return deals

@router.post("/deals")
async def create_deal(
    deal_data: DealCreate,
    tenant_query: TenantAwareQuery = Depends(get_tenant_query)
):
    # Organization ID is automatically set
    deal = tenant_query.create(Deal, **deal_data.dict())
    return deal

@router.get("/deals/{deal_id}")
async def get_deal(
    deal_id: int,
    tenant_query: TenantAwareQuery = Depends(get_tenant_query)
):
    # Will return 404 if deal doesn't exist or belongs to another org
    deal = tenant_query.get_or_404(Deal, deal_id)
    return deal
"""

from datetime import datetime