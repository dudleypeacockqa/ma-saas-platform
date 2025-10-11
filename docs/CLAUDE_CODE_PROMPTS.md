# Claude Code Prompts for 100daysandbeyond.com

## Master Development Prompts

These prompts are designed for use in Cursor IDE with Claude Code to build the complete M&A SaaS platform.

---

## Phase 1: Foundation Setup

### Prompt 1.1: PostgreSQL Database Schema

```
Create a complete PostgreSQL database schema for a multi-tenant M&A SaaS platform with the following requirements:

TABLES:
1. users
   - id (UUID, PK)
   - clerk_user_id (VARCHAR, unique, indexed)
   - email (VARCHAR, unique)
   - full_name (VARCHAR)
   - role (ENUM: 'admin', 'account_owner', 'account_user')
   - stripe_customer_id (VARCHAR, nullable)
   - subscription_status (ENUM: 'trial', 'active', 'past_due', 'canceled')
   - subscription_tier (ENUM: 'starter', 'professional', 'enterprise')
   - created_at, updated_at, deleted_at

2. accounts (sub-accounts/workspaces)
   - id (UUID, PK)
   - owner_id (UUID, FK to users)
   - name (VARCHAR)
   - slug (VARCHAR, unique)
   - stripe_subscription_id (VARCHAR)
   - subscription_status
   - max_users (INT, based on tier)
   - max_deals (INT, based on tier)
   - created_at, updated_at, deleted_at

3. account_users (many-to-many relationship)
   - id (UUID, PK)
   - account_id (UUID, FK)
   - user_id (UUID, FK)
   - role (ENUM: 'owner', 'admin', 'member', 'viewer')
   - permissions (JSONB)
   - invited_by (UUID, FK to users)
   - joined_at, created_at

4. deals
   - id (UUID, PK)
   - account_id (UUID, FK)
   - created_by (UUID, FK to users)
   - title (VARCHAR)
   - company_name (VARCHAR)
   - deal_type (ENUM: 'acquisition', 'merger', 'sale', 'investment')
   - deal_value (DECIMAL 15,2)
   - currency (VARCHAR 3, default 'USD')
   - stage (ENUM: 'lead', 'qualification', 'due_diligence', 'negotiation', 'closing', 'closed', 'lost')
   - probability (INT, 0-100)
   - expected_close_date (DATE)
   - actual_close_date (DATE, nullable)
   - description (TEXT)
   - status (ENUM: 'active', 'paused', 'completed', 'archived')
   - created_at, updated_at, deleted_at

5. documents
   - id (UUID, PK)
   - deal_id (UUID, FK)
   - uploaded_by (UUID, FK to users)
   - file_name (VARCHAR)
   - file_size (BIGINT, bytes)
   - file_type (VARCHAR)
   - storage_provider (ENUM: 'r2', 's3')
   - storage_key (VARCHAR, R2/S3 path)
   - storage_url (TEXT, signed URL)
   - is_confidential (BOOLEAN, default true)
   - created_at, updated_at, deleted_at

6. activities (audit log)
   - id (UUID, PK)
   - account_id (UUID, FK)
   - user_id (UUID, FK)
   - entity_type (ENUM: 'deal', 'document', 'account', 'user')
   - entity_id (UUID)
   - action (VARCHAR, e.g., 'created', 'updated', 'deleted')
   - changes (JSONB, before/after values)
   - ip_address (INET)
   - user_agent (TEXT)
   - created_at

INDEXES:
- All foreign keys
- users.clerk_user_id
- accounts.slug
- deals.account_id, stage, status
- documents.deal_id
- activities.account_id, entity_type, created_at

CONSTRAINTS:
- Cascade deletes for account_users when account is deleted
- Soft deletes for users, accounts, deals, documents
- Check constraints for positive deal values
- Check constraints for probability 0-100

Generate:
1. SQLAlchemy models in backend/app/models/
2. Alembic migrations
3. Database initialization script
4. Seed data for development

Use best practices for multi-tenancy, security, and performance.
```

### Prompt 1.2: Backend API Structure

```
Create a FastAPI backend in backend/ with the following structure:

STRUCTURE:
backend/
├── app/
│   ├── main.py (FastAPI app, CORS, middleware)
│   ├── config.py (Settings, environment variables)
│   ├── database.py (DB connection, session management)
│   ├── dependencies.py (Auth, DB session dependencies)
│   ├── models/ (SQLAlchemy models)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── account.py
│   │   ├── deal.py
│   │   ├── document.py
│   │   └── activity.py
│   ├── schemas/ (Pydantic models)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── account.py
│   │   ├── deal.py
│   │   └── document.py
│   ├── routers/ (API endpoints)
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── accounts.py
│   │   ├── deals.py
│   │   ├── documents.py
│   │   └── webhooks.py
│   ├── services/ (Business logic)
│   │   ├── __init__.py
│   │   ├── auth_service.py (Clerk JWT verification)
│   │   ├── stripe_service.py (Subscriptions)
│   │   ├── storage_service.py (R2 uploads)
│   │   └── email_service.py (Notifications)
│   └── middleware/
│       ├── __init__.py
│       ├── auth.py (JWT verification)
│       └── tenant.py (Multi-tenancy)
├── tests/
├── migrations/ (Alembic)
├── requirements.txt
└── run.py

FEATURES:
- FastAPI with async/await
- Clerk authentication (JWT verification)
- Multi-tenant row-level security
- Cloudflare R2 file uploads
- Stripe subscription management
- Comprehensive error handling
- Request logging and monitoring
- API rate limiting
- OpenAPI documentation
- Health check endpoint

SECURITY:
- Verify Clerk JWTs on all protected routes
- Implement tenant isolation (users can only access their account's data)
- Validate all inputs with Pydantic
- SQL injection prevention (use SQLAlchemy ORM)
- XSS prevention (sanitize outputs)
- CORS configured for 100daysandbeyond.com only

Generate all files with production-ready code.
```

### Prompt 1.3: Frontend Application Structure

```
Create a React frontend in frontend/src/ with the following structure:

STRUCTURE:
frontend/src/
├── components/
│   ├── ui/ (shadcn/ui components)
│   ├── layout/
│   │   ├── Header.jsx (with user menu, notifications)
│   │   ├── Sidebar.jsx (navigation)
│   │   └── Footer.jsx
│   ├── auth/
│   │   ├── SignIn.jsx
│   │   ├── SignUp.jsx
│   │   └── ProtectedRoute.jsx
│   ├── deals/
│   │   ├── DealCard.jsx
│   │   ├── DealList.jsx
│   │   ├── DealForm.jsx
│   │   ├── DealDetails.jsx
│   │   └── DealKanban.jsx
│   ├── documents/
│   │   ├── DocumentUpload.jsx
│   │   ├── DocumentList.jsx
│   │   └── DocumentViewer.jsx
│   └── settings/
│       ├── AccountSettings.jsx
│       ├── TeamManagement.jsx
│       └── BillingSettings.jsx
├── pages/
│   ├── Dashboard.jsx
│   ├── Deals.jsx
│   ├── DealDetails.jsx
│   ├── Documents.jsx
│   ├── Settings.jsx
│   └── Billing.jsx
├── hooks/
│   ├── useAuth.js
│   ├── useAccount.js
│   ├── useDeals.js
│   └── useDocuments.js
├── lib/
│   ├── api.js (Axios instance with auth)
│   ├── clerk.js (Clerk configuration)
│   └── utils.js
├── contexts/
│   ├── AccountContext.jsx
│   └── ThemeContext.jsx
└── App.jsx

FEATURES:
- Clerk authentication (ClerkProvider)
- React Router for navigation
- React Query for data fetching
- shadcn/ui for components
- Tailwind CSS for styling
- Responsive design (mobile-first)
- Dark mode support
- Loading states and skeletons
- Error boundaries
- Toast notifications
- Form validation (Zod)

PAGES TO BUILD:
1. Dashboard - KPIs, charts, recent deals
2. Deals - List/Kanban view with filters
3. Deal Details - Full deal information, documents, timeline
4. Documents - File management with upload
5. Settings - Account, team, billing
6. Billing - Subscription management with Stripe

Use best practices for React, accessibility (ARIA), and performance (code splitting, lazy loading).
```

---

## Phase 2: Core Features

### Prompt 2.1: Deal Management System

```
Implement a complete deal management system with:

FEATURES:
1. Deal CRUD operations
   - Create deal with form validation
   - Update deal (inline editing + modal)
   - Delete deal (with confirmation)
   - Soft delete with restore option

2. Deal Views
   - List view with sorting, filtering, pagination
   - Kanban board (drag-and-drop between stages)
   - Calendar view (by expected close date)
   - Grid view (card-based)

3. Deal Filtering
   - By stage (multi-select)
   - By deal type
   - By value range (slider)
   - By date range (date picker)
   - By assigned user
   - Save filter presets

4. Deal Analytics
   - Total deals by stage (funnel chart)
   - Deal value by stage (bar chart)
   - Win rate percentage
   - Average deal size
   - Average time to close
   - Conversion rates between stages

5. Deal Details Page
   - Overview section (all deal fields)
   - Documents section (upload, view, download)
   - Activity timeline (auto-generated + manual notes)
   - Related contacts
   - Financial information
   - Comments/Notes section

BACKEND:
- API endpoints in backend/app/routers/deals.py
- Business logic in backend/app/services/deal_service.py
- Implement row-level security (tenant isolation)
- Add caching for analytics queries
- Log all deal changes to activities table

FRONTEND:
- Deal components in frontend/src/components/deals/
- Use React Query for data fetching with cache
- Implement optimistic updates
- Add keyboard shortcuts
- Export deals to CSV/Excel

Test thoroughly with edge cases.
```

### Prompt 2.2: Document Management with R2

```
Implement secure document management with Cloudflare R2:

FEATURES:
1. Document Upload
   - Drag-and-drop interface
   - Multiple file upload
   - File type validation (PDF, DOCX, XLSX, images)
   - File size limits (50MB per file)
   - Upload progress indicators
   - Automatic thumbnail generation for images

2. Document Storage
   - Upload to Cloudflare R2
   - Generate signed URLs (1-hour expiry)
   - Organize by deal_id/document_id structure
   - Compress images before upload
   - Extract metadata (file size, type, dimensions)

3. Document Access Control
   - Only account members can access documents
   - Track document views in activities table
   - Generate audit log of downloads
   - Watermark option for PDFs

4. Document Viewer
   - In-browser PDF viewer
   - Image gallery
   - Office docs (use Google Docs Viewer API)
   - Download original file
   - Share link (with expiry)

BACKEND (backend/app/services/storage_service.py):
- Use boto3 with R2 S3-compatible API
- Implement multipart upload for large files
- Generate presigned URLs for secure access
- Delete old files from R2 when document is deleted
- Virus scanning integration (optional: ClamAV)

FRONTEND (frontend/src/components/documents/):
- Use react-dropzone for file upload
- Show upload progress with progress bar
- Display file list with icons by type
- Implement search and filtering
- Add document categories/tags

ENV VARS:
- CLOUDFLARE_ACCOUNT_ID
- R2_ACCESS_KEY_ID
- R2_SECRET_ACCESS_KEY
- R2_BUCKET_NAME
- R2_ENDPOINT

Test with various file types and sizes.
```

### Prompt 2.3: Stripe Subscription System

```
Implement complete subscription management with Stripe and Clerk:

SUBSCRIPTION TIERS:
1. Starter - $49/month
   - 1 account
   - 3 users
   - 50 deals
   - 5GB storage

2. Professional - $149/month
   - 3 accounts
   - 10 users
   - Unlimited deals
   - 50GB storage
   - Priority support

3. Enterprise - $499/month
   - Unlimited accounts
   - Unlimited users
   - Unlimited deals
   - 500GB storage
   - Dedicated support
   - White-label option
   - API access

FEATURES:
1. Subscription Creation
   - Create Stripe customer on user signup
   - Link Stripe customer to Clerk user
   - Create subscription with selected tier
   - Handle payment methods (card, SEPA, etc.)
   - Apply promo codes/coupons

2. Subscription Management
   - View current subscription
   - Upgrade/downgrade plans
   - Update payment method
   - View invoices and receipts
   - Cancel subscription (with feedback)
   - Reactivate canceled subscription

3. Usage Limits
   - Track usage (users, deals, storage)
   - Show usage meters in UI
   - Block actions when limit reached
   - Send email warnings at 80% usage
   - Offer upgrade prompts

4. Billing Portal
   - Embedded Stripe Checkout
   - Stripe Customer Portal (for existing customers)
   - Invoice history
   - Payment method management
   - Subscription details

WEBHOOKS (backend/app/routers/webhooks.py):
Handle these Stripe events:
- customer.subscription.created
- customer.subscription.updated
- customer.subscription.deleted
- customer.subscription.trial_will_end
- invoice.payment_succeeded
- invoice.payment_failed
- customer.updated
- payment_method.attached

Update user subscription_status and subscription_tier in database.

FRONTEND (frontend/src/pages/Billing.jsx):
- Pricing table (PricingCard components)
- Subscription overview
- Usage meters (circular progress)
- Payment method display
- Invoice list
- Cancel/upgrade modals

CLERK INTEGRATION:
- Store stripe_customer_id in Clerk user metadata
- Update Clerk user publicMetadata with subscription_tier
- Use Clerk webhooks to sync user data

Test with Stripe test mode cards.
```

---

## Phase 3: Advanced Features

### Prompt 3.1: Multi-Tenant Sub-Account System

```
Implement sub-account/workspace system for enterprise users:

FEATURES:
1. Account Creation
   - Create new account (workspace)
   - Set account name and slug
   - Choose subscription tier
   - Invite initial team members

2. Account Switching
   - Dropdown in header to switch accounts
   - Load account-specific data
   - Update UI context
   - Persist selected account in localStorage

3. Team Management
   - Invite users by email
   - Set user roles (owner, admin, member, viewer)
   - Custom permissions per user
   - Remove team members
   - Transfer ownership

4. Role-Based Access Control (RBAC)
   - Owner: Full access
   - Admin: Manage users, deals, settings
   - Member: Create/edit deals, upload documents
   - Viewer: Read-only access

5. Account Settings
   - Update account name
   - Configure account-level preferences
   - Set branding (logo, colors) for enterprise
   - API keys for integrations
   - Webhook configurations

BACKEND:
- Middleware to inject account_id from JWT
- Filter all queries by account_id (tenant isolation)
- Validate user has access to account
- Implement permission checks
- Log account switching in activities

FRONTEND:
- AccountContext to manage current account
- Account switcher in header
- Team management page
- Invitation flow with email links
- Permission-based UI rendering

SECURITY:
- Verify user belongs to account on every request
- Prevent cross-account data leaks
- Rate limit account creation
- Validate invitation tokens

Test multi-tenancy thoroughly with multiple accounts and users.
```

### Prompt 3.2: Real-Time Notifications

```
Implement real-time notifications system:

NOTIFICATION TYPES:
1. Deal Updates
   - Deal stage changed
   - Deal assigned to you
   - Deal approaching close date
   - Deal closed/won/lost

2. Document Updates
   - New document uploaded
   - Document shared with you
   - Document comment added

3. Team Updates
   - New user invited
   - User joined account
   - User removed from account
   - Role changed

4. Billing Updates
   - Subscription upgraded
   - Subscription canceled
   - Payment failed
   - Usage limit approaching

DELIVERY CHANNELS:
1. In-App Notifications
   - Bell icon in header with badge count
   - Dropdown list of notifications
   - Mark as read/unread
   - Delete notification
   - Filter by type

2. Email Notifications
   - Digest email (daily/weekly)
   - Instant email for critical events
   - Email preferences in settings
   - Unsubscribe link

3. Browser Push Notifications (optional)
   - Request permission
   - Show OS-level notifications
   - Click to navigate to relevant page

BACKEND:
- notifications table in database
- Create notification service
- Send notifications on events
- Email service integration (SendGrid/AWS SES)
- Notification preferences per user

FRONTEND:
- NotificationBell component in header
- NotificationList with infinite scroll
- Toast notifications for real-time events
- Notification settings page
- WebSocket or polling for real-time updates

Test notification delivery and rendering.
```

---

## Phase 4: Marketing Website

### Prompt 4.1: World-Class Homepage

```
Create a world-class, high-converting homepage for 100daysandbeyond.com:

SECTIONS:
1. Hero Section
   - Attention-grabbing headline: "Close Deals Faster with AI-Powered M&A Management"
   - Subheadline: "The complete platform for private equity firms, M&A advisors, and business buyers to manage acquisitions from lead to close"
   - CTA buttons: "Start Free Trial" + "Watch Demo"
   - Hero image/animation: Dashboard preview or deal pipeline visualization
   - Trust badges: "Trusted by 500+ PE firms", "4.9/5 stars", "SOC 2 Certified"

2. Social Proof Section
   - Logos of notable clients (PE firms, investment banks)
   - Testimonial carousel
   - Key metrics: "10,000+ deals managed", "$5B+ in transaction value"

3. Problem/Solution Section
   - "Are you still managing deals in spreadsheets?"
   - Pain points: Manual data entry, lost documents, missed deadlines, poor visibility
   - Solution: Visual comparison (before/after)

4. Features Section (cards with icons)
   - Deal Pipeline Management
   - Secure Document Storage
   - Team Collaboration
   - Due Diligence Tracking
   - Financial Modeling
   - Automated Reporting

5. How It Works (3 steps)
   - 1. Import Your Deals
   - 2. Collaborate with Your Team
   - 3. Close Faster with Insights

6. Use Cases
   - Private Equity Firms
   - M&A Advisors
   - Corporate Development Teams
   - Investment Bankers
   - Business Brokers

7. Pricing Section
   - 3-tier pricing table
   - Feature comparison
   - "14-day free trial, no credit card required"
   - Money-back guarantee badge

8. Video Section
   - Product demo video (2-3 minutes)
   - Testimonial videos
   - Founder story

9. FAQ Section
   - 8-10 common questions
   - Accordion-style

10. Final CTA Section
    - "Ready to transform your deal management?"
    - Large CTA button
    - "Join 500+ firms already using 100 Days and Beyond"

DESIGN:
- Modern, professional, clean
- Primary color: Blue (#2563EB) - trust, stability
- Accent color: Green (#10B981) - growth, success
- White space and breathing room
- High-quality images and illustrations
- Smooth scroll animations
- Mobile-responsive
- Fast loading (< 2s)

SEO:
- Title: "M&A Deal Management Software | 100 Days and Beyond"
- Meta description (155 chars)
- Schema.org markup (SoftwareApplication)
- Open Graph tags for social sharing
- H1, H2, H3 hierarchy
- Alt text for all images
- Internal linking
- Structured data

PERFORMANCE:
- Lazy load images
- Compress assets
- Use WebP format
- Inline critical CSS
- Defer non-critical JS
- Lighthouse score 95+

Create in frontend/src/pages/Home.jsx with reusable components.
```

### Prompt 4.2: SEO-Optimized Blog System

```
Create a comprehensive blog system with 50 SEO-optimized articles:

BLOG STRUCTURE:
frontend/src/
├── pages/
│   ├── Blog.jsx (blog listing)
│   ├── BlogPost.jsx (single post)
│   └── BlogCategory.jsx (category listing)
├── components/
│   └── blog/
│       ├── BlogCard.jsx
│       ├── BlogHeader.jsx
│       ├── BlogSidebar.jsx
│       ├── AuthorBio.jsx
│       └── RelatedPosts.jsx
└── content/
    └── blog/ (Markdown files)
        ├── post-1.md
        ├── post-2.md
        └── ...

BLOG CATEGORIES:
1. M&A Strategy (10 articles)
2. Due Diligence (10 articles)
3. Deal Sourcing (8 articles)
4. Valuation (8 articles)
5. Integration (7 articles)
6. Case Studies (7 articles)

ARTICLE TEMPLATE (2000-2500 words each):
---
title: "[Keyword-Rich Title]"
description: "[155-char meta description]"
author: "Your Name"
date: "2025-10-11"
category: "M&A Strategy"
tags: ["mergers", "acquisitions", "private equity"]
featured_image: "/images/blog/post-1.jpg"
---

# [H1 Title with Primary Keyword]

[Introduction paragraph with secondary keywords]

## [H2 Section 1]
[300-400 words]

## [H2 Section 2]
[300-400 words]

## [H2 Section 3]
[300-400 words]

## [H2 Section 4]
[300-400 words]

## Conclusion
[Recap + CTA]

---

SAMPLE ARTICLE TITLES:
1. "The Complete Guide to M&A Due Diligence in 2025"
2. "How Private Equity Firms Source Deals: A Step-by-Step Guide"
3. "10 Red Flags to Watch for During M&A Due Diligence"
4. "Valuation Methods for Middle-Market Acquisitions"
5. "Post-Merger Integration: Best Practices from 100+ Deals"
6. "How to Build a Deal Pipeline That Converts"
7. "M&A Deal Structures Explained: Asset vs. Stock Purchase"
8. "The Role of Technology in Modern M&A Transactions"
9. "Letter of Intent (LOI) Template and Negotiation Tips"
10. "How to Conduct Financial Due Diligence: Checklist Included"
[... 40 more titles]

SEO REQUIREMENTS:
- Primary keyword in title, URL, H1, first paragraph
- LSI keywords throughout
- Internal links to other blog posts
- External links to authoritative sources
- Alt text for all images
- Schema.org Article markup
- Open Graph tags
- Twitter Card tags
- 2-3% keyword density
- Readability score: 60+ (Flesch Reading Ease)

FEATURES:
- Reading time estimate
- Share buttons (LinkedIn, Twitter, Email)
- Author bio box
- Related posts section
- Comment system (optional: Disqus)
- Newsletter signup CTA
- Table of contents for long posts
- Search functionality
- Category/tag filtering
- RSS feed

Generate all 50 articles as Markdown files with frontmatter.
Use AI to write high-quality, informative content.
```

### Prompt 4.3: Podcast Page

```
Create a professional podcast page for "100 Days and Beyond Podcast":

FEATURES:
1. Podcast Header
   - Podcast cover art
   - Podcast title and description
   - Host information
   - Subscribe buttons (Apple Podcasts, Spotify, Google Podcasts, RSS)
   - Social media links

2. Episode List
   - Episode cards with:
     - Episode number
     - Title
     - Description (excerpt)
     - Duration
     - Release date
     - Play button (embedded player)
     - Show notes link
   - Pagination or infinite scroll
   - Filter by season/category

3. Embedded Player
   - HTML5 audio player
   - Play/pause, skip, speed controls
   - Progress bar
   - Volume control
   - Download episode button

4. Show Notes
   - Full episode description
   - Timestamps for key topics
   - Guest bio and links
   - Resources mentioned
   - Transcript (optional)

5. Subscribe Section
   - Call-to-action to subscribe
   - Buttons for all podcast platforms
   - RSS feed link
   - Email newsletter signup

PODCAST CONTENT:
- Topic: M&A insights, interviews with PE partners, deal stories
- Format: 30-45 minute episodes
- Release schedule: Weekly
- Guests: M&A advisors, PE partners, founders who've sold

SAMPLE EPISODES:
1. "How to Value a Middle-Market Company" (with PE partner)
2. "Red Flags in Due Diligence" (with M&A attorney)
3. "Founder's Story: Selling Our $50M Company" (with founder)
4. "Deal Sourcing Strategies for Independent Sponsors"
5. "Post-Merger Integration Lessons Learned"

DESIGN:
- Modern podcast page design
- Responsive (mobile-first)
- Fast loading
- Accessible (ARIA labels)

SEO:
- Title: "100 Days and Beyond Podcast | M&A Insights"
- Meta description
- Schema.org Podcast markup
- Episode transcripts for SEO

Create in frontend/src/pages/Podcast.jsx
```

---

## Phase 5: Sales Funnel

### Prompt 5.1: Video Sales Letter (VSL) Page

```
Create a high-converting Video Sales Letter landing page:

STRUCTURE:
1. Headline
   "How [Target Audience] Can [Achieve Desired Outcome] in [Timeframe] Without [Pain Point]"
   Example: "How Private Equity Firms Can Close 3x More Deals in 100 Days Without Hiring More Staff"

2. Video Player
   - Centered, large video player
   - No distractions (hide navigation)
   - Auto-play with muted option
   - Captions for accessibility
   - 10-15 minute VSL video

3. VSL Script Structure:
   - Hook (0:00-0:30): Attention-grabbing problem
   - Story (0:30-3:00): Founder's journey, customer story
   - Problem (3:00-5:00): Deep dive into pain points
   - Solution (5:00-8:00): Product demo, features
   - Social Proof (8:00-10:00): Testimonials, case studies
   - Offer (10:00-12:00): Pricing, bonuses, guarantee
   - CTA (12:00-15:00): Clear next steps

4. Below-Video Content
   - Transcript option
   - Key takeaways (bullet points)
   - Social proof (logos, testimonials)
   - FAQ section
   - Final CTA button

5. Sticky CTA Bar
   - Fixed to bottom of screen
   - "Start Free Trial" button
   - Countdown timer (optional: "Offer ends in 4:32:15")

CONVERSION OPTIMIZATION:
- Remove navigation links (reduce distractions)
- One clear CTA throughout page
- Exit-intent popup with special offer
- Urgency/scarcity elements
- Trust badges (security, money-back guarantee)
- Live chat widget

TRACKING:
- Video engagement (% watched)
- Scroll depth tracking
- CTA click tracking
- Conversion tracking (to Stripe Checkout)

Create in frontend/src/pages/VSL.jsx
Use react-player for video embedding
A/B test different headlines and CTAs
```

### Prompt 5.2: Sales Offer Squeeze Pages

```
Create 3 high-converting squeeze pages (lead capture pages):

PAGE 1: Free Trial Signup
- Headline: "Start Your 14-Day Free Trial (No Credit Card Required)"
- Subheadline: "Join 500+ firms managing $5B+ in deals"
- Simple form: Email + Name
- CTA: "Start Free Trial"
- Privacy assurance: "We'll never spam you"
- Social proof: Client logos, testimonial
- Below fold: Benefits of trial (bullet points)

PAGE 2: Lead Magnet Download
- Offer: "Free M&A Due Diligence Checklist"
- Headline: "Download Our 47-Point Due Diligence Checklist (Used by Top PE Firms)"
- Form: Email + Company Name
- CTA: "Download Free Checklist"
- Preview: Thumbnail of PDF
- Social proof: "Downloaded by 5,000+ M&A professionals"

PAGE 3: Webinar Registration
- Offer: Free webinar on "How to Close Deals Faster"
- Headline: "Join Our Live Webinar: Close Deals 3x Faster with AI"
- Date/time: "Next session: Thursday, Oct 17 at 2pm EST"
- Form: Email + Name + Phone (optional)
- CTA: "Save My Seat"
- Bonus: "Register today and get our Deal Pipeline Template ($97 value) free"

DESIGN ELEMENTS:
- Minimal navigation (logo only)
- Hero image/video
- Short form (2-3 fields max)
- Large, contrasting CTA button
- Trust badges below form
- Mobile-responsive
- Fast loading

CONVERSION TACTICS:
- Urgency: "Limited spots available"
- Scarcity: "Only 100 downloads left"
- Social proof: "1,247 people signed up this week"
- Risk reversal: "Unsubscribe anytime"
- Exit-intent popup: "Wait! Get 20% off your first month"

FOLLOW-UP:
- Thank you page with next steps
- Confirmation email
- Nurture email sequence (5-7 emails)
- Retargeting pixel for ads

Create in frontend/src/pages/:
- TrialSignup.jsx
- LeadMagnet.jsx
- WebinarRegistration.jsx

Integrate with email service (ConvertKit, Mailchimp)
Track conversion rate for each page
A/B test headlines, CTAs, form fields
```

---

## Phase 6: Integration & Testing

### Prompt 6.1: End-to-End Testing

```
Create comprehensive test suite for the entire application:

TEST TYPES:
1. Unit Tests
   - Frontend: Jest + React Testing Library
   - Backend: pytest
   - Test individual functions and components
   - Mock external dependencies
   - Aim for 80%+ code coverage

2. Integration Tests
   - Test API endpoints with database
   - Test authentication flow
   - Test Stripe integration
   - Test R2 file upload
   - Test webhook handlers

3. End-to-End Tests
   - Use Playwright or Cypress
   - Test complete user journeys:
     - Sign up → Create deal → Upload document → Close deal
     - Invite user → User joins → Collaborate on deal
     - Subscribe → Upgrade plan → Cancel subscription
   - Test on multiple browsers (Chrome, Firefox, Safari)

4. Performance Tests
   - Load testing with k6 or Artillery
   - Test with 100 concurrent users
   - Measure response times
   - Identify bottlenecks
   - Optimize slow queries

5. Security Tests
   - SQL injection attempts
   - XSS attempts
   - CSRF token validation
   - JWT tampering
   - Rate limit testing
   - Privilege escalation attempts

TEST FILES:
frontend/tests/
├── unit/
│   ├── components/
│   └── hooks/
├── integration/
│   └── api/
└── e2e/
    └── user-flows/

backend/tests/
├── unit/
│   ├── models/
│   └── services/
├── integration/
│   └── api/
└── fixtures/

Create comprehensive test coverage with clear assertions.
Document test setup and running instructions.
```

### Prompt 6.2: Deployment Pipeline

```
Set up complete CI/CD pipeline:

GITHUB ACTIONS WORKFLOWS:

1. .github/workflows/frontend-ci.yml
   - Trigger: Push to main, Pull requests
   - Steps:
     - Checkout code
     - Install dependencies (pnpm)
     - Run linters (ESLint, Prettier)
     - Run unit tests
     - Run integration tests
     - Build production bundle
     - Upload build artifacts

2. .github/workflows/backend-ci.yml
   - Trigger: Push to main, Pull requests
   - Steps:
     - Checkout code
     - Set up Python
     - Install dependencies
     - Run linters (Black, Flake8)
     - Run unit tests
     - Run integration tests
     - Build Docker image
     - Push to registry

3. .github/workflows/deploy-frontend.yml
   - Trigger: Push to main (after CI passes)
   - Steps:
     - Build production bundle
     - Deploy to Render
     - Run smoke tests
     - Notify team (Slack)

4. .github/workflows/deploy-backend.yml
   - Trigger: Push to main (after CI passes)
   - Steps:
     - Build Docker image
     - Push to Render
     - Run database migrations
     - Run smoke tests
     - Notify team (Slack)

ENVIRONMENTS:
- Development (auto-deploy from dev branch)
- Staging (auto-deploy from staging branch)
- Production (manual approval required)

MONITORING:
- Sentry for error tracking
- LogRocket for session replay
- Render metrics for performance
- Uptime monitoring (UptimeRobot)

ROLLBACK PLAN:
- Keep previous 5 deployments
- One-click rollback in Render
- Database migration rollback scripts

Create all workflow files with proper secrets management.
```

---

## Master Prompt for Complete Platform

### The One Prompt to Rule Them All

```
Build a complete, production-ready, multi-tenant M&A SaaS platform for 100daysandbeyond.com with:

TECH STACK:
- Frontend: React + Vite + Tailwind CSS + shadcn/ui
- Backend: FastAPI (Python) + PostgreSQL
- Auth: Clerk
- Payments: Stripe
- Storage: Cloudflare R2
- Hosting: Render
- CDN: Cloudflare

CORE FEATURES:
1. Multi-tenant architecture (sub-accounts/workspaces)
2. Clerk authentication with JWT verification
3. Deal management (CRUD, Kanban, calendar views)
4. Document management with R2 storage
5. Team collaboration (invite users, assign roles, permissions)
6. Stripe subscription management (3 tiers)
7. Usage tracking and limits
8. Real-time notifications
9. Activity audit logs
10. Analytics dashboard

MARKETING WEBSITE:
1. World-class homepage (10 sections)
2. Pricing page
3. Blog with 50 SEO-optimized articles (2000-2500 words each)
4. Podcast page with embedded player
5. About, Contact, FAQ pages
6. VSL landing page
7. 3 squeeze pages (lead capture)

DATABASE SCHEMA:
- users, accounts, account_users, deals, documents, activities, notifications

API ENDPOINTS:
- Auth, Accounts, Deals, Documents, Webhooks, Analytics

SECURITY:
- Row-level multi-tenancy
- JWT authentication on all protected routes
- Input validation with Pydantic
- CORS configured
- Rate limiting
- SQL injection prevention
- XSS prevention

SEO:
- Meta tags (title, description, OG, Twitter Card)
- Schema.org markup
- Sitemap and robots.txt
- Fast loading (< 2s)
- Mobile-responsive
- Lighthouse score 95+

TESTING:
- Unit tests (80%+ coverage)
- Integration tests
- E2E tests (Playwright)
- Performance tests (k6)

CI/CD:
- GitHub Actions workflows
- Auto-deploy to Render
- Database migrations
- Smoke tests

INTEGRATIONS:
- Clerk for auth
- Stripe for payments
- Cloudflare R2 for storage
- SendGrid for emails
- Sentry for error tracking

Generate all code, tests, documentation, and deployment configs.
Follow best practices for security, performance, and scalability.
Make it production-ready, world-class, and enterprise-grade.
```

---

**Use these prompts in Cursor IDE with Claude Code to build the complete platform systematically.**

**Adjust prompts as needed based on your specific requirements.**

**Test thoroughly after each phase before moving to the next.**

---

**Last Updated:** 2025-10-11
