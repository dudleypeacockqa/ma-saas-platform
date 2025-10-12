"""
Slack Integration
Notifications, workflow automation, and deal collaboration
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import aiohttp
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

from ..core.integration_manager import (
    BaseIntegration, IntegrationConfig, SyncResult, WebhookEvent,
    SyncDirection, IntegrationStatus
)
from ...core.database import get_db
from ...models.deal import Deal
from ...models.notification import Notification
from ...models.workflow import WorkflowExecution
from ...models.deal_room import DealRoom

logger = logging.getLogger(__name__)


class SlackIntegration(BaseIntegration):
    """Slack integration for deal notifications and workflow automation"""

    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.slack_client: Optional[AsyncWebClient] = None
        self.bot_token: Optional[str] = None
        self.signing_secret: Optional[str] = None

    async def authenticate(self) -> bool:
        """Authenticate with Slack using Bot Token"""
        try:
            credentials = self.config.credentials
            self.bot_token = credentials.get("bot_token")
            self.signing_secret = credentials.get("signing_secret")

            if not self.bot_token:
                logger.error("Slack bot token not provided")
                return False

            # Initialize Slack client
            self.slack_client = AsyncWebClient(token=self.bot_token)

            return True

        except Exception as e:
            logger.error(f"Slack authentication failed: {str(e)}")
            return False

    async def test_connection(self) -> bool:
        """Test Slack connection"""
        try:
            if not self.slack_client:
                return False

            # Test with auth.test API call
            response = await self.slack_client.auth_test()
            return response["ok"]

        except SlackApiError as e:
            logger.error(f"Slack connection test failed: {e.response['error']}")
            return False
        except Exception as e:
            logger.error(f"Slack connection test error: {str(e)}")
            return False

    async def sync_data(self, direction: SyncDirection) -> SyncResult:
        """Synchronize Slack data with M&A platform"""
        sync_id = f"slack_sync_{datetime.now().timestamp()}"
        start_time = datetime.now()

        result = SyncResult(
            sync_id=sync_id,
            integration_id=self.config.integration_id,
            direction=direction,
            records_processed=0,
            records_created=0,
            records_updated=0,
            records_failed=0,
            conflicts_detected=0,
            start_time=start_time,
            end_time=start_time,
            errors=[],
            success=False
        )

        try:
            if not self.slack_client:
                result.errors.append("Not authenticated with Slack")
                result.end_time = datetime.now()
                return result

            self.status = IntegrationStatus.SYNCING

            if direction in [SyncDirection.INBOUND, SyncDirection.BIDIRECTIONAL]:
                # Sync from Slack to M&A platform
                inbound_result = await self._sync_from_slack()
                result.records_processed += inbound_result["processed"]
                result.records_created += inbound_result["created"]
                result.records_updated += inbound_result["updated"]
                result.records_failed += inbound_result["failed"]
                result.errors.extend(inbound_result["errors"])

            if direction in [SyncDirection.OUTBOUND, SyncDirection.BIDIRECTIONAL]:
                # Sync from M&A platform to Slack
                outbound_result = await self._sync_to_slack()
                result.records_processed += outbound_result["processed"]
                result.records_created += outbound_result["created"]
                result.records_updated += outbound_result["updated"]
                result.records_failed += outbound_result["failed"]
                result.errors.extend(outbound_result["errors"])

            result.success = result.records_failed == 0
            result.end_time = datetime.now()
            self.last_sync = result.end_time
            self.status = IntegrationStatus.CONNECTED

            logger.info(f"Slack sync completed: {result.records_processed} processed, {result.records_failed} failed")

        except Exception as e:
            logger.error(f"Slack sync error: {str(e)}")
            result.errors.append(str(e))
            result.end_time = datetime.now()
            self.status = IntegrationStatus.ERROR

        return result

    async def _sync_from_slack(self) -> Dict[str, Any]:
        """Sync data from Slack to M&A platform"""
        result = {
            "processed": 0,
            "created": 0,
            "updated": 0,
            "failed": 0,
            "errors": []
        }

        try:
            # Sync workspace info
            workspace_result = await self._sync_workspace_info()
            for key in result:
                if key in workspace_result:
                    result[key] += workspace_result[key]

            # Sync channels
            channels_result = await self._sync_channels_from_slack()
            for key in result:
                if key in channels_result:
                    result[key] += channels_result[key]

            # Sync recent messages from deal channels
            messages_result = await self._sync_messages_from_slack()
            for key in result:
                if key in messages_result:
                    result[key] += messages_result[key]

        except Exception as e:
            result["errors"].append(f"Inbound sync error: {str(e)}")
            result["failed"] += 1

        return result

    async def _sync_workspace_info(self) -> Dict[str, Any]:
        """Sync Slack workspace information"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            # Get team info
            team_info = await self.slack_client.team_info()
            if team_info["ok"]:
                result["processed"] += 1
                logger.info(f"Connected to Slack workspace: {team_info['team']['name']}")

        except SlackApiError as e:
            result["errors"].append(f"Failed to get workspace info: {e.response['error']}")
            result["failed"] += 1

        return result

    async def _sync_channels_from_slack(self) -> Dict[str, Any]:
        """Sync Slack channels"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            # Get all channels
            channels_response = await self.slack_client.conversations_list(
                types="public_channel,private_channel",
                limit=1000
            )

            if channels_response["ok"]:
                channels = channels_response["channels"]

                async with get_db() as db:
                    for channel in channels:
                        try:
                            result["processed"] += 1

                            # Check if this is a deal-related channel
                            if self._is_deal_channel(channel):
                                deal_room = await self._find_or_create_deal_room(db, channel)
                                if deal_room:
                                    result["created"] += 1

                        except Exception as e:
                            result["failed"] += 1
                            result["errors"].append(f"Failed to sync channel {channel.get('id')}: {str(e)}")

                    await db.commit()

        except SlackApiError as e:
            result["errors"].append(f"Failed to get channels: {e.response['error']}")
            result["failed"] += 1

        return result

    async def _sync_messages_from_slack(self) -> Dict[str, Any]:
        """Sync messages from Slack channels"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            # Get deal-related channels
            async with get_db() as db:
                deal_rooms_query = select(DealRoom).where(DealRoom.platform == "slack")
                deal_rooms_result = await db.execute(deal_rooms_query)
                deal_rooms = deal_rooms_result.scalars().all()

                for deal_room in deal_rooms:
                    try:
                        # Get recent messages from channel
                        messages_response = await self.slack_client.conversations_history(
                            channel=deal_room.external_id,
                            limit=50
                        )

                        if messages_response["ok"]:
                            messages = messages_response["messages"]
                            result["processed"] += len(messages)
                            # Process messages as needed

                    except SlackApiError as e:
                        result["failed"] += 1
                        result["errors"].append(f"Failed to get messages from {deal_room.external_id}: {e.response['error']}")

        except Exception as e:
            result["errors"].append(f"Messages sync error: {str(e)}")
            result["failed"] += 1

        return result

    async def _sync_to_slack(self) -> Dict[str, Any]:
        """Sync M&A platform data to Slack"""
        result = {
            "processed": 0,
            "created": 0,
            "updated": 0,
            "failed": 0,
            "errors": []
        }

        try:
            # Create channels for new deals
            deal_channels_result = await self._create_deal_channels()
            for key in result:
                if key in deal_channels_result:
                    result[key] += deal_channels_result[key]

            # Send notifications to Slack
            notifications_result = await self._send_slack_notifications()
            for key in result:
                if key in notifications_result:
                    result[key] += notifications_result[key]

            # Send workflow updates
            workflow_result = await self._send_workflow_updates()
            for key in result:
                if key in workflow_result:
                    result[key] += workflow_result[key]

        except Exception as e:
            result["errors"].append(f"Outbound sync error: {str(e)}")
            result["failed"] += 1

        return result

    async def _create_deal_channels(self) -> Dict[str, Any]:
        """Create Slack channels for new deals"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            async with get_db() as db:
                # Get deals that need Slack integration
                deals_query = select(Deal).where(
                    Deal.is_active == True,
                    Deal.slack_integration_status.is_(None)
                )
                deals_result = await db.execute(deals_query)
                deals = deals_result.scalars().all()

                for deal in deals:
                    try:
                        result["processed"] += 1

                        # Create channel for deal
                        channel_name = self._generate_channel_name(deal.title)

                        channel_response = await self.slack_client.conversations_create(
                            name=channel_name,
                            is_private=True
                        )

                        if channel_response["ok"]:
                            channel = channel_response["channel"]

                            # Update deal with Slack information
                            deal.slack_integration_status = "integrated"
                            deal.slack_channel_id = channel["id"]

                            # Create deal room record
                            deal_room = DealRoom(
                                deal_id=deal.id,
                                platform="slack",
                                external_id=channel["id"],
                                name=channel["name"],
                                description=f"Deal channel for {deal.title}",
                                created_at=datetime.now()
                            )
                            db.add(deal_room)

                            # Send welcome message
                            await self._send_welcome_message(channel["id"], deal)

                            result["created"] += 1
                            logger.info(f"Created Slack channel for deal {deal.title}")

                        else:
                            result["failed"] += 1
                            result["errors"].append(f"Failed to create channel for deal {deal.id}")

                    except SlackApiError as e:
                        result["failed"] += 1
                        result["errors"].append(f"Failed to create channel for deal {deal.id}: {e.response['error']}")

                await db.commit()

        except Exception as e:
            result["errors"].append(f"Deal channels creation error: {str(e)}")
            result["failed"] += 1

        return result

    async def _send_slack_notifications(self) -> Dict[str, Any]:
        """Send notifications to Slack channels"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            async with get_db() as db:
                # Get pending Slack notifications
                notifications_query = select(Notification).where(
                    Notification.channel == "slack",
                    Notification.status == "pending"
                )
                notifications_result = await db.execute(notifications_query)
                notifications = notifications_result.scalars().all()

                for notification in notifications:
                    try:
                        result["processed"] += 1

                        # Get channel from notification metadata
                        channel_id = notification.metadata.get("channel_id")
                        if not channel_id:
                            # Try to find deal channel
                            if notification.deal_id:
                                deal_query = select(Deal).where(Deal.id == notification.deal_id)
                                deal_result = await db.execute(deal_query)
                                deal = deal_result.scalar_one_or_none()
                                if deal and deal.slack_channel_id:
                                    channel_id = deal.slack_channel_id

                        if channel_id:
                            # Format message
                            message_blocks = self._format_slack_message(notification)

                            # Send message
                            message_response = await self.slack_client.chat_postMessage(
                                channel=channel_id,
                                blocks=message_blocks,
                                text=notification.title  # Fallback text
                            )

                            if message_response["ok"]:
                                notification.status = "sent"
                                notification.sent_at = datetime.now()
                                result["created"] += 1
                            else:
                                result["failed"] += 1
                                result["errors"].append(f"Failed to send notification {notification.id}")

                        else:
                            result["failed"] += 1
                            result["errors"].append(f"No channel found for notification {notification.id}")

                    except SlackApiError as e:
                        result["failed"] += 1
                        result["errors"].append(f"Failed to send notification {notification.id}: {e.response['error']}")

                await db.commit()

        except Exception as e:
            result["errors"].append(f"Slack notifications error: {str(e)}")
            result["failed"] += 1

        return result

    async def _send_workflow_updates(self) -> Dict[str, Any]:
        """Send workflow execution updates to Slack"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            async with get_db() as db:
                # Get recent workflow executions that need Slack updates
                workflow_query = select(WorkflowExecution).where(
                    WorkflowExecution.status.in_(["completed", "failed"]),
                    WorkflowExecution.slack_notified == False,
                    WorkflowExecution.updated_at >= datetime.now() - timedelta(hours=1)
                )
                workflow_result = await db.execute(workflow_query)
                workflows = workflow_result.scalars().all()

                for workflow in workflows:
                    try:
                        result["processed"] += 1

                        # Get deal channel for workflow
                        if workflow.deal_id:
                            deal_query = select(Deal).where(Deal.id == workflow.deal_id)
                            deal_result = await db.execute(deal_query)
                            deal = deal_result.scalar_one_or_none()

                            if deal and deal.slack_channel_id:
                                # Send workflow update
                                message_blocks = self._format_workflow_message(workflow)

                                message_response = await self.slack_client.chat_postMessage(
                                    channel=deal.slack_channel_id,
                                    blocks=message_blocks,
                                    text=f"Workflow {workflow.workflow_name} {workflow.status}"
                                )

                                if message_response["ok"]:
                                    workflow.slack_notified = True
                                    result["created"] += 1

                    except SlackApiError as e:
                        result["failed"] += 1
                        result["errors"].append(f"Failed to send workflow update {workflow.id}: {e.response['error']}")

                await db.commit()

        except Exception as e:
            result["errors"].append(f"Workflow updates error: {str(e)}")
            result["failed"] += 1

        return result

    async def handle_webhook(self, event: WebhookEvent) -> bool:
        """Handle Slack webhook events"""
        try:
            event_type = event.event_type
            payload = event.payload

            if event_type == "message":
                await self._handle_message_webhook(payload)
            elif event_type == "app_mention":
                await self._handle_app_mention_webhook(payload)
            elif event_type == "channel_created":
                await self._handle_channel_created_webhook(payload)

            return True

        except Exception as e:
            logger.error(f"Slack webhook handling error: {str(e)}")
            return False

    async def _handle_message_webhook(self, payload: Dict[str, Any]):
        """Handle message webhook events"""
        # Process incoming messages for deal-related channels
        logger.info(f"Processing Slack message webhook: {payload}")

    async def _handle_app_mention_webhook(self, payload: Dict[str, Any]):
        """Handle app mention webhook events"""
        # Process when the bot is mentioned
        logger.info(f"Processing Slack app mention webhook: {payload}")

    async def _handle_channel_created_webhook(self, payload: Dict[str, Any]):
        """Handle channel created webhook events"""
        # Process channel creation events
        logger.info(f"Processing Slack channel created webhook: {payload}")

    async def get_supported_entities(self) -> List[str]:
        """Get list of entities this integration can sync"""
        return ["channels", "messages", "notifications", "workflows", "deal_rooms"]

    # Deal-specific Slack operations

    async def send_deal_update(
        self,
        deal_id: str,
        message: str,
        urgency: str = "normal"
    ) -> bool:
        """Send a deal update to the deal's Slack channel"""
        try:
            if not self.slack_client:
                return False

            async with get_db() as db:
                # Get deal information
                deal_query = select(Deal).where(Deal.id == deal_id)
                deal_result = await db.execute(deal_query)
                deal = deal_result.scalar_one_or_none()

                if not deal or not deal.slack_channel_id:
                    return False

                # Format message based on urgency
                blocks = self._format_deal_update_message(deal, message, urgency)

                # Send message
                response = await self.slack_client.chat_postMessage(
                    channel=deal.slack_channel_id,
                    blocks=blocks,
                    text=f"Deal Update: {message}"
                )

                return response["ok"]

        except Exception as e:
            logger.error(f"Failed to send deal update: {str(e)}")
            return False

    async def create_deal_reminder(
        self,
        deal_id: str,
        reminder_text: str,
        remind_at: datetime
    ) -> bool:
        """Schedule a reminder for a deal"""
        try:
            if not self.slack_client:
                return False

            async with get_db() as db:
                deal_query = select(Deal).where(Deal.id == deal_id)
                deal_result = await db.execute(deal_query)
                deal = deal_result.scalar_one_or_none()

                if not deal or not deal.slack_channel_id:
                    return False

                # Schedule message using Slack's scheduled messages
                response = await self.slack_client.chat_scheduleMessage(
                    channel=deal.slack_channel_id,
                    text=f"🔔 Reminder: {reminder_text}",
                    post_at=int(remind_at.timestamp())
                )

                return response["ok"]

        except Exception as e:
            logger.error(f"Failed to create deal reminder: {str(e)}")
            return False

    async def invite_users_to_deal_channel(
        self,
        deal_id: str,
        user_emails: List[str]
    ) -> bool:
        """Invite users to a deal channel"""
        try:
            if not self.slack_client:
                return False

            async with get_db() as db:
                deal_query = select(Deal).where(Deal.id == deal_id)
                deal_result = await db.execute(deal_query)
                deal = deal_result.scalar_one_or_none()

                if not deal or not deal.slack_channel_id:
                    return False

                # Get user IDs from emails
                for email in user_emails:
                    try:
                        user_response = await self.slack_client.users_lookupByEmail(email=email)
                        if user_response["ok"]:
                            user_id = user_response["user"]["id"]

                            # Invite user to channel
                            invite_response = await self.slack_client.conversations_invite(
                                channel=deal.slack_channel_id,
                                users=[user_id]
                            )

                            if not invite_response["ok"]:
                                logger.warning(f"Failed to invite {email} to deal channel")

                    except SlackApiError as e:
                        logger.warning(f"Failed to find/invite user {email}: {e.response['error']}")

                return True

        except Exception as e:
            logger.error(f"Failed to invite users to deal channel: {str(e)}")
            return False

    # Helper methods

    async def _find_or_create_deal_room(self, db, channel: Dict[str, Any]) -> Optional[DealRoom]:
        """Find or create a deal room for a Slack channel"""
        try:
            channel_id = channel["id"]

            # Check if deal room already exists
            existing_room_query = select(DealRoom).where(
                DealRoom.external_id == channel_id,
                DealRoom.platform == "slack"
            )
            result = await db.execute(existing_room_query)
            existing_room = result.scalar_one_or_none()

            if existing_room:
                return existing_room

            # Create new deal room if this is a deal-related channel
            if self._is_deal_channel(channel):
                deal_room = DealRoom(
                    platform="slack",
                    external_id=channel_id,
                    name=channel.get("name", ""),
                    description=channel.get("purpose", {}).get("value", ""),
                    created_at=datetime.now()
                )
                db.add(deal_room)
                return deal_room

        except Exception as e:
            logger.error(f"Failed to find/create deal room: {str(e)}")

        return None

    def _is_deal_channel(self, channel: Dict[str, Any]) -> bool:
        """Check if a Slack channel is deal-related"""
        channel_name = channel.get("name", "").lower()
        keywords = ["deal", "acquisition", "merger", "ma", "transaction", "project"]
        return any(keyword in channel_name for keyword in keywords)

    def _generate_channel_name(self, deal_title: str) -> str:
        """Generate a valid Slack channel name from deal title"""
        # Slack channel names must be lowercase, no spaces, limited chars
        channel_name = deal_title.lower()
        channel_name = "".join(c if c.isalnum() or c in "-_" else "-" for c in channel_name)
        channel_name = channel_name[:21]  # Slack limit
        return f"deal-{channel_name}"

    async def _send_welcome_message(self, channel_id: str, deal: Deal):
        """Send welcome message to new deal channel"""
        try:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🎯 Welcome to {deal.title}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"This channel is for collaboration on the *{deal.title}* deal.\n\n*Deal Value:* ${deal.deal_value:,.0f}\n*Stage:* {deal.stage.replace('_', ' ').title()}\n*Expected Close:* {deal.expected_close_date.strftime('%Y-%m-%d') if deal.expected_close_date else 'TBD'}"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "View Deal Details"
                            },
                            "url": f"https://platform.example.com/deals/{deal.id}"
                        }
                    ]
                }
            ]

            await self.slack_client.chat_postMessage(
                channel=channel_id,
                blocks=blocks,
                text=f"Welcome to {deal.title} deal channel"
            )

        except Exception as e:
            logger.error(f"Failed to send welcome message: {str(e)}")

    def _format_slack_message(self, notification: Notification) -> List[Dict[str, Any]]:
        """Format notification for Slack message blocks"""
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": notification.title
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": notification.content
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Sent at {notification.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            }
        ]

    def _format_workflow_message(self, workflow: WorkflowExecution) -> List[Dict[str, Any]]:
        """Format workflow execution for Slack message"""
        status_emoji = "✅" if workflow.status == "completed" else "❌"

        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{status_emoji} *Workflow {workflow.workflow_name}* {workflow.status}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Duration:* {workflow.execution_time_seconds}s\n*Started:* {workflow.started_at.strftime('%Y-%m-%d %H:%M:%S')}"
                }
            }
        ]

    def _format_deal_update_message(
        self,
        deal: Deal,
        message: str,
        urgency: str
    ) -> List[Dict[str, Any]]:
        """Format deal update message"""
        urgency_emoji = {"high": "🚨", "medium": "⚠️", "normal": "ℹ️"}.get(urgency, "ℹ️")

        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{urgency_emoji} *Deal Update: {deal.title}*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Stage: {deal.stage.replace('_', ' ').title()} | Value: ${deal.deal_value:,.0f}"
                    }
                ]
            }
        ]