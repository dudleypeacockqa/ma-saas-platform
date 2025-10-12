# Cursor IDE BMAD Agent Prompts for M&A Platform Completion

## 🎯 Cursor-Specific BMAD Agent Commands

### Agent Activation Commands

#### 1. BMAD Master Agent Activation
```bash
cd ma-saas-platform && @bmad/core/agents/bmad-master.md
```

**Complete Activation Prompt:**
```
🧙 BMad Master Agent - M&A Platform Completion Phase

PROJECT CONTEXT:
- Name: "100 Days and Beyond" - M&A Ecosystem Platform
- Status: Phase 1 Complete (100%), Phase 2 Partial (40%)
- Priority: Complete Epic 2 (AI Features) and Epic 4 (Community Platform)
- Timeline: 80 days remaining to GTM launch
- BMAD Version: v6.0.0-alpha.0

IMMEDIATE OBJECTIVES:
1. Complete solution architecture for remaining epics
2. Implement AI valuation engine (Epic 2.1)
3. Build deal matching system (Epic 2.3)
4. Create community platform foundation (Epic 4.1-4.3)
5. Establish testing infrastructure

AVAILABLE RESOURCES:
- docs/PRD.md (20 FRs, 10 NFRs, 4 epics)
- docs/epics.md (27 stories defined)
- Backend: 22+ models, FastAPI, PostgreSQL
- Integrations: Clerk, Stripe, Cloudflare R2, Claude, OpenAI

EXECUTION MODE: Systematic story-driven development
QUALITY GATES: 80% test coverage, <2s response times, security review

Ready to execute Phase 2 completion workflows.
```

#### 2. Solution Architect Agent
```bash
cd ma-saas-platform && @bmad/core/agents/solution-architect.md
```

**Architect Activation Prompt:**
```
🏗️ Solution Architect Agent - M&A Platform Architecture

ARCHITECTURE MISSION:
Design technical solutions for Epic 2 (AI Intelligence) and Epic 4 (Community Platform)

CURRENT ARCHITECTURE:
- Multi-tenant PostgreSQL with RLS
- FastAPI backend with 22+ models
- Cloudflare R2 document storage
- Clerk authentication
- Stripe payment processing

ARCHITECTURE REQUIREMENTS:
1. AI Valuation Engine
   - Claude integration for deal analysis
   - Financial modeling algorithms
   - Risk assessment framework
   - Confidence scoring system

2. Deal Matching System
   - Semantic similarity algorithms
   - Buyer/seller preference matching
   - Real-time notification system
   - Background processing with Celery

3. Community Platform
   - Deal marketplace architecture
   - Forum discussion system
   - Knowledge library structure
   - Event management framework

CONSTRAINTS:
- Maintain <2s response times
- Support 1000+ concurrent users
- Preserve multi-tenant isolation
- Ensure GDPR compliance

DELIVERABLES:
- Technical specifications for each epic
- Database schema updates
- API design patterns
- Integration architecture
- Scalability considerations

Execute solution-architecture workflow for Epic 2 and Epic 4.
```

#### 3. AI Development Agent
```bash
cd ma-saas-platform && @bmad/core/agents/ai-developer.md
```

**AI Developer Activation Prompt:**
```
🤖 AI Developer Agent - M&A Intelligence Implementation

AI DEVELOPMENT MISSION:
Implement Epic 2 - AI-Powered Intelligence (currently 25% complete)

EPIC 2 REQUIREMENTS:
1. AI Valuation Engine (Story 2.1)
   - DCF model automation
   - Comparable company analysis
   - Precedent transaction analysis
   - Risk assessment algorithms
   - Confidence scoring

2. Deal Matching Engine (Story 2.3)
   - Semantic deal analysis
   - Buyer/seller preference matching
   - Similarity scoring algorithms
   - Automated recommendations

3. Document Intelligence (Story 2.7)
   - Contract term extraction
   - Key date identification
   - Financial metric extraction
   - Risk factor analysis

4. Predictive Analytics (Story 2.4)
   - Deal success probability
   - Timeline prediction
   - Market trend analysis
   - Performance forecasting

TECHNICAL STACK:
- Primary AI: Anthropic Claude (existing MCP integration)
- Secondary AI: OpenAI GPT-4 (existing integration)
- Vector DB: pgvector (PostgreSQL extension)
- Background Processing: Celery + Redis
- Document Processing: Cloudflare R2 + AI analysis

IMPLEMENTATION APPROACH:
- Service-oriented architecture
- Async processing for heavy AI tasks
- Caching for repeated analyses
- Error handling and fallbacks
- Performance monitoring

Create implementation stories for each AI feature with 1-3 day cycles.
```

#### 4. Community Platform Agent
```bash
cd ma-saas-platform && @bmad/core/agents/community-developer.md
```

**Community Developer Activation Prompt:**
```
👥 Community Developer Agent - Network Platform Implementation

COMMUNITY MISSION:
Implement Epic 4 - Community & Network (currently 10% complete)

EPIC 4 REQUIREMENTS:
1. Deal Marketplace (Story 4.1)
   - Public deal listings
   - Private deal rooms
   - Interest/bidding system
   - Deal status tracking
   - Seller/buyer matching

2. Community Forums (Story 4.2)
   - Industry discussion boards
   - Deal-specific discussions
   - Expert Q&A sections
   - Moderation system
   - Reputation scoring

3. Knowledge Library (Story 4.3)
   - Document repository
   - Best practices library
   - Template marketplace
   - Search and categorization
   - Version control

4. Event Management (Story 4.5)
   - Virtual event hosting
   - Registration system
   - Networking features
   - Recording and playback
   - Calendar integration

TECHNICAL REQUIREMENTS:
- Models: community_posts, deal_listings, knowledge_articles, events
- Real-time features: WebSocket for live discussions
- Search: Full-text search with PostgreSQL
- Permissions: Role-based access control
- Moderation: Automated content filtering

INTEGRATION POINTS:
- User/organization models (existing)
- Deal management system (existing)
- Document storage (Cloudflare R2)
- Notification system (SendGrid)
- Payment processing (Stripe for events)

Create implementation stories for marketplace, forums, and knowledge base.
```

---

## 🔄 Workflow-Specific Agent Prompts

### 1. Story Creation Agent
```bash
cd ma-saas-platform && @bmad/bmm/workflows/4-implementation/create-story.md
```

**Story Creation Prompt Template:**
```
📝 Story Creation Agent - [EPIC_NAME] Implementation

STORY CONTEXT:
- Epic: [EPIC_NUMBER] - [EPIC_NAME]
- Current Status: [CURRENT_PERCENTAGE]% complete
- Priority: [P0/P1/P2]
- Dependencies: [LIST_DEPENDENCIES]

STORY REQUIREMENTS:
[DETAILED_FEATURE_REQUIREMENTS]

TECHNICAL SPECIFICATIONS:
- Service Layer: app/services/[service_name].py
- API Layer: app/api/[api_name].py
- Models: [model_updates_needed]
- Database: [schema_changes]
- Integration: [external_services]

ACCEPTANCE CRITERIA:
[DETAILED_ACCEPTANCE_CRITERIA_IN_GHERKIN_FORMAT]

STORY SIZING:
- Target: 1-3 days per story
- Complexity: [Simple/Medium/Complex]
- Risk Level: [Low/Medium/High]

QUALITY GATES:
- Unit tests with 80%+ coverage
- Integration tests for API endpoints
- Performance tests (<2s response time)
- Security review for sensitive operations
- Documentation updates

Create [NUMBER] implementation stories with clear tasks and dependencies.
```

### 2. Technical Specification Agent
```bash
cd ma-saas-platform && @bmad/bmm/workflows/3-solutioning/tech-spec.md
```

**Tech Spec Prompt Template:**
```
🔧 Technical Specification Agent - [FEATURE_NAME]

FEATURE OVERVIEW:
[FEATURE_DESCRIPTION_AND_PURPOSE]

TECHNICAL REQUIREMENTS:
1. Functional Requirements
   [LIST_FUNCTIONAL_REQUIREMENTS]

2. Non-Functional Requirements
   - Performance: [PERFORMANCE_TARGETS]
   - Scalability: [SCALABILITY_REQUIREMENTS]
   - Security: [SECURITY_REQUIREMENTS]
   - Reliability: [RELIABILITY_TARGETS]

ARCHITECTURE DESIGN:
1. Service Architecture
   [SERVICE_LAYER_DESIGN]

2. Data Architecture
   [DATABASE_SCHEMA_DESIGN]

3. API Architecture
   [API_ENDPOINT_DESIGN]

4. Integration Architecture
   [EXTERNAL_SERVICE_INTEGRATIONS]

IMPLEMENTATION APPROACH:
- Development Strategy: [STRATEGY]
- Testing Strategy: [TESTING_APPROACH]
- Deployment Strategy: [DEPLOYMENT_PLAN]
- Monitoring Strategy: [MONITORING_PLAN]

RISK ASSESSMENT:
[TECHNICAL_RISKS_AND_MITIGATIONS]

Create comprehensive technical specification with implementation roadmap.
```

### 3. Testing Infrastructure Agent
```bash
cd ma-saas-platform && @bmad/bmm/workflows/4-implementation/testing-setup.md
```

**Testing Setup Prompt:**
```
🧪 Testing Infrastructure Agent - Comprehensive Test Suite

TESTING MISSION:
Establish comprehensive testing infrastructure for M&A platform

CURRENT STATE:
- 15 verification scripts exist
- No proper unit test framework
- No test coverage metrics
- Integration tests only

TESTING REQUIREMENTS:
1. Unit Testing Framework
   - pytest with async support
   - Test fixtures and factories
   - Mocking for external services
   - Coverage reporting (target: 80%+)

2. Integration Testing
   - API endpoint testing
   - Database integration tests
   - External service integration tests
   - End-to-end workflow tests

3. Performance Testing
   - Load testing for API endpoints
   - Database performance tests
   - Concurrent user testing
   - Response time validation

4. Security Testing
   - Authentication/authorization tests
   - Input validation tests
   - SQL injection prevention
   - XSS prevention tests

TECHNICAL IMPLEMENTATION:
- Framework: pytest + pytest-asyncio
- Coverage: pytest-cov
- Mocking: pytest-mock + httpx-mock
- Database: Test database with fixtures
- CI/CD: GitHub Actions integration

Create testing infrastructure with comprehensive test suites.
```

---

## 🚀 Phase-Specific Agent Prompts

### Phase 2 Completion Agent
```bash
cd ma-saas-platform && @bmad/core/agents/phase2-completion.md
```

**Phase 2 Completion Prompt:**
```
🎯 Phase 2 Completion Agent - Advanced Features Implementation

PHASE 2 MISSION:
Complete Phase 2 (40% → 100%) within 30 days

REMAINING PHASE 2 WORK:
1. Epic 2 - AI Intelligence (25% → 100%)
   - AI valuation engine
   - Deal matching system
   - Document intelligence
   - Predictive analytics

2. Epic 4 - Community Platform (10% → 100%)
   - Deal marketplace
   - Community forums
   - Knowledge library
   - Event management

3. Technical Infrastructure
   - Testing framework
   - Performance optimization
   - Security hardening
   - Documentation updates

EXECUTION STRATEGY:
- Week 1: AI valuation engine + deal matching
- Week 2: Community platform foundation
- Week 3: Advanced AI features + testing
- Week 4: Event management + optimization

QUALITY TARGETS:
- 80%+ test coverage
- <2s response times
- 99.9% uptime
- Security review passed

DELIVERABLES:
- Functional AI-powered features
- Active community platform
- Comprehensive test suite
- Performance benchmarks
- Security audit report

Execute systematic completion of Phase 2 with quality gates.
```

### Phase 3 Preparation Agent
```bash
cd ma-saas-platform && @bmad/core/agents/phase3-preparation.md
```

**Phase 3 Preparation Prompt:**
```
📈 Phase 3 Preparation Agent - Market Launch Readiness

PHASE 3 MISSION:
Prepare for market launch (Days 31-60)

PHASE 3 COMPONENTS:
1. Content Marketing Engine
   - AI-powered content generation
   - SEO optimization
   - Social media automation
   - Lead capture systems

2. Conversion Optimization
   - Landing page A/B testing
   - Onboarding flow optimization
   - Trial-to-paid conversion
   - User engagement analytics

3. Launch Execution
   - Beta user program
   - Product hunt launch
   - PR and media outreach
   - Customer success program

TECHNICAL PREPARATION:
- Content management system
- Analytics and tracking
- A/B testing framework
- Email marketing automation
- Customer support tools

MARKETING INFRASTRUCTURE:
- SEO-optimized website
- Lead generation funnels
- Customer onboarding flows
- Success metrics dashboard
- Feedback collection system

Create implementation plan for Phase 3 market launch preparation.
```

---

## 🎮 Agent Coordination Commands

### Multi-Agent Workflow Coordination
```bash
cd ma-saas-platform && @bmad/core/agents/workflow-coordinator.md
```

**Workflow Coordination Prompt:**
```
🎭 Workflow Coordinator Agent - Multi-Agent Orchestration

COORDINATION MISSION:
Orchestrate multiple BMAD agents for parallel development

AGENT COORDINATION:
1. Solution Architect Agent
   - Create technical specifications
   - Define integration patterns
   - Establish quality gates

2. AI Developer Agent
   - Implement Epic 2 features
   - Integrate Claude/OpenAI services
   - Build AI workflows

3. Community Developer Agent
   - Implement Epic 4 features
   - Build social features
   - Create engagement systems

4. Testing Agent
   - Establish test infrastructure
   - Create test suites
   - Monitor quality metrics

PARALLEL EXECUTION:
- Week 1: Architecture + AI Valuation + Community Foundation
- Week 2: Deal Matching + Forums + Testing Framework
- Week 3: Document Intelligence + Knowledge Library + Performance
- Week 4: Predictive Analytics + Event Management + Security

COORDINATION POINTS:
- Daily standup summaries
- Integration checkpoints
- Quality gate reviews
- Dependency management

DELIVERABLE INTEGRATION:
- Unified codebase
- Consistent API patterns
- Shared data models
- Common testing standards

Execute coordinated multi-agent development workflow.
```

---

## 📊 Success Metrics and Monitoring

### Progress Tracking Agent
```bash
cd ma-saas-platform && @bmad/core/agents/progress-tracker.md
```

**Progress Tracking Prompt:**
```
📊 Progress Tracking Agent - Development Metrics

TRACKING MISSION:
Monitor and report development progress across all epics

METRICS TO TRACK:
1. Epic Completion Rates
   - Epic 1: 85% → 100%
   - Epic 2: 25% → 100%
   - Epic 3: 55% → 100%
   - Epic 4: 10% → 100%

2. Quality Metrics
   - Test coverage percentage
   - Performance benchmarks
   - Security scan results
   - Code quality scores

3. Timeline Metrics
   - Story completion velocity
   - Sprint burn-down rates
   - Milestone achievement
   - Risk indicators

REPORTING FORMAT:
- Daily progress updates
- Weekly milestone reports
- Epic completion summaries
- Quality gate assessments

DASHBOARD ELEMENTS:
- Epic progress visualization
- Story completion tracking
- Quality metrics trends
- Timeline adherence

Generate automated progress reports and quality assessments.
```

---

## 🎯 Quick Reference Commands

### Immediate Action Commands (Copy-Paste Ready)

```bash
# 1. Activate BMAD Master for immediate work
cd ma-saas-platform && @bmad/core/agents/bmad-master.md

# 2. Create solution architecture
cd ma-saas-platform && @bmad/bmm/workflows/3-solutioning/solution-architecture.md

# 3. Generate AI valuation stories
cd ma-saas-platform && @bmad/bmm/workflows/4-implementation/create-story.md

# 4. Generate community platform stories  
cd ma-saas-platform && @bmad/bmm/workflows/4-implementation/create-story.md

# 5. Setup testing infrastructure
cd ma-saas-platform && @bmad/bmm/workflows/4-implementation/testing-setup.md

# 6. Create technical specifications
cd ma-saas-platform && @bmad/bmm/workflows/3-solutioning/tech-spec.md

# 7. Coordinate multi-agent workflow
cd ma-saas-platform && @bmad/core/agents/workflow-coordinator.md

# 8. Track progress and metrics
cd ma-saas-platform && @bmad/core/agents/progress-tracker.md
```

### Priority Execution Order:
1. **Solution Architecture** (2-3 hours)
2. **AI Valuation Engine** (3-5 days)
3. **Community Platform Foundation** (5-7 days)
4. **Deal Matching System** (3-5 days)
5. **Testing Infrastructure** (2-3 days)
6. **Advanced AI Features** (7-10 days)
7. **Event Management** (3-5 days)
8. **Performance Optimization** (2-3 days)

**Total Estimated Time: 25-35 days to complete Phase 2**

Use these prompts systematically with BMAD Method in Cursor IDE to complete your M&A platform and achieve your £200M wealth-building goal!
