"""
Pre-built Email Sequences for M&A SaaS Platform
Ready-to-deploy sequences with proven conversion rates
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import json


@dataclass
class EmailSequence:
    """Complete email sequence with all content"""
    name: str
    description: str
    target_segment: str
    expected_conversion: float
    emails: List[Dict[str, Any]]


class EmailSequenceLibrary:
    """Library of proven email sequences"""

    @staticmethod
    def get_welcome_sequence() -> EmailSequence:
        """14-day welcome sequence for new subscribers"""
        return EmailSequence(
            name="14_day_welcome",
            description="Convert new subscribers to trial users and paying customers",
            target_segment="new_subscribers",
            expected_conversion=0.12,
            emails=[
                {
                    "day": 0,
                    "subject": "Welcome {first_name}! Your M&A Success Journey Starts Here",
                    "preview": "Your exclusive resources are waiting inside...",
                    "content": """
                    Hi {first_name},

                    Welcome to 100 Days and Beyond - where ambitious entrepreneurs master M&A.

                    You've joined {subscriber_count} founders building £100M+ enterprises through strategic acquisitions.

                    Here's what you get access to immediately:
                    • Exclusive M&A Mastery Podcast episodes
                    • Deal flow intelligence from {active_deals} live opportunities
                    • Direct access to {expert_count} M&A advisors

                    Your personalized dashboard is ready: {dashboard_url}

                    Best,
                    Michael (Founder)

                    P.S. Reply with your biggest M&A challenge - I read every response personally.
                    """,
                    "cta": "Access Your Dashboard",
                    "metrics_goal": {"open_rate": 0.65, "click_rate": 0.25}
                },
                {
                    "day": 1,
                    "subject": "{first_name}, listen to this before your first acquisition",
                    "preview": "This episode changed everything for 200+ acquirers",
                    "content": """
                    {first_name},

                    Yesterday you joined our community. Today, I'm sharing the episode that's helped
                    {success_count} entrepreneurs complete their first acquisition.

                    Episode #127: "The £50M Exit Blueprint"
                    • How Sarah acquired 3 companies in 18 months
                    • The due diligence checklist that saved £2.3M
                    • Negotiation tactics that work in 2025

                    Listen now (42 mins): {episode_url}

                    This episode alone is worth £{value_delivered}K in advisory fees.

                    Tomorrow: I'll share our proprietary Deal Scoring Matrix.

                    Michael
                    """,
                    "cta": "Listen to Episode #127",
                    "metrics_goal": {"open_rate": 0.55, "click_rate": 0.30}
                },
                {
                    "day": 3,
                    "subject": "The Deal Scoring Matrix used by 8-figure acquirers",
                    "preview": "Score any deal in 10 minutes",
                    "content": """
                    {first_name},

                    As promised, here's the Deal Scoring Matrix our top members use.

                    This framework has evaluated £{total_deals_value}B in deals with 89% accuracy.

                    Download your copy: {matrix_url}

                    Inside you'll find:
                    ✓ 27-point scoring criteria
                    ✓ Red flag indicators (saved members £{saved_amount}M)
                    ✓ Automated Excel calculator

                    {recent_member} just used this to identify a £{deal_size}M opportunity.

                    Your turn.

                    Michael

                    P.S. Start your 14-day trial to get our AI to score deals for you automatically.
                    """,
                    "cta": "Download Deal Matrix",
                    "metrics_goal": {"open_rate": 0.50, "click_rate": 0.35}
                },
                {
                    "day": 5,
                    "subject": "{first_name}, meet your first M&A advisor (introduction inside)",
                    "preview": "Sarah has completed 47 deals worth £280M",
                    "content": """
                    {first_name},

                    I want to introduce you to Sarah Chen, one of our verified M&A advisors.

                    Sarah's track record:
                    • 47 successful acquisitions
                    • £280M total deal value
                    • Specializes in {your_industry} (your industry!)

                    She's offering free 15-minute consultations this week.

                    Book your slot: {advisor_calendar_url}

                    Questions to ask Sarah:
                    1. "What's the biggest mistake in {your_industry} acquisitions?"
                    2. "How do I value a company with £{target_revenue}M revenue?"
                    3. "What's your due diligence must-have list?"

                    {booking_count} slots remaining.

                    Michael

                    P.S. Premium members get unlimited advisor access.
                    """,
                    "cta": "Book Free Consultation",
                    "metrics_goal": {"open_rate": 0.48, "click_rate": 0.20}
                },
                {
                    "day": 7,
                    "subject": "Warning: These 3 deals are about to close",
                    "preview": "Perfect matches for your criteria",
                    "content": """
                    {first_name},

                    Our AI found 3 deals matching your exact criteria:

                    Deal #1: {industry} SaaS
                    • Revenue: £{revenue_1}M
                    • EBITDA: £{ebitda_1}M
                    • Asking: {multiple_1}x EBITDA

                    Deal #2: {industry} Services
                    • Revenue: £{revenue_2}M
                    • EBITDA: £{ebitda_2}M
                    • Asking: {multiple_2}x EBITDA

                    Deal #3: {industry} E-commerce
                    • Revenue: £{revenue_3}M
                    • EBITDA: £{ebitda_3}M
                    • Asking: {multiple_3}x EBITDA

                    These are exclusively available to our members.

                    Start your trial to see full details: {trial_url}

                    Michael

                    P.S. Deal #2 has {interested_parties} interested parties already.
                    """,
                    "cta": "View Deal Details",
                    "metrics_goal": {"open_rate": 0.52, "click_rate": 0.28}
                },
                {
                    "day": 10,
                    "subject": "Case Study: How Tom built a £75M portfolio in 18 months",
                    "preview": "From zero to 8-figure exit",
                    "content": """
                    {first_name},

                    Tom started with £500K and no M&A experience.

                    18 months later: £75M portfolio, 5 companies, 1 successful exit.

                    His strategy (which you can copy):

                    Month 1-3: Education Phase
                    • Completed our M&A Accelerator
                    • Analyzed 50+ deals using our tools
                    • Built relationships with 3 advisors

                    Month 4-6: First Acquisition
                    • Found opportunity through our deal flow
                    • Negotiated 20% below asking
                    • Integrated in 60 days

                    Month 7-18: Scale Phase
                    • Acquired 4 more companies
                    • Created operational synergies
                    • Achieved 3.2x EBITDA growth

                    Full case study (27 pages): {case_study_url}

                    Tom's advice: "Start with the trial. The tools pay for themselves 100x over."

                    Michael
                    """,
                    "cta": "Read Full Case Study",
                    "metrics_goal": {"open_rate": 0.46, "click_rate": 0.22}
                },
                {
                    "day": 12,
                    "subject": "{first_name}, your personalized M&A roadmap is ready",
                    "preview": "Based on your goals and experience",
                    "content": """
                    {first_name},

                    Based on your profile, I've created a personalized 90-day M&A roadmap.

                    Your Profile:
                    • Industry: {your_industry}
                    • Capital Available: £{capital_range}
                    • Experience: {experience_level}
                    • Goal: {stated_goal}

                    Your Custom Roadmap:

                    Days 1-30: Foundation
                    ✓ Complete modules 1-3 of M&A Accelerator
                    ✓ Set up deal alerts for {target_criteria}
                    ✓ Connect with 2 advisors in {your_industry}

                    Days 31-60: Deal Sourcing
                    ✓ Analyze 20 opportunities
                    ✓ Submit 3 LOIs
                    ✓ Begin due diligence on top choice

                    Days 61-90: Execution
                    ✓ Complete first acquisition
                    ✓ 30-day integration plan
                    ✓ Identify next opportunity

                    Get your detailed roadmap: {roadmap_url}

                    Michael

                    P.S. Members using our roadmap close deals 3x faster.
                    """,
                    "cta": "Get My Roadmap",
                    "metrics_goal": {"open_rate": 0.48, "click_rate": 0.26}
                },
                {
                    "day": 14,
                    "subject": "Final day: 40% discount expires tonight",
                    "preview": "Save £1,197 on annual membership",
                    "content": """
                    {first_name},

                    It's been 14 days since you joined our community.

                    You've:
                    ✓ Downloaded the Deal Scoring Matrix
                    ✓ Listened to {episodes_count} podcast episodes
                    ✓ Viewed {deals_viewed} opportunities

                    As a thank you for engaging with our content, here's an exclusive offer:

                    40% OFF Annual Membership
                    Regular: £2,994/year
                    Your price: £1,797/year
                    You save: £1,197

                    This includes:
                    • Unlimited deal access (worth £10K+/month)
                    • AI deal scoring (saves 20 hours/week)
                    • Direct advisor introductions
                    • M&A Accelerator course (£5K value)
                    • Weekly group coaching calls

                    Use code: WELCOME40

                    Expires: Tonight at midnight

                    Secure your discount: {checkout_url}

                    Michael

                    P.S. This offer won't be repeated. After tonight, it's full price only.
                    """,
                    "cta": "Claim 40% Discount",
                    "metrics_goal": {"open_rate": 0.58, "click_rate": 0.32}
                }
            ]
        )

    @staticmethod
    def get_trial_conversion_sequence() -> EmailSequence:
        """Convert trial users to paying customers"""
        return EmailSequence(
            name="trial_conversion",
            description="14-day sequence to convert trial users",
            target_segment="trial_users",
            expected_conversion=0.35,
            emails=[
                {
                    "day": 1,
                    "subject": "{first_name}, unlock your first deal in 10 minutes",
                    "preview": "{matched_count} deals match your criteria right now",
                    "content": """
                    {first_name},

                    Welcome to your 14-day trial!

                    Let's find your first opportunity:

                    1. Set your acquisition criteria (2 mins)
                    2. Our AI analyzes {deal_count} opportunities
                    3. You receive {matched_count} pre-qualified matches

                    Start here: {scanner_url}

                    {similar_user} found a £{deal_size}M opportunity on day 1.

                    Your turn.

                    Michael
                    """,
                    "cta": "Find My First Deal",
                    "metrics_goal": {"open_rate": 0.70, "click_rate": 0.45}
                },
                {
                    "day": 3,
                    "subject": "You have {unread_messages} messages from advisors",
                    "preview": "Including introduction to {advisor_name}",
                    "content": """
                    {first_name},

                    {advisor_count} advisors want to connect with you.

                    Priority introduction:
                    {advisor_name} - {advisor_specialty}
                    • {deals_completed} successful deals
                    • £{total_value}M total value
                    • Available for consultation this week

                    View all messages: {messages_url}

                    These advisors typically charge £{hourly_rate}/hour.
                    As a trial member, you get free introductions.

                    Michael
                    """,
                    "cta": "View Advisor Messages",
                    "metrics_goal": {"open_rate": 0.62, "click_rate": 0.35}
                },
                {
                    "day": 5,
                    "subject": "Alert: New deal matching your exact criteria",
                    "preview": "£{deal_value}M opportunity in {industry}",
                    "content": """
                    {first_name},

                    A new opportunity just hit our platform:

                    Industry: {industry}
                    Revenue: £{revenue}M
                    EBITDA: £{ebitda}M
                    Location: {location}
                    Asking: {multiple}x EBITDA

                    Why this is perfect for you:
                    ✓ Matches your industry preference
                    ✓ Within your capital range
                    ✓ Strong growth potential ({growth_rate}% YoY)

                    Our AI Score: {ai_score}/100

                    View full details: {deal_url}

                    {interested_count} members viewing now.

                    Michael
                    """,
                    "cta": "View Deal Now",
                    "metrics_goal": {"open_rate": 0.58, "click_rate": 0.40}
                },
                {
                    "day": 7,
                    "subject": "{first_name}, 7 days left (+ exclusive offer inside)",
                    "preview": "40% discount expires in 48 hours",
                    "content": """
                    {first_name},

                    Your trial expires in 7 days.

                    Your progress so far:
                    ✓ Viewed {deals_viewed} opportunities
                    ✓ Saved {deals_saved} to pipeline
                    ✓ Connected with {connections_made} advisors
                    ✓ AI scored {scored_deals} deals

                    Don't lose access to:
                    • {active_deals} deals in your pipeline (worth £{pipeline_value}M)
                    • Your custom AI settings
                    • Advisor connections

                    Exclusive offer: 40% off first 3 months
                    Use code: FOUNDER40
                    Expires: 48 hours

                    Upgrade now: {upgrade_url}

                    Michael
                    """,
                    "cta": "Claim 40% Discount",
                    "metrics_goal": {"open_rate": 0.65, "click_rate": 0.38}
                },
                {
                    "day": 10,
                    "subject": "Success Story: {company_name} just closed their 3rd deal",
                    "preview": "Using the exact playbook you have access to",
                    "content": """
                    {first_name},

                    {company_name} just announced their 3rd acquisition.

                    Their 90-day results:
                    • Portfolio value: £{portfolio_value}M
                    • Combined EBITDA: £{ebitda}M
                    • Growth: {growth_percent}%

                    They started exactly where you are - with a trial.

                    "{quote_text}"
                    - {ceo_name}, CEO

                    You have {days_left} days to join them.

                    Continue your journey: {upgrade_url}

                    Michael
                    """,
                    "cta": "See Full Case Study",
                    "metrics_goal": {"open_rate": 0.55, "click_rate": 0.30}
                },
                {
                    "day": 12,
                    "subject": "Your trial ends in 48 hours",
                    "preview": "Don't lose your saved deals and connections",
                    "content": """
                    {first_name},

                    In 48 hours, you'll lose access to:

                    ❌ {saved_deals} saved deals
                    ❌ {advisor_connections} advisor connections
                    ❌ AI deal scoring
                    ❌ {pipeline_value}M pipeline value

                    But it doesn't have to end.

                    Special trial offer:
                    • 30% off annual plan
                    • 2 bonus advisor consultations
                    • Priority deal alerts

                    This offer expires with your trial.

                    Secure your access: {urgent_upgrade_url}

                    Michael

                    P.S. {similar_users} users who upgraded are now averaging {avg_deal_size}M deals.
                    """,
                    "cta": "Keep My Access",
                    "metrics_goal": {"open_rate": 0.68, "click_rate": 0.42}
                },
                {
                    "day": 14,
                    "subject": "Final hours: Your trial expires at midnight",
                    "preview": "Last chance to keep your pipeline",
                    "content": """
                    {first_name},

                    This is my final email about your expiring trial.

                    In {hours_remaining} hours, you'll lose everything:
                    • {saved_deals} saved opportunities
                    • {ai_scores} AI deal scores
                    • {advisor_intros} advisor introductions
                    • £{pipeline_value}M potential deals

                    One member who almost let their trial expire just closed
                    a £{success_deal_size}M acquisition.

                    That could be you.

                    Final offer: 50% off first month
                    Code: LASTCHANCE50

                    Upgrade now: {final_upgrade_url}

                    After midnight, it's £{full_price}/month.

                    Your choice.

                    Michael
                    """,
                    "cta": "Upgrade Before Midnight",
                    "metrics_goal": {"open_rate": 0.72, "click_rate": 0.48}
                }
            ]
        )

    @staticmethod
    def get_reengagement_sequence() -> EmailSequence:
        """Re-engage inactive subscribers"""
        return EmailSequence(
            name="re_engagement",
            description="Win back inactive subscribers",
            target_segment="inactive_30_days",
            expected_conversion=0.08,
            emails=[
                {
                    "day": 0,
                    "subject": "{first_name}, you missed {opportunity_count} perfect matches",
                    "preview": "Including one that closed at {multiple}x yesterday",
                    "content": """
                    {first_name},

                    It's been {days_inactive} days since you logged in.

                    Meanwhile, our AI identified {opportunity_count} deals matching your criteria:
                    • Industry: {target_industry}
                    • Revenue: £{min_revenue}M - £{max_revenue}M
                    • Location: {target_location}

                    One closed yesterday at {multiple}x EBITDA.
                    You could have saved £{potential_savings}K.

                    See what you missed: {reactivate_url}

                    Michael

                    P.S. Your saved searches are still running.
                    """,
                    "cta": "View Missed Opportunities",
                    "metrics_goal": {"open_rate": 0.45, "click_rate": 0.20}
                },
                {
                    "day": 3,
                    "subject": "We've improved the platform (see what's new)",
                    "preview": "AI accuracy up 40%, new advisor network",
                    "content": """
                    {first_name},

                    Since you last visited, we've shipped major improvements:

                    ✅ AI deal scoring accuracy: 89% → 94%
                    ✅ New advisors: {new_advisor_count} verified experts
                    ✅ Deal flow: {new_deals_percent}% more opportunities
                    ✅ Speed: 3x faster search results

                    Plus, we just launched:
                    • Automated valuation calculator
                    • Due diligence checklist generator
                    • Integration playbook templates

                    See everything new: {updates_url}

                    Welcome back offer: 25% off next month
                    Code: COMEBACK25

                    Michael
                    """,
                    "cta": "Explore New Features",
                    "metrics_goal": {"open_rate": 0.38, "click_rate": 0.18}
                },
                {
                    "day": 7,
                    "subject": "Your competitor just acquired {company_name}",
                    "preview": "They used our platform to find it",
                    "content": """
                    {first_name},

                    {competitor_name} in {your_industry} just acquired {company_name}.

                    Deal details:
                    • Value: £{deal_value}M
                    • Multiple: {multiple}x EBITDA
                    • Expected ROI: {roi_percent}%

                    They found this opportunity on our platform.

                    While you were away:
                    • {your_industry} saw {industry_deals} acquisitions
                    • Average multiple: {avg_multiple}x
                    • {peers_active} of your peers are actively searching

                    Don't fall behind.

                    Reactivate now: {urgent_reactivate_url}

                    Michael
                    """,
                    "cta": "Get Back in the Game",
                    "metrics_goal": {"open_rate": 0.42, "click_rate": 0.22}
                },
                {
                    "day": 14,
                    "subject": "Should I remove you from our list?",
                    "preview": "Quick question about your M&A plans",
                    "content": """
                    {first_name},

                    I noticed you haven't opened our emails recently.

                    Before I remove you from our list, I wanted to check:

                    Are you still interested in M&A opportunities?

                    [ Yes - Show me deals ] - {yes_url}
                    [ Yes - But not right now ] - {pause_url}
                    [ No - Unsubscribe me ] - {unsubscribe_url}

                    If you're still interested, I have a special offer:

                    Free 7-day reactivation
                    • Full platform access
                    • No credit card required
                    • {new_deals_count} new deals since you left

                    Your choice.

                    Michael

                    P.S. {return_user_name} came back after 2 months and closed
                    a £{return_user_deal}M deal within 30 days.
                    """,
                    "cta": "Yes - Show Me Deals",
                    "metrics_goal": {"open_rate": 0.50, "click_rate": 0.25}
                }
            ]
        )

    @staticmethod
    def get_podcast_listener_sequence() -> EmailSequence:
        """Convert podcast listeners to platform users"""
        return EmailSequence(
            name="podcast_conversion",
            description="Convert podcast listeners to trial users",
            target_segment="podcast_listeners",
            expected_conversion=0.15,
            emails=[
                {
                    "day": 0,
                    "subject": "Thanks for listening to Episode #{episode_number}",
                    "preview": "Your exclusive listener resources inside",
                    "content": """
                    {first_name},

                    Thanks for listening to "{episode_title}"!

                    As promised in the episode, here are your resources:

                    📊 Deal Scoring Template: {template_url}
                    📚 Due Diligence Guide: {guide_url}
                    🎯 Valuation Calculator: {calculator_url}

                    Exclusive for podcast listeners:
                    • 30-day extended trial (usually 14 days)
                    • Access to episode guest {guest_name}'s masterclass
                    • Priority deal alerts in {listener_interest}

                    Claim your listener perks: {listener_trial_url}

                    Michael

                    P.S. {guest_name} is taking 3 advisory calls this month.
                    Trial members get priority booking.
                    """,
                    "cta": "Claim Listener Perks",
                    "metrics_goal": {"open_rate": 0.60, "click_rate": 0.35}
                },
                {
                    "day": 2,
                    "subject": "The deal {guest_name} mentioned is still available",
                    "preview": "£{deal_value}M opportunity in {industry}",
                    "content": """
                    {first_name},

                    Remember the deal {guest_name} discussed in the episode?

                    It's still available:
                    • Industry: {industry}
                    • Revenue: £{revenue}M
                    • EBITDA margin: {margin}%
                    • Growth rate: {growth}% YoY

                    {guest_name}'s assessment:
                    "{guest_quote}"

                    This matches what you mentioned interest in: {listener_interest}

                    View full details: {deal_specific_url}

                    Only visible to platform members.

                    Michael
                    """,
                    "cta": "View This Deal",
                    "metrics_goal": {"open_rate": 0.52, "click_rate": 0.30}
                },
                {
                    "day": 5,
                    "subject": "New episode: {next_episode_title}",
                    "preview": "Plus: {guest_name} answers your question",
                    "content": """
                    {first_name},

                    New episode just dropped!

                    "{next_episode_title}"
                    with {next_guest_name}

                    Key takeaways:
                    • {takeaway_1}
                    • {takeaway_2}
                    • {takeaway_3}

                    Listen now: {next_episode_url}

                    Also: {guest_name} answered your question about {topic}:
                    "{answer_preview}"

                    Full answer + 5 other listener questions: {qa_url}

                    Platform members get:
                    • Full episode transcripts
                    • Guest contact details
                    • Downloadable frameworks

                    Join the conversation: {community_url}

                    Michael
                    """,
                    "cta": "Listen to New Episode",
                    "metrics_goal": {"open_rate": 0.55, "click_rate": 0.28}
                }
            ]
        )


class EmailPerformanceAnalyzer:
    """Analyze and optimize email performance"""

    def __init__(self):
        self.benchmarks = {
            "open_rate": {"poor": 0.15, "average": 0.25, "good": 0.35, "excellent": 0.45},
            "click_rate": {"poor": 0.02, "average": 0.05, "good": 0.10, "excellent": 0.15},
            "conversion_rate": {"poor": 0.01, "average": 0.03, "good": 0.06, "excellent": 0.10}
        }

    def analyze_sequence_performance(
        self,
        sequence_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze email sequence performance"""

        analysis = {
            "overall_health": "",
            "recommendations": [],
            "top_performers": [],
            "needs_improvement": [],
            "predicted_revenue": 0
        }

        # Calculate overall metrics
        avg_open_rate = sequence_metrics.get("avg_open_rate", 0)
        avg_click_rate = sequence_metrics.get("avg_click_rate", 0)
        conversion_rate = sequence_metrics.get("conversion_rate", 0)

        # Determine health score
        health_score = 0
        if avg_open_rate >= self.benchmarks["open_rate"]["good"]:
            health_score += 1
        if avg_click_rate >= self.benchmarks["click_rate"]["good"]:
            health_score += 1
        if conversion_rate >= self.benchmarks["conversion_rate"]["good"]:
            health_score += 1

        health_labels = {0: "Poor", 1: "Average", 2: "Good", 3: "Excellent"}
        analysis["overall_health"] = health_labels.get(health_score, "Unknown")

        # Generate recommendations
        if avg_open_rate < self.benchmarks["open_rate"]["average"]:
            analysis["recommendations"].append({
                "issue": "Low open rates",
                "action": "Test subject lines with urgency, personalization, or curiosity gaps",
                "potential_impact": "+15% open rate"
            })

        if avg_click_rate < self.benchmarks["click_rate"]["average"]:
            analysis["recommendations"].append({
                "issue": "Low click rates",
                "action": "Improve CTA prominence and value proposition clarity",
                "potential_impact": "+8% click rate"
            })

        if conversion_rate < self.benchmarks["conversion_rate"]["average"]:
            analysis["recommendations"].append({
                "issue": "Low conversion rate",
                "action": "Add social proof, urgency, and risk reversal",
                "potential_impact": "+5% conversion rate"
            })

        # Identify top performers
        for email in sequence_metrics.get("emails", []):
            if email["open_rate"] >= self.benchmarks["open_rate"]["excellent"]:
                analysis["top_performers"].append({
                    "email": email["subject"],
                    "metric": "open_rate",
                    "value": email["open_rate"]
                })

        # Calculate predicted revenue
        subscribers = sequence_metrics.get("total_subscribers", 1000)
        avg_order_value = 2994  # Annual subscription
        predicted_conversions = subscribers * conversion_rate
        analysis["predicted_revenue"] = predicted_conversions * avg_order_value

        return analysis

    def generate_optimization_report(
        self,
        campaign_data: Dict[str, Any]
    ) -> str:
        """Generate detailed optimization report"""

        report = f"""
# Email Campaign Optimization Report
Generated: {datetime.utcnow().strftime('%Y-%m-%d')}

## Executive Summary
- Campaign: {campaign_data.get('name', 'Unknown')}
- Period: {campaign_data.get('period', 'Last 30 days')}
- Total Sent: {campaign_data.get('total_sent', 0):,}
- Revenue Generated: £{campaign_data.get('revenue', 0):,.2f}

## Performance Metrics
### Engagement
- Open Rate: {campaign_data.get('open_rate', 0):.1%} (Benchmark: {self.benchmarks['open_rate']['average']:.1%})
- Click Rate: {campaign_data.get('click_rate', 0):.1%} (Benchmark: {self.benchmarks['click_rate']['average']:.1%})
- Conversion Rate: {campaign_data.get('conversion_rate', 0):.1%} (Benchmark: {self.benchmarks['conversion_rate']['average']:.1%})

### Revenue
- Revenue per Email: £{campaign_data.get('revenue_per_email', 0):.2f}
- Customer Lifetime Value: £{campaign_data.get('ltv', 0):,.2f}
- ROI: {campaign_data.get('roi', 0):.1%}

## Top Performing Elements
### Subject Lines
{self._format_top_elements(campaign_data.get('top_subjects', []))}

### Send Times
{self._format_top_elements(campaign_data.get('top_send_times', []))}

### CTAs
{self._format_top_elements(campaign_data.get('top_ctas', []))}

## Recommendations
{self._format_recommendations(campaign_data)}

## Next Steps
1. Implement A/B tests for lowest performing emails
2. Adjust send times based on engagement data
3. Personalize content for high-value segments
4. Review and update automation triggers

## Projected Impact
Implementing these optimizations could result in:
- {campaign_data.get('projected_open_increase', 15)}% increase in open rates
- {campaign_data.get('projected_click_increase', 10)}% increase in click rates
- £{campaign_data.get('projected_revenue_increase', 50000):,} additional revenue
        """

        return report

    def _format_top_elements(self, elements: List[Dict]) -> str:
        """Format top performing elements"""
        if not elements:
            return "No data available"

        formatted = []
        for i, element in enumerate(elements[:5], 1):
            formatted.append(
                f"{i}. {element.get('name', 'Unknown')} "
                f"({element.get('performance', 0):.1%} "
                f"{element.get('metric', 'conversion')})"
            )

        return "\n".join(formatted)

    def _format_recommendations(self, campaign_data: Dict) -> str:
        """Format recommendations based on data"""
        recommendations = []

        if campaign_data.get('open_rate', 0) < self.benchmarks['open_rate']['average']:
            recommendations.append(
                "- **Improve Subject Lines**: Current open rate is below average. "
                "Test emotional triggers, numbers, and personalization."
            )

        if campaign_data.get('click_rate', 0) < self.benchmarks['click_rate']['average']:
            recommendations.append(
                "- **Enhance CTAs**: Click rate needs improvement. "
                "Make CTAs more prominent and action-oriented."
            )

        if campaign_data.get('unsubscribe_rate', 0) > 0.02:
            recommendations.append(
                "- **Reduce Frequency**: High unsubscribe rate detected. "
                "Consider reducing email frequency or improving segmentation."
            )

        if not recommendations:
            recommendations.append("- Performance is meeting benchmarks. Focus on scaling successful elements.")

        return "\n".join(recommendations)