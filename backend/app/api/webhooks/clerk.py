"""
Clerk webhook handlers for subscription and user events
Handles real-time updates from Clerk for subscriptions, users, and organizations
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.organization import Organization
from app.models.subscription import Subscription, SubscriptionStatus, SubscriptionPlan
from app.core.config import settings
import hmac
import hashlib

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks/clerk", tags=["webhooks"])


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify Clerk webhook signature"""
    if not signature or not secret:
        return False
    
    try:
        # Clerk uses HMAC-SHA256
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Remove 'sha256=' prefix if present
        if signature.startswith('sha256='):
            signature = signature[7:]
            
        return hmac.compare_digest(expected_signature, signature)
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {e}")
        return False


async def get_webhook_payload(request: Request) -> Dict[str, Any]:
    """Extract and validate webhook payload"""
    try:
        payload = await request.body()
        signature = request.headers.get('clerk-signature', '')
        
        # Verify signature if webhook secret is configured
        if settings.CLERK_WEBHOOK_SECRET:
            if not verify_webhook_signature(payload, signature, settings.CLERK_WEBHOOK_SECRET):
                raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        return json.loads(payload.decode('utf-8'))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error(f"Error processing webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Error processing webhook")


@router.post("/user")
async def handle_user_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle user-related webhook events from Clerk"""
    payload = await get_webhook_payload(request)
    event_type = payload.get('type')
    data = payload.get('data', {})
    
    logger.info(f"Received user webhook: {event_type}")
    
    try:
        if event_type == 'user.created':
            await handle_user_created(data, db)
        elif event_type == 'user.updated':
            await handle_user_updated(data, db)
        elif event_type == 'user.deleted':
            await handle_user_deleted(data, db)
        else:
            logger.warning(f"Unhandled user event type: {event_type}")
            
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error handling user webhook {event_type}: {e}")
        raise HTTPException(status_code=500, detail="Error processing webhook")


@router.post("/organization")
async def handle_organization_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle organization-related webhook events from Clerk"""
    payload = await get_webhook_payload(request)
    event_type = payload.get('type')
    data = payload.get('data', {})
    
    logger.info(f"Received organization webhook: {event_type}")
    
    try:
        if event_type == 'organization.created':
            await handle_organization_created(data, db)
        elif event_type == 'organization.updated':
            await handle_organization_updated(data, db)
        elif event_type == 'organization.deleted':
            await handle_organization_deleted(data, db)
        elif event_type == 'organizationMembership.created':
            await handle_membership_created(data, db)
        elif event_type == 'organizationMembership.updated':
            await handle_membership_updated(data, db)
        elif event_type == 'organizationMembership.deleted':
            await handle_membership_deleted(data, db)
        else:
            logger.warning(f"Unhandled organization event type: {event_type}")
            
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error handling organization webhook {event_type}: {e}")
        raise HTTPException(status_code=500, detail="Error processing webhook")


@router.post("/subscription")
async def handle_subscription_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle subscription-related webhook events from Clerk Billing"""
    payload = await get_webhook_payload(request)
    event_type = payload.get('type')
    data = payload.get('data', {})

    logger.info(f"Received subscription webhook: {event_type}")

    try:
        # Clerk Billing webhook event types
        if event_type == 'subscription.created':
            await handle_subscription_created(data, db)
        elif event_type == 'subscription.updated':
            await handle_subscription_updated(data, db)
        elif event_type == 'subscription.deleted' or event_type == 'subscription.cancelled':
            await handle_subscription_deleted(data, db)
        elif event_type == 'subscription.trial_will_end':
            await handle_trial_will_end(data, db)
        elif event_type == 'invoice.payment_succeeded' or event_type == 'payment.succeeded':
            await handle_payment_succeeded(data, db)
        elif event_type == 'invoice.payment_failed' or event_type == 'payment.failed':
            await handle_payment_failed(data, db)
        else:
            logger.warning(f"Unhandled subscription event type: {event_type}")

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error handling subscription webhook {event_type}: {e}")
        raise HTTPException(status_code=500, detail="Error processing webhook")


# User event handlers
async def handle_user_created(data: Dict[str, Any], db: Session):
    """Handle user creation from Clerk"""
    clerk_id = data.get('id')
    email_addresses = data.get('email_addresses', [])
    
    if not clerk_id or not email_addresses:
        logger.error("Missing required user data in webhook")
        return
    
    primary_email = next((e for e in email_addresses if e.get('id') == data.get('primary_email_address_id')), None)
    if not primary_email:
        primary_email = email_addresses[0]
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if existing_user:
        logger.info(f"User {clerk_id} already exists, skipping creation")
        return
    
    # Create new user
    user = User(
        clerk_id=clerk_id,
        email=primary_email.get('email_address'),
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        username=data.get('username'),
        avatar_url=data.get('image_url'),
        email_verified=primary_email.get('verification', {}).get('status') == 'verified',
        phone_verified=bool(data.get('phone_numbers', [])),
        two_factor_enabled=data.get('two_factor_enabled', False),
        system_role='system_user',
        is_active=True
    )
    
    db.add(user)
    db.commit()
    logger.info(f"Created user {clerk_id}")


async def handle_user_updated(data: Dict[str, Any], db: Session):
    """Handle user updates from Clerk"""
    clerk_id = data.get('id')
    
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        logger.warning(f"User {clerk_id} not found for update")
        return
    
    # Update user fields
    email_addresses = data.get('email_addresses', [])
    if email_addresses:
        primary_email = next((e for e in email_addresses if e.get('id') == data.get('primary_email_address_id')), None)
        if primary_email:
            user.email = primary_email.get('email_address')
            user.email_verified = primary_email.get('verification', {}).get('status') == 'verified'
    
    user.first_name = data.get('first_name')
    user.last_name = data.get('last_name')
    user.username = data.get('username')
    user.avatar_url = data.get('image_url')
    user.phone_verified = bool(data.get('phone_numbers', []))
    user.two_factor_enabled = data.get('two_factor_enabled', False)
    
    db.commit()
    logger.info(f"Updated user {clerk_id}")


async def handle_user_deleted(data: Dict[str, Any], db: Session):
    """Handle user deletion from Clerk"""
    clerk_id = data.get('id')
    
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        logger.warning(f"User {clerk_id} not found for deletion")
        return
    
    # Soft delete the user
    user.soft_delete()
    db.commit()
    logger.info(f"Soft deleted user {clerk_id}")


# Organization event handlers
async def handle_organization_created(data: Dict[str, Any], db: Session):
    """Handle organization creation from Clerk"""
    clerk_id = data.get('id')
    name = data.get('name')
    
    if not clerk_id or not name:
        logger.error("Missing required organization data in webhook")
        return
    
    # Check if organization already exists
    existing_org = db.query(Organization).filter(Organization.clerk_id == clerk_id).first()
    if existing_org:
        logger.info(f"Organization {clerk_id} already exists, skipping creation")
        return
    
    # Create new organization
    org = Organization(
        clerk_id=clerk_id,
        name=name,
        slug=data.get('slug'),
        subscription_tier='free',
        max_users=5,
        storage_quota_gb=10.0,
        storage_used_gb=0.0,
        data_retention_days=365,
        is_verified=False,
        requires_2fa=False,
        is_active=True
    )
    
    db.add(org)
    db.commit()
    logger.info(f"Created organization {clerk_id}")


async def handle_organization_updated(data: Dict[str, Any], db: Session):
    """Handle organization updates from Clerk"""
    clerk_id = data.get('id')
    
    org = db.query(Organization).filter(Organization.clerk_id == clerk_id).first()
    if not org:
        logger.warning(f"Organization {clerk_id} not found for update")
        return
    
    # Update organization fields
    org.name = data.get('name', org.name)
    org.slug = data.get('slug', org.slug)
    
    db.commit()
    logger.info(f"Updated organization {clerk_id}")


async def handle_organization_deleted(data: Dict[str, Any], db: Session):
    """Handle organization deletion from Clerk"""
    clerk_id = data.get('id')
    
    org = db.query(Organization).filter(Organization.clerk_id == clerk_id).first()
    if not org:
        logger.warning(f"Organization {clerk_id} not found for deletion")
        return
    
    # Soft delete the organization
    org.soft_delete()
    db.commit()
    logger.info(f"Soft deleted organization {clerk_id}")


# Membership event handlers
async def handle_membership_created(data: Dict[str, Any], db: Session):
    """Handle organization membership creation"""
    # Implementation depends on your membership model structure
    logger.info("Membership created webhook received")


async def handle_membership_updated(data: Dict[str, Any], db: Session):
    """Handle organization membership updates"""
    # Implementation depends on your membership model structure
    logger.info("Membership updated webhook received")


async def handle_membership_deleted(data: Dict[str, Any], db: Session):
    """Handle organization membership deletion"""
    # Implementation depends on your membership model structure
    logger.info("Membership deleted webhook received")


# Subscription event handlers
async def handle_subscription_created(data: Dict[str, Any], db: Session):
    """Handle subscription creation from Clerk Billing"""
    clerk_subscription_id = data.get('id')
    organization_id = data.get('organization_id')  # Clerk Billing links to org directly

    # Find organization by Clerk organization ID
    org = db.query(Organization).filter(Organization.clerk_id == organization_id).first()
    if not org:
        logger.error(f"Organization not found for Clerk org ID {organization_id}")
        return

    # Extract subscription details from Clerk Billing format
    plan_tier = data.get('plan', {}).get('name', 'solo').lower()  # solo, growth, enterprise
    billing_interval = data.get('interval', 'month')  # month or year
    amount = data.get('amount', 0)  # Already in dollars for Clerk Billing
    currency = data.get('currency', 'USD').upper()
    status = data.get('status', 'incomplete')  # active, trialing, past_due, canceled, etc.

    # Map plan tier to our internal plan names
    plan_mapping = {
        'solo': SubscriptionPlan.SOLO.value,
        'growth': SubscriptionPlan.GROWTH.value,
        'enterprise': SubscriptionPlan.ENTERPRISE.value,
        'solo_dealmaker': SubscriptionPlan.SOLO.value,
        'growth_firm': SubscriptionPlan.GROWTH.value,
    }

    plan = plan_mapping.get(plan_tier, SubscriptionPlan.SOLO.value)
    plan_config = Subscription.get_plan_config(plan)

    # Extract trial information
    trial_start = data.get('trial_start')
    trial_end = data.get('trial_end')
    is_trialing = status == 'trialing'

    # Create subscription
    subscription = Subscription(
        organization_id=org.id,
        clerk_subscription_id=clerk_subscription_id,
        clerk_customer_id=organization_id,  # Use org ID as customer ID
        plan=plan,
        plan_name=plan_config.get('name', plan.title()),
        billing_interval=billing_interval,
        amount=amount,
        currency=currency,
        status=status,
        max_users=plan_config.get('max_users', 5),
        max_deals=plan_config.get('max_deals'),
        storage_quota_gb=plan_config.get('storage_quota_gb', 10),
        api_requests_per_month=plan_config.get('api_requests_per_month'),
        features=plan_config.get('features', {}),
        trial_start=datetime.fromtimestamp(trial_start) if trial_start else None,
        trial_end=datetime.fromtimestamp(trial_end) if trial_end else None,
    )

    db.add(subscription)

    # Update organization subscription tier
    org.subscription_tier = plan
    org.max_users = subscription.max_users
    org.max_deals = subscription.max_deals
    org.storage_quota_gb = subscription.storage_quota_gb

    db.commit()
    logger.info(f"Created subscription {clerk_subscription_id} for organization {org.id} (plan: {plan}, interval: {billing_interval}, trial: {is_trialing})")


async def handle_subscription_updated(data: Dict[str, Any], db: Session):
    """Handle subscription updates from Clerk Billing"""
    clerk_subscription_id = data.get('id')

    subscription = db.query(Subscription).filter(
        Subscription.clerk_subscription_id == clerk_subscription_id
    ).first()

    if not subscription:
        logger.warning(f"Subscription {clerk_subscription_id} not found for update")
        return

    # Update subscription status and other fields
    old_status = subscription.status
    subscription.status = data.get('status', subscription.status)

    # Handle plan changes (upgrades/downgrades)
    plan_tier = data.get('plan', {}).get('name', '').lower()
    if plan_tier:
        plan_mapping = {
            'solo': SubscriptionPlan.SOLO.value,
            'growth': SubscriptionPlan.GROWTH.value,
            'enterprise': SubscriptionPlan.ENTERPRISE.value,
            'solo_dealmaker': SubscriptionPlan.SOLO.value,
            'growth_firm': SubscriptionPlan.GROWTH.value,
        }
        new_plan = plan_mapping.get(plan_tier)
        if new_plan and new_plan != subscription.plan:
            old_plan = subscription.plan
            subscription.plan = new_plan
            plan_config = Subscription.get_plan_config(new_plan)
            subscription.plan_name = plan_config.get('name', new_plan.title())
            subscription.max_users = plan_config.get('max_users', 5)
            subscription.max_deals = plan_config.get('max_deals')
            subscription.storage_quota_gb = plan_config.get('storage_quota_gb', 10)
            subscription.features = plan_config.get('features', {})

            # Update organization
            org = subscription.organization
            org.subscription_tier = new_plan
            org.max_users = subscription.max_users
            org.max_deals = subscription.max_deals
            org.storage_quota_gb = subscription.storage_quota_gb

            logger.info(f"Subscription {clerk_subscription_id} plan changed from {old_plan} to {new_plan}")

    # Update billing interval if changed
    billing_interval = data.get('interval')
    if billing_interval:
        subscription.billing_interval = billing_interval

    # Update amount if changed
    amount = data.get('amount')
    if amount is not None:
        subscription.amount = amount

    # Update period dates if available
    current_period_start = data.get('current_period_start')
    if current_period_start:
        subscription.current_period_start = datetime.fromtimestamp(current_period_start)

    current_period_end = data.get('current_period_end')
    if current_period_end:
        subscription.current_period_end = datetime.fromtimestamp(current_period_end)

    # Update trial dates if available
    trial_start = data.get('trial_start')
    if trial_start:
        subscription.trial_start = datetime.fromtimestamp(trial_start)

    trial_end = data.get('trial_end')
    if trial_end:
        subscription.trial_end = datetime.fromtimestamp(trial_end)

    db.commit()
    logger.info(f"Updated subscription {clerk_subscription_id} (status: {old_status} -> {subscription.status})")


async def handle_subscription_deleted(data: Dict[str, Any], db: Session):
    """Handle subscription cancellation from Clerk"""
    clerk_subscription_id = data.get('id')
    
    subscription = db.query(Subscription).filter(
        Subscription.clerk_subscription_id == clerk_subscription_id
    ).first()
    
    if not subscription:
        logger.warning(f"Subscription {clerk_subscription_id} not found for deletion")
        return
    
    # Cancel the subscription
    subscription.cancel("Canceled via Clerk")
    
    # Revert organization to free tier
    org = subscription.organization
    org.subscription_tier = 'free'
    org.max_users = 5
    org.max_deals = None
    org.storage_quota_gb = 10.0
    
    db.commit()
    logger.info(f"Canceled subscription {clerk_subscription_id}")


async def handle_payment_succeeded(data: Dict[str, Any], db: Session):
    """Handle successful payment from Clerk"""
    subscription_id = data.get('subscription')
    
    subscription = db.query(Subscription).filter(
        Subscription.clerk_subscription_id == subscription_id
    ).first()
    
    if not subscription:
        logger.warning(f"Subscription {subscription_id} not found for payment update")
        return
    
    # Update last payment date
    subscription.last_payment_date = datetime.utcnow()
    subscription.status = SubscriptionStatus.ACTIVE.value
    
    db.commit()
    logger.info(f"Payment succeeded for subscription {subscription_id}")


async def handle_payment_failed(data: Dict[str, Any], db: Session):
    """Handle failed payment from Clerk"""
    subscription_id = data.get('subscription')

    subscription = db.query(Subscription).filter(
        Subscription.clerk_subscription_id == subscription_id
    ).first()

    if not subscription:
        logger.warning(f"Subscription {subscription_id} not found for payment failure")
        return

    # Update subscription status
    subscription.status = SubscriptionStatus.PAST_DUE.value

    db.commit()
    logger.info(f"Payment failed for subscription {subscription_id}")


async def handle_trial_will_end(data: Dict[str, Any], db: Session):
    """Handle trial ending soon notification from Clerk Billing"""
    clerk_subscription_id = data.get('id')

    subscription = db.query(Subscription).filter(
        Subscription.clerk_subscription_id == clerk_subscription_id
    ).first()

    if not subscription:
        logger.warning(f"Subscription {clerk_subscription_id} not found for trial ending")
        return

    # Log trial ending (can be used to send notification emails)
    trial_end_date = subscription.trial_end
    logger.info(f"Trial ending soon for subscription {clerk_subscription_id} (ends: {trial_end_date})")

    # You can add email notification logic here
    # For example:
    # - Send email to organization admin
    # - Show in-app notification
    # - Update UI to show trial expiration warning

    # Optional: Update a field to track that we've sent the notification
    # subscription.trial_ending_notified = True
    # db.commit()
