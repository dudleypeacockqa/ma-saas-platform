"""
SendGrid Email Service for M&A SaaS Platform
Handles email campaigns, transactional emails, and user communications
"""

import os
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
from sendgrid.helpers.mail import Personalization, CustomArg, Category, Header
from python_http_client import exceptions
import base64
import mimetypes

logger = logging.getLogger(__name__)

class SendGridService:
    """SendGrid email service for M&A platform communications"""
    
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@100daysandbeyond.com')
        self.from_name = os.getenv('SENDGRID_FROM_NAME', '100 Days and Beyond')
        
        if not self.api_key:
            raise ValueError("SENDGRID_API_KEY environment variable is required")
        
        self.sg = sendgrid.SendGridAPIClient(api_key=self.api_key)
        
    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None,
        template_id: Optional[str] = None,
        dynamic_template_data: Optional[Dict] = None,
        attachments: Optional[List[Dict]] = None,
        categories: Optional[List[str]] = None,
        custom_args: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Send email using SendGrid
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject line
            html_content: HTML email content
            plain_content: Plain text email content (optional)
            template_id: SendGrid template ID (optional)
            dynamic_template_data: Template data for dynamic templates
            attachments: List of file attachments
            categories: Email categories for tracking
            custom_args: Custom arguments for tracking
            
        Returns:
            Dict with send status and message ID
        """
        try:
            from_email = Email(self.from_email, self.from_name)
            
            # Create mail object
            if template_id:
                # Use dynamic template
                mail = Mail(
                    from_email=from_email,
                    to_emails=to_emails[0] if len(to_emails) == 1 else None
                )
                mail.template_id = template_id
                
                if dynamic_template_data:
                    mail.dynamic_template_data = dynamic_template_data
                    
                # Add multiple recipients for template emails
                if len(to_emails) > 1:
                    for email in to_emails:
                        personalization = Personalization()
                        personalization.add_to(To(email))
                        if dynamic_template_data:
                            personalization.dynamic_template_data = dynamic_template_data
                        mail.add_personalization(personalization)
            else:
                # Use custom content
                to_list = [To(email) for email in to_emails]
                mail = Mail(
                    from_email=from_email,
                    to_emails=to_list,
                    subject=subject,
                    html_content=Content("text/html", html_content)
                )
                
                if plain_content:
                    mail.add_content(Content("text/plain", plain_content))
            
            # Add categories for tracking
            if categories:
                for category in categories:
                    mail.add_category(Category(category))
            
            # Add custom arguments
            if custom_args:
                for key, value in custom_args.items():
                    mail.add_custom_arg(CustomArg(key, str(value)))
            
            # Add attachments
            if attachments:
                for attachment_data in attachments:
                    self._add_attachment(mail, attachment_data)
            
            # Send email
            response = self.sg.send(mail)
            
            logger.info(f"Email sent successfully. Status: {response.status_code}")
            
            return {
                'success': True,
                'status_code': response.status_code,
                'message_id': response.headers.get('X-Message-Id'),
                'recipients': len(to_emails)
            }
            
        except exceptions.BadRequestsError as e:
            logger.error(f"SendGrid bad request: {e.body}")
            return {
                'success': False,
                'error': 'Bad request',
                'details': str(e.body)
            }
        except Exception as e:
            logger.error(f"SendGrid error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _add_attachment(self, mail: Mail, attachment_data: Dict):
        """Add attachment to email"""
        try:
            file_path = attachment_data.get('file_path')
            file_content = attachment_data.get('content')
            filename = attachment_data.get('filename')
            content_type = attachment_data.get('content_type')
            
            if file_path and os.path.exists(file_path):
                # Read file from path
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                encoded_file = base64.b64encode(file_data).decode()
                
                if not filename:
                    filename = os.path.basename(file_path)
                if not content_type:
                    content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
                    
            elif file_content:
                # Use provided content
                if isinstance(file_content, str):
                    encoded_file = base64.b64encode(file_content.encode()).decode()
                else:
                    encoded_file = base64.b64encode(file_content).decode()
            else:
                logger.warning("No file content provided for attachment")
                return
            
            attachment = Attachment(
                FileContent(encoded_file),
                FileName(filename),
                FileType(content_type or 'application/octet-stream'),
                Disposition('attachment')
            )
            
            mail.add_attachment(attachment)
            
        except Exception as e:
            logger.error(f"Error adding attachment: {str(e)}")
    
    def send_welcome_email(self, user_email: str, user_name: str, organization_name: str = None) -> Dict[str, Any]:
        """Send welcome email to new users"""
        subject = f"Welcome to 100 Days and Beyond - Your M&A Journey Begins!"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 28px;">Welcome to 100 Days and Beyond!</h1>
                <p style="color: white; margin: 10px 0 0 0; font-size: 16px;">Your M&A Success Platform</p>
            </div>
            
            <div style="padding: 40px 20px; background: white;">
                <h2 style="color: #333; margin-bottom: 20px;">Hi {user_name}! 👋</h2>
                
                <p style="color: #666; line-height: 1.6; margin-bottom: 20px;">
                    Welcome to the most comprehensive M&A platform designed for ambitious professionals like you. 
                    {"Your organization " + organization_name + " is" if organization_name else "You are"} now part of an exclusive 
                    community focused on building wealth through strategic M&A activities.
                </p>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #333; margin-top: 0;">🚀 What's Next?</h3>
                    <ul style="color: #666; line-height: 1.8;">
                        <li><strong>Set up your first deal pipeline</strong> - Track opportunities from sourcing to closing</li>
                        <li><strong>Upload deal documents</strong> - Secure, organized document management</li>
                        <li><strong>Invite your team</strong> - Collaborate with colleagues and advisors</li>
                        <li><strong>Explore AI insights</strong> - Get intelligent deal analysis and recommendations</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://100daysandbeyond.com/dashboard" 
                       style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; 
                              border-radius: 5px; font-weight: bold; display: inline-block;">
                        Access Your Dashboard
                    </a>
                </div>
                
                <div style="border-top: 1px solid #eee; padding-top: 20px; margin-top: 30px;">
                    <p style="color: #999; font-size: 14px; margin: 0;">
                        Need help getting started? Reply to this email or visit our 
                        <a href="https://100daysandbeyond.com/support" style="color: #667eea;">support center</a>.
                    </p>
                </div>
            </div>
        </div>
        """
        
        return self.send_email(
            to_emails=[user_email],
            subject=subject,
            html_content=html_content,
            categories=['welcome', 'onboarding'],
            custom_args={
                'user_type': 'new_user',
                'organization': organization_name or 'individual'
            }
        )
    
    def send_deal_notification(
        self, 
        user_email: str, 
        user_name: str, 
        deal_name: str, 
        notification_type: str, 
        deal_details: Dict
    ) -> Dict[str, Any]:
        """Send deal-related notifications"""
        
        notification_templates = {
            'deal_created': {
                'subject': f'New Deal Created: {deal_name}',
                'title': '🎯 New Deal in Your Pipeline',
                'message': f'A new deal "{deal_name}" has been added to your pipeline and is ready for your attention.'
            },
            'deal_updated': {
                'subject': f'Deal Updated: {deal_name}',
                'title': '📈 Deal Progress Update',
                'message': f'Deal "{deal_name}" has been updated with new information.'
            },
            'deal_stage_changed': {
                'subject': f'Deal Stage Change: {deal_name}',
                'title': '🔄 Deal Stage Progression',
                'message': f'Deal "{deal_name}" has moved to {deal_details.get("new_stage", "a new stage")}.'
            },
            'document_uploaded': {
                'subject': f'New Document: {deal_name}',
                'title': '📄 New Document Available',
                'message': f'A new document has been uploaded for deal "{deal_name}".'
            }
        }
        
        template = notification_templates.get(notification_type, notification_templates['deal_updated'])
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #667eea; padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">{template['title']}</h1>
            </div>
            
            <div style="padding: 30px 20px; background: white;">
                <h2 style="color: #333;">Hi {user_name},</h2>
                
                <p style="color: #666; line-height: 1.6; margin-bottom: 20px;">
                    {template['message']}
                </p>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #333; margin-top: 0;">Deal Details:</h3>
                    <ul style="color: #666; line-height: 1.6;">
                        <li><strong>Deal Name:</strong> {deal_name}</li>
                        <li><strong>Current Stage:</strong> {deal_details.get('stage', 'N/A')}</li>
                        <li><strong>Deal Value:</strong> {deal_details.get('value', 'N/A')}</li>
                        <li><strong>Last Updated:</strong> {deal_details.get('updated_at', 'N/A')}</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://100daysandbeyond.com/deals/{deal_details.get('deal_id', '')}" 
                       style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; 
                              border-radius: 5px; font-weight: bold; display: inline-block;">
                        View Deal Details
                    </a>
                </div>
            </div>
        </div>
        """
        
        return self.send_email(
            to_emails=[user_email],
            subject=template['subject'],
            html_content=html_content,
            categories=['deal_notification', notification_type],
            custom_args={
                'deal_id': deal_details.get('deal_id'),
                'notification_type': notification_type
            }
        )
    
    def send_market_insights_newsletter(self, subscribers: List[Dict[str, str]], insights_data: Dict) -> Dict[str, Any]:
        """Send market insights newsletter to subscribers"""
        subject = f"M&A Market Insights - {insights_data.get('period', 'Weekly Update')}"
        
        # Use dynamic template for personalized newsletters
        template_data = {
            'subject': subject,
            'insights_data': insights_data,
            'unsubscribe_url': 'https://100daysandbeyond.com/unsubscribe'
        }
        
        recipient_emails = [subscriber['email'] for subscriber in subscribers]
        
        return self.send_email(
            to_emails=recipient_emails,
            subject=subject,
            html_content="",  # Will use template
            template_id=os.getenv('SENDGRID_NEWSLETTER_TEMPLATE_ID'),
            dynamic_template_data=template_data,
            categories=['newsletter', 'market_insights'],
            custom_args={
                'campaign_type': 'newsletter',
                'period': insights_data.get('period', 'weekly')
            }
        )
    
    def send_password_reset(self, user_email: str, user_name: str, reset_token: str) -> Dict[str, Any]:
        """Send password reset email"""
        reset_url = f"https://100daysandbeyond.com/reset-password?token={reset_token}"
        
        subject = "Reset Your 100 Days and Beyond Password"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #667eea; padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">Password Reset Request</h1>
            </div>
            
            <div style="padding: 30px 20px; background: white;">
                <h2 style="color: #333;">Hi {user_name},</h2>
                
                <p style="color: #666; line-height: 1.6; margin-bottom: 20px;">
                    We received a request to reset your password for your 100 Days and Beyond account.
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" 
                       style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; 
                              border-radius: 5px; font-weight: bold; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                
                <p style="color: #666; font-size: 14px; line-height: 1.6;">
                    This link will expire in 24 hours. If you didn't request this password reset, 
                    please ignore this email or contact our support team.
                </p>
                
                <p style="color: #999; font-size: 12px; margin-top: 20px;">
                    If the button doesn't work, copy and paste this link into your browser:<br>
                    <span style="word-break: break-all;">{reset_url}</span>
                </p>
            </div>
        </div>
        """
        
        return self.send_email(
            to_emails=[user_email],
            subject=subject,
            html_content=html_content,
            categories=['transactional', 'password_reset'],
            custom_args={
                'email_type': 'password_reset',
                'user_email': user_email
            }
        )
    
    def get_email_stats(self, start_date: str, end_date: str = None) -> Dict[str, Any]:
        """Get email campaign statistics from SendGrid"""
        try:
            params = {
                'start_date': start_date,
                'aggregated_by': 'day'
            }
            
            if end_date:
                params['end_date'] = end_date
            
            response = self.sg.client.stats.get(query_params=params)
            
            return {
                'success': True,
                'data': response.body
            }
            
        except Exception as e:
            logger.error(f"Error fetching email stats: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Initialize service instance
sendgrid_service = SendGridService()
