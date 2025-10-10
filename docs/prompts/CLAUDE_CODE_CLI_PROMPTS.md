# Claude Code CLI Prompts for Phase 1 Completion

**Platform**: "100 Days and Beyond" M&A Ecosystem  
**Integration Target**: Advanced AI capabilities and complex business logic  
**Tool**: Claude Code CLI in Cursor IDE  
**Objective**: Complete Phase 1 with sophisticated AI-powered features  

## Executive Summary: Claude Code CLI Integration Strategy

These prompts are designed for use with Claude Code CLI in Cursor IDE to implement the most sophisticated aspects of the M&A platform. Each prompt is optimized for Claude's M&A domain expertise and advanced reasoning capabilities.

**Usage Instructions**:
1. Open Cursor IDE with the M&A SaaS platform project
2. Activate Claude Code CLI integration
3. Use these prompts in sequence for optimal results
4. Each prompt builds upon previous implementations

## 🤖 PROMPT 1: Claude MCP Server Integration

```
@claude I need you to implement comprehensive Claude MCP server integration for our M&A ecosystem platform. This is a multi-tenant SaaS application focused on wealth building through strategic acquisitions.

CONTEXT:
- Platform: "100 Days and Beyond" M&A Ecosystem
- Backend: FastAPI with PostgreSQL vector database
- Frontend: React with TypeScript
- Goal: £200 million wealth building through ecosystem intelligence

REQUIREMENTS:
1. Set up Claude MCP server with advanced M&A business logic
2. Implement vector database integration with semantic search capabilities
3. Create AI-powered deal analysis with predictive modeling
4. Add partnership identification with compatibility scoring
5. Configure ecosystem intelligence for wealth-building optimization

TECHNICAL SPECIFICATIONS:
- Use Anthropic API with Claude 3.5 Sonnet model
- Integrate with existing PostgreSQL vector database (pgvector)
- Implement embedding generation for semantic search
- Create real-time AI processing with caching optimization
- Add comprehensive error handling and fallback mechanisms

BUSINESS LOGIC REQUIREMENTS:
- Deal sourcing automation with market intelligence
- Due diligence automation with risk assessment
- Partnership compatibility analysis with influence mapping
- Wealth-building optimization through ecosystem insights
- Strategic recommendations with confidence scoring

Please implement this with production-ready code, comprehensive error handling, and detailed documentation. Focus on M&A domain expertise and sophisticated business intelligence capabilities.
```

## 🔍 PROMPT 2: Advanced Vector Database Implementation

```
@claude Implement a sophisticated vector database system for our M&A platform that enables ecosystem intelligence and partnership identification.

CONTEXT:
- Existing PostgreSQL database with pgvector extension
- Need semantic search across deals, opportunities, and community content
- Goal: Identify partnership opportunities and optimize deal flow
- Multi-tenant architecture with organization-based isolation

REQUIREMENTS:
1. Install and configure pgvector extensions with optimal settings
2. Implement embedding generation using OpenAI text-embedding-3-small
3. Create semantic search capabilities across all content types
4. Set up relationship mapping with influence assessment
5. Add predictive modeling for partnership compatibility

TECHNICAL IMPLEMENTATION:
- Vector dimension: 1536 (matching OpenAI embeddings)
- Index type: IVFFlat with 100 lists for optimal performance
- Similarity threshold: 0.8 for high-quality matches
- Batch processing for efficient embedding generation
- Real-time search with sub-second response times

BUSINESS INTELLIGENCE FEATURES:
- Opportunity scoring based on compatibility analysis
- Partnership identification through semantic similarity
- Market trend analysis through content clustering
- Competitive intelligence through relationship mapping
- Wealth-building optimization through ecosystem insights

SPECIFIC IMPLEMENTATIONS NEEDED:
1. Embedding generation service with batch processing
2. Semantic search API endpoints with filtering
3. Partnership matching algorithm with scoring
4. Relationship mapping with influence assessment
5. Predictive analytics with success probability modeling

Please create production-ready code with comprehensive testing, monitoring, and documentation. Focus on performance optimization and business value generation.
```

## 💳 PROMPT 3: Sophisticated Stripe Payment Integration

```
@claude Implement advanced Stripe payment integration for our M&A platform with comprehensive subscription management and international support.

CONTEXT:
- Multi-tenant M&A SaaS platform with three pricing tiers
- Pricing: Solo ($279), Growth ($798), Enterprise ($1,598)
- Need automated billing, dunning management, and revenue optimization
- Integration with Clerk authentication and organization management

REQUIREMENTS:
1. Create subscription plans with annual discount options (10% off)
2. Implement webhook endpoints with comprehensive event handling
3. Set up automated billing with intelligent dunning management
4. Add international payment processing with multi-currency support
5. Configure revenue analytics with optimization insights

SUBSCRIPTION TIERS:
- Solo Dealmaker: $279/month, $251/month annual (10% discount)
- Growth Firm: $798/month, $718/month annual (10% discount)  
- Enterprise: $1,598/month, $1,438/month annual (10% discount)

ADVANCED FEATURES NEEDED:
1. Proration handling for plan changes
2. Failed payment recovery with smart retry logic
3. Usage-based billing for overage charges
4. Team member management with seat-based pricing
5. Revenue recognition with financial reporting

WEBHOOK EVENTS TO HANDLE:
- customer.subscription.created
- customer.subscription.updated
- customer.subscription.deleted
- invoice.payment_succeeded
- invoice.payment_failed
- customer.subscription.trial_will_end

BUSINESS LOGIC:
- Automatic feature access control based on subscription tier
- Usage tracking and limit enforcement
- Churn prediction and retention optimization
- Revenue analytics with cohort analysis
- Customer lifetime value optimization

Please implement with production-grade security, comprehensive error handling, and detailed logging. Focus on revenue optimization and customer experience excellence.
```

## 🧠 PROMPT 4: AI-Powered M&A Business Logic

```
@claude Develop sophisticated AI-powered business logic for our M&A platform that leverages your expertise in mergers and acquisitions to create intelligent automation and insights.

CONTEXT:
- Platform owner is building personal wealth toward £200 million target
- Platform serves both personal deal flow and SaaS business development
- Multi-tenant architecture with ecosystem intelligence capabilities
- Integration with Claude MCP server and vector database

CORE AI CAPABILITIES NEEDED:
1. Intelligent Deal Sourcing with Market Analysis
2. Automated Due Diligence with Risk Assessment
3. Strategic Partnership Identification with Compatibility Scoring
4. Wealth-Building Optimization through Ecosystem Intelligence
5. Automated Insights with Strategic Recommendations

DEAL SOURCING INTELLIGENCE:
- Market opportunity identification through trend analysis
- Company valuation estimation with multiple methodologies
- Industry analysis with competitive positioning
- Growth potential assessment with predictive modeling
- Risk evaluation with mitigation strategies

DUE DILIGENCE AUTOMATION:
- Financial analysis with red flag detection
- Legal risk assessment with compliance checking
- Operational efficiency evaluation with improvement recommendations
- Market position analysis with competitive advantages
- Integration complexity assessment with success probability

PARTNERSHIP IDENTIFICATION:
- Compatibility scoring based on strategic alignment
- Influence mapping with relationship strength assessment
- Collaboration opportunity identification with value estimation
- Network effect analysis with ecosystem benefits
- Partnership success prediction with confidence intervals

WEALTH-BUILDING OPTIMIZATION:
- Portfolio optimization with risk-adjusted returns
- Deal flow prioritization with ROI maximization
- Strategic timing recommendations with market conditions
- Exit strategy optimization with value maximization
- Ecosystem leverage with network effect amplification

IMPLEMENTATION REQUIREMENTS:
- Real-time processing with sub-second response times
- Confidence scoring for all AI-generated insights
- Explainable AI with reasoning transparency
- Continuous learning with feedback incorporation
- Multi-tenant isolation with organization-specific optimization

Please create production-ready AI services with comprehensive testing, monitoring, and documentation. Focus on generating actionable insights that directly contribute to wealth building and business success.
```

## 🎯 PROMPT 5: Advanced Analytics and Business Intelligence

```
@claude Implement comprehensive analytics and business intelligence system for our M&A platform that provides actionable insights for wealth building and business optimization.

CONTEXT:
- Multi-tenant M&A platform with ecosystem intelligence
- Need real-time analytics for business optimization
- Goal: Support £200 million wealth-building objective
- Integration with existing vector database and AI capabilities

ANALYTICS REQUIREMENTS:
1. Real-time dashboard with key performance indicators
2. Predictive analytics with success probability modeling
3. Cohort analysis with customer lifetime value optimization
4. Ecosystem intelligence with partnership opportunity identification
5. Revenue optimization with pricing strategy recommendations

KEY METRICS TO TRACK:
- Deal flow velocity and conversion rates
- Partnership identification and success rates
- User engagement and feature utilization
- Revenue growth and churn prediction
- Ecosystem network effects and value creation

BUSINESS INTELLIGENCE FEATURES:
- Market trend analysis with competitive positioning
- Customer segmentation with personalization opportunities
- Feature usage analytics with optimization recommendations
- Revenue attribution with channel effectiveness
- Predictive modeling with confidence intervals

DASHBOARD COMPONENTS:
1. Executive Summary with key metrics
2. Deal Pipeline with probability-weighted values
3. Partnership Opportunities with compatibility scores
4. Revenue Analytics with growth projections
5. Ecosystem Intelligence with network insights

ADVANCED ANALYTICS:
- Machine learning models for churn prediction
- Recommendation engines for deal matching
- Anomaly detection for risk identification
- Sentiment analysis for market intelligence
- Network analysis for relationship mapping

Please implement with real-time data processing, interactive visualizations, and actionable insights. Focus on supporting strategic decision-making and wealth-building optimization.
```

## 🔧 PROMPT 6: Production Deployment and Monitoring

```
@claude Set up comprehensive production deployment and monitoring for our M&A platform with enterprise-grade reliability and performance.

CONTEXT:
- Render hosting with PostgreSQL vector database
- FastAPI backend with React frontend
- Multi-tenant architecture with high availability requirements
- Need comprehensive monitoring and alerting

DEPLOYMENT REQUIREMENTS:
1. Optimize Render deployment configuration for production
2. Set up comprehensive monitoring with alerting
3. Implement error tracking with detailed logging
4. Configure performance monitoring with optimization
5. Set up security monitoring with threat detection

MONITORING STACK:
- Application performance monitoring (APM)
- Database performance monitoring
- Infrastructure monitoring with alerts
- Security monitoring with threat detection
- Business metrics monitoring with insights

ALERTING CONFIGURATION:
- Critical: System downtime, security breaches
- High: Performance degradation, error rate spikes
- Medium: Resource utilization, slow queries
- Low: Feature usage anomalies, business metrics

PERFORMANCE OPTIMIZATION:
- Database query optimization with indexing
- API response time optimization with caching
- Frontend performance with lazy loading
- CDN configuration for static assets
- Auto-scaling configuration for traffic spikes

SECURITY MONITORING:
- Authentication failure detection
- Suspicious activity monitoring
- Data access auditing
- Compliance monitoring (GDPR, SOC2)
- Vulnerability scanning and patching

Please implement with production-grade reliability, comprehensive documentation, and operational excellence. Focus on maintaining 99.9% uptime and optimal performance.
```

## 📋 BMAD Method Agent Initiation Prompts

### BMAD Analyst Agent Initiation

```
BMAD Analyst Agent - Phase 1 Strategic Validation

You are the BMAD Analyst Agent responsible for market intelligence and strategic validation for the "100 Days and Beyond" M&A ecosystem platform.

MISSION: Validate current implementation against market requirements and competitive positioning for optimal wealth-building potential.

ANALYSIS REQUIREMENTS:
1. Market Position Assessment
   - Competitive analysis vs. dealmakers.co.uk and similar platforms
   - Technology advantage evaluation with AI capabilities
   - Pricing strategy validation with market positioning
   - Value proposition differentiation with unique selling points

2. User Experience Optimization
   - Conversion funnel analysis with optimization opportunities
   - User journey mapping with friction point identification
   - Feature prioritization with business impact assessment
   - Retention strategy with engagement optimization

3. Business Model Validation
   - Revenue stream optimization with growth potential
   - Customer acquisition cost with lifetime value analysis
   - Market size assessment with growth projections
   - Competitive moat evaluation with sustainability factors

4. Wealth-Building Potential Assessment
   - Ecosystem intelligence value with partnership opportunities
   - Deal flow generation with quality assessment
   - Network effect potential with value amplification
   - Strategic positioning with market leadership potential

5. Risk Assessment and Mitigation
   - Market risks with mitigation strategies
   - Technology risks with contingency planning
   - Competitive risks with defensive strategies
   - Operational risks with process optimization

DELIVERABLES:
- Comprehensive market analysis report
- Competitive positioning strategy
- User experience optimization recommendations
- Business model validation with growth projections
- Risk assessment with mitigation strategies

Please provide detailed analysis with actionable recommendations for achieving the £200 million wealth-building objective.
```

### BMAD Product Manager Agent Initiation

```
BMAD Product Manager Agent - Phase 1 Feature Optimization

You are the BMAD Product Manager Agent responsible for feature prioritization and user experience optimization for the M&A ecosystem platform.

MISSION: Ensure optimal feature implementation and user journey for maximum conversion and retention.

PRODUCT REQUIREMENTS:
1. User Onboarding Optimization
   - Conversion funnel analysis with A/B testing recommendations
   - Onboarding flow optimization with friction reduction
   - Trial-to-paid conversion with value demonstration
   - User activation with feature adoption strategies

2. Feature Prioritization Matrix
   - Business impact assessment with ROI calculation
   - User value evaluation with satisfaction metrics
   - Development effort estimation with resource allocation
   - Strategic alignment with wealth-building objectives

3. Subscription Tier Optimization
   - Value proposition validation with market research
   - Feature distribution with tier differentiation
   - Pricing strategy with elasticity analysis
   - Upgrade path optimization with revenue maximization

4. User Experience Excellence
   - Interface design with usability optimization
   - Performance requirements with speed optimization
   - Mobile responsiveness with cross-device consistency
   - Accessibility compliance with inclusive design

5. Product Roadmap Development
   - Phase 2-4 feature planning with strategic alignment
   - Resource allocation with timeline optimization
   - Stakeholder alignment with communication strategy
   - Success metrics with measurement framework

DELIVERABLES:
- Feature prioritization matrix with business justification
- User experience optimization recommendations
- Subscription tier analysis with pricing strategy
- Product roadmap with strategic alignment
- Success metrics framework with KPI definitions

Please provide detailed product strategy with user-centric approach and business value optimization.
```

## 🚀 Implementation Sequence

### Phase 1A: Immediate Claude Integration (Hours 1-8)
1. **Claude MCP Server Setup**: Use Prompt 1 for advanced AI integration
2. **Vector Database Implementation**: Use Prompt 2 for semantic search
3. **Payment Integration**: Use Prompt 3 for Stripe implementation
4. **AI Business Logic**: Use Prompt 4 for intelligent automation

### Phase 1B: BMAD Agent Coordination (Hours 9-16)
1. **Analyst Agent**: Market validation and competitive analysis
2. **Product Manager Agent**: Feature optimization and user experience
3. **Architect Agent**: System design validation and optimization
4. **Developer Agent**: Code quality and implementation excellence

### Phase 1C: Advanced Features (Hours 17-24)
1. **Analytics Implementation**: Use Prompt 5 for business intelligence
2. **Production Deployment**: Use Prompt 6 for monitoring and reliability
3. **Quality Assurance**: Comprehensive testing and validation
4. **Performance Optimization**: Speed and scalability enhancement

## 📊 Success Metrics

### Technical Metrics
- API response time < 200ms
- Database query performance < 50ms
- Frontend load time < 2 seconds
- 99.9% uptime reliability

### Business Metrics
- Trial-to-paid conversion > 15%
- Monthly churn rate < 5%
- Customer lifetime value > $5,000
- Net Promoter Score > 50

### AI Performance Metrics
- Semantic search accuracy > 90%
- Partnership matching precision > 85%
- Deal scoring confidence > 80%
- Insight generation speed < 1 second

Use these prompts systematically to achieve 100% Phase 1 completion with enterprise-grade quality and sophisticated AI capabilities that directly support the £200 million wealth-building objective.
