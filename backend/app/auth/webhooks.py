"""
Clerk Webhook Handler
Processes webhook events from Clerk for user and organization management
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, Depends, Header, status
from sqlalchemy.orm import Session
from svix.webhooks import Webhook, WebhookVerificationError
from app.core.database import get_db
from app.models.user import User, OrganizationMembership
from app.models.organization import Organization
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Configuration
CLERK_WEBHOOK_SECRET = os.getenv("CLERK_WEBHOOK_SECRET")

if not CLERK_WEBHOOK_SECRET:
    logger.warning("CLERK_WEBHOOK_SECRET not set. Webhook verification will fail.")

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


class WebhookEvent(BaseModel):
    """Base webhook event model"""
    type: str
    object: str
    data: Dict[str, Any]
    created_at: datetime


class UserEventData(BaseModel):
    """User-related webhook event data"""
    id: str
    email_addresses: list
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    public_metadata: Dict[str, Any] = Field(default_factory=dict)
    private_metadata: Dict[str, Any] = Field(default_factory=dict)


class OrganizationEventData(BaseModel):
    """Organization-related webhook event data"""
    id: str
    name: str
    slug: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    max_allowed_memberships: int = 5
    public_metadata: Dict[str, Any] = Field(default_factory=dict)
    private_metadata: Dict[str, Any] = Field(default_factory=dict)


class MembershipEventData(BaseModel):
    """Organization membership event data"""
    id: str
    user_id: str
    organization_id: str
    role: str
    created_at: datetime
    updated_at: datetime
    public_metadata: Dict[str, Any] = Field(default_factory=dict)


class WebhookHandler:
    """Handler for processing Clerk webhook events"""

    def __init__(self):
        self.webhook_secret = CLERK_WEBHOOK_SECRET
        self._webhook = None

    @property
    def webhook(self):
        """Lazy initialization of Webhook to avoid import-time crashes"""
        if self._webhook is None and self.webhook_secret:
            try:
                self._webhook = Webhook(self.webhook_secret)
            except Exception as e:
                logger.error(f"Failed to initialize webhook: {e}")
        return self._webhook

    def verify_webhook(self, payload: bytes, headers: Dict[str, str]) -> Dict[str, Any]:
        """Verify webhook signature and return parsed payload"""
        if not self.webhook:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Webhook secret not configured"
            )

        try:
            # Svix headers format
            svix_headers = {
                "svix-id": headers.get("svix-id"),
                "svix-signature": headers.get("svix-signature"),
                "svix-timestamp": headers.get("svix-timestamp")
            }

            # Verify and parse the webhook
            verified_payload = self.webhook.verify(payload, svix_headers)
            return verified_payload
        except WebhookVerificationError as e:
            logger.error(f"Webhook verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error processing webhook: {str(e)}"
            )

    async def handle_user_created(self, data: Dict[str, Any], db: Session):
        """Handle user.created event"""
        try:
            # Extract primary email
            primary_email = None
            for email in data.get("email_addresses", []):
                if email.get("id") == data.get("primary_email_address_id"):
                    primary_email = email.get("email_address")
                    break

            # Create or update user in our database
            user = db.query(User).filter(User.clerk_id == data["id"]).first()

            if not user:
                user = User(
                    clerk_id=data["id"],
                    email=primary_email,
                    first_name=data.get("first_name"),
                    last_name=data.get("last_name"),
                    username=data.get("username"),
                    image_url=data.get("image_url"),
                    created_at=datetime.fromisoformat(data["created_at"].rstrip("Z")),
                    metadata=data.get("public_metadata", {})
                )
                db.add(user)
            else:
                # Update existing user
                user.email = primary_email
                user.first_name = data.get("first_name")
                user.last_name = data.get("last_name")
                user.username = data.get("username")
                user.image_url = data.get("image_url")
                user.metadata = data.get("public_metadata", {})

            db.commit()
            logger.info(f"User created/updated: {data['id']}")

        except Exception as e:
            logger.error(f"Error handling user.created: {e}")
            db.rollback()
            raise

    async def handle_user_updated(self, data: Dict[str, Any], db: Session):
        """Handle user.updated event"""
        await self.handle_user_created(data, db)  # Same logic for updates

    async def handle_user_deleted(self, data: Dict[str, Any], db: Session):
        """Handle user.deleted event"""
        try:
            user = db.query(User).filter(User.clerk_id == data["id"]).first()
            if user:
                # Soft delete or mark as inactive
                user.is_active = False
                user.deleted_at = datetime.utcnow()
                db.commit()
                logger.info(f"User deleted: {data['id']}")
        except Exception as e:
            logger.error(f"Error handling user.deleted: {e}")
            db.rollback()
            raise

    async def handle_organization_created(self, data: Dict[str, Any], db: Session):
        """Handle organization.created event"""
        try:
            org = db.query(Organization).filter(Organization.clerk_id == data["id"]).first()

            if not org:
                org = Organization(
                    clerk_id=data["id"],
                    name=data["name"],
                    slug=data.get("slug"),
                    created_at=datetime.fromisoformat(data["created_at"].rstrip("Z")),
                    max_allowed_memberships=data.get("max_allowed_memberships", 5),
                    metadata=data.get("public_metadata", {}),
                    settings=data.get("private_metadata", {})
                )
                db.add(org)
            else:
                # Update existing organization
                org.name = data["name"]
                org.slug = data.get("slug")
                org.max_allowed_memberships = data.get("max_allowed_memberships", 5)
                org.metadata = data.get("public_metadata", {})
                org.settings = data.get("private_metadata", {})

            db.commit()
            logger.info(f"Organization created/updated: {data['id']}")

        except Exception as e:
            logger.error(f"Error handling organization.created: {e}")
            db.rollback()
            raise

    async def handle_organization_updated(self, data: Dict[str, Any], db: Session):
        """Handle organization.updated event"""
        await self.handle_organization_created(data, db)

    async def handle_organization_deleted(self, data: Dict[str, Any], db: Session):
        """Handle organization.deleted event"""
        try:
            org = db.query(Organization).filter(Organization.clerk_id == data["id"]).first()
            if org:
                # Soft delete or mark as inactive
                org.is_active = False
                org.deleted_at = datetime.utcnow()
                db.commit()
                logger.info(f"Organization deleted: {data['id']}")
        except Exception as e:
            logger.error(f"Error handling organization.deleted: {e}")
            db.rollback()
            raise

    async def handle_organization_membership_created(self, data: Dict[str, Any], db: Session):
        """Handle organizationMembership.created event"""
        try:
            membership = db.query(OrganizationMembership).filter(
                OrganizationMembership.clerk_id == data["id"]
            ).first()

            if not membership:
                # Get user and org from database
                user = db.query(User).filter(User.clerk_id == data["user_id"]).first()
                org = db.query(Organization).filter(Organization.clerk_id == data["organization_id"]).first()

                if user and org:
                    membership = OrganizationMembership(
                        clerk_id=data["id"],
                        user_id=user.id,
                        organization_id=org.id,
                        role=data.get("role", "member"),
                        created_at=datetime.fromisoformat(data["created_at"].rstrip("Z")),
                        metadata=data.get("public_metadata", {})
                    )
                    db.add(membership)
                    db.commit()
                    logger.info(f"Membership created: {data['id']}")
                else:
                    logger.warning(f"User or Org not found for membership: {data['id']}")

        except Exception as e:
            logger.error(f"Error handling organizationMembership.created: {e}")
            db.rollback()
            raise

    async def handle_organization_membership_deleted(self, data: Dict[str, Any], db: Session):
        """Handle organizationMembership.deleted event"""
        try:
            membership = db.query(OrganizationMembership).filter(
                OrganizationMembership.clerk_id == data["id"]
            ).first()

            if membership:
                db.delete(membership)
                db.commit()
                logger.info(f"Membership deleted: {data['id']}")

        except Exception as e:
            logger.error(f"Error handling organizationMembership.deleted: {e}")
            db.rollback()
            raise

    async def handle_organization_invitation_created(self, data: Dict[str, Any], db: Session):
        """Handle organizationInvitation.created event"""
        # Log the invitation for tracking
        logger.info(f"Organization invitation created: {data.get('id')}")
        # Additional logic for tracking invitations can be added here

    async def handle_session_created(self, data: Dict[str, Any], db: Session):
        """Handle session.created event for audit logging"""
        try:
            user_id = data.get("user_id")
            if user_id:
                user = db.query(User).filter(User.clerk_id == user_id).first()
                if user:
                    user.last_sign_in_at = datetime.utcnow()
                    db.commit()
                    logger.info(f"User session created: {user_id}")

        except Exception as e:
            logger.error(f"Error handling session.created: {e}")
            db.rollback()


# Create webhook handler instance
webhook_handler = WebhookHandler()


@router.post("/clerk")
async def clerk_webhook(
    request: Request,
    db: Session = Depends(get_db),
    svix_id: Optional[str] = Header(None),
    svix_signature: Optional[str] = Header(None),
    svix_timestamp: Optional[str] = Header(None)
):
    """
    Handle incoming webhooks from Clerk
    """
    # Get raw body
    body = await request.body()

    # Build headers dict
    headers = {
        "svix-id": svix_id,
        "svix-signature": svix_signature,
        "svix-timestamp": svix_timestamp
    }

    # Verify webhook signature
    try:
        payload = webhook_handler.verify_webhook(body, headers)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Webhook verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook payload"
        )

    # Process the webhook event
    event_type = payload.get("type")
    event_data = payload.get("data")

    logger.info(f"Processing webhook event: {event_type}")

    try:
        # Route to appropriate handler based on event type
        if event_type == "user.created":
            await webhook_handler.handle_user_created(event_data, db)
        elif event_type == "user.updated":
            await webhook_handler.handle_user_updated(event_data, db)
        elif event_type == "user.deleted":
            await webhook_handler.handle_user_deleted(event_data, db)
        elif event_type == "organization.created":
            await webhook_handler.handle_organization_created(event_data, db)
        elif event_type == "organization.updated":
            await webhook_handler.handle_organization_updated(event_data, db)
        elif event_type == "organization.deleted":
            await webhook_handler.handle_organization_deleted(event_data, db)
        elif event_type == "organizationMembership.created":
            await webhook_handler.handle_organization_membership_created(event_data, db)
        elif event_type == "organizationMembership.deleted":
            await webhook_handler.handle_organization_membership_deleted(event_data, db)
        elif event_type == "organizationInvitation.created":
            await webhook_handler.handle_organization_invitation_created(event_data, db)
        elif event_type == "session.created":
            await webhook_handler.handle_session_created(event_data, db)
        else:
            logger.info(f"Unhandled webhook event type: {event_type}")

        return {"status": "success", "event_type": event_type}

    except Exception as e:
        logger.error(f"Error processing webhook event {event_type}: {e}")
        # Return success to avoid retries for processing errors
        return {"status": "error", "event_type": event_type, "error": str(e)}


@router.get("/webhook-test")
async def webhook_test():
    """Test endpoint to verify webhook setup"""
    return {
        "status": "ok",
        "webhook_secret_configured": bool(CLERK_WEBHOOK_SECRET),
        "timestamp": datetime.utcnow()
    }