"""
Automated Outreach and Email Marketing Service
Handles personalized campaigns, nurture sequences, and conversion optimization
"""
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import hashlib
import re
from jinja2 import Template
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.prospects import (
    Prospect, OutreachAttempt, OutreachCampaign,
    ProspectActivity, MessageTemplate, ProspectStatus,
    LeadScore, ProspectSource
)
from app.integrations.linkedin_api import LinkedInAPI
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Email sending service with SendGrid integration"""

    def __init__(self):
        self.api_key = settings.SENDGRID_API_KEY
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        tracking_params: Optional[Dict] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Send email via SendGrid"""

        import httpx

        # Add tracking pixels and click tracking
        if tracking_params:
            tracking_pixel = self._create_tracking_pixel(tracking_params)
            html_content = html_content.replace('</body>', f'{tracking_pixel}</body>')

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'personalizations': [{
                'to': [{'email': to_email}]
            }],
            'from': {
                'email': self.from_email,
                'name': self.from_name
            },
            'subject': subject,
            'content': [
                {'type': 'text/html', 'value': html_content}
            ],
            'tracking_settings': {
                'click_tracking': {'enable': True},
                'open_tracking': {'enable': True}
            }
        }

        if text_content:
            payload['content'].append({'type': 'text/plain', 'value': text_content})

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    'https://api.sendgrid.com/v3/mail/send',
                    headers=headers,
                    json=payload
                )

                if response.status_code == 202:
                    return True, {'message_id': response.headers.get('X-Message-Id')}
                else:
                    return False, {'error': f'SendGrid error: {response.status_code}'}

        except Exception as e:
            logger.error(f"Email send error: {e}")
            return False, {'error': str(e)}

    def _create_tracking_pixel(self, params: Dict) -> str:
        """Create tracking pixel for email opens"""
        tracking_id = hashlib.md5(
            f"{params.get('prospect_id')}{params.get('campaign_id')}{datetime.utcnow()}".encode()
        ).hexdigest()

        return f'<img src="{settings.API_URL}/api/marketing/track/open/{tracking_id}" width="1" height="1" />'

    async def verify_email(self, email: str) -> bool:
        """Verify email deliverability"""

        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False

        # Check against known bounce list
        # In production, integrate with email verification service
        return True

class PersonalizationEngine:
    """Generate personalized messages using templates and prospect data"""

    def __init__(self):
        self.linkedin_api = LinkedInAPI()

    async def personalize_message(
        self,
        template: str,
        prospect: Prospect,
        additional_data: Optional[Dict] = None
    ) -> str:
        """Personalize message template with prospect data"""

        # Prepare personalization tokens
        tokens = {
            'first_name': prospect.first_name or 'there',
            'last_name': prospect.last_name or '',
            'full_name': f"{prospect.first_name or ''} {prospect.last_name or ''}".strip() or 'there',
            'company': prospect.company or 'your company',
            'title': prospect.title or 'your role',
            'industry': prospect.industry_segment or 'your industry',
            'current_date': datetime.utcnow().strftime('%B %d, %Y'),
            'current_year': datetime.utcnow().year
        }

        # Add additional data if provided
        if additional_data:
            tokens.update(additional_data)

        # Add dynamic content based on prospect behavior
        if prospect.website_visits > 5:
            tokens['engagement_line'] = "I noticed you've been exploring our platform recently."
        elif prospect.content_downloads > 0:
            tokens['engagement_line'] = "Thank you for downloading our resources."
        else:
            tokens['engagement_line'] = "I wanted to reach out to share how we're helping companies like yours."

        # Industry-specific value propositions
        value_props = {
            'private_equity': 'streamline due diligence and portfolio management',
            'investment_banking': 'accelerate deal flow and transaction management',
            'business_broker': 'manage multiple deals and client relationships efficiently',
            'corporate_development': 'identify and execute strategic acquisitions'
        }

        tokens['value_proposition'] = value_props.get(
            prospect.industry_segment,
            'transform your M&A process'
        )

        # Render template with tokens
        try:
            template_obj = Template(template)
            return template_obj.render(**tokens)
        except Exception as e:
            logger.error(f"Template personalization error: {e}")
            return template

    def generate_subject_line(
        self,
        prospect: Prospect,
        campaign_type: str
    ) -> str:
        """Generate personalized subject line"""

        subject_templates = {
            'cold_outreach': [
                "Quick question about {company}'s M&A strategy",
                "{first_name}, reducing DD time by 40% at {company}",
                "How {company} can close deals 2x faster"
            ],
            'nurture': [
                "New: {industry} M&A trends report",
                "{first_name}, your personalized deal pipeline update",
                "3 ways {company} can improve deal flow"
            ],
            'trial_conversion': [
                "{first_name}, your trial ends in 3 days",
                "Unlock full features for {company}",
                "Special offer for {company} - 20% off annual plan"
            ],
            're_engagement': [
                "{first_name}, we miss you at 100daysandbeyond",
                "What's changed since you last visited",
                "Exclusive comeback offer for {company}"
            ]
        }

        templates = subject_templates.get(campaign_type, subject_templates['cold_outreach'])
        import random
        template = random.choice(templates)

        return self.personalize_message(template, prospect)

class LeadScoringEngine:
    """Calculate and update lead scores based on behavior and attributes"""

    def calculate_lead_score(self, prospect: Prospect) -> Tuple[float, str]:
        """Calculate lead score and grade"""

        score = 0.0

        # Demographic scoring (40 points max)
        if prospect.industry_segment in [
            'private_equity', 'investment_banking', 'venture_capital'
        ]:
            score += 15
        elif prospect.industry_segment in [
            'corporate_development', 'family_office'
        ]:
            score += 10
        else:
            score += 5

        # Company size scoring
        size_scores = {
            '201-500': 10,
            '501-1000': 15,
            '1000+': 20,
            '51-200': 8,
            '11-50': 5
        }
        score += size_scores.get(prospect.company_size, 3)

        # Title/seniority scoring
        if prospect.title:
            title_lower = prospect.title.lower()
            if any(term in title_lower for term in ['ceo', 'president', 'founder', 'owner']):
                score += 20
            elif any(term in title_lower for term in ['vp', 'vice president', 'director', 'partner']):
                score += 15
            elif any(term in title_lower for term in ['manager', 'head of', 'lead']):
                score += 10
            else:
                score += 5

        # Behavioral scoring (60 points max)
        score += min(prospect.website_visits * 2, 15)  # Max 15 points
        score += min(prospect.page_views * 0.5, 10)     # Max 10 points
        score += prospect.content_downloads * 5         # 5 points per download
        score += prospect.email_opens * 1               # 1 point per open
        score += prospect.email_clicks * 3              # 3 points per click

        # Engagement recency boost
        if prospect.last_activity_date:
            days_since_activity = (datetime.utcnow() - prospect.last_activity_date).days
            if days_since_activity <= 7:
                score += 10
            elif days_since_activity <= 30:
                score += 5

        # Source quality bonus
        high_quality_sources = [
            ProspectSource.REFERRAL,
            ProspectSource.PODCAST,
            ProspectSource.WEBINAR
        ]
        if prospect.source in high_quality_sources:
            score += 10

        # Determine grade based on score
        if score >= 80:
            grade = LeadScore.HOT
        elif score >= 50:
            grade = LeadScore.WARM
        elif score >= 25:
            grade = LeadScore.COLD
        else:
            grade = LeadScore.UNQUALIFIED

        return min(score, 100), grade

    def should_notify_sales(self, prospect: Prospect, old_score: float, new_score: float) -> bool:
        """Determine if sales should be notified of score change"""

        # Notify if prospect becomes hot
        if new_score >= 80 and old_score < 80:
            return True

        # Notify if significant score increase
        if new_score - old_score >= 20:
            return True

        # Notify if specific high-value actions
        if prospect.trial_start_date:
            return True

        return False

class OutreachAutomation:
    """Main outreach automation service"""

    def __init__(self, db: Session):
        self.db = db
        self.email_service = EmailService()
        self.personalization = PersonalizationEngine()
        self.lead_scoring = LeadScoringEngine()
        self.linkedin_api = LinkedInAPI()

    async def run_campaign(self, campaign_id: str):
        """Execute an outreach campaign"""

        campaign = self.db.query(OutreachCampaign).filter(
            OutreachCampaign.id == campaign_id
        ).first()

        if not campaign or campaign.status != 'active':
            return

        # Get prospects for campaign
        prospects = self._get_campaign_prospects(campaign)

        # Check daily limits
        sent_today = self.db.query(func.count(OutreachAttempt.id)).filter(
            and_(
                OutreachAttempt.campaign_id == campaign_id,
                func.date(OutreachAttempt.sent_at) == datetime.utcnow().date()
            )
        ).scalar()

        remaining_today = campaign.daily_limit - sent_today

        for prospect in prospects[:remaining_today]:
            await self._process_prospect_outreach(campaign, prospect)
            await asyncio.sleep(5)  # Rate limiting

        # Update campaign metrics
        self._update_campaign_metrics(campaign)

    def _get_campaign_prospects(self, campaign: OutreachCampaign) -> List[Prospect]:
        """Get qualified prospects for campaign"""

        query = self.db.query(Prospect)

        # Apply campaign filters
        if campaign.target_segment:
            query = query.filter(Prospect.industry_segment == campaign.target_segment)

        # Exclude already contacted
        contacted_ids = self.db.query(OutreachAttempt.prospect_id).filter(
            OutreachAttempt.campaign_id == campaign.id
        ).subquery()

        query = query.filter(~Prospect.id.in_(contacted_ids))

        # Exclude opted out
        query = query.filter(
            and_(
                Prospect.do_not_contact == False,
                Prospect.marketing_consent == True
            )
        )

        # Order by lead score
        query = query.order_by(Prospect.lead_score.desc())

        return query.limit(100).all()

    async def _process_prospect_outreach(self, campaign: OutreachCampaign, prospect: Prospect):
        """Process outreach for a single prospect"""

        # Select template and channel
        template = self._select_template(campaign, prospect)
        channel = self._determine_channel(prospect)

        # Personalize message
        subject = self.personalization.generate_subject_line(prospect, campaign.campaign_type)
        message = await self.personalization.personalize_message(
            template['body_template'],
            prospect
        )

        # Create outreach attempt record
        attempt = OutreachAttempt(
            prospect_id=prospect.id,
            campaign_id=campaign.id,
            channel=channel,
            message_template_id=template.get('id'),
            personalized_message=message,
            subject_line=subject,
            status='pending'
        )
        self.db.add(attempt)
        self.db.flush()

        # Send based on channel
        success = False
        if channel == 'email':
            success, result = await self.email_service.send_email(
                prospect.email,
                subject,
                message,
                tracking_params={
                    'prospect_id': str(prospect.id),
                    'campaign_id': str(campaign.id),
                    'attempt_id': str(attempt.id)
                }
            )
        elif channel == 'linkedin':
            if prospect.linkedin_id:
                success = await self.linkedin_api.send_message(
                    prospect.linkedin_id,
                    subject,
                    message
                )

        # Update attempt status
        if success:
            attempt.status = 'sent'
            attempt.sent_at = datetime.utcnow()
            prospect.status = ProspectStatus.CONTACTED
            campaign.prospects_contacted += 1
            campaign.emails_sent += 1
        else:
            attempt.status = 'failed'

        self.db.commit()

    def _select_template(self, campaign: OutreachCampaign, prospect: Prospect) -> Dict:
        """Select best template for prospect"""

        # For A/B testing
        if campaign.ab_test_enabled and campaign.ab_test_variants:
            import random
            return random.choice(campaign.ab_test_variants)

        # Select based on prospect attributes
        if campaign.templates:
            # Score templates based on prospect match
            best_template = campaign.templates[0]
            for template in campaign.templates:
                if template.get('segment') == prospect.industry_segment:
                    best_template = template
                    break

            return best_template

        # Default template
        return {
            'id': 'default',
            'body_template': "Hi {{first_name}}, {{engagement_line}} {{value_proposition}}..."
        }

    def _determine_channel(self, prospect: Prospect) -> str:
        """Determine best outreach channel"""

        # Check preferences
        if prospect.contact_preferences:
            preferred = prospect.contact_preferences.get('preferred_channel')
            if preferred:
                return preferred

        # Use email if available
        if prospect.email and prospect.marketing_consent:
            return 'email'

        # Use LinkedIn if connected
        if prospect.linkedin_id:
            return 'linkedin'

        return 'email'  # Default

    def _update_campaign_metrics(self, campaign: OutreachCampaign):
        """Update campaign performance metrics"""

        # Calculate open rate
        opens = self.db.query(func.count(OutreachAttempt.id)).filter(
            and_(
                OutreachAttempt.campaign_id == campaign.id,
                OutreachAttempt.opened_at.isnot(None)
            )
        ).scalar()

        sent = self.db.query(func.count(OutreachAttempt.id)).filter(
            and_(
                OutreachAttempt.campaign_id == campaign.id,
                OutreachAttempt.status == 'sent'
            )
        ).scalar()

        if sent > 0:
            campaign.open_rate = (opens / sent) * 100

            # Calculate click rate
            clicks = self.db.query(func.count(OutreachAttempt.id)).filter(
                and_(
                    OutreachAttempt.campaign_id == campaign.id,
                    OutreachAttempt.clicked_at.isnot(None)
                )
            ).scalar()
            campaign.click_rate = (clicks / sent) * 100

            # Calculate reply rate
            replies = self.db.query(func.count(OutreachAttempt.id)).filter(
                and_(
                    OutreachAttempt.campaign_id == campaign.id,
                    OutreachAttempt.replied_at.isnot(None)
                )
            ).scalar()
            campaign.reply_rate = (replies / sent) * 100

        self.db.commit()

    async def process_follow_ups(self):
        """Process scheduled follow-up messages"""

        # Get attempts requiring follow-up
        attempts = self.db.query(OutreachAttempt).filter(
            and_(
                OutreachAttempt.requires_follow_up == True,
                OutreachAttempt.follow_up_date <= datetime.utcnow(),
                OutreachAttempt.response_received == False
            )
        ).limit(50).all()

        for attempt in attempts:
            await self._send_follow_up(attempt)

    async def _send_follow_up(self, original_attempt: OutreachAttempt):
        """Send follow-up message"""

        prospect = original_attempt.prospect
        campaign = original_attempt.campaign

        # Generate follow-up message
        follow_up_template = """
        Hi {{first_name}},

        I wanted to follow up on my previous message about {{value_proposition}}.

        I understand you're busy, but I believe we can add significant value to {{company}}'s M&A process.

        Would you be open to a quick 15-minute call this week to explore if there's a fit?

        Best regards
        """

        message = await self.personalization.personalize_message(
            follow_up_template,
            prospect
        )

        # Create new attempt
        attempt = OutreachAttempt(
            prospect_id=prospect.id,
            campaign_id=campaign.id if campaign else None,
            channel=original_attempt.channel,
            attempt_number=original_attempt.attempt_number + 1,
            personalized_message=message,
            subject_line=f"Re: {original_attempt.subject_line}",
            status='pending'
        )
        self.db.add(attempt)

        # Send message
        if original_attempt.channel == 'email':
            success, _ = await self.email_service.send_email(
                prospect.email,
                attempt.subject_line,
                message
            )
            if success:
                attempt.status = 'sent'
                attempt.sent_at = datetime.utcnow()

        # Mark original as followed up
        original_attempt.requires_follow_up = False
        self.db.commit()

class ComplianceManager:
    """Ensure compliance with marketing regulations"""

    @staticmethod
    def check_gdpr_compliance(prospect: Prospect) -> bool:
        """Check GDPR compliance for EU prospects"""

        # Check consent
        if not prospect.gdpr_consent:
            return False

        # Check consent age (re-confirm after 2 years)
        if prospect.gdpr_consent_date:
            days_since_consent = (datetime.utcnow() - prospect.gdpr_consent_date).days
            if days_since_consent > 730:  # 2 years
                return False

        return True

    @staticmethod
    def check_can_spam_compliance(message: str, subject: str) -> Tuple[bool, List[str]]:
        """Check CAN-SPAM compliance"""

        issues = []

        # Check for unsubscribe link
        if 'unsubscribe' not in message.lower():
            issues.append("Missing unsubscribe link")

        # Check for physical address
        if not any(term in message.lower() for term in ['address', 'location', 'suite', 'street']):
            issues.append("Missing physical address")

        # Check for misleading subject
        spam_terms = ['free', 'guarantee', 'no risk', 'winner', 'urgent']
        for term in spam_terms:
            if term in subject.lower():
                issues.append(f"Potentially misleading term in subject: {term}")

        return len(issues) == 0, issues

    @staticmethod
    def add_compliance_footer(message: str, prospect_id: str) -> str:
        """Add compliant footer to email"""

        unsubscribe_url = f"{settings.API_URL}/unsubscribe/{prospect_id}"

        footer = f"""
        <hr>
        <p style="font-size: 12px; color: #666;">
        100daysandbeyond.com | 123 Business St, Suite 100, London, UK<br>
        You received this email because you expressed interest in M&A solutions.<br>
        <a href="{unsubscribe_url}">Unsubscribe</a> | <a href="{settings.API_URL}/preferences/{prospect_id}">Update Preferences</a>
        </p>
        """

        return message + footer