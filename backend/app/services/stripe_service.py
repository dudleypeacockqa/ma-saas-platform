"""Stripe payment processing service for ONE-TIME event payments

IMPORTANT: This service handles ONLY one-time event payments (£497-£2,997).
Subscription payments are handled by Clerk Native Billing - NOT by this service.

See SUBSCRIPTION_FLOWS.md for complete payment architecture documentation.
"""

import stripe
from typing import Dict, Any, Optional
from datetime import datetime
import structlog

from app.core.config import settings


logger = structlog.get_logger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """
    Service for managing Stripe one-time event payments.

    **SUBSCRIPTIONS ARE HANDLED BY CLERK** - This service does NOT manage subscriptions.

    This service provides:
    - Event ticket payment processing (£497-£2,997)
    - Checkout session creation for one-time payments
    - Webhook processing for checkout.session.completed events
    """

    def __init__(self):
        # Event pricing structure (one-time payments in pence for GBP)
        self.event_pricing = {
            "premium_masterclass": {
                "price": 49700,  # £497.00
                "currency": "gbp",
                "display": "£497",
                "name": "Premium Masterclass",
                "description": "2-hour intensive session with industry leader"
            },
            "executive_workshop": {
                "price": 129700,  # £1,297.00
                "currency": "gbp",
                "display": "£1,297",
                "name": "Executive Workshop",
                "description": "Half-day strategic workshop for senior professionals"
            },
            "vip_deal_summit": {
                "price": 299700,  # £2,997.00
                "currency": "gbp",
                "display": "£2,997",
                "name": "VIP Deal Summit",
                "description": "Full-day exclusive summit with deal-making opportunities"
            }
        }

    async def create_event_checkout_session(
        self,
        event_type: str,
        customer_email: str,
        user_id: Optional[str] = None,
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe Checkout session for a one-time event payment.

        Args:
            event_type: Type of event (premium_masterclass, executive_workshop, vip_deal_summit)
            customer_email: Customer's email address
            user_id: Clerk user ID for tracking
            success_url: Redirect URL on successful payment
            cancel_url: Redirect URL on cancelled payment

        Returns:
            Dict with session_id and checkout URL

        Raises:
            ValueError: If event_type is invalid
            stripe.error.StripeError: If Stripe API call fails
        """
        try:
            # Validate event type
            event_key = event_type.lower().replace(" ", "_")
            event_info = self.event_pricing.get(event_key)

            if not event_info:
                raise ValueError(f"Invalid event type: {event_type}")

            # Default URLs if not provided
            if not success_url:
                success_url = f"{settings.FRONTEND_URL}/events/success?session_id={{CHECKOUT_SESSION_ID}}"
            if not cancel_url:
                cancel_url = f"{settings.FRONTEND_URL}/events/cancel"

            # Create Checkout Session
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": event_info["currency"],
                        "product_data": {
                            "name": event_info["name"],
                            "description": event_info["description"],
                        },
                        "unit_amount": event_info["price"],
                    },
                    "quantity": 1,
                }],
                mode="payment",  # One-time payment, NOT subscription
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=customer_email,
                metadata={
                    "user_id": user_id or "guest",
                    "event_type": event_type,
                    "payment_type": "one_time_event",
                    "environment": settings.ENVIRONMENT
                },
                # Enable automatic tax calculation
                automatic_tax={"enabled": True},
                # Allow promotion codes
                allow_promotion_codes=True,
            )

            logger.info(
                "Event checkout session created",
                session_id=session.id,
                event_type=event_type,
                amount=event_info["price"],
                user_id=user_id
            )

            return {
                "session_id": session.id,
                "url": session.url,
                "event_type": event_type,
                "amount": event_info["display"]
            }

        except ValueError as e:
            logger.error("Invalid event type", event_type=event_type, error=str(e))
            raise
        except stripe.error.StripeError as e:
            logger.error("Failed to create event checkout session", error=str(e))
            raise

    async def retrieve_checkout_session(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve a Checkout Session by ID.

        Args:
            session_id: Stripe Checkout Session ID

        Returns:
            Session details including payment status

        Raises:
            stripe.error.StripeError: If retrieval fails
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)

            return {
                "session_id": session.id,
                "payment_status": session.payment_status,
                "customer_email": session.customer_details.email if session.customer_details else None,
                "amount_total": session.amount_total,
                "currency": session.currency,
                "metadata": session.metadata,
                "created": datetime.fromtimestamp(session.created)
            }

        except stripe.error.StripeError as e:
            logger.error("Failed to retrieve checkout session", session_id=session_id, error=str(e))
            raise

    async def handle_checkout_completed(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle checkout.session.completed webhook event.

        This is called when a customer successfully completes payment for an event.

        Args:
            session: Stripe Session object from webhook

        Returns:
            Processing result with event access details

        TODO: Implement event access granting logic
        - Send confirmation email with event details
        - Grant access to event materials
        - Add to event attendee list
        - Track for Community Leader revenue sharing (if applicable)
        """
        try:
            session_id = session.get("id")
            customer_email = session.get("customer_details", {}).get("email")
            metadata = session.get("metadata", {})

            user_id = metadata.get("user_id")
            event_type = metadata.get("event_type")
            amount_paid = session.get("amount_total", 0)

            logger.info(
                "Event payment completed",
                session_id=session_id,
                user_id=user_id,
                event_type=event_type,
                amount_paid=amount_paid,
                customer_email=customer_email
            )

            # TODO: Grant event access
            # - Create event_attendees record in database
            # - Send email with event details and calendar invite
            # - If hosted by Community Leader, track for 20% revenue share

            return {
                "status": "success",
                "session_id": session_id,
                "event_type": event_type,
                "customer_email": customer_email,
                "access_granted": True  # Set to True after implementing access logic
            }

        except Exception as e:
            logger.error("Failed to handle checkout completed", error=str(e), session_id=session.get("id"))
            raise

    async def handle_webhook(
        self,
        payload: bytes,
        signature: str
    ) -> Dict[str, Any]:
        """
        Handle Stripe webhook events for one-time payments.

        Args:
            payload: Raw webhook payload
            signature: Stripe signature header

        Returns:
            Processing result

        Raises:
            ValueError: If signature verification fails
        """
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                settings.STRIPE_WEBHOOK_SECRET
            )

            event_type = event["type"]

            logger.info("Processing Stripe webhook", event_type=event_type, event_id=event["id"])

            # Handle checkout completion for event payments
            if event_type == "checkout.session.completed":
                session = event["data"]["object"]

                # Only process if this is an event payment (not subscription)
                if session.get("metadata", {}).get("payment_type") == "one_time_event":
                    return await self.handle_checkout_completed(session)
                else:
                    logger.info("Ignoring non-event checkout session", session_id=session.get("id"))

            # Ignore subscription-related events (handled by Clerk)
            elif event_type in [
                "customer.subscription.created",
                "customer.subscription.updated",
                "customer.subscription.deleted",
                "invoice.payment_succeeded",
                "invoice.payment_failed"
            ]:
                logger.info(
                    "Ignoring subscription event (handled by Clerk)",
                    event_type=event_type
                )

            return {"status": "success", "event_type": event_type}

        except stripe.error.SignatureVerificationError as e:
            logger.error("Invalid webhook signature", error=str(e))
            raise ValueError("Invalid webhook signature")
        except Exception as e:
            logger.error("Webhook processing failed", error=str(e), event_type=event.get("type"))
            raise

    def get_event_pricing(self) -> Dict[str, Dict[str, Any]]:
        """
        Get pricing information for all event types.

        Returns:
            Dict of event pricing details
        """
        return self.event_pricing
