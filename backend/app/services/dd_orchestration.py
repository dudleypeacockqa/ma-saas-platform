"""
Due Diligence Orchestration Services
Business logic for DD process management, checklist generation, and progress tracking
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from uuid import UUID
import logging

from app.models.due_diligence import (
    DueDiligenceChecklist, DueDiligenceItem, DueDiligenceProcess,
    DocumentRequest, DueDiligenceDocument, RiskAssessment,
    DocumentCategory, DocumentStatus, RiskLevel, ChecklistType
)
from app.models.deal import Deal, DealStage

logger = logging.getLogger(__name__)


class DueDiligenceProcessService:
    """Service for managing due diligence processes"""

    @staticmethod
    async def create_process(
        db: Session,
        deal_id: UUID,
        organization_id: UUID,
        process_data: Dict[str, Any],
        user_id: str
    ) -> DueDiligenceProcess:
        """
        Create a new due diligence process for a deal

        Args:
            db: Database session
            deal_id: ID of the deal
            organization_id: Organization ID
            process_data: Process configuration
            user_id: User creating the process

        Returns:
            Created DueDiligenceProcess
        """
        # Verify deal exists and is in appropriate stage
        deal = db.query(Deal).filter(
            Deal.id == deal_id,
            Deal.organization_id == organization_id
        ).first()

        if not deal:
            raise ValueError("Deal not found")

        if deal.stage not in [DealStage.PRELIMINARY_ANALYSIS, DealStage.VALUATION, DealStage.DUE_DILIGENCE]:
            raise ValueError(f"Deal must be in preliminary analysis, valuation, or due diligence stage (currently: {deal.stage})")

        # Check if process already exists
        existing = db.query(DueDiligenceProcess).filter(
            DueDiligenceProcess.deal_id == deal_id,
            DueDiligenceProcess.deleted_at.is_(None)
        ).first()

        if existing:
            raise ValueError("Due diligence process already exists for this deal")

        # Get or create checklist
        checklist_id = process_data.get("checklist_id")
        if not checklist_id:
            # Auto-generate checklist based on deal industry
            checklist = await ChecklistManagementService.generate_checklist_for_deal(
                db, deal, organization_id
            )
            checklist_id = checklist.id

        # Create process
        process = DueDiligenceProcess(
            deal_id=deal_id,
            organization_id=organization_id,
            checklist_id=checklist_id,
            name=process_data.get("name") or f"DD Process: {deal.title}",
            start_date=process_data.get("start_date") or datetime.utcnow(),
            target_completion_date=process_data.get("target_completion_date") or (datetime.utcnow() + timedelta(days=60)),
            lead_reviewer_id=process_data.get("lead_reviewer_id") or user_id,
            assigned_team=process_data.get("assigned_team", []),
            notes=process_data.get("notes")
        )

        db.add(process)
        db.commit()
        db.refresh(process)

        # Update deal stage if needed
        if deal.stage != DealStage.DUE_DILIGENCE:
            deal.stage = DealStage.DUE_DILIGENCE
            db.commit()

        # Auto-generate document requests
        if process_data.get("auto_generate_requests", True):
            await DocumentRequestService.generate_requests_from_checklist(
                db, process.id, user_id
            )

        return process

    @staticmethod
    async def update_progress(
        db: Session,
        process_id: UUID,
        organization_id: UUID
    ) -> DueDiligenceProcess:
        """
        Recalculate and update process progress

        Args:
            db: Database session
            process_id: Process ID
            organization_id: Organization ID

        Returns:
            Updated DueDiligenceProcess
        """
        process = db.query(DueDiligenceProcess).filter(
            DueDiligenceProcess.id == process_id,
            DueDiligenceProcess.organization_id == organization_id
        ).first()

        if not process:
            raise ValueError("Process not found")

        # Calculate document request completion
        total_requests = db.query(DocumentRequest).filter(
            DocumentRequest.process_id == process_id
        ).count()

        completed_requests = db.query(DocumentRequest).filter(
            DocumentRequest.process_id == process_id,
            DocumentRequest.status.in_([DocumentStatus.REVIEWED, DocumentStatus.APPROVED])
        ).count()

        # Calculate checklist item completion
        checklist_items = db.query(DueDiligenceItem).filter(
            DueDiligenceItem.checklist_id == process.checklist_id
        ).all()

        # Calculate weighted completion
        if total_requests > 0:
            completion = (completed_requests / total_requests) * 100
        else:
            completion = 0.0

        process.completion_percentage = round(completion, 2)

        # Determine status based on completion and dates
        if process.completion_percentage >= 100:
            process.status = "completed"
            if not process.actual_completion_date:
                process.actual_completion_date = datetime.utcnow()
        elif process.target_completion_date and datetime.utcnow() > process.target_completion_date:
            process.status = "overdue"
        elif process.completion_percentage > 0:
            process.status = "in_progress"
        else:
            process.status = "not_started"

        # Update risk score
        await RiskScoringService.calculate_overall_risk(db, process_id)

        db.commit()
        db.refresh(process)

        return process

    @staticmethod
    async def assign_team_members(
        db: Session,
        process_id: UUID,
        organization_id: UUID,
        team_member_ids: List[str],
        lead_reviewer_id: Optional[str] = None
    ) -> DueDiligenceProcess:
        """
        Assign team members to DD process

        Args:
            db: Database session
            process_id: Process ID
            organization_id: Organization ID
            team_member_ids: List of user IDs to assign
            lead_reviewer_id: Optional lead reviewer ID

        Returns:
            Updated DueDiligenceProcess
        """
        process = db.query(DueDiligenceProcess).filter(
            DueDiligenceProcess.id == process_id,
            DueDiligenceProcess.organization_id == organization_id
        ).first()

        if not process:
            raise ValueError("Process not found")

        process.assigned_team = team_member_ids

        if lead_reviewer_id:
            process.lead_reviewer_id = lead_reviewer_id

        db.commit()
        db.refresh(process)

        return process


class ChecklistManagementService:
    """Service for managing DD checklists and templates"""

    @staticmethod
    async def create_template(
        db: Session,
        organization_id: UUID,
        template_data: Dict[str, Any],
        user_id: str
    ) -> DueDiligenceChecklist:
        """
        Create a new checklist template

        Args:
            db: Database session
            organization_id: Organization ID
            template_data: Template configuration
            user_id: User creating template

        Returns:
            Created DueDiligenceChecklist
        """
        checklist = DueDiligenceChecklist(
            organization_id=organization_id,
            name=template_data["name"],
            description=template_data.get("description"),
            checklist_type=template_data["checklist_type"],
            industry=template_data.get("industry"),
            is_template=True,
            is_active=True,
            categories=template_data.get("categories", []),
            custom_fields=template_data.get("custom_fields", {})
        )

        db.add(checklist)
        db.commit()
        db.refresh(checklist)

        # Create checklist items
        items = template_data.get("items", [])
        for idx, item_data in enumerate(items):
            item = DueDiligenceItem(
                organization_id=organization_id,
                checklist_id=checklist.id,
                category=item_data["category"],
                title=item_data["title"],
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

    @staticmethod
    async def generate_checklist_for_deal(
        db: Session,
        deal: Deal,
        organization_id: UUID
    ) -> DueDiligenceChecklist:
        """
        Auto-generate checklist based on deal characteristics

        Args:
            db: Database session
            deal: Deal object
            organization_id: Organization ID

        Returns:
            Generated DueDiligenceChecklist
        """
        # Determine checklist type based on industry
        checklist_type = ChecklistManagementService._determine_checklist_type(
            deal.target_industry
        )

        # Look for existing template
        template = db.query(DueDiligenceChecklist).filter(
            DueDiligenceChecklist.organization_id == organization_id,
            DueDiligenceChecklist.checklist_type == checklist_type,
            DueDiligenceChecklist.is_template == True,
            DueDiligenceChecklist.is_active == True
        ).order_by(DueDiligenceChecklist.created_at.desc()).first()

        if not template:
            # Create default template
            template = await ChecklistManagementService._create_default_template(
                db, organization_id, checklist_type, deal.target_industry
            )

        # Clone template for this deal
        checklist = DueDiligenceChecklist(
            organization_id=organization_id,
            name=f"{deal.title} - Due Diligence Checklist",
            description=f"Generated checklist for {deal.target_company_name}",
            checklist_type=checklist_type,
            industry=deal.target_industry,
            is_template=False,
            is_active=True,
            categories=template.categories,
            custom_fields=template.custom_fields,
            parent_template_id=template.id
        )

        db.add(checklist)
        db.commit()
        db.refresh(checklist)

        # Clone items from template
        template_items = db.query(DueDiligenceItem).filter(
            DueDiligenceItem.checklist_id == template.id
        ).order_by(DueDiligenceItem.order_index).all()

        for item in template_items:
            cloned_item = DueDiligenceItem(
                organization_id=organization_id,
                checklist_id=checklist.id,
                category=item.category,
                title=item.title,
                description=item.description,
                is_required=item.is_required,
                order_index=item.order_index,
                document_types=item.document_types,
                validation_rules=item.validation_rules,
                review_guidelines=item.review_guidelines,
                risk_weight=item.risk_weight,
                critical_item=item.critical_item
            )
            db.add(cloned_item)

        db.commit()

        # Update template usage
        template.usage_count += 1
        template.last_used_at = datetime.utcnow()
        db.commit()

        return checklist

    @staticmethod
    def _determine_checklist_type(industry: Optional[str]) -> ChecklistType:
        """Determine checklist type based on industry"""
        if not industry:
            return ChecklistType.CUSTOM

        industry_lower = industry.lower()

        if "tech" in industry_lower or "software" in industry_lower or "saas" in industry_lower:
            return ChecklistType.B2B_SAAS
        elif "health" in industry_lower or "medical" in industry_lower:
            return ChecklistType.HEALTHCARE
        elif "manufact" in industry_lower:
            return ChecklistType.MANUFACTURING
        elif "retail" in industry_lower or "ecommerce" in industry_lower:
            return ChecklistType.RETAIL
        elif "financ" in industry_lower or "bank" in industry_lower:
            return ChecklistType.FINANCIAL_SERVICES
        elif "real estate" in industry_lower or "property" in industry_lower:
            return ChecklistType.REAL_ESTATE
        elif "energy" in industry_lower or "utilities" in industry_lower:
            return ChecklistType.ENERGY
        elif "marketplace" in industry_lower:
            return ChecklistType.MARKETPLACE
        else:
            return ChecklistType.CUSTOM

    @staticmethod
    async def _create_default_template(
        db: Session,
        organization_id: UUID,
        checklist_type: ChecklistType,
        industry: Optional[str]
    ) -> DueDiligenceChecklist:
        """Create default template for checklist type"""
        template = DueDiligenceChecklist(
            organization_id=organization_id,
            name=f"Default {checklist_type.value.replace('_', ' ').title()} Template",
            description=f"Standard due diligence checklist for {checklist_type.value} industry",
            checklist_type=checklist_type,
            industry=industry,
            is_template=True,
            is_active=True,
            categories=[cat.value for cat in DocumentCategory]
        )

        db.add(template)
        db.commit()
        db.refresh(template)

        # Add standard items
        standard_items = ChecklistManagementService._get_standard_items(checklist_type)
        for idx, item_data in enumerate(standard_items):
            item = DueDiligenceItem(
                organization_id=organization_id,
                checklist_id=template.id,
                **item_data,
                order_index=idx
            )
            db.add(item)

        db.commit()
        db.refresh(template)

        return template

    @staticmethod
    def _get_standard_items(checklist_type: ChecklistType) -> List[Dict]:
        """Get standard checklist items for type"""
        # Financial items (common to all)
        financial_items = [
            {
                "category": DocumentCategory.FINANCIAL,
                "title": "Audited Financial Statements (3 years)",
                "description": "Complete audited financials for last 3 fiscal years",
                "is_required": True,
                "critical_item": True,
                "risk_weight": 2.0
            },
            {
                "category": DocumentCategory.FINANCIAL,
                "title": "Management Accounts (Latest)",
                "description": "Most recent monthly/quarterly management accounts",
                "is_required": True,
                "risk_weight": 1.5
            },
            {
                "category": DocumentCategory.FINANCIAL,
                "title": "Cash Flow Statements",
                "description": "Historical and projected cash flows",
                "is_required": True,
                "risk_weight": 1.5
            }
        ]

        # Legal items (common to all)
        legal_items = [
            {
                "category": DocumentCategory.LEGAL,
                "title": "Articles of Incorporation",
                "description": "Certificate of incorporation and bylaws",
                "is_required": True,
                "critical_item": True,
                "risk_weight": 2.0
            },
            {
                "category": DocumentCategory.LEGAL,
                "title": "Cap Table",
                "description": "Complete capitalization table with ownership breakdown",
                "is_required": True,
                "critical_item": True,
                "risk_weight": 2.0
            },
            {
                "category": DocumentCategory.LEGAL,
                "title": "Material Contracts",
                "description": "All contracts > $100k or strategic importance",
                "is_required": True,
                "risk_weight": 1.8
            }
        ]

        # Tax items
        tax_items = [
            {
                "category": DocumentCategory.TAX,
                "title": "Tax Returns (3 years)",
                "description": "Corporate tax returns for last 3 years",
                "is_required": True,
                "risk_weight": 1.5
            }
        ]

        # HR items
        hr_items = [
            {
                "category": DocumentCategory.HR,
                "title": "Employee List",
                "description": "Complete employee roster with compensation",
                "is_required": True,
                "risk_weight": 1.2
            },
            {
                "category": DocumentCategory.HR,
                "title": "Key Employment Agreements",
                "description": "Contracts for executives and key employees",
                "is_required": True,
                "risk_weight": 1.5
            }
        ]

        # Type-specific items
        if checklist_type == ChecklistType.B2B_SAAS:
            tech_items = [
                {
                    "category": DocumentCategory.IT,
                    "title": "Technology Stack Documentation",
                    "description": "Complete architecture and technology overview",
                    "is_required": True,
                    "risk_weight": 1.5
                },
                {
                    "category": DocumentCategory.INTELLECTUAL_PROPERTY,
                    "title": "Source Code Repository Access",
                    "description": "Read-only access to code repositories",
                    "is_required": True,
                    "critical_item": True,
                    "risk_weight": 2.0
                },
                {
                    "category": DocumentCategory.COMMERCIAL,
                    "title": "Customer List & ARR Breakdown",
                    "description": "All customers with ARR/MRR details",
                    "is_required": True,
                    "critical_item": True,
                    "risk_weight": 2.0
                }
            ]
            return financial_items + legal_items + tax_items + hr_items + tech_items

        # Return basic set for other types
        return financial_items + legal_items + tax_items + hr_items


class DocumentRequestService:
    """Service for managing document requests"""

    @staticmethod
    async def generate_requests_from_checklist(
        db: Session,
        process_id: UUID,
        user_id: str
    ) -> List[DocumentRequest]:
        """
        Auto-generate document requests from checklist items

        Args:
            db: Database session
            process_id: DD process ID
            user_id: User generating requests

        Returns:
            List of created DocumentRequest objects
        """
        process = db.query(DueDiligenceProcess).filter(
            DueDiligenceProcess.id == process_id
        ).first()

        if not process:
            raise ValueError("Process not found")

        # Get checklist items
        items = db.query(DueDiligenceItem).filter(
            DueDiligenceItem.checklist_id == process.checklist_id
        ).order_by(DueDiligenceItem.order_index).all()

        requests = []
        for item in items:
            request = DocumentRequest(
                organization_id=process.organization_id,
                process_id=process_id,
                checklist_item_id=item.id,
                title=item.title,
                description=item.description,
                category=item.category,
                status=DocumentStatus.NOT_REQUESTED,
                priority="critical" if item.critical_item else ("high" if item.is_required else "normal"),
                requested_by=user_id,
                requested_date=datetime.utcnow(),
                due_date=process.target_completion_date
            )
            db.add(request)
            requests.append(request)

        db.commit()

        return requests


class RiskScoringService:
    """Service for calculating risk scores"""

    @staticmethod
    async def calculate_overall_risk(
        db: Session,
        process_id: UUID
    ) -> float:
        """
        Calculate overall risk score for DD process

        Args:
            db: Database session
            process_id: DD process ID

        Returns:
            Risk score (0-100)
        """
        process = db.query(DueDiligenceProcess).filter(
            DueDiligenceProcess.id == process_id
        ).first()

        if not process:
            return 0.0

        # Get all document reviews
        reviews = db.query(DocumentReview).filter(
            DocumentReview.process_id == process_id
        ).all()

        if not reviews:
            process.overall_risk_score = 0.0
            process.risk_level = RiskLevel.NONE
            db.commit()
            return 0.0

        # Calculate weighted risk score
        risk_scores = {
            RiskLevel.CRITICAL: 100,
            RiskLevel.HIGH: 75,
            RiskLevel.MEDIUM: 50,
            RiskLevel.LOW: 25,
            RiskLevel.NONE: 0
        }

        total_score = sum(risk_scores.get(review.risk_level, 0) for review in reviews)
        avg_score = total_score / len(reviews)

        # Determine risk level
        if avg_score >= 75:
            risk_level = RiskLevel.CRITICAL
        elif avg_score >= 50:
            risk_level = RiskLevel.HIGH
        elif avg_score >= 25:
            risk_level = RiskLevel.MEDIUM
        elif avg_score > 0:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.NONE

        process.overall_risk_score = round(avg_score, 2)
        process.risk_level = risk_level

        db.commit()

        return avg_score


class ProgressTrackingService:
    """Service for tracking DD progress and milestones"""

    @staticmethod
    async def get_completion_stats(
        db: Session,
        process_id: UUID
    ) -> Dict[str, Any]:
        """
        Get detailed completion statistics

        Args:
            db: Database session
            process_id: DD process ID

        Returns:
            Dictionary with completion statistics
        """
        process = db.query(DueDiligenceProcess).filter(
            DueDiligenceProcess.id == process_id
        ).first()

        if not process:
            raise ValueError("Process not found")

        # Document request stats
        total_requests = db.query(DocumentRequest).filter(
            DocumentRequest.process_id == process_id
        ).count()

        requests_by_status = db.query(
            DocumentRequest.status,
            func.count(DocumentRequest.id)
        ).filter(
            DocumentRequest.process_id == process_id
        ).group_by(DocumentRequest.status).all()

        # Document stats
        total_documents = db.query(DueDiligenceDocument).filter(
            DueDiligenceDocument.process_id == process_id
        ).count()

        reviewed_documents = db.query(DueDiligenceDocument).filter(
            DueDiligenceDocument.process_id == process_id,
            DueDiligenceDocument.review_status.in_([
                DocumentStatus.REVIEWED,
                DocumentStatus.APPROVED
            ])
        ).count()

        # Category completion
        categories_stats = db.query(
            DocumentRequest.category,
            func.count(DocumentRequest.id).label("total"),
            func.sum(
                func.cast(
                    DocumentRequest.status.in_([
                        DocumentStatus.REVIEWED,
                        DocumentStatus.APPROVED
                    ]), db.Integer
                )
            ).label("completed")
        ).filter(
            DocumentRequest.process_id == process_id
        ).group_by(DocumentRequest.category).all()

        return {
            "process_id": str(process_id),
            "completion_percentage": process.completion_percentage,
            "status": process.status,
            "documents": {
                "total": total_documents,
                "reviewed": reviewed_documents,
                "review_rate": (reviewed_documents / total_documents * 100) if total_documents > 0 else 0
            },
            "requests": {
                "total": total_requests,
                "by_status": {status.value: count for status, count in requests_by_status}
            },
            "categories": [
                {
                    "category": cat.value,
                    "total": total,
                    "completed": completed or 0,
                    "completion_rate": ((completed or 0) / total * 100) if total > 0 else 0
                }
                for cat, total, completed in categories_stats
            ],
            "risk": {
                "overall_score": process.overall_risk_score,
                "level": process.risk_level.value if process.risk_level else "none"
            },
            "timeline": {
                "start_date": process.start_date.isoformat() if process.start_date else None,
                "target_completion": process.target_completion_date.isoformat() if process.target_completion_date else None,
                "actual_completion": process.actual_completion_date.isoformat() if process.actual_completion_date else None,
                "days_remaining": (process.target_completion_date - datetime.utcnow()).days if process.target_completion_date else None
            }
        }
