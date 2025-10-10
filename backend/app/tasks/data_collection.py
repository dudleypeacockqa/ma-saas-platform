"""
Data Collection Tasks for Deal Sourcing
Automated collection from Companies House, SEC EDGAR, and other sources
"""
import asyncio
import aiohttp
from celery import Celery, Task
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional
import os
import json
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import requests
from requests_ratelimiter import LimiterSession
from sqlalchemy.orm import Session
import re
import hashlib
from decimal import Decimal

from app.core.database import SessionLocal
from app.models.opportunities import (
    MarketOpportunity, OpportunitySource, OpportunityStatus,
    CompanyRegion, IndustryVertical, ActivityType
)
from app.services.deal_sourcing import (
    OpportunityDiscoveryService,
    OpportunityScoringService,
    OpportunityManagementService
)
import redis

logger = get_task_logger(__name__)

# Initialize Celery
celery_app = Celery(
    'data_collection',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    'scan-companies-house-daily': {
        'task': 'app.tasks.data_collection.scan_companies_house_daily',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'scan-sec-edgar-weekly': {
        'task': 'app.tasks.data_collection.scan_sec_edgar_weekly',
        'schedule': crontab(hour=3, minute=0, day_of_week=1),  # Weekly on Monday at 3 AM
    },
    'monitor-news-hourly': {
        'task': 'app.tasks.data_collection.monitor_market_news',
        'schedule': crontab(minute=0),  # Every hour
    },
    'score-new-opportunities': {
        'task': 'app.tasks.data_collection.score_unscored_opportunities',
        'schedule': crontab(hour=4, minute=0),  # Daily at 4 AM
    },
}

class DataCollectionTask(Task):
    """Base task with database session management"""
    _db = None
    _redis = None

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    @property
    def redis_client(self):
        if self._redis is None:
            self._redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
        return self._redis

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None

class CompaniesHouseAPI:
    """Companies House API client with rate limiting"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.company-information.service.gov.uk"
        # Companies House rate limit: 600 requests per 5 minutes
        self.session = LimiterSession(per_minute=120)
        self.session.auth = (api_key, '')

    async def search_companies(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search for companies matching criteria"""
        params = {
            'q': query,
            'items_per_page': 50,
            'start_index': 0
        }

        if filters:
            if 'size' in filters:
                params['size'] = filters['size']
            if 'status' in filters:
                params['company_status'] = filters['status']

        response = self.session.get(f"{self.base_url}/search/companies", params=params)

        if response.status_code == 200:
            data = response.json()
            return data.get('items', [])
        else:
            logger.error(f"Companies House API error: {response.status_code}")
            return []

    async def get_company_profile(self, company_number: str) -> Optional[Dict]:
        """Get detailed company profile"""
        response = self.session.get(f"{self.base_url}/company/{company_number}")

        if response.status_code == 200:
            return response.json()
        return None

    async def get_filing_history(self, company_number: str) -> List[Dict]:
        """Get company filing history"""
        response = self.session.get(f"{self.base_url}/company/{company_number}/filing-history")

        if response.status_code == 200:
            data = response.json()
            return data.get('items', [])
        return []

    async def get_accounts(self, company_number: str) -> Optional[Dict]:
        """Get company accounts data"""
        filings = await self.get_filing_history(company_number)

        # Find latest accounts filing
        for filing in filings:
            if filing.get('category') == 'accounts':
                # Get document metadata
                doc_response = self.session.get(
                    f"{self.base_url}/company/{company_number}/filing-history/{filing['transaction_id']}"
                )
                if doc_response.status_code == 200:
                    return doc_response.json()
        return None

class SECEdgarAPI:
    """SEC EDGAR API client for US company data"""

    def __init__(self):
        self.base_url = "https://www.sec.gov"
        self.data_url = "https://data.sec.gov"
        # SEC rate limit: 10 requests per second
        self.session = LimiterSession(per_second=10)
        self.session.headers.update({
            'User-Agent': 'M&A Platform (contact@100daysandbeyond.com)'
        })

    async def search_companies(self, query: str) -> List[Dict]:
        """Search for companies in EDGAR"""
        params = {
            'q': query,
            'count': 100
        }

        response = self.session.get(f"{self.data_url}/submissions/", params=params)

        if response.status_code == 200:
            return response.json()
        return []

    async def get_company_facts(self, cik: str) -> Optional[Dict]:
        """Get company facts and financials"""
        # Pad CIK to 10 digits
        cik = str(cik).zfill(10)

        response = self.session.get(f"{self.data_url}/api/xbrl/companyfacts/CIK{cik}.json")

        if response.status_code == 200:
            return response.json()
        return None

    async def get_recent_filings(self, cik: str, form_types: List[str] = None) -> List[Dict]:
        """Get recent filings for a company"""
        cik = str(cik).zfill(10)

        response = self.session.get(f"{self.data_url}/submissions/CIK{cik}.json")

        if response.status_code == 200:
            data = response.json()
            filings = data.get('filings', {}).get('recent', {})

            if form_types:
                # Filter by form type
                filtered = []
                for i in range(len(filings.get('form', []))):
                    if filings['form'][i] in form_types:
                        filtered.append({
                            'form': filings['form'][i],
                            'filingDate': filings['filingDate'][i],
                            'accessionNumber': filings['accessionNumber'][i],
                            'primaryDocument': filings.get('primaryDocument', [])[i] if i < len(filings.get('primaryDocument', [])) else None
                        })
                return filtered

            return filings
        return []

    def parse_xbrl_facts(self, facts: Dict) -> Dict:
        """Parse XBRL company facts into financial metrics"""
        financials = {}

        try:
            # Extract revenue
            if 'us-gaap' in facts.get('facts', {}):
                gaap = facts['facts']['us-gaap']

                # Revenue
                if 'Revenues' in gaap:
                    revenues = gaap['Revenues']['units']['USD']
                    latest_annual = [r for r in revenues if r.get('form') == '10-K']
                    if latest_annual:
                        financials['revenue'] = latest_annual[-1]['val']

                # Net Income
                if 'NetIncomeLoss' in gaap:
                    net_income = gaap['NetIncomeLoss']['units']['USD']
                    latest_annual = [n for n in net_income if n.get('form') == '10-K']
                    if latest_annual:
                        financials['net_income'] = latest_annual[-1]['val']

                # Total Assets
                if 'Assets' in gaap:
                    assets = gaap['Assets']['units']['USD']
                    latest = [a for a in assets if a.get('form') in ['10-K', '10-Q']]
                    if latest:
                        financials['total_assets'] = latest[-1]['val']

                # Total Liabilities
                if 'Liabilities' in gaap:
                    liabilities = gaap['Liabilities']['units']['USD']
                    latest = [l for l in liabilities if l.get('form') in ['10-K', '10-Q']]
                    if latest:
                        financials['total_liabilities'] = latest[-1]['val']

        except Exception as e:
            logger.error(f"Error parsing XBRL facts: {str(e)}")

        return financials

class MarketIntelligenceCollector:
    """Collect market intelligence from news and other sources"""

    def __init__(self, news_api_key: str):
        self.news_api_key = news_api_key
        self.session = LimiterSession(per_minute=60)  # Most news APIs limit to 1 req/sec

    async def collect_news(self, company_name: str, industry: str = None) -> List[Dict]:
        """Collect news articles about a company or industry"""
        articles = []

        # NewsAPI endpoint
        params = {
            'q': f'"{company_name}" AND (acquisition OR merger OR "M&A" OR buyout)',
            'apiKey': self.news_api_key,
            'language': 'en',
            'sortBy': 'relevancy',
            'pageSize': 20
        }

        response = self.session.get('https://newsapi.org/v2/everything', params=params)

        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])

        return articles

    def analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis"""
        positive_words = ['growth', 'profit', 'success', 'expansion', 'acquisition', 'strategic']
        negative_words = ['loss', 'bankruptcy', 'decline', 'layoff', 'closure', 'distressed']

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        return 'neutral'

@celery_app.task(base=DataCollectionTask, bind=True, name='app.tasks.data_collection.scan_companies_house_daily')
def scan_companies_house_daily(self, organization_id: str = None):
    """
    Daily scan of Companies House for UK opportunities

    Scans across multiple industries and identifies potential M&A targets
    """
    try:
        db = self.db
        discovery_service = OpportunityDiscoveryService(db)

        # Get all active organizations if no specific org provided
        if not organization_id:
            # Would query organizations from DB - for now use placeholder
            organizations = [organization_id] if organization_id else []
        else:
            organizations = [organization_id]

        total_opportunities = 0

        # Define industry scans
        industry_scans = [
            {"industry_sic": "62", "min_age_years": 3},  # IT/Software
            {"industry_sic": "86", "min_age_years": 5},  # Healthcare
            {"industry_sic": "45", "min_age_years": 5},  # Manufacturing
            {"industry_sic": "70", "min_age_years": 3},  # Professional services
        ]

        for org_id in organizations:
            for scan_filter in industry_scans:
                try:
                    opportunities = asyncio.run(
                        discovery_service.scan_companies_house(
                            organization_id=org_id,
                            filters=scan_filter
                        )
                    )
                    total_opportunities += len(opportunities)
                    logger.info(f"Found {len(opportunities)} opportunities in SIC {scan_filter['industry_sic']}")
                except Exception as e:
                    logger.error(f"Error scanning SIC {scan_filter['industry_sic']}: {str(e)}")
                    continue

        logger.info(f"Daily Companies House scan complete: {total_opportunities} total opportunities")

        return {
            'source': 'companies_house',
            'opportunities_discovered': total_opportunities,
            'organizations_scanned': len(organizations),
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Companies House daily scan error: {str(e)}")
        raise

@celery_app.task(base=DataCollectionTask, bind=True, name='app.tasks.data_collection.scan_sec_edgar_weekly')
def scan_sec_edgar_weekly(self, organization_id: str = None, cik_list: List[str] = None):
    """
    Weekly scan of SEC EDGAR for US opportunities

    Scans SEC filings and financial data for potential M&A targets
    """
    try:
        db = self.db
        discovery_service = OpportunityDiscoveryService(db)

        # Default CIK list for scanning (would be customizable per organization)
        if not cik_list:
            # Sample CIKs - in production would be from organization preferences
            cik_list = []

        # Get all active organizations if no specific org provided
        if not organization_id:
            organizations = []
        else:
            organizations = [organization_id]

        total_opportunities = 0

        for org_id in organizations:
            try:
                opportunities = asyncio.run(
                    discovery_service.scan_sec_edgar(
                        organization_id=org_id,
                        filters={"cik_list": cik_list}
                    )
                )
                total_opportunities += len(opportunities)
                logger.info(f"Found {len(opportunities)} US opportunities for org {org_id}")
            except Exception as e:
                logger.error(f"Error scanning SEC EDGAR for org {org_id}: {str(e)}")
                continue

        logger.info(f"Weekly SEC EDGAR scan complete: {total_opportunities} total opportunities")

        return {
            'source': 'sec_edgar',
            'opportunities_discovered': total_opportunities,
            'organizations_scanned': len(organizations),
            'ciks_scanned': len(cik_list),
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"SEC EDGAR weekly scan error: {str(e)}")
        raise

@celery_app.task(base=DataCollectionTask, bind=True, name='app.tasks.data_collection.monitor_market_news')
def monitor_market_news(self, organization_id: str = None):
    """
    Hourly monitoring of market news for M&A signals

    Monitors news sources for acquisition signals, distress indicators, and market opportunities
    """
    try:
        news_api_key = os.getenv('NEWS_API_KEY')
        if not news_api_key:
            logger.warning("News API key not configured - skipping news monitoring")
            return {
                'status': 'skipped',
                'reason': 'NEWS_API_KEY not configured'
            }

        collector = MarketIntelligenceCollector(news_api_key)
        db = self.db
        management_service = OpportunityManagementService(db)

        # Get qualified opportunities to monitor
        opportunities = db.query(MarketOpportunity).filter(
            MarketOpportunity.status.in_([
                OpportunityStatus.QUALIFIED,
                OpportunityStatus.CONTACTED,
                OpportunityStatus.IN_DISCUSSION
            ])
        )

        if organization_id:
            opportunities = opportunities.filter(
                MarketOpportunity.organization_id == organization_id
            )

        opportunities = opportunities.limit(50).all()

        total_articles = 0
        opportunities_with_news = 0

        for opportunity in opportunities:
            articles = asyncio.run(collector.collect_news(
                opportunity.company_name,
                opportunity.industry_vertical.value if opportunity.industry_vertical else None
            ))

            if articles:
                opportunities_with_news += 1

                for article in articles[:5]:  # Limit to 5 articles per company
                    # Check if already processed
                    url_hash = hashlib.md5(article['url'].encode()).hexdigest()
                    if self.redis_client.get(f"news:{url_hash}"):
                        continue

                    # Track as activity
                    management_service.track_activity(
                        opportunity_id=opportunity.id,
                        user_id="system",  # System-generated activity
                        activity_type=ActivityType.NOTE_ADDED,
                        description=f"News article: {article['title']}",
                        metadata={
                            'article_url': article['url'],
                            'source': article['source']['name'],
                            'published_at': article['publishedAt'],
                            'sentiment': collector.analyze_sentiment(article.get('description', ''))
                        }
                    )

                    total_articles += 1

                    # Cache to prevent reprocessing
                    self.redis_client.setex(f"news:{url_hash}", 86400, json.dumps({'processed': True}))

        logger.info(f"Monitored {len(opportunities)} opportunities, found {total_articles} relevant articles")

        return {
            'opportunities_monitored': len(opportunities),
            'opportunities_with_news': opportunities_with_news,
            'articles_collected': total_articles,
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"News monitoring error: {str(e)}")
        raise

@celery_app.task(base=DataCollectionTask, bind=True, name='app.tasks.data_collection.score_unscored_opportunities')
def score_unscored_opportunities(self, organization_id: str = None):
    """
    Score opportunities that haven't been scored yet

    Uses AI-powered scoring service to analyze and score new opportunities
    """
    try:
        db = self.db
        scoring_service = OpportunityScoringService(db)

        # Find opportunities without scores
        opportunities = db.query(MarketOpportunity).filter(
            MarketOpportunity.overall_score.is_(None)
        )

        if organization_id:
            opportunities = opportunities.filter(
                MarketOpportunity.organization_id == organization_id
            )

        opportunities = opportunities.limit(100).all()  # Batch process 100 at a time

        scored_count = 0

        for opportunity in opportunities:
            try:
                # Prepare company data for scoring
                company_data = {
                    "revenue": float(opportunity.annual_revenue) if opportunity.annual_revenue else 0,
                    "ebitda": float(opportunity.ebitda) if opportunity.ebitda else 0,
                    "industry": opportunity.industry_vertical.value if opportunity.industry_vertical else "other",
                    "region": opportunity.region.value if opportunity.region else "unknown",
                    "employee_count": opportunity.employee_count,
                    "revenue_growth_rate": 5.0,  # Would calculate from historical data
                    "profit_growth_rate": 3.0,
                    "market_share_trend": "stable",
                    "industry_match": True,
                    "geography_match": True,
                    "synergy_potential": "medium"
                }

                # Calculate score
                score = asyncio.run(
                    scoring_service.calculate_opportunity_score(
                        opportunity_id=opportunity.id,
                        company_data=company_data
                    )
                )

                scored_count += 1
                logger.info(f"Scored opportunity {opportunity.company_name}: {score.overall_score}/100")

            except Exception as e:
                logger.error(f"Error scoring opportunity {opportunity.id}: {str(e)}")
                continue

        logger.info(f"Scored {scored_count} out of {len(opportunities)} opportunities")

        return {
            'opportunities_scored': scored_count,
            'opportunities_processed': len(opportunities),
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Opportunity scoring error: {str(e)}")
        raise

# Helper methods for DataCollectionTask
def _map_company_type(self, uk_type: str) -> CompanyType:
    """Map UK company type to our enum"""
    mapping = {
        'ltd': CompanyType.PRIVATE_LIMITED,
        'plc': CompanyType.PUBLIC_LIMITED,
        'llp': CompanyType.LLP,
        'partnership': CompanyType.PARTNERSHIP
    }
    return mapping.get(uk_type, CompanyType.PRIVATE_LIMITED)

def _parse_date(self, date_str: str) -> Optional[date]:
    """Parse date string to date object"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return None

def _parse_datetime(self, dt_str: str) -> Optional[datetime]:
    """Parse datetime string"""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except:
        return None

def _format_address(self, address_dict: Dict) -> str:
    """Format UK address from dict"""
    if not address_dict:
        return ""

    parts = [
        address_dict.get('premises'),
        address_dict.get('address_line_1'),
        address_dict.get('address_line_2'),
        address_dict.get('locality'),
        address_dict.get('postal_code')
    ]

    return ', '.join(filter(None, parts))

def _process_uk_accounts(self, opportunity: Opportunity, accounts: Dict):
    """Process UK company accounts data"""
    # This would parse actual XBRL/iXBRL data
    # For now, using placeholder logic
    pass

def _check_action_required(self, article: Dict) -> bool:
    """Check if article requires action"""
    action_keywords = ['bankruptcy', 'acquisition', 'merger', 'sale', 'liquidation']
    content = (article.get('title', '') + ' ' + article.get('description', '')).lower()
    return any(keyword in content for keyword in action_keywords)

# Bind methods to task class
DataCollectionTask._map_company_type = _map_company_type
DataCollectionTask._parse_date = _parse_date
DataCollectionTask._parse_datetime = _parse_datetime
DataCollectionTask._format_address = _format_address
DataCollectionTask._process_uk_accounts = _process_uk_accounts
DataCollectionTask._check_action_required = _check_action_required