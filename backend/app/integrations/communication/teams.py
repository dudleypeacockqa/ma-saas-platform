"""
Microsoft Teams Integration
Deal rooms, workflow automation, and collaboration hub
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import aiohttp
from msal import ConfidentialClientApplication

from ..core.integration_manager import (
    BaseIntegration, IntegrationConfig, SyncResult, WebhookEvent,
    SyncDirection, IntegrationStatus
)
from ...core.database import get_db
from ...models.deal import Deal
from ...models.deal_room import DealRoom
from ...models.message import Message
from ...models.notification import Notification

logger = logging.getLogger(__name__)


class TeamsIntegration(BaseIntegration):
    """Microsoft Teams integration for deal collaboration and automation"""

    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.access_token: Optional[str] = None
        self.client_app: Optional[ConfidentialClientApplication] = None
        self.graph_api_base = "https://graph.microsoft.com/v1.0"

    async def authenticate(self) -> bool:
        """Authenticate with Microsoft Graph API using OAuth2"""
        try:
            credentials = self.config.credentials

            # Initialize MSAL client
            self.client_app = ConfidentialClientApplication(
                client_id=credentials["client_id"],
                client_credential=credentials["client_secret"],
                authority=f"https://login.microsoftonline.com/{credentials['tenant_id']}"
            )

            # Get access token
            scopes = [
                "https://graph.microsoft.com/Team.ReadBasic.All",
                "https://graph.microsoft.com/Channel.ReadBasic.All",
                "https://graph.microsoft.com/ChatMessage.Send",
                "https://graph.microsoft.com/Group.ReadWrite.All",
                "https://graph.microsoft.com/Directory.Read.All"
            ]

            result = self.client_app.acquire_token_for_client(scopes=scopes)

            if "access_token" in result:
                self.access_token = result["access_token"]
                return True
            else:
                logger.error(f"Teams authentication failed: {result.get('error_description')}")
                return False

        except Exception as e:
            logger.error(f"Teams authentication error: {str(e)}")
            return False

    async def test_connection(self) -> bool:
        """Test Teams connection"""
        try:
            if not self.access_token:
                return False

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.graph_api_base}/me", headers=headers) as response:
                    return response.status == 200

        except Exception as e:
            logger.error(f"Teams connection test failed: {str(e)}")
            return False

    async def sync_data(self, direction: SyncDirection) -> SyncResult:
        """Synchronize Teams data with M&A platform"""
        sync_id = f"teams_sync_{datetime.now().timestamp()}"
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
            if not self.access_token:
                result.errors.append("Not authenticated with Teams")
                result.end_time = datetime.now()
                return result

            self.status = IntegrationStatus.SYNCING

            if direction in [SyncDirection.INBOUND, SyncDirection.BIDIRECTIONAL]:
                # Sync from Teams to M&A platform
                inbound_result = await self._sync_from_teams()
                result.records_processed += inbound_result["processed"]
                result.records_created += inbound_result["created"]
                result.records_updated += inbound_result["updated"]
                result.records_failed += inbound_result["failed"]
                result.errors.extend(inbound_result["errors"])

            if direction in [SyncDirection.OUTBOUND, SyncDirection.BIDIRECTIONAL]:
                # Sync from M&A platform to Teams
                outbound_result = await self._sync_to_teams()
                result.records_processed += outbound_result["processed"]
                result.records_created += outbound_result["created"]
                result.records_updated += outbound_result["updated"]
                result.records_failed += outbound_result["failed"]
                result.errors.extend(outbound_result["errors"])

            result.success = result.records_failed == 0
            result.end_time = datetime.now()
            self.last_sync = result.end_time
            self.status = IntegrationStatus.CONNECTED

            logger.info(f"Teams sync completed: {result.records_processed} processed, {result.records_failed} failed")

        except Exception as e:
            logger.error(f"Teams sync error: {str(e)}")
            result.errors.append(str(e))
            result.end_time = datetime.now()
            self.status = IntegrationStatus.ERROR

        return result

    async def _sync_from_teams(self) -> Dict[str, Any]:
        """Sync data from Teams to M&A platform"""
        result = {
            "processed": 0,
            "created": 0,
            "updated": 0,
            "failed": 0,
            "errors": []
        }

        try:
            # Sync teams and channels
            teams_result = await self._sync_teams_from_graph()
            for key in result:
                if key in teams_result:
                    result[key] += teams_result[key]

            # Sync messages from deal-related channels
            messages_result = await self._sync_messages_from_teams()
            for key in result:
                if key in messages_result:
                    result[key] += messages_result[key]

        except Exception as e:
            result["errors"].append(f"Inbound sync error: {str(e)}")
            result["failed"] += 1

        return result

    async def _sync_teams_from_graph(self) -> Dict[str, Any]:
        """Sync Teams teams and channels"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            async with aiohttp.ClientSession() as session:
                # Get all teams
                async with session.get(f"{self.graph_api_base}/teams", headers=headers) as response:
                    if response.status == 200:
                        teams_data = await response.json()
                        teams = teams_data.get("value", [])

                        async with get_db() as db:
                            for team in teams:
                                try:
                                    result["processed"] += 1

                                    # Check if this is a deal-related team
                                    if self._is_deal_team(team):
                                        deal_room = await self._find_or_create_deal_room(db, team)
                                        if deal_room:
                                            result["created"] += 1

                                        # Sync channels for this team
                                        channels_result = await self._sync_team_channels(
                                            session, headers, team["id"], deal_room
                                        )
                                        result["processed"] += channels_result["processed"]

                                except Exception as e:
                                    result["failed"] += 1
                                    result["errors"].append(f"Failed to sync team {team.get('id')}: {str(e)}")

                            await db.commit()

                    else:
                        result["errors"].append(f"Failed to fetch teams: {response.status}")

        except Exception as e:
            result["errors"].append(f"Teams sync error: {str(e)}")
            result["failed"] += 1

        return result

    async def _sync_team_channels(
        self,
        session: aiohttp.ClientSession,
        headers: Dict[str, str],
        team_id: str,
        deal_room: Optional[DealRoom]
    ) -> Dict[str, Any]:
        """Sync channels for a specific team"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            async with session.get(
                f"{self.graph_api_base}/teams/{team_id}/channels",
                headers=headers
            ) as response:
                if response.status == 200:
                    channels_data = await response.json()
                    channels = channels_data.get("value", [])

                    for channel in channels:
                        result["processed"] += 1
                        # Store channel information if needed
                        logger.info(f"Found channel: {channel.get('displayName')} in team {team_id}")

        except Exception as e:
            result["errors"].append(f"Channels sync error for team {team_id}: {str(e)}")
            result["failed"] += 1

        return result

    async def _sync_messages_from_teams(self) -> Dict[str, Any]:
        """Sync messages from Teams channels"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            # This would sync recent messages from deal-related channels
            # Implementation depends on specific requirements
            logger.info("Message sync from Teams channels - placeholder implementation")

        except Exception as e:
            result["errors"].append(f"Messages sync error: {str(e)}")
            result["failed"] += 1

        return result

    async def _sync_to_teams(self) -> Dict[str, Any]:
        """Sync M&A platform data to Teams"""
        result = {
            "processed": 0,
            "created": 0,
            "updated": 0,
            "failed": 0,
            "errors": []
        }

        try:
            # Create Teams for new deals
            deal_teams_result = await self._create_deal_teams()
            for key in result:
                if key in deal_teams_result:
                    result[key] += deal_teams_result[key]

            # Send notifications to Teams
            notifications_result = await self._send_teams_notifications()
            for key in result:
                if key in notifications_result:
                    result[key] += notifications_result[key]

        except Exception as e:
            result["errors"].append(f"Outbound sync error: {str(e)}")
            result["failed"] += 1

        return result

    async def _create_deal_teams(self) -> Dict[str, Any]:
        """Create Teams teams for new deals"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            async with get_db() as db:
                # Get deals that need Teams integration
                deals_query = select(Deal).where(
                    Deal.is_active == True,
                    Deal.teams_integration_status.is_(None)
                )
                result_deals = await db.execute(deals_query)
                deals = result_deals.scalars().all()

                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }

                async with aiohttp.ClientSession() as session:
                    for deal in deals:
                        try:
                            result["processed"] += 1

                            # Create team for deal
                            team_data = {
                                "template@odata.bind": "https://graph.microsoft.com/v1.0/teamsTemplates('standard')",
                                "displayName": f"Deal: {deal.title}",
                                "description": f"Collaboration space for {deal.title} deal",
                                "visibility": "private"
                            }

                            async with session.post(
                                f"{self.graph_api_base}/teams",
                                headers=headers,
                                json=team_data
                            ) as response:
                                if response.status == 201:
                                    team_info = await response.json()

                                    # Update deal with Teams information
                                    deal.teams_integration_status = "integrated"
                                    deal.teams_team_id = team_info.get("id")

                                    result["created"] += 1
                                    logger.info(f"Created Teams team for deal {deal.title}")

                                    # Create deal room record
                                    deal_room = DealRoom(
                                        deal_id=deal.id,
                                        platform="teams",
                                        external_id=team_info.get("id"),
                                        name=team_data["displayName"],
                                        description=team_data["description"],
                                        created_at=datetime.now()
                                    )
                                    db.add(deal_room)

                                else:
                                    result["failed"] += 1
                                    result["errors"].append(f"Failed to create team for deal {deal.id}: {response.status}")

                        except Exception as e:
                            result["failed"] += 1
                            result["errors"].append(f"Failed to create team for deal {deal.id}: {str(e)}")

                await db.commit()

        except Exception as e:
            result["errors"].append(f"Deal teams creation error: {str(e)}")
            result["failed"] += 1

        return result

    async def _send_teams_notifications(self) -> Dict[str, Any]:
        """Send notifications to Teams channels"""
        result = {"processed": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        try:
            async with get_db() as db:
                # Get pending notifications for Teams
                notifications_query = select(Notification).where(
                    Notification.channel == "teams",
                    Notification.status == "pending"
                )
                result_notifications = await db.execute(notifications_query)
                notifications = result_notifications.scalars().all()

                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }

                async with aiohttp.ClientSession() as session:
                    for notification in notifications:
                        try:
                            result["processed"] += 1

                            # Send message to Teams channel
                            message_data = {
                                "body": {
                                    "contentType": "html",
                                    "content": self._format_teams_message(notification)
                                }
                            }

                            # Get team and channel info from notification metadata
                            team_id = notification.metadata.get("team_id")
                            channel_id = notification.metadata.get("channel_id", "general")

                            if team_id:
                                async with session.post(
                                    f"{self.graph_api_base}/teams/{team_id}/channels/{channel_id}/messages",
                                    headers=headers,
                                    json=message_data
                                ) as response:
                                    if response.status == 201:
                                        notification.status = "sent"
                                        notification.sent_at = datetime.now()
                                        result["created"] += 1
                                    else:
                                        result["failed"] += 1
                                        result["errors"].append(f"Failed to send notification {notification.id}: {response.status}")

                        except Exception as e:
                            result["failed"] += 1
                            result["errors"].append(f"Failed to send notification {notification.id}: {str(e)}")

                await db.commit()

        except Exception as e:
            result["errors"].append(f"Teams notifications error: {str(e)}")
            result["failed"] += 1

        return result

    async def handle_webhook(self, event: WebhookEvent) -> bool:
        """Handle Teams webhook events"""
        try:
            event_type = event.event_type
            payload = event.payload

            if event_type == "chatMessage":
                await self._handle_chat_message_webhook(payload)
            elif event_type == "team.created":
                await self._handle_team_created_webhook(payload)
            elif event_type == "channel.created":
                await self._handle_channel_created_webhook(payload)

            return True

        except Exception as e:
            logger.error(f"Teams webhook handling error: {str(e)}")
            return False

    async def _handle_chat_message_webhook(self, payload: Dict[str, Any]):
        """Handle chat message webhook events"""
        # Process incoming chat messages for deal-related channels
        logger.info(f"Processing Teams chat message webhook: {payload}")

    async def _handle_team_created_webhook(self, payload: Dict[str, Any]):
        """Handle team created webhook events"""
        # Process team creation events
        logger.info(f"Processing Teams team created webhook: {payload}")

    async def _handle_channel_created_webhook(self, payload: Dict[str, Any]):
        """Handle channel created webhook events"""
        # Process channel creation events
        logger.info(f"Processing Teams channel created webhook: {payload}")

    async def get_supported_entities(self) -> List[str]:
        """Get list of entities this integration can sync"""
        return ["teams", "channels", "messages", "deal_rooms", "notifications"]

    # Deal-specific Teams operations

    async def create_deal_team(self, deal_id: str, team_name: str, members: List[str]) -> bool:
        """Create a dedicated Teams team for a deal"""
        try:
            if not self.access_token:
                return False

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            # Create team
            team_data = {
                "template@odata.bind": "https://graph.microsoft.com/v1.0/teamsTemplates('standard')",
                "displayName": team_name,
                "description": f"Collaboration space for deal {deal_id}",
                "visibility": "private"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.graph_api_base}/teams",
                    headers=headers,
                    json=team_data
                ) as response:
                    if response.status == 201:
                        team_info = await response.json()
                        team_id = team_info.get("id")

                        # Add members to team
                        for member_email in members:
                            await self._add_team_member(session, headers, team_id, member_email)

                        # Create standard channels
                        await self._create_deal_channels(session, headers, team_id)

                        return True

            return False

        except Exception as e:
            logger.error(f"Failed to create deal team: {str(e)}")
            return False

    async def _add_team_member(
        self,
        session: aiohttp.ClientSession,
        headers: Dict[str, str],
        team_id: str,
        member_email: str
    ):
        """Add a member to a Teams team"""
        try:
            member_data = {
                "@odata.type": "#microsoft.graph.aadUserConversationMember",
                "user@odata.bind": f"https://graph.microsoft.com/v1.0/users('{member_email}')",
                "roles": ["member"]
            }

            async with session.post(
                f"{self.graph_api_base}/teams/{team_id}/members",
                headers=headers,
                json=member_data
            ) as response:
                if response.status != 201:
                    logger.warning(f"Failed to add member {member_email} to team {team_id}")

        except Exception as e:
            logger.error(f"Failed to add team member {member_email}: {str(e)}")

    async def _create_deal_channels(
        self,
        session: aiohttp.ClientSession,
        headers: Dict[str, str],
        team_id: str
    ):
        """Create standard channels for a deal team"""
        try:
            channels_to_create = [
                {
                    "displayName": "Due Diligence",
                    "description": "Due diligence discussions and documents"
                },
                {
                    "displayName": "Financial Analysis",
                    "description": "Financial modeling and analysis"
                },
                {
                    "displayName": "Legal & Compliance",
                    "description": "Legal matters and compliance issues"
                },
                {
                    "displayName": "Integration Planning",
                    "description": "Post-acquisition integration planning"
                }
            ]

            for channel_data in channels_to_create:
                async with session.post(
                    f"{self.graph_api_base}/teams/{team_id}/channels",
                    headers=headers,
                    json=channel_data
                ) as response:
                    if response.status != 201:
                        logger.warning(f"Failed to create channel {channel_data['displayName']}")

        except Exception as e:
            logger.error(f"Failed to create deal channels: {str(e)}")

    async def send_deal_notification(
        self,
        deal_id: str,
        message: str,
        channel_name: str = "General"
    ) -> bool:
        """Send a notification to a deal team channel"""
        try:
            if not self.access_token:
                return False

            # Get deal room information
            async with get_db() as db:
                deal_room_query = select(DealRoom).where(
                    DealRoom.deal_id == deal_id,
                    DealRoom.platform == "teams"
                )
                result = await db.execute(deal_room_query)
                deal_room = result.scalar_one_or_none()

                if not deal_room:
                    return False

                team_id = deal_room.external_id

                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }

                message_data = {
                    "body": {
                        "contentType": "html",
                        "content": f"<div><strong>Deal Update:</strong><br/>{message}</div>"
                    }
                }

                async with aiohttp.ClientSession() as session:
                    # Get channel ID by name
                    channel_id = await self._get_channel_id_by_name(
                        session, headers, team_id, channel_name
                    )

                    if channel_id:
                        async with session.post(
                            f"{self.graph_api_base}/teams/{team_id}/channels/{channel_id}/messages",
                            headers=headers,
                            json=message_data
                        ) as response:
                            return response.status == 201

            return False

        except Exception as e:
            logger.error(f"Failed to send deal notification: {str(e)}")
            return False

    async def _get_channel_id_by_name(
        self,
        session: aiohttp.ClientSession,
        headers: Dict[str, str],
        team_id: str,
        channel_name: str
    ) -> Optional[str]:
        """Get channel ID by name"""
        try:
            async with session.get(
                f"{self.graph_api_base}/teams/{team_id}/channels",
                headers=headers
            ) as response:
                if response.status == 200:
                    channels_data = await response.json()
                    channels = channels_data.get("value", [])

                    for channel in channels:
                        if channel.get("displayName", "").lower() == channel_name.lower():
                            return channel.get("id")

        except Exception as e:
            logger.error(f"Failed to get channel ID: {str(e)}")

        return None

    # Helper methods

    async def _find_or_create_deal_room(self, db, team: Dict[str, Any]) -> Optional[DealRoom]:
        """Find or create a deal room for a Teams team"""
        try:
            team_id = team["id"]

            # Check if deal room already exists
            existing_room_query = select(DealRoom).where(
                DealRoom.external_id == team_id,
                DealRoom.platform == "teams"
            )
            result = await db.execute(existing_room_query)
            existing_room = result.scalar_one_or_none()

            if existing_room:
                return existing_room

            # Create new deal room if this is a deal-related team
            if self._is_deal_team(team):
                deal_room = DealRoom(
                    platform="teams",
                    external_id=team_id,
                    name=team.get("displayName", ""),
                    description=team.get("description", ""),
                    created_at=datetime.now()
                )
                db.add(deal_room)
                return deal_room

        except Exception as e:
            logger.error(f"Failed to find/create deal room: {str(e)}")

        return None

    def _is_deal_team(self, team: Dict[str, Any]) -> bool:
        """Check if a Teams team is deal-related"""
        team_name = team.get("displayName", "").lower()
        keywords = ["deal", "acquisition", "merger", "m&a", "transaction"]
        return any(keyword in team_name for keyword in keywords)

    def _format_teams_message(self, notification: Notification) -> str:
        """Format notification for Teams message"""
        return f"""
        <div>
            <h3>{notification.title}</h3>
            <p>{notification.content}</p>
            <small>Sent at {notification.created_at.strftime('%Y-%m-%d %H:%M:%S')}</small>
        </div>
        """