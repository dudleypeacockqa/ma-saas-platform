"""
Stripe Event Payment API Endpoints

Handles ONE-TIME event payments for premium M&A events (£497-£2,997).
These are separate from Clerk-managed subscriptions.
"""

from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import structlog

from app.services.stripe_service import StripeService


logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/stripe", tags=["stripe", "events"])


class CreateCheckoutSessionRequest(BaseModel):
    """Request model for creating an event checkout session"""
    eventType: str = Field(..., description="Type of event (Premium Masterclass, Executive Workshop, VIP Deal Summit)")
    price: int = Field(..., description="Event price in GBP")
    customerEmail: EmailStr = Field(..., description="Customer email address")
    userId: Optional[str] = Field(None, description="Clerk user ID if logged in")


@router.post("/create-checkout-session")
async def create_event_checkout_session(request: CreateCheckoutSessionRequest):
    """
    Create a Stripe Checkout session for a one-time event payment.

    This endpoint is called by the EventCheckout component on the frontend.
    It creates a Stripe Checkout Session for purchasing premium event tickets.

    Args:
        request: Event checkout details

    Returns:
        Dict with sessionId and checkout URL

    Raises:
        HTTPException: If session creation fails
    """
    try:
        stripe_service = StripeService()

        # Create checkout session
        result = await stripe_service.create_event_checkout_session(
            event_type=request.eventType,
            customer_email=request.customerEmail,
            user_id=request.userId
        )

        logger.info(
            "Event checkout session created",
            event_type=request.eventType,
            user_id=request.userId,
            session_id=result["session_id"]
        )

        return {
            "sessionId": result["session_id"],
            "url": result["url"]
        }

    except ValueError as e:
        logger.error("Invalid event type", event_type=request.eventType, error=str(e))
        raise HTTPException(
            status_code=400,
            detail=f"Invalid event type: {request.eventType}"
        )
    except Exception as e:
        logger.error("Failed to create checkout session", error=str(e), event_type=request.eventType)
        raise HTTPException(
            status_code=500,
            detail="Failed to create checkout session. Please try again."
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature")
):
    """
    Handle Stripe webhook events for one-time event payments.

    This endpoint receives notifications from Stripe when:
    - checkout.session.completed: Payment succeeded
    - checkout.session.expired: Checkout session expired

    Note: Subscription events are handled by Clerk, not this endpoint.

    Args:
        request: FastAPI request with raw webhook payload
        stripe_signature: Stripe signature header for verification

    Returns:
        Success response

    Raises:
        HTTPException: If signature verification fails or processing errors
    """
    try:
        # Get raw body for signature verification
        payload = await request.body()

        if not stripe_signature:
            logger.error("Missing Stripe signature header")
            raise HTTPException(status_code=400, detail="Missing Stripe signature")

        stripe_service = StripeService()

        # Process webhook (includes signature verification)
        result = await stripe_service.handle_webhook(
            payload=payload,
            signature=stripe_signature
        )

        logger.info(
            "Stripe webhook processed successfully",
            event_type=result.get("event_type"),
            status=result.get("status")
        )

        return {"status": "success"}

    except ValueError as e:
        # Signature verification failed
        logger.error("Webhook signature verification failed", error=str(e))
        raise HTTPException(status_code=401, detail="Invalid signature")
    except Exception as e:
        logger.error("Webhook processing failed", error=str(e))
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@router.get("/event-pricing")
async def get_event_pricing():
    """
    Get pricing information for all event types.

    Returns:
        Dict of event pricing details for display on frontend

    Example response:
    {
        "premium_masterclass": {
            "price": 49700,
            "currency": "gbp",
            "display": "£497",
            "name": "Premium Masterclass",
            "description": "2-hour intensive session with industry leader"
        },
        ...
    }
    """
    stripe_service = StripeService()
    return stripe_service.get_event_pricing()
