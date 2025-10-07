# 🤖 AI Agent Development Prompts for Claude Code CLI

## Overview

These prompts are designed for use with Claude Code CLI in Cursor IDE to build a comprehensive AI agent system that automates your entire M&A business ecosystem. Each agent handles specific business functions while integrating seamlessly with your SaaS platform.

---

## 🎯 PROMPT 1: Content Creation Agent

```
I need you to build a comprehensive Content Creation Agent for my M&A SaaS platform that automates podcast show notes, social media posts, blog articles, and marketing content.

CONTEXT:
- Platform: 100daysandbeyond.com M&A deal management SaaS
- Podcast: "100 Days and Beyond" focusing on M&A deals and business acquisitions
- Target Audience: Private equity firms, investment bankers, business buyers/sellers
- Brand Voice: Professional, authoritative, practical, results-focused

REQUIREMENTS:
1. Podcast Show Notes Generator
   - Input: Audio transcript or video file
   - Output: Structured show notes with timestamps, key takeaways, guest bio, resources
   - Format: SEO-optimized with H2/H3 headings, bullet points, call-to-actions

2. Social Media Content Creator
   - LinkedIn posts (professional, thought leadership)
   - Twitter threads (key insights, statistics)
   - YouTube video descriptions with timestamps
   - Instagram/TikTok captions for video clips

3. Blog Article Generator
   - Long-form articles (2000-2500 words)
   - SEO optimization for M&A keywords
   - Integration of podcast insights and guest expertise
   - Call-to-actions for SaaS trial signup

4. Email Newsletter Content
   - Weekly newsletter with deal insights
   - Subscriber-only content previews
   - Market analysis and trends

TECHNICAL SPECIFICATIONS:
- Use Claude MCP server for content generation
- Integrate with existing FastAPI backend
- Store content in PostgreSQL database
- API endpoints for content management
- Webhook integration with podcast hosting platforms

FILES TO CREATE/UPDATE:
- backend/app/agents/content_agent.py
- backend/app/api/content.py
- backend/app/models/content.py
- frontend/src/components/ContentDashboard.tsx
- backend/app/services/content_service.py

Please build this agent with proper error handling, content quality validation, and integration with our existing multi-tenant architecture.
```

---

## 🔍 PROMPT 2: Deal Sourcing & Research Agent

```
Build a sophisticated Deal Sourcing & Research Agent that automatically identifies M&A opportunities, analyzes market trends, and generates investment recommendations for my platform.

CONTEXT:
- Target: UK and US middle-market companies (£1M-£50M revenue)
- Focus: Technology, healthcare, professional services, manufacturing
- Goal: Support both platform subscribers and my personal acquisition strategy
- Integration: Existing M&A SaaS platform with deal pipeline management

CORE FUNCTIONS:
1. Market Opportunity Scanner
   - Monitor industry news and reports
   - Identify distressed companies and succession opportunities
   - Track competitor acquisitions and market consolidation
   - Generate weekly market intelligence reports

2. Company Analysis Engine
   - Financial health assessment using public data
   - Competitive positioning analysis
   - Growth trajectory evaluation
   - Risk factor identification

3. Deal Opportunity Scorer
   - Proprietary scoring algorithm based on financial metrics
   - Strategic fit assessment for different buyer profiles
   - ROI projections and valuation ranges
   - Deal complexity and timeline estimates

4. Research Report Generator
   - Comprehensive company profiles
   - Industry analysis and market positioning
   - Financial performance summaries
   - Investment thesis development

DATA SOURCES INTEGRATION:
- Companies House API (UK company data)
- SEC EDGAR database (US public filings)
- Industry databases and reports
- News APIs and market intelligence platforms
- Social media sentiment analysis

TECHNICAL ARCHITECTURE:
- Background task processing with Celery
- Data pipeline with automated updates
- Machine learning models for scoring
- Real-time alerts and notifications
- Integration with existing deal management system

FILES TO CREATE/UPDATE:
- backend/app/agents/deal_sourcing_agent.py
- backend/app/services/market_intelligence.py
- backend/app/models/opportunities.py
- backend/app/api/research.py
- backend/app/tasks/data_collection.py
- frontend/src/components/OpportunityDashboard.tsx

Build this with proper data validation, rate limiting for API calls, and comprehensive logging for audit trails.
```

---

## 📧 PROMPT 3: Subscriber Acquisition Agent

```
Create a Subscriber Acquisition Agent that identifies potential SaaS customers, personalizes outreach campaigns, and automates the conversion funnel for my M&A platform.

BUSINESS CONTEXT:
- SaaS Platform: 100daysandbeyond.com (£99-£999/month tiers)
- Target Customers: M&A professionals, PE firms, investment bankers, business brokers
- Goal: Acquire 500 subscribers in first 12 months
- Current Conversion: Website visitors to trial signups

AGENT CAPABILITIES:
1. Prospect Identification System
   - LinkedIn Sales Navigator integration
   - Industry database mining (Crunchbase, PitchBook)
   - Website visitor tracking and lead scoring
   - Referral network analysis from podcast guests

2. Personalized Outreach Engine
   - LinkedIn connection requests with personalized messages
   - Email sequences based on prospect profile and behavior
   - Content recommendations aligned with prospect interests
   - Follow-up automation with intelligent timing

3. Lead Nurturing Workflows
   - Behavioral trigger campaigns
   - Content-based lead scoring
   - Trial conversion optimization
   - Onboarding sequence automation

4. Performance Analytics
   - Outreach campaign effectiveness
   - Conversion funnel analysis
   - ROI tracking per acquisition channel
   - A/B testing for message optimization

INTEGRATION REQUIREMENTS:
- CRM system (HubSpot or custom)
- Email marketing platform (Mailchimp/SendGrid)
- LinkedIn automation tools
- Analytics and tracking systems
- Existing user management system

COMPLIANCE & ETHICS:
- GDPR compliance for data handling
- CAN-SPAM compliance for email marketing
- LinkedIn terms of service adherence
- Opt-out mechanisms and preference management

FILES TO CREATE/UPDATE:
- backend/app/agents/acquisition_agent.py
- backend/app/services/outreach_service.py
- backend/app/models/prospects.py
- backend/app/api/marketing.py
- backend/app/integrations/linkedin_api.py
- frontend/src/components/MarketingDashboard.tsx

Implement with proper rate limiting, compliance checks, and detailed analytics for campaign optimization.
```

---

## 📊 PROMPT 4: Performance Analytics Agent

```
Build a comprehensive Performance Analytics Agent that tracks all business metrics, generates insights, and provides optimization recommendations across the entire business ecosystem.

SCOPE OF ANALYSIS:
- SaaS platform performance (subscribers, churn, revenue)
- Podcast metrics (downloads, engagement, monetization)
- Content performance (blog traffic, social engagement)
- Deal pipeline tracking (opportunities, conversions, ROI)
- Personal wealth building progress toward £200M goal

CORE ANALYTICS MODULES:
1. Business Intelligence Dashboard
   - Real-time KPI monitoring
   - Revenue forecasting and trend analysis
   - Customer lifetime value calculations
   - Churn prediction and prevention alerts

2. Content Performance Analyzer
   - Podcast episode performance tracking
   - Blog article SEO and engagement metrics
   - Social media reach and conversion analysis
   - Content ROI and optimization recommendations

3. Deal Pipeline Analytics
   - Opportunity progression tracking
   - Win/loss analysis and pattern recognition
   - Deal velocity and bottleneck identification
   - Portfolio performance monitoring

4. Predictive Modeling Engine
   - Revenue forecasting using historical data
   - Customer behavior prediction
   - Market opportunity scoring
   - Risk assessment and mitigation strategies

REPORTING CAPABILITIES:
- Automated daily/weekly/monthly reports
- Executive summary dashboards
- Detailed performance breakdowns
- Actionable insights and recommendations
- Comparative analysis and benchmarking

TECHNICAL IMPLEMENTATION:
- Data warehouse design for multi-source integration
- ETL pipelines for data processing
- Machine learning models for predictions
- Real-time alerting system
- Interactive visualization components

DATA SOURCES:
- SaaS platform database
- Podcast hosting analytics
- Google Analytics and social media APIs
- Financial systems and deal tracking
- Market data and industry benchmarks

FILES TO CREATE/UPDATE:
- backend/app/agents/analytics_agent.py
- backend/app/services/data_warehouse.py
- backend/app/models/analytics.py
- backend/app/api/reporting.py
- backend/app/tasks/data_processing.py
- frontend/src/components/AnalyticsDashboard.tsx
- frontend/src/components/ReportingInterface.tsx

Build with scalable data architecture, real-time processing capabilities, and intuitive visualization interfaces.
```

---

## 🎙️ PROMPT 5: Podcast Production Agent

```
Create a Podcast Production Agent that automates the entire podcast workflow from recording to distribution, including show notes, social media clips, and audience engagement.

PODCAST DETAILS:
- Show: "100 Days and Beyond"
- Format: 45-60 minute episodes with industry experts
- Frequency: 2 episodes per week (Tuesday/Friday)
- Distribution: Spotify, Apple Podcasts, YouTube, LinkedIn

AUTOMATION WORKFLOW:
1. Pre-Production Assistant
   - Guest research and background preparation
   - Interview question generation based on guest expertise
   - Technical setup checklists and reminders
   - Calendar integration and guest communication

2. Post-Production Pipeline
   - Audio processing and enhancement
   - Video editing with branded templates
   - Transcript generation and accuracy checking
   - Chapter markers and timestamp creation

3. Content Distribution System
   - Multi-platform publishing automation
   - RSS feed management and updates
   - Social media clip generation (30-60 second highlights)
   - Audiogram creation for social sharing

4. Audience Engagement Engine
   - Comment monitoring and response suggestions
   - Listener feedback analysis and categorization
   - Guest follow-up and relationship management
   - Audience growth tracking and optimization

TECHNICAL INTEGRATIONS:
- Podcast hosting platform APIs (Buzzsprout/Captivate)
- Video editing software automation
- Social media platform APIs
- Email marketing system integration
- CRM system for guest management

CONTENT OPTIMIZATION:
- SEO optimization for podcast titles and descriptions
- Keyword research for episode topics
- Trending topic identification
- Cross-platform content repurposing

FILES TO CREATE/UPDATE:
- backend/app/agents/podcast_agent.py
- backend/app/services/audio_processing.py
- backend/app/models/episodes.py
- backend/app/api/podcast.py
- backend/app/integrations/podcast_platforms.py
- frontend/src/components/PodcastStudio.tsx
- frontend/src/components/EpisodeManager.tsx

Implement with quality control checks, automated backup systems, and comprehensive analytics tracking.
```

---

## 💼 PROMPT 6: Deal Execution Agent

```
Build a Deal Execution Agent that manages the entire M&A process from initial evaluation through closing, supporting both platform subscribers and personal acquisitions.

DEAL LIFECYCLE MANAGEMENT:
- Initial opportunity assessment and screening
- Due diligence coordination and tracking
- Valuation modeling and scenario analysis
- Negotiation support and documentation
- Closing coordination and post-acquisition integration

CORE FUNCTIONALITIES:
1. Due Diligence Orchestrator
   - Automated checklist generation based on deal type
   - Document collection and organization system
   - Third-party vendor coordination (lawyers, accountants)
   - Risk assessment and red flag identification

2. Financial Modeling Engine
   - DCF model generation with sensitivity analysis
   - Comparable company analysis automation
   - LBO modeling for leveraged transactions
   - ROI projections and scenario planning

3. Deal Documentation Assistant
   - Letter of intent template generation
   - Purchase agreement clause recommendations
   - Regulatory compliance checking
   - Closing checklist and timeline management

4. Integration Planning System
   - Post-acquisition integration roadmap
   - Synergy identification and tracking
   - Cultural integration assessment
   - Performance monitoring setup

RISK MANAGEMENT:
- Automated risk scoring algorithms
- Compliance checking for regulatory requirements
- Insurance and warranty recommendations
- Contingency planning and scenario modeling

COLLABORATION FEATURES:
- Multi-party access with role-based permissions
- Real-time collaboration on documents
- Communication tracking and audit trails
- Progress reporting and milestone tracking

FILES TO CREATE/UPDATE:
- backend/app/agents/deal_execution_agent.py
- backend/app/services/due_diligence.py
- backend/app/models/transactions.py
- backend/app/api/deals.py
- backend/app/services/financial_modeling.py
- frontend/src/components/DealRoom.tsx
- frontend/src/components/DueDiligenceTracker.tsx

Build with enterprise-grade security, comprehensive audit logging, and integration with legal and financial systems.
```

---

## 🌐 PROMPT 7: Multi-Platform Integration Agent

```
Create a Multi-Platform Integration Agent that connects all business systems, automates data synchronization, and ensures seamless workflow across the entire business ecosystem.

INTEGRATION SCOPE:
- SaaS platform and user management
- Podcast hosting and distribution platforms
- Social media and content management systems
- CRM and email marketing platforms
- Financial systems and deal tracking
- Analytics and reporting tools

CORE INTEGRATION MODULES:
1. Data Synchronization Engine
   - Real-time data sync across all platforms
   - Conflict resolution and data validation
   - Automated backup and recovery systems
   - API rate limiting and error handling

2. Workflow Automation Hub
   - Cross-platform trigger and action systems
   - Business process automation
   - Event-driven architecture implementation
   - Custom workflow builder interface

3. Single Sign-On (SSO) Manager
   - Unified authentication across all systems
   - Role-based access control
   - Session management and security
   - Multi-factor authentication integration

4. API Gateway and Management
   - Centralized API management
   - Request routing and load balancing
   - Authentication and authorization
   - Rate limiting and monitoring

PLATFORM CONNECTIONS:
- Clerk (authentication)
- Stripe (payments)
- Buzzsprout/Captivate (podcast hosting)
- LinkedIn, Twitter, YouTube (social media)
- HubSpot/Pipedrive (CRM)
- Google Analytics (tracking)
- Render (hosting and deployment)

MONITORING AND ALERTING:
- System health monitoring
- Integration failure alerts
- Performance metrics tracking
- Automated troubleshooting

FILES TO CREATE/UPDATE:
- backend/app/agents/integration_agent.py
- backend/app/services/api_gateway.py
- backend/app/integrations/platform_connectors.py
- backend/app/models/integrations.py
- backend/app/api/integrations.py
- frontend/src/components/IntegrationDashboard.tsx
- backend/app/middleware/auth_middleware.py

Implement with robust error handling, comprehensive logging, and scalable architecture for future platform additions.
```

---

## 🎯 Implementation Priority Order

1. **Content Creation Agent** - Immediate content production needs
2. **Performance Analytics Agent** - Essential for tracking progress
3. **Subscriber Acquisition Agent** - Critical for revenue generation
4. **Deal Sourcing Agent** - Core business functionality
5. **Podcast Production Agent** - Content distribution automation
6. **Deal Execution Agent** - Advanced M&A functionality
7. **Multi-Platform Integration Agent** - System optimization

Each agent should be built incrementally, tested thoroughly, and integrated with the existing platform architecture. Use the BMAD methodology for structured development and ensure all agents work together as a cohesive system.
