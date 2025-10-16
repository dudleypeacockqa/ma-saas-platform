# Claude Code Prompts for Cursor IDE

## 🔐 **Authentication & Multi-Tenancy**

### Prompt 1: Frontend Clerk Integration

```
I need to integrate Clerk authentication into my React M&A SaaS platform. Please help me:

1. Set up ClerkProvider in App.jsx with proper configuration
2. Create protected routes that require authentication
3. Add SignIn and SignUp components with custom styling
4. Implement organization (tenant) switching in the header
5. Create a user profile management component
6. Handle authentication state throughout the app
7. Add proper loading states and error handling

Environment variables available:
- VITE_CLERK_PUBLISHABLE_KEY=<your-clerk-publishable-key>
- VITE_API_URL=https://api.100daysandbeyond.com

The app should support multi-tenant architecture where Clerk organizations represent different M&A firms/clients. Use modern React patterns with TypeScript, Tailwind CSS, and shadcn/ui components.
```

### Prompt 2: Backend Authentication Middleware

```
I need to create FastAPI authentication middleware that integrates with Clerk. Please help me:

1. Create middleware that validates Clerk JWT tokens
2. Extract user ID and organization ID from tokens
3. Create dependency functions for protected endpoints
4. Implement tenant isolation in database queries
5. Add role-based access control (admin, manager, user)
6. Handle Clerk webhooks for user/organization events
7. Create user and tenant management endpoints

Environment variables available:
- CLERK_SECRET_KEY=<your-clerk-secret-key>
- DATABASE_URL=postgresql://...

The backend should enforce strict tenant isolation and proper authorization for all M&A deal data.
```

### Prompt 3: Multi-Tenant Database Schema

```
I need to design a comprehensive database schema for a multi-tenant M&A SaaS platform. Please create:

1. Tenant/Organization models (maps to Clerk organizations)
2. User models with tenant relationships and roles
3. M&A Deal/Transaction models with complete deal lifecycle
4. Document management models for due diligence
5. Activity/Audit logging models
6. Subscription and billing models
7. Proper indexes, constraints, and relationships
8. Alembic migration files

Key requirements:
- Strict tenant isolation (all business data scoped to tenant_id)
- Support for deal pipeline management
- Document storage and categorization
- User activity tracking
- Soft deletes with deleted_at timestamps
- UUID primary keys for security

Use SQLAlchemy with proper type hints and validation.
```

## 💼 **M&A Core Features**

### Prompt 4: Deal Management System

```
I need to create a comprehensive deal management system for M&A transactions. Please build:

1. Deal pipeline dashboard with kanban-style board
2. Deal creation and editing forms with validation
3. Deal detail pages with all transaction information
4. Deal status tracking (Sourcing, Due Diligence, Negotiation, Closing)
5. Financial modeling components (valuation, returns)
6. Document upload and management for each deal
7. Activity timeline and notes system
8. Deal comparison and analytics features

Frontend: React with TypeScript, Tailwind CSS, shadcn/ui
Backend: FastAPI with SQLAlchemy models and CRUD operations

The system should handle complex M&A workflows and provide insights for deal evaluation.
```

### Prompt 5: Due Diligence Management

```
I need to create a due diligence management system for M&A deals. Please develop:

1. Due diligence checklist templates by industry
2. Document request and tracking system
3. Document categorization and tagging
4. Review status tracking (Pending, In Review, Approved, Issues)
5. Reviewer assignment and notifications
6. Risk assessment and flagging system
7. Progress reporting and dashboards
8. Integration with deal management system

Features needed:
- Customizable checklists
- File upload with categorization
- Collaborative review workflows
- Risk scoring algorithms
- Progress tracking and reporting

Use modern React patterns with proper state management and real-time updates.
```

### Prompt 6: Financial Analysis Tools

```
I need to create financial analysis tools for M&A deal evaluation. Please build:

1. Company valuation models (DCF, Comparable Company, Precedent Transaction)
2. Financial statement analysis and ratio calculations
3. Deal structure modeling (cash, stock, earnouts)
4. Return analysis (IRR, MOIC, payback period)
5. Sensitivity analysis and scenario modeling
6. Interactive charts and visualizations
7. Export capabilities (PDF reports, Excel models)
8. Historical deal comparison tools

Technical requirements:
- Complex financial calculations with proper validation
- Interactive charts using Chart.js or similar
- Excel-like interface for model inputs
- PDF generation for investment memos
- Real-time calculation updates

The tools should be professional-grade and suitable for institutional investors.
```

## 🤖 **AI Integration**

### Prompt 7: Claude AI Deal Analysis

```
I need to integrate Anthropic Claude for AI-powered deal analysis. Please create:

1. Deal summary and key insights generation
2. Market research and competitive analysis
3. Risk assessment and red flag identification
4. Document analysis and summarization
5. Valuation range suggestions based on comparables
6. Investment thesis generation
7. Due diligence question suggestions
8. Market trend analysis and predictions

Backend integration:
- Use Anthropic Claude API with proper error handling
- Cache AI responses for performance
- Implement rate limiting and cost controls
- Create structured prompts for consistent outputs
- Add human review workflows for AI suggestions

Frontend components:
- AI insights dashboard
- Interactive chat interface for deal questions
- AI-generated report previews
- Confidence scoring for AI recommendations

The AI should enhance human decision-making, not replace it.
```

### Prompt 8: Document Intelligence

```
I need to create an AI-powered document intelligence system for M&A due diligence. Please build:

1. Document upload and OCR processing
2. Automatic document categorization and tagging
3. Key information extraction (dates, amounts, parties)
4. Contract analysis and risk identification
5. Financial statement data extraction
6. Compliance and regulatory flag detection
7. Document similarity and duplicate detection
8. Searchable document database with AI-powered search

Technical implementation:
- File upload with progress tracking
- OCR integration for scanned documents
- Claude API for document analysis
- Vector database for semantic search
- Structured data extraction and validation
- Audit trail for all AI processing

The system should handle various document types (PDFs, Word, Excel, images) and provide accurate, actionable insights.
```

## 📊 **Analytics & Reporting**

### Prompt 9: Executive Dashboard

```
I need to create a comprehensive executive dashboard for M&A portfolio management. Please build:

1. Portfolio overview with key metrics
2. Deal pipeline visualization and forecasting
3. Performance analytics (returns, success rates)
4. Market trend analysis and insights
5. Team productivity and activity metrics
6. Financial performance tracking
7. Risk assessment and monitoring
8. Customizable reporting and exports

Dashboard features:
- Interactive charts and visualizations
- Real-time data updates
- Drill-down capabilities
- Custom date ranges and filters
- Export to PDF/Excel
- Mobile-responsive design
- Role-based view permissions

Use modern charting libraries (Chart.js, D3.js) and ensure fast loading with proper data caching.
```

### Prompt 10: Advanced Analytics

```
I need to create advanced analytics capabilities for M&A deal intelligence. Please develop:

1. Predictive deal success modeling
2. Market timing and cycle analysis
3. Valuation multiple trending and benchmarking
4. Industry consolidation tracking
5. Competitive landscape analysis
6. Deal flow optimization recommendations
7. Performance attribution analysis
8. Risk-adjusted return calculations

Analytics features:
- Machine learning models for predictions
- Statistical analysis and correlation studies
- Benchmarking against market data
- Scenario analysis and stress testing
- Custom metric definitions and tracking
- Automated insight generation
- API integration for market data

The system should provide institutional-quality analytics suitable for professional investors.
```

## 🌐 **Website & Marketing**

### Prompt 11: Landing Page Development

```
I need to create a world-class landing page for my M&A SaaS platform (100daysandbeyond.com). Please build:

1. Hero section with compelling value proposition
2. Feature highlights with benefits for each target audience
3. Social proof section (testimonials, case studies, logos)
4. Pricing tiers with clear differentiation
5. Lead capture forms and CTAs
6. FAQ section addressing common concerns
7. Footer with all necessary links and information
8. Mobile-responsive design with fast loading

Target audiences:
- Private Equity firms
- M&A professionals and investment bankers
- Business owners (buyers and sellers)
- Corporate development teams

The page should be conversion-optimized with clear value propositions for each audience segment.
```

### Prompt 12: Blog and Content System

```
I need to create a comprehensive blog and content management system. Please build:

1. Blog homepage with featured articles and categories
2. Article pages with SEO optimization
3. Author profiles and bio pages
4. Category and tag-based organization
5. Search functionality with filters
6. Related articles and recommendations
7. Social sharing and engagement features
8. Newsletter signup integration

Content categories:
- M&A Strategy and Best Practices
- Private Equity Insights
- Business Valuation Methods
- Due Diligence Processes
- Market Analysis and Trends
- Technology in M&A
- Regulatory and Legal Updates
- Case Studies and Success Stories

Each article should be 2000-2500 words, SEO-optimized, and provide genuine value to M&A professionals.
```

### Prompt 13: Podcast Integration

```
I need to create a podcast section for "100 Days and Beyond" podcast. Please build:

1. Podcast homepage with latest episodes
2. Episode detail pages with show notes
3. Audio player with progress tracking
4. Episode categorization and tagging
5. Guest profiles and bio pages
6. Transcript display and search
7. Subscription links to major platforms
8. Social sharing and engagement features

Podcast features:
- Embedded audio player
- Episode download capabilities
- Playlist creation and management
- Comment system for episodes
- Email notifications for new episodes
- RSS feed generation
- Analytics and listening metrics

The podcast focuses on M&A strategies, deal stories, and industry insights for professionals.
```

## 🔧 **Technical Infrastructure**

### Prompt 14: Performance Optimization

```
I need to optimize the performance of my M&A SaaS platform. Please help me:

1. Implement code splitting and lazy loading for React components
2. Optimize database queries with proper indexing
3. Add caching layers (Redis, browser caching)
4. Implement image optimization and compression
5. Minimize bundle sizes and eliminate unused code
6. Add service worker for offline capabilities
7. Optimize API response times and pagination
8. Implement proper error boundaries and fallbacks

Performance targets:
- Page load times under 3 seconds
- API response times under 500ms
- 95+ Lighthouse scores
- Smooth interactions on mobile devices
- Efficient memory usage
- Minimal network requests

Use modern optimization techniques and monitoring tools to achieve enterprise-grade performance.
```

### Prompt 15: Security Implementation

```
I need to implement comprehensive security measures for my M&A SaaS platform. Please help me:

1. Implement proper input validation and sanitization
2. Add rate limiting and DDoS protection
3. Secure file upload and storage
4. Implement audit logging for all sensitive operations
5. Add data encryption at rest and in transit
6. Create security headers and CSP policies
7. Implement proper session management
8. Add vulnerability scanning and monitoring

Security requirements:
- SOC 2 Type II compliance readiness
- GDPR compliance for EU users
- Multi-factor authentication support
- Regular security audits and penetration testing
- Secure API design with proper authentication
- Data backup and disaster recovery
- Incident response procedures

The platform handles sensitive financial data and must meet institutional security standards.
```

---

## 🎯 **Usage Instructions**

1. **Copy the relevant prompt** for your current development task
2. **Paste it into Cursor's Claude Code chat**
3. **Provide additional context** about your specific requirements
4. **Review the generated code** and ask for modifications if needed
5. **Test thoroughly** before implementing in production

## 📝 **Customization Tips**

- **Modify prompts** to match your specific business requirements
- **Add context** about your existing codebase and architecture
- **Specify constraints** like performance requirements or compliance needs
- **Request explanations** for complex implementations
- **Ask for tests** to be included with the generated code

These prompts are designed to work with the existing codebase structure and follow the development rules outlined in `.cursor/rules.md`.
