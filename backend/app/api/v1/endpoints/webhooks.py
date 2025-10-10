"""Webhook handlers for external services"""

from fastapi import APIRouter, Request, HTTPException, status, Header
from typing import Optional
import structlog

from app.services.stripe_service import StripeService
from app.core.config import settings


logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/stripe")
async def handle_stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature")
):
    """
    Handle Stripe webhook events.

    This endpoint processes webhook events from Stripe including:
    - Subscription lifecycle events (created, updated, deleted)
    - Payment events (succeeded, failed)
    - Trial ending notifications
    - Customer updates

    Webhook signature verification ensures the request is from Stripe.
    """
    try:
        # Get raw payload
        payload = await request.body()
        payload_str = payload.decode("utf-8")

        if not stripe_signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing Stripe signature"
            )

        stripe_service = StripeService()
        result = await stripe_service.handle_webhook(payload_str, stripe_signature)

        logger.info(
            "Stripe webhook processed",
            event_type=result.get("event_type")
        )

        return {"status": "success"}

    except ValueError as e:
        logger.error("Invalid webhook signature", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature"
        )
    except Exception as e:
        logger.error("Webhook processing failed", error=str(e))
        # Return 200 to prevent Stripe from retrying
        # Log the error for investigation
        return {"status": "error", "message": "Processing failed but acknowledged"}


@router.post("/clerk")
async def handle_clerk_webhook(
    request: Request,
    svix_id: Optional[str] = Header(None),
    svix_timestamp: Optional[str] = Header(None),
    svix_signature: Optional[str] = Header(None)
):
    """
    Handle Clerk authentication webhook events.

    This endpoint processes webhook events from Clerk including:
    - User created/updated/deleted
    - Organization created/updated/deleted
    - Membership changes
    - Session events

    Uses Svix for webhook verification.
    """
    try:
        # Get raw payload
        payload = await request.body()
        payload_str = payload.decode("utf-8")

        # Verify webhook if secret is configured
        if settings.CLERK_WEBHOOK_SECRET:
            from svix import Webhook

            headers = {
                "svix-id": svix_id,
                "svix-timestamp": svix_timestamp,
                "svix-signature": svix_signature
            }

            wh = Webhook(settings.CLERK_WEBHOOK_SECRET)
            try:
                event = wh.verify(payload_str, headers)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid webhook signature"
                )
        else:
            import json
            event = json.loads(payload_str)

        # Process different event types
        event_type = event.get("type")
        data = event.get("data")

        if event_type == "user.created":
            await _handle_user_created(data)
        elif event_type == "user.updated":
            await _handle_user_updated(data)
        elif event_type == "user.deleted":
            await _handle_user_deleted(data)
        elif event_type == "organization.created":
            await _handle_organization_created(data)
        elif event_type == "organization.updated":
            await _handle_organization_updated(data)
        elif event_type == "organizationMembership.created":
            await _handle_membership_created(data)
        elif event_type == "organizationMembership.deleted":
            await _handle_membership_deleted(data)

        logger.info(
            "Clerk webhook processed",
            event_type=event_type,
            event_id=event.get("id")
        )

        return {"status": "success"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Clerk webhook processing failed", error=str(e))
        # Return 200 to prevent retries
        return {"status": "error", "message": "Processing failed but acknowledged"}


async def _handle_user_created(data: dict):
    """Handle user creation from Clerk"""
    from app.core.database import AsyncSessionLocal
    from app.models.user import User

    async with AsyncSessionLocal() as session:
        user = User(
            clerk_user_id=data.get("id"),
            email=data.get("email_addresses", [{}])[0].get("email_address"),
            full_name=f"{data.get('first_name', '')} {data.get('last_name', '')}".strip(),
            organization_id=data.get("organization_id"),
            role="member"
        )
        session.add(user)
        await session.commit()

    logger.info("User created from Clerk webhook", clerk_user_id=data.get("id"))


async def _handle_user_updated(data: dict):
    """Handle user update from Clerk"""
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        await session.execute(
            """UPDATE users
               SET email = :email,
                   full_name = :full_name,
                   updated_at = NOW()
               WHERE clerk_user_id = :clerk_id""",
            {
                "email": data.get("email_addresses", [{}])[0].get("email_address"),
                "full_name": f"{data.get('first_name', '')} {data.get('last_name', '')}".strip(),
                "clerk_id": data.get("id")
            }
        )
        await session.commit()

    logger.info("User updated from Clerk webhook", clerk_user_id=data.get("id"))


async def _handle_user_deleted(data: dict):
    """Handle user deletion from Clerk"""
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        await session.execute(
            """UPDATE users
               SET is_active = FALSE,
                   updated_at = NOW()
               WHERE clerk_user_id = :clerk_id""",
            {"clerk_id": data.get("id")}
        )
        await session.commit()

    logger.info("User deactivated from Clerk webhook", clerk_user_id=data.get("id"))


async def _handle_organization_created(data: dict):
    """Handle organization creation from Clerk"""
    from app.core.database import AsyncSessionLocal
    from app.models.organization import Organization

    async with AsyncSessionLocal() as session:
        org = Organization(
            clerk_org_id=data.get("id"),
            name=data.get("name"),
            domain=data.get("slug")
        )
        session.add(org)
        await session.commit()

    logger.info("Organization created from Clerk webhook", clerk_org_id=data.get("id"))


async def _handle_organization_updated(data: dict):
    """Handle organization update from Clerk"""
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        await session.execute(
            """UPDATE organizations
               SET name = :name,
                   updated_at = NOW()
               WHERE clerk_org_id = :clerk_id""",
            {
                "name": data.get("name"),
                "clerk_id": data.get("id")
            }
        )
        await session.commit()

    logger.info("Organization updated from Clerk webhook", clerk_org_id=data.get("id"))


async def _handle_membership_created(data: dict):
    """Handle organization membership creation"""
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        # Update user's organization
        await session.execute(
            """UPDATE users
               SET organization_id = (
                   SELECT id FROM organizations WHERE clerk_org_id = :org_id
               ),
               role = :role,
               updated_at = NOW()
               WHERE clerk_user_id = :user_id""",
            {
                "org_id": data.get("organization").get("id"),
                "role": data.get("role", "member"),
                "user_id": data.get("public_user_data").get("user_id")
            }
        )
        await session.commit()

    logger.info(
        "Membership created from Clerk webhook",
        user_id=data.get("public_user_data").get("user_id"),
        org_id=data.get("organization").get("id")
    )


async def _handle_membership_deleted(data: dict):
    """Handle organization membership deletion"""
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        # Remove user's organization
        await session.execute(
            """UPDATE users
               SET organization_id = NULL,
                   updated_at = NOW()
               WHERE clerk_user_id = :user_id""",
            {"user_id": data.get("public_user_data").get("user_id")}
        )
        await session.commit()

    logger.info(
        "Membership deleted from Clerk webhook",
        user_id=data.get("public_user_data").get("user_id")
    )


@router.post("/render")
async def handle_render_webhook(
    request: Request,
    x_render_signature: Optional[str] = Header(None, alias="x-render-signature")
):
    """
    Handle Render deployment webhook events.

    This endpoint processes deployment notifications from Render including:
    - Deploy started
    - Deploy succeeded
    - Deploy failed
    - Service suspended/resumed
    """
    try:
        payload = await request.body()
        payload_str = payload.decode("utf-8")

        import json
        event = json.loads(payload_str)

        event_type = event.get("type")

        if event_type == "deploy.created":
            logger.info("Deployment started", service=event.get("service"))
        elif event_type == "deploy.updated":
            status = event.get("deploy", {}).get("status")
            if status == "live":
                logger.info("Deployment succeeded", service=event.get("service"))
                # Could trigger post-deployment tasks here
            elif status == "failed":
                logger.error("Deployment failed", service=event.get("service"))
                # Could send alerts here

        return {"status": "success"}

    except Exception as e:
        logger.error("Render webhook processing failed", error=str(e))
        return {"status": "error", "message": "Processing failed but acknowledged"}