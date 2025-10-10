# BMAD Method Implementation Guide for Cursor IDE

**Project**: 100 Days and Beyond M&A SaaS Platform  
**Framework**: BMAD Method v4.x  
**IDE**: Cursor with Claude Integration  
**Date**: October 9, 2025  

## Overview

This guide provides step-by-step instructions for implementing the BMAD Method in Cursor IDE for the "100 Days and Beyond" M&A SaaS platform. The BMAD Method provides a structured approach to AI-driven development through specialized agents that collaborate to deliver high-quality software solutions.

## Prerequisites

### Required Software
- **Cursor IDE**: Latest version with Claude integration
- **Node.js**: Version 20 or higher
- **Git**: For version control and BMAD installation
- **Claude API Access**: Anthropic Claude API key or Cursor Pro subscription

### Project Setup
- Existing M&A SaaS platform codebase
- PostgreSQL database (local or cloud)
- Environment variables configured
- Git repository initialized

## Step 1: Install BMAD Method

### 1.1 Navigate to Project Directory
```bash
cd /path/to/ma-saas-platform
```

### 1.2 Install BMAD Method
```bash
npx bmad-method install
```

### 1.3 Configuration Options
When prompted, select the following options:
- **Directory**: Current directory (.)
- **Core Package**: BMAD Core (default)
- **Shard PRD**: Yes (recommended)
- **Shard Architecture**: Yes (recommended)
- **IDE Selection**: Select Cursor (use spacebar to select)
- **Web Bundles**: No (not needed for IDE usage)

### 1.4 Verify Installation
After installation, you should see:
```
├── bmad/
│   ├── agents/           # BMAD agent configurations
│   ├── commands/         # Custom commands for Cursor
│   └── core/            # Core BMAD system files
├── docs/                # Project documentation
│   ├── prd.md          # Product Requirements Document
│   ├── architecture.md  # System Architecture
│   └── project-brief.md # Project Brief
```

## Step 2: Configure Cursor for BMAD

### 2.1 Open Project in Cursor
```bash
cursor .
```

### 2.2 Verify BMAD Commands
In Cursor, open the command palette (Cmd/Ctrl + Shift + P) and verify BMAD commands are available:
- `/analyst` - Business Analyst agent
- `/pm` - Product Manager agent
- `/architect` - System Architect agent
- `/sm` - Scrum Master agent
- `/dev` - Developer agent
- `/qa` - Quality Assurance agent

### 2.3 Configure Claude Integration
Ensure Claude is properly configured in Cursor:
1. Open Cursor settings
2. Navigate to AI/Claude settings
3. Verify API key or subscription is active
4. Set preferred model (Claude 3.5 Sonnet recommended)

## Step 3: BMAD Workflow Implementation

### 3.1 Phase 1: Document Preparation

#### Analyst Agent Usage
Start with the Business Analyst to refine project understanding:

```
/analyst

*help
```

Available analyst commands:
- `*brainstorm` - Brainstorm project ideas and features
- `*research` - Market research and competitive analysis
- `*brief` - Create or refine project brief
- `*competitor` - Analyze competitors

Example usage:
```
/analyst

*brief

I need to create a comprehensive project brief for our M&A SaaS platform "100 Days and Beyond". We have an existing platform with the following features:
- Multi-tenant architecture
- Deal pipeline management
- Document management
- Team collaboration
- Podcast platform
- Subscription management via Clerk

Our goal is £200 million valuation through bootstrap growth.
```

#### Product Manager Agent Usage
Use the PM agent to create or refine the PRD:

```
/pm

*help
```

Available PM commands:
- `*prd` - Create or update Product Requirements Document
- `*features` - Define feature requirements
- `*stories` - Create user stories
- `*acceptance` - Define acceptance criteria

Example usage:
```
/pm

*prd

Based on our project brief, create a comprehensive PRD for our M&A SaaS platform. Focus on:
1. Current feature set optimization
2. Growth features for scaling to £200M valuation
3. Competitive differentiation
4. Technical requirements for multi-tenant architecture
```

#### Architect Agent Usage
Use the Architect agent to create or refine system architecture:

```
/architect

*help
```

Available architect commands:
- `*architecture` - Create system architecture document
- `*design` - Design system components
- `*tech-stack` - Define technology stack
- `*scalability` - Plan scalability approach

Example usage:
```
/architect

*architecture

Create a comprehensive architecture document for our M&A SaaS platform with:
- Multi-tenant PostgreSQL database design
- FastAPI backend architecture
- React frontend architecture
- Clerk authentication integration
- Self-hosted podcast system
- Scalability plan for 10,000+ users
```

### 3.2 Phase 2: Document Sharding

#### Shard PRD Document
Use the built-in shard command to break down large documents:

```bash
# In Cursor terminal
shard docs/prd.md
```

This creates:
```
docs/
├── epics/
│   ├── epic-1-user-management.md
│   ├── epic-2-deal-pipeline.md
│   ├── epic-3-document-management.md
│   └── ...
└── stories/
    ├── story-1-1-user-registration.md
    ├── story-1-2-team-invitations.md
    └── ...
```

#### Shard Architecture Document
```bash
shard docs/architecture.md
```

This creates:
```
docs/
├── architecture/
│   ├── coding-standards.md
│   ├── tech-stack.md
│   ├── source-tree.md
│   └── ...
```

### 3.3 Phase 3: Development Cycle

#### Scrum Master Agent Usage
Use the SM agent to create detailed development stories:

```
/sm

*help
```

Available SM commands:
- `*draft` - Draft next development story
- `*plan` - Plan sprint activities
- `*review` - Review story completion
- `*correct` - Correct course for project changes

Example usage:
```
/sm

*draft 1.1

Create a detailed development story for Epic 1, Story 1 (User Registration). Include:
- Detailed acceptance criteria
- Technical implementation tasks
- Architecture context from our sharded documents
- Testing requirements
```

#### Developer Agent Usage
Use the Developer agent to implement features:

```
/dev

*help
```

Available developer commands:
- `*develop` - Develop a specific story
- `*implement` - Implement feature or component
- `*refactor` - Refactor existing code
- `*optimize` - Optimize performance

Example usage:
```
/dev

*develop story-1-1-user-registration.md

Implement the user registration story following our FastAPI backend architecture and React frontend design. Ensure:
- Clerk integration for authentication
- Multi-tenant organization setup
- Proper error handling and validation
- TypeScript type safety
```

#### Quality Assurance Agent Usage
Use the QA agent to review and test implementations:

```
/qa

*help
```

Available QA commands:
- `*review` - Review story implementation
- `*test` - Create test cases
- `*audit` - Audit code quality
- `*compliance` - Check compliance requirements

Example usage:
```
/qa

*review story-1-1-user-registration.md

Review the implementation of user registration story. Check:
- Code quality and standards compliance
- Security best practices
- Test coverage
- Performance considerations
- Multi-tenant data isolation
```

## Step 4: Advanced BMAD Usage

### 4.1 Context Management
BMAD agents automatically load relevant context from sharded documents. To optimize context:

1. **Keep documents focused**: Each epic and story should be self-contained
2. **Update regularly**: Keep documents current as implementation progresses
3. **Use clear naming**: Follow BMAD naming conventions for automatic loading

### 4.2 Custom Agent Configuration
Customize agents for your specific needs by editing files in `bmad/agents/`:

```javascript
// Example: Customize developer agent for FastAPI/React stack
{
  "name": "Developer",
  "role": "Full-stack developer specializing in FastAPI and React",
  "context": [
    "docs/architecture/tech-stack.md",
    "docs/architecture/coding-standards.md"
  ],
  "instructions": "Focus on TypeScript, FastAPI best practices, and multi-tenant architecture"
}
```

### 4.3 Workflow Optimization

#### Best Practices
1. **Start new chat sessions**: Begin fresh chat for each major task
2. **Use specific commands**: Leverage BMAD commands rather than generic requests
3. **Provide context**: Reference specific documents and requirements
4. **Iterate incrementally**: Work on one story at a time
5. **Review regularly**: Use QA agent to maintain quality

#### Common Patterns
```
# Epic Planning
/sm -> *plan -> Review epic breakdown

# Story Development
/sm -> *draft -> /dev -> *develop -> /qa -> *review

# Feature Enhancement
/architect -> *design -> /dev -> *implement -> /qa -> *audit

# Bug Fixes
/qa -> *audit -> /dev -> *refactor -> /qa -> *review
```

## Step 5: Integration with Existing Codebase

### 5.1 Brownfield Integration
Since we have an existing codebase, use BMAD's brownfield approach:

1. **Document current state**: Use analyst to document existing features
2. **Create architecture docs**: Use architect to document current architecture
3. **Plan enhancements**: Use PM to plan new features and improvements
4. **Incremental development**: Use SM/Dev/QA cycle for new features

### 5.2 Maintaining Existing Code
When working with existing code:

```
/dev

*refactor

Refactor the existing deal management API to improve:
- Performance optimization
- Code organization
- Type safety
- Error handling
- Multi-tenant security

Current code is in backend/app/api/deals.py
```

### 5.3 Database Migrations
For database changes:

```
/architect

*design

Design database migration for new podcast analytics features:
- Episode download tracking
- User engagement metrics
- Performance analytics
- Ensure multi-tenant isolation
```

## Step 6: Monitoring and Optimization

### 6.1 Performance Monitoring
Use BMAD agents to optimize performance:

```
/dev

*optimize

Analyze and optimize the following performance bottlenecks:
- API response times >200ms
- Database query optimization
- Frontend bundle size
- Memory usage patterns
```

### 6.2 Security Auditing
Regular security reviews:

```
/qa

*compliance

Perform security audit focusing on:
- Multi-tenant data isolation
- Authentication and authorization
- Input validation and sanitization
- GDPR compliance requirements
```

### 6.3 Code Quality Maintenance
Maintain code quality:

```
/qa

*audit

Review codebase for:
- TypeScript type coverage
- Test coverage gaps
- Code duplication
- Architecture compliance
- Documentation completeness
```

## Step 7: Troubleshooting

### Common Issues and Solutions

#### BMAD Commands Not Available
**Problem**: BMAD commands don't appear in Cursor
**Solution**: 
1. Verify installation: `ls bmad/`
2. Restart Cursor IDE
3. Check Cursor extensions are enabled

#### Agent Context Issues
**Problem**: Agents don't have proper context
**Solution**:
1. Ensure documents are sharded properly
2. Check file paths in agent configurations
3. Update document references after file moves

#### Performance Issues
**Problem**: Slow agent responses
**Solution**:
1. Reduce context size by sharding large documents
2. Use specific commands rather than general requests
3. Start fresh chat sessions for complex tasks

### Getting Help

#### BMAD Community Resources
- **Discord**: Join BMAD community for support
- **GitHub**: Check issues and discussions
- **Documentation**: Review official BMAD docs

#### Project-Specific Support
- **Team Communication**: Use established team channels
- **Code Reviews**: Regular peer reviews of BMAD-generated code
- **Documentation**: Maintain project-specific BMAD usage patterns

## Conclusion

The BMAD Method integration with Cursor IDE provides a powerful framework for AI-driven development of the M&A SaaS platform. By following this implementation guide, development teams can leverage specialized AI agents to maintain high code quality, accelerate development velocity, and ensure architectural consistency.

The structured approach of BMAD agents (Analyst → PM → Architect → SM → Developer → QA) provides a comprehensive workflow that supports both greenfield development and brownfield enhancement of existing codebases.

Regular use of BMAD agents throughout the development lifecycle will help achieve the £200 million valuation goal by maintaining development velocity, code quality, and architectural integrity as the platform scales to serve thousands of customers.

## Next Steps

1. **Install BMAD Method** in your project directory
2. **Configure Cursor** with proper Claude integration
3. **Start with Analyst** to document current platform state
4. **Create comprehensive PRD** using PM agent
5. **Document architecture** using Architect agent
6. **Begin development cycle** with SM/Dev/QA workflow
7. **Iterate and improve** based on agent feedback and results

This implementation guide provides the foundation for successful BMAD Method adoption in your M&A SaaS platform development workflow.
