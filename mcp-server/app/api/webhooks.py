"""
BMAD v6 MCP Server Webhook Endpoints
Real-time integration endpoints for external services
"""

from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
import json
import hmac
import hashlib
import logging
from typing import Dict, Any

from app.db.init_db import get_db
from app.crud.crud_project import crud_project
from app.crud.crud_deal import crud_deal
from app.services.security_manager import SecurityManager
from app.services.state_manager import StateManager
from app.services.workflow_engine import WorkflowEngine
from app.core.exceptions import ValidationException, IntegrationException

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# Initialize services (would be dependency injected in production)
security_manager = SecurityManager()
state_manager = StateManager()
workflow_engine = WorkflowEngine()

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify webhook signature for security."""
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected_signature}", signature)

@router.post("/clerk")
async def clerk_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle Clerk authentication webhooks."""
    try:
        # Get raw payload
        payload = await request.body()
        
        # Verify signature (in production, use actual Clerk webhook secret)
        signature = request.headers.get("svix-signature", "")
        webhook_secret = "clerk_webhook_secret"  # From environment
        
        if not verify_webhook_signature(payload, signature, webhook_secret):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse webhook data
        webhook_data = json.loads(payload)
        event_type = webhook_data.get("type")
        user_data = webhook_data.get("data", {})
        
        logger.info(f"Received Clerk webhook: {event_type}")
        
        # Handle different event types
        if event_type == "user.created":
            background_tasks.add_task(handle_user_created, user_data, db)
        elif event_type == "user.updated":
            background_tasks.add_task(handle_user_updated, user_data, db)
        elif event_type == "user.deleted":
            background_tasks.add_task(handle_user_deleted, user_data, db)
        
        return {"success": True, "message": "Webhook processed"}
        
    except Exception as e:
        logger.error(f"Clerk webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle Stripe payment webhooks."""
    try:
        # Get raw payload
        payload = await request.body()
        
        # Verify signature
        signature = request.headers.get("stripe-signature", "")
        webhook_secret = "stripe_webhook_secret"  # From environment
        
        if not verify_webhook_signature(payload, signature, webhook_secret):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse webhook data
        webhook_data = json.loads(payload)
        event_type = webhook_data.get("type")
        event_data = webhook_data.get("data", {}).get("object", {})
        
        logger.info(f"Received Stripe webhook: {event_type}")
        
        # Handle different event types
        if event_type == "payment_intent.succeeded":
            background_tasks.add_task(handle_payment_succeeded, event_data, db)
        elif event_type == "subscription.created":
            background_tasks.add_task(handle_subscription_created, event_data, db)
        elif event_type == "subscription.updated":
            background_tasks.add_task(handle_subscription_updated, event_data, db)
        elif event_type == "subscription.deleted":
            background_tasks.add_task(handle_subscription_cancelled, event_data, db)
        
        return {"success": True, "message": "Webhook processed"}
        
    except Exception as e:
        logger.error(f"Stripe webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.post("/project-update")
async def project_update_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle project update webhooks from external systems."""
    try:
        # Get payload
        webhook_data = await request.json()
        
        project_id = webhook_data.get("project_id")
        update_type = webhook_data.get("update_type")
        data = webhook_data.get("data", {})
        
        if not project_id or not update_type:
            raise ValidationException("Missing required fields: project_id, update_type")
        
        logger.info(f"Received project update webhook: {project_id} - {update_type}")
        
        # Handle different update types
        if update_type == "story_completed":
            background_tasks.add_task(handle_story_completed, project_id, data, db)
        elif update_type == "epic_completed":
            background_tasks.add_task(handle_epic_completed, project_id, data, db)
        elif update_type == "phase_transition":
            background_tasks.add_task(handle_phase_transition, project_id, data, db)
        elif update_type == "deal_status_change":
            background_tasks.add_task(handle_deal_status_change, project_id, data, db)
        
        return {"success": True, "message": "Project update processed"}
        
    except Exception as e:
        logger.error(f"Project update webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.post("/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle GitHub webhooks for code repository events."""
    try:
        # Get payload
        payload = await request.body()
        
        # Verify signature
        signature = request.headers.get("x-hub-signature-256", "")
        webhook_secret = "github_webhook_secret"  # From environment
        
        if not verify_webhook_signature(payload, signature, webhook_secret):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse webhook data
        webhook_data = json.loads(payload)
        event_type = request.headers.get("x-github-event")
        
        logger.info(f"Received GitHub webhook: {event_type}")
        
        # Handle different event types
        if event_type == "push":
            background_tasks.add_task(handle_github_push, webhook_data, db)
        elif event_type == "pull_request":
            background_tasks.add_task(handle_github_pr, webhook_data, db)
        elif event_type == "issues":
            background_tasks.add_task(handle_github_issue, webhook_data, db)
        
        return {"success": True, "message": "GitHub webhook processed"}
        
    except Exception as e:
        logger.error(f"GitHub webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.post("/slack")
async def slack_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Handle Slack webhooks for team notifications."""
    try:
        # Get payload
        webhook_data = await request.json()
        
        # Handle Slack URL verification
        if webhook_data.get("type") == "url_verification":
            return {"challenge": webhook_data.get("challenge")}
        
        event_type = webhook_data.get("event", {}).get("type")
        
        logger.info(f"Received Slack webhook: {event_type}")
        
        # Handle different event types
        if event_type == "message":
            background_tasks.add_task(handle_slack_message, webhook_data, db)
        elif event_type == "app_mention":
            background_tasks.add_task(handle_slack_mention, webhook_data, db)
        
        return {"success": True, "message": "Slack webhook processed"}
        
    except Exception as e:
        logger.error(f"Slack webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

# Background task handlers

async def handle_user_created(user_data: Dict[str, Any], db: Session):
    """Handle new user creation from Clerk."""
    try:
        user_id = user_data.get("id")
        email = user_data.get("email_addresses", [{}])[0].get("email_address")
        
        logger.info(f"Processing new user: {user_id} - {email}")
        
        # Create default project for new user
        if user_id:
            project_id = f"user-{user_id}-onboarding"
            crud_project.create_project(
                db=db,
                project_id=project_id,
                name="User Onboarding",
                description="Default onboarding project for new user",
                phase=1,
                scale_level=0
            )
            
            # Trigger onboarding workflow
            await workflow_engine.execute_workflow(
                workflow_name="user-onboarding",
                context={"user_id": user_id, "email": email},
                project_id=project_id
            )
        
    except Exception as e:
        logger.error(f"Error handling user creation: {str(e)}")

async def handle_user_updated(user_data: Dict[str, Any], db: Session):
    """Handle user updates from Clerk."""
    try:
        user_id = user_data.get("id")
        logger.info(f"Processing user update: {user_id}")
        
        # Update user-related projects or settings
        # Implementation depends on specific requirements
        
    except Exception as e:
        logger.error(f"Error handling user update: {str(e)}")

async def handle_user_deleted(user_data: Dict[str, Any], db: Session):
    """Handle user deletion from Clerk."""
    try:
        user_id = user_data.get("id")
        logger.info(f"Processing user deletion: {user_id}")
        
        # Clean up user-related data
        # Implementation depends on data retention policies
        
    except Exception as e:
        logger.error(f"Error handling user deletion: {str(e)}")

async def handle_payment_succeeded(payment_data: Dict[str, Any], db: Session):
    """Handle successful payment from Stripe."""
    try:
        payment_intent_id = payment_data.get("id")
        amount = payment_data.get("amount")
        customer_id = payment_data.get("customer")
        
        logger.info(f"Processing successful payment: {payment_intent_id} - ${amount/100}")
        
        # Update subscription status or unlock features
        # Implementation depends on business logic
        
    except Exception as e:
        logger.error(f"Error handling payment success: {str(e)}")

async def handle_subscription_created(subscription_data: Dict[str, Any], db: Session):
    """Handle new subscription from Stripe."""
    try:
        subscription_id = subscription_data.get("id")
        customer_id = subscription_data.get("customer")
        
        logger.info(f"Processing new subscription: {subscription_id}")
        
        # Activate premium features for user
        # Implementation depends on subscription tiers
        
    except Exception as e:
        logger.error(f"Error handling subscription creation: {str(e)}")

async def handle_subscription_updated(subscription_data: Dict[str, Any], db: Session):
    """Handle subscription updates from Stripe."""
    try:
        subscription_id = subscription_data.get("id")
        status = subscription_data.get("status")
        
        logger.info(f"Processing subscription update: {subscription_id} - {status}")
        
        # Update user access based on subscription status
        # Implementation depends on business logic
        
    except Exception as e:
        logger.error(f"Error handling subscription update: {str(e)}")

async def handle_subscription_cancelled(subscription_data: Dict[str, Any], db: Session):
    """Handle subscription cancellation from Stripe."""
    try:
        subscription_id = subscription_data.get("id")
        customer_id = subscription_data.get("customer")
        
        logger.info(f"Processing subscription cancellation: {subscription_id}")
        
        # Downgrade user access
        # Implementation depends on business logic
        
    except Exception as e:
        logger.error(f"Error handling subscription cancellation: {str(e)}")

async def handle_story_completed(project_id: str, data: Dict[str, Any], db: Session):
    """Handle story completion notification."""
    try:
        story_id = data.get("story_id")
        
        logger.info(f"Processing story completion: {project_id} - {story_id}")
        
        # Update project state
        await state_manager.transition_story_state(
            project_id=project_id,
            story_id=story_id,
            from_state="IN_PROGRESS",
            to_state="DONE"
        )
        
        # Trigger next workflow if needed
        await workflow_engine.execute_workflow(
            workflow_name="story-approved",
            context={"story_id": story_id},
            project_id=project_id
        )
        
    except Exception as e:
        logger.error(f"Error handling story completion: {str(e)}")

async def handle_epic_completed(project_id: str, data: Dict[str, Any], db: Session):
    """Handle epic completion notification."""
    try:
        epic_id = data.get("epic_id")
        
        logger.info(f"Processing epic completion: {project_id} - {epic_id}")
        
        # Trigger retrospective workflow
        await workflow_engine.execute_workflow(
            workflow_name="retrospective",
            context={"epic_id": epic_id},
            project_id=project_id
        )
        
    except Exception as e:
        logger.error(f"Error handling epic completion: {str(e)}")

async def handle_phase_transition(project_id: str, data: Dict[str, Any], db: Session):
    """Handle project phase transition."""
    try:
        new_phase = data.get("new_phase")
        
        logger.info(f"Processing phase transition: {project_id} - Phase {new_phase}")
        
        # Update project phase
        crud_project.update_project_phase(
            db=db,
            project_id=project_id,
            new_phase=new_phase
        )
        
    except Exception as e:
        logger.error(f"Error handling phase transition: {str(e)}")

async def handle_deal_status_change(project_id: str, data: Dict[str, Any], db: Session):
    """Handle M&A deal status change."""
    try:
        deal_id = data.get("deal_id")
        new_status = data.get("new_status")
        
        logger.info(f"Processing deal status change: {deal_id} - {new_status}")
        
        # Update deal status
        crud_deal.update_deal_status(
            db=db,
            deal_id=deal_id,
            status=new_status
        )
        
        # Trigger appropriate workflow based on status
        if new_status == "DUE_DILIGENCE":
            await workflow_engine.execute_workflow(
                workflow_name="due-diligence",
                context={"deal_id": deal_id},
                project_id=project_id
            )
        
    except Exception as e:
        logger.error(f"Error handling deal status change: {str(e)}")

async def handle_github_push(webhook_data: Dict[str, Any], db: Session):
    """Handle GitHub push events."""
    try:
        repository = webhook_data.get("repository", {}).get("name")
        commits = webhook_data.get("commits", [])
        
        logger.info(f"Processing GitHub push: {repository} - {len(commits)} commits")
        
        # Process commits and update related stories
        for commit in commits:
            commit_message = commit.get("message", "")
            # Look for story references in commit message
            # Implementation depends on commit message conventions
        
    except Exception as e:
        logger.error(f"Error handling GitHub push: {str(e)}")

async def handle_github_pr(webhook_data: Dict[str, Any], db: Session):
    """Handle GitHub pull request events."""
    try:
        action = webhook_data.get("action")
        pr_number = webhook_data.get("number")
        
        logger.info(f"Processing GitHub PR: {action} - #{pr_number}")
        
        # Update related stories based on PR status
        # Implementation depends on PR workflow
        
    except Exception as e:
        logger.error(f"Error handling GitHub PR: {str(e)}")

async def handle_github_issue(webhook_data: Dict[str, Any], db: Session):
    """Handle GitHub issue events."""
    try:
        action = webhook_data.get("action")
        issue_number = webhook_data.get("issue", {}).get("number")
        
        logger.info(f"Processing GitHub issue: {action} - #{issue_number}")
        
        # Create or update stories based on issues
        # Implementation depends on issue workflow
        
    except Exception as e:
        logger.error(f"Error handling GitHub issue: {str(e)}")

async def handle_slack_message(webhook_data: Dict[str, Any], db: Session):
    """Handle Slack message events."""
    try:
        message = webhook_data.get("event", {})
        text = message.get("text", "")
        user = message.get("user")
        
        logger.info(f"Processing Slack message from {user}: {text[:50]}...")
        
        # Process message for project updates or commands
        # Implementation depends on Slack bot functionality
        
    except Exception as e:
        logger.error(f"Error handling Slack message: {str(e)}")

async def handle_slack_mention(webhook_data: Dict[str, Any], db: Session):
    """Handle Slack app mentions."""
    try:
        message = webhook_data.get("event", {})
        text = message.get("text", "")
        user = message.get("user")
        
        logger.info(f"Processing Slack mention from {user}: {text[:50]}...")
        
        # Process mention and respond appropriately
        # Implementation depends on bot commands
        
    except Exception as e:
        logger.error(f"Error handling Slack mention: {str(e)}")
