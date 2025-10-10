"""
Payment API Endpoints
Handles Stripe payment operations, subscriptions, and webhooks
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Header, status
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from app.core.database import get_db
from app.auth.clerk_auth import ClerkUser, get_current_user, require_admin
from app.integrations.stripe_service import stripe_service
from app.models.subscription import (
    StripeCustomer,
    Subscription,
    Payment,
    WebhookEvent,
    SubscriptionStatus,
    PaymentStatus,
    PlanTier,
    SUBSCRIPTION_PLANS
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payments", tags=["payments"])


# Pydantic schemas
class CheckoutSessionRequest(BaseModel):
    """Request to create a checkout session"""
    price_id: str
    success_url: str
    cancel_url: str
    mode: str = "subscription"


class CheckoutSessionResponse(BaseModel):
    """Checkout session response"""
    session_id: str
    session_url: str
    publishable_key: str


class SubscriptionResponse(BaseModel):
    """Subscription information response"""
    id: int
    stripe_subscription_id: str
    plan_tier: PlanTier
    status: SubscriptionStatus
    amount: int
    currency: str
    interval: str
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    cancel_at_period_end: bool
    features: Dict[str, Any]


class CreateSubscriptionRequest(BaseModel):
    """Request to create a subscription"""
    price_id: str
    plan_tier: PlanTier
    trial_days: Optional[int] = None


class CancelSubscriptionRequest(BaseModel):
    """Request to cancel a subscription"""
    subscription_id: int
    immediately: bool = False


class PaymentResponse(BaseModel):
    """Payment information response"""
    id: int
    amount: int
    currency: str
    status: PaymentStatus
    description: Optional[str]
    paid_at: Optional[datetime]
    created_at: datetime


class PlanInfo(BaseModel):
    """Subscription plan information"""
    tier: PlanTier
    name: str
    price: int
    currency: str
    interval: str
    features: Dict[str, Any]


# Endpoints
@router.get("/plans", response_model=List[PlanInfo])
async def get_subscription_plans():
    """Get available subscription plans"""
    plans = []
    for tier, config in SUBSCRIPTION_PLANS.items():
        plans.append(PlanInfo(
            tier=tier,
            name=config["name"],
            price=config["price"],
            currency=config["currency"],
            interval=config["interval"],
            features=config["features"]
        ))
    return plans


@router.post("/checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a Stripe Checkout session for subscription"""
    try:
        # Get or create Stripe customer
        customer = await stripe_service.get_or_create_customer(
            email=current_user.email,
            clerk_user_id=current_user.user_id,
            organization_id=current_user.organization_id,
            name=f"{current_user.first_name} {current_user.last_name}".strip()
        )

        if not customer:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create customer"
            )

        # Store customer in database
        db_customer = db.query(StripeCustomer).filter(
            StripeCustomer.organization_id == current_user.organization_id
        ).first()

        if not db_customer:
            db_customer = StripeCustomer(
                organization_id=current_user.organization_id,
                stripe_customer_id=customer.id,
                email=current_user.email,
                name=customer.name
            )
            db.add(db_customer)
            db.commit()

        # Create checkout session
        session = await stripe_service.create_checkout_session(
            price_id=request.price_id,
            customer_id=customer.id,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            mode=request.mode,
            metadata={
                "clerk_user_id": current_user.user_id,
                "clerk_organization_id": current_user.organization_id
            }
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create checkout session"
            )

        return CheckoutSessionResponse(
            session_id=session.id,
            session_url=session.url,
            publishable_key=stripe_service.api_key.split("_")[0] + "_test_publishable_key"  # TODO: Use real publishable key
        )

    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/subscriptions", response_model=List[SubscriptionResponse])
async def get_subscriptions(
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all subscriptions for current organization"""
    subscriptions = db.query(Subscription).filter(
        Subscription.organization_id == current_user.organization_id
    ).all()

    response = []
    for sub in subscriptions:
        plan_config = SUBSCRIPTION_PLANS.get(sub.plan_tier, {})
        response.append(SubscriptionResponse(
            id=sub.id,
            stripe_subscription_id=sub.stripe_subscription_id,
            plan_tier=sub.plan_tier,
            status=sub.status,
            amount=sub.amount,
            currency=sub.currency,
            interval=sub.interval,
            current_period_start=sub.current_period_start,
            current_period_end=sub.current_period_end,
            cancel_at_period_end=sub.cancel_at_period_end,
            features=plan_config.get("features", {})
        ))

    return response


@router.get("/subscription/current", response_model=Optional[SubscriptionResponse])
async def get_current_subscription(
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current active subscription for organization"""
    subscription = db.query(Subscription).filter(
        Subscription.organization_id == current_user.organization_id,
        Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING])
    ).first()

    if not subscription:
        return None

    plan_config = SUBSCRIPTION_PLANS.get(subscription.plan_tier, {})
    return SubscriptionResponse(
        id=subscription.id,
        stripe_subscription_id=subscription.stripe_subscription_id,
        plan_tier=subscription.plan_tier,
        status=subscription.status,
        amount=subscription.amount,
        currency=subscription.currency,
        interval=subscription.interval,
        current_period_start=subscription.current_period_start,
        current_period_end=subscription.current_period_end,
        cancel_at_period_end=subscription.cancel_at_period_end,
        features=plan_config.get("features", {})
    )


@router.post("/subscription/cancel")
async def cancel_subscription(
    request: CancelSubscriptionRequest,
    current_user: ClerkUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Cancel a subscription"""
    subscription = db.query(Subscription).filter(
        Subscription.id == request.subscription_id,
        Subscription.organization_id == current_user.organization_id
    ).first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    # Cancel in Stripe
    cancelled = await stripe_service.cancel_subscription(
        subscription.stripe_subscription_id,
        immediately=request.immediately
    )

    if not cancelled:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )

    # Update database
    if request.immediately:
        subscription.status = SubscriptionStatus.CANCELED
        subscription.canceled_at = datetime.utcnow()
        subscription.ended_at = datetime.utcnow()
    else:
        subscription.cancel_at_period_end = True

    db.commit()

    return {"status": "success", "message": "Subscription cancelled"}


@router.get("/payments", response_model=List[PaymentResponse])
async def get_payments(
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment history for organization"""
    # Get customer
    customer = db.query(StripeCustomer).filter(
        StripeCustomer.organization_id == current_user.organization_id
    ).first()

    if not customer:
        return []

    payments = db.query(Payment).filter(
        Payment.customer_id == customer.id
    ).order_by(Payment.created_at.desc()).limit(50).all()

    return [
        PaymentResponse(
            id=payment.id,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status,
            description=payment.description,
            paid_at=payment.paid_at,
            created_at=payment.created_at
        )
        for payment in payments
    ]


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    db: Session = Depends(get_db)
):
    """Handle Stripe webhook events"""
    try:
        # Get raw payload
        payload = await request.body()

        # Verify webhook signature
        event = await stripe_service.verify_webhook_signature(
            payload, stripe_signature
        )

        if not event:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook signature"
            )

        # Check if event already processed
        existing_event = db.query(WebhookEvent).filter(
            WebhookEvent.stripe_event_id == event.id
        ).first()

        if existing_event:
            logger.info(f"Webhook event already processed: {event.id}")
            return {"status": "already_processed"}

        # Log webhook event
        webhook_event = WebhookEvent(
            stripe_event_id=event.id,
            event_type=event.type,
            event_data=event.to_dict()
        )
        db.add(webhook_event)
        db.commit()

        # Handle event
        result = await stripe_service.handle_webhook_event(event, db)

        # Mark as processed
        webhook_event.processed = True
        webhook_event.processed_at = datetime.utcnow()
        db.commit()

        return {"status": "success", "result": result}

    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/customer")
async def get_customer_info(
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Stripe customer information"""
    customer = db.query(StripeCustomer).filter(
        StripeCustomer.organization_id == current_user.organization_id
    ).first()

    if not customer:
        return {"exists": False}

    return {
        "exists": True,
        "stripe_customer_id": customer.stripe_customer_id,
        "email": customer.email,
        "name": customer.name
    }


@router.get("/portal-session")
async def create_portal_session(
    return_url: str,
    current_user: ClerkUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a Stripe Customer Portal session"""
    import stripe

    customer = db.query(StripeCustomer).filter(
        StripeCustomer.organization_id == current_user.organization_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No customer found"
        )

    try:
        session = stripe.billing_portal.Session.create(
            customer=customer.stripe_customer_id,
            return_url=return_url
        )

        return {"url": session.url}

    except Exception as e:
        logger.error(f"Error creating portal session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
