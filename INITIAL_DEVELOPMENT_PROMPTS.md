# 🚀 Initial Development Prompts for Multi-Tenant M&A SaaS Platform

## 📋 **Overview**

These prompts are designed for use with Claude Code in Cursor IDE to build your multi-tenant M&A SaaS platform. Each prompt focuses on a specific layer of the application and follows the BMAD methodology for structured development.

---

## 🗄️ **PROMPT 1: PostgreSQL Database Schema & Multi-Tenant Architecture**

### **Context**
You are building a multi-tenant M&A SaaS platform where each organization (tenant) has isolated data. The platform manages deals, users, documents, and AI analysis for M&A professionals.

### **Task**
Create a comprehensive PostgreSQL database schema with proper multi-tenant isolation using the tenant-per-schema approach. Include all necessary tables, relationships, indexes, and security policies.

### **Requirements**
- Multi-tenant architecture with schema-level isolation
- Support for organizations, users, deals, documents, and AI analysis
- Proper foreign key relationships and constraints
- Database indexes for performance optimization
- Row-level security policies where appropriate
- Migration scripts using Alembic
- Seed data for development and testing

### **Database Entities Needed**
1. **Tenants/Organizations** - Company information, subscription plans, settings
2. **Users** - User profiles, roles, permissions, Clerk integration
3. **Deals** - M&A transactions, stages, valuations, timelines
4. **Companies** - Target companies, acquirer companies, company profiles
5. **Documents** - Deal documents, due diligence files, contracts
6. **AI Analysis** - Claude-powered deal analysis, market research, valuations
7. **Activities** - Audit logs, user activities, deal timeline events
8. **Notifications** - System notifications, deal alerts, reminders

### **Technical Specifications**
- Use PostgreSQL 17 with modern features
- Implement proper JSONB columns for flexible data
- Create database functions for common operations
- Set up proper backup and recovery procedures
- Include performance monitoring queries

### **Files to Create/Update**
- `backend/app/models/` - SQLAlchemy models for all entities
- `backend/alembic/versions/` - Migration scripts
- `backend/app/core/database.py` - Database connection and tenant management
- `backend/app/core/tenant.py` - Multi-tenant utilities and middleware
- `backend/scripts/seed_data.py` - Development seed data
- `backend/sql/` - Raw SQL scripts for complex operations

---

## 🔧 **PROMPT 2: FastAPI Backend with Multi-Tenant API Architecture**

### **Context**
Build a robust FastAPI backend that serves the multi-tenant M&A SaaS platform. The backend must handle authentication via Clerk, implement proper tenant isolation, and provide comprehensive APIs for deal management.

### **Task**
Create a complete FastAPI backend with multi-tenant support, Clerk authentication, and comprehensive API endpoints for all M&A platform features.

### **Requirements**
- FastAPI with async/await for high performance
- Clerk authentication integration with JWT validation
- Multi-tenant middleware for automatic tenant resolution
- Comprehensive API endpoints for all business entities
- Input validation using Pydantic models
- Error handling and logging
- API documentation with OpenAPI/Swagger
- Rate limiting and security middleware
- Background tasks for AI processing
- File upload handling for documents

### **API Endpoints Needed**
1. **Authentication** - Login, logout, user profile, tenant switching
2. **Organizations** - CRUD operations, settings, subscription management
3. **Users** - User management, roles, permissions, invitations
4. **Deals** - Deal CRUD, stage management, valuation tracking
5. **Companies** - Company profiles, search, due diligence data
6. **Documents** - Upload, download, categorization, AI analysis
7. **AI Analysis** - Deal scoring, market research, valuation models
8. **Dashboard** - Analytics, KPIs, deal pipeline, notifications
9. **Reports** - Deal reports, portfolio analysis, performance metrics

### **Technical Specifications**
- Use dependency injection for tenant context
- Implement proper error handling with custom exceptions
- Add request/response logging and monitoring
- Create background tasks for heavy operations
- Implement caching with Redis (optional)
- Add API versioning support
- Include comprehensive test coverage

### **Files to Create/Update**
- `backend/app/api/` - All API route modules
- `backend/app/core/auth.py` - Clerk authentication middleware
- `backend/app/core/tenant.py` - Multi-tenant middleware and utilities
- `backend/app/schemas/` - Pydantic models for request/response
- `backend/app/services/` - Business logic services
- `backend/app/utils/` - Utility functions and helpers
- `backend/app/exceptions.py` - Custom exception classes
- `backend/tests/` - Comprehensive test suite

---

## ⚛️ **PROMPT 3: React Frontend with Multi-Tenant Dashboard**

### **Context**
Create a modern React frontend for the M&A SaaS platform with multi-tenant support, Clerk authentication, and a professional dashboard for deal management.

### **Task**
Build a comprehensive React application with TypeScript, Tailwind CSS, and shadcn/ui components that provides a world-class user experience for M&A professionals.

### **Requirements**
- React 19 with TypeScript for type safety
- Clerk authentication with organization switching
- Multi-tenant context management
- Responsive design with Tailwind CSS
- Professional UI components using shadcn/ui
- Real-time updates with WebSocket or polling
- File upload with drag-and-drop
- Data visualization with charts and graphs
- Advanced filtering and search capabilities
- Export functionality for reports and data

### **Key Features Needed**
1. **Authentication Flow** - Login, signup, organization selection
2. **Dashboard** - Deal pipeline, KPIs, recent activities, notifications
3. **Deal Management** - Deal creation, editing, stage progression, timeline
4. **Company Profiles** - Target company research, due diligence tracking
5. **Document Management** - Upload, categorization, AI analysis results
6. **AI Analysis** - Deal scoring, market research, valuation tools
7. **Team Management** - User invitations, role management, permissions
8. **Reports & Analytics** - Deal reports, portfolio analysis, performance metrics
9. **Settings** - Organization settings, user preferences, integrations

### **Technical Specifications**
- Use React Query for server state management
- Implement proper error boundaries and loading states
- Add form validation with React Hook Form and Zod
- Create reusable component library
- Implement proper routing with React Router
- Add accessibility features (ARIA labels, keyboard navigation)
- Include comprehensive error handling
- Optimize for performance with code splitting

### **Files to Create/Update**
- `frontend/src/components/` - Reusable UI components
- `frontend/src/pages/` - Page components for each route
- `frontend/src/hooks/` - Custom React hooks
- `frontend/src/services/` - API service functions
- `frontend/src/contexts/` - React contexts for global state
- `frontend/src/utils/` - Utility functions and helpers
- `frontend/src/types/` - TypeScript type definitions
- `frontend/src/lib/` - Third-party library configurations

---

## 🤖 **PROMPT 4: AI Integration with Claude MCP and Analysis Features**

### **Context**
Integrate Claude AI capabilities into the M&A platform to provide intelligent deal analysis, market research, and valuation assistance using the Claude MCP server and SDK.

### **Task**
Create comprehensive AI-powered features that leverage Claude's capabilities to assist M&A professionals with deal analysis, due diligence, and decision-making.

### **Requirements**
- Claude MCP server integration for AI capabilities
- Hugging Face integration for additional AI models
- Real-time AI analysis of deals and companies
- Intelligent document processing and summarization
- Market research and competitive analysis
- Automated valuation models and deal scoring
- Natural language querying of deal data
- AI-powered insights and recommendations

### **AI Features Needed**
1. **Deal Analysis** - Automated deal scoring, risk assessment, opportunity identification
2. **Market Research** - Industry analysis, competitive landscape, market trends
3. **Company Analysis** - Financial analysis, business model evaluation, growth potential
4. **Document Intelligence** - Contract analysis, due diligence document processing
5. **Valuation Models** - DCF analysis, comparable company analysis, precedent transactions
6. **Risk Assessment** - Deal risk factors, regulatory concerns, integration challenges
7. **Recommendation Engine** - Deal recommendations, strategic insights, next steps
8. **Natural Language Interface** - Chat-based querying of deal data and insights

### **Technical Specifications**
- Use Claude MCP server for primary AI capabilities
- Implement proper error handling for AI service failures
- Add caching for expensive AI operations
- Create background jobs for long-running AI tasks
- Implement proper rate limiting for AI API calls
- Add monitoring and logging for AI operations
- Include fallback mechanisms for AI service outages

### **Files to Create/Update**
- `backend/app/services/ai/` - AI service modules
- `backend/app/services/claude_service.py` - Claude MCP integration
- `backend/app/services/analysis_service.py` - Deal analysis logic
- `backend/app/api/ai.py` - AI-related API endpoints
- `frontend/src/components/ai/` - AI-powered UI components
- `frontend/src/services/ai.ts` - Frontend AI service functions

---

## 🔐 **PROMPT 5: Clerk Authentication & Multi-Tenant Security Implementation**

### **Context**
Implement comprehensive authentication and authorization using Clerk with proper multi-tenant security, role-based access control, and organization management.

### **Task**
Create a secure authentication system that handles user management, organization switching, role-based permissions, and proper tenant isolation throughout the application.

### **Requirements**
- Clerk authentication with JWT validation
- Multi-tenant organization management
- Role-based access control (RBAC)
- Permission-based feature access
- Secure API endpoints with proper authorization
- Organization switching functionality
- User invitation and onboarding flow
- Session management and security

### **Security Features Needed**
1. **Authentication Flow** - Login, signup, password reset, MFA support
2. **Organization Management** - Create, join, switch organizations
3. **Role Management** - Admin, Manager, Analyst, Viewer roles
4. **Permission System** - Granular permissions for features and data
5. **API Security** - JWT validation, rate limiting, CORS configuration
6. **Data Isolation** - Tenant-level data separation and access control
7. **Audit Logging** - User activities, data access, security events
8. **Compliance** - GDPR, SOC 2, data retention policies

### **Technical Specifications**
- Implement Clerk webhooks for user lifecycle events
- Create middleware for automatic tenant resolution
- Add proper error handling for authentication failures
- Implement session timeout and refresh mechanisms
- Add security headers and HTTPS enforcement
- Create comprehensive audit logging system
- Include security testing and vulnerability scanning

### **Files to Create/Update**
- `backend/app/core/auth.py` - Authentication middleware and utilities
- `backend/app/core/permissions.py` - Permission system and decorators
- `backend/app/models/auth.py` - User and organization models
- `backend/app/api/auth.py` - Authentication API endpoints
- `frontend/src/contexts/AuthContext.tsx` - Authentication context
- `frontend/src/components/auth/` - Authentication UI components
- `frontend/src/hooks/useAuth.ts` - Authentication hooks

---

## 📊 **PROMPT 6: Dashboard & Analytics Implementation**

### **Context**
Create a comprehensive dashboard and analytics system that provides M&A professionals with real-time insights, KPIs, and data visualizations for their deal pipeline and portfolio performance.

### **Task**
Build an advanced dashboard with interactive charts, real-time data, customizable widgets, and comprehensive analytics for deal management and portfolio tracking.

### **Requirements**
- Real-time dashboard with live data updates
- Interactive charts and data visualizations
- Customizable dashboard widgets and layouts
- Advanced filtering and search capabilities
- Export functionality for reports and data
- Mobile-responsive design
- Performance optimization for large datasets
- Drill-down capabilities for detailed analysis

### **Dashboard Features Needed**
1. **Deal Pipeline** - Visual pipeline with drag-and-drop, stage progression
2. **KPI Metrics** - Deal volume, success rates, average deal size, time to close
3. **Portfolio Overview** - Total portfolio value, ROI, performance trends
4. **Activity Feed** - Recent activities, notifications, team updates
5. **Financial Analytics** - Revenue tracking, valuation trends, investment returns
6. **Market Intelligence** - Industry trends, competitive analysis, market data
7. **Team Performance** - Individual and team metrics, productivity tracking
8. **Custom Reports** - Configurable reports, scheduled exports, data insights

### **Technical Specifications**
- Use Recharts or Chart.js for data visualizations
- Implement real-time updates with WebSocket or polling
- Add proper loading states and error handling
- Create responsive grid layouts for widgets
- Implement data caching for performance
- Add export functionality (PDF, Excel, CSV)
- Include accessibility features for charts and data

### **Files to Create/Update**
- `frontend/src/components/dashboard/` - Dashboard components and widgets
- `frontend/src/components/charts/` - Chart components and utilities
- `frontend/src/hooks/useDashboard.ts` - Dashboard data management
- `backend/app/api/analytics.py` - Analytics API endpoints
- `backend/app/services/analytics_service.py` - Analytics business logic
- `backend/app/utils/export.py` - Data export utilities

---

## 🎯 **Usage Instructions**

### **Getting Started**
1. **Clone the repository** and open in Cursor IDE
2. **Start with Prompt 1** to establish the database foundation
3. **Progress sequentially** through each prompt
4. **Use Claude Code** in Cursor to implement each prompt
5. **Test thoroughly** after each implementation
6. **Iterate and refine** based on results

### **Best Practices**
- **Follow BMAD methodology** for structured development
- **Implement comprehensive testing** for each component
- **Use TypeScript** for type safety throughout
- **Add proper error handling** and logging
- **Optimize for performance** and scalability
- **Include accessibility features** in the frontend
- **Document all APIs** and components

### **Development Workflow**
1. **Database First** - Establish solid data foundation
2. **Backend APIs** - Create robust API layer
3. **Frontend Components** - Build user interface
4. **AI Integration** - Add intelligent features
5. **Security Implementation** - Ensure proper authentication
6. **Dashboard & Analytics** - Complete with insights

Each prompt is designed to build upon the previous ones, creating a comprehensive, production-ready M&A SaaS platform that will help you achieve your £200 million wealth-building goal! 🚀
