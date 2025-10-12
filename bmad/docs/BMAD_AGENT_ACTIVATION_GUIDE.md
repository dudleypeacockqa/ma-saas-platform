# BMAD Agent Activation Guide - Cursor Claude Code CLI

## Overview

This guide provides the exact commands and prompts needed to activate BMAD agents in Cursor Claude Code CLI for Phase 2 development of the M&A SaaS platform.

---

## 🎯 Primary Agent: BMAD Master

### **Cursor Claude Code CLI Activation**

```bash
# Navigate to project directory
cd ma-saas-platform

# Activate BMAD Master agent in Cursor Claude Code CLI
@bmad/core/agents/bmad-master.md
```

### **Agent Activation Prompt**

```
Activate BMAD Master agent for M&A SaaS platform Phase 2 development.

Project context:
- Phase 1 infrastructure complete and operational
- Frontend: https://100daysandbeyond.com (React/Vite)
- Backend: https://ma-saas-backend.onrender.com (FastAPI)
- Database: PostgreSQL with 125 tables
- Authentication: Clerk multi-tenant system
- User: Dudley
- Goal: £200M wealth-building through M&A platform

Load configuration from bmad/core/config.yaml and show available workflows for Phase 2 core business features development.
```

---

## 📋 Phase 2 Workflow Execution

### **1. Product Brief Workflow**

**Cursor Command:**

```bash
@bmad/core/agents/bmad-master.md
```

**Activation Prompt:**

```
Execute product-brief workflow for M&A SaaS platform Phase 2.

Context: Phase 1 infrastructure complete. Need to define core business features:
- Deal pipeline management and tracking
- Document management and collaboration
- Team workspace and permissions
- Analytics and reporting dashboard
- Integration capabilities

Target: Revenue-generating features for M&A professionals. Multi-tenant SaaS with subscription model.
User: Dudley | Goal: £200M wealth-building
```

### **2. Product Requirements Document (PRD)**

**Cursor Command:**

```bash
@bmad/core/agents/bmad-master.md
```

**Activation Prompt:**

```
Execute PRD workflow for M&A SaaS platform core business features.

Product brief complete. Need detailed requirements for:
- Deal creation, tracking, and pipeline management
- Document upload, organization, and collaboration
- Team workspaces with role-based permissions
- Analytics dashboards and reporting
- CRM and email integrations

Platform: Level 3 complexity enterprise SaaS
User: Dudley | Communication: English
```

### **3. UX/UI Specification**

**Cursor Command:**

```bash
@bmad/core/agents/bmad-master.md
```

**Activation Prompt:**

```
Execute ux-spec workflow for M&A SaaS platform user experience design.

User personas:
- M&A Advisors (primary users - deal management)
- Deal Team Members (collaborators - document review)
- Firm Partners (executives - analytics oversight)

Focus: Professional, efficient workflows for high-stakes M&A transactions
Platform: React frontend with modern UI components
User: Dudley | Communication: English
```

### **4. Solution Architecture**

**Cursor Command:**

```bash
@bmad/core/agents/bmad-master.md
```

**Activation Prompt:**

```
Execute solution-architecture workflow for Phase 2 business features.

Existing infrastructure:
- Frontend: React/Vite with Clerk authentication
- Backend: FastAPI with PostgreSQL (125 tables)
- Hosting: Render.com with Cloudflare CDN
- Multi-tenant architecture established

New requirements: Real-time collaboration, file management, advanced analytics, third-party integrations, notification system
User: Dudley | Communication: English
```

### **5. Technical Specifications**

**Cursor Command:**

```bash
@bmad/core/agents/bmad-master.md
```

**Activation Prompt:**

```
Execute tech-spec workflow for Phase 2 core features implementation.

Generate detailed technical specifications:
- API endpoint specifications (FastAPI)
- Database schema updates (PostgreSQL)
- Frontend component architecture (React)
- Integration specifications (CRM, email)
- Security and performance requirements
- Acceptance criteria for each feature

Codebase: ma-saas-platform/ | User: Dudley | Communication: English
```

### **6. Story Creation**

**Cursor Command:**

```bash
@bmad/core/agents/bmad-master.md
```

**Activation Prompt:**

```
Execute create-story workflow for Phase 2 feature development.

Break down technical specifications into development stories:
1. Deal creation and management (MVP priority)
2. Pipeline visualization and tracking
3. Document upload and organization
4. Team collaboration features
5. Analytics foundation

Story sizing: 1-3 day implementation cycles
User: Dudley | Communication: English
```

### **7. Development Execution**

**Cursor Command:**

```bash
@bmad/core/agents/bmad-master.md
```

**Activation Prompt:**

```
Execute dev-story workflow for [STORY_NAME].

Implementation context:
- Codebase: ma-saas-platform/
- Frontend: React/Vite (frontend/ directory)
- Backend: FastAPI (backend/ directory)
- Database: PostgreSQL with Alembic migrations
- Follow established patterns and code quality standards

Story: [Specific story from create-story workflow]
User: Dudley | Communication: English
```

---

## 🔧 Workflow Management Commands

### **List Available Workflows**

**Cursor Command:**

```bash
@bmad/core/agents/bmad-master.md
```

**Prompt:**

```
*list-workflows

Show all available BMAD workflows for Phase 2 development.
```

### **List Available Tasks**

**Cursor Command:**

```bash
@bmad/core/agents/bmad-master.md
```

**Prompt:**

```
*list-tasks

Show all available BMAD tasks for M&A SaaS platform development.
```

### **Help Menu**

**Cursor Command:**

```bash
@bmad/core/agents/bmad-master.md
```

**Prompt:**

```
*help

Show BMAD Master agent menu and available commands.
```

---

## 🚀 Quick Start Commands

### **Immediate Phase 2 Start**

**Single Command Activation:**

```bash
cd ma-saas-platform && @bmad/core/agents/bmad-master.md
```

**Complete Activation Prompt:**

```
Activate BMAD Master agent and execute product-brief workflow for M&A SaaS platform Phase 2.

Phase 1 Status: ✅ Complete and operational
- Frontend: https://100daysandbeyond.com
- Backend: https://ma-saas-backend.onrender.com
- Database: PostgreSQL (125 tables, 1,196 indexes)
- Authentication: Clerk multi-tenant system

Phase 2 Objective: Core business features for revenue generation
- Deal pipeline management
- Document collaboration
- Team workspaces
- Analytics dashboards
- Integration capabilities

User: Dudley | Goal: £200M wealth-building | Communication: English
Target: First paying customers within 30 days

Load bmad/core/config.yaml and begin product-brief workflow.
```

---

## 📊 Workflow Sequence

### **Recommended Execution Order**

1. **Product Brief** → Define what to build
2. **PRD** → Detail requirements and specifications
3. **UX Spec** → Design user experience
4. **Solution Architecture** → Plan technical implementation
5. **Tech Spec** → Create detailed technical specifications
6. **Create Stories** → Break into development tasks
7. **Dev Stories** → Implement features iteratively

### **Time Allocation**

- **Week 1**: Product Brief + PRD (workflows 1-2)
- **Week 2**: UX Spec + Solution Architecture (workflows 3-4)
- **Week 3**: Tech Spec + Story Creation (workflows 5-6)
- **Week 4-8**: Development Execution (workflow 7, multiple iterations)

---

## 🔍 Troubleshooting

### **Agent Not Loading**

**Issue**: BMAD Master agent doesn't activate
**Solution**:

```bash
# Ensure you're in the correct directory
cd ma-saas-platform

# Verify agent file exists
ls bmad/core/agents/bmad-master.md

# Use full path if needed
@./bmad/core/agents/bmad-master.md
```

### **Config Not Found**

**Issue**: "Config file not found" error
**Solution**:

```bash
# Verify config file exists
ls bmad/core/config.yaml

# If missing, check the BMAD infrastructure context file for restoration
```

### **Workflow Not Found**

**Issue**: Workflow path not recognized
**Solution**:

```bash
# List available workflows first
*list-workflows

# Use exact workflow names from the manifest
```

---

## 📝 Configuration Verification

### **Before Starting Phase 2**

**Verify Configuration:**

```bash
# Check BMAD structure
ls -la bmad/
ls -la bmad/core/
ls -la bmad/core/agents/
ls -la bmad/_cfg/

# Verify key files exist
cat bmad/core/config.yaml
cat bmad/_cfg/workflow-manifest.csv
cat bmad/_cfg/task-manifest.csv
```

**Expected Output:**

- ✅ bmad-master.md agent file
- ✅ config.yaml with user settings
- ✅ workflow-manifest.csv with available workflows
- ✅ task-manifest.csv with available tasks

---

## 🎯 Success Indicators

### **Successful Agent Activation**

You'll know the agent is working when you see:

1. **Greeting with your name** (Dudley)
2. **Numbered menu** of available options
3. **Workflow list** when requested
4. **Task execution** following BMAD methodology

### **Successful Workflow Execution**

Each workflow should:

1. **Load configuration** from config.yaml
2. **Execute systematically** following BMAD steps
3. **Generate outputs** in specified formats
4. **Save results** to appropriate directories
5. **Provide next steps** for continuation

---

## 🚀 Ready for Phase 2

**Your platform is ready when:**

- ✅ BMAD Master agent activates successfully
- ✅ Configuration loads without errors
- ✅ Workflows execute and generate outputs
- ✅ Development stories are created and prioritized
- ✅ Implementation begins with clear specifications

**Use these exact commands and prompts to ensure consistent, successful BMAD methodology execution for your Phase 2 development!**

---

_Last updated: October 11, 2025 | BMAD Methodology v6_
