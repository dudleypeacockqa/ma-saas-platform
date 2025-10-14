# Content Creation Agent for M&A SaaS Platform

## Overview

The Content Creation Agent is an AI-powered system that automates content generation for the "100 Days and Beyond" M&A podcast and platform using Claude AI.

## Features

### 1. Podcast Show Notes Generation

- Automated show notes from podcast transcripts
- SEO-optimized titles and descriptions
- Timestamps extraction
- Key takeaways summarization
- Guest bio generation
- Resource links compilation

### 2. Social Media Content

- **LinkedIn Posts**: Professional thought leadership content (1300 chars)
- **Twitter/X Threads**: Multi-tweet threads with insights
- **YouTube Descriptions**: Video descriptions with timestamps
- **Instagram Captions**: Engaging captions for video clips

### 3. Blog Articles

- Long-form articles (2000-2500 words)
- SEO optimization with keyword targeting
- Professional M&A industry tone
- Structured with H2/H3 headings
- Call-to-action for SaaS signup

### 4. Email Newsletters

- Weekly newsletter generation
- Episode summaries
- Market insights
- Deal highlights
- Subscriber engagement

### 5. Content Quality Validation

- Quality scoring (0-100)
- SEO optimization analysis
- Improvement suggestions
- Brand voice alignment check

## Architecture

### Backend Components

#### Models (`backend/app/models/content.py`)

- **Content**: Main content storage with status tracking
- **PodcastEpisode**: Podcast-specific data and transcripts
- **ContentTemplate**: Reusable content templates

#### Agent (`backend/app/agents/content_agent.py`)

- **ContentCreationAgent**: Core AI agent using Claude API
  - `generate_podcast_show_notes()`
  - `generate_linkedin_post()`
  - `generate_twitter_thread()`
  - `generate_blog_article()`
  - `generate_youtube_description()`
  - `generate_newsletter_content()`
  - `validate_content_quality()`

#### Service Layer (`backend/app/services/content_service.py`)

- **ContentService**: Business logic and orchestration
  - CRUD operations
  - AI content generation workflows
  - Content validation
  - Multi-tenant isolation

#### API (`backend/app/api/content.py`)

- RESTful endpoints for content management
- AI generation endpoints
- Content validation API
- Multi-tenant authentication

### Frontend Components

#### ContentDashboard (`frontend/src/components/ContentDashboard.tsx`)

- Podcast episode management
- AI content generation interface
- Content library with filtering
- Real-time previews
- Status tracking

## API Endpoints

### Content Management

- `POST /api/content/` - Create content
- `GET /api/content/` - List contents (with filters)
- `GET /api/content/{id}` - Get content by ID
- `PATCH /api/content/{id}` - Update content
- `DELETE /api/content/{id}` - Delete content

### Podcast Episodes

- `POST /api/content/podcast-episodes` - Create episode
- `GET /api/content/podcast-episodes` - List episodes
- `GET /api/content/podcast-episodes/{id}` - Get episode

### AI Generation

- `POST /api/content/generate/show-notes` - Generate podcast show notes
- `POST /api/content/generate/social-media` - Generate social media post
- `POST /api/content/generate/blog-article` - Generate blog article
- `POST /api/content/generate/newsletter` - Generate newsletter
- `POST /api/content/validate/{id}` - Validate content quality

## Usage Examples

### 1. Create Podcast Episode

```bash
POST /api/content/podcast-episodes
{
  "episode_title": "Acquiring SaaS Companies: A $50M Success Story",
  "episode_number": 42,
  "guest_name": "John Smith",
  "guest_company": "Smith Capital Partners",
  "transcript_text": "Full episode transcript here..."
}
```

### 2. Generate Show Notes

```bash
POST /api/content/generate/show-notes
{
  "episode_id": 123
}
```

Response includes:

- SEO-optimized title
- Summary
- Timestamps
- Key takeaways
- Guest bio
- Resources mentioned

### 3. Generate LinkedIn Post

```bash
POST /api/content/generate/social-media
{
  "source_content_id": 456,
  "platform": "linkedin"
}
```

### 4. Generate Blog Article

```bash
POST /api/content/generate/blog-article
{
  "topic": "The Ultimate Guide to M&A Due Diligence in 2025",
  "source_content_id": 456,
  "seo_keywords": ["M&A", "due diligence", "mergers", "acquisitions"]
}
```

## Content Types

```python
class ContentType(str, enum.Enum):
    PODCAST_SHOW_NOTES = "podcast_show_notes"
    LINKEDIN_POST = "linkedin_post"
    TWITTER_THREAD = "twitter_thread"
    YOUTUBE_DESCRIPTION = "youtube_description"
    INSTAGRAM_CAPTION = "instagram_caption"
    BLOG_ARTICLE = "blog_article"
    EMAIL_NEWSLETTER = "email_newsletter"
```

## Content Status Workflow

```
DRAFT → PENDING_REVIEW → APPROVED → PUBLISHED → ARCHIVED
```

## Configuration

### Environment Variables Required

```bash
# Claude API
ANTHROPIC_API_KEY=your-api-key

# Database
DATABASE_URL=postgresql://...

# Authentication
CLERK_SECRET_KEY=your-clerk-secret
```

## Brand Voice

The AI agent is configured with:

- **Tone**: Professional, authoritative, practical, results-focused
- **Audience**: Private equity firms, investment bankers, business buyers/sellers
- **Platform**: 100 Days and Beyond - M&A deal management SaaS

## Database Schema

### Content Table

- `id` (UUID)
- `organization_id` (UUID)
- `user_id` (UUID)
- `title` (String)
- `content_type` (Enum)
- `status` (Enum)
- `content_body` (Text)
- `metadata` (JSON)
- `seo_keywords` (JSON)
- `published_url` (String)
- `created_at`, `updated_at` (DateTime)

### Podcast Episode Table

- `id` (UUID)
- `organization_id` (UUID)
- `episode_number` (Integer)
- `episode_title` (String)
- `guest_name`, `guest_bio`, `guest_company` (String)
- `transcript_text` (Text)
- `timestamps`, `key_takeaways`, `resources_mentioned` (JSON)
- `audio_url`, `video_url` (String)
- `created_at`, `updated_at` (DateTime)

## Integration Points

1. **Claude API**: All AI generation uses Anthropic's Claude 3.5 Sonnet
2. **Multi-tenant**: Organization-level isolation via Clerk
3. **Content Storage**: PostgreSQL with JSON metadata
4. **File Uploads**: Support for audio/video transcripts (future)
5. **Webhooks**: Podcast platform integrations (planned)

## Future Enhancements

- [ ] Auto-transcription from audio files
- [ ] Direct podcast platform publishing
- [ ] Content scheduling
- [ ] A/B testing for social media posts
- [ ] Analytics and engagement tracking
- [ ] Multi-language support
- [ ] Content personalization per audience segment
- [ ] Automated content distribution
- [ ] SEO performance tracking

## Error Handling

The system includes:

- Input validation
- API rate limiting awareness
- Graceful fallbacks for AI failures
- Detailed error logging
- User-friendly error messages

## Security

- Multi-tenant data isolation
- Role-based access control
- API authentication via Clerk
- Content version control
- Audit logging

## Performance

- Async AI generation
- Background task support
- Efficient content caching
- Optimized database queries
- Pagination for large datasets

## Monitoring

- Content generation metrics
- AI API usage tracking
- Quality score analytics
- User engagement stats
- Error rate monitoring
