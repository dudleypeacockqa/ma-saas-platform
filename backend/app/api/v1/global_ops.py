"""
Global Operations API endpoints - Sprint 11
Advanced market intelligence and global operations for the M&A SaaS platform
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.global_ops import (
    get_market_intelligence_engine, get_global_operations_hub,
    get_deal_matching_engine, get_regulatory_automation_engine,
    MarketSector, GeographicRegion, Currency, Jurisdiction,
    DealType, MatchingCriteria, RegulatoryFramework
)

router = APIRouter()


# Market Intelligence Endpoints
@router.post("/market-intelligence/analyze-sector")
async def analyze_market_sector(
    analysis_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze market sector for investment opportunities"""
    engine = get_market_intelligence_engine()

    sector = MarketSector(analysis_data.get("sector"))
    region = GeographicRegion(analysis_data.get("region"))
    depth = analysis_data.get("depth", "comprehensive")

    analysis = await engine.analyze_market_sector(sector, region, depth)
    return analysis


@router.get("/market-intelligence/competitive-landscape")
async def get_competitive_landscape(
    sector: str,
    region: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get competitive landscape analysis"""
    engine = get_market_intelligence_engine()

    landscape = engine.get_competitive_landscape(
        MarketSector(sector),
        GeographicRegion(region)
    )

    return {
        "sector": landscape.sector.value,
        "region": landscape.region.value,
        "market_leaders": landscape.market_leaders,
        "emerging_players": landscape.emerging_players,
        "market_concentration": landscape.market_concentration,
        "barriers_to_entry": landscape.barriers_to_entry,
        "key_success_factors": landscape.key_success_factors,
        "disruption_threats": landscape.disruption_threats,
        "analysis_date": landscape.analysis_date.isoformat()
    }


@router.post("/market-intelligence/identify-opportunities")
async def identify_market_opportunities(
    opportunity_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Identify market opportunities across sectors and regions"""
    engine = get_market_intelligence_engine()

    sectors = [MarketSector(s) for s in opportunity_data.get("sectors", [])]
    regions = [GeographicRegion(r) for r in opportunity_data.get("regions", [])]
    min_value = opportunity_data.get("min_value_threshold", 100_000_000)

    opportunities = await engine.identify_market_opportunities(sectors, regions, min_value)

    return {
        "opportunities": [
            {
                "opportunity_id": opp.opportunity_id,
                "title": opp.title,
                "description": opp.description,
                "sector": opp.sector.value,
                "region": opp.region.value,
                "estimated_value": opp.estimated_value,
                "probability_score": opp.probability_score,
                "time_sensitivity": opp.time_sensitivity,
                "key_drivers": opp.key_drivers,
                "risks": opp.risks,
                "strategic_implications": opp.strategic_implications,
                "identified_at": opp.identified_at.isoformat()
            }
            for opp in opportunities
        ]
    }


@router.get("/market-intelligence/trends")
async def analyze_market_trends(
    sector: str,
    region: str,
    time_horizon: int = 12,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze market trends and predictions"""
    engine = get_market_intelligence_engine()

    trends = engine.analyze_market_trends(
        MarketSector(sector),
        GeographicRegion(region),
        time_horizon
    )

    return {
        "trends": [
            {
                "trend_id": trend.trend_id,
                "trend_type": trend.trend_type.value,
                "sector": trend.sector.value,
                "region": trend.region.value,
                "impact_score": trend.impact_score,
                "velocity": trend.velocity,
                "duration_estimate": trend.duration_estimate,
                "key_indicators": trend.key_indicators,
                "affected_companies": trend.affected_companies,
                "investment_implications": trend.investment_implications,
                "analysis_date": trend.analysis_date.isoformat()
            }
            for trend in trends
        ]
    }


@router.get("/market-intelligence/insights")
async def get_market_insights(
    sector: str,
    region: str,
    insight_type: str = "comprehensive",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get actionable market insights"""
    engine = get_market_intelligence_engine()

    insights = engine.get_market_insights(
        MarketSector(sector),
        GeographicRegion(region),
        insight_type
    )

    return insights


# Global Operations Endpoints
@router.post("/global-operations/currency/convert")
async def convert_currency(
    conversion_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Convert currency amounts"""
    hub = get_global_operations_hub()

    amount = Decimal(str(conversion_data.get("amount")))
    from_currency = Currency(conversion_data.get("from_currency"))
    to_currency = Currency(conversion_data.get("to_currency"))
    fee_percentage = conversion_data.get("fee_percentage", 0.001)

    conversion = hub.currency_manager.convert_currency(
        amount, from_currency, to_currency, fee_percentage
    )

    return {
        "conversion_id": conversion.conversion_id,
        "from_currency": conversion.from_currency.value,
        "to_currency": conversion.to_currency.value,
        "original_amount": float(conversion.original_amount),
        "converted_amount": float(conversion.converted_amount),
        "exchange_rate": float(conversion.exchange_rate),
        "fees": float(conversion.fees),
        "net_amount": float(conversion.net_amount),
        "conversion_date": conversion.conversion_date.isoformat()
    }


@router.get("/global-operations/currency/rates")
async def get_exchange_rates(
    from_currency: str,
    to_currency: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current exchange rates"""
    hub = get_global_operations_hub()

    rate = hub.currency_manager.get_exchange_rate(
        Currency(from_currency),
        Currency(to_currency)
    )

    if not rate:
        raise HTTPException(status_code=404, detail="Exchange rate not available")

    return {
        "from_currency": rate.from_currency.value,
        "to_currency": rate.to_currency.value,
        "rate": float(rate.rate),
        "bid": float(rate.bid) if rate.bid else None,
        "ask": float(rate.ask) if rate.ask else None,
        "timestamp": rate.timestamp.isoformat(),
        "source": rate.source
    }


@router.post("/global-operations/currency/multi-currency-summary")
async def get_multi_currency_summary(
    summary_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get multi-currency portfolio summary"""
    hub = get_global_operations_hub()

    amounts = {
        Currency(curr): Decimal(str(amount))
        for curr, amount in summary_data.get("amounts", {}).items()
    }
    target_currency = Currency(summary_data.get("target_currency"))

    summary = hub.currency_manager.get_multi_currency_summary(amounts, target_currency)

    return {
        "target_currency": summary["target_currency"],
        "total_amount": float(summary["total_amount"]),
        "currency_breakdown": [
            {
                "currency": breakdown["currency"],
                "original_amount": float(breakdown["original_amount"]),
                "converted_amount": float(breakdown["converted_amount"])
            }
            for breakdown in summary["currency_breakdown"]
        ],
        "summary_date": summary["summary_date"]
    }


@router.post("/global-operations/tax-implications")
async def get_tax_implications(
    tax_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculate tax implications for cross-border transactions"""
    hub = get_global_operations_hub()

    deal_value = Decimal(str(tax_data.get("deal_value")))
    buyer_jurisdiction = Jurisdiction(tax_data.get("buyer_jurisdiction"))
    seller_jurisdiction = Jurisdiction(tax_data.get("seller_jurisdiction"))
    deal_structure = tax_data.get("deal_structure", "asset_acquisition")

    implications = hub.regulatory_manager.get_tax_implications(
        deal_value, buyer_jurisdiction, seller_jurisdiction, deal_structure
    )

    # Convert Decimal values to float for JSON serialization
    tax_breakdown = {}
    for tax_type, details in implications["tax_breakdown"].items():
        tax_breakdown[tax_type] = {
            "rate": details["rate"],
            "amount": float(details["amount"]),
            "jurisdiction": details["jurisdiction"]
        }

    return {
        "buyer_jurisdiction": implications["buyer_jurisdiction"],
        "seller_jurisdiction": implications["seller_jurisdiction"],
        "deal_value": float(implications["deal_value"]),
        "deal_structure": implications["deal_structure"],
        "tax_breakdown": tax_breakdown,
        "total_tax_burden": float(implications["total_tax_burden"]),
        "optimization_opportunities": implications["optimization_opportunities"],
        "compliance_requirements": implications["compliance_requirements"]
    }


@router.post("/global-operations/regulatory-requirements")
async def get_regulatory_requirements(
    requirements_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get regulatory requirements for multi-jurisdiction deals"""
    hub = get_global_operations_hub()

    deal_value = Decimal(str(requirements_data.get("deal_value")))
    jurisdictions = [Jurisdiction(j) for j in requirements_data.get("jurisdictions", [])]
    industry_sector = requirements_data.get("industry_sector", "general")

    requirements = hub.regulatory_manager.get_regulatory_requirements(
        deal_value, jurisdictions, industry_sector
    )

    return {
        "requirements": [
            {
                "requirement_id": req.requirement_id,
                "jurisdiction": req.jurisdiction.value,
                "category": req.category,
                "description": req.description,
                "compliance_deadline": req.compliance_deadline.isoformat(),
                "severity": req.severity,
                "applicable_deal_size": float(req.applicable_deal_size) if req.applicable_deal_size else None,
                "required_actions": req.required_actions,
                "penalties": req.penalties
            }
            for req in requirements
        ]
    }


@router.post("/global-operations/create-deal-structure")
async def create_global_deal_structure(
    structure_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create optimized global deal structure"""
    hub = get_global_operations_hub()

    deal_id = structure_data.get("deal_id")
    deal_value = Decimal(str(structure_data.get("deal_value")))
    buyer_jurisdiction = Jurisdiction(structure_data.get("buyer_jurisdiction"))
    seller_jurisdiction = Jurisdiction(structure_data.get("seller_jurisdiction"))
    deal_currency = Currency(structure_data.get("deal_currency"))
    complexity_factors = structure_data.get("complexity_factors", [])

    structure = hub.create_global_deal_structure(
        deal_id, deal_value, buyer_jurisdiction, seller_jurisdiction,
        deal_currency, complexity_factors
    )

    return {
        "structure_id": structure.structure_id,
        "deal_id": structure.deal_id,
        "primary_jurisdiction": structure.primary_jurisdiction.value,
        "secondary_jurisdictions": [j.value for j in structure.secondary_jurisdictions],
        "base_currency": structure.base_currency.value,
        "deal_currencies": [c.value for c in structure.deal_currencies],
        "tax_optimization_strategy": structure.tax_optimization_strategy,
        "regulatory_pathway": structure.regulatory_pathway,
        "estimated_completion_time": structure.estimated_completion_time,
        "complexity_score": structure.complexity_score
    }


@router.post("/global-operations/analyze-opportunity")
async def analyze_global_opportunity(
    opportunity_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Comprehensive analysis of global deal opportunity"""
    hub = get_global_operations_hub()

    deal_value = Decimal(str(opportunity_data.get("deal_value")))
    target_jurisdictions = [Jurisdiction(j) for j in opportunity_data.get("target_jurisdictions", [])]
    industry_sector = opportunity_data.get("industry_sector", "general")

    analysis = hub.analyze_global_opportunity(deal_value, target_jurisdictions, industry_sector)
    return analysis


@router.post("/global-operations/cross-border-requirements")
async def get_cross_border_requirements(
    requirements_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific cross-border transaction requirements"""
    hub = get_global_operations_hub()

    from_jurisdiction = Jurisdiction(requirements_data.get("from_jurisdiction"))
    to_jurisdiction = Jurisdiction(requirements_data.get("to_jurisdiction"))
    deal_value = Decimal(str(requirements_data.get("deal_value")))

    requirements = hub.get_cross_border_requirements(from_jurisdiction, to_jurisdiction, deal_value)
    return requirements


# Deal Matching Endpoints
@router.post("/deal-matching/add-company-profile")
async def add_company_profile(
    profile_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add or update company profile for deal matching"""
    from app.global_ops.deal_matching import CompanyProfile

    engine = get_deal_matching_engine()

    profile = CompanyProfile(
        company_id=profile_data.get("company_id"),
        name=profile_data.get("name"),
        industry_sector=profile_data.get("industry_sector"),
        geographic_regions=profile_data.get("geographic_regions", []),
        revenue=profile_data.get("revenue"),
        employees=profile_data.get("employees"),
        valuation=profile_data.get("valuation"),
        growth_rate=profile_data.get("growth_rate"),
        technology_stack=profile_data.get("technology_stack", []),
        market_position=profile_data.get("market_position", ""),
        financial_health_score=profile_data.get("financial_health_score", 0.7),
        strategic_priorities=profile_data.get("strategic_priorities", []),
        available_for=[DealType(dt) for dt in profile_data.get("available_for", [])],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    success = engine.add_company_profile(profile)
    return {"success": success, "company_id": profile.company_id}


@router.post("/deal-matching/find-matches")
async def find_deal_matches(
    matching_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Find potential deal matches for a buyer"""
    engine = get_deal_matching_engine()

    buyer_id = matching_data.get("buyer_id")
    deal_type = DealType(matching_data.get("deal_type"))
    criteria_weights = {
        MatchingCriteria(k): v for k, v in matching_data.get("criteria_weights", {}).items()
    } if matching_data.get("criteria_weights") else None
    min_score_threshold = matching_data.get("min_score_threshold", 0.6)
    max_results = matching_data.get("max_results", 10)

    matches = engine.find_matches(
        buyer_id, deal_type, criteria_weights, min_score_threshold, max_results
    )

    return {
        "matches": [
            {
                "match_id": match.match_id,
                "seller": {
                    "company_id": match.seller_profile.company_id,
                    "name": match.seller_profile.name,
                    "industry_sector": match.seller_profile.industry_sector,
                    "geographic_regions": match.seller_profile.geographic_regions,
                    "revenue": match.seller_profile.revenue,
                    "valuation": match.seller_profile.valuation
                },
                "deal_type": match.deal_type.value,
                "match_score": {
                    "overall_score": match.match_score.overall_score,
                    "criteria_scores": {k.value: v for k, v in match.match_score.criteria_scores.items()},
                    "confidence_level": match.match_score.confidence_level,
                    "explanation": match.match_score.explanation,
                    "key_synergies": match.match_score.key_synergies,
                    "potential_challenges": match.match_score.potential_challenges
                },
                "estimated_deal_value": match.estimated_deal_value,
                "strategic_rationale": match.strategic_rationale,
                "synergy_potential": match.synergy_potential,
                "timeline_estimate": match.timeline_estimate,
                "match_date": match.match_date.isoformat()
            }
            for match in matches
        ]
    }


@router.post("/deal-matching/strategic-fit-analysis")
async def analyze_strategic_fit(
    analysis_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Perform detailed strategic fit analysis"""
    engine = get_deal_matching_engine()

    buyer_id = analysis_data.get("buyer_id")
    target_id = analysis_data.get("target_id")

    analysis = engine.analyze_strategic_fit(buyer_id, target_id)

    return {
        "analysis_id": analysis.analysis_id,
        "buyer_id": analysis.buyer_id,
        "target_id": analysis.target_id,
        "strategic_alignment_score": analysis.strategic_alignment_score,
        "operational_synergies": analysis.operational_synergies,
        "financial_synergies": analysis.financial_synergies,
        "market_synergies": analysis.market_synergies,
        "technology_synergies": analysis.technology_synergies,
        "integration_complexity": analysis.integration_complexity,
        "cultural_fit_score": analysis.cultural_fit_score,
        "regulatory_fit_score": analysis.regulatory_fit_score,
        "overall_recommendation": analysis.overall_recommendation,
        "analysis_date": analysis.analysis_date.isoformat()
    }


@router.post("/deal-matching/market-timing-analysis")
async def analyze_market_timing(
    timing_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze optimal timing for deal execution"""
    engine = get_deal_matching_engine()

    deal_type = DealType(timing_data.get("deal_type"))
    industry_sector = timing_data.get("industry_sector")
    geographic_region = timing_data.get("geographic_region")

    analysis = engine.analyze_market_timing(deal_type, industry_sector, geographic_region)

    return {
        "timing_id": analysis.timing_id,
        "deal_type": analysis.deal_type.value,
        "industry_sector": analysis.industry_sector,
        "geographic_region": analysis.geographic_region,
        "market_conditions_score": analysis.market_conditions_score,
        "timing_recommendation": analysis.timing_recommendation,
        "optimal_window_start": analysis.optimal_window_start.isoformat(),
        "optimal_window_end": analysis.optimal_window_end.isoformat(),
        "key_timing_factors": analysis.key_timing_factors,
        "competitive_activity": analysis.competitive_activity,
        "regulatory_calendar": analysis.regulatory_calendar,
        "analysis_date": analysis.analysis_date.isoformat()
    }


@router.post("/deal-matching/recommendations")
async def get_match_recommendations(
    recommendations_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized match recommendations"""
    engine = get_deal_matching_engine()

    buyer_id = recommendations_data.get("buyer_id")
    preferences = recommendations_data.get("preferences", {})

    # Convert string deal types to enum
    if "deal_types" in preferences:
        preferences["deal_types"] = [DealType(dt) for dt in preferences["deal_types"]]

    recommendations = engine.get_match_recommendations(buyer_id, preferences)
    return recommendations


# Regulatory Automation Endpoints
@router.post("/regulatory/analyze-requirements")
async def analyze_regulatory_requirements(
    requirements_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Comprehensive regulatory requirements analysis"""
    engine = get_regulatory_automation_engine()

    deal_id = requirements_data.get("deal_id")
    deal_characteristics = requirements_data.get("deal_characteristics", {})

    analysis = engine.analyze_regulatory_requirements(deal_id, deal_characteristics)
    return analysis


@router.post("/regulatory/create-compliance-workflow")
async def create_compliance_workflow(
    workflow_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create automated compliance workflow"""
    engine = get_regulatory_automation_engine()

    deal_id = workflow_data.get("deal_id")
    frameworks = [RegulatoryFramework(f) for f in workflow_data.get("frameworks", [])]
    jurisdictions = workflow_data.get("jurisdictions", [])

    workflow_id = engine.create_compliance_workflow(deal_id, frameworks, jurisdictions)
    return {"workflow_id": workflow_id}


@router.post("/regulatory/compliance-assessment")
async def create_compliance_assessment(
    assessment_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create compliance assessment for specific framework"""
    engine = get_regulatory_automation_engine()

    deal_id = assessment_data.get("deal_id")
    framework = RegulatoryFramework(assessment_data.get("framework"))
    jurisdiction = assessment_data.get("jurisdiction")
    deal_characteristics = assessment_data.get("deal_characteristics", {})

    assessment = engine.compliance_tracker.create_compliance_assessment(
        deal_id, framework, jurisdiction, deal_characteristics
    )

    return {
        "assessment_id": assessment.assessment_id,
        "deal_id": assessment.deal_id,
        "framework": assessment.framework.value,
        "jurisdiction": assessment.jurisdiction,
        "assessment_date": assessment.assessment_date.isoformat(),
        "compliance_status": assessment.compliance_status.value,
        "risk_level": assessment.risk_level.value,
        "key_findings": assessment.key_findings,
        "required_actions": assessment.required_actions,
        "estimated_timeline": assessment.estimated_timeline,
        "cost_estimate": assessment.cost_estimate,
        "dependencies": assessment.dependencies
    }


@router.post("/regulatory/risk-assessment")
async def perform_risk_assessment(
    risk_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Perform comprehensive regulatory risk assessment"""
    engine = get_regulatory_automation_engine()

    deal_id = risk_data.get("deal_id")
    frameworks = [RegulatoryFramework(f) for f in risk_data.get("frameworks", [])]
    deal_characteristics = risk_data.get("deal_characteristics", {})

    assessment = engine.risk_monitor.perform_risk_assessment(
        deal_id, frameworks, deal_characteristics
    )

    return {
        "assessment_id": assessment.assessment_id,
        "deal_id": assessment.deal_id,
        "overall_risk_score": assessment.overall_risk_score,
        "risk_breakdown": {k.value: v for k, v in assessment.risk_breakdown.items()},
        "critical_risks": assessment.critical_risks,
        "mitigation_strategies": assessment.mitigation_strategies,
        "monitoring_requirements": assessment.monitoring_requirements,
        "assessment_date": assessment.assessment_date.isoformat(),
        "next_review_date": assessment.next_review_date.isoformat()
    }


@router.post("/regulatory/filing")
async def create_regulatory_filing(
    filing_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create and track regulatory filing"""
    engine = get_regulatory_automation_engine()

    deal_id = filing_data.get("deal_id")
    framework = RegulatoryFramework(filing_data.get("framework"))
    jurisdiction = filing_data.get("jurisdiction")
    filing_type = filing_data.get("filing_type")

    filing = engine.compliance_tracker.create_regulatory_filing(
        deal_id, framework, jurisdiction, filing_type
    )

    return {
        "filing_id": filing.filing_id,
        "deal_id": filing.deal_id,
        "framework": filing.framework.value,
        "jurisdiction": filing.jurisdiction,
        "filing_type": filing.filing_type,
        "status": filing.status.value,
        "response_deadline": filing.response_deadline.isoformat() if filing.response_deadline else None,
        "filing_documents": filing.filing_documents,
        "estimated_approval_time": filing.estimated_approval_time
    }


@router.put("/regulatory/filing/{filing_id}/status")
async def update_filing_status(
    filing_id: str,
    status_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update filing status"""
    from app.global_ops.regulatory_automation import FilingStatus

    engine = get_regulatory_automation_engine()

    new_status = FilingStatus(status_data.get("status"))
    comments = status_data.get("comments")

    success = engine.compliance_tracker.update_filing_status(filing_id, new_status, comments)

    if not success:
        raise HTTPException(status_code=404, detail="Filing not found")

    return {"success": True, "filing_id": filing_id, "new_status": new_status.value}


@router.post("/regulatory/compliance-report")
async def generate_compliance_report(
    report_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate comprehensive compliance report"""
    engine = get_regulatory_automation_engine()

    deal_id = report_data.get("deal_id")
    period_start = datetime.fromisoformat(report_data.get("period_start"))
    period_end = datetime.fromisoformat(report_data.get("period_end"))

    report = engine.generate_compliance_report(deal_id, period_start, period_end)

    return {
        "report_id": report.report_id,
        "deal_id": report.deal_id,
        "reporting_period_start": report.reporting_period_start.isoformat(),
        "reporting_period_end": report.reporting_period_end.isoformat(),
        "frameworks_covered": [f.value for f in report.frameworks_covered],
        "compliance_summary": report.compliance_summary,
        "outstanding_issues": report.outstanding_issues,
        "upcoming_deadlines": report.upcoming_deadlines,
        "recommendations": report.recommendations,
        "generated_date": report.generated_date.isoformat()
    }


# Localization and Cultural Intelligence Endpoints
@router.get("/global-operations/business-culture/{jurisdiction}")
async def get_business_culture_insights(
    jurisdiction: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get business culture insights for jurisdiction"""
    hub = get_global_operations_hub()

    insights = hub.localization_manager.get_business_culture_insights(
        Jurisdiction(jurisdiction)
    )

    return insights


@router.post("/global-operations/optimal-meeting-times")
async def get_optimal_meeting_times(
    meeting_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Find optimal meeting times across multiple time zones"""
    from app.global_ops.global_operations import TimeZone

    hub = get_global_operations_hub()

    participant_timezones = [TimeZone(tz) for tz in meeting_data.get("participant_timezones", [])]
    duration_hours = meeting_data.get("duration_hours", 1)

    optimal_times = hub.localization_manager.get_optimal_meeting_times(
        participant_timezones, duration_hours
    )

    return {"optimal_times": optimal_times}