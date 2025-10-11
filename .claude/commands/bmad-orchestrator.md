# BMAD v6-Alpha Workflow Orchestrator 🎭

## Overview

Central orchestrator for the BMAD v6-Alpha methodology, designed to guide you through the complete development lifecycle for M&A platform features using the revolutionary 4-phase approach.

## The BMAD v6-Alpha Methodology

### Phase 1: Analysis (Optional)

**Purpose**: Project discovery and requirements gathering
**Output**: Product briefs, research artifacts, conceptual foundation
**When**: New features, unclear requirements, market validation needed

### Phase 2: Planning (Required)

**Purpose**: Scale-adaptive project planning with automatic routing
**Output**: PRDs, epics, technical specifications (scale-dependent)
**When**: Every project - determines scope and next phase

### Phase 3: Solutioning (Levels 3-4 Only)

**Purpose**: Architecture design and technical planning
**Output**: Architecture documentation, technical patterns
**When**: Large projects (12+ stories, 2+ epics)

### Phase 4: Implementation (Required)

**Purpose**: Iterative development and delivery
**Output**: Working software, tests, documentation
**When**: All projects after planning/solutioning

## Available Workflows

### 🎯 start-project

**Description**: Initiate new M&A feature development with proper phase routing
**Usage**: I want to start developing a new M&A platform feature

### 📊 assess-scale

**Description**: Determine project scale (Level 0-4) and appropriate workflow
**Usage**: Help me understand the scale and complexity of my project

### 🔄 phase-transition

**Description**: Move between BMAD phases with proper handoffs
**Usage**: I'm ready to move from [current phase] to [next phase]

### 🎨 brainstorm-session

**Description**: Structured brainstorming for M&A features using advanced techniques
**Usage**: Guide me through creative ideation for new M&A functionality

### 📋 plan-feature

**Description**: Scale-adaptive planning with automatic workflow routing
**Usage**: Plan my M&A feature with appropriate scope and documentation

### 🏗️ architect-solution

**Description**: Design technical architecture for complex M&A features
**Usage**: Create technical architecture for my M&A platform feature

### 👥 assemble-team

**Description**: Orchestrate specialist agents for complex projects
**Usage**: Coordinate multiple agents for comprehensive feature development

## Scale-Adaptive Routing

### Level 0: Atomic Change

- **Scope**: Single bug fix or minor enhancement
- **Route**: Planning → Implementation
- **Agents**: Developer
- **Timeline**: Hours to 1 day

### Level 1: Small Feature (1-10 stories)

- **Scope**: Simple feature addition
- **Route**: Planning → Implementation
- **Agents**: PM → Developer → QA
- **Timeline**: 1-2 weeks

### Level 2: Medium Feature (5-15 stories)

- **Scope**: Complex feature with multiple components
- **Route**: Planning → Implementation
- **Agents**: Analyst → PM → Developer → QA
- **Timeline**: 2-4 weeks

### Level 3: Large Feature (12-40 stories)

- **Scope**: Major platform enhancement
- **Route**: Analysis → Planning → Solutioning → Implementation
- **Agents**: Analyst → PM → Architect → Developer → QA
- **Timeline**: 1-3 months

### Level 4: Platform Expansion (40+ stories)

- **Scope**: New product lines or major integrations
- **Route**: Analysis → Planning → Solutioning → Implementation
- **Agents**: Full team + M&A Specialist
- **Timeline**: 3+ months

## M&A-Specific Workflows

### Deal Discovery Features

```
Level 2-3: Company screening, market intelligence, pipeline management
Agents: M&A Analyst → PM → Architect → Developer
Focus: Data integration, screening algorithms, pipeline visualization
```

### Financial Modeling Features

```
Level 3-4: Valuation models, scenario analysis, deal comparison
Agents: M&A Analyst → PM → Architect → Developer → QA
Focus: Complex calculations, model templates, sensitivity analysis
```

### Due Diligence Features

```
Level 3: Checklist automation, document management, collaboration
Agents: M&A Analyst → PM → Developer → QA
Focus: Workflow automation, progress tracking, stakeholder coordination
```

## Usage Instructions

1. **Start Here**: Use `start-project` for any new initiative
2. **Follow Routing**: Trust the scale assessment and phase routing
3. **Engage Specialists**: Use domain experts (M&A Analyst) for complex features
4. **Maintain Momentum**: Don't skip phases - each builds on the previous
5. **Iterate**: Use retrospectives to improve future projects

## Phase Transition Checklist

### Analysis → Planning

- [ ] Business requirements clarified
- [ ] Market research completed
- [ ] Product brief approved
- [ ] Stakeholder alignment achieved

### Planning → Solutioning (Level 3-4 only)

- [ ] PRD completed and approved
- [ ] Epic breakdown finalized
- [ ] Technical constraints identified
- [ ] Architecture requirements defined

### Solutioning → Implementation

- [ ] Architecture documentation complete
- [ ] Technical patterns established
- [ ] Development standards defined
- [ ] Team capacity confirmed

### Implementation → Delivery

- [ ] All stories completed
- [ ] Testing and QA passed
- [ ] Documentation updated
- [ ] Retrospective conducted

## Command Examples

```
/start-project "Enhanced deal screening with AI-powered scoring"
/assess-scale "Multi-tenant document management for due diligence"
/brainstorm-session "Innovative M&A deal discovery methods"
/plan-feature "Automated valuation model templates"
/architect-solution "Scalable financial calculation engine"
```

## Integration Benefits

- **Consistent Process**: Standardized approach across all M&A features
- **Right-Sized Planning**: No over-engineering small features, no under-planning large ones
- **Knowledge Preservation**: Decisions and rationale captured throughout
- **Quality Assurance**: Built-in checkpoints and validation steps
- **Team Coordination**: Clear handoffs between specialists

Ready to orchestrate your M&A platform development? Let's start with the right phase for your project!
