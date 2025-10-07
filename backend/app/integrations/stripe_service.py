"""
Stripe Payment Service Integration
Handles payment processing, subscription management, and customer sync with Clerk
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import stripe
import httpx
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY
else:
    logger.warning("STRIPE_SECRET_KEY not set. Payment processing will fail.")


class StripeService:
    """Stripe payment and subscription management service"""

    def __init__(self):
        self.api_key = STRIPE_SECRET_KEY
        self.webhook_secret = STRIPE_WEBHOOK_SECRET

    async def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        clerk_user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[stripe.Customer]:
        """Create a Stripe customer linked to Clerk user/organization"""
        try:
            customer_metadata = metadata or {}
            customer_metadata.update({
                "clerk_user_id": clerk_user_id,
                "clerk_organization_id": organization_id
            })

            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=customer_metadata
            )

            logger.info(f"Created Stripe customer: {customer.id} for user: {clerk_user_id}")
            return customer

        except stripe.error.StripeError as e:
            logger.error(f"Stripe customer creation failed: {e}")
            return None

    async def get_or_create_customer(
        self,
        email: str,
        clerk_user_id: str,
        organization_id: Optional[str] = None,
        name: Optional[str] = None
    ) -> Optional[stripe.Customer]:
        """Get existing customer or create new one"""
        try:
            # Search for existing customer by Clerk user ID
            customers = stripe.Customer.list(
                email=email,
                limit=1
            )

            if customers.data:
                customer = customers.data[0]
                # Update metadata if needed
                if customer.metadata.get("clerk_user_id") != clerk_user_id:
                    stripe.Customer.modify(
                        customer.id,
                        metadata={
                            "clerk_user_id": clerk_user_id,
                            "clerk_organization_id": organization_id
                        }
                    )
                return customer

            # Create new customer
            return await self.create_customer(
                email=email,
                name=name,
                clerk_user_id=clerk_user_id,
                organization_id=organization_id
            )

        except stripe.error.StripeError as e:
            logger.error(f"Error getting/creating customer: {e}")
            return None

    async def create_checkout_session(
        self,
        price_id: str,
        customer_id: str,
        success_url: str,
        cancel_url: str,
        mode: str = "subscription",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[stripe.checkout.Session]:
        """Create a Stripe Checkout session"""
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[{
                    "price": price_id,
                    "quantity": 1
                }],
                mode=mode,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata or {},
                subscription_data={
                    "metadata": metadata or {}
                } if mode == "subscription" else None
            )

            logger.info(f"Created checkout session: {session.id}")
            return session

        except stripe.error.StripeError as e:
            logger.error(f"Checkout session creation failed: {e}")
            return None

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[stripe.Subscription]:
        """Create a subscription for a customer"""
        try:
            subscription_params = {
                "customer": customer_id,
                "items": [{"price": price_id}],
                "metadata": metadata or {}
            }

            if trial_days:
                subscription_params["trial_period_days"] = trial_days

            subscription = stripe.Subscription.create(**subscription_params)

            logger.info(f"Created subscription: {subscription.id} for customer: {customer_id}")
            return subscription

        except stripe.error.StripeError as e:
            logger.error(f"Subscription creation failed: {e}")
            return None

    async def cancel_subscription(
        self,
        subscription_id: str,
        immediately: bool = False
    ) -> Optional[stripe.Subscription]:
        """Cancel a subscription"""
        try:
            if immediately:
                subscription = stripe.Subscription.cancel(subscription_id)
            else:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )

            logger.info(f"Cancelled subscription: {subscription_id}")
            return subscription

        except stripe.error.StripeError as e:
            logger.error(f"Subscription cancellation failed: {e}")
            return None

    async def get_subscription(self, subscription_id: str) -> Optional[stripe.Subscription]:
        """Retrieve subscription details"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving subscription: {e}")
            return None

    async def list_customer_subscriptions(
        self,
        customer_id: str
    ) -> List[stripe.Subscription]:
        """List all subscriptions for a customer"""
        try:
            subscriptions = stripe.Subscription.list(
                customer=customer_id,
                limit=100
            )
            return subscriptions.data
        except stripe.error.StripeError as e:
            logger.error(f"Error listing subscriptions: {e}")
            return []

    async def create_payment_intent(
        self,
        amount: int,
        currency: str = "usd",
        customer_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[stripe.PaymentIntent]:
        """Create a payment intent for one-time payments"""
        try:
            payment_intent_params = {
                "amount": amount,
                "currency": currency,
                "metadata": metadata or {}
            }

            if customer_id:
                payment_intent_params["customer"] = customer_id

            payment_intent = stripe.PaymentIntent.create(**payment_intent_params)

            logger.info(f"Created payment intent: {payment_intent.id}")
            return payment_intent

        except stripe.error.StripeError as e:
            logger.error(f"Payment intent creation failed: {e}")
            return None

    async def create_product(
        self,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[stripe.Product]:
        """Create a Stripe product"""
        try:
            product = stripe.Product.create(
                name=name,
                description=description,
                metadata=metadata or {}
            )

            logger.info(f"Created product: {product.id}")
            return product

        except stripe.error.StripeError as e:
            logger.error(f"Product creation failed: {e}")
            return None

    async def create_price(
        self,
        product_id: str,
        unit_amount: int,
        currency: str = "usd",
        recurring_interval: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[stripe.Price]:
        """Create a price for a product"""
        try:
            price_params = {
                "product": product_id,
                "unit_amount": unit_amount,
                "currency": currency,
                "metadata": metadata or {}
            }

            if recurring_interval:
                price_params["recurring"] = {"interval": recurring_interval}

            price = stripe.Price.create(**price_params)

            logger.info(f"Created price: {price.id}")
            return price

        except stripe.error.StripeError as e:
            logger.error(f"Price creation failed: {e}")
            return None

    async def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str
    ) -> Optional[stripe.Event]:
        """Verify Stripe webhook signature and construct event"""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return event
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {e}")
            return None
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            return None

    async def sync_subscription_to_clerk(
        self,
        subscription: stripe.Subscription,
        organization_id: str
    ) -> bool:
        """Update Clerk organization metadata with subscription info"""
        try:
            async with httpx.AsyncClient() as client:
                url = f"https://api.clerk.com/v1/organizations/{organization_id}"
                headers = {
                    "Authorization": f"Bearer {CLERK_SECRET_KEY}",
                    "Content-Type": "application/json"
                }

                subscription_metadata = {
                    "stripe_subscription_id": subscription.id,
                    "stripe_customer_id": subscription.customer,
                    "subscription_status": subscription.status,
                    "current_period_end": subscription.current_period_end,
                    "plan_id": subscription.items.data[0].price.id if subscription.items.data else None
                }

                data = {
                    "private_metadata": {
                        "subscription": subscription_metadata
                    }
                }

                response = await client.patch(url, headers=headers, json=data)

                if response.status_code == 200:
                    logger.info(f"Synced subscription to Clerk org: {organization_id}")
                    return True
                else:
                    logger.error(f"Failed to sync to Clerk: {response.status_code}")
                    return False

        except Exception as e:
            logger.error(f"Error syncing to Clerk: {e}")
            return False

    async def handle_webhook_event(
        self,
        event: stripe.Event,
        db: Session
    ) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        event_type = event.type
        data = event.data.object

        logger.info(f"Processing Stripe webhook: {event_type}")

        handlers = {
            "customer.created": self._handle_customer_created,
            "customer.updated": self._handle_customer_updated,
            "customer.deleted": self._handle_customer_deleted,
            "customer.subscription.created": self._handle_subscription_created,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "invoice.paid": self._handle_invoice_paid,
            "invoice.payment_failed": self._handle_payment_failed,
            "checkout.session.completed": self._handle_checkout_completed,
        }

        handler = handlers.get(event_type)
        if handler:
            return await handler(data, db)

        return {"status": "unhandled", "event_type": event_type}

    async def _handle_customer_created(self, customer: stripe.Customer, db: Session) -> Dict[str, Any]:
        """Handle customer.created event"""
        logger.info(f"Customer created: {customer.id}")
        return {"status": "success", "customer_id": customer.id}

    async def _handle_customer_updated(self, customer: stripe.Customer, db: Session) -> Dict[str, Any]:
        """Handle customer.updated event"""
        logger.info(f"Customer updated: {customer.id}")
        return {"status": "success", "customer_id": customer.id}

    async def _handle_customer_deleted(self, customer: stripe.Customer, db: Session) -> Dict[str, Any]:
        """Handle customer.deleted event"""
        logger.info(f"Customer deleted: {customer.id}")
        return {"status": "success", "customer_id": customer.id}

    async def _handle_subscription_created(self, subscription: stripe.Subscription, db: Session) -> Dict[str, Any]:
        """Handle customer.subscription.created event"""
        logger.info(f"Subscription created: {subscription.id}")

        # Sync to Clerk if organization_id in metadata
        org_id = subscription.metadata.get("clerk_organization_id")
        if org_id:
            await self.sync_subscription_to_clerk(subscription, org_id)

        return {"status": "success", "subscription_id": subscription.id}

    async def _handle_subscription_updated(self, subscription: stripe.Subscription, db: Session) -> Dict[str, Any]:
        """Handle customer.subscription.updated event"""
        logger.info(f"Subscription updated: {subscription.id}")

        # Sync to Clerk
        org_id = subscription.metadata.get("clerk_organization_id")
        if org_id:
            await self.sync_subscription_to_clerk(subscription, org_id)

        return {"status": "success", "subscription_id": subscription.id}

    async def _handle_subscription_deleted(self, subscription: stripe.Subscription, db: Session) -> Dict[str, Any]:
        """Handle customer.subscription.deleted event"""
        logger.info(f"Subscription deleted: {subscription.id}")

        # Update Clerk to mark subscription as cancelled
        org_id = subscription.metadata.get("clerk_organization_id")
        if org_id:
            await self.sync_subscription_to_clerk(subscription, org_id)

        return {"status": "success", "subscription_id": subscription.id}

    async def _handle_invoice_paid(self, invoice: stripe.Invoice, db: Session) -> Dict[str, Any]:
        """Handle invoice.paid event"""
        logger.info(f"Invoice paid: {invoice.id}")
        return {"status": "success", "invoice_id": invoice.id}

    async def _handle_payment_failed(self, invoice: stripe.Invoice, db: Session) -> Dict[str, Any]:
        """Handle invoice.payment_failed event"""
        logger.error(f"Payment failed for invoice: {invoice.id}")
        # TODO: Send notification to user
        return {"status": "success", "invoice_id": invoice.id}

    async def _handle_checkout_completed(self, session: stripe.checkout.Session, db: Session) -> Dict[str, Any]:
        """Handle checkout.session.completed event"""
        logger.info(f"Checkout completed: {session.id}")
        return {"status": "success", "session_id": session.id}


# Singleton instance
stripe_service = StripeService()
