"""Payment and subscription management API endpoints"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from pydantic import BaseModel, Field
import structlog

from app.services.stripe_service import StripeService
from app.api.deps import get_current_user, get_db
from app.core.database import AsyncSession
from app.models.organization import Organization
from app.models.subscription import Subscription


logger = structlog.get_logger(__name__)

router = APIRouter()


class CreateSubscriptionRequest(BaseModel):
    """Request model for creating a subscription"""
    tier: str = Field(..., description="Subscription tier: solo, growth, or enterprise")
    billing_cycle: str = Field("monthly", description="Billing cycle: monthly or annual")
    payment_method_id: Optional[str] = Field(None, description="Payment method ID from Stripe.js")
    trial_days: int = Field(14, ge=0, le=60, description="Trial period in days")


class UpdateSubscriptionRequest(BaseModel):
    """Request model for updating a subscription"""
    new_tier: Optional[str] = Field(None, description="New subscription tier")
    new_billing_cycle: Optional[str] = Field(None, description="New billing cycle")
    cancel_at_period_end: Optional[bool] = Field(None, description="Cancel at period end")


class CreateCheckoutRequest(BaseModel):
    """Request model for creating a checkout session"""
    tier: str = Field(..., description="Subscription tier")
    billing_cycle: str = Field("monthly", description="Billing cycle")
    success_url: Optional[str] = Field(None, description="Redirect URL on success")
    cancel_url: Optional[str] = Field(None, description="Redirect URL on cancel")


class PaymentMethodRequest(BaseModel):
    """Request model for adding a payment method"""
    payment_method_id: str = Field(..., description="Payment method ID from Stripe.js")
    set_default: bool = Field(True, description="Set as default payment method")


@router.post("/create-subscription")
async def create_subscription(
    request: CreateSubscriptionRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new subscription for the organization.

    This endpoint creates a Stripe subscription with the specified tier
    and billing cycle. It includes a trial period and returns payment
    intent details for completing the initial setup.
    """
    try:
        stripe_service = StripeService()

        # Get organization
        org = await db.get(Organization, current_user.organization_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        # Create Stripe customer if doesn't exist
        if not org.stripe_customer_id:
            customer_id = await stripe_service.create_customer(
                organization_id=str(org.id),
                email=current_user.email,
                name=org.name,
                metadata={"environment": settings.ENVIRONMENT}
            )
            org.stripe_customer_id = customer_id
            await db.commit()
        else:
            customer_id = org.stripe_customer_id

        # Attach payment method if provided
        if request.payment_method_id:
            await stripe_service.create_payment_method(
                customer_id=customer_id,
                payment_method_id=request.payment_method_id
            )

        # Create subscription
        subscription = await stripe_service.create_subscription(
            customer_id=customer_id,
            tier=request.tier,
            billing_cycle=request.billing_cycle,
            trial_days=request.trial_days
        )

        # Save subscription to database
        db_subscription = Subscription(
            organization_id=org.id,
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription["subscription_id"],
            tier=request.tier,
            status=subscription["status"],
            billing_cycle=request.billing_cycle,
            current_period_start=subscription["current_period_start"],
            current_period_end=subscription["current_period_end"],
            trial_end=subscription.get("trial_end")
        )
        db.add(db_subscription)
        await db.commit()

        logger.info(
            "Subscription created",
            organization_id=str(org.id),
            tier=request.tier,
            subscription_id=subscription["subscription_id"]
        )

        return {
            "subscription": subscription,
            "features": stripe_service.get_tier_features(request.tier)
        }

    except Exception as e:
        logger.error("Failed to create subscription", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subscription. Please try again."
        )


@router.put("/update-subscription")
async def update_subscription(
    request: UpdateSubscriptionRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing subscription.

    Allows changing tier, billing cycle, or scheduling cancellation.
    Handles proration automatically through Stripe.
    """
    try:
        stripe_service = StripeService()

        # Get current subscription
        subscription = await db.execute(
            "SELECT * FROM subscriptions WHERE organization_id = :org_id",
            {"org_id": current_user.organization_id}
        )
        sub_record = subscription.fetchone()

        if not sub_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )

        # Update subscription in Stripe
        result = await stripe_service.update_subscription(
            subscription_id=sub_record.stripe_subscription_id,
            new_tier=request.new_tier,
            new_billing_cycle=request.new_billing_cycle,
            cancel_at_period_end=request.cancel_at_period_end
        )

        # Update database
        update_query = """
            UPDATE subscriptions
            SET tier = COALESCE(:tier, tier),
                billing_cycle = COALESCE(:billing_cycle, billing_cycle),
                cancel_at = CASE
                    WHEN :cancel_at_period_end THEN current_period_end
                    ELSE NULL
                END,
                updated_at = NOW()
            WHERE organization_id = :org_id
        """
        await db.execute(update_query, {
            "tier": request.new_tier,
            "billing_cycle": request.new_billing_cycle,
            "cancel_at_period_end": request.cancel_at_period_end,
            "org_id": current_user.organization_id
        })
        await db.commit()

        logger.info(
            "Subscription updated",
            organization_id=str(current_user.organization_id),
            updates=request.dict(exclude_none=True)
        )

        return result

    except Exception as e:
        logger.error("Failed to update subscription", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update subscription. Please try again."
        )


@router.post("/cancel-subscription")
async def cancel_subscription(
    immediate: bool = False,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel a subscription.

    By default, cancels at the end of the current period.
    Set immediate=true for immediate cancellation.
    """
    try:
        stripe_service = StripeService()

        # Get subscription
        subscription = await db.execute(
            "SELECT * FROM subscriptions WHERE organization_id = :org_id",
            {"org_id": current_user.organization_id}
        )
        sub_record = subscription.fetchone()

        if not sub_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )

        # Cancel in Stripe
        result = await stripe_service.cancel_subscription(
            subscription_id=sub_record.stripe_subscription_id,
            immediate=immediate
        )

        # Update database
        await db.execute(
            """UPDATE subscriptions
               SET status = :status,
                   canceled_at = :canceled_at,
                   cancel_at = :cancel_at,
                   updated_at = NOW()
               WHERE organization_id = :org_id""",
            {
                "status": result["status"],
                "canceled_at": result.get("canceled_at"),
                "cancel_at": result.get("cancel_at"),
                "org_id": current_user.organization_id
            }
        )
        await db.commit()

        logger.info(
            "Subscription canceled",
            organization_id=str(current_user.organization_id),
            immediate=immediate
        )

        return result

    except Exception as e:
        logger.error("Failed to cancel subscription", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription. Please try again."
        )


@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CreateCheckoutRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a Stripe Checkout session for subscription signup.

    Returns a URL to redirect the user to Stripe's hosted checkout page.
    """
    try:
        stripe_service = StripeService()

        # Get or create Stripe customer
        org = await db.get(Organization, current_user.organization_id)
        if not org.stripe_customer_id:
            customer_id = await stripe_service.create_customer(
                organization_id=str(org.id),
                email=current_user.email,
                name=org.name
            )
            org.stripe_customer_id = customer_id
            await db.commit()
        else:
            customer_id = org.stripe_customer_id

        # Create checkout session
        checkout_url = await stripe_service.create_checkout_session(
            customer_id=customer_id,
            tier=request.tier,
            billing_cycle=request.billing_cycle,
            success_url=request.success_url,
            cancel_url=request.cancel_url
        )

        logger.info(
            "Checkout session created",
            organization_id=str(org.id),
            tier=request.tier
        )

        return {"checkout_url": checkout_url}

    except Exception as e:
        logger.error("Failed to create checkout session", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session. Please try again."
        )


@router.post("/create-billing-portal-session")
async def create_billing_portal_session(
    return_url: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a Stripe Billing Portal session for customer self-service.

    Returns a URL to redirect the user to Stripe's hosted billing portal
    where they can manage their subscription, payment methods, and invoices.
    """
    try:
        stripe_service = StripeService()

        # Get organization's Stripe customer ID
        org = await db.get(Organization, current_user.organization_id)
        if not org or not org.stripe_customer_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Stripe customer found for organization"
            )

        # Create portal session
        portal_url = await stripe_service.create_billing_portal_session(
            customer_id=org.stripe_customer_id,
            return_url=return_url
        )

        logger.info(
            "Billing portal session created",
            organization_id=str(org.id)
        )

        return {"portal_url": portal_url}

    except Exception as e:
        logger.error("Failed to create billing portal session", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to access billing portal. Please try again."
        )


@router.post("/add-payment-method")
async def add_payment_method(
    request: PaymentMethodRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a payment method to the organization's Stripe customer.

    The payment_method_id should be obtained from Stripe.js on the frontend
    after collecting card details.
    """
    try:
        stripe_service = StripeService()

        # Get organization's Stripe customer ID
        org = await db.get(Organization, current_user.organization_id)
        if not org or not org.stripe_customer_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Stripe customer found for organization"
            )

        # Attach payment method
        success = await stripe_service.create_payment_method(
            customer_id=org.stripe_customer_id,
            payment_method_id=request.payment_method_id,
            set_default=request.set_default
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add payment method"
            )

        logger.info(
            "Payment method added",
            organization_id=str(org.id)
        )

        return {"success": True, "message": "Payment method added successfully"}

    except Exception as e:
        logger.error("Failed to add payment method", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add payment method. Please try again."
        )


@router.get("/subscription-status")
async def get_subscription_status(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current subscription status and details.

    Returns subscription tier, status, billing information, and available features.
    """
    try:
        stripe_service = StripeService()

        # Get subscription from database
        result = await db.execute(
            """SELECT s.*, o.name as org_name
               FROM subscriptions s
               JOIN organizations o ON s.organization_id = o.id
               WHERE s.organization_id = :org_id""",
            {"org_id": current_user.organization_id}
        )
        subscription = result.fetchone()

        if not subscription:
            return {
                "has_subscription": False,
                "tier": "free",
                "features": ["Basic features", "Limited usage"]
            }

        return {
            "has_subscription": True,
            "subscription_id": subscription.stripe_subscription_id,
            "tier": subscription.tier,
            "status": subscription.status,
            "billing_cycle": subscription.billing_cycle,
            "current_period_start": subscription.current_period_start,
            "current_period_end": subscription.current_period_end,
            "cancel_at": subscription.cancel_at,
            "trial_end": subscription.trial_end,
            "features": stripe_service.get_tier_features(subscription.tier)
        }

    except Exception as e:
        logger.error("Failed to get subscription status", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get subscription status."
        )


@router.get("/pricing")
async def get_pricing():
    """
    Get pricing information for all subscription tiers.

    Returns tier details, features, and pricing for display on pricing page.
    """
    stripe_service = StripeService()

    return {
        "tiers": [
            {
                "name": "solo",
                "display_name": "Solo",
                "monthly_price": 279,
                "annual_price": 3010,
                "annual_savings": 338,
                "features": stripe_service.get_tier_features("solo"),
                "recommended": False
            },
            {
                "name": "growth",
                "display_name": "Growth",
                "monthly_price": 798,
                "annual_price": 8618,
                "annual_savings": 958,
                "features": stripe_service.get_tier_features("growth"),
                "recommended": True
            },
            {
                "name": "enterprise",
                "display_name": "Enterprise",
                "monthly_price": 1598,
                "annual_price": 17258,
                "annual_savings": 1918,
                "features": stripe_service.get_tier_features("enterprise"),
                "recommended": False
            }
        ],
        "currency": "USD",
        "trial_days": 14
    }