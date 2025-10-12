"""
Email Campaign API Endpoints for M&A SaaS Platform
Handles email campaigns, notifications, and transactional emails
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.organization import Organization
from app.models.deals import Deal
from app.services.sendgrid_service import sendgrid_service
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/emails", tags=["emails"])

# Pydantic models for request/response
class EmailRequest(BaseModel):
    to_emails: List[EmailStr]
    subject: str
    html_content: str
    plain_content: Optional[str] = None
    categories: Optional[List[str]] = None
    custom_args: Optional[Dict[str, str]] = None

class BulkEmailRequest(BaseModel):
    recipients: List[Dict[str, str]]  # [{"email": "user@example.com", "name": "User Name"}]
    subject: str
    html_content: str
    template_id: Optional[str] = None
    dynamic_template_data: Optional[Dict] = None
    categories: Optional[List[str]] = None

class DealNotificationRequest(BaseModel):
    deal_id: int
    notification_type: str  # 'deal_created', 'deal_updated', 'deal_stage_changed', 'document_uploaded'
    recipients: Optional[List[EmailStr]] = None  # If not provided, will notify deal team

class NewsletterRequest(BaseModel):
    subject: str
    content: Dict[str, Any]
    subscriber_segments: Optional[List[str]] = None  # ['all', 'premium', 'trial']

class EmailStatsRequest(BaseModel):
    start_date: str  # YYYY-MM-DD format
    end_date: Optional[str] = None
    categories: Optional[List[str]] = None

@router.post("/send")
async def send_email(
    email_request: EmailRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a single email or bulk email"""
    try:
        # Add user context to custom args
        custom_args = email_request.custom_args or {}
        custom_args.update({
            'sender_user_id': str(current_user.id),
            'sender_organization_id': str(current_user.organization_id) if current_user.organization_id else 'none'
        })
        
        # Send email in background
        def send_email_task():
            result = sendgrid_service.send_email(
                to_emails=email_request.to_emails,
                subject=email_request.subject,
                html_content=email_request.html_content,
                plain_content=email_request.plain_content,
                categories=email_request.categories,
                custom_args=custom_args
            )
            
            if not result['success']:
                logger.error(f"Failed to send email: {result.get('error')}")
        
        background_tasks.add_task(send_email_task)
        
        return {
            "success": True,
            "message": "Email queued for sending",
            "recipients": len(email_request.to_emails)
        }
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )

@router.post("/bulk-send")
async def send_bulk_email(
    bulk_request: BulkEmailRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send bulk emails with personalization"""
    try:
        # Verify user has permission for bulk emails (e.g., admin or premium user)
        if not current_user.is_admin and not _has_bulk_email_permission(current_user, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for bulk email campaigns"
            )
        
        recipient_emails = [recipient['email'] for recipient in bulk_request.recipients]
        
        # Send bulk email in background
        def send_bulk_email_task():
            result = sendgrid_service.send_email(
                to_emails=recipient_emails,
                subject=bulk_request.subject,
                html_content=bulk_request.html_content,
                template_id=bulk_request.template_id,
                dynamic_template_data=bulk_request.dynamic_template_data,
                categories=bulk_request.categories,
                custom_args={
                    'campaign_type': 'bulk',
                    'sender_user_id': str(current_user.id),
                    'sender_organization_id': str(current_user.organization_id) if current_user.organization_id else 'none'
                }
            )
            
            if not result['success']:
                logger.error(f"Failed to send bulk email: {result.get('error')}")
        
        background_tasks.add_task(send_bulk_email_task)
        
        return {
            "success": True,
            "message": "Bulk email campaign queued for sending",
            "recipients": len(recipient_emails)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending bulk email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send bulk email: {str(e)}"
        )

@router.post("/deal-notification")
async def send_deal_notification(
    notification_request: DealNotificationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send deal-related notifications"""
    try:
        # Get deal information
        deal = db.query(Deal).filter(Deal.id == notification_request.deal_id).first()
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal not found"
            )
        
        # Verify user has access to this deal
        if not _user_has_deal_access(current_user, deal, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this deal"
            )
        
        # Determine recipients
        recipients = notification_request.recipients
        if not recipients:
            recipients = _get_deal_team_emails(deal, db)
        
        # Prepare deal details
        deal_details = {
            'deal_id': deal.id,
            'stage': deal.stage,
            'value': f"${deal.value:,.2f}" if deal.value else "N/A",
            'updated_at': deal.updated_at.strftime("%Y-%m-%d %H:%M") if deal.updated_at else "N/A",
            'new_stage': deal.stage  # This would be updated based on notification type
        }
        
        # Send notifications in background
        def send_notifications_task():
            for recipient_email in recipients:
                # Get recipient user info
                recipient_user = db.query(User).filter(User.email == recipient_email).first()
                recipient_name = recipient_user.full_name if recipient_user else recipient_email.split('@')[0]
                
                result = sendgrid_service.send_deal_notification(
                    user_email=recipient_email,
                    user_name=recipient_name,
                    deal_name=deal.name,
                    notification_type=notification_request.notification_type,
                    deal_details=deal_details
                )
                
                if not result['success']:
                    logger.error(f"Failed to send deal notification to {recipient_email}: {result.get('error')}")
        
        background_tasks.add_task(send_notifications_task)
        
        return {
            "success": True,
            "message": "Deal notifications queued for sending",
            "recipients": len(recipients),
            "deal_name": deal.name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending deal notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send deal notification: {str(e)}"
        )

@router.post("/welcome")
async def send_welcome_email(
    user_email: EmailStr,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send welcome email to new user"""
    try:
        # Get user information
        new_user = db.query(User).filter(User.email == user_email).first()
        if not new_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get organization name if applicable
        organization_name = None
        if new_user.organization_id:
            organization = db.query(Organization).filter(Organization.id == new_user.organization_id).first()
            organization_name = organization.name if organization else None
        
        # Send welcome email in background
        def send_welcome_task():
            result = sendgrid_service.send_welcome_email(
                user_email=new_user.email,
                user_name=new_user.full_name or new_user.email.split('@')[0],
                organization_name=organization_name
            )
            
            if not result['success']:
                logger.error(f"Failed to send welcome email to {new_user.email}: {result.get('error')}")
        
        background_tasks.add_task(send_welcome_task)
        
        return {
            "success": True,
            "message": "Welcome email queued for sending",
            "recipient": new_user.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending welcome email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send welcome email: {str(e)}"
        )

@router.post("/newsletter")
async def send_newsletter(
    newsletter_request: NewsletterRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send newsletter to subscribers"""
    try:
        # Verify user has admin permissions
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permissions required for newsletter campaigns"
            )
        
        # Get subscribers based on segments
        subscribers = _get_newsletter_subscribers(newsletter_request.subscriber_segments, db)
        
        if not subscribers:
            return {
                "success": True,
                "message": "No subscribers found for the specified segments",
                "recipients": 0
            }
        
        # Send newsletter in background
        def send_newsletter_task():
            result = sendgrid_service.send_market_insights_newsletter(
                subscribers=subscribers,
                insights_data=newsletter_request.content
            )
            
            if not result['success']:
                logger.error(f"Failed to send newsletter: {result.get('error')}")
        
        background_tasks.add_task(send_newsletter_task)
        
        return {
            "success": True,
            "message": "Newsletter queued for sending",
            "recipients": len(subscribers)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending newsletter: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send newsletter: {str(e)}"
        )

@router.get("/stats")
async def get_email_stats(
    start_date: str,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get email campaign statistics"""
    try:
        # Verify user has permission to view stats
        if not current_user.is_admin and not _has_stats_permission(current_user, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view email statistics"
            )
        
        result = sendgrid_service.get_email_stats(start_date, end_date)
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch email statistics: {result.get('error')}"
            )
        
        return {
            "success": True,
            "data": result['data'],
            "period": {
                "start_date": start_date,
                "end_date": end_date or datetime.now().strftime("%Y-%m-%d")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching email stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch email statistics: {str(e)}"
        )

# Helper functions
def _has_bulk_email_permission(user: User, db: Session) -> bool:
    """Check if user has permission to send bulk emails"""
    # Check if user has premium subscription or admin role
    if user.subscription_tier in ['premium', 'enterprise']:
        return True
    return False

def _user_has_deal_access(user: User, deal: Deal, db: Session) -> bool:
    """Check if user has access to the deal"""
    # Check if user owns the deal or is part of the deal team
    if deal.created_by == user.id:
        return True
    
    # Check if user is in the same organization
    if user.organization_id and deal.organization_id == user.organization_id:
        return True
    
    return False

def _get_deal_team_emails(deal: Deal, db: Session) -> List[str]:
    """Get email addresses of deal team members"""
    # This would query deal team members and return their emails
    # For now, return the deal creator's email
    creator = db.query(User).filter(User.id == deal.created_by).first()
    return [creator.email] if creator else []

def _get_newsletter_subscribers(segments: Optional[List[str]], db: Session) -> List[Dict[str, str]]:
    """Get newsletter subscribers based on segments"""
    query = db.query(User).filter(User.newsletter_subscribed == True)
    
    if segments and 'all' not in segments:
        if 'premium' in segments:
            query = query.filter(User.subscription_tier.in_(['premium', 'enterprise']))
        elif 'trial' in segments:
            query = query.filter(User.subscription_tier == 'trial')
    
    users = query.all()
    return [{'email': user.email, 'name': user.full_name or user.email.split('@')[0]} for user in users]

def _has_stats_permission(user: User, db: Session) -> bool:
    """Check if user has permission to view email statistics"""
    # Allow premium users and organization admins to view stats
    return user.subscription_tier in ['premium', 'enterprise'] or user.role == 'admin'
