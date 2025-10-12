"""
Beta Program Excellence Manager
Elite M&A professional recruitment, white-glove support, and referral network building
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update, func, and_, or_

from ..core.database import get_db
from ..models.user import User
from ..models.organization import Organization
from ..models.feedback import Feedback
from ..models.beta_program import BetaApplication, BetaUser, BetaMetrics

logger = logging.getLogger(__name__)


class BetaStatus(str, Enum):
    APPLIED = "applied"
    REVIEWING = "reviewing"
    ACCEPTED = "accepted"
    ACTIVE = "active"
    COMPLETED = "completed"
    DECLINED = "declined"


class FeedbackType(str, Enum):
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    UX_IMPROVEMENT = "ux_improvement"
    INTEGRATION_REQUEST = "integration_request"
    GENERAL_FEEDBACK = "general_feedback"
    SUCCESS_STORY = "success_story"


@dataclass
class BetaUserProfile:
    """Elite M&A professional profile for beta program"""
    user_id: str
    name: str
    email: str
    company: str
    title: str
    years_experience: int
    deal_volume_annual: float  # Annual deal volume in millions
    industry_focus: List[str]
    geographic_regions: List[str]
    firm_type: str  # investment_bank, private_equity, corporate_dev, advisory
    team_size: int
    current_tools: List[str]
    pain_points: List[str]
    success_metrics: List[str]
    referral_potential: int  # 1-10 scale
    status: BetaStatus
    joined_at: datetime
    last_activity: Optional[datetime] = None


@dataclass
class FeedbackItem:
    """Beta user feedback collection"""
    feedback_id: str
    user_id: str
    feedback_type: FeedbackType
    title: str
    description: str
    priority: str  # critical, high, medium, low
    category: str  # ui_ux, functionality, performance, integration
    feature_area: str  # deals, analytics, integrations, etc.
    attachments: List[str]
    votes: int
    status: str  # new, reviewing, in_progress, completed, declined
    created_at: datetime
    resolved_at: Optional[datetime] = None


@dataclass
class BetaSuccessStory:
    """Beta user success story for marketing"""
    story_id: str
    user_id: str
    company: str
    title: str
    summary: str
    metrics: Dict[str, Any]  # time_saved, deals_closed, efficiency_gain
    quote: str
    permission_to_use: bool
    created_at: datetime


class FeedbackCollector:
    """Comprehensive feedback collection and analysis system"""

    def __init__(self):
        self.feedback_queue: asyncio.Queue = asyncio.Queue()
        self.analysis_engine = FeedbackAnalysisEngine()

    async def collect_feedback(
        self,
        user_id: str,
        feedback_type: FeedbackType,
        title: str,
        description: str,
        priority: str = "medium",
        category: str = "functionality",
        feature_area: str = "general",
        attachments: List[str] = None
    ) -> str:
        """Collect feedback from beta users"""
        try:
            feedback_id = f"feedback_{datetime.now().timestamp()}"

            feedback = FeedbackItem(
                feedback_id=feedback_id,
                user_id=user_id,
                feedback_type=feedback_type,
                title=title,
                description=description,
                priority=priority,
                category=category,
                feature_area=feature_area,
                attachments=attachments or [],
                votes=0,
                status="new",
                created_at=datetime.now()
            )

            # Store in database
            await self._store_feedback(feedback)

            # Queue for analysis
            await self.feedback_queue.put(feedback)

            # Notify product team for critical feedback
            if priority == "critical":
                await self._notify_critical_feedback(feedback)

            logger.info(f"Collected feedback: {feedback_id} from user {user_id}")
            return feedback_id

        except Exception as e:
            logger.error(f"Failed to collect feedback: {str(e)}")
            raise

    async def get_feedback_trends(
        self,
        time_period: int = 30
    ) -> Dict[str, Any]:
        """Analyze feedback trends and patterns"""
        try:
            async with get_db() as db:
                cutoff_date = datetime.now() - timedelta(days=time_period)

                # Get feedback summary
                feedback_query = select(Feedback).where(
                    Feedback.created_at >= cutoff_date,
                    Feedback.source == "beta_program"
                )
                result = await db.execute(feedback_query)
                feedback_items = result.scalars().all()

                # Analyze trends
                trends = {
                    "total_feedback": len(feedback_items),
                    "by_type": {},
                    "by_category": {},
                    "by_priority": {},
                    "by_feature_area": {},
                    "common_themes": [],
                    "top_requests": [],
                    "critical_issues": 0
                }

                for feedback in feedback_items:
                    # Count by type
                    feedback_type = feedback.feedback_type
                    trends["by_type"][feedback_type] = trends["by_type"].get(feedback_type, 0) + 1

                    # Count by category
                    category = feedback.category
                    trends["by_category"][category] = trends["by_category"].get(category, 0) + 1

                    # Count by priority
                    priority = feedback.priority
                    trends["by_priority"][priority] = trends["by_priority"].get(priority, 0) + 1

                    # Count by feature area
                    feature_area = feedback.feature_area
                    trends["by_feature_area"][feature_area] = trends["by_feature_area"].get(feature_area, 0) + 1

                    # Count critical issues
                    if priority == "critical":
                        trends["critical_issues"] += 1

                # Generate insights
                trends["insights"] = await self._generate_feedback_insights(trends)

                return trends

        except Exception as e:
            logger.error(f"Failed to analyze feedback trends: {str(e)}")
            return {}

    async def _store_feedback(self, feedback: FeedbackItem):
        """Store feedback in database"""
        async with get_db() as db:
            feedback_record = Feedback(
                feedback_id=feedback.feedback_id,
                user_id=feedback.user_id,
                feedback_type=feedback.feedback_type.value,
                title=feedback.title,
                description=feedback.description,
                priority=feedback.priority,
                category=feedback.category,
                feature_area=feedback.feature_area,
                attachments=feedback.attachments,
                votes=feedback.votes,
                status=feedback.status,
                source="beta_program",
                created_at=feedback.created_at
            )

            db.add(feedback_record)
            await db.commit()

    async def _notify_critical_feedback(self, feedback: FeedbackItem):
        """Notify product team of critical feedback"""
        # Implementation would send notifications to product team
        logger.critical(f"Critical feedback received: {feedback.title}")

    async def _generate_feedback_insights(self, trends: Dict[str, Any]) -> List[str]:
        """Generate actionable insights from feedback trends"""
        insights = []

        # Most requested features
        if trends["by_type"].get("feature_request", 0) > 0:
            insights.append("Feature requests are driving beta engagement")

        # UX issues
        if trends["by_category"].get("ui_ux", 0) > trends["total_feedback"] * 0.3:
            insights.append("UX improvements needed - 30%+ of feedback is UI/UX related")

        # Critical issues
        if trends["critical_issues"] > 0:
            insights.append(f"{trends['critical_issues']} critical issues need immediate attention")

        # Integration requests
        if trends["by_type"].get("integration_request", 0) > 0:
            insights.append("Integration requests indicate strong market demand")

        return insights


class FeedbackAnalysisEngine:
    """AI-powered feedback analysis and prioritization"""

    async def analyze_feedback_sentiment(self, feedback: FeedbackItem) -> Dict[str, Any]:
        """Analyze sentiment and extract insights from feedback"""
        # Simplified sentiment analysis - would use AI/NLP in production
        positive_keywords = ["great", "excellent", "love", "amazing", "helpful", "efficient"]
        negative_keywords = ["slow", "confusing", "broken", "difficult", "frustrating", "missing"]

        text = f"{feedback.title} {feedback.description}".lower()

        positive_score = sum(1 for word in positive_keywords if word in text)
        negative_score = sum(1 for word in negative_keywords if word in text)

        sentiment = "neutral"
        if positive_score > negative_score:
            sentiment = "positive"
        elif negative_score > positive_score:
            sentiment = "negative"

        return {
            "sentiment": sentiment,
            "positive_score": positive_score,
            "negative_score": negative_score,
            "confidence": min((abs(positive_score - negative_score) + 1) / 5, 1.0)
        }

    async def extract_feature_requests(self, feedback_items: List[FeedbackItem]) -> List[Dict[str, Any]]:
        """Extract and prioritize feature requests from feedback"""
        feature_requests = []

        for feedback in feedback_items:
            if feedback.feedback_type == FeedbackType.FEATURE_REQUEST:
                # Extract key themes and prioritize
                feature_request = {
                    "feedback_id": feedback.feedback_id,
                    "title": feedback.title,
                    "description": feedback.description,
                    "votes": feedback.votes,
                    "priority_score": self._calculate_priority_score(feedback),
                    "implementation_effort": await self._estimate_effort(feedback),
                    "business_impact": await self._estimate_impact(feedback)
                }
                feature_requests.append(feature_request)

        # Sort by priority score
        feature_requests.sort(key=lambda x: x["priority_score"], reverse=True)
        return feature_requests

    def _calculate_priority_score(self, feedback: FeedbackItem) -> float:
        """Calculate priority score for feedback item"""
        priority_weights = {
            "critical": 10,
            "high": 7,
            "medium": 5,
            "low": 2
        }

        base_score = priority_weights.get(feedback.priority, 5)
        vote_multiplier = 1 + (feedback.votes * 0.1)

        return base_score * vote_multiplier

    async def _estimate_effort(self, feedback: FeedbackItem) -> str:
        """Estimate implementation effort (simplified)"""
        # Would use AI/ML models in production
        complex_keywords = ["integration", "api", "workflow", "automation", "ai"]
        simple_keywords = ["button", "color", "text", "display", "format"]

        text = f"{feedback.title} {feedback.description}".lower()

        if any(keyword in text for keyword in complex_keywords):
            return "high"
        elif any(keyword in text for keyword in simple_keywords):
            return "low"
        else:
            return "medium"

    async def _estimate_impact(self, feedback: FeedbackItem) -> str:
        """Estimate business impact (simplified)"""
        # Would use AI/ML models in production
        high_impact_keywords = ["time saving", "efficiency", "automation", "revenue", "deals"]
        text = f"{feedback.title} {feedback.description}".lower()

        if any(keyword in text for keyword in high_impact_keywords):
            return "high"
        else:
            return "medium"


class BetaProgramManager:
    """Elite M&A professional beta program management"""

    def __init__(self):
        self.feedback_collector = FeedbackCollector()
        self.target_beta_users = 50
        self.min_experience_years = 5
        self.min_deal_volume = 50  # Million USD annually

    async def evaluate_beta_application(
        self,
        application_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate beta program application from M&A professional"""
        try:
            # Extract application details
            years_experience = application_data.get("years_experience", 0)
            deal_volume = application_data.get("deal_volume_annual", 0)
            firm_type = application_data.get("firm_type", "")
            title = application_data.get("title", "")
            company = application_data.get("company", "")

            # Calculate eligibility score
            score = 0

            # Experience scoring (0-30 points)
            if years_experience >= 15:
                score += 30
            elif years_experience >= 10:
                score += 25
            elif years_experience >= 5:
                score += 20
            else:
                score += years_experience * 3

            # Deal volume scoring (0-25 points)
            if deal_volume >= 500:
                score += 25
            elif deal_volume >= 250:
                score += 20
            elif deal_volume >= 100:
                score += 15
            elif deal_volume >= 50:
                score += 10
            else:
                score += deal_volume / 10

            # Firm type scoring (0-20 points)
            firm_scores = {
                "investment_bank": 20,
                "private_equity": 18,
                "corporate_dev": 15,
                "advisory": 12,
                "other": 5
            }
            score += firm_scores.get(firm_type, 5)

            # Title/seniority scoring (0-15 points)
            if any(title_keyword in title.lower() for title_keyword in ["ceo", "cfo", "president", "partner"]):
                score += 15
            elif any(title_keyword in title.lower() for title_keyword in ["vp", "director", "head"]):
                score += 12
            elif any(title_keyword in title.lower() for title_keyword in ["senior", "lead", "principal"]):
                score += 8
            else:
                score += 5

            # Company reputation scoring (0-10 points)
            elite_firms = [
                "goldman sachs", "morgan stanley", "jp morgan", "blackstone", "kkr",
                "carlyle", "apollo", "mckinsey", "bain", "bcg"
            ]
            if any(firm in company.lower() for firm in elite_firms):
                score += 10
            else:
                score += 5

            # Determine acceptance
            accepted = score >= 70  # Minimum 70/100 points for acceptance

            evaluation = {
                "score": score,
                "accepted": accepted,
                "criteria_met": {
                    "experience": years_experience >= self.min_experience_years,
                    "deal_volume": deal_volume >= self.min_deal_volume,
                    "elite_profile": score >= 70
                },
                "feedback": self._generate_evaluation_feedback(score, application_data)
            }

            return evaluation

        except Exception as e:
            logger.error(f"Failed to evaluate beta application: {str(e)}")
            return {"score": 0, "accepted": False, "error": str(e)}

    async def onboard_beta_user(
        self,
        user_id: str,
        application_data: Dict[str, Any]
    ) -> BetaUserProfile:
        """Onboard accepted beta user with white-glove experience"""
        try:
            # Create beta user profile
            beta_user = BetaUserProfile(
                user_id=user_id,
                name=application_data["name"],
                email=application_data["email"],
                company=application_data["company"],
                title=application_data["title"],
                years_experience=application_data["years_experience"],
                deal_volume_annual=application_data["deal_volume_annual"],
                industry_focus=application_data.get("industry_focus", []),
                geographic_regions=application_data.get("geographic_regions", []),
                firm_type=application_data["firm_type"],
                team_size=application_data.get("team_size", 1),
                current_tools=application_data.get("current_tools", []),
                pain_points=application_data.get("pain_points", []),
                success_metrics=application_data.get("success_metrics", []),
                referral_potential=application_data.get("referral_potential", 5),
                status=BetaStatus.ACTIVE,
                joined_at=datetime.now()
            )

            # Store in database
            await self._store_beta_user(beta_user)

            # Schedule onboarding activities
            await self._schedule_onboarding(beta_user)

            # Assign customer success manager
            await self._assign_success_manager(beta_user)

            # Customize platform for user
            await self._customize_user_experience(beta_user)

            logger.info(f"Successfully onboarded beta user: {user_id}")
            return beta_user

        except Exception as e:
            logger.error(f"Failed to onboard beta user: {str(e)}")
            raise

    async def collect_success_story(
        self,
        user_id: str,
        story_data: Dict[str, Any]
    ) -> BetaSuccessStory:
        """Collect success story from beta user"""
        try:
            story_id = f"story_{datetime.now().timestamp()}"

            success_story = BetaSuccessStory(
                story_id=story_id,
                user_id=user_id,
                company=story_data["company"],
                title=story_data["title"],
                summary=story_data["summary"],
                metrics=story_data.get("metrics", {}),
                quote=story_data["quote"],
                permission_to_use=story_data.get("permission_to_use", False),
                created_at=datetime.now()
            )

            # Store success story
            await self._store_success_story(success_story)

            # Generate marketing materials if permission granted
            if success_story.permission_to_use:
                await self._generate_marketing_materials(success_story)

            logger.info(f"Collected success story: {story_id}")
            return success_story

        except Exception as e:
            logger.error(f"Failed to collect success story: {str(e)}")
            raise

    async def generate_referral_network(self) -> Dict[str, Any]:
        """Generate referral opportunities from beta users"""
        try:
            async with get_db() as db:
                # Get active beta users with high referral potential
                beta_users_query = select(BetaUser).where(
                    BetaUser.status == BetaStatus.ACTIVE.value,
                    BetaUser.referral_potential >= 7
                )
                result = await db.execute(beta_users_query)
                high_potential_users = result.scalars().all()

                referral_network = {
                    "total_beta_users": len(high_potential_users),
                    "estimated_referrals": 0,
                    "target_segments": {},
                    "referral_opportunities": []
                }

                for user in high_potential_users:
                    # Estimate referral potential
                    estimated_referrals = user.referral_potential * user.team_size * 0.3

                    referral_network["estimated_referrals"] += estimated_referrals

                    # Segment by firm type
                    firm_type = user.firm_type
                    if firm_type not in referral_network["target_segments"]:
                        referral_network["target_segments"][firm_type] = 0
                    referral_network["target_segments"][firm_type] += estimated_referrals

                    # Create referral opportunity
                    opportunity = {
                        "user_id": user.user_id,
                        "name": user.name,
                        "company": user.company,
                        "firm_type": user.firm_type,
                        "estimated_referrals": estimated_referrals,
                        "networks": user.geographic_regions,
                        "industries": user.industry_focus
                    }
                    referral_network["referral_opportunities"].append(opportunity)

                return referral_network

        except Exception as e:
            logger.error(f"Failed to generate referral network: {str(e)}")
            return {}

    async def get_beta_program_metrics(self) -> Dict[str, Any]:
        """Get comprehensive beta program metrics"""
        try:
            async with get_db() as db:
                # Get beta program statistics
                total_applications = await self._count_applications(db)
                active_users = await self._count_active_users(db)
                completion_rate = await self._calculate_completion_rate(db)
                feedback_volume = await self._count_feedback(db)
                success_stories = await self._count_success_stories(db)

                metrics = {
                    "program_health": {
                        "total_applications": total_applications,
                        "acceptance_rate": (active_users / total_applications * 100) if total_applications > 0 else 0,
                        "active_users": active_users,
                        "target_users": self.target_beta_users,
                        "completion_rate": completion_rate
                    },
                    "engagement": {
                        "feedback_items": feedback_volume,
                        "avg_feedback_per_user": feedback_volume / active_users if active_users > 0 else 0,
                        "success_stories": success_stories,
                        "success_story_rate": success_stories / active_users * 100 if active_users > 0 else 0
                    },
                    "quality_indicators": {
                        "avg_experience_years": await self._avg_experience(db),
                        "avg_deal_volume": await self._avg_deal_volume(db),
                        "firm_distribution": await self._firm_distribution(db)
                    }
                }

                return metrics

        except Exception as e:
            logger.error(f"Failed to get beta program metrics: {str(e)}")
            return {}

    # Helper methods

    def _generate_evaluation_feedback(
        self,
        score: float,
        application_data: Dict[str, Any]
    ) -> str:
        """Generate personalized feedback for beta application"""
        if score >= 90:
            return "Exceptional candidate - elite M&A professional with outstanding credentials"
        elif score >= 80:
            return "Strong candidate - experienced professional with significant deal experience"
        elif score >= 70:
            return "Qualified candidate - meets beta program criteria"
        elif score >= 60:
            return "Borderline candidate - consider waitlist for future openings"
        else:
            return "Does not meet current beta program criteria - consider reapplying with additional experience"

    async def _store_beta_user(self, beta_user: BetaUserProfile):
        """Store beta user profile in database"""
        async with get_db() as db:
            beta_record = BetaUser(
                user_id=beta_user.user_id,
                name=beta_user.name,
                email=beta_user.email,
                company=beta_user.company,
                title=beta_user.title,
                years_experience=beta_user.years_experience,
                deal_volume_annual=beta_user.deal_volume_annual,
                industry_focus=beta_user.industry_focus,
                geographic_regions=beta_user.geographic_regions,
                firm_type=beta_user.firm_type,
                team_size=beta_user.team_size,
                current_tools=beta_user.current_tools,
                pain_points=beta_user.pain_points,
                success_metrics=beta_user.success_metrics,
                referral_potential=beta_user.referral_potential,
                status=beta_user.status.value,
                joined_at=beta_user.joined_at
            )

            db.add(beta_record)
            await db.commit()

    async def _schedule_onboarding(self, beta_user: BetaUserProfile):
        """Schedule personalized onboarding activities"""
        # Implementation would schedule onboarding calls, demos, training
        logger.info(f"Scheduled onboarding for {beta_user.name}")

    async def _assign_success_manager(self, beta_user: BetaUserProfile):
        """Assign dedicated customer success manager"""
        # Implementation would assign CSM based on user profile
        logger.info(f"Assigned success manager for {beta_user.name}")

    async def _customize_user_experience(self, beta_user: BetaUserProfile):
        """Customize platform experience for beta user"""
        # Implementation would customize dashboard, features, integrations
        logger.info(f"Customized experience for {beta_user.name}")

    async def _store_success_story(self, story: BetaSuccessStory):
        """Store success story in database"""
        # Implementation would store in database
        logger.info(f"Stored success story: {story.story_id}")

    async def _generate_marketing_materials(self, story: BetaSuccessStory):
        """Generate marketing materials from success story"""
        # Implementation would create case studies, testimonials, etc.
        logger.info(f"Generated marketing materials for story: {story.story_id}")

    async def _count_applications(self, db: AsyncSession) -> int:
        """Count total beta applications"""
        result = await db.execute(select(func.count(BetaApplication.id)))
        return result.scalar() or 0

    async def _count_active_users(self, db: AsyncSession) -> int:
        """Count active beta users"""
        result = await db.execute(
            select(func.count(BetaUser.user_id)).where(
                BetaUser.status == BetaStatus.ACTIVE.value
            )
        )
        return result.scalar() or 0

    async def _calculate_completion_rate(self, db: AsyncSession) -> float:
        """Calculate beta program completion rate"""
        total_result = await db.execute(select(func.count(BetaUser.user_id)))
        total = total_result.scalar() or 0

        completed_result = await db.execute(
            select(func.count(BetaUser.user_id)).where(
                BetaUser.status == BetaStatus.COMPLETED.value
            )
        )
        completed = completed_result.scalar() or 0

        return (completed / total * 100) if total > 0 else 0

    async def _count_feedback(self, db: AsyncSession) -> int:
        """Count total feedback items"""
        result = await db.execute(
            select(func.count(Feedback.id)).where(
                Feedback.source == "beta_program"
            )
        )
        return result.scalar() or 0

    async def _count_success_stories(self, db: AsyncSession) -> int:
        """Count success stories"""
        # Implementation would count success stories
        return 0

    async def _avg_experience(self, db: AsyncSession) -> float:
        """Calculate average experience years"""
        result = await db.execute(
            select(func.avg(BetaUser.years_experience)).where(
                BetaUser.status == BetaStatus.ACTIVE.value
            )
        )
        return result.scalar() or 0

    async def _avg_deal_volume(self, db: AsyncSession) -> float:
        """Calculate average deal volume"""
        result = await db.execute(
            select(func.avg(BetaUser.deal_volume_annual)).where(
                BetaUser.status == BetaStatus.ACTIVE.value
            )
        )
        return result.scalar() or 0

    async def _firm_distribution(self, db: AsyncSession) -> Dict[str, int]:
        """Get firm type distribution"""
        result = await db.execute(
            select(BetaUser.firm_type, func.count(BetaUser.user_id))
            .where(BetaUser.status == BetaStatus.ACTIVE.value)
            .group_by(BetaUser.firm_type)
        )

        distribution = {}
        for firm_type, count in result.all():
            distribution[firm_type] = count

        return distribution


# Service factory function
async def get_beta_program_manager() -> BetaProgramManager:
    """Get beta program manager instance"""
    return BetaProgramManager()