"""
Subscriber Acquisition Agent
Intelligent agent that identifies, qualifies, and converts prospects into subscribers
"""
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import random

from app.models.prospects import (
    Prospect, ProspectStatus, ProspectSource, LeadScore,
    IndustrySegment, OutreachCampaign, ProspectActivity
)
from app.services.outreach_service import (
    OutreachAutomation, LeadScoringEngine, PersonalizationEngine
)
from app.integrations.linkedin_api import (
    LinkedInAPI, LinkedInProspectEnricher
)

logger = logging.getLogger(__name__)

class ProspectIdentifier:
    """Identify and qualify potential prospects"""

    def __init__(self, db: Session):
        self.db = db
        self.linkedin_api = LinkedInAPI()
        self.enricher = LinkedInProspectEnricher()

    async def identify_prospects(
        self,
        source: str,
        limit: int = 100
    ) -> List[Prospect]:
        """Identify new prospects from various sources"""

        prospects = []

        if source == 'linkedin':
            prospects = await self._identify_linkedin_prospects(limit)
        elif source == 'website':
            prospects = self._identify_website_visitors(limit)
        elif source == 'referral':
            prospects = await self._identify_referrals(limit)
        elif source == 'content':
            prospects = self._identify_content_leads(limit)

        return prospects

    async def _identify_linkedin_prospects(self, limit: int) -> List[Prospect]:
        """Find prospects from LinkedIn Sales Navigator"""

        # Target search criteria for M&A professionals
        search_criteria = [
            {
                'keywords': ['M&A', 'mergers acquisitions', 'deal'],
                'industry': IndustrySegment.PRIVATE_EQUITY,
                'company_size': '201-500'
            },
            {
                'keywords': ['investment banking', 'corporate finance'],
                'industry': IndustrySegment.INVESTMENT_BANKING,
                'company_size': '501-1000'
            },
            {
                'keywords': ['business development', 'corporate strategy'],
                'industry': IndustrySegment.CORPORATE_DEVELOPMENT,
                'company_size': '1000+'
            }
        ]

        all_prospects = []

        for criteria in search_criteria:
            results = await self.linkedin_api.search_prospects(
                keywords=criteria['keywords'],
                industry=criteria.get('industry'),
                company_size=criteria.get('company_size'),
                limit=limit // len(search_criteria)
            )

            for result in results:
                # Check if prospect already exists
                existing = self.db.query(Prospect).filter(
                    or_(
                        Prospect.email == result.get('email'),
                        Prospect.linkedin_id == result.get('linkedin_id')
                    )
                ).first()

                if not existing:
                    prospect = Prospect(
                        email=result.get('email'),
                        first_name=result.get('first_name'),
                        last_name=result.get('last_name'),
                        title=result.get('title'),
                        company=result.get('company'),
                        linkedin_url=result.get('linkedin_url'),
                        linkedin_id=result.get('linkedin_id'),
                        linkedin_headline=result.get('headline'),
                        linkedin_connections=result.get('connections', 0),
                        industry_segment=criteria.get('industry'),
                        source=ProspectSource.LINKEDIN,
                        source_detail=f"Search: {' '.join(criteria['keywords'])}"
                    )

                    # Enrich with additional data
                    enriched = await self.enricher.enrich_prospect(prospect)
                    for key, value in enriched.items():
                        setattr(prospect, key, value)

                    self.db.add(prospect)
                    all_prospects.append(prospect)

        self.db.commit()
        return all_prospects

    def _identify_website_visitors(self, limit: int) -> List[Prospect]:
        """Identify prospects from website analytics"""

        # Query website activity for non-registered visitors
        # In production, integrate with analytics tools (GA4, Segment, etc.)

        activities = self.db.query(ProspectActivity).filter(
            and_(
                ProspectActivity.activity_type == 'website_visit',
                ProspectActivity.prospect_id.is_(None)  # Anonymous visitors
            )
        ).group_by(ProspectActivity.ip_address).having(
            func.count(ProspectActivity.id) >= 3  # Multiple visits
        ).limit(limit).all()

        prospects = []
        for activity_group in activities:
            # Try to identify visitor
            # In production, use IP enrichment services
            prospect = Prospect(
                source=ProspectSource.WEBSITE,
                source_detail=f"IP: {activity_group.ip_address}",
                website_visits=activity_group.count,
                last_activity_date=activity_group.created_at
            )
            self.db.add(prospect)
            prospects.append(prospect)

        self.db.commit()
        return prospects

    async def _identify_referrals(self, limit: int) -> List[Prospect]:
        """Identify prospects from referral network"""

        # Get existing customers who might refer
        # In production, integrate with referral tracking system

        referral_sources = [
            'podcast_guest',
            'partner_referral',
            'customer_referral'
        ]

        prospects = []
        for source in referral_sources:
            # Mock implementation
            # In production, pull from CRM or referral platform
            pass

        return prospects

    def _identify_content_leads(self, limit: int) -> List[Prospect]:
        """Identify prospects who consumed content"""

        # Find users who downloaded resources but aren't customers
        activities = self.db.query(ProspectActivity).filter(
            and_(
                ProspectActivity.activity_type == 'content_download',
                ProspectActivity.prospect_id.is_(None)
            )
        ).limit(limit).all()

        prospects = []
        for activity in activities:
            # Create prospect from content download
            prospect = Prospect(
                email=activity.activity_detail,  # Email from form
                source=ProspectSource.CONTENT,
                source_detail=activity.page_url,
                content_downloads=1
            )
            self.db.add(prospect)
            prospects.append(prospect)

        self.db.commit()
        return prospects

class ConversionOptimizer:
    """Optimize conversion rates through testing and personalization"""

    def __init__(self, db: Session):
        self.db = db
        self.personalization = PersonalizationEngine()

    def select_best_variant(
        self,
        campaign: OutreachCampaign,
        prospect: Prospect
    ) -> Dict[str, Any]:
        """Select best message variant for prospect"""

        if not campaign.ab_test_enabled:
            return campaign.templates[0] if campaign.templates else {}

        # Multi-armed bandit approach (Thompson Sampling)
        variants = campaign.ab_test_variants
        variant_scores = []

        for variant in variants:
            # Calculate success rate
            attempts = self.db.query(OutreachAttempt).filter(
                and_(
                    OutreachAttempt.campaign_id == campaign.id,
                    OutreachAttempt.message_template_id == variant['id']
                )
            ).count()

            conversions = self.db.query(OutreachAttempt).filter(
                and_(
                    OutreachAttempt.campaign_id == campaign.id,
                    OutreachAttempt.message_template_id == variant['id'],
                    OutreachAttempt.response_received == True
                )
            ).count()

            # Thompson Sampling score
            alpha = conversions + 1
            beta = attempts - conversions + 1
            score = random.betavariate(alpha, beta)

            variant_scores.append((variant, score))

        # Select variant with highest score
        best_variant = max(variant_scores, key=lambda x: x[1])[0]
        return best_variant

    def optimize_send_time(self, prospect: Prospect) -> datetime:
        """Determine optimal send time for prospect"""

        # Analyze past engagement patterns
        activities = self.db.query(ProspectActivity).filter(
            ProspectActivity.prospect_id == prospect.id
        ).all()

        if activities:
            # Find most common activity hours
            activity_hours = [a.created_at.hour for a in activities]
            if activity_hours:
                from collections import Counter
                most_common_hour = Counter(activity_hours).most_common(1)[0][0]

                # Schedule for that hour tomorrow
                send_time = datetime.utcnow().replace(
                    hour=most_common_hour,
                    minute=random.randint(0, 59)
                )
                if send_time <= datetime.utcnow():
                    send_time += timedelta(days=1)

                return send_time

        # Default: Business hours in prospect's timezone
        default_hour = random.choice([9, 10, 11, 14, 15, 16])  # Avoid lunch
        return datetime.utcnow().replace(hour=default_hour, minute=0)

    def segment_prospects(self) -> Dict[str, List[Prospect]]:
        """Segment prospects for targeted campaigns"""

        segments = {}

        # High-value segment
        segments['high_value'] = self.db.query(Prospect).filter(
            and_(
                Prospect.lead_score >= 70,
                Prospect.industry_segment.in_([
                    IndustrySegment.PRIVATE_EQUITY,
                    IndustrySegment.INVESTMENT_BANKING
                ])
            )
        ).all()

        # Engaged segment
        segments['engaged'] = self.db.query(Prospect).filter(
            and_(
                Prospect.website_visits >= 5,
                Prospect.content_downloads >= 1
            )
        ).all()

        # Trial-ready segment
        segments['trial_ready'] = self.db.query(Prospect).filter(
            and_(
                Prospect.lead_score >= 50,
                Prospect.last_activity_date >= datetime.utcnow() - timedelta(days=7)
            )
        ).all()

        # Re-engagement segment
        segments['re_engagement'] = self.db.query(Prospect).filter(
            and_(
                Prospect.status == ProspectStatus.ENGAGED,
                Prospect.last_activity_date < datetime.utcnow() - timedelta(days=30)
            )
        ).all()

        return segments

class SubscriberAcquisitionAgent:
    """Main agent orchestrating prospect acquisition and conversion"""

    def __init__(self, db: Session):
        self.db = db
        self.identifier = ProspectIdentifier(db)
        self.outreach = OutreachAutomation(db)
        self.optimizer = ConversionOptimizer(db)
        self.scorer = LeadScoringEngine()

    async def run_acquisition_cycle(self):
        """Run complete acquisition cycle"""

        logger.info("Starting subscriber acquisition cycle")

        # 1. Identify new prospects
        await self._identify_new_prospects()

        # 2. Score and qualify prospects
        self._score_all_prospects()

        # 3. Run active campaigns
        await self._run_campaigns()

        # 4. Process follow-ups
        await self._process_follow_ups()

        # 5. Optimize conversions
        self._optimize_campaigns()

        # 6. Generate reports
        self._generate_performance_report()

        logger.info("Acquisition cycle completed")

    async def _identify_new_prospects(self):
        """Identify prospects from all sources"""

        sources = ['linkedin', 'website', 'content']
        daily_limit = 100

        for source in sources:
            try:
                prospects = await self.identifier.identify_prospects(
                    source,
                    limit=daily_limit // len(sources)
                )
                logger.info(f"Identified {len(prospects)} prospects from {source}")
            except Exception as e:
                logger.error(f"Error identifying prospects from {source}: {e}")

    def _score_all_prospects(self):
        """Update lead scores for all prospects"""

        prospects = self.db.query(Prospect).filter(
            Prospect.status.in_([
                ProspectStatus.NEW,
                ProspectStatus.CONTACTED,
                ProspectStatus.ENGAGED
            ])
        ).all()

        for prospect in prospects:
            old_score = prospect.lead_score
            new_score, grade = self.scorer.calculate_lead_score(prospect)

            prospect.lead_score = new_score
            prospect.lead_grade = grade

            # Notify sales if needed
            if self.scorer.should_notify_sales(prospect, old_score, new_score):
                self._notify_sales_team(prospect)

        self.db.commit()

    async def _run_campaigns(self):
        """Execute all active campaigns"""

        campaigns = self.db.query(OutreachCampaign).filter(
            OutreachCampaign.status == 'active'
        ).all()

        for campaign in campaigns:
            try:
                await self.outreach.run_campaign(campaign.id)
            except Exception as e:
                logger.error(f"Error running campaign {campaign.name}: {e}")

    async def _process_follow_ups(self):
        """Process scheduled follow-ups"""

        try:
            await self.outreach.process_follow_ups()
        except Exception as e:
            logger.error(f"Error processing follow-ups: {e}")

    def _optimize_campaigns(self):
        """Optimize campaign performance"""

        campaigns = self.db.query(OutreachCampaign).filter(
            and_(
                OutreachCampaign.status == 'active',
                OutreachCampaign.ab_test_enabled == True
            )
        ).all()

        for campaign in campaigns:
            # Determine winning variant
            variants = campaign.ab_test_variants
            best_variant = None
            best_rate = 0

            for variant in variants:
                attempts = self.db.query(OutreachAttempt).filter(
                    and_(
                        OutreachAttempt.campaign_id == campaign.id,
                        OutreachAttempt.message_template_id == variant['id']
                    )
                ).count()

                if attempts >= 100:  # Minimum sample size
                    conversions = self.db.query(OutreachAttempt).filter(
                        and_(
                            OutreachAttempt.campaign_id == campaign.id,
                            OutreachAttempt.message_template_id == variant['id'],
                            OutreachAttempt.response_received == True
                        )
                    ).count()

                    conversion_rate = conversions / attempts
                    if conversion_rate > best_rate:
                        best_rate = conversion_rate
                        best_variant = variant

            if best_variant and best_rate > 0.05:  # 5% minimum conversion
                campaign.winning_variant = best_variant['id']
                campaign.ab_test_enabled = False  # Stop test
                logger.info(f"Campaign {campaign.name} winner: {best_variant['id']} ({best_rate:.2%})")

        self.db.commit()

    def _notify_sales_team(self, prospect: Prospect):
        """Notify sales team of hot lead"""

        # In production, integrate with CRM or notification system
        logger.info(f"HOT LEAD ALERT: {prospect.email} - Score: {prospect.lead_score}")

    def _generate_performance_report(self) -> Dict[str, Any]:
        """Generate acquisition performance metrics"""

        # Date ranges
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # Prospect metrics
        total_prospects = self.db.query(func.count(Prospect.id)).scalar()
        new_this_week = self.db.query(func.count(Prospect.id)).filter(
            Prospect.created_at >= week_ago
        ).scalar()
        new_this_month = self.db.query(func.count(Prospect.id)).filter(
            Prospect.created_at >= month_ago
        ).scalar()

        # Conversion metrics
        trials_this_month = self.db.query(func.count(Prospect.id)).filter(
            and_(
                Prospect.trial_start_date >= month_ago,
                Prospect.trial_start_date.isnot(None)
            )
        ).scalar()

        customers_this_month = self.db.query(func.count(Prospect.id)).filter(
            and_(
                Prospect.conversion_date >= month_ago,
                Prospect.conversion_date.isnot(None)
            )
        ).scalar()

        # Calculate conversion rates
        trial_conversion_rate = 0
        if trials_this_month > 0:
            trial_conversion_rate = (customers_this_month / trials_this_month) * 100

        # Campaign performance
        campaigns = self.db.query(OutreachCampaign).filter(
            OutreachCampaign.status == 'active'
        ).all()

        campaign_metrics = []
        for campaign in campaigns:
            campaign_metrics.append({
                'name': campaign.name,
                'contacted': campaign.prospects_contacted,
                'open_rate': campaign.open_rate,
                'click_rate': campaign.click_rate,
                'reply_rate': campaign.reply_rate,
                'cost_per_acquisition': campaign.cost_per_acquisition
            })

        # Source performance
        source_metrics = self.db.query(
            Prospect.source,
            func.count(Prospect.id).label('count'),
            func.avg(Prospect.lead_score).label('avg_score')
        ).group_by(Prospect.source).all()

        report = {
            'prospects': {
                'total': total_prospects,
                'new_this_week': new_this_week,
                'new_this_month': new_this_month
            },
            'conversions': {
                'trials_this_month': trials_this_month,
                'customers_this_month': customers_this_month,
                'trial_conversion_rate': trial_conversion_rate
            },
            'campaigns': campaign_metrics,
            'sources': [
                {
                    'source': str(s.source),
                    'count': s.count,
                    'avg_score': float(s.avg_score) if s.avg_score else 0
                }
                for s in source_metrics
            ],
            'generated_at': datetime.utcnow().isoformat()
        }

        logger.info(f"Performance Report: {report}")
        return report

    async def create_campaign(
        self,
        name: str,
        campaign_type: str,
        target_segment: Optional[IndustrySegment] = None,
        daily_limit: int = 50
    ) -> OutreachCampaign:
        """Create a new outreach campaign"""

        campaign = OutreachCampaign(
            name=name,
            campaign_type=campaign_type,
            target_segment=target_segment,
            daily_limit=daily_limit,
            status='draft',
            start_date=datetime.utcnow(),
            templates=self._get_default_templates(campaign_type),
            ab_test_enabled=True,
            gdpr_compliant=True,
            can_spam_compliant=True
        )

        self.db.add(campaign)
        self.db.commit()

        return campaign

    def _get_default_templates(self, campaign_type: str) -> List[Dict]:
        """Get default templates for campaign type"""

        templates = {
            'cold_outreach': [
                {
                    'id': 'cold_v1',
                    'subject': 'Quick question about {{company}}\'s M&A strategy',
                    'body_template': '''Hi {{first_name}},

I noticed {{company}} is actively involved in M&A transactions.

We're helping firms like yours reduce due diligence time by 40% and close deals 2x faster.

Would you be open to a brief 15-minute call to explore if there's a fit?

Best regards'''
                }
            ],
            'nurture': [
                {
                    'id': 'nurture_v1',
                    'subject': 'New M&A trends report for {{industry}}',
                    'body_template': '''Hi {{first_name}},

We just published our Q4 M&A trends report for the {{industry}} sector.

Key insights:
- Average deal multiples increased by 15%
- Due diligence timelines compressed by 30%
- ESG factors now impact 70% of valuations

Download the full report here: [Link]

Best regards'''
                }
            ],
            'trial_conversion': [
                {
                    'id': 'trial_v1',
                    'subject': '{{first_name}}, your trial ends in 3 days',
                    'body_template': '''Hi {{first_name}},

Your trial of 100daysandbeyond expires in 3 days.

During your trial, you've:
- Created {{deals_count}} deal pipelines
- Uploaded {{documents_count}} documents
- Saved {{time_saved}} hours

Ready to continue? Upgrade now and get 20% off your first year.

[Upgrade Now]

Best regards'''
                }
            ]
        }

        return templates.get(campaign_type, templates['cold_outreach'])