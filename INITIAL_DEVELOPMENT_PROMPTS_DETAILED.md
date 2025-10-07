# 🚀 Initial Claude Code Prompts: Multi-Tenant SaaS Development

## Overview

These comprehensive Claude Code CLI prompts are designed for use in Cursor IDE to develop your multi-tenant M&A SaaS application. Each prompt provides detailed context, specific requirements, and implementation guidance for building enterprise-grade functionality.

## 📊 **Prompt 1: PostgreSQL Multi-Tenant Database Schema**

```
I'm building a multi-tenant M&A SaaS platform called "100 Days and Beyond" that helps private equity firms, investment bankers, and business owners manage deals from sourcing to exit. I need you to create a comprehensive PostgreSQL database schema with proper multi-tenant architecture.

CONTEXT:
- Multi-tenant SaaS with organization-based isolation
- Clerk authentication for user management
- Deal lifecycle: sourcing → due diligence → negotiation → closing → integration
- AI-powered analysis and insights
- Document management and collaboration
- Financial modeling and valuation tools

REQUIREMENTS:
1. Multi-tenant architecture with organization-based data isolation
2. User management with role-based permissions
3. Complete deal lifecycle management
4. Company and contact management
5. Document storage and version control
6. Financial modeling and valuation data
7. AI analysis results and insights
8. Audit trails and activity logging
9. Integration with external APIs
10. Performance optimization with proper indexing

TECHNICAL SPECIFICATIONS:
- PostgreSQL 17 with modern features
- UUID primary keys for security
- Proper foreign key relationships
- Indexes for query optimization
- Row-level security for multi-tenancy
- JSONB fields for flexible data
- Timestamp tracking for all records
- Soft deletes for data retention

Please create the complete database schema with:
- All table definitions with proper data types
- Relationships and foreign keys
- Indexes for performance
- Row-level security policies
- Initial migration scripts
- Sample data for testing

Files to create/update:
- backend/migrations/001_initial_schema.sql
- backend/migrations/002_sample_data.sql
- backend/app/models/database.py
- backend/app/models/schemas.py
```

## 🔧 **Prompt 2: FastAPI Backend Architecture**

```
I need you to build a comprehensive FastAPI backend for my multi-tenant M&A SaaS platform "100 Days and Beyond". The backend should handle authentication, multi-tenancy, and all business logic for deal management.

CONTEXT:
- Multi-tenant SaaS platform for M&A professionals
- Clerk authentication integration
- PostgreSQL database with organization-based isolation
- AI integration with Claude for deal analysis
- RESTful API with comprehensive endpoints
- Background tasks for heavy processing
- Real-time updates via WebSockets

REQUIREMENTS:
1. Clerk authentication middleware
2. Multi-tenant request handling
3. Complete CRUD operations for all entities
4. Deal pipeline management
5. Document upload and processing
6. Financial modeling endpoints
7. AI analysis integration
8. Real-time notifications
9. Background task processing
10. Comprehensive error handling
11. API documentation with OpenAPI
12. Rate limiting and security

TECHNICAL SPECIFICATIONS:
- FastAPI with async/await
- SQLAlchemy 2.0 with async support
- Pydantic v2 for data validation
- Clerk SDK for authentication
- Anthropic SDK for AI integration
- Celery for background tasks
- WebSocket support for real-time updates
- Comprehensive logging and monitoring

Please create:
- Authentication middleware and dependencies
- Database connection and session management
- All API endpoints with proper validation
- Background task definitions
- WebSocket handlers for real-time updates
- Error handling and logging
- API documentation and examples

Files to create/update:
- backend/app/main.py
- backend/app/core/auth.py
- backend/app/core/database.py
- backend/app/api/v1/deals.py
- backend/app/api/v1/companies.py
- backend/app/api/v1/documents.py
- backend/app/api/v1/analytics.py
- backend/app/services/ai_service.py
- backend/app/services/notification_service.py
- backend/app/tasks/background_tasks.py
```

## ⚛️ **Prompt 3: React Frontend Application**

```
I need you to build a modern React frontend for my multi-tenant M&A SaaS platform "100 Days and Beyond". The frontend should provide a professional, enterprise-grade interface for managing M&A deals.

CONTEXT:
- Multi-tenant M&A deal management platform
- Target users: PE firms, investment bankers, business owners
- Clerk authentication with organization management
- Real-time collaboration and updates
- Complex data visualization and analytics
- Document management and review
- Mobile-responsive design

REQUIREMENTS:
1. Clerk authentication integration
2. Multi-tenant organization switching
3. Deal pipeline with drag-and-drop
4. Company and contact management
5. Document upload and viewer
6. Financial modeling interface
7. Analytics dashboard with charts
8. Real-time notifications
9. User management and permissions
10. Professional, enterprise-grade UI
11. Mobile-responsive design
12. Offline capability for key features

TECHNICAL SPECIFICATIONS:
- React 18 with TypeScript
- Clerk React SDK for authentication
- Tailwind CSS with shadcn/ui components
- React Query for data fetching
- React Hook Form for form management
- Recharts for data visualization
- React DnD for drag-and-drop
- Socket.io for real-time updates
- PWA capabilities for offline use

Please create:
- Authentication setup with Clerk
- Multi-tenant organization management
- Deal pipeline with Kanban interface
- Company and contact management
- Document management system
- Analytics dashboard with charts
- User management interface
- Responsive layout components
- Real-time notification system

Files to create/update:
- frontend/src/App.tsx
- frontend/src/components/auth/AuthProvider.tsx
- frontend/src/components/deals/DealPipeline.tsx
- frontend/src/components/companies/CompanyList.tsx
- frontend/src/components/documents/DocumentManager.tsx
- frontend/src/components/analytics/Dashboard.tsx
- frontend/src/components/users/UserManagement.tsx
- frontend/src/hooks/useAuth.ts
- frontend/src/hooks/useRealtime.ts
- frontend/src/services/api.ts
```

## 🤖 **Prompt 4: AI Integration with Claude**

```
I need you to integrate Claude AI capabilities into my M&A SaaS platform "100 Days and Beyond" to provide intelligent deal analysis, market insights, and automated due diligence support.

CONTEXT:
- M&A SaaS platform for deal management
- Claude integration for intelligent analysis
- Document processing and summarization
- Market research and competitive analysis
- Risk assessment and due diligence
- Valuation modeling assistance
- Natural language querying of deal data

REQUIREMENTS:
1. Document analysis and summarization
2. Due diligence checklist generation
3. Market research and analysis
4. Competitive landscape assessment
5. Risk identification and scoring
6. Valuation model suggestions
7. Deal recommendation engine
8. Natural language query interface
9. Automated report generation
10. Integration with existing workflows

TECHNICAL SPECIFICATIONS:
- Anthropic Claude API integration
- MCP (Model Context Protocol) server setup
- Async processing for large documents
- Structured output for consistent results
- Error handling and retry logic
- Rate limiting and cost optimization
- Caching for repeated queries
- Background processing for heavy tasks

Please create:
- Claude service with comprehensive methods
- Document processing pipeline
- Market analysis functions
- Risk assessment algorithms
- Natural language query handler
- Report generation system
- Integration with existing API endpoints
- Background task definitions
- Caching and optimization

Files to create/update:
- backend/app/services/claude_service.py
- backend/app/services/document_processor.py
- backend/app/services/market_analyzer.py
- backend/app/services/risk_assessor.py
- backend/app/api/v1/ai_analysis.py
- backend/app/tasks/ai_tasks.py
- frontend/src/components/ai/AIAnalysis.tsx
- frontend/src/components/ai/QueryInterface.tsx
```

## 🔐 **Prompt 5: Authentication & Multi-Tenancy**

```
I need you to implement comprehensive authentication and multi-tenancy for my M&A SaaS platform "100 Days and Beyond" using Clerk for user management and organization-based data isolation.

CONTEXT:
- Multi-tenant SaaS with organization-based isolation
- Clerk authentication for enterprise features
- Role-based access control (Admin, Manager, Analyst, Viewer)
- Organization switching and management
- Invitation system for team members
- Audit logging for compliance
- SSO integration for enterprise clients

REQUIREMENTS:
1. Clerk authentication integration
2. Organization-based multi-tenancy
3. Role-based permission system
4. User invitation and onboarding
5. Organization switching interface
6. Audit trail for all actions
7. SSO configuration for enterprise
8. Session management and security
9. API key management for integrations
10. Compliance and data governance

TECHNICAL SPECIFICATIONS:
- Clerk SDK for authentication
- JWT token validation
- Middleware for tenant isolation
- Permission decorators for endpoints
- Database row-level security
- Audit logging system
- SSO provider integration
- Session management

Please create:
- Authentication middleware and guards
- Multi-tenant request handling
- Permission system with decorators
- User invitation workflow
- Organization management interface
- Audit logging system
- SSO configuration
- Security headers and CORS setup

Files to create/update:
- backend/app/core/auth.py
- backend/app/core/permissions.py
- backend/app/middleware/tenant.py
- backend/app/services/invitation_service.py
- backend/app/api/v1/organizations.py
- frontend/src/components/auth/OrganizationSwitcher.tsx
- frontend/src/components/users/InviteUser.tsx
- frontend/src/hooks/usePermissions.ts
```

## 📊 **Prompt 6: Analytics Dashboard & Reporting**

```
I need you to create a comprehensive analytics dashboard and reporting system for my M&A SaaS platform "100 Days and Beyond" that provides insights into deal performance, portfolio metrics, and business intelligence.

CONTEXT:
- M&A deal management platform
- Multiple user types: PE firms, investment banks, business owners
- Deal pipeline analytics and performance metrics
- Portfolio tracking and ROI analysis
- Market trends and competitive intelligence
- Custom reporting and data export
- Real-time dashboard updates

REQUIREMENTS:
1. Deal pipeline analytics
2. Portfolio performance tracking
3. ROI and financial metrics
4. Market trend analysis
5. Team performance metrics
6. Custom report builder
7. Data export capabilities
8. Real-time dashboard updates
9. Comparative analysis tools
10. Predictive analytics
11. Mobile-responsive charts
12. Scheduled report delivery

TECHNICAL SPECIFICATIONS:
- React with TypeScript for frontend
- Recharts for data visualization
- D3.js for advanced charts
- Real-time updates via WebSockets
- Export to PDF, Excel, CSV
- Responsive design for mobile
- Caching for performance
- Background data processing

Please create:
- Analytics dashboard with multiple chart types
- Portfolio performance tracking
- Custom report builder interface
- Data export functionality
- Real-time update system
- Mobile-responsive design
- Backend analytics endpoints
- Data aggregation services

Files to create/update:
- frontend/src/components/analytics/Dashboard.tsx
- frontend/src/components/analytics/PortfolioMetrics.tsx
- frontend/src/components/analytics/ReportBuilder.tsx
- frontend/src/components/charts/DealPipelineChart.tsx
- frontend/src/components/charts/ROIChart.tsx
- backend/app/api/v1/analytics.py
- backend/app/services/analytics_service.py
- backend/app/services/report_generator.py
```

## 🎯 **Implementation Guidelines**

### Development Workflow
1. **Start with Database Schema**: Establish the data foundation first
2. **Build Backend APIs**: Create the business logic and data access layer
3. **Develop Frontend Components**: Build the user interface incrementally
4. **Integrate AI Features**: Add intelligent capabilities progressively
5. **Implement Security**: Ensure proper authentication and authorization
6. **Add Analytics**: Build reporting and dashboard capabilities

### Best Practices
- **Type Safety**: Use TypeScript throughout the frontend
- **Error Handling**: Implement comprehensive error handling
- **Testing**: Write unit and integration tests
- **Documentation**: Document all APIs and components
- **Performance**: Optimize for speed and scalability
- **Security**: Follow security best practices
- **Accessibility**: Ensure WCAG compliance

### Quality Assurance
- **Code Reviews**: Review all code before deployment
- **Testing**: Automated testing for all features
- **Performance**: Monitor and optimize performance
- **Security**: Regular security audits
- **User Experience**: Continuous UX improvements
- **Documentation**: Keep documentation updated

These prompts provide a comprehensive foundation for building your multi-tenant M&A SaaS platform with enterprise-grade features and professional quality suitable for your target market of private equity firms, investment banks, and business owners.
