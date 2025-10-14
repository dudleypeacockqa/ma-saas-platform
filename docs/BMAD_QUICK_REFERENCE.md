# BMAD Method Quick Reference Guide

**Project**: 100 Days and Beyond M&A SaaS Platform  
**Framework**: BMAD Method v4.x  
**IDE**: Cursor with Claude Integration

## Agent Commands Overview

### Analyst Agent (`/analyst`)

**Purpose**: Business analysis, market research, competitive intelligence, project briefing

| Command       | Description                   | Usage Example                                         |
| ------------- | ----------------------------- | ----------------------------------------------------- |
| `*help`       | Show available commands       | `/analyst` → `*help`                                  |
| `*brainstorm` | Brainstorm ideas and features | `*brainstorm` → Discuss M&A platform enhancements     |
| `*research`   | Market research and analysis  | `*research` → Analyze M&A software market trends      |
| `*brief`      | Create/refine project brief   | `*brief` → Update project brief with new requirements |
| `*competitor` | Competitive analysis          | `*competitor` → Analyze DealRoom vs our platform      |

### Product Manager Agent (`/pm`)

**Purpose**: Product requirements, feature definition, user stories, acceptance criteria

| Command       | Description                 | Usage Example                                     |
| ------------- | --------------------------- | ------------------------------------------------- |
| `*help`       | Show available commands     | `/pm` → `*help`                                   |
| `*prd`        | Create/update PRD           | `*prd` → Refine PRD based on market feedback      |
| `*features`   | Define feature requirements | `*features` → Define AI analytics requirements    |
| `*stories`    | Create user stories         | `*stories` → Create stories for podcast platform  |
| `*acceptance` | Define acceptance criteria  | `*acceptance` → Define criteria for deal pipeline |

### Architect Agent (`/architect`)

**Purpose**: System architecture, technical design, scalability planning, technology decisions

| Command         | Description                  | Usage Example                                      |
| --------------- | ---------------------------- | -------------------------------------------------- |
| `*help`         | Show available commands      | `/architect` → `*help`                             |
| `*architecture` | Create architecture document | `*architecture` → Design multi-tenant architecture |
| `*design`       | Design system components     | `*design` → Design podcast RSS system              |
| `*tech-stack`   | Define technology stack      | `*tech-stack` → Evaluate FastAPI vs Django         |
| `*scalability`  | Plan scalability approach    | `*scalability` → Plan for 10,000+ users            |

### Scrum Master Agent (`/sm`)

**Purpose**: Sprint planning, story creation, project management, workflow coordination

| Command    | Description                | Usage Example                                            |
| ---------- | -------------------------- | -------------------------------------------------------- |
| `*help`    | Show available commands    | `/sm` → `*help`                                          |
| `*draft`   | Draft development story    | `*draft 1.1` → Create detailed story for Epic 1, Story 1 |
| `*plan`    | Plan sprint activities     | `*plan` → Plan next 2-week sprint                        |
| `*review`  | Review story completion    | `*review` → Review completed user registration story     |
| `*correct` | Correct course for changes | `*correct` → Adjust plan for new requirements            |

### Developer Agent (`/dev`)

**Purpose**: Code implementation, feature development, refactoring, optimization

| Command      | Description                 | Usage Example                                         |
| ------------ | --------------------------- | ----------------------------------------------------- |
| `*help`      | Show available commands     | `/dev` → `*help`                                      |
| `*develop`   | Develop specific story      | `*develop story-1-1.md` → Implement user registration |
| `*implement` | Implement feature/component | `*implement` → Build podcast RSS generator            |
| `*refactor`  | Refactor existing code      | `*refactor` → Optimize deal pipeline API              |
| `*optimize`  | Optimize performance        | `*optimize` → Improve database query performance      |

### Quality Assurance Agent (`/qa`)

**Purpose**: Testing, code review, quality validation, compliance checking

| Command       | Description             | Usage Example                                          |
| ------------- | ----------------------- | ------------------------------------------------------ |
| `*help`       | Show available commands | `/qa` → `*help`                                        |
| `*review`     | Review implementation   | `*review story-1-1.md` → Review user registration code |
| `*test`       | Create test cases       | `*test` → Create tests for deal pipeline               |
| `*audit`      | Audit code quality      | `*audit` → Audit security practices                    |
| `*compliance` | Check compliance        | `*compliance` → Verify GDPR compliance                 |

## Common Workflows

### 1. New Feature Development

```
1. /analyst → *research → Market analysis for feature
2. /pm → *features → Define feature requirements
3. /architect → *design → Design technical approach
4. /sm → *draft → Create detailed development story
5. /dev → *develop → Implement the feature
6. /qa → *review → Test and validate implementation
```

### 2. Performance Optimization

```
1. /qa → *audit → Identify performance issues
2. /architect → *scalability → Design optimization approach
3. /dev → *optimize → Implement optimizations
4. /qa → *test → Validate performance improvements
```

### 3. Bug Fix Workflow

```
1. /qa → *audit → Analyze bug and root cause
2. /dev → *refactor → Fix the issue
3. /qa → *review → Validate fix and test regression
```

### 4. Architecture Enhancement

```
1. /analyst → *research → Research new technologies/approaches
2. /architect → *architecture → Design enhanced architecture
3. /sm → *plan → Plan migration/implementation
4. /dev → *implement → Execute architecture changes
5. /qa → *compliance → Validate security and compliance
```

## Document Management

### Sharding Commands

```bash
# Shard PRD into epics and stories
shard docs/prd.md

# Shard architecture into components
shard docs/architecture.md

# Custom sharding with specific output directory
shard docs/large-document.md --output docs/sharded/
```

### Document Structure

```
docs/
├── project-brief.md          # Initial project overview
├── prd.md                   # Product Requirements Document
├── architecture.md          # System Architecture Document
├── epics/                   # Sharded epic documents
│   ├── epic-1-user-mgmt.md
│   ├── epic-2-deals.md
│   └── epic-3-docs.md
├── stories/                 # Development stories
│   ├── story-1-1-registration.md
│   ├── story-1-2-invitations.md
│   └── story-2-1-deal-creation.md
└── architecture/            # Sharded architecture docs
    ├── coding-standards.md
    ├── tech-stack.md
    └── source-tree.md
```

## Best Practices

### Context Management

- **Start fresh chats** for major tasks to avoid context pollution
- **Reference specific documents** when asking agents to work on features
- **Keep documents updated** as implementation progresses
- **Use clear, descriptive filenames** for automatic context loading

### Agent Interaction Tips

- **Be specific** with commands and requirements
- **Provide context** about existing code and architecture
- **Ask for clarification** if agent responses are unclear
- **Iterate incrementally** rather than requesting large changes

### Quality Assurance

- **Always use QA agent** to review implementations
- **Test at multiple levels** (unit, integration, system)
- **Validate security** and compliance requirements
- **Monitor performance** impact of changes

### Development Velocity

- **Follow BMAD workflow** consistently for predictable results
- **Maintain documentation** to support agent context
- **Regular retrospectives** to improve process efficiency
- **Automate repetitive tasks** through agent workflows

## Troubleshooting

### Common Issues

#### Agent Commands Not Working

**Problem**: BMAD commands don't appear in Cursor
**Solution**:

- Verify BMAD installation: `ls bmad/`
- Restart Cursor IDE
- Check agent configurations in `bmad/agents/`

#### Poor Agent Responses

**Problem**: Agents provide generic or incorrect responses
**Solution**:

- Provide more specific context and requirements
- Reference relevant documents and existing code
- Start fresh chat session to clear context
- Verify agent has access to necessary documents

#### Context Overload

**Problem**: Agents seem confused or provide inconsistent responses
**Solution**:

- Shard large documents into smaller, focused files
- Start new chat sessions between major tasks
- Remove outdated or irrelevant documents from context
- Use specific commands rather than general requests

### Getting Help

#### BMAD Community

- **Discord**: Join BMAD community for support and discussions
- **GitHub**: Check issues, discussions, and documentation
- **YouTube**: Watch BMAD tutorial videos and masterclasses

#### Project Support

- **Team Reviews**: Regular code reviews of BMAD-generated code
- **Documentation**: Maintain project-specific BMAD patterns
- **Process Improvement**: Regular retrospectives on BMAD usage

## Environment Variables

### Required Configuration

```bash
# Cursor/Claude Configuration
ANTHROPIC_API_KEY=your_api_key_here
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Project Configuration
DATABASE_URL=postgresql://user:pass@host:port/db
CLERK_SECRET_KEY=your_clerk_secret
CLERK_PUBLISHABLE_KEY=your_clerk_public_key
BASE_URL=https://your-domain.com
```

### BMAD Configuration

```bash
# BMAD Method Configuration
BMAD_PROJECT_ROOT=/path/to/project
BMAD_DOCS_PATH=docs/
BMAD_AGENTS_PATH=bmad/agents/
```

## Performance Tips

### Optimize Agent Performance

- **Use specific commands** instead of general requests
- **Provide focused context** rather than entire codebase
- **Shard large documents** for better context management
- **Start fresh sessions** for complex or unrelated tasks

### Maintain Development Velocity

- **Follow consistent workflows** for predictable results
- **Automate repetitive tasks** through agent patterns
- **Regular quality checks** to prevent technical debt
- **Continuous process improvement** based on results

## Quick Command Reference

### Most Used Commands

```
# Start agents
/analyst
/pm
/architect
/sm
/dev
/qa

# Get help
*help

# Common workflows
*research → *brief → *prd → *architecture → *draft → *develop → *review

# Document management
shard docs/prd.md
shard docs/architecture.md
```

### Emergency Commands

```
# Quick bug fix
/qa → *audit → /dev → *refactor → /qa → *review

# Performance issue
/dev → *optimize → /qa → *test

# Architecture problem
/architect → *design → /dev → *implement
```

This quick reference provides the essential commands and workflows for effective BMAD Method usage in your M&A SaaS platform development.
