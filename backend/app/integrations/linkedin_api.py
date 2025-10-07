"""
LinkedIn Integration Service
Handles LinkedIn Sales Navigator API and automation with compliance
"""
import asyncio
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import hashlib
import hmac
import json
from urllib.parse import quote
import logging

from app.core.config import settings
from app.models.prospects import Prospect, ProspectSource, IndustrySegment

logger = logging.getLogger(__name__)

class LinkedInRateLimiter:
    """Rate limiting for LinkedIn API to avoid bans"""

    def __init__(self):
        self.connection_requests_per_day = 100
        self.messages_per_day = 150
        self.searches_per_day = 300
        self.profile_views_per_day = 500

        self._request_counts = {}
        self._last_reset = datetime.utcnow()

    async def check_rate_limit(self, action: str) -> bool:
        """Check if action is within rate limits"""
        self._reset_if_needed()

        limits = {
            'connection': self.connection_requests_per_day,
            'message': self.messages_per_day,
            'search': self.searches_per_day,
            'profile_view': self.profile_views_per_day
        }

        current_count = self._request_counts.get(action, 0)
        limit = limits.get(action, 100)

        if current_count >= limit:
            logger.warning(f"LinkedIn rate limit reached for {action}: {current_count}/{limit}")
            return False

        self._request_counts[action] = current_count + 1
        return True

    def _reset_if_needed(self):
        """Reset counts if a day has passed"""
        now = datetime.utcnow()
        if (now - self._last_reset).days >= 1:
            self._request_counts = {}
            self._last_reset = now

    async def wait_if_needed(self, action: str):
        """Add delays between actions to appear human"""
        delays = {
            'connection': (5, 15),  # 5-15 seconds
            'message': (10, 30),    # 10-30 seconds
            'search': (3, 8),       # 3-8 seconds
            'profile_view': (2, 5)  # 2-5 seconds
        }

        min_delay, max_delay = delays.get(action, (2, 5))
        import random
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)

class LinkedInAPI:
    """LinkedIn Sales Navigator API integration"""

    def __init__(self):
        self.api_key = settings.LINKEDIN_API_KEY
        self.api_secret = settings.LINKEDIN_API_SECRET
        self.access_token = None
        self.rate_limiter = LinkedInRateLimiter()
        self.base_url = "https://api.linkedin.com/v2"
        self.sales_nav_url = "https://api.linkedin.com/v2/salesNavigatorApi"

    async def authenticate(self) -> bool:
        """Authenticate with LinkedIn API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://www.linkedin.com/oauth/v2/accessToken",
                    data={
                        'grant_type': 'client_credentials',
                        'client_id': self.api_key,
                        'client_secret': self.api_secret
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data['access_token']
                    return True

                logger.error(f"LinkedIn authentication failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"LinkedIn authentication error: {e}")
            return False

    async def search_prospects(
        self,
        keywords: List[str],
        industry: Optional[IndustrySegment] = None,
        company_size: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search for prospects using Sales Navigator"""

        if not await self.rate_limiter.check_rate_limit('search'):
            return []

        if not self.access_token:
            await self.authenticate()

        # Build search query
        query_parts = []
        if keywords:
            query_parts.append(' '.join(keywords))

        filters = []
        if industry:
            industry_mapping = {
                IndustrySegment.PRIVATE_EQUITY: 'Private Equity',
                IndustrySegment.INVESTMENT_BANKING: 'Investment Banking',
                IndustrySegment.VENTURE_CAPITAL: 'Venture Capital',
                IndustrySegment.BUSINESS_BROKER: 'Business Brokerage'
            }
            if industry in industry_mapping:
                filters.append(f"industry:{industry_mapping[industry]}")

        if company_size:
            filters.append(f"company_size:{company_size}")

        if location:
            filters.append(f"location:{location}")

        query = ' AND '.join(query_parts + filters)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.sales_nav_url}/search/people",
                    headers={
                        'Authorization': f'Bearer {self.access_token}',
                        'X-Restli-Protocol-Version': '2.0.0'
                    },
                    params={
                        'q': 'search',
                        'keywords': quote(query),
                        'count': min(limit, 50),  # LinkedIn limits per page
                        'start': 0
                    }
                )

                await self.rate_limiter.wait_if_needed('search')

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_search_results(data)

                logger.error(f"LinkedIn search failed: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"LinkedIn search error: {e}")
            return []

    def _parse_search_results(self, data: Dict) -> List[Dict[str, Any]]:
        """Parse LinkedIn search results"""
        results = []

        for element in data.get('elements', []):
            profile = {
                'linkedin_id': element.get('publicIdentifier'),
                'first_name': element.get('firstName'),
                'last_name': element.get('lastName'),
                'headline': element.get('headline'),
                'company': element.get('companyName'),
                'title': element.get('title'),
                'location': element.get('locationName'),
                'linkedin_url': f"https://linkedin.com/in/{element.get('publicIdentifier')}",
                'industry': element.get('industry'),
                'connections': element.get('numConnections', 0)
            }

            # Extract email if available (Sales Navigator feature)
            if 'contactInfo' in element:
                profile['email'] = element['contactInfo'].get('emailAddress')

            results.append(profile)

        return results

    async def send_connection_request(
        self,
        linkedin_id: str,
        message: str
    ) -> bool:
        """Send a personalized connection request"""

        if not await self.rate_limiter.check_rate_limit('connection'):
            return False

        if not self.access_token:
            await self.authenticate()

        # LinkedIn limits connection messages to 300 characters
        if len(message) > 300:
            message = message[:297] + "..."

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/invitations",
                    headers={
                        'Authorization': f'Bearer {self.access_token}',
                        'Content-Type': 'application/json',
                        'X-Restli-Protocol-Version': '2.0.0'
                    },
                    json={
                        'invitee': {
                            'com.linkedin.voyager.growth.invitation.InviteeProfile': {
                                'publicIdentifier': linkedin_id
                            }
                        },
                        'message': message
                    }
                )

                await self.rate_limiter.wait_if_needed('connection')

                if response.status_code in [200, 201]:
                    logger.info(f"Connection request sent to {linkedin_id}")
                    return True

                logger.error(f"Connection request failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Connection request error: {e}")
            return False

    async def send_message(
        self,
        linkedin_id: str,
        subject: str,
        message: str
    ) -> bool:
        """Send a direct message to a connection"""

        if not await self.rate_limiter.check_rate_limit('message'):
            return False

        if not self.access_token:
            await self.authenticate()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers={
                        'Authorization': f'Bearer {self.access_token}',
                        'Content-Type': 'application/json',
                        'X-Restli-Protocol-Version': '2.0.0'
                    },
                    json={
                        'recipients': [linkedin_id],
                        'subject': subject,
                        'body': message,
                        'messageType': 'MEMBER_TO_MEMBER'
                    }
                )

                await self.rate_limiter.wait_if_needed('message')

                if response.status_code in [200, 201]:
                    logger.info(f"Message sent to {linkedin_id}")
                    return True

                logger.error(f"Message send failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Message send error: {e}")
            return False

    async def get_profile(self, linkedin_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed profile information"""

        if not await self.rate_limiter.check_rate_limit('profile_view'):
            return None

        if not self.access_token:
            await self.authenticate()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/people/(id:{linkedin_id})",
                    headers={
                        'Authorization': f'Bearer {self.access_token}',
                        'X-Restli-Protocol-Version': '2.0.0'
                    },
                    params={
                        'projection': '(id,firstName,lastName,headline,summary,positions,educations,skills,emailAddress)'
                    }
                )

                await self.rate_limiter.wait_if_needed('profile_view')

                if response.status_code == 200:
                    return response.json()

                logger.error(f"Profile fetch failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Profile fetch error: {e}")
            return None

    async def track_profile_views(self) -> List[Dict[str, Any]]:
        """Get list of who viewed your profile (for lead identification)"""

        if not self.access_token:
            await self.authenticate()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/me/profile-views",
                    headers={
                        'Authorization': f'Bearer {self.access_token}',
                        'X-Restli-Protocol-Version': '2.0.0'
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    viewers = []
                    for viewer in data.get('elements', []):
                        viewers.append({
                            'linkedin_id': viewer.get('viewerPublicIdentifier'),
                            'name': f"{viewer.get('viewerFirstName', '')} {viewer.get('viewerLastName', '')}",
                            'headline': viewer.get('viewerHeadline'),
                            'company': viewer.get('viewerCompanyName'),
                            'viewed_at': viewer.get('viewedAt')
                        })
                    return viewers

                return []

        except Exception as e:
            logger.error(f"Profile views fetch error: {e}")
            return []

class LinkedInProspectEnricher:
    """Enrich prospect data using LinkedIn"""

    def __init__(self):
        self.api = LinkedInAPI()

    async def enrich_prospect(self, prospect: Prospect) -> Dict[str, Any]:
        """Enrich prospect data with LinkedIn information"""

        enriched_data = {}

        # Try to find LinkedIn profile
        if not prospect.linkedin_id and (prospect.email or (prospect.first_name and prospect.last_name)):
            search_terms = []
            if prospect.first_name and prospect.last_name:
                search_terms.append(f"{prospect.first_name} {prospect.last_name}")
            if prospect.company:
                search_terms.append(prospect.company)

            results = await self.api.search_prospects(
                keywords=search_terms,
                limit=5
            )

            # Match by email or name similarity
            for result in results:
                if result.get('email') == prospect.email:
                    enriched_data['linkedin_id'] = result['linkedin_id']
                    enriched_data['linkedin_url'] = result['linkedin_url']
                    break
                elif self._name_similarity(
                    prospect.first_name,
                    prospect.last_name,
                    result.get('first_name'),
                    result.get('last_name')
                ) > 0.8:
                    enriched_data['linkedin_id'] = result['linkedin_id']
                    enriched_data['linkedin_url'] = result['linkedin_url']
                    break

        # Get full profile if we have LinkedIn ID
        linkedin_id = enriched_data.get('linkedin_id') or prospect.linkedin_id
        if linkedin_id:
            profile = await self.api.get_profile(linkedin_id)
            if profile:
                enriched_data.update(self._extract_profile_data(profile))

        return enriched_data

    def _name_similarity(self, first1: str, last1: str, first2: str, last2: str) -> float:
        """Calculate name similarity score"""
        if not all([first1, last1, first2, last2]):
            return 0.0

        # Simple similarity based on exact match and initials
        if first1.lower() == first2.lower() and last1.lower() == last2.lower():
            return 1.0

        if first1[0].lower() == first2[0].lower() and last1.lower() == last2.lower():
            return 0.8

        return 0.0

    def _extract_profile_data(self, profile: Dict) -> Dict[str, Any]:
        """Extract relevant data from LinkedIn profile"""

        data = {
            'linkedin_headline': profile.get('headline'),
            'linkedin_summary': profile.get('summary'),
            'linkedin_connections': profile.get('numConnections', 0)
        }

        # Extract current position
        positions = profile.get('positions', {}).get('values', [])
        if positions:
            current = positions[0]
            data['title'] = current.get('title')
            data['company'] = current.get('company', {}).get('name')

        # Extract skills
        skills = profile.get('skills', {}).get('values', [])
        if skills:
            data['skills'] = [skill.get('name') for skill in skills[:10]]

        return data

class LinkedInComplianceChecker:
    """Ensure LinkedIn automation compliance"""

    @staticmethod
    def validate_connection_message(message: str) -> tuple[bool, str]:
        """Validate connection request message"""

        if len(message) > 300:
            return False, "Message exceeds 300 character limit"

        # Check for spam indicators
        spam_patterns = [
            'buy now',
            'limited time',
            'act now',
            'click here',
            'free money',
            'guaranteed'
        ]

        message_lower = message.lower()
        for pattern in spam_patterns:
            if pattern in message_lower:
                return False, f"Message contains spam indicator: {pattern}"

        # Ensure personalization
        if not any(token in message for token in ['{first_name}', '{company}', '{title}']):
            return False, "Message lacks personalization tokens"

        return True, "Message is compliant"

    @staticmethod
    def validate_daily_limits(action_counts: Dict[str, int]) -> bool:
        """Check if daily limits are exceeded"""

        limits = {
            'connections': 100,
            'messages': 150,
            'searches': 300,
            'profile_views': 500
        }

        for action, count in action_counts.items():
            if count >= limits.get(action, 100):
                return False

        return True