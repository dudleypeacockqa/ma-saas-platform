# 🚀 OpenAI Codex BMAD-Method Prompts (Master Branch)

## Specialized Code Generation Prompts for M&A SaaS Platform

### 📋 **Updated for Master Branch Deployment**
- All sophisticated multipage website code is now in **master branch**
- Production deployment should reference **master branch**
- Environment variables and configuration are production-ready

---

## 🎯 **CODEX PROMPT 1: Master Branch Render Deployment**

```python
"""
BMAD-Method Codex Prompt: Master Branch Production Deployment

CONTEXT:
- M&A SaaS Platform with sophisticated multipage website ready for production
- Repository: dudleypeacockqa/ma-saas-platform
- Branch: master (contains all latest code including multipage website)
- Current: Basic site at https://100daysandbeyond.com needs replacement
- Backend: Live at https://ma-saas-backend.onrender.com

TECHNICAL STACK:
- Frontend: React 18 + Vite + TypeScript + Tailwind CSS
- Build System: pnpm
- Deployment: Render Static Site
- Authentication: Clerk
- Payments: Stripe

DIRECTORY STRUCTURE:
/ma-saas-platform/ (master branch)
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── HomePage.jsx
│   │   │   ├── PricingPage.jsx
│   │   │   ├── PlatformPage.jsx
│   │   │   └── DashboardPage.jsx
│   │   ├── components/
│   │   │   ├── Navigation.jsx
│   │   │   ├── Footer.jsx
│   │   │   └── platform/QuickActionsMenu.tsx
│   │   └── App.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.production
│   └── Dockerfile
├── render.yaml
├── RENDER_QUICK_DEPLOY.md
└── OPENAI_CODEX_BMAD_PROMPTS_MASTER.md

ENVIRONMENT VARIABLES (Production Ready):
VITE_API_URL=https://ma-saas-backend.onrender.com
VITE_CLERK_PUBLISHABLE_KEY=pk_live_Y2xlcmsuMTAwZGF5c2FuZGJleW9uZC5jb20k
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_51QwSgkFVol9SKsekxmCj4lDnvd1T6XZPi9VWuI7eKkxNopxC1N60ypXZzwQdyk64AuAQJMvQxuIJ1VuLeOdbeWQC00mV7ZDNB1
VITE_ENVIRONMENT=production
VITE_APP_NAME="100 Days and Beyond"
VITE_APP_VERSION=2.0.0

OBJECTIVE: Generate complete Render deployment configuration for master branch

REQUIRED OUTPUTS:
1. Render static site service configuration
2. Build commands optimized for production
3. Environment variable setup script
4. Custom domain configuration (100daysandbeyond.com)
5. Performance optimization settings
6. Security headers configuration

RENDER CONFIGURATION:
- Repository: dudleypeacockqa/ma-saas-platform
- Branch: master
- Root Directory: frontend
- Build Command: pnpm install && pnpm build
- Publish Directory: dist
- Node Version: 18

QUALITY GATES:
- Build completes without errors on master branch
- All environment variables properly injected
- Custom domain (100daysandbeyond.com) configured correctly
- HTTPS redirect implemented
- Performance optimization enabled (< 3s load time)
- All multipage navigation functional
"""

# Generate the master branch deployment automation code here
```

---

## 🎯 **CODEX PROMPT 2: Master Branch Revenue Optimization**

```typescript
/*
BMAD-Method Codex Prompt: Revenue Optimization (Master Branch)

CONTEXT:
- Sophisticated M&A SaaS platform deployed from master branch
- Three-tier pricing: Solo £279, Growth £798, Enterprise £1,598
- Integrated Stripe payments and Clerk authentication
- Need to maximize conversion rates and revenue generation

MASTER BRANCH CODE STRUCTURE:
/frontend/src/ (master branch)
├── pages/
│   ├── PricingPage.jsx (sophisticated pricing with Stripe integration)
│   ├── DashboardPage.jsx (user portal with subscription management)
│   └── HomePage.jsx (enterprise hero section with conversion optimization)
├── components/
│   ├── pricing/
│   │   ├── PricingCard.jsx
│   │   └── SubscriptionManager.jsx
│   ├── platform/
│   │   └── QuickActionsMenu.tsx (advanced dropdown with shortcuts)
│   └── analytics/
│       └── ConversionTracker.jsx
└── services/
    ├── stripe.js
    ├── clerk.js
    └── analytics.js

CURRENT MASTER BRANCH FEATURES:
- Sophisticated multipage website with enterprise navigation
- Advanced pricing components with ROI calculator
- Clerk authentication with subscription management
- Stripe payment processing integration
- Professional design system (Navy Blue #1E3A5F, Royal Blue #2E5B9C)

OBJECTIVE: Implement advanced revenue optimization on master branch

REQUIRED CODE IMPLEMENTATIONS:

1. Advanced Analytics Integration:
   - Google Analytics 4 with enhanced ecommerce tracking
   - Custom conversion funnel analysis
   - A/B testing framework for pricing experiments
   - Revenue attribution and customer journey mapping

2. Conversion Rate Optimization:
   - Dynamic pricing based on user behavior and market data
   - Personalized onboarding flows by user segment
   - Exit-intent popups with targeted offers
   - Social proof and testimonial automation

3. Customer Success Automation:
   - Progressive feature discovery and guided tours
   - Usage-based upgrade recommendations
   - Automated retention campaigns
   - Churn prediction and prevention workflows

4. Advanced Subscription Management:
   - Seamless upgrade/downgrade flows
   - Usage analytics and billing optimization
   - Custom enterprise pricing negotiations
   - Multi-currency and international payment support

TECHNICAL REQUIREMENTS:
- TypeScript for type safety and maintainability
- React hooks for efficient state management
- Integration with existing Clerk/Stripe master branch setup
- Tailwind CSS with established design system
- Mobile-responsive design for all devices
- Performance optimized (< 3s load time, 95+ Lighthouse score)

BUSINESS METRICS TO IMPLEMENT:
- Trial-to-paid conversion rate tracking
- Monthly recurring revenue (MRR) analytics
- Customer lifetime value (LTV) calculation
- Churn rate analysis by subscription tier
- Feature adoption and engagement metrics
*/

// Generate the revenue optimization code implementations for master branch here
```

---

## 🎯 **CODEX PROMPT 3: Master Branch Advanced Features**

```javascript
/**
 * BMAD-Method Codex Prompt: Advanced M&A Platform Features (Master Branch)
 * 
 * CONTEXT:
 * - Enterprise M&A SaaS platform deployed from master branch
 * - Target market: Investment banks, M&A advisors, corporate development teams
 * - Need advanced features to compete with industry leaders
 * - Platform must handle complex M&A workflows and enterprise data
 * 
 * MASTER BRANCH BACKEND STRUCTURE:
 * /backend/app/ (master branch)
 * ├── api/
 * │   ├── deals/ (deal pipeline management)
 * │   ├── documents/ (document collaboration)
 * │   ├── teams/ (team management)
 * │   ├── analytics/ (executive analytics)
 * │   ├── master_admin.py (business portal)
 * │   ├── content_creation.py (podcast/video studio)
 * │   ├── event_management.py (EventBrite integration)
 * │   └── lead_generation.py (marketing automation)
 * ├── models/
 * │   ├── deal.py
 * │   ├── document.py
 * │   ├── user.py
 * │   ├── subscription_management.py
 * │   └── content_creation.py
 * ├── services/
 * │   ├── stripe_enhanced_service.py
 * │   ├── ai_insights.py
 * │   ├── document_processor.py
 * │   └── notification_service.py
 * └── main.py (complete FastAPI application)
 * 
 * CURRENT MASTER BRANCH FEATURES:
 * - Comprehensive deal pipeline management
 * - Advanced document storage and collaboration
 * - Team management with role-based permissions
 * - Executive analytics and reporting
 * - Master Admin & Business Portal
 * - Content creation suite for podcasts and videos
 * - Event management with EventBrite integration
 * - Lead generation and marketing automation
 * 
 * OBJECTIVE: Implement next-generation M&A platform features
 * 
 * REQUIRED IMPLEMENTATIONS:
 * 
 * 1. AI-Powered Deal Intelligence:
 *    - Machine learning deal scoring and risk assessment
 *    - Automated market comparables analysis using real-time data
 *    - Due diligence checklist generation based on deal type
 *    - Financial model validation and scenario analysis
 *    - Predictive analytics for deal success probability
 * 
 * 2. Advanced Document Management:
 *    - OCR and intelligent document parsing
 *    - Automated data extraction from financial statements
 *    - Version control with comprehensive audit trails
 *    - Secure virtual data room functionality
 *    - Document workflow automation and approval processes
 * 
 * 3. Real-time Collaboration Platform:
 *    - WebSocket-based live editing and commenting
 *    - Video conferencing integration (Zoom, Teams)
 *    - Real-time deal room collaboration
 *    - Task assignment and progress tracking
 *    - Notification system for deal milestones
 * 
 * 4. Enterprise Integrations:
 *    - CRM system connectors (Salesforce, HubSpot, Pipedrive)
 *    - Financial data providers (Bloomberg, Refinitiv, FactSet)
 *    - Legal document management (iManage, NetDocuments)
 *    - Communication platforms (Slack, Microsoft Teams)
 *    - Accounting systems (QuickBooks, Xero, SAP)
 * 
 * 5. Advanced Analytics and Business Intelligence:
 *    - Deal pipeline forecasting with machine learning
 *    - Team performance metrics and optimization
 *    - Market trend analysis and competitive intelligence
 *    - Custom reporting engine with drag-and-drop interface
 *    - Executive dashboards with real-time KPIs
 * 
 * TECHNICAL SPECIFICATIONS:
 * - FastAPI backend with async/await patterns
 * - PostgreSQL with vector extensions for AI features
 * - Redis for caching and real-time features
 * - Celery for background task processing
 * - Docker containerization for scalability
 * - Comprehensive error handling and logging
 * - OpenAPI documentation for all endpoints
 * 
 * SECURITY REQUIREMENTS:
 * - SOC 2 Type II compliance implementation
 * - End-to-end encryption for sensitive M&A data
 * - Role-based access control (RBAC) with granular permissions
 * - Comprehensive audit logging for all actions
 * - Data residency compliance (GDPR, CCPA, SOX)
 * 
 * PERFORMANCE REQUIREMENTS:
 * - API response times < 200ms for all endpoints
 * - Support for 10,000+ concurrent users
 * - 99.9% uptime SLA with automatic failover
 * - Horizontal scaling capability with load balancing
 * - Database query optimization for large datasets
 * 
 * INTEGRATION PATTERNS:
 * - RESTful APIs with comprehensive OpenAPI documentation
 * - WebSocket connections for real-time collaboration
 * - Event-driven architecture with message queues
 * - Microservices architecture for independent scaling
 * - API rate limiting and authentication middleware
 */

// Generate the advanced platform feature implementations for master branch here
```

---

## 🎯 **CODEX PROMPT 4: Master Branch Mobile App**

```jsx
/*
BMAD-Method Codex Prompt: Mobile App Implementation (Master Branch)

CONTEXT:
- M&A SaaS platform deployed from master branch needs mobile companion
- Target users: M&A professionals requiring mobile access to deals and documents
- Core functionality: Deal updates, document review, team communication
- Platform: React Native for iOS and Android

MASTER BRANCH WEB PLATFORM:
- React frontend with TypeScript and sophisticated multipage design
- Clerk authentication with subscription management
- Stripe payments with three-tier pricing
- FastAPI backend with comprehensive M&A features
- Real-time WebSocket connections for collaboration

MOBILE APP REQUIREMENTS:

1. Core M&A Features:
   - Deal pipeline view with status updates
   - Document viewer with annotation capabilities
   - Push notifications for deal milestones and team updates
   - Offline capability for critical deal data
   - Biometric authentication for security

2. Technical Architecture:
   - React Native with TypeScript for type safety
   - Redux Toolkit for state management
   - React Navigation for seamless routing
   - Async Storage for offline data persistence
   - Push notifications (Firebase Cloud Messaging)

3. API Integration:
   - Shared authentication with master branch web platform
   - Real-time sync with backend API
   - Optimistic updates for better user experience
   - Background sync capabilities for offline usage

4. Security Features:
   - Certificate pinning for API communications
   - Encrypted local storage for sensitive data
   - Session management with automatic logout
   - Secure communication protocols (TLS 1.3)

DIRECTORY STRUCTURE:
/mobile/ (new directory in master branch)
├── src/
│   ├── components/
│   │   ├── deals/
│   │   │   ├── DealCard.tsx
│   │   │   └── DealPipeline.tsx
│   │   ├── documents/
│   │   │   ├── DocumentViewer.tsx
│   │   │   └── DocumentList.tsx
│   │   └── common/
│   │       ├── Header.tsx
│   │       └── LoadingSpinner.tsx
│   ├── screens/
│   │   ├── DealListScreen.tsx
│   │   ├── DealDetailScreen.tsx
│   │   ├── DocumentViewerScreen.tsx
│   │   └── ProfileScreen.tsx
│   ├── services/
│   │   ├── api.ts (integration with master branch backend)
│   │   ├── auth.ts (Clerk integration)
│   │   └── notifications.ts
│   ├── store/
│   │   ├── slices/
│   │   │   ├── dealsSlice.ts
│   │   │   └── authSlice.ts
│   │   └── index.ts
│   └── utils/
│       ├── storage.ts
│       └── encryption.ts
├── android/
├── ios/
└── package.json

PERFORMANCE REQUIREMENTS:
- App launch time < 3 seconds
- Smooth 60fps animations and transitions
- Efficient memory usage (< 100MB baseline)
- Battery optimization for background sync
- Network request optimization with caching

OFFLINE CAPABILITIES:
- Cache critical deal data for offline viewing
- Queue actions for sync when connection restored
- Offline document viewing with local storage
- Local search functionality for cached data
*/

// Generate the React Native mobile app implementation for master branch here
```

---

## 🎯 **CODEX PROMPT 5: Master Branch DevOps Infrastructure**

```yaml
# BMAD-Method Codex Prompt: DevOps Infrastructure (Master Branch)

# CONTEXT:
# - M&A SaaS platform scaling from master branch to enterprise customers
# - Need robust CI/CD, monitoring, and infrastructure automation
# - Current: Render deployment from master branch
# - Target: Enterprise-grade infrastructure with high availability

# MASTER BRANCH INFRASTRUCTURE:
# - Frontend: Render Static Site (master branch)
# - Backend: Render Web Service (master branch)
# - Database: Render PostgreSQL with vector extensions
# - Domain: 100daysandbeyond.com
# - Repository: dudleypeacockqa/ma-saas-platform (master branch)

# OBJECTIVE: Implement enterprise-grade DevOps for master branch

# REQUIRED IMPLEMENTATIONS:

# 1. CI/CD Pipeline (GitHub Actions for Master Branch):
#    - Automated testing on pull requests to master
#    - Staging environment deployment from master
#    - Production deployment with approval gates
#    - Database migration automation
#    - Security scanning and compliance checks

# 2. Infrastructure as Code (Master Branch):
#    - Terraform configurations for cloud resources
#    - Docker containerization optimization
#    - Kubernetes deployment manifests
#    - Environment-specific configurations

# 3. Monitoring and Observability:
#    - Application performance monitoring (APM)
#    - Error tracking and alerting
#    - Business metrics dashboards
#    - Log aggregation and analysis
#    - Uptime monitoring for 100daysandbeyond.com

# 4. Security Automation:
#    - Dependency vulnerability scanning
#    - Container security scanning
#    - Secrets management for production keys
#    - Compliance monitoring (SOC 2, GDPR)
#    - Backup and disaster recovery

# 5. Performance Optimization:
#    - CDN configuration for global delivery
#    - Database query optimization
#    - Caching strategies (Redis)
#    - Load balancing for high availability
#    - Auto-scaling policies

# TECHNICAL STACK:
# - CI/CD: GitHub Actions (master branch triggers)
# - Infrastructure: Terraform + AWS/GCP
# - Containers: Docker + Kubernetes
# - Monitoring: Datadog/New Relic + Sentry
# - Security: Snyk + HashiCorp Vault

# COMPLIANCE REQUIREMENTS:
# - SOC 2 Type II for enterprise customers
# - GDPR compliance for international users
# - Data encryption at rest and in transit
# - Comprehensive audit logging
# - Backup and recovery procedures

# Generate the DevOps automation code and configurations for master branch here
```

---

## 🛠️ **Master Branch Usage Guidelines**

### **Updated Deployment Instructions:**
- **Repository**: `dudleypeacockqa/ma-saas-platform`
- **Branch**: `master` (contains all latest code)
- **Frontend Directory**: `frontend`
- **Build Command**: `pnpm install && pnpm build`
- **Environment Variables**: Use production configuration from master branch

### **Key Advantages of Master Branch:**
- **Production Ready**: All code is in the main branch for deployment
- **Complete Integration**: Sophisticated multipage website fully integrated
- **Environment Variables**: Production configuration ready
- **OpenAI Prompts**: Updated to reference correct branch
- **Render Deployment**: Simplified configuration pointing to master

### **Immediate Next Steps:**
1. **Deploy from Master**: Update Render to use master branch
2. **Verify Environment Variables**: Ensure all production keys are configured
3. **Test Deployment**: Confirm sophisticated website replaces basic version
4. **Monitor Performance**: Track metrics and user engagement

---

This updated guide ensures all OpenAI Codex prompts reference the correct **master branch** for production deployment and development.
