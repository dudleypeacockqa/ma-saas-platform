"""
Enhanced Stripe Payment Integration Service
Advanced subscription and payment processing with promotional codes and business intelligence
"""

import stripe
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.config import settings
from app.models.subscription_management import (
    Subscription, SubscriptionPlan, Payment, PaymentMethod, 
    Invoice, PromotionalCode, PromoCodeUsage, SubscriptionStatus,
    PaymentStatus, BillingCycle, DiscountType, CustomerHealthScore,
    SubscriptionEvent, BillingAlert
)
from app.models.organization import Organization
from app.models.user import User

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class EnhancedStripeService:
    """Enhanced Stripe integration with promotional codes and business intelligence"""
    
    def __init__(self):
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        
        # M&A SaaS Platform pricing structure
        self.pricing_plans = {
            "starter": {
                "monthly": 99.00,
                "quarterly": 267.30,  # 10% discount
                "annual": 1009.20     # 15% discount
            },
            "professional": {
                "monthly": 299.00,
                "quarterly": 807.30,  # 10% discount
                "annual": 3049.20     # 15% discount
            },
            "enterprise": {
                "monthly": 999.00,
                "quarterly": 2697.30, # 10% discount
                "annual": 10192.20    # 15% discount
            }
        }
    
    # ============================================================================
    # PROMOTIONAL CODE MANAGEMENT
    # ============================================================================
    
    async def create_promotional_campaign(
        self, 
        db: Session,
        campaign_name: str,
        discount_type: DiscountType,
        discount_value: float,
        max_uses: Optional[int] = None,
        expiry_date: Optional[datetime] = None,
        applicable_plans: Optional[List[str]] = None,
        description: Optional[str] = None,
        created_by: str = None
    ) -> Dict[str, Any]:
        """Create promotional campaign with multiple codes"""
        try:
            # Generate campaign codes
            campaign_codes = []
            base_code = campaign_name.upper().replace(" ", "")
            
            # Create main campaign code
            main_code = f"{base_code}2025"
            promo_code = await self._create_single_promo_code(
                db, main_code, discount_type, discount_value, 
                max_uses, expiry_date, applicable_plans, description, created_by
            )
            campaign_codes.append(promo_code)
            
            # Create variant codes for different channels
            variants = ["WEB", "EMAIL", "SOCIAL", "PARTNER"]
            for variant in variants:
                variant_code = f"{base_code}{variant}"
                variant_promo = await self._create_single_promo_code(
                    db, variant_code, discount_type, discount_value,
                    max_uses // 4 if max_uses else None, expiry_date, 
                    applicable_plans, f"{description} - {variant} Channel", created_by
                )
                campaign_codes.append(variant_promo)
            
            return {
                "campaign_name": campaign_name,
                "codes_created": len(campaign_codes),
                "codes": campaign_codes,
                "total_potential_uses": max_uses * len(campaign_codes) if max_uses else "unlimited"
            }
            
        except Exception as e:
            logger.error(f"Failed to create promotional campaign: {e}")
            db.rollback()
            raise
    
    async def _create_single_promo_code(
        self,
        db: Session,
        code: str,
        discount_type: DiscountType,
        discount_value: float,
        max_uses: Optional[int],
        expiry_date: Optional[datetime],
        applicable_plans: Optional[List[str]],
        description: Optional[str],
        created_by: Optional[str]
    ) -> PromotionalCode:
        """Create individual promotional code"""
        # Check if code already exists
        existing = db.query(PromotionalCode).filter(PromotionalCode.code == code).first()
        if existing:
            raise ValueError(f"Promotional code {code} already exists")
        
        # Create Stripe coupon
        stripe_coupon = await self._create_stripe_coupon(code, discount_type, discount_value, expiry_date)
        
        # Create local promotional code
        promo_code = PromotionalCode(
            code=code,
            discount_type=discount_type,
            discount_value=discount_value,
            max_uses=max_uses,
            expiry_date=expiry_date,
            applicable_plans=applicable_plans,
            description=description,
            stripe_coupon_id=stripe_coupon.id,
            created_by=created_by
        )
        
        db.add(promo_code)
        db.commit()
        db.refresh(promo_code)
        
        return promo_code
    
    async def _create_stripe_coupon(
        self,
        code: str,
        discount_type: DiscountType,
        discount_value: float,
        expiry_date: Optional[datetime]
    ) -> stripe.Coupon:
        """Create Stripe coupon"""
        coupon_params = {
            "id": f"promo_{code.lower()}",
            "name": f"Promotional Code: {code}",
            "metadata": {"source": "ma_saas_platform"}
        }
        
        if discount_type == DiscountType.PERCENTAGE:
            coupon_params["percent_off"] = discount_value
        else:
            coupon_params["amount_off"] = int(discount_value * 100)  # Convert to pence
            coupon_params["currency"] = "gbp"
        
        if expiry_date:
            coupon_params["redeem_by"] = int(expiry_date.timestamp())
        
        return stripe.Coupon.create(**coupon_params)
    
    # ============================================================================
    # SEASONAL PROMOTIONAL CAMPAIGNS
    # ============================================================================
    
    async def create_seasonal_campaigns(self, db: Session, created_by: str) -> Dict[str, Any]:
        """Create seasonal promotional campaigns for the year"""
        campaigns = []
        
        # New Year Campaign - 30% off first 3 months
        new_year = await self.create_promotional_campaign(
            db, "New Year Fresh Start", DiscountType.PERCENTAGE, 30.0,
            max_uses=500, expiry_date=datetime(2025, 2, 28),
            description="New Year 30% off first 3 months", created_by=created_by
        )
        campaigns.append(new_year)
        
        # Q1 Business Planning - 25% off annual plans
        q1_planning = await self.create_promotional_campaign(
            db, "Q1 Business Planning", DiscountType.PERCENTAGE, 25.0,
            max_uses=200, expiry_date=datetime(2025, 3, 31),
            applicable_plans=["annual"], 
            description="Q1 Business Planning - 25% off annual subscriptions", created_by=created_by
        )
        campaigns.append(q1_planning)
        
        # Summer M&A Season - £200 off Enterprise
        summer_ma = await self.create_promotional_campaign(
            db, "Summer MA Season", DiscountType.FIXED_AMOUNT, 200.0,
            max_uses=100, expiry_date=datetime(2025, 8, 31),
            applicable_plans=["enterprise"],
            description="Summer M&A Season - £200 off Enterprise plans", created_by=created_by
        )
        campaigns.append(summer_ma)
        
        # Black Friday - 40% off everything
        black_friday = await self.create_promotional_campaign(
            db, "Black Friday Special", DiscountType.PERCENTAGE, 40.0,
            max_uses=1000, expiry_date=datetime(2025, 11, 30),
            description="Black Friday Special - 40% off all plans", created_by=created_by
        )
        campaigns.append(black_friday)
        
        return {
            "campaigns_created": len(campaigns),
            "campaigns": campaigns,
            "total_codes": sum(c["codes_created"] for c in campaigns)
        }
    
    # ============================================================================
    # ADVANCED SUBSCRIPTION ANALYTICS
    # ============================================================================
    
    async def calculate_subscription_metrics(self, db: Session) -> Dict[str, Any]:
        """Calculate comprehensive subscription metrics"""
        try:
            # Basic counts
            total_subs = db.query(Subscription).count()
            active_subs = db.query(Subscription).filter(
                Subscription.status == SubscriptionStatus.ACTIVE
            ).count()
            trial_subs = db.query(Subscription).filter(
                Subscription.status == SubscriptionStatus.TRIAL
            ).count()
            
            # Revenue metrics
            mrr = db.query(Subscription).filter(
                Subscription.status == SubscriptionStatus.ACTIVE
            ).with_entities(
                db.func.sum(Subscription.monthly_amount)
            ).scalar() or 0
            
            arr = mrr * 12
            
            # Churn analysis
            current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            previous_month = (current_month - timedelta(days=1)).replace(day=1)
            
            churned_this_month = db.query(Subscription).filter(
                and_(
                    Subscription.cancelled_at >= current_month,
                    Subscription.cancelled_at < datetime.utcnow()
                )
            ).count()
            
            active_start_month = db.query(Subscription).filter(
                Subscription.created_at < current_month,
                or_(
                    Subscription.cancelled_at.is_(None),
                    Subscription.cancelled_at >= current_month
                )
            ).count()
            
            churn_rate = (churned_this_month / active_start_month * 100) if active_start_month > 0 else 0
            
            # Plan distribution
            plan_distribution = {}
            plans = db.query(SubscriptionPlan).all()
            for plan in plans:
                plan_count = db.query(Subscription).filter(
                    Subscription.plan_id == plan.id,
                    Subscription.status == SubscriptionStatus.ACTIVE
                ).count()
                plan_distribution[plan.name] = plan_count
            
            # Trial conversion rate
            converted_trials = db.query(Subscription).filter(
                and_(
                    Subscription.status == SubscriptionStatus.ACTIVE,
                    Subscription.trial_end_date.isnot(None)
                )
            ).count()
            
            total_trials = trial_subs + converted_trials
            trial_conversion_rate = (converted_trials / total_trials * 100) if total_trials > 0 else 0
            
            return {
                "total_subscriptions": total_subs,
                "active_subscriptions": active_subs,
                "trial_subscriptions": trial_subs,
                "mrr": float(mrr),
                "arr": float(arr),
                "churn_rate": round(churn_rate, 2),
                "trial_conversion_rate": round(trial_conversion_rate, 2),
                "plan_distribution": plan_distribution,
                "average_revenue_per_user": float(mrr / active_subs) if active_subs > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate subscription metrics: {e}")
            raise
    
    # ============================================================================
    # CUSTOMER SUCCESS & HEALTH SCORING
    # ============================================================================
    
    async def calculate_customer_health_scores(self, db: Session) -> List[Dict[str, Any]]:
        """Calculate health scores for all customers"""
        try:
            organizations = db.query(Organization).all()
            health_scores = []
            
            for org in organizations:
                score = await self._calculate_individual_health_score(db, org)
                health_scores.append(score)
            
            return health_scores
            
        except Exception as e:
            logger.error(f"Failed to calculate customer health scores: {e}")
            raise
    
    async def _calculate_individual_health_score(self, db: Session, organization: Organization) -> Dict[str, Any]:
        """Calculate health score for individual customer"""
        try:
            # Get subscription
            subscription = db.query(Subscription).filter(
                Subscription.organization_id == organization.id
            ).first()
            
            if not subscription:
                return {
                    "organization_id": str(organization.id),
                    "organization_name": organization.name,
                    "health_score": 0,
                    "risk_level": "high",
                    "reason": "No active subscription"
                }
            
            # Calculate component scores (0-100)
            usage_score = await self._calculate_usage_score(db, organization)
            engagement_score = await self._calculate_engagement_score(db, organization)
            payment_score = await self._calculate_payment_score(db, subscription)
            support_score = await self._calculate_support_score(db, organization)
            
            # Overall weighted score
            overall_score = (
                usage_score * 0.3 +
                engagement_score * 0.25 +
                payment_score * 0.25 +
                support_score * 0.2
            )
            
            # Determine risk level
            if overall_score >= 80:
                risk_level = "low"
                expansion_opportunity = "high"
            elif overall_score >= 60:
                risk_level = "medium"
                expansion_opportunity = "medium"
            else:
                risk_level = "high"
                expansion_opportunity = "low"
            
            # Store health score
            health_record = CustomerHealthScore(
                organization_id=organization.id,
                overall_score=int(overall_score),
                usage_score=int(usage_score),
                engagement_score=int(engagement_score),
                support_score=int(support_score),
                churn_risk=risk_level,
                expansion_opportunity=expansion_opportunity
            )
            
            db.add(health_record)
            db.commit()
            
            return {
                "organization_id": str(organization.id),
                "organization_name": organization.name,
                "health_score": int(overall_score),
                "usage_score": int(usage_score),
                "engagement_score": int(engagement_score),
                "payment_score": int(payment_score),
                "support_score": int(support_score),
                "risk_level": risk_level,
                "expansion_opportunity": expansion_opportunity
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate health score for {organization.name}: {e}")
            return {
                "organization_id": str(organization.id),
                "organization_name": organization.name,
                "health_score": 0,
                "risk_level": "unknown",
                "reason": str(e)
            }
    
    async def _calculate_usage_score(self, db: Session, organization: Organization) -> float:
        """Calculate usage score based on platform activity"""
        # This would integrate with actual usage tracking
        # For now, return a placeholder score
        return 75.0
    
    async def _calculate_engagement_score(self, db: Session, organization: Organization) -> float:
        """Calculate engagement score based on user activity"""
        # This would track logins, feature usage, content consumption
        # For now, return a placeholder score
        return 68.0
    
    async def _calculate_payment_score(self, db: Session, subscription: Subscription) -> float:
        """Calculate payment score based on payment history"""
        try:
            # Check recent payment failures
            recent_failures = db.query(Payment).filter(
                Payment.subscription_id == subscription.id,
                Payment.status == PaymentStatus.FAILED,
                Payment.created_at >= datetime.utcnow() - timedelta(days=90)
            ).count()
            
            if recent_failures == 0:
                return 100.0
            elif recent_failures <= 2:
                return 70.0
            else:
                return 30.0
                
        except Exception:
            return 50.0
    
    async def _calculate_support_score(self, db: Session, organization: Organization) -> float:
        """Calculate support score based on ticket history"""
        # This would integrate with support ticket system
        # For now, return a placeholder score
        return 85.0
    
    # ============================================================================
    # REVENUE OPTIMIZATION
    # ============================================================================
    
    async def identify_expansion_opportunities(self, db: Session) -> List[Dict[str, Any]]:
        """Identify customers ready for plan upgrades"""
        try:
            opportunities = []
            
            # Find customers on lower plans with high usage
            starter_customers = db.query(Subscription).join(SubscriptionPlan).filter(
                SubscriptionPlan.name == "Starter",
                Subscription.status == SubscriptionStatus.ACTIVE
            ).all()
            
            for subscription in starter_customers:
                health_score = db.query(CustomerHealthScore).filter(
                    CustomerHealthScore.organization_id == subscription.organization_id
                ).order_by(CustomerHealthScore.created_at.desc()).first()
                
                if health_score and health_score.expansion_opportunity == "high":
                    opportunities.append({
                        "organization_id": str(subscription.organization_id),
                        "current_plan": "Starter",
                        "recommended_plan": "Professional",
                        "potential_additional_mrr": 200.0,  # £299 - £99
                        "health_score": health_score.overall_score,
                        "reason": "High usage and engagement on starter plan"
                    })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Failed to identify expansion opportunities: {e}")
            raise
    
    async def create_win_back_campaign(self, db: Session, created_by: str) -> Dict[str, Any]:
        """Create win-back campaign for churned customers"""
        try:
            # Find recently churned customers
            churned_customers = db.query(Subscription).filter(
                Subscription.status == SubscriptionStatus.CANCELLED,
                Subscription.cancelled_at >= datetime.utcnow() - timedelta(days=90)
            ).all()
            
            # Create special win-back promotional code
            win_back_promo = await self._create_single_promo_code(
                db, "COMEBACK50", DiscountType.PERCENTAGE, 50.0,
                max_uses=len(churned_customers), 
                expiry_date=datetime.utcnow() + timedelta(days=30),
                description="Win-back campaign - 50% off for 3 months",
                created_by=created_by
            )
            
            return {
                "campaign_name": "Win-Back Campaign",
                "target_customers": len(churned_customers),
                "promotional_code": win_back_promo.code,
                "discount": "50% off for 3 months",
                "expires": win_back_promo.expiry_date
            }
            
        except Exception as e:
            logger.error(f"Failed to create win-back campaign: {e}")
            db.rollback()
            raise
    
    # ============================================================================
    # BILLING ALERTS & NOTIFICATIONS
    # ============================================================================
    
    async def create_billing_alerts(self, db: Session) -> List[Dict[str, Any]]:
        """Create billing alerts for various scenarios"""
        try:
            alerts = []
            
            # Payment failures
            failed_payments = db.query(Payment).filter(
                Payment.status == PaymentStatus.FAILED,
                Payment.created_at >= datetime.utcnow() - timedelta(days=7)
            ).all()
            
            for payment in failed_payments:
                alert = BillingAlert(
                    subscription_id=payment.subscription_id,
                    alert_type="payment_failed",
                    severity="high",
                    title="Payment Failed",
                    message=f"Payment of £{payment.amount} failed. Reason: {payment.failure_message}",
                    metadata={"payment_id": str(payment.id)}
                )
                db.add(alert)
                alerts.append({
                    "type": "payment_failed",
                    "subscription_id": str(payment.subscription_id),
                    "amount": payment.amount
                })
            
            # Trials ending soon
            trials_ending = db.query(Subscription).filter(
                Subscription.status == SubscriptionStatus.TRIAL,
                Subscription.trial_end_date <= datetime.utcnow() + timedelta(days=3),
                Subscription.trial_end_date > datetime.utcnow()
            ).all()
            
            for subscription in trials_ending:
                alert = BillingAlert(
                    subscription_id=subscription.id,
                    alert_type="trial_ending",
                    severity="medium",
                    title="Trial Ending Soon",
                    message=f"Trial ends on {subscription.trial_end_date.strftime('%Y-%m-%d')}",
                    metadata={"days_remaining": (subscription.trial_end_date - datetime.utcnow()).days}
                )
                db.add(alert)
                alerts.append({
                    "type": "trial_ending",
                    "subscription_id": str(subscription.id),
                    "days_remaining": (subscription.trial_end_date - datetime.utcnow()).days
                })
            
            db.commit()
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to create billing alerts: {e}")
            db.rollback()
            raise

# Global instance
enhanced_stripe_service = EnhancedStripeService()
