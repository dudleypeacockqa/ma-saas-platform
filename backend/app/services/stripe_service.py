"""Stripe payment processing service for subscription management"""

import stripe
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import structlog
from decimal import Decimal

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.subscription import Subscription
from app.models.organization import Organization


logger = structlog.get_logger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """
    Service for managing Stripe payments, subscriptions, and billing.
    Implements three-tier subscription model with comprehensive payment handling.
    """

    def __init__(self):
        self.tiers = settings.SUBSCRIPTION_TIERS
        self._setup_price_ids()

    def _setup_price_ids(self):
        """Set up Stripe price IDs for each subscription tier"""
        # These would be created via Stripe Dashboard or API
        # Placeholder IDs for now - will be replaced with actual Stripe price IDs
        self.price_ids = {
            "solo_monthly": "price_solo_monthly",
            "solo_annual": "price_solo_annual",
            "growth_monthly": "price_growth_monthly",
            "growth_annual": "price_growth_annual",
            "enterprise_monthly": "price_enterprise_monthly",
            "enterprise_annual": "price_enterprise_annual"
        }

    async def create_customer(
        self,
        organization_id: str,
        email: str,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a Stripe customer for an organization.

        Args:
            organization_id: Organization ID
            email: Customer email
            name: Customer/organization name
            metadata: Additional metadata

        Returns:
            Stripe customer ID
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={
                    "organization_id": organization_id,
                    **(metadata or {})
                }
            )

            logger.info(
                "Stripe customer created",
                customer_id=customer.id,
                organization_id=organization_id
            )

            return customer.id

        except stripe.error.StripeError as e:
            logger.error("Failed to create Stripe customer", error=str(e))
            raise

    async def create_subscription(
        self,
        customer_id: str,
        tier: str,
        billing_cycle: str = "monthly",
        trial_days: int = 14,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a subscription for a customer.

        Args:
            customer_id: Stripe customer ID
            tier: Subscription tier (solo, growth, enterprise)
            billing_cycle: monthly or annual
            trial_days: Trial period in days
            metadata: Additional metadata

        Returns:
            Subscription details
        """
        try:
            # Get the appropriate price ID
            price_key = f"{tier}_{billing_cycle}"
            price_id = self.price_ids.get(price_key)

            if not price_id:
                raise ValueError(f"Invalid tier or billing cycle: {tier}/{billing_cycle}")

            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                trial_period_days=trial_days if trial_days > 0 else None,
                payment_behavior="default_incomplete",
                payment_settings={"save_default_payment_method": "on_subscription"},
                expand=["latest_invoice.payment_intent"],
                metadata={
                    "tier": tier,
                    "billing_cycle": billing_cycle,
                    **(metadata or {})
                }
            )

            # Get payment intent for initial setup
            payment_intent = None
            if subscription.latest_invoice and subscription.latest_invoice.payment_intent:
                payment_intent = {
                    "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                    "status": subscription.latest_invoice.payment_intent.status
                }

            result = {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "tier": tier,
                "billing_cycle": billing_cycle,
                "current_period_start": datetime.fromtimestamp(subscription.current_period_start),
                "current_period_end": datetime.fromtimestamp(subscription.current_period_end),
                "trial_end": datetime.fromtimestamp(subscription.trial_end) if subscription.trial_end else None,
                "payment_intent": payment_intent
            }

            logger.info(
                "Subscription created",
                subscription_id=subscription.id,
                customer_id=customer_id,
                tier=tier
            )

            return result

        except stripe.error.StripeError as e:
            logger.error("Failed to create subscription", error=str(e))
            raise

    async def update_subscription(
        self,
        subscription_id: str,
        new_tier: Optional[str] = None,
        new_billing_cycle: Optional[str] = None,
        cancel_at_period_end: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update an existing subscription.

        Args:
            subscription_id: Stripe subscription ID
            new_tier: New subscription tier
            new_billing_cycle: New billing cycle
            cancel_at_period_end: Whether to cancel at period end

        Returns:
            Updated subscription details
        """
        try:
            # Get current subscription
            subscription = stripe.Subscription.retrieve(subscription_id)

            update_params = {}

            # Handle tier/billing cycle change
            if new_tier or new_billing_cycle:
                tier = new_tier or subscription.metadata.get("tier")
                billing_cycle = new_billing_cycle or subscription.metadata.get("billing_cycle")
                price_key = f"{tier}_{billing_cycle}"
                price_id = self.price_ids.get(price_key)

                if price_id:
                    update_params["items"] = [{
                        "id": subscription["items"]["data"][0].id,
                        "price": price_id
                    }]
                    update_params["metadata"] = {
                        "tier": tier,
                        "billing_cycle": billing_cycle
                    }

            # Handle cancellation
            if cancel_at_period_end is not None:
                update_params["cancel_at_period_end"] = cancel_at_period_end

            # Update subscription
            if update_params:
                subscription = stripe.Subscription.modify(subscription_id, **update_params)

            result = {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "current_period_end": datetime.fromtimestamp(subscription.current_period_end)
            }

            logger.info(
                "Subscription updated",
                subscription_id=subscription_id,
                updates=update_params
            )

            return result

        except stripe.error.StripeError as e:
            logger.error("Failed to update subscription", error=str(e))
            raise

    async def cancel_subscription(
        self,
        subscription_id: str,
        immediate: bool = False
    ) -> Dict[str, Any]:
        """
        Cancel a subscription.

        Args:
            subscription_id: Stripe subscription ID
            immediate: Cancel immediately vs at period end

        Returns:
            Cancellation details
        """
        try:
            if immediate:
                subscription = stripe.Subscription.delete(subscription_id)
            else:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )

            result = {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "canceled_at": datetime.fromtimestamp(subscription.canceled_at) if subscription.canceled_at else None,
                "cancel_at": datetime.fromtimestamp(subscription.cancel_at) if subscription.cancel_at else None
            }

            logger.info(
                "Subscription canceled",
                subscription_id=subscription_id,
                immediate=immediate
            )

            return result

        except stripe.error.StripeError as e:
            logger.error("Failed to cancel subscription", error=str(e))
            raise

    async def create_payment_method(
        self,
        customer_id: str,
        payment_method_id: str,
        set_default: bool = True
    ) -> bool:
        """
        Attach a payment method to a customer.

        Args:
            customer_id: Stripe customer ID
            payment_method_id: Payment method ID from frontend
            set_default: Set as default payment method

        Returns:
            Success status
        """
        try:
            # Attach payment method to customer
            stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)

            # Set as default if requested
            if set_default:
                stripe.Customer.modify(
                    customer_id,
                    invoice_settings={"default_payment_method": payment_method_id}
                )

            logger.info(
                "Payment method attached",
                customer_id=customer_id,
                payment_method_id=payment_method_id
            )

            return True

        except stripe.error.StripeError as e:
            logger.error("Failed to attach payment method", error=str(e))
            return False

    async def create_checkout_session(
        self,
        customer_id: str,
        tier: str,
        billing_cycle: str = "monthly",
        success_url: str = None,
        cancel_url: str = None
    ) -> str:
        """
        Create a Stripe Checkout session for subscription.

        Args:
            customer_id: Stripe customer ID
            tier: Subscription tier
            billing_cycle: monthly or annual
            success_url: Redirect URL on success
            cancel_url: Redirect URL on cancel

        Returns:
            Checkout session URL
        """
        try:
            price_key = f"{tier}_{billing_cycle}"
            price_id = self.price_ids.get(price_key)

            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[{"price": price_id, "quantity": 1}],
                mode="subscription",
                success_url=success_url or f"{settings.FRONTEND_URL}/subscription/success",
                cancel_url=cancel_url or f"{settings.FRONTEND_URL}/subscription/cancel",
                allow_promotion_codes=True,
                billing_address_collection="auto",
                automatic_tax={"enabled": True}
            )

            logger.info(
                "Checkout session created",
                session_id=session.id,
                customer_id=customer_id
            )

            return session.url

        except stripe.error.StripeError as e:
            logger.error("Failed to create checkout session", error=str(e))
            raise

    async def create_billing_portal_session(
        self,
        customer_id: str,
        return_url: str = None
    ) -> str:
        """
        Create a Stripe Billing Portal session for customer self-service.

        Args:
            customer_id: Stripe customer ID
            return_url: Return URL after portal session

        Returns:
            Portal session URL
        """
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url or f"{settings.FRONTEND_URL}/subscription"
            )

            return session.url

        except stripe.error.StripeError as e:
            logger.error("Failed to create billing portal session", error=str(e))
            raise

    async def handle_webhook(
        self,
        payload: str,
        signature: str
    ) -> Dict[str, Any]:
        """
        Handle Stripe webhook events.

        Args:
            payload: Webhook payload
            signature: Stripe signature

        Returns:
            Processing result
        """
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                settings.STRIPE_WEBHOOK_SECRET
            )

            # Process different event types
            if event.type == "customer.subscription.created":
                await self._handle_subscription_created(event.data.object)
            elif event.type == "customer.subscription.updated":
                await self._handle_subscription_updated(event.data.object)
            elif event.type == "customer.subscription.deleted":
                await self._handle_subscription_deleted(event.data.object)
            elif event.type == "invoice.payment_succeeded":
                await self._handle_payment_succeeded(event.data.object)
            elif event.type == "invoice.payment_failed":
                await self._handle_payment_failed(event.data.object)
            elif event.type == "customer.subscription.trial_will_end":
                await self._handle_trial_ending(event.data.object)

            logger.info("Webhook processed", event_type=event.type, event_id=event.id)

            return {"status": "success", "event_type": event.type}

        except stripe.error.SignatureVerificationError:
            logger.error("Invalid webhook signature")
            raise ValueError("Invalid webhook signature")
        except Exception as e:
            logger.error("Webhook processing failed", error=str(e))
            raise

    async def _handle_subscription_created(self, subscription):
        """Handle subscription creation event"""
        async with AsyncSessionLocal() as session:
            # Find organization by customer ID
            org = await session.execute(
                "SELECT * FROM organizations WHERE stripe_customer_id = :customer_id",
                {"customer_id": subscription.customer}
            )
            org_record = org.fetchone()

            if org_record:
                # Create or update subscription record
                sub = Subscription(
                    organization_id=org_record.id,
                    stripe_customer_id=subscription.customer,
                    stripe_subscription_id=subscription.id,
                    tier=subscription.metadata.get("tier", "solo"),
                    status=subscription.status,
                    billing_cycle=subscription.metadata.get("billing_cycle", "monthly"),
                    current_period_start=datetime.fromtimestamp(subscription.current_period_start),
                    current_period_end=datetime.fromtimestamp(subscription.current_period_end),
                    trial_end=datetime.fromtimestamp(subscription.trial_end) if subscription.trial_end else None
                )
                session.add(sub)
                await session.commit()

    async def _handle_subscription_updated(self, subscription):
        """Handle subscription update event"""
        async with AsyncSessionLocal() as session:
            # Update subscription record
            await session.execute(
                """UPDATE subscriptions
                   SET status = :status,
                       current_period_end = :period_end,
                       cancel_at = :cancel_at,
                       updated_at = :now
                   WHERE stripe_subscription_id = :sub_id""",
                {
                    "status": subscription.status,
                    "period_end": datetime.fromtimestamp(subscription.current_period_end),
                    "cancel_at": datetime.fromtimestamp(subscription.cancel_at) if subscription.cancel_at else None,
                    "now": datetime.utcnow(),
                    "sub_id": subscription.id
                }
            )
            await session.commit()

    async def _handle_subscription_deleted(self, subscription):
        """Handle subscription deletion event"""
        async with AsyncSessionLocal() as session:
            await session.execute(
                """UPDATE subscriptions
                   SET status = 'canceled',
                       canceled_at = :now,
                       updated_at = :now
                   WHERE stripe_subscription_id = :sub_id""",
                {
                    "now": datetime.utcnow(),
                    "sub_id": subscription.id
                }
            )
            await session.commit()

    async def _handle_payment_succeeded(self, invoice):
        """Handle successful payment event"""
        logger.info(
            "Payment succeeded",
            invoice_id=invoice.id,
            customer_id=invoice.customer,
            amount=invoice.amount_paid
        )

    async def _handle_payment_failed(self, invoice):
        """Handle failed payment event"""
        logger.warning(
            "Payment failed",
            invoice_id=invoice.id,
            customer_id=invoice.customer,
            attempt_count=invoice.attempt_count
        )
        # Implement dunning logic here

    async def _handle_trial_ending(self, subscription):
        """Handle trial ending event"""
        logger.info(
            "Trial ending soon",
            subscription_id=subscription.id,
            trial_end=datetime.fromtimestamp(subscription.trial_end)
        )
        # Send trial ending notification

    def get_tier_features(self, tier: str) -> List[str]:
        """Get features for a subscription tier"""
        return self.tiers.get(tier, {}).get("features", [])

    def calculate_proration(
        self,
        current_tier: str,
        new_tier: str,
        billing_cycle: str,
        days_remaining: int
    ) -> Decimal:
        """Calculate proration amount for tier change"""
        current_price = self.tiers[current_tier][f"{billing_cycle}_price"]
        new_price = self.tiers[new_tier][f"{billing_cycle}_price"]

        days_in_period = 30 if billing_cycle == "monthly" else 365
        daily_current = Decimal(current_price) / days_in_period
        daily_new = Decimal(new_price) / days_in_period

        proration = (daily_new - daily_current) * days_remaining
        return round(proration, 2)