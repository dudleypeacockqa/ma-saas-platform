# 🎯 Core M&A Feature Development Prompts for Claude Code CLI

## Overview

These prompts are specifically designed for developing the core M&A functionality of your SaaS platform using Claude Code CLI in Cursor IDE. Each prompt focuses on essential M&A processes that both your subscribers and your personal deal activities require.

---

## 🔍 PROMPT 1: Deal Discovery & Sourcing System

```
I need you to build a comprehensive Deal Discovery & Sourcing System for my M&A SaaS platform that helps users find, evaluate, and track potential acquisition opportunities.

BUSINESS CONTEXT:
- Platform: 100daysandbeyond.com M&A deal management SaaS
- Users: Private equity firms, investment bankers, business buyers, corporate development teams
- Goal: Systematically identify and evaluate middle-market acquisition opportunities (£1M-£50M revenue)
- Integration: Existing multi-tenant architecture with Clerk authentication

CORE FUNCTIONALITY:
1. Opportunity Discovery Engine
   - Industry database integration (Companies House, SEC EDGAR, Crunchbase)
   - Market intelligence monitoring (news, reports, industry publications)
   - Distressed company identification through financial indicators
   - Succession planning opportunity detection
   - Competitor acquisition tracking

2. Company Screening & Filtering
   - Revenue range filtering (£1M-£50M)
   - Industry sector categorization (technology, healthcare, manufacturing, services)
   - Geographic location filtering (UK, US, EU markets)
   - Financial health scoring based on available data
   - Strategic fit assessment criteria

3. Deal Opportunity Scoring
   - Proprietary scoring algorithm based on financial metrics
   - Growth trajectory analysis using historical data
   - Market position evaluation and competitive landscape
   - Risk factor identification and weighting
   - ROI projection modeling

4. Opportunity Tracking & Management
   - Deal pipeline management with stage progression
   - Contact information and relationship tracking
   - Document storage and organization
   - Activity logging and follow-up reminders
   - Team collaboration and note sharing

TECHNICAL REQUIREMENTS:
- FastAPI backend with PostgreSQL database
- Real-time data updates and notifications
- API integrations with external data sources
- Advanced search and filtering capabilities
- Export functionality for reports and presentations

DATA SOURCES:
- Companies House API for UK company data
- SEC EDGAR database for US public companies
- Industry databases and market intelligence platforms
- News APIs for market monitoring
- Financial data providers for screening criteria

FILES TO CREATE/UPDATE:
- backend/app/models/opportunities.py
- backend/app/services/deal_sourcing.py
- backend/app/api/opportunities.py
- backend/app/tasks/data_collection.py
- frontend/src/components/OpportunityDashboard.tsx
- frontend/src/components/DealPipeline.tsx

Build this with proper error handling, rate limiting for API calls, and comprehensive logging for audit trails.
```

---

## 💰 PROMPT 2: Financial Modeling & Valuation Engine

```
Create a sophisticated Financial Modeling & Valuation Engine that provides comprehensive valuation analysis for M&A transactions, supporting both platform subscribers and personal deal evaluation.

BUSINESS CONTEXT:
- Target: Middle-market companies with complex financial structures
- Users: M&A professionals requiring detailed financial analysis
- Output: Professional-grade valuation reports and models
- Integration: Deal pipeline and opportunity management system

VALUATION METHODOLOGIES:
1. Discounted Cash Flow (DCF) Analysis
   - Revenue forecasting with multiple scenarios (base, optimistic, pessimistic)
   - Operating expense modeling with scalability assumptions
   - Working capital and capital expenditure projections
   - Terminal value calculations using perpetuity and exit multiple methods
   - Sensitivity analysis for key assumptions

2. Comparable Company Analysis
   - Industry peer identification and selection
   - Trading multiple analysis (EV/Revenue, EV/EBITDA, P/E ratios)
   - Size and growth adjustments for comparability
   - Liquidity and control premium considerations
   - Market condition adjustments

3. Precedent Transaction Analysis
   - Historical transaction database integration
   - Transaction multiple analysis with deal characteristics
   - Strategic vs financial buyer premium analysis
   - Market timing and cycle adjustments
   - Deal structure impact on valuation

4. Leveraged Buyout (LBO) Modeling
   - Debt capacity analysis based on cash flow coverage
   - Capital structure optimization
   - Return scenarios for different hold periods
   - Management equity participation modeling
   - Exit strategy analysis and returns

ADVANCED FEATURES:
- Monte Carlo simulation for risk analysis
- Scenario planning with probability weighting
- Real-time market data integration
- Automated report generation with charts and graphs
- Collaborative modeling with version control

TECHNICAL IMPLEMENTATION:
- Python-based financial modeling engine
- NumPy and Pandas for numerical calculations
- Matplotlib/Plotly for visualization
- Real-time market data APIs
- PDF report generation with professional formatting

FILES TO CREATE/UPDATE:
- backend/app/services/valuation_engine.py
- backend/app/models/financial_models.py
- backend/app/api/valuations.py
- backend/app/utils/financial_calculations.py
- frontend/src/components/ValuationDashboard.tsx
- frontend/src/components/FinancialModeling.tsx

Implement with proper financial calculation accuracy, comprehensive error handling, and professional report formatting.
```

---

## 📋 PROMPT 3: Due Diligence Management System

```
Build a comprehensive Due Diligence Management System that orchestrates the entire due diligence process from initial planning through completion, supporting both buy-side and sell-side transactions.

BUSINESS CONTEXT:
- Process: Complete due diligence workflow management
- Users: Deal teams, advisors, and third-party service providers
- Scope: Financial, legal, commercial, operational, and technical due diligence
- Integration: Document management, team collaboration, and reporting systems

CORE MODULES:
1. Due Diligence Planning & Setup
   - Deal-specific checklist generation based on industry and transaction type
   - Work stream organization (financial, legal, commercial, operational, IT)
   - Team assignment and role-based access control
   - Timeline creation with milestone tracking
   - Budget planning and vendor coordination

2. Document Request & Management
   - Automated document request list generation
   - Virtual data room integration and management
   - Document categorization and indexing
   - Version control and audit trails
   - Access logging and security monitoring

3. Work Stream Coordination
   - Task assignment and progress tracking
   - Cross-functional dependency management
   - Issue identification and escalation procedures
   - Quality control and review processes
   - Communication and collaboration tools

4. Risk Assessment & Red Flag Management
   - Automated risk scoring based on findings
   - Red flag identification and categorization
   - Impact assessment and mitigation planning
   - Decision tree analysis for deal continuation
   - Risk register maintenance and reporting

5. Reporting & Documentation
   - Real-time progress dashboards
   - Executive summary generation
   - Detailed findings reports by work stream
   - Management presentation creation
   - Final due diligence report compilation

INTEGRATION CAPABILITIES:
- Third-party service provider portals
- Legal and accounting firm collaboration
- Expert network integration
- Reference call management
- Site visit coordination and documentation

TECHNICAL ARCHITECTURE:
- Multi-tenant document storage with encryption
- Role-based access control with audit logging
- Real-time collaboration features
- Mobile accessibility for field work
- Integration APIs for external service providers

FILES TO CREATE/UPDATE:
- backend/app/models/due_diligence.py
- backend/app/services/dd_orchestration.py
- backend/app/api/due_diligence.py
- backend/app/utils/document_management.py
- frontend/src/components/DueDiligenceDashboard.tsx
- frontend/src/components/DocumentRoom.tsx
- frontend/src/components/TaskManagement.tsx

Build with enterprise-grade security, comprehensive audit trails, and scalable document management capabilities.
```

---

## 🤝 PROMPT 4: Deal Negotiation & Structuring Platform

```
Develop a Deal Negotiation & Structuring Platform that supports complex M&A negotiations, deal structuring, and documentation management throughout the transaction process.

BUSINESS CONTEXT:
- Process: End-to-end deal negotiation and structuring
- Users: Deal principals, advisors, and legal teams
- Scope: Term sheet development through definitive agreement execution
- Integration: Valuation models, due diligence findings, and legal documentation

NEGOTIATION MANAGEMENT:
1. Term Sheet Development
   - Interactive term sheet builder with industry templates
   - Valuation integration with negotiation parameters
   - Deal structure optimization (cash, stock, earnouts, escrows)
   - Tax efficiency analysis and structuring recommendations
   - Comparative analysis of negotiation positions

2. Negotiation Tracking & Analytics
   - Position tracking for all deal terms
   - Concession analysis and trade-off modeling
   - Negotiation timeline and milestone management
   - Communication logging and decision documentation
   - Market benchmark comparison for deal terms

3. Deal Structure Optimization
   - Capital structure analysis and recommendations
   - Tax optimization strategies and modeling
   - Regulatory compliance checking
   - Financing structure evaluation
   - Risk allocation and mitigation strategies

4. Documentation Management
   - Legal document template library
   - Automated document generation from negotiated terms
   - Version control and redlining capabilities
   - Signature workflow and execution tracking
   - Closing checklist and coordination

ADVANCED FEATURES:
- AI-powered negotiation insights and recommendations
- Market intelligence integration for benchmarking
- Scenario modeling for different deal structures
- Automated compliance checking
- Integration with legal and tax advisory systems

COLLABORATION TOOLS:
- Multi-party negotiation workspaces
- Real-time communication and messaging
- Document sharing and collaboration
- Decision tracking and approval workflows
- Meeting scheduling and agenda management

TECHNICAL IMPLEMENTATION:
- Secure multi-party collaboration platform
- Document generation and management system
- Real-time synchronization and updates
- Integration with e-signature platforms
- Comprehensive audit and compliance logging

FILES TO CREATE/UPDATE:
- backend/app/models/negotiations.py
- backend/app/services/deal_structuring.py
- backend/app/api/negotiations.py
- backend/app/utils/document_generation.py
- frontend/src/components/NegotiationDashboard.tsx
- frontend/src/components/TermSheetBuilder.tsx
- frontend/src/components/DealStructuring.tsx

Implement with robust security, comprehensive audit trails, and seamless integration with legal and financial systems.
```

---

## 🏢 PROMPT 5: Post-Acquisition Integration Planning

```
Create a comprehensive Post-Acquisition Integration Planning system that manages the critical 100-day integration process and long-term value creation initiatives.

BUSINESS CONTEXT:
- Timeline: Pre-closing planning through 24-month integration
- Users: Integration teams, executives, and operational managers
- Scope: Operational, financial, cultural, and strategic integration
- Goal: Maximize synergy realization and minimize integration risks

INTEGRATION MODULES:
1. Integration Planning & Strategy
   - Integration approach selection (absorption, preservation, symbiosis)
   - Synergy identification and quantification
   - Integration timeline and milestone planning
   - Resource allocation and team formation
   - Risk assessment and mitigation planning

2. Operational Integration Management
   - Systems integration planning and execution
   - Process harmonization and optimization
   - Organizational design and restructuring
   - Talent retention and development programs
   - Customer and supplier relationship management

3. Financial Integration & Synergy Tracking
   - Financial systems integration and reporting
   - Synergy realization tracking and measurement
   - Cost reduction initiative management
   - Revenue enhancement opportunity identification
   - Integration cost monitoring and control

4. Cultural Integration & Change Management
   - Cultural assessment and integration planning
   - Communication strategy and execution
   - Change management program development
   - Employee engagement and retention initiatives
   - Leadership alignment and development

5. Performance Monitoring & Optimization
   - KPI dashboard and performance tracking
   - Integration milestone monitoring
   - Issue identification and resolution
   - Continuous improvement initiatives
   - Success measurement and reporting

SYNERGY REALIZATION:
- Revenue synergy identification and tracking
- Cost synergy quantification and realization
- Operational efficiency improvements
- Technology and process optimization
- Market expansion and cross-selling opportunities

TECHNICAL FEATURES:
- Integration project management tools
- Performance dashboard and reporting
- Communication and collaboration platforms
- Document management and knowledge sharing
- Mobile accessibility for field teams

FILES TO CREATE/UPDATE:
- backend/app/models/integration.py
- backend/app/services/integration_management.py
- backend/app/api/integration.py
- backend/app/utils/synergy_tracking.py
- frontend/src/components/IntegrationDashboard.tsx
- frontend/src/components/SynergyTracker.tsx
- frontend/src/components/ChangeManagement.tsx

Build with comprehensive project management capabilities, real-time collaboration tools, and detailed performance tracking.
```

---

## 🎯 PROMPT 6: M&A Team & Workflow Management

```
Develop an M&A Team & Workflow Management system that coordinates complex deal teams, manages workflows, and ensures efficient collaboration across all stakeholders.

BUSINESS CONTEXT:
- Teams: Internal deal teams, external advisors, service providers
- Workflows: Deal origination through post-closing integration
- Scope: Multi-tenant team management with role-based access
- Integration: All M&A platform modules and external systems

TEAM MANAGEMENT:
1. Team Formation & Organization
   - Deal team creation and member assignment
   - Role definition and responsibility mapping
   - Skill assessment and team optimization
   - External advisor and service provider integration
   - Escalation hierarchy and decision authority

2. Workflow Orchestration
   - Deal stage progression and gate management
   - Task assignment and dependency tracking
   - Approval workflows and decision points
   - Quality control and review processes
   - Timeline management and milestone tracking

3. Communication & Collaboration
   - Team communication channels and messaging
   - Meeting scheduling and agenda management
   - Document sharing and collaboration
   - Decision logging and audit trails
   - Status reporting and updates

4. Resource Management
   - Team capacity planning and allocation
   - Budget tracking and expense management
   - Vendor coordination and management
   - Travel and logistics coordination
   - Resource optimization and efficiency

WORKFLOW AUTOMATION:
- Automated task creation and assignment
- Notification and reminder systems
- Approval workflow automation
- Document routing and review processes
- Status update and reporting automation

PERFORMANCE MANAGEMENT:
- Team performance tracking and analytics
- Individual contribution measurement
- Efficiency metrics and optimization
- Quality assessment and improvement
- Knowledge capture and sharing

TECHNICAL ARCHITECTURE:
- Multi-tenant team management system
- Real-time collaboration and communication
- Mobile accessibility and offline capabilities
- Integration with external collaboration tools
- Comprehensive audit and compliance logging

FILES TO CREATE/UPDATE:
- backend/app/models/teams.py
- backend/app/services/workflow_management.py
- backend/app/api/teams.py
- backend/app/utils/collaboration_tools.py
- frontend/src/components/TeamDashboard.tsx
- frontend/src/components/WorkflowManager.tsx
- frontend/src/components/CollaborationHub.tsx

Implement with scalable team management, efficient workflow automation, and comprehensive performance tracking.
```

---

## 🎲 PROMPT 7: M&A Arbitrage & Investment Strategy Engine

```
Build an M&A Arbitrage & Investment Strategy Engine that identifies arbitrage opportunities, analyzes investment strategies, and optimizes portfolio allocation for M&A investments.

BUSINESS CONTEXT:
- Strategy: Systematic M&A arbitrage and investment approach
- Users: Investment professionals and portfolio managers
- Scope: Public and private M&A arbitrage opportunities
- Integration: Market data, deal tracking, and portfolio management

ARBITRAGE MODULES:
1. Deal Arbitrage Opportunity Scanner
   - Announced deal monitoring and analysis
   - Spread analysis and risk assessment
   - Probability of completion modeling
   - Timeline analysis and expected returns
   - Regulatory approval tracking

2. Investment Strategy Optimization
   - Portfolio allocation optimization
   - Risk-adjusted return analysis
   - Correlation analysis and diversification
   - Sector and geographic allocation
   - Capital deployment strategies

3. Risk Management & Hedging
   - Deal break risk assessment
   - Regulatory risk analysis
   - Market risk hedging strategies
   - Liquidity risk management
   - Concentration risk monitoring

4. Performance Analytics
   - Portfolio performance tracking
   - Attribution analysis by strategy
   - Risk-adjusted return measurement
   - Benchmark comparison and analysis
   - Performance optimization recommendations

MARKET INTELLIGENCE:
- Real-time deal announcement monitoring
- Regulatory filing analysis
- Market sentiment tracking
- Insider trading analysis
- Institutional investor positioning

TECHNICAL IMPLEMENTATION:
- Real-time market data integration
- Advanced analytics and modeling
- Portfolio optimization algorithms
- Risk management systems
- Performance reporting and analytics

FILES TO CREATE/UPDATE:
- backend/app/models/arbitrage.py
- backend/app/services/investment_strategy.py
- backend/app/api/arbitrage.py
- backend/app/utils/portfolio_optimization.py
- frontend/src/components/ArbitrageDashboard.tsx
- frontend/src/components/PortfolioManager.tsx
- frontend/src/components/RiskAnalytics.tsx

Build with sophisticated financial modeling, real-time market integration, and comprehensive risk management capabilities.
```

---

## 🚀 Implementation Priority & Integration

### Development Sequence

1. **Deal Discovery & Sourcing** - Foundation for opportunity identification
2. **Financial Modeling & Valuation** - Core analytical capabilities
3. **Due Diligence Management** - Process orchestration
4. **Deal Negotiation & Structuring** - Transaction execution
5. **Post-Acquisition Integration** - Value realization
6. **Team & Workflow Management** - Operational efficiency
7. **Arbitrage & Investment Strategy** - Advanced portfolio management

### Integration Architecture

Each module integrates seamlessly with the existing multi-tenant SaaS platform, sharing data and insights to create a comprehensive M&A management ecosystem. The modular design allows for independent development and deployment while maintaining system coherence.

### Quality Assurance

All modules include comprehensive error handling, security measures, audit trails, and performance optimization. The BMAD methodology ensures structured development with proper testing and documentation throughout the implementation process.
