"""
Celery Background Tasks for Deal Discovery
Automated data collection, enrichment, and monitoring
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from celery import shared_task
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.deal_discovery import (
    Company,
    DealOpportunity,
    MarketIntelligence,
    DealStage
)
from app.services.opportunity_discovery import get_discovery_engine
from app.services.deal_scoring import get_scoring_engine
from app.services.financial_analyzer import get_financial_analyzer
from app.integrations.news_api import get_news_api

logger = logging.getLogger(__name__)


@shared_task(name="discover_new_opportunities")
def discover_new_opportunities_task(
    organization_id: str,
    user_id: str,
    criteria: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Background task to discover new M&A opportunities

    Args:
        organization_id: Clerk organization ID
        user_id: User who initiated discovery
        criteria: Discovery criteria

    Returns:
        Task result summary
    """
    db = SessionLocal()
    result = {
        "status": "started",
        "organization_id": organization_id,
        "opportunities_found": 0,
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "errors": []
    }

    try:
        logger.info(f"Starting opportunity discovery for organization {organization_id}")

        # Get discovery engine
        discovery_engine = get_discovery_engine()

        # Run discovery
        opportunities = await discovery_engine.discover_opportunities(
            organization_id=organization_id,
            user_id=user_id,
            db=db,
            criteria=criteria
        )

        result["opportunities_found"] = len(opportunities)
        result["status"] = "completed"
        result["completed_at"] = datetime.utcnow().isoformat()

        logger.info(f"Discovery completed: {len(opportunities)} opportunities found")

    except Exception as e:
        logger.error(f"Error in opportunity discovery task: {e}")
        result["status"] = "failed"
        result["errors"].append(str(e))
    finally:
        db.close()

    return result


@shared_task(name="enrich_opportunity_data")
def enrich_opportunity_data_task(opportunity_id: str) -> Dict[str, Any]:
    """
    Enrich opportunity with additional data sources

    Args:
        opportunity_id: Opportunity UUID

    Returns:
        Enrichment result
    """
    db = SessionLocal()
    result = {
        "status": "started",
        "opportunity_id": opportunity_id,
        "enrichments_added": 0,
        "errors": []
    }

    try:
        logger.info(f"Enriching opportunity {opportunity_id}")

        discovery_engine = get_discovery_engine()

        # Enrich with news and market intelligence
        opportunity = await discovery_engine.enrich_opportunity(opportunity_id, db)

        result["status"] = "completed"
        result["enrichments_added"] = 1

        logger.info(f"Opportunity {opportunity_id} enriched successfully")

    except Exception as e:
        logger.error(f"Error enriching opportunity: {e}")
        result["status"] = "failed"
        result["errors"].append(str(e))
    finally:
        db.close()

    return result


@shared_task(name="update_opportunity_scores")
def update_opportunity_scores_task(organization_id: str) -> Dict[str, Any]:
    """
    Recalculate scores for all opportunities in an organization

    Args:
        organization_id: Clerk organization ID

    Returns:
        Update result
    """
    db = SessionLocal()
    result = {
        "status": "started",
        "organization_id": organization_id,
        "opportunities_scored": 0,
        "errors": []
    }

    try:
        logger.info(f"Updating opportunity scores for organization {organization_id}")

        # Get all active opportunities
        opportunities = db.query(DealOpportunity).filter(
            DealOpportunity.organization_id == organization_id,
            DealOpportunity.stage.notin_([DealStage.COMPLETED, DealStage.REJECTED])
        ).all()

        scoring_engine = get_scoring_engine()

        for opp in opportunities:
            try:
                scoring_engine.calculate_opportunity_score(opp, db)
                result["opportunities_scored"] += 1
            except Exception as e:
                logger.error(f"Error scoring opportunity {opp.id}: {e}")
                result["errors"].append(f"Opportunity {opp.id}: {str(e)}")

        db.commit()
        result["status"] = "completed"

        logger.info(f"Scored {result['opportunities_scored']} opportunities")

    except Exception as e:
        logger.error(f"Error updating opportunity scores: {e}")
        result["status"] = "failed"
        result["errors"].append(str(e))
        db.rollback()
    finally:
        db.close()

    return result


@shared_task(name="monitor_companies")
def monitor_companies_task(organization_id: str) -> Dict[str, Any]:
    """
    Monitor companies for news and market events

    Args:
        organization_id: Clerk organization ID

    Returns:
        Monitoring result
    """
    db = SessionLocal()
    result = {
        "status": "started",
        "organization_id": organization_id,
        "companies_monitored": 0,
        "alerts_created": 0,
        "errors": []
    }

    try:
        logger.info(f"Monitoring companies for organization {organization_id}")

        # Get all companies in active opportunities
        opportunities = db.query(DealOpportunity).filter(
            DealOpportunity.organization_id == organization_id,
            DealOpportunity.stage.in_([
                DealStage.DISCOVERY,
                DealStage.INITIAL_REVIEW,
                DealStage.DUE_DILIGENCE,
                DealStage.NEGOTIATION
            ])
        ).all()

        news_api = get_news_api()

        for opp in opportunities:
            try:
                company = opp.company

                # Monitor company news
                monitoring_result = await news_api.monitor_company(company.name)

                # Create market intelligence records for alerts
                if monitoring_result.get("alerts"):
                    for alert in monitoring_result["alerts"]:
                        intel = MarketIntelligence(
                            company_id=company.id,
                            intelligence_type="news_alert",
                            source="news_api",
                            content=alert,
                            relevance_score=0.9 if alert.get("type") == "ma_activity" else 0.7
                        )
                        db.add(intel)
                        result["alerts_created"] += 1

                result["companies_monitored"] += 1

            except Exception as e:
                logger.error(f"Error monitoring company {opp.company_id}: {e}")
                result["errors"].append(f"Company {opp.company_id}: {str(e)}")

        db.commit()
        result["status"] = "completed"

        logger.info(f"Monitored {result['companies_monitored']} companies, created {result['alerts_created']} alerts")

    except Exception as e:
        logger.error(f"Error in company monitoring task: {e}")
        result["status"] = "failed"
        result["errors"].append(str(e))
        db.rollback()
    finally:
        db.close()

    return result


@shared_task(name="refresh_company_data")
def refresh_company_data_task(company_id: str) -> Dict[str, Any]:
    """
    Refresh company data from external sources

    Args:
        company_id: Company UUID

    Returns:
        Refresh result
    """
    db = SessionLocal()
    result = {
        "status": "started",
        "company_id": company_id,
        "data_updated": False,
        "errors": []
    }

    try:
        logger.info(f"Refreshing data for company {company_id}")

        company = db.query(Company).filter(Company.id == company_id).first()

        if not company:
            raise ValueError(f"Company {company_id} not found")

        # Get appropriate API based on data source
        if company.data_source.value == "companies_house":
            from app.integrations.companies_house_enhanced import get_companies_house_api
            api = get_companies_house_api()
            profile = await api.get_company_full_profile(company.external_id)

            # Update company data
            company.raw_data = profile
            company.last_updated_at = datetime.utcnow()

        elif company.data_source.value == "sec_edgar":
            from app.integrations.sec_edgar_enhanced import get_sec_edgar_api
            api = get_sec_edgar_api()
            profile = await api.get_company_full_profile(company.external_id)

            company.raw_data = profile
            company.last_updated_at = datetime.utcnow()

        elif company.data_source.value == "crunchbase":
            from app.integrations.crunchbase import get_crunchbase_api
            api = get_crunchbase_api()
            details = await api.get_organization_details(company.external_id)

            company.raw_data = details
            company.last_updated_at = datetime.utcnow()

        db.commit()
        result["data_updated"] = True
        result["status"] = "completed"

        logger.info(f"Company {company_id} data refreshed successfully")

    except Exception as e:
        logger.error(f"Error refreshing company data: {e}")
        result["status"] = "failed"
        result["errors"].append(str(e))
        db.rollback()
    finally:
        db.close()

    return result


@shared_task(name="analyze_company_financials")
def analyze_company_financials_task(company_id: str) -> Dict[str, Any]:
    """
    Perform comprehensive financial analysis

    Args:
        company_id: Company UUID

    Returns:
        Analysis result
    """
    db = SessionLocal()
    result = {
        "status": "started",
        "company_id": company_id,
        "analysis_completed": False,
        "errors": []
    }

    try:
        logger.info(f"Analyzing financials for company {company_id}")

        financial_analyzer = get_financial_analyzer()

        analysis = financial_analyzer.analyze_company_financials(company_id, db)

        if "error" not in analysis:
            result["analysis_completed"] = True
            result["analysis_summary"] = {
                "profitability_rating": analysis.get("profitability_analysis", {}).get("rating"),
                "liquidity_assessment": analysis.get("liquidity_analysis", {}).get("assessment"),
                "growth_rating": analysis.get("growth_analysis", {}).get("growth_rating"),
                "red_flags_count": len(analysis.get("red_flags", [])),
                "strengths_count": len(analysis.get("strengths", []))
            }

        result["status"] = "completed"

        logger.info(f"Financial analysis completed for company {company_id}")

    except Exception as e:
        logger.error(f"Error analyzing company financials: {e}")
        result["status"] = "failed"
        result["errors"].append(str(e))
    finally:
        db.close()

    return result


@shared_task(name="daily_discovery_routine")
def daily_discovery_routine_task() -> Dict[str, Any]:
    """
    Daily routine to discover new opportunities for all active organizations

    Returns:
        Routine execution summary
    """
    db = SessionLocal()
    result = {
        "status": "started",
        "organizations_processed": 0,
        "total_opportunities_found": 0,
        "started_at": datetime.utcnow().isoformat(),
        "errors": []
    }

    try:
        logger.info("Starting daily discovery routine")

        # Get all organizations with active users
        # In a real implementation, you'd query active organizations from database
        # For now, this is a placeholder structure

        # Example: Process saved search criteria for each organization
        # This would be stored in a separate table in production

        result["status"] = "completed"
        result["completed_at"] = datetime.utcnow().isoformat()

        logger.info("Daily discovery routine completed")

    except Exception as e:
        logger.error(f"Error in daily discovery routine: {e}")
        result["status"] = "failed"
        result["errors"].append(str(e))
    finally:
        db.close()

    return result


@shared_task(name="cleanup_old_data")
def cleanup_old_data_task(days_to_keep: int = 90) -> Dict[str, Any]:
    """
    Clean up old market intelligence and temporary data

    Args:
        days_to_keep: Number of days of data to retain

    Returns:
        Cleanup result
    """
    db = SessionLocal()
    result = {
        "status": "started",
        "records_deleted": 0,
        "errors": []
    }

    try:
        logger.info(f"Cleaning up data older than {days_to_keep} days")

        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        # Delete old market intelligence with low relevance
        old_intel = db.query(MarketIntelligence).filter(
            MarketIntelligence.created_at < cutoff_date,
            MarketIntelligence.relevance_score < 0.5
        ).delete()

        result["records_deleted"] = old_intel

        db.commit()
        result["status"] = "completed"

        logger.info(f"Cleanup completed: {result['records_deleted']} records deleted")

    except Exception as e:
        logger.error(f"Error in cleanup task: {e}")
        result["status"] = "failed"
        result["errors"].append(str(e)")
        db.rollback()
    finally:
        db.close()

    return result


# Periodic task configuration (to be added to celery beat schedule)
CELERY_BEAT_SCHEDULE = {
    "daily-discovery": {
        "task": "daily_discovery_routine",
        "schedule": 86400.0,  # Daily (24 hours in seconds)
    },
    "hourly-monitoring": {
        "task": "monitor_companies",
        "schedule": 3600.0,  # Hourly
    },
    "weekly-cleanup": {
        "task": "cleanup_old_data",
        "schedule": 604800.0,  # Weekly
    }
}
