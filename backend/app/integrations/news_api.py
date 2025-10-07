"""
News API Integration
Market intelligence and company news monitoring for M&A opportunities
API Documentation: https://newsapi.org/docs
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
import asyncio
import re

logger = logging.getLogger(__name__)


class NewsAPI:
    """
    Integration with News API for market intelligence and company monitoring
    Tracks M&A news, company announcements, and industry trends
    """

    BASE_URL = "https://newsapi.org/v2"
    RATE_LIMIT_DELAY = 0.1  # Conservative rate limiting

    # M&A-related keywords for signal detection
    MA_KEYWORDS = [
        "acquisition", "merger", "buyout", "takeover", "acquired by",
        "merger with", "agrees to buy", "to acquire", "deal valued",
        "transaction valued", "purchase agreement"
    ]

    DISTRESS_KEYWORDS = [
        "bankruptcy", "administration", "liquidation", "insolvency",
        "receivership", "restructuring", "financial difficulties",
        "cash flow problems", "debt restructuring"
    ]

    GROWTH_KEYWORDS = [
        "expansion", "funding round", "investment", "valuation",
        "growth", "revenue increase", "profit surge", "market share"
    ]

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize News API client

        Args:
            api_key: News API key (required for access)
        """
        self.api_key = api_key or os.getenv("NEWS_API_KEY")

        if not self.api_key:
            logger.warning("NEWS_API_KEY not set - News intelligence disabled")

        self.session = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "100DaysAndBeyond/1.0"
            }
        )

        self.last_request_time = 0

    async def _rate_limit(self):
        """Enforce rate limiting"""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.RATE_LIMIT_DELAY:
            await asyncio.sleep(self.RATE_LIMIT_DELAY - time_since_last)

        self.last_request_time = asyncio.get_event_loop().time()

    async def _request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to News API

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            API response data
        """
        if not self.api_key:
            raise ValueError("News API key not configured")

        await self._rate_limit()

        url = f"{self.BASE_URL}/{endpoint}"

        request_params = params or {}
        request_params["apiKey"] = self.api_key

        try:
            response = await self.session.get(url, params=request_params)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"News API error: {e.response.status_code} - {e.response.text}")
            return {}
        except httpx.HTTPError as e:
            logger.error(f"News request error: {e}")
            return {}

    async def search_company_news(
        self,
        company_name: str,
        days_back: int = 30,
        language: str = "en",
        sort_by: str = "relevancy"
    ) -> List[Dict[str, Any]]:
        """
        Search for news articles about a specific company

        Args:
            company_name: Company name to search for
            days_back: Number of days to look back
            language: Language code (en, es, fr, etc.)
            sort_by: Sort by relevancy, popularity, or publishedAt

        Returns:
            List of news articles
        """
        try:
            from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")

            params = {
                "q": f'"{company_name}"',
                "from": from_date,
                "language": language,
                "sortBy": sort_by,
                "pageSize": 100
            }

            response = await self._request("everything", params)

            articles = response.get("articles", [])

            # Enrich articles with signal detection
            enriched_articles = []
            for article in articles:
                enriched = {
                    "title": article.get("title"),
                    "description": article.get("description"),
                    "content": article.get("content"),
                    "url": article.get("url"),
                    "source": article.get("source", {}).get("name"),
                    "published_at": article.get("publishedAt"),
                    "author": article.get("author"),
                    "signals": self._detect_signals(article)
                }
                enriched_articles.append(enriched)

            return enriched_articles

        except Exception as e:
            logger.error(f"Error searching company news for {company_name}: {e}")
            return []

    async def search_ma_news(
        self,
        industry: Optional[str] = None,
        days_back: int = 7,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """
        Search for M&A news and transactions

        Args:
            industry: Industry filter (optional)
            days_back: Number of days to look back
            language: Language code

        Returns:
            List of M&A-related news articles
        """
        try:
            from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")

            # Build query
            query_parts = ["merger OR acquisition OR takeover OR buyout"]
            if industry:
                query_parts.append(f'AND "{industry}"')

            query = " ".join(query_parts)

            params = {
                "q": query,
                "from": from_date,
                "language": language,
                "sortBy": "publishedAt",
                "pageSize": 100
            }

            response = await self._request("everything", params)

            articles = response.get("articles", [])

            # Enrich with signal detection
            enriched_articles = []
            for article in articles:
                signals = self._detect_signals(article)

                # Only include articles with M&A signals
                if signals.get("ma_activity"):
                    enriched = {
                        "title": article.get("title"),
                        "description": article.get("description"),
                        "content": article.get("content"),
                        "url": article.get("url"),
                        "source": article.get("source", {}).get("name"),
                        "published_at": article.get("publishedAt"),
                        "author": article.get("author"),
                        "signals": signals,
                        "companies_mentioned": self._extract_company_names(article)
                    }
                    enriched_articles.append(enriched)

            return enriched_articles

        except Exception as e:
            logger.error(f"Error searching M&A news: {e}")
            return []

    async def search_industry_news(
        self,
        industry: str,
        days_back: int = 7,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """
        Search for industry-specific news and trends

        Args:
            industry: Industry name or keyword
            days_back: Number of days to look back
            language: Language code

        Returns:
            List of industry news articles
        """
        try:
            from_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")

            params = {
                "q": industry,
                "from": from_date,
                "language": language,
                "sortBy": "relevancy",
                "pageSize": 100
            }

            response = await self._request("everything", params)

            articles = response.get("articles", [])

            # Enrich articles
            enriched_articles = []
            for article in articles:
                enriched = {
                    "title": article.get("title"),
                    "description": article.get("description"),
                    "content": article.get("content"),
                    "url": article.get("url"),
                    "source": article.get("source", {}).get("name"),
                    "published_at": article.get("publishedAt"),
                    "author": article.get("author"),
                    "signals": self._detect_signals(article)
                }
                enriched_articles.append(enriched)

            return enriched_articles

        except Exception as e:
            logger.error(f"Error searching industry news for {industry}: {e}")
            return []

    async def get_top_headlines(
        self,
        category: Optional[str] = "business",
        country: str = "us",
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get top business headlines

        Args:
            category: News category (business, technology, etc.)
            country: Country code (us, gb, etc.)
            limit: Number of headlines to return

        Returns:
            List of top headline articles
        """
        try:
            params = {
                "category": category,
                "country": country,
                "pageSize": limit
            }

            response = await self._request("top-headlines", params)

            articles = response.get("articles", [])

            enriched_articles = []
            for article in articles:
                enriched = {
                    "title": article.get("title"),
                    "description": article.get("description"),
                    "url": article.get("url"),
                    "source": article.get("source", {}).get("name"),
                    "published_at": article.get("publishedAt"),
                    "signals": self._detect_signals(article)
                }
                enriched_articles.append(enriched)

            return enriched_articles

        except Exception as e:
            logger.error(f"Error getting top headlines: {e}")
            return []

    def _detect_signals(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect M&A-relevant signals in article content

        Args:
            article: News article data

        Returns:
            Detected signals and categories
        """
        signals = {
            "ma_activity": False,
            "distress": False,
            "growth": False,
            "keywords_found": []
        }

        # Combine title, description, and content for analysis
        text_parts = [
            article.get("title", ""),
            article.get("description", ""),
            article.get("content", "")
        ]
        full_text = " ".join(text_parts).lower()

        # Check for M&A signals
        for keyword in self.MA_KEYWORDS:
            if keyword.lower() in full_text:
                signals["ma_activity"] = True
                signals["keywords_found"].append(keyword)

        # Check for distress signals
        for keyword in self.DISTRESS_KEYWORDS:
            if keyword.lower() in full_text:
                signals["distress"] = True
                signals["keywords_found"].append(keyword)

        # Check for growth signals
        for keyword in self.GROWTH_KEYWORDS:
            if keyword.lower() in full_text:
                signals["growth"] = True
                signals["keywords_found"].append(keyword)

        return signals

    def _extract_company_names(self, article: Dict[str, Any]) -> List[str]:
        """
        Extract company names mentioned in article
        (Simplified implementation - would use NER in production)

        Args:
            article: News article data

        Returns:
            List of potential company names
        """
        companies = []

        text = f"{article.get('title', '')} {article.get('description', '')}"

        # Simple pattern matching for capitalized sequences
        # In production, use spaCy or similar NER tool
        pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Inc|LLC|Ltd|Corp|Corporation|Group|Holdings))?)\b'
        matches = re.findall(pattern, text)

        # Filter out common words
        common_words = {"The", "A", "An", "In", "On", "At", "By"}
        companies = [m for m in matches if m not in common_words]

        return list(set(companies))[:10]  # Return unique names, max 10

    async def monitor_company(
        self,
        company_name: str,
        alert_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Monitor a company for significant news events

        Args:
            company_name: Company name to monitor
            alert_keywords: Additional keywords to trigger alerts

        Returns:
            Monitoring summary with alerts
        """
        monitoring_result = {
            "company_name": company_name,
            "monitored_at": datetime.utcnow().isoformat(),
            "recent_articles_count": 0,
            "alerts": [],
            "signals_detected": {
                "ma_activity": False,
                "distress": False,
                "growth": False
            },
            "latest_articles": []
        }

        try:
            # Search for recent news (last 7 days)
            articles = await self.search_company_news(company_name, days_back=7)

            monitoring_result["recent_articles_count"] = len(articles)
            monitoring_result["latest_articles"] = articles[:5]  # Keep top 5

            # Analyze signals
            for article in articles:
                signals = article.get("signals", {})

                if signals.get("ma_activity"):
                    monitoring_result["signals_detected"]["ma_activity"] = True
                    monitoring_result["alerts"].append({
                        "type": "ma_activity",
                        "title": article.get("title"),
                        "url": article.get("url"),
                        "published_at": article.get("published_at")
                    })

                if signals.get("distress"):
                    monitoring_result["signals_detected"]["distress"] = True
                    monitoring_result["alerts"].append({
                        "type": "distress",
                        "title": article.get("title"),
                        "url": article.get("url"),
                        "published_at": article.get("published_at")
                    })

                if signals.get("growth"):
                    monitoring_result["signals_detected"]["growth"] = True

                # Check custom alert keywords
                if alert_keywords:
                    text = f"{article.get('title', '')} {article.get('description', '')}".lower()
                    for keyword in alert_keywords:
                        if keyword.lower() in text:
                            monitoring_result["alerts"].append({
                                "type": "custom",
                                "keyword": keyword,
                                "title": article.get("title"),
                                "url": article.get("url"),
                                "published_at": article.get("published_at")
                            })

        except Exception as e:
            logger.error(f"Error monitoring company {company_name}: {e}")

        return monitoring_result

    async def get_market_sentiment(
        self,
        industry: str,
        days_back: int = 7
    ) -> Dict[str, Any]:
        """
        Analyze market sentiment for an industry

        Args:
            industry: Industry name
            days_back: Number of days to analyze

        Returns:
            Sentiment analysis summary
        """
        sentiment = {
            "industry": industry,
            "period_days": days_back,
            "total_articles": 0,
            "ma_activity_count": 0,
            "distress_signal_count": 0,
            "growth_signal_count": 0,
            "sentiment_score": 0.0,  # -1 to 1 scale
            "trending_topics": []
        }

        try:
            articles = await self.search_industry_news(industry, days_back=days_back)

            sentiment["total_articles"] = len(articles)

            for article in articles:
                signals = article.get("signals", {})

                if signals.get("ma_activity"):
                    sentiment["ma_activity_count"] += 1

                if signals.get("distress"):
                    sentiment["distress_signal_count"] += 1
                    sentiment["sentiment_score"] -= 0.1

                if signals.get("growth"):
                    sentiment["growth_signal_count"] += 1
                    sentiment["sentiment_score"] += 0.1

            # Normalize sentiment score
            if sentiment["total_articles"] > 0:
                sentiment["sentiment_score"] = max(-1.0, min(1.0, sentiment["sentiment_score"]))

        except Exception as e:
            logger.error(f"Error analyzing market sentiment for {industry}: {e}")

        return sentiment

    async def close(self):
        """Close HTTP session"""
        await self.session.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# Singleton instance
_news_api: Optional[NewsAPI] = None


def get_news_api() -> NewsAPI:
    """Get or create News API instance"""
    global _news_api
    if _news_api is None:
        _news_api = NewsAPI()
    return _news_api
