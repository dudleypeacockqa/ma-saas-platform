# Cursor + Claude Code CLI + OpenAI Codex Setup Guide

## Project Structure for AI-Assisted Development

This M&A SaaS platform is optimized for development with Cursor IDE using Claude Code CLI and OpenAI Codex CLI.

## Development Workflow

### 1. BMAD Methodology Integration
The project includes the complete BMAD (Breakthrough Method of Agile AI-Driven Development) framework in the `bmad-core/` directory:

- **Agents**: Pre-configured AI agents for different roles (Analyst, PM, Architect, Dev, QA)
- **Templates**: Structured templates for PRDs, architecture docs, and user stories
- **Workflows**: Step-by-step development processes
- **Checklists**: Quality gates and validation criteria

### 2. Recommended Cursor Extensions
- Claude Code CLI integration
- OpenAI Codex CLI integration
- Python extension pack
- React/TypeScript extensions
- PostgreSQL extension

### 3. AI-Assisted Development Commands

#### Using Claude Code CLI
```bash
# Start with business analysis
claude --agent bmad-core/agents/analyst.md

# Create product requirements
claude --agent bmad-core/agents/pm.md

# Generate user stories
claude --agent bmad-core/agents/sm.md

# Implement features
claude --agent bmad-core/agents/dev.md

# Quality assurance
claude --agent bmad-core/agents/qa.md
```

#### Using OpenAI Codex CLI
```bash
# Generate boilerplate code
codex generate --template react-component
codex generate --template fastapi-endpoint
codex generate --template postgresql-schema

# Code review and optimization
codex review --file src/components/DealPipeline.tsx
codex optimize --file backend/api/deals.py
```

### 4. Project Architecture for AI Development

```
ma-saas-platform/
├── bmad-core/              # BMAD methodology framework
├── frontend/               # React TypeScript application
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/         # Main application pages
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # API integration
│   │   └── types/         # TypeScript definitions
├── backend/               # Python FastAPI application
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   └── utils/        # Utility functions
├── database/             # Database schemas and migrations
├── docs/                # Project documentation
└── deployment/          # Render deployment configs
```

### 5. AI Prompting Best Practices

#### For Claude Code CLI
- Use specific, context-rich prompts
- Reference the BMAD agents for role-specific guidance
- Include business context from the M&A domain
- Leverage the existing templates and checklists

#### For OpenAI Codex CLI
- Focus on code generation and optimization
- Use for boilerplate creation and refactoring
- Leverage for testing and documentation generation
- Optimize for performance and security

### 6. Development Phases with AI Assistance

#### Phase 1: Foundation (Using BMAD Analyst + PM)
1. Use Analyst agent to refine M&A workflow requirements
2. Use PM agent to create detailed PRD
3. Use Architect agent to finalize system design

#### Phase 2: Core Development (Using BMAD SM + Dev)
1. Use SM agent to break down features into stories
2. Use Dev agent for implementation guidance
3. Use Codex for rapid code generation

#### Phase 3: AI Integration (Using Claude Code CLI)
1. Integrate Claude MCP server
2. Implement AI-powered deal analysis
3. Add intelligent document processing

#### Phase 4: Quality & Deployment (Using BMAD QA)
1. Use QA agent for comprehensive testing
2. Use Codex for test generation
3. Deploy to Render with CI/CD

### 7. Key Files for AI Context

When working with AI assistants, always include these files for context:
- `README.md` - Project overview
- `bmad-core/data/bmad-kb.md` - BMAD knowledge base
- `docs/architecture.md` - System architecture
- `docs/api-spec.md` - API specifications
- `docs/user-stories.md` - Feature requirements

### 8. Multi-Tenant Considerations

The AI assistants should be aware of:
- Tenant isolation requirements
- Data security and privacy
- Scalability patterns
- Role-based access control

### 9. M&A Domain Context

Provide AI assistants with M&A-specific context:
- Deal lifecycle stages
- Due diligence processes
- Financial modeling requirements
- Regulatory compliance needs
- Private equity workflows

This setup ensures maximum productivity when using Cursor with Claude Code CLI and OpenAI Codex CLI for developing the M&A SaaS platform.
