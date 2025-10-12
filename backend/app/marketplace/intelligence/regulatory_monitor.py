"""
Regulatory Monitor Service
Real-time monitoring of regulatory changes impacting M&A activity
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import aiohttp
import json
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import re
from urllib.parse import urljoin

from app.core.config import settings
from app.core.database import get_database
from app.marketplace import MARKETPLACE_CONFIG
from app.marketplace.intelligence.market_trends import MarketSegment

logger = logging.getLogger(__name__)

class RegulatoryImpact(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RegulatoryType(str, Enum):
    ANTITRUST = "antitrust"
    SECURITIES = "securities"
    FOREIGN_INVESTMENT = "foreign_investment"
    SECTOR_SPECIFIC = "sector_specific"
    TAX = "tax"
    ENVIRONMENTAL = "environmental"
    DATA_PRIVACY = "data_privacy"
    LABOR = "labor"

class RegulatoryStatus(str, Enum):
    PROPOSED = "proposed"
    UNDER_REVIEW = "under_review"
    ENACTED = "enacted"
    EFFECTIVE = "effective"
    SUPERSEDED = "superseded"

@dataclass
class RegulatoryChange:
    regulation_id: str
    title: str
    description: str
    regulatory_type: RegulatoryType
    jurisdiction: str
    status: RegulatoryStatus
    impact_level: RegulatoryImpact
    affected_segments: List[MarketSegment]
    effective_date: Optional[datetime]
    compliance_deadline: Optional[datetime]
    requirements: List[str]
    penalties: Optional[str]
    guidance_documents: List[str]
    related_regulations: List[str]
    deal_impact_assessment: Dict[str, Any]
    monitoring_keywords: List[str]
    last_updated: datetime

@dataclass
class ComplianceRequirement:
    requirement_id: str
    regulation_id: str
    description: str
    applicable_deal_types: List[str]
    compliance_steps: List[str]
    documentation_needed: List[str]
    timeline_requirements: Dict[str, int]  # step -> days
    cost_implications: Optional[float]
    risk_level: RegulatoryImpact

@dataclass
class RegulatoryAlert:
    alert_id: str
    alert_type: str  # "new_regulation", "status_change", "deadline_approaching"
    title: str
    description: str
    urgency_level: RegulatoryImpact
    affected_regulations: List[str]
    recommended_actions: List[str]
    deadline: Optional[datetime]
    generated_at: datetime

@dataclass
class RegulatoryEnvironmentReport:
    jurisdiction: str
    segments: List[MarketSegment]
    active_regulations: List[RegulatoryChange]
    pending_changes: List[RegulatoryChange]
    compliance_requirements: List[ComplianceRequirement]
    recent_alerts: List[RegulatoryAlert]
    regulatory_burden_score: float  # 0-100 scale
    risk_assessment: Dict[str, Any]
    trend_analysis: Dict[str, Any]
    generated_at: datetime

class RegulatoryMonitorService:
    """Service for monitoring regulatory changes and their impact on M&A activity"""

    def __init__(self):
        self.config = MARKETPLACE_CONFIG["intelligence"]
        self.monitored_jurisdictions = [
            "United States", "European Union", "United Kingdom", "Canada",
            "Australia", "Singapore", "Hong Kong", "Japan"
        ]

    async def get_regulatory_environment(
        self,
        jurisdiction: str = "United States",
        segments: Optional[List[MarketSegment]] = None
    ) -> RegulatoryEnvironmentReport:
        """Get comprehensive regulatory environment report"""
        try:
            logger.info(f"Generating regulatory environment report for {jurisdiction}")

            target_segments = segments or list(MarketSegment)

            # Gather regulatory data
            tasks = [
                self._get_active_regulations(jurisdiction, target_segments),
                self._get_pending_changes(jurisdiction, target_segments),
                self._get_compliance_requirements(jurisdiction, target_segments),
                self._get_recent_alerts(jurisdiction),
                self._calculate_regulatory_burden(jurisdiction, target_segments),
                self._analyze_regulatory_trends(jurisdiction)
            ]

            (active_regs, pending_changes, compliance_reqs,
             alerts, burden_score, trend_analysis) = await asyncio.gather(*tasks)

            # Generate risk assessment
            risk_assessment = await self._assess_regulatory_risks(
                active_regs, pending_changes, target_segments
            )

            return RegulatoryEnvironmentReport(
                jurisdiction=jurisdiction,
                segments=target_segments,
                active_regulations=active_regs,
                pending_changes=pending_changes,
                compliance_requirements=compliance_reqs,
                recent_alerts=alerts,
                regulatory_burden_score=burden_score,
                risk_assessment=risk_assessment,
                trend_analysis=trend_analysis,
                generated_at=datetime.utcnow()
            )

        except Exception as e:
            logger.error(f"Error generating regulatory environment report: {e}")
            raise

    async def _get_active_regulations(
        self,
        jurisdiction: str,
        segments: List[MarketSegment]
    ) -> List[RegulatoryChange]:
        """Get currently active regulations affecting M&A"""
        # Mock data - in production would integrate with regulatory databases
        us_regulations = [
            RegulatoryChange(
                regulation_id="us_antitrust_001",
                title="Hart-Scott-Rodino Antitrust Improvements Act",
                description="Requires pre-merger notification for transactions above certain thresholds",
                regulatory_type=RegulatoryType.ANTITRUST,
                jurisdiction="United States",
                status=RegulatoryStatus.EFFECTIVE,
                impact_level=RegulatoryImpact.HIGH,
                affected_segments=list(MarketSegment),
                effective_date=datetime(1976, 9, 30),
                compliance_deadline=None,
                requirements=[
                    "File HSR notification for deals >$101M",
                    "30-day waiting period (15 days for cash tender offers)",
                    "Provide transaction documents and business information"
                ],
                penalties="Up to $46,517 per day for violations",
                guidance_documents=[
                    "HSR Rules and Regulations",
                    "Premerger Notification Program Manual"
                ],
                related_regulations=["us_antitrust_002", "us_antitrust_003"],
                deal_impact_assessment={
                    "timeline_impact_days": 30,
                    "cost_impact_range": [50000, 500000],
                    "approval_probability": 0.95
                },
                monitoring_keywords=["HSR", "antitrust", "merger review", "FTC", "DOJ"],
                last_updated=datetime.utcnow()
            ),
            RegulatoryChange(
                regulation_id="us_cfius_001",
                title="Committee on Foreign Investment in the United States",
                description="Reviews foreign acquisitions of US companies for national security implications",
                regulatory_type=RegulatoryType.FOREIGN_INVESTMENT,
                jurisdiction="United States",
                status=RegulatoryStatus.EFFECTIVE,
                impact_level=RegulatoryImpact.CRITICAL,
                affected_segments=[
                    MarketSegment.TECHNOLOGY, MarketSegment.TELECOMMUNICATIONS,
                    MarketSegment.HEALTHCARE, MarketSegment.ENERGY
                ],
                effective_date=datetime(2018, 11, 10),
                compliance_deadline=None,
                requirements=[
                    "Mandatory filing for covered transactions",
                    "Enhanced due diligence for critical technologies",
                    "Risk mitigation agreements may be required"
                ],
                penalties="Forced divestiture, fines up to transaction value",
                guidance_documents=[
                    "CFIUS Filing Guidance",
                    "Critical Technology List"
                ],
                related_regulations=["us_cfius_002"],
                deal_impact_assessment={
                    "timeline_impact_days": 75,
                    "cost_impact_range": [200000, 2000000],
                    "approval_probability": 0.82
                },
                monitoring_keywords=["CFIUS", "foreign investment", "national security", "critical technology"],
                last_updated=datetime.utcnow()
            )
        ]

        eu_regulations = [
            RegulatoryChange(
                regulation_id="eu_merger_001",
                title="EU Merger Regulation",
                description="Controls concentrations between undertakings in the EU",
                regulatory_type=RegulatoryType.ANTITRUST,
                jurisdiction="European Union",
                status=RegulatoryStatus.EFFECTIVE,
                impact_level=RegulatoryImpact.HIGH,
                affected_segments=list(MarketSegment),
                effective_date=datetime(2004, 5, 1),
                compliance_deadline=None,
                requirements=[
                    "Notification for deals with EU dimension",
                    "Suspensive effect - cannot close before approval",
                    "Phase I: 25 working days, Phase II: 90 working days"
                ],
                penalties="Up to 10% of annual turnover",
                guidance_documents=[
                    "Best Practices Guidelines",
                    "Merger Remedies Study"
                ],
                related_regulations=["eu_merger_002"],
                deal_impact_assessment={
                    "timeline_impact_days": 35,
                    "cost_impact_range": [75000, 750000],
                    "approval_probability": 0.93
                },
                monitoring_keywords=["EU merger", "competition", "concentration", "European Commission"],
                last_updated=datetime.utcnow()
            )
        ]

        if jurisdiction == "United States":
            return [reg for reg in us_regulations if any(seg in reg.affected_segments for seg in segments)]
        elif jurisdiction == "European Union":
            return [reg for reg in eu_regulations if any(seg in reg.affected_segments for seg in segments)]
        else:
            return []

    async def _get_pending_changes(
        self,
        jurisdiction: str,
        segments: List[MarketSegment]
    ) -> List[RegulatoryChange]:
        """Get pending regulatory changes that may impact M&A"""
        # Mock data for pending changes
        pending_us = [
            RegulatoryChange(
                regulation_id="us_proposed_001",
                title="Enhanced Merger Filing Requirements Act",
                description="Proposed legislation to expand merger notification requirements",
                regulatory_type=RegulatoryType.ANTITRUST,
                jurisdiction="United States",
                status=RegulatoryStatus.PROPOSED,
                impact_level=RegulatoryImpact.MEDIUM,
                affected_segments=list(MarketSegment),
                effective_date=None,
                compliance_deadline=datetime(2024, 12, 31),
                requirements=[
                    "Lower notification thresholds",
                    "Enhanced information requirements",
                    "Extended review periods"
                ],
                penalties="TBD",
                guidance_documents=[],
                related_regulations=["us_antitrust_001"],
                deal_impact_assessment={
                    "timeline_impact_days": 45,
                    "cost_impact_range": [100000, 1000000],
                    "approval_probability": 0.85
                },
                monitoring_keywords=["merger filing", "enhanced requirements", "Congress"],
                last_updated=datetime.utcnow()
            )
        ]

        if jurisdiction == "United States":
            return [reg for reg in pending_us if any(seg in reg.affected_segments for seg in segments)]
        else:
            return []

    async def _get_compliance_requirements(
        self,
        jurisdiction: str,
        segments: List[MarketSegment]
    ) -> List[ComplianceRequirement]:
        """Get specific compliance requirements for M&A transactions"""
        requirements = []

        if jurisdiction == "United States":
            hsr_requirement = ComplianceRequirement(
                requirement_id="req_us_hsr_001",
                regulation_id="us_antitrust_001",
                description="Hart-Scott-Rodino filing and waiting period",
                applicable_deal_types=["merger", "acquisition", "joint_venture"],
                compliance_steps=[
                    "Determine if transaction meets size thresholds",
                    "Prepare HSR notification forms",
                    "Submit filings to FTC and DOJ",
                    "Observe waiting period",
                    "Respond to any second requests"
                ],
                documentation_needed=[
                    "Transaction agreements",
                    "Board resolutions",
                    "Financial statements",
                    "Business plans",
                    "Competitive analysis"
                ],
                timeline_requirements={
                    "filing_preparation": 14,
                    "waiting_period": 30,
                    "second_request_response": 60
                },
                cost_implications=250000.0,
                risk_level=RegulatoryImpact.HIGH
            )
            requirements.append(hsr_requirement)

        return requirements

    async def _get_recent_alerts(self, jurisdiction: str) -> List[RegulatoryAlert]:
        """Get recent regulatory alerts and notifications"""
        alerts = [
            RegulatoryAlert(
                alert_id="alert_001",
                alert_type="new_regulation",
                title="New CFIUS Filing Requirements for AI Companies",
                description="Enhanced review requirements for AI-related acquisitions effective immediately",
                urgency_level=RegulatoryImpact.HIGH,
                affected_regulations=["us_cfius_001"],
                recommended_actions=[
                    "Review all pending AI company acquisitions",
                    "Assess mandatory filing requirements",
                    "Prepare enhanced technical documentation"
                ],
                deadline=datetime.utcnow() + timedelta(days=30),
                generated_at=datetime.utcnow() - timedelta(days=3)
            ),
            RegulatoryAlert(
                alert_id="alert_002",
                alert_type="deadline_approaching",
                title="EU Digital Services Act Compliance Deadline",
                description="Large platforms must comply with DSA requirements by February 17, 2024",
                urgency_level=RegulatoryImpact.MEDIUM,
                affected_regulations=["eu_dsa_001"],
                recommended_actions=[
                    "Assess target companies' DSA compliance status",
                    "Include compliance costs in deal modeling",
                    "Plan integration timeline around compliance"
                ],
                deadline=datetime(2024, 2, 17),
                generated_at=datetime.utcnow() - timedelta(days=7)
            )
        ]

        return alerts

    async def _calculate_regulatory_burden(
        self,
        jurisdiction: str,
        segments: List[MarketSegment]
    ) -> float:
        """Calculate regulatory burden score (0-100)"""
        # Mock calculation based on number of regulations and their impact
        active_regs = await self._get_active_regulations(jurisdiction, segments)
        pending_regs = await self._get_pending_changes(jurisdiction, segments)

        # Base score calculation
        base_score = 0
        for reg in active_regs:
            impact_weights = {
                RegulatoryImpact.LOW: 5,
                RegulatoryImpact.MEDIUM: 15,
                RegulatoryImpact.HIGH: 30,
                RegulatoryImpact.CRITICAL: 50
            }
            base_score += impact_weights.get(reg.impact_level, 15)

        # Add pending regulation uncertainty
        for reg in pending_regs:
            base_score += 10  # Uncertainty factor

        # Jurisdiction-specific adjustments
        jurisdiction_multipliers = {
            "United States": 1.2,
            "European Union": 1.4,
            "China": 1.6,
            "United Kingdom": 1.1
        }

        final_score = min(100, base_score * jurisdiction_multipliers.get(jurisdiction, 1.0))
        return round(final_score, 1)

    async def _analyze_regulatory_trends(self, jurisdiction: str) -> Dict[str, Any]:
        """Analyze regulatory trends and patterns"""
        return {
            "trend_direction": "increasing_complexity",
            "key_focus_areas": [
                "Digital platform regulation",
                "Foreign investment screening",
                "Climate-related disclosures",
                "AI governance"
            ],
            "enforcement_activity": "heightened",
            "timeline_trends": {
                "average_review_time_days": 87,
                "change_from_last_year": 12
            },
            "approval_rates": {
                "overall": 0.91,
                "foreign_transactions": 0.83,
                "large_transactions": 0.78
            }
        }

    async def _assess_regulatory_risks(
        self,
        active_regs: List[RegulatoryChange],
        pending_regs: List[RegulatoryChange],
        segments: List[MarketSegment]
    ) -> Dict[str, Any]:
        """Assess regulatory risks for M&A transactions"""
        high_impact_regs = [
            reg for reg in active_regs + pending_regs
            if reg.impact_level in [RegulatoryImpact.HIGH, RegulatoryImpact.CRITICAL]
        ]

        segment_risks = {}
        for segment in segments:
            applicable_regs = [reg for reg in high_impact_regs if segment in reg.affected_segments]
            segment_risks[segment.value] = {
                "risk_level": "high" if len(applicable_regs) > 2 else "medium",
                "key_regulations": [reg.regulation_id for reg in applicable_regs[:3]],
                "estimated_timeline_impact": sum(
                    reg.deal_impact_assessment.get("timeline_impact_days", 30)
                    for reg in applicable_regs
                ),
                "estimated_cost_impact": sum(
                    reg.deal_impact_assessment.get("cost_impact_range", [0, 0])[1]
                    for reg in applicable_regs
                )
            }

        return {
            "overall_risk_level": "elevated",
            "segment_specific_risks": segment_risks,
            "top_risk_factors": [
                "Foreign investment screening delays",
                "Antitrust review complexity",
                "Sector-specific compliance requirements"
            ],
            "mitigation_strategies": [
                "Early regulatory consultation",
                "Comprehensive due diligence",
                "Risk allocation in agreements",
                "Regulatory approval conditions"
            ]
        }

    async def monitor_regulatory_changes(self) -> List[RegulatoryAlert]:
        """Monitor for new regulatory changes and generate alerts"""
        alerts = []

        try:
            # In production, this would:
            # 1. Check regulatory websites and databases
            # 2. Parse new regulations and rule changes
            # 3. Assess impact on M&A activity
            # 4. Generate appropriate alerts

            # Mock alert generation
            new_alerts = [
                {
                    "alert_type": "status_change",
                    "title": "EU AI Act Final Vote Scheduled",
                    "description": "European Parliament scheduled final vote on AI Act for March 2024",
                    "urgency_level": RegulatoryImpact.HIGH,
                    "affected_segments": [MarketSegment.TECHNOLOGY],
                    "deadline": datetime(2024, 3, 15)
                }
            ]

            for i, alert_data in enumerate(new_alerts):
                alert = RegulatoryAlert(
                    alert_id=f"auto_alert_{datetime.utcnow().strftime('%Y%m%d')}_{i+1:03d}",
                    alert_type=alert_data["alert_type"],
                    title=alert_data["title"],
                    description=alert_data["description"],
                    urgency_level=alert_data["urgency_level"],
                    affected_regulations=[],
                    recommended_actions=[
                        "Monitor legislative progress",
                        "Assess impact on pending transactions",
                        "Update compliance procedures"
                    ],
                    deadline=alert_data.get("deadline"),
                    generated_at=datetime.utcnow()
                )
                alerts.append(alert)

        except Exception as e:
            logger.error(f"Error monitoring regulatory changes: {e}")

        return alerts

    async def assess_deal_regulatory_impact(
        self,
        deal_details: Dict[str, Any],
        jurisdictions: List[str]
    ) -> Dict[str, Any]:
        """Assess regulatory impact for a specific deal"""
        try:
            impact_assessment = {
                "overall_complexity": "medium",
                "required_filings": [],
                "estimated_timeline": 60,  # days
                "estimated_costs": 150000,
                "approval_probability": 0.88,
                "key_risks": [],
                "mitigation_recommendations": []
            }

            for jurisdiction in jurisdictions:
                jurisdiction_assessment = await self._assess_jurisdiction_impact(
                    deal_details, jurisdiction
                )

                # Aggregate impact across jurisdictions
                impact_assessment["required_filings"].extend(
                    jurisdiction_assessment.get("required_filings", [])
                )
                impact_assessment["estimated_timeline"] = max(
                    impact_assessment["estimated_timeline"],
                    jurisdiction_assessment.get("timeline_impact", 0)
                )
                impact_assessment["estimated_costs"] += jurisdiction_assessment.get("cost_impact", 0)

            # Adjust approval probability based on complexity
            if len(impact_assessment["required_filings"]) > 3:
                impact_assessment["approval_probability"] *= 0.9

            return impact_assessment

        except Exception as e:
            logger.error(f"Error assessing deal regulatory impact: {e}")
            raise

    async def _assess_jurisdiction_impact(
        self,
        deal_details: Dict[str, Any],
        jurisdiction: str
    ) -> Dict[str, Any]:
        """Assess regulatory impact for specific jurisdiction"""
        deal_value = deal_details.get("deal_value", 0)
        target_sector = deal_details.get("target_sector")
        buyer_nationality = deal_details.get("buyer_nationality")

        impact = {
            "required_filings": [],
            "timeline_impact": 0,
            "cost_impact": 0
        }

        # HSR filing requirement (US)
        if jurisdiction == "United States" and deal_value > 101_000_000:
            impact["required_filings"].append("HSR Notification")
            impact["timeline_impact"] = 30
            impact["cost_impact"] = 250000

        # CFIUS review (US foreign investment)
        if (jurisdiction == "United States" and
            buyer_nationality != "United States" and
            target_sector in ["technology", "telecommunications", "defense"]):
            impact["required_filings"].append("CFIUS Filing")
            impact["timeline_impact"] = max(impact["timeline_impact"], 75)
            impact["cost_impact"] += 500000

        # EU Merger Control
        if jurisdiction == "European Union" and deal_value > 5_000_000_000:
            impact["required_filings"].append("EU Merger Notification")
            impact["timeline_impact"] = max(impact["timeline_impact"], 35)
            impact["cost_impact"] += 200000

        return impact

    async def get_compliance_checklist(
        self,
        deal_details: Dict[str, Any],
        jurisdictions: List[str]
    ) -> Dict[str, List[str]]:
        """Generate compliance checklist for a deal"""
        checklist = {}

        for jurisdiction in jurisdictions:
            jurisdiction_items = []

            if jurisdiction == "United States":
                jurisdiction_items.extend([
                    "Determine HSR notification requirements",
                    "Assess CFIUS filing obligations",
                    "Review antitrust clearance timeline",
                    "Prepare required documentation",
                    "Plan for waiting periods"
                ])

            if jurisdiction == "European Union":
                jurisdiction_items.extend([
                    "Calculate EU dimension thresholds",
                    "Determine member state referrals",
                    "Prepare merger notification",
                    "Assess market definition issues",
                    "Plan for Phase I/II review"
                ])

            checklist[jurisdiction] = jurisdiction_items

        return checklist