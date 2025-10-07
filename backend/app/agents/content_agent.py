import anthropic
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os


class ContentCreationAgent:
    """
    AI-powered Content Creation Agent using Claude API for generating
    podcast show notes, social media posts, blog articles, and marketing content.
    """

    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.model = "claude-3-5-sonnet-20241022"
        self.brand_voice = """Professional, authoritative, practical, and results-focused.
Target audience: Private equity firms, investment bankers, business buyers/sellers.
Platform: 100 Days and Beyond - M&A deal management SaaS."""

    async def generate_podcast_show_notes(
        self,
        transcript: str,
        episode_title: str,
        guest_name: Optional[str] = None,
        guest_company: Optional[str] = None,
        episode_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive podcast show notes from transcript.

        Returns:
            - title: SEO-optimized title
            - summary: Episode summary
            - timestamps: List of topic timestamps
            - key_takeaways: Main insights
            - guest_bio: Guest information
            - seo_description: Meta description
            - resources: Mentioned resources/links
        """
        prompt = f"""Generate comprehensive podcast show notes for the "100 Days and Beyond" M&A podcast.

EPISODE DETAILS:
{f'Episode #{episode_number}: ' if episode_number else ''}{episode_title}
{f'Guest: {guest_name}' if guest_name else ''}
{f'Company: {guest_company}' if guest_company else ''}

TRANSCRIPT:
{transcript[:15000]}  # Limit for API

INSTRUCTIONS:
Create professional show notes with:

1. SEO-OPTIMIZED TITLE (60 chars max)
2. EPISODE SUMMARY (150-200 words)
3. TIMESTAMPS (Format: "00:00 - Topic")
   - Extract 8-12 key moments from the transcript
4. KEY TAKEAWAYS (5-7 bullet points)
   - Actionable insights for M&A professionals
5. GUEST BIO (if applicable, 100-150 words)
6. SEO DESCRIPTION (155 chars max)
7. RESOURCES MENTIONED
   - Books, tools, companies, websites mentioned
8. CALL-TO-ACTION
   - Encourage SaaS trial signup

Brand voice: {self.brand_voice}

Return as JSON with keys: title, summary, timestamps (array), key_takeaways (array),
guest_bio, seo_description, resources (array), cta"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        # Parse JSON response
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback: return structured response
            return {
                "title": episode_title,
                "summary": response_text[:500],
                "timestamps": [],
                "key_takeaways": [],
                "guest_bio": "",
                "seo_description": response_text[:155],
                "resources": [],
                "cta": "Start your free trial at 100daysandbeyond.com"
            }

    async def generate_linkedin_post(
        self,
        source_content: str,
        focus_topic: Optional[str] = None,
        include_hashtags: bool = True
    ) -> Dict[str, str]:
        """
        Generate professional LinkedIn post for thought leadership.

        Returns:
            - post_text: LinkedIn post (1300 chars max)
            - hashtags: Relevant hashtags
        """
        prompt = f"""Create a professional LinkedIn post for the "100 Days and Beyond" M&A platform.

SOURCE CONTENT:
{source_content[:5000]}

{f'FOCUS ON: {focus_topic}' if focus_topic else ''}

REQUIREMENTS:
- Professional, thought leadership tone
- Target audience: Private equity, investment bankers, M&A professionals
- Length: 1200-1300 characters
- Include compelling hook in first line
- Add value and insights
- End with call-to-action
{f'- Include 5-7 relevant hashtags' if include_hashtags else ''}

Brand voice: {self.brand_voice}

Return as JSON with keys: post_text, hashtags (array)"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        try:
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            return json.loads(response_text)
        except json.JSONDecodeError:
            return {
                "post_text": response_text[:1300],
                "hashtags": ["#MandA", "#PrivateEquity", "#DealMaking", "#BusinessAcquisition"]
            }

    async def generate_twitter_thread(
        self,
        source_content: str,
        num_tweets: int = 5
    ) -> Dict[str, List[str]]:
        """
        Generate Twitter thread with key insights.

        Returns:
            - tweets: List of tweet texts (280 chars each)
        """
        prompt = f"""Create a Twitter thread (X post) about M&A insights.

SOURCE CONTENT:
{source_content[:5000]}

REQUIREMENTS:
- Create {num_tweets} tweets
- First tweet: Compelling hook with a question or stat
- Tweets 2-{num_tweets-1}: Key insights, one per tweet
- Last tweet: Call-to-action with link
- Each tweet max 270 characters (leave room for thread numbering)
- Include relevant emojis strategically
- Professional but engaging tone

Brand voice: {self.brand_voice}

Return as JSON with key: tweets (array of strings)"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        try:
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            return json.loads(response_text)
        except json.JSONDecodeError:
            return {"tweets": [response_text[:270]]}

    async def generate_blog_article(
        self,
        topic: str,
        source_content: Optional[str] = None,
        target_word_count: int = 2000,
        seo_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate long-form blog article optimized for SEO.

        Returns:
            - title: SEO-optimized title
            - slug: URL slug
            - meta_description: SEO meta description
            - content: Full article in markdown
            - excerpt: Article excerpt
            - seo_keywords: Keyword list
        """
        keywords = seo_keywords or ["M&A", "mergers and acquisitions", "deal management", "due diligence"]

        prompt = f"""Write a comprehensive blog article for the 100 Days and Beyond M&A platform.

TOPIC: {topic}

{f'SOURCE CONTENT/RESEARCH:{source_content[:8000]}' if source_content else ''}

SEO KEYWORDS: {', '.join(keywords)}

REQUIREMENTS:
- Target length: {target_word_count} words
- SEO-optimized with H2 and H3 headings
- Include introduction, body sections, conclusion
- Professional, authoritative tone for M&A professionals
- Include statistics and actionable insights
- Add call-to-action for SaaS trial at end
- Use keywords naturally throughout
- Include bullet points and numbered lists where appropriate

STRUCTURE:
1. Introduction (150-200 words)
2. 3-5 main sections with H2 headings
3. Subsections with H3 headings
4. Conclusion with CTA (100-150 words)

Brand voice: {self.brand_voice}

Return as JSON with keys: title, slug, meta_description, content (markdown), excerpt, seo_keywords (array)"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        try:
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            return json.loads(response_text)
        except json.JSONDecodeError:
            return {
                "title": topic,
                "slug": topic.lower().replace(" ", "-"),
                "meta_description": f"Learn about {topic} in M&A deals.",
                "content": response_text,
                "excerpt": response_text[:300],
                "seo_keywords": keywords
            }

    async def generate_youtube_description(
        self,
        video_title: str,
        transcript: str,
        timestamps: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, str]:
        """
        Generate YouTube video description with timestamps.

        Returns:
            - description: Full YouTube description
            - tags: Video tags
        """
        timestamp_text = ""
        if timestamps:
            timestamp_text = "\n".join([f"{t['time']} - {t['topic']}" for t in timestamps])

        prompt = f"""Create a YouTube video description for the "100 Days and Beyond" podcast.

VIDEO TITLE: {video_title}

TRANSCRIPT SUMMARY:
{transcript[:5000]}

{f'TIMESTAMPS:{timestamp_text}' if timestamps else ''}

REQUIREMENTS:
- Engaging description (300-500 words)
- Include timestamps if provided
- Add links to SaaS platform
- Include guest info if applicable
- Social media links
- Call-to-action for subscriptions and platform trial
- 10-15 relevant tags for YouTube SEO

Brand voice: {self.brand_voice}

Return as JSON with keys: description, tags (array)"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        try:
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            return json.loads(response_text)
        except json.JSONDecodeError:
            return {
                "description": response_text,
                "tags": ["M&A", "Mergers and Acquisitions", "Private Equity", "Business", "Investing"]
            }

    async def generate_newsletter_content(
        self,
        recent_episodes: List[Dict[str, str]],
        market_insights: Optional[str] = None,
        deal_highlights: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Generate email newsletter content.

        Returns:
            - subject_line: Email subject
            - preview_text: Email preview
            - content: Newsletter HTML/Markdown
        """
        episodes_text = "\n".join([
            f"- {ep.get('title', '')} ({ep.get('guest', 'N/A')})"
            for ep in recent_episodes
        ])

        prompt = f"""Create a weekly email newsletter for "100 Days and Beyond" subscribers.

RECENT PODCAST EPISODES:
{episodes_text}

{f'MARKET INSIGHTS:{market_insights}' if market_insights else ''}

{f'DEAL HIGHLIGHTS:{chr(10).join(deal_highlights)}' if deal_highlights else ''}

REQUIREMENTS:
- Compelling subject line (50 chars max)
- Preview text (90 chars max)
- Newsletter content in markdown
- Sections: Welcome, Recent Episodes, Market Insights, Featured Deals, CTA
- Professional, valuable content for M&A professionals
- Include links to platform and episodes
- Subscriber-only insights teaser
- Strong call-to-action for engagement

Brand voice: {self.brand_voice}

Return as JSON with keys: subject_line, preview_text, content (markdown)"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        try:
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            return json.loads(response_text)
        except json.JSONDecodeError:
            return {
                "subject_line": "This Week in M&A: Insights from 100 Days and Beyond",
                "preview_text": "Your weekly dose of M&A insights and deal intelligence",
                "content": response_text
            }

    async def validate_content_quality(self, content: str, content_type: str) -> Dict[str, Any]:
        """
        Validate content quality and suggest improvements.

        Returns:
            - quality_score: 0-100
            - suggestions: List of improvement suggestions
            - seo_score: SEO optimization score
        """
        prompt = f"""Analyze this {content_type} content for quality and provide feedback.

CONTENT:
{content[:5000]}

Evaluate:
1. Clarity and readability
2. Value for target audience (M&A professionals)
3. SEO optimization
4. Call-to-action effectiveness
5. Brand voice alignment

Return as JSON with keys: quality_score (0-100), suggestions (array), seo_score (0-100), feedback (string)"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        try:
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            return json.loads(response_text)
        except json.JSONDecodeError:
            return {
                "quality_score": 75,
                "suggestions": ["Review content structure"],
                "seo_score": 70,
                "feedback": response_text
            }
