"""
BMAD v6 MCP Server CRUD Operations for M&A Deals
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import Deal, ValuationModel
from datetime import datetime

class CRUDDeal:
    def create_deal(
        self,
        db: Session,
        deal_id: str,
        name: str,
        target_company: str,
        deal_type: str,
        deal_value: float = None,
        currency: str = "GBP",
        project_id: str = None
    ) -> Deal:
        """Create a new M&A deal."""
        db_deal = Deal(
            id=deal_id,
            name=name,
            target_company=target_company,
            deal_type=deal_type,
            deal_value=deal_value,
            currency=currency,
            project_id=project_id
        )
        db.add(db_deal)
        db.commit()
        db.refresh(db_deal)
        return db_deal
    
    def get_deal(self, db: Session, deal_id: str) -> Optional[Deal]:
        """Get deal by ID."""
        return db.query(Deal).filter(Deal.id == deal_id).first()
    
    def get_deals(self, db: Session, skip: int = 0, limit: int = 100) -> List[Deal]:
        """Get list of deals."""
        return db.query(Deal).offset(skip).limit(limit).all()
    
    def get_deals_by_status(self, db: Session, status: str) -> List[Deal]:
        """Get deals by status."""
        return db.query(Deal).filter(Deal.status == status).all()
    
    def update_deal_status(self, db: Session, deal_id: str, status: str) -> Optional[Deal]:
        """Update deal status."""
        db_deal = self.get_deal(db, deal_id)
        if db_deal:
            db_deal.status = status
            db_deal.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_deal)
        return db_deal
    
    def update_deal_financials(
        self,
        db: Session,
        deal_id: str,
        revenue: float = None,
        ebitda: float = None,
        multiple: float = None
    ) -> Optional[Deal]:
        """Update deal financial metrics."""
        db_deal = self.get_deal(db, deal_id)
        if db_deal:
            if revenue is not None:
                db_deal.revenue = revenue
            if ebitda is not None:
                db_deal.ebitda = ebitda
            if multiple is not None:
                db_deal.multiple = multiple
            
            db_deal.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_deal)
        return db_deal
    
    def create_valuation_model(
        self,
        db: Session,
        deal_id: str,
        model_type: str,
        **kwargs
    ) -> ValuationModel:
        """Create a valuation model for a deal."""
        db_valuation = ValuationModel(
            deal_id=deal_id,
            model_type=model_type,
            **kwargs
        )
        db.add(db_valuation)
        db.commit()
        db.refresh(db_valuation)
        return db_valuation
    
    def get_valuations_by_deal(self, db: Session, deal_id: str) -> List[ValuationModel]:
        """Get all valuation models for a deal."""
        return db.query(ValuationModel).filter(ValuationModel.deal_id == deal_id).all()
    
    def delete_deal(self, db: Session, deal_id: str) -> bool:
        """Delete deal."""
        db_deal = self.get_deal(db, deal_id)
        if db_deal:
            db.delete(db_deal)
            db.commit()
            return True
        return False

crud_deal = CRUDDeal()
