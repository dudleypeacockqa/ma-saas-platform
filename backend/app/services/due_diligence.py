"""
Enhanced Due Diligence Service
Automated checklist generation, document analysis, and risk assessment
"""
import asyncio
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import numpy as np
import pandas as pd
from enum import Enum
import hashlib
import json
import logging
from pathlib import Path

from app.models.due_diligence import (
    DueDiligenceChecklist, DueDiligenceItem, DueDiligenceProcess,
    DocumentRequest, DueDiligenceDocument, DocumentReview,
    RiskAssessment, DocumentCategory, DocumentStatus,
    RiskLevel, ChecklistType
)
from app.models.deal import Deal, DealType, DealStage
from app.models.transactions import VendorManagement, VendorType

logger = logging.getLogger(__name__)

class DueDiligenceService:
    """
    Comprehensive due diligence orchestration service
    """

    def __init__(self, db: Session):
        self.db = db
        self.checklist_templates = self._load_checklist_templates()

    def _load_checklist_templates(self) -> Dict[str, Dict]:
        """Load industry-specific checklist templates"""
        return {
            ChecklistType.TECHNOLOGY: {
                "name": "Technology Company Due Diligence",
                "categories": {
                    DocumentCategory.FINANCIAL: [
                        "Three years audited financial statements",
                        "Management accounts and KPI dashboards",
                        "Revenue recognition policies",
                        "Customer contracts and pricing",
                        "Accounts receivable aging",
                        "Cash flow projections",
                        "Cap table and equity agreements",
                        "Debt agreements and covenants"
                    ],
                    DocumentCategory.LEGAL: [
                        "Corporate structure and ownership",
                        "Material contracts and agreements",
                        "Intellectual property portfolio",
                        "Employment agreements",
                        "Litigation history and pending claims",
                        "Regulatory compliance records",
                        "Data privacy and security policies"
                    ],
                    DocumentCategory.OPERATIONAL: [
                        "Product roadmap and development pipeline",
                        "Technology architecture documentation",
                        "Source code and repositories",
                        "Third-party licenses and dependencies",
                        "Infrastructure and hosting agreements",
                        "Disaster recovery and business continuity",
                        "Customer support metrics"
                    ],
                    DocumentCategory.COMMERCIAL: [
                        "Customer list and concentration analysis",
                        "Sales pipeline and conversion metrics",
                        "Market analysis and competitive positioning",
                        "Partner and channel agreements",
                        "Marketing strategy and CAC/LTV metrics",
                        "Customer satisfaction scores",
                        "Churn analysis and retention metrics"
                    ],
                    DocumentCategory.HR: [
                        "Organization chart and headcount",
                        "Employee census and compensation",
                        "Benefits and retirement plans",
                        "Key employee retention agreements",
                        "Employee handbook and policies",
                        "Training and development programs",
                        "Culture assessment results"
                    ],
                    DocumentCategory.IT: [
                        "IT systems inventory",
                        "Software licenses and subscriptions",
                        "Cybersecurity assessments",
                        "Data architecture and governance",
                        "Integration requirements",
                        "Technical debt assessment",
                        "Development methodology"
                    ]
                },
                "risk_weights": {
                    DocumentCategory.FINANCIAL: 0.25,
                    DocumentCategory.LEGAL: 0.20,
                    DocumentCategory.OPERATIONAL: 0.20,
                    DocumentCategory.COMMERCIAL: 0.15,
                    DocumentCategory.IT: 0.10,
                    DocumentCategory.HR: 0.10
                }
            },
            ChecklistType.MANUFACTURING: {
                "name": "Manufacturing Company Due Diligence",
                "categories": {
                    DocumentCategory.FINANCIAL: [
                        "Three years audited financial statements",
                        "Inventory valuation and turnover",
                        "Cost accounting methodology",
                        "Capital expenditure history and plans",
                        "Working capital analysis",
                        "Product profitability analysis"
                    ],
                    DocumentCategory.OPERATIONAL: [
                        "Manufacturing facilities and capacity",
                        "Production processes and efficiency",
                        "Quality control procedures",
                        "Supply chain and vendor relationships",
                        "Inventory management systems",
                        "Equipment age and maintenance records",
                        "Safety records and OSHA compliance"
                    ],
                    DocumentCategory.ENVIRONMENTAL: [
                        "Environmental permits and compliance",
                        "Hazardous materials handling",
                        "Waste management procedures",
                        "Environmental liabilities assessment",
                        "Sustainability initiatives",
                        "Energy consumption and efficiency"
                    ]
                }
            }
        }

    async def generate_checklist(
        self,
        deal_id: str,
        deal_type: DealType,
        industry: str,
        customize: bool = True
    ) -> DueDiligenceChecklist:
        """
        Generate automated due diligence checklist based on deal characteristics
        """
        deal = self.db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            raise ValueError(f"Deal {deal_id} not found")

        # Determine checklist type based on industry
        checklist_type = self._map_industry_to_checklist_type(industry)
        template = self.checklist_templates.get(
            checklist_type,
            self.checklist_templates[ChecklistType.TECHNOLOGY]
        )

        # Create checklist
        checklist = DueDiligenceChecklist(
            organization_id=deal.organization_id,
            name=f"{deal.title} - Due Diligence Checklist",
            description=f"Automated checklist for {industry} {deal_type.value}",
            checklist_type=checklist_type,
            industry=industry,
            is_template=False,
            categories=list(template["categories"].keys())
        )

        self.db.add(checklist)
        self.db.flush()

        # Create checklist items
        items_created = 0
        for category, items in template["categories"].items():
            for item_title in items:
                # Determine if item is critical based on deal characteristics
                is_critical = self._is_critical_item(
                    category, item_title, deal_type, deal.deal_value
                )

                item = DueDiligenceItem(
                    checklist_id=checklist.id,
                    category=category,
                    title=item_title,
                    is_required=is_critical or category in [
                        DocumentCategory.FINANCIAL,
                        DocumentCategory.LEGAL
                    ],
                    critical_item=is_critical,
                    risk_weight=template.get("risk_weights", {}).get(category, 1.0)
                )
                self.db.add(item)
                items_created += 1

        # Customize based on deal specifics if requested
        if customize:
            custom_items = await self._generate_custom_items(deal)
            for custom_item in custom_items:
                self.db.add(custom_item)
                items_created += 1

        self.db.commit()
        logger.info(f"Generated checklist with {items_created} items for deal {deal_id}")

        return checklist

    def _map_industry_to_checklist_type(self, industry: str) -> ChecklistType:
        """Map industry to checklist type"""
        industry_lower = industry.lower()

        if any(tech in industry_lower for tech in ["software", "saas", "tech", "digital"]):
            return ChecklistType.TECHNOLOGY
        elif any(mfg in industry_lower for mfg in ["manufacturing", "industrial", "production"]):
            return ChecklistType.MANUFACTURING
        elif any(health in industry_lower for health in ["healthcare", "medical", "pharma"]):
            return ChecklistType.HEALTHCARE
        elif any(fin in industry_lower for fin in ["finance", "banking", "insurance"]):
            return ChecklistType.FINANCIAL_SERVICES
        elif "real estate" in industry_lower or "property" in industry_lower:
            return ChecklistType.REAL_ESTATE
        else:
            return ChecklistType.CUSTOM

    def _is_critical_item(
        self,
        category: DocumentCategory,
        item_title: str,
        deal_type: DealType,
        deal_value: Decimal
    ) -> bool:
        """Determine if an item is critical based on deal characteristics"""
        # High-value deals have more critical items
        is_high_value = deal_value and deal_value > 100000000  # $100M+

        critical_keywords = [
            "financial statements", "intellectual property", "litigation",
            "material contracts", "regulatory compliance", "environmental",
            "key employee", "customer concentration", "debt agreements"
        ]

        if any(keyword in item_title.lower() for keyword in critical_keywords):
            return True

        if is_high_value and category in [DocumentCategory.FINANCIAL, DocumentCategory.LEGAL]:
            return True

        if deal_type == DealType.LEVERAGED_BUYOUT and "debt" in item_title.lower():
            return True

        return False

    async def _generate_custom_items(self, deal: Deal) -> List[DueDiligenceItem]:
        """Generate custom checklist items based on deal specifics"""
        custom_items = []

        # Add items based on deal type
        if deal.deal_type == DealType.LEVERAGED_BUYOUT:
            custom_items.append(DueDiligenceItem(
                checklist_id=deal.id,
                category=DocumentCategory.FINANCIAL,
                title="LBO model and returns analysis",
                description="Detailed LBO model with sensitivity analysis",
                is_required=True,
                critical_item=True
            ))

        # Add items based on cross-border deals
        if deal.target_country and deal.target_country != "US":
            custom_items.append(DueDiligenceItem(
                checklist_id=deal.id,
                category=DocumentCategory.REGULATORY,
                title="Foreign investment regulatory approvals",
                description="Required regulatory approvals for cross-border transaction",
                is_required=True,
                critical_item=True
            ))

        # Add items for high-tech deals
        if deal.target_industry and "technology" in deal.target_industry.lower():
            custom_items.extend([
                DueDiligenceItem(
                    checklist_id=deal.id,
                    category=DocumentCategory.INTELLECTUAL_PROPERTY,
                    title="Source code review and quality assessment",
                    is_required=True
                ),
                DueDiligenceItem(
                    checklist_id=deal.id,
                    category=DocumentCategory.IT,
                    title="Cybersecurity and data privacy audit",
                    is_required=True,
                    critical_item=True
                )
            ])

        return custom_items

    async def analyze_document(
        self,
        document_id: str,
        use_ai: bool = True
    ) -> DocumentReview:
        """
        Analyze uploaded document and identify risks/issues
        """
        document = self.db.query(DueDiligenceDocument).filter(
            DueDiligenceDocument.id == document_id
        ).first()

        if not document:
            raise ValueError(f"Document {document_id} not found")

        review = DocumentReview(
            document_id=document_id,
            reviewed_by=document.uploaded_by,  # Would be current user
            review_date=datetime.utcnow(),
            status=DocumentStatus.UNDER_REVIEW
        )

        # Perform document analysis
        if use_ai:
            analysis_results = await self._ai_document_analysis(document)
            review.ai_analysis_results = analysis_results
            review.confidence_score = analysis_results.get("confidence", 0.0)

            # Extract findings
            issues = analysis_results.get("issues", [])
            review.issues_identified = issues
            review.risk_level = self._calculate_risk_level(issues)

            # Generate recommendations
            review.recommendations = self._generate_recommendations(issues)
            review.action_items = self._extract_action_items(analysis_results)
        else:
            # Manual review placeholder
            review.findings = "Document requires manual review"
            review.risk_level = RiskLevel.MEDIUM

        # Check if blocking issues exist
        review.is_blocking = any(
            issue.get("severity") == "critical"
            for issue in review.issues_identified
        )

        review.requires_follow_up = len(review.action_items) > 0
        review.status = DocumentStatus.REVIEWED

        self.db.add(review)
        self.db.commit()

        return review

    async def _ai_document_analysis(self, document: DueDiligenceDocument) -> Dict:
        """
        AI-powered document analysis (placeholder for actual AI integration)
        """
        # This would integrate with AI services for document analysis
        # For now, return mock analysis results

        analysis = {
            "document_type": document.category,
            "confidence": np.random.uniform(0.7, 0.95),
            "key_terms_extracted": [],
            "issues": [],
            "opportunities": [],
            "data_quality": np.random.uniform(0.6, 1.0)
        }

        # Simulate different findings based on document category
        if document.category == DocumentCategory.FINANCIAL:
            analysis["issues"] = [
                {
                    "type": "revenue_recognition",
                    "description": "Non-standard revenue recognition policy identified",
                    "severity": "medium",
                    "impact": "May affect revenue comparability"
                }
            ]
            analysis["key_metrics"] = {
                "revenue_growth": "15%",
                "gross_margin": "65%",
                "ebitda_margin": "20%"
            }

        elif document.category == DocumentCategory.LEGAL:
            analysis["issues"] = [
                {
                    "type": "contract_clause",
                    "description": "Change of control provision in key customer contract",
                    "severity": "high",
                    "impact": "May trigger contract termination rights"
                }
            ]

        elif document.category == DocumentCategory.INTELLECTUAL_PROPERTY:
            analysis["key_terms_extracted"] = [
                "15 registered patents",
                "25 pending applications",
                "Key patent expiry in 2028"
            ]

        return analysis

    def _calculate_risk_level(self, issues: List[Dict]) -> RiskLevel:
        """Calculate overall risk level based on identified issues"""
        if not issues:
            return RiskLevel.LOW

        severities = [issue.get("severity", "low") for issue in issues]

        if "critical" in severities:
            return RiskLevel.CRITICAL
        elif "high" in severities:
            return RiskLevel.HIGH
        elif "medium" in severities:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _generate_recommendations(self, issues: List[Dict]) -> str:
        """Generate recommendations based on identified issues"""
        if not issues:
            return "No significant issues identified. Document appears satisfactory."

        recommendations = []
        for issue in issues:
            severity = issue.get("severity", "low")
            issue_type = issue.get("type", "general")

            if severity == "critical":
                recommendations.append(
                    f"URGENT: Address {issue_type} immediately. Consider deal implications."
                )
            elif severity == "high":
                recommendations.append(
                    f"Require seller clarification on {issue_type} before proceeding."
                )
            else:
                recommendations.append(
                    f"Monitor {issue_type} and include in integration planning."
                )

        return " ".join(recommendations)

    def _extract_action_items(self, analysis: Dict) -> List[str]:
        """Extract action items from analysis results"""
        action_items = []

        for issue in analysis.get("issues", []):
            if issue.get("severity") in ["critical", "high"]:
                action_items.append(f"Follow up on: {issue.get('description')}")

        if analysis.get("data_quality", 1.0) < 0.7:
            action_items.append("Request higher quality documents or additional information")

        return action_items

    async def assess_overall_risk(
        self,
        process_id: str
    ) -> RiskAssessment:
        """
        Perform comprehensive risk assessment for due diligence process
        """
        process = self.db.query(DueDiligenceProcess).filter(
            DueDiligenceProcess.id == process_id
        ).first()

        if not process:
            raise ValueError(f"Process {process_id} not found")

        # Get all document reviews
        reviews = self.db.query(DocumentReview).join(
            DueDiligenceDocument
        ).filter(
            DueDiligenceDocument.process_id == process_id
        ).all()

        # Calculate risk scores by category
        risk_scores = {
            "financial_risk": 0.0,
            "legal_risk": 0.0,
            "operational_risk": 0.0,
            "market_risk": 0.0,
            "regulatory_risk": 0.0,
            "reputation_risk": 0.0
        }

        category_mapping = {
            DocumentCategory.FINANCIAL: "financial_risk",
            DocumentCategory.LEGAL: "legal_risk",
            DocumentCategory.OPERATIONAL: "operational_risk",
            DocumentCategory.COMMERCIAL: "market_risk",
            DocumentCategory.REGULATORY: "regulatory_risk",
            DocumentCategory.COMPLIANCE: "regulatory_risk"
        }

        # Aggregate risks from reviews
        for review in reviews:
            if review.document.category in category_mapping:
                risk_category = category_mapping[review.document.category]
                risk_value = self._risk_level_to_score(review.risk_level)
                risk_scores[risk_category] = max(
                    risk_scores[risk_category],
                    risk_value
                )

        # Create risk assessment
        assessment = RiskAssessment(
            process_id=process_id,
            assessment_date=datetime.utcnow(),
            financial_risk=risk_scores["financial_risk"],
            legal_risk=risk_scores["legal_risk"],
            operational_risk=risk_scores["operational_risk"],
            market_risk=risk_scores["market_risk"],
            regulatory_risk=risk_scores["regulatory_risk"],
            reputation_risk=risk_scores["reputation_risk"],
            overall_risk_score=np.mean(list(risk_scores.values())),
            confidence_level=self._calculate_confidence_level(reviews)
        )

        # Identify key risks
        assessment.key_risks = self._identify_key_risks(reviews)

        # Generate mitigation strategies
        assessment.mitigation_strategies = self._generate_mitigation_strategies(
            assessment.key_risks
        )

        # Generate deal recommendation
        assessment.deal_recommendation = self._generate_deal_recommendation(
            assessment.overall_risk_score
        )

        # Calculate price adjustment if needed
        if assessment.overall_risk_score > 60:
            assessment.price_adjustment_recommendation = self._calculate_price_adjustment(
                assessment.overall_risk_score,
                process.deal.deal_value if process.deal else 0
            )

        self.db.add(assessment)
        self.db.commit()

        return assessment

    def _risk_level_to_score(self, risk_level: RiskLevel) -> float:
        """Convert risk level to numerical score (0-100)"""
        mapping = {
            RiskLevel.NONE: 0,
            RiskLevel.LOW: 25,
            RiskLevel.MEDIUM: 50,
            RiskLevel.HIGH: 75,
            RiskLevel.CRITICAL: 100
        }
        return mapping.get(risk_level, 50)

    def _calculate_confidence_level(self, reviews: List[DocumentReview]) -> float:
        """Calculate confidence level based on review completeness and quality"""
        if not reviews:
            return 0.0

        confidence_scores = [
            review.confidence_score for review in reviews
            if review.confidence_score is not None
        ]

        if not confidence_scores:
            # Base confidence on review completeness
            reviewed_count = sum(1 for r in reviews if r.status == DocumentStatus.REVIEWED)
            return (reviewed_count / len(reviews)) * 70  # Max 70% without AI confidence

        return np.mean(confidence_scores) * 100

    def _identify_key_risks(self, reviews: List[DocumentReview]) -> List[Dict]:
        """Identify and prioritize key risks from reviews"""
        key_risks = []

        for review in reviews:
            if review.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                for issue in review.issues_identified:
                    key_risks.append({
                        "category": review.document.category.value,
                        "risk": issue.get("description"),
                        "severity": review.risk_level.value,
                        "impact": issue.get("impact"),
                        "likelihood": "medium"  # Would be calculated based on patterns
                    })

        # Sort by severity
        key_risks.sort(key=lambda x: x["severity"], reverse=True)

        return key_risks[:10]  # Top 10 risks

    def _generate_mitigation_strategies(self, key_risks: List[Dict]) -> List[Dict]:
        """Generate mitigation strategies for identified risks"""
        strategies = []

        for risk in key_risks:
            strategy = {
                "risk": risk["risk"],
                "mitigation": "",
                "owner": "TBD",
                "timeline": "Pre-closing"
            }

            # Generate specific mitigation based on risk type
            if "contract" in risk["risk"].lower():
                strategy["mitigation"] = "Negotiate contract amendments or waivers"
            elif "compliance" in risk["risk"].lower():
                strategy["mitigation"] = "Implement compliance remediation program"
            elif "financial" in risk.get("category", "").lower():
                strategy["mitigation"] = "Adjust valuation or implement earnout structure"
            else:
                strategy["mitigation"] = "Develop specific action plan with expert consultation"

            strategies.append(strategy)

        return strategies

    def _generate_deal_recommendation(self, risk_score: float) -> str:
        """Generate deal recommendation based on risk score"""
        if risk_score < 30:
            return "PROCEED: Low risk profile. Recommend proceeding with standard terms."
        elif risk_score < 50:
            return "PROCEED WITH CONDITIONS: Moderate risks identified. Implement mitigation strategies."
        elif risk_score < 70:
            return "PROCEED WITH CAUTION: Significant risks require careful mitigation and price adjustment."
        else:
            return "RECONSIDER: High risk profile. Major renegotiation or deal termination recommended."

    def _calculate_price_adjustment(
        self,
        risk_score: float,
        deal_value: Decimal
    ) -> float:
        """Calculate recommended price adjustment based on risk"""
        if not deal_value or risk_score < 50:
            return 0.0

        # Higher risk = higher discount
        # Risk score 50-70: 5-15% discount
        # Risk score 70-90: 15-30% discount
        # Risk score 90+: 30%+ discount

        if risk_score < 70:
            adjustment_pct = 5 + (risk_score - 50) * 0.5
        elif risk_score < 90:
            adjustment_pct = 15 + (risk_score - 70) * 0.75
        else:
            adjustment_pct = 30 + (risk_score - 90) * 1.0

        return float(deal_value) * (adjustment_pct / 100)

    async def coordinate_vendors(
        self,
        deal_id: str,
        process_id: str
    ) -> List[VendorManagement]:
        """
        Coordinate third-party vendors for due diligence
        """
        vendors = self.db.query(VendorManagement).filter(
            VendorManagement.deal_id == deal_id,
            VendorManagement.vendor_type.in_([
                VendorType.LAW_FIRM,
                VendorType.ACCOUNTING_FIRM,
                VendorType.CONSULTING_FIRM
            ])
        ).all()

        # Assign vendors to specific due diligence tasks
        for vendor in vendors:
            if vendor.vendor_type == VendorType.LAW_FIRM:
                vendor.deliverables.append({
                    "task": "Legal due diligence review",
                    "due_date": (datetime.utcnow() + timedelta(days=14)).isoformat(),
                    "status": "assigned"
                })
            elif vendor.vendor_type == VendorType.ACCOUNTING_FIRM:
                vendor.deliverables.append({
                    "task": "Financial due diligence and quality of earnings",
                    "due_date": (datetime.utcnow() + timedelta(days=21)).isoformat(),
                    "status": "assigned"
                })

        self.db.commit()
        return vendors