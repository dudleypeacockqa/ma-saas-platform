# Phase 2 Continuation Prompts - BMAD Methodology

## Project Context

**Project**: M&A SaaS Platform - 100 Days and Beyond**User**: Dudley**Goal**: £200M wealth-building through M&A platform**Current Status**: Phase 1 Complete - Infrastructure Operational**Next Phase**: Core Business Features Development

## Phase 2 Objectives

Phase 2 focuses on developing the core business features that will enable revenue generation and customer acquisition. The technical foundation from Phase 1 provides a solid base for rapid feature development and deployment.

## Required BMAD Continuation Prompts

### 1. Product Brief Creation

**Prompt**:

```
I need to continue building my M&A SaaS platform using BMAD methodology. Phase 1 infrastructure is complete and operational at https://100daysandbeyond.com with backend at https://ma-saas-backend.onrender.com.

Please activate the BMAD Master agent and execute the product-brief workflow to define the core business features for Phase 2. The platform needs to support M&A professionals with deal management, pipeline tracking, team collaboration, and analytics.

Context: Multi-tenant SaaS platform with Clerk authentication, PostgreSQL database (125 tables), React frontend, FastAPI backend. Target: £200M wealth-building through subscription revenue model.
```

### 2. Product Requirements Document (PRD)

**Prompt**:

```
Using BMAD methodology, execute the PRD workflow for my M&A SaaS platform Phase 2. The product brief is complete, now I need detailed product requirements for core business features.

Focus areas:
- Deal pipeline management and tracking
- Document management and collaboration
- Team workspace and permissions
- Analytics and reporting dashboard
- Integration capabilities (CRM, email, etc.)

The platform is Level 3 complexity (enterprise SaaS) and needs comprehensive PRD with epics for development team handoff.
```

### 3. UX/UI Specification

**Prompt**:

```
Execute the BMAD ux-spec workflow for my M&A SaaS platform. I need comprehensive UX/UI specifications for the core business features defined in the PRD.

Key user personas:
- M&A Advisors (primary users)
- Deal Team Members (collaborators)
- Firm Partners (executives/oversight)

Focus on intuitive deal management workflows, collaborative document review, and executive-level analytics dashboards. The platform should feel professional and efficient for high-stakes M&A transactions.
```

### 4. Solution Architecture for Business Features

**Prompt**:

```
Using BMAD methodology, execute the solution-architecture workflow for Phase 2 business features. The infrastructure architecture is complete, now I need the business logic and feature architecture.

Technical context:
- Existing: React frontend, FastAPI backend, PostgreSQL database
- Authentication: Clerk (multi-tenant)
- Hosting: Render.com with Cloudflare CDN
- Database: 125 tables with multi-tenant schema

New requirements: Real-time collaboration, file management, advanced analytics, third-party integrations, notification system.
```

### 5. Technical Specifications

**Prompt**:

```
Execute the BMAD tech-spec workflow to create detailed technical specifications for Phase 2 core features. The PRD and solution architecture are complete.

Generate comprehensive technical specs with:
- API endpoint specifications
- Database schema updates
- Frontend component architecture
- Integration specifications
- Security and performance requirements
- Acceptance criteria for each feature

Focus on maintainable, scalable code that supports rapid feature iteration and customer feedback incorporation.
```

### 6. Story Creation and Development

**Prompt**:

```
Using BMAD create-story workflow, generate user stories for Phase 2 core features implementation. Break down the technical specifications into manageable development stories.

Prioritize stories for:
1. Deal creation and management (MVP)
2. Basic pipeline visualization
3. Document upload and organization
4. Team collaboration features
5. Analytics foundation

Each story should be sized for 1-3 day implementation cycles to maintain rapid development velocity.
```

### 7. Development Execution

**Prompt**:

```
Execute BMAD dev-story workflow for [specific story name]. Implement the story following the technical specifications and acceptance criteria.

Context: M&A SaaS platform with existing codebase at ma-saas-platform/. Frontend in React/Vite, backend in FastAPI, database PostgreSQL. Follow established patterns and maintain code quality.

After implementation, update story status and prepare for review workflow.
```

## Phase 2 Success Criteria

### Business Metrics

- **Revenue Generation**: First paying customers within 30 days

- **User Engagement**: Daily active users on core features

- **Deal Velocity**: Measurable improvement in user deal closure rates

- **Customer Satisfaction**: Positive feedback on core workflows

### Technical Metrics

- **Feature Completion**: All Phase 2 core features operational

- **Performance**: Maintain <2s load times with new features

- **Reliability**: 99.9% uptime for business-critical features

- **Scalability**: Support for 100+ concurrent users

## Development Workflow

### Sprint Structure

1. **Week 1**: Product brief and PRD completion

1. **Week 2**: UX specifications and solution architecture

1. **Week 3**: Technical specifications and story creation

1. **Week 4-6**: Core feature development (3x 2-week sprints)

1. **Week 7**: Integration testing and deployment

1. **Week 8**: User testing and feedback incorporation

### Quality Gates

- **Code Review**: All code reviewed using BMAD review-story workflow

- **Testing**: Automated tests for all business logic

- **Performance**: Load testing for concurrent user scenarios

- **Security**: Security review for multi-tenant data isolation

## Integration Points

### Existing Systems

- **Clerk Authentication**: Extend user management for business features

- **PostgreSQL Database**: Utilize existing multi-tenant schema

- **Render Deployment**: Maintain existing CI/CD pipeline

- **Cloudflare CDN**: Optimize for new feature assets

### New Integrations (Phase 2)

- **File Storage**: AWS S3 or similar for document management

- **Email Service**: Transactional emails for notifications

- **Analytics**: Advanced reporting and dashboard features

- **Third-party APIs**: CRM integration capabilities

## Risk Mitigation

### Technical Risks

- **Database Performance**: Monitor query performance with new features

- **File Storage**: Implement efficient document management

- **Real-time Features**: Ensure WebSocket stability for collaboration

- **Third-party Dependencies**: Maintain service reliability

### Business Risks

- **User Adoption**: Continuous user feedback and iteration

- **Market Fit**: Validate features with target M&A professionals

- **Competition**: Maintain feature development velocity

- **Revenue Model**: Optimize pricing and subscription tiers

## Next Steps

1. **Immediate**: Execute product-brief workflow using first prompt

1. **Week 1**: Complete PRD using second prompt

1. **Week 2**: Develop UX specifications using third prompt

1. **Week 3**: Create solution architecture using fourth prompt

1. **Week 4**: Generate technical specifications using fifth prompt

1. **Week 5+**: Begin story-driven development using remaining prompts

This structured approach ensures systematic progression through Phase 2 while maintaining the quality and methodology that made Phase 1 successful. Each prompt builds upon the previous work and maintains alignment with the £200M wealth-building business objective.
