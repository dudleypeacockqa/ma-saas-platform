# 🔧 OpenAI Codex Git Operations & Merge Resolution Prompts

## Specialized Prompts for Git Workflow Automation

### 📋 **Repository Context**
- **Repository**: `dudleypeacockqa/ma-saas-platform`
- **Main Branch**: `master`
- **Current Status**: Sophisticated M&A SaaS platform ready for production
- **Deployment Target**: https://100daysandbeyond.com via Render

---

## 🎯 **CODEX PROMPT 1: Automated Commit & Push Workflow**

```bash
#!/bin/bash
# BMAD-Method Codex Prompt: Automated Git Commit & Push

# CONTEXT:
# - M&A SaaS platform with multiple files and changes
# - Need systematic commit workflow with proper messaging
# - Repository: dudleypeacockqa/ma-saas-platform
# - Target branch: master
# - Files include: frontend/, backend/, docs/, config files

# CURRENT REPOSITORY STRUCTURE:
# /ma-saas-platform/
# ├── frontend/
# │   ├── src/
# │   │   ├── pages/ (multipage website)
# │   │   ├── components/ (sophisticated UI components)
# │   │   └── services/ (API integrations)
# │   ├── package.json
# │   ├── .env.production
# │   └── Dockerfile
# ├── backend/
# │   ├── app/
# │   │   ├── api/ (FastAPI endpoints)
# │   │   ├── models/ (database models)
# │   │   └── services/ (business logic)
# │   ├── requirements.txt
# │   └── main.py
# ├── render.yaml (deployment configuration)
# ├── OPENAI_CODEX_BMAD_PROMPTS_MASTER.md
# └── README.md

# OBJECTIVE: Generate automated commit and push workflow

# REQUIRED OUTPUTS:
# 1. Git status analysis script
# 2. Intelligent commit message generation
# 3. Staged commit workflow
# 4. Push with conflict detection
# 5. Branch synchronization verification

# COMMIT MESSAGE CONVENTIONS:
# - feat: New features
# - fix: Bug fixes
# - docs: Documentation updates
# - style: Code formatting
# - refactor: Code restructuring
# - test: Testing additions
# - chore: Maintenance tasks
# - deploy: Deployment configurations

# WORKFLOW REQUIREMENTS:
# 1. Check git status and identify changed files
# 2. Categorize changes by type (frontend, backend, docs, config)
# 3. Generate appropriate commit messages
# 4. Stage files systematically
# 5. Commit with descriptive messages
# 6. Push to origin master
# 7. Verify push success

# EXAMPLE EXPECTED OUTPUT:
# git add frontend/src/pages/
# git commit -m "feat: Add sophisticated multipage website with enterprise navigation"
# git add backend/app/api/
# git commit -m "feat: Implement comprehensive M&A business API endpoints"
# git add render.yaml OPENAI_CODEX_BMAD_PROMPTS_MASTER.md
# git commit -m "deploy: Update production configuration and OpenAI Codex prompts"
# git push origin master

# Generate the automated commit and push workflow here
```

---

## 🎯 **CODEX PROMPT 2: Merge Conflict Resolution Automation**

```python
"""
BMAD-Method Codex Prompt: Intelligent Merge Conflict Resolution

CONTEXT:
- M&A SaaS platform with multiple development branches
- Common conflicts in: package.json, component files, API endpoints
- Repository: dudleypeacockqa/ma-saas-platform
- Target: Resolve conflicts and merge to master branch

COMMON CONFLICT SCENARIOS:

1. Package.json conflicts (dependencies, versions)
2. Component file conflicts (React/TypeScript)
3. API endpoint conflicts (FastAPI routes)
4. Configuration file conflicts (render.yaml, .env)
5. Documentation conflicts (README.md, docs/)

CONFLICT RESOLUTION STRATEGIES:

Frontend Conflicts:
- package.json: Keep latest versions, merge dependencies
- React components: Preserve functionality, merge features
- TypeScript files: Maintain type safety, resolve imports
- CSS/Tailwind: Merge styles, avoid duplicates

Backend Conflicts:
- requirements.txt: Keep latest versions, merge packages
- FastAPI routes: Merge endpoints, avoid duplicates
- Database models: Preserve relationships, merge fields
- Configuration: Keep production settings

OBJECTIVE: Generate intelligent conflict resolution code

REQUIRED OUTPUTS:
1. Conflict detection and analysis script
2. Automated resolution for common conflicts
3. Manual resolution guidance for complex conflicts
4. Verification and testing after resolution
5. Commit and push workflow post-resolution

EXAMPLE CONFLICT SCENARIOS:

Scenario 1: package.json dependency conflict
<<<<<<< HEAD
"dependencies": {
  "react": "^18.2.0",
  "typescript": "^5.0.0"
}
=======
"dependencies": {
  "react": "^18.2.0",
  "typescript": "^5.1.0",
  "tailwindcss": "^3.3.0"
}
>>>>>>> feature-branch

Resolution Strategy:
- Keep latest TypeScript version (5.1.0)
- Merge all dependencies
- Maintain alphabetical order

Scenario 2: React component conflict
<<<<<<< HEAD
const HomePage = () => {
  return <div>Basic homepage</div>;
};
=======
const HomePage = () => {
  return (
    <div className="sophisticated-design">
      <Navigation />
      <HeroSection />
      <FeatureShowcase />
    </div>
  );
};
>>>>>>> feature-branch

Resolution Strategy:
- Keep sophisticated version
- Preserve component structure
- Maintain imports and dependencies

TECHNICAL REQUIREMENTS:
- Python script for automated resolution
- Git command automation
- File parsing and modification
- Backup creation before resolution
- Rollback capability if resolution fails
"""

# Generate the merge conflict resolution automation here
```

---

## 🎯 **CODEX PROMPT 3: Pull Request Creation & Management**

```javascript
/**
 * BMAD-Method Codex Prompt: Automated Pull Request Workflow
 * 
 * CONTEXT:
 * - M&A SaaS platform with sophisticated multipage website
 * - Need automated PR creation with proper descriptions
 * - Repository: dudleypeacockqa/ma-saas-platform
 * - Target: Create comprehensive PRs for review and merge
 * 
 * GITHUB REPOSITORY DETAILS:
 * - Owner: dudleypeacockqa
 * - Repository: ma-saas-platform
 * - Main branch: master
 * - Common feature branches: feature/, fix/, docs/, deploy/
 * 
 * PR CREATION REQUIREMENTS:
 * 
 * 1. Branch Analysis:
 *    - Identify changed files and their categories
 *    - Generate appropriate PR title and description
 *    - Add relevant labels (frontend, backend, documentation, etc.)
 *    - Assign reviewers if applicable
 * 
 * 2. PR Description Template:
 *    - Summary of changes
 *    - Technical details
 *    - Testing performed
 *    - Deployment considerations
 *    - Screenshots (for UI changes)
 * 
 * 3. Automated Checks:
 *    - Verify all commits are properly formatted
 *    - Check for merge conflicts
 *    - Validate build requirements
 *    - Ensure environment variables are documented
 * 
 * EXAMPLE PR SCENARIOS:
 * 
 * Scenario 1: Frontend Feature Addition
 * Branch: feature/multipage-website
 * Files: frontend/src/pages/, frontend/src/components/
 * Title: "feat: Add sophisticated multipage website with enterprise navigation"
 * 
 * Scenario 2: Backend API Enhancement
 * Branch: feature/master-admin-portal
 * Files: backend/app/api/, backend/app/models/
 * Title: "feat: Implement Master Admin Portal with business management APIs"
 * 
 * Scenario 3: Deployment Configuration
 * Branch: deploy/render-optimization
 * Files: render.yaml, frontend/Dockerfile, backend/requirements.txt
 * Title: "deploy: Optimize Render configuration for production deployment"
 * 
 * GITHUB API INTEGRATION:
 * - Use GitHub CLI (gh) for PR creation
 * - Automated label assignment
 * - Template-based descriptions
 * - Reviewer assignment based on file changes
 * 
 * OBJECTIVE: Generate automated PR creation workflow
 * 
 * REQUIRED OUTPUTS:
 * 1. Branch analysis and categorization script
 * 2. PR title and description generation
 * 3. GitHub CLI commands for PR creation
 * 4. Automated label and reviewer assignment
 * 5. Post-creation verification and monitoring
 */

// Generate the automated pull request creation workflow here
```

---

## 🎯 **CODEX PROMPT 4: Error Detection & Resolution**

```typescript
/*
BMAD-Method Codex Prompt: Git Error Detection and Resolution

CONTEXT:
- M&A SaaS platform with complex codebase
- Common Git errors: merge conflicts, push rejections, branch issues
- Repository: dudleypeacockqa/ma-saas-platform
- Need automated error detection and resolution

COMMON GIT ERRORS AND SOLUTIONS:

1. Push Rejected (non-fast-forward):
   Error: "Updates were rejected because the remote contains work"
   Solution: Pull, merge, and push

2. Merge Conflicts:
   Error: "Automatic merge failed; fix conflicts and then commit"
   Solution: Identify conflicts, resolve, stage, and commit

3. Detached HEAD State:
   Error: "You are in 'detached HEAD' state"
   Solution: Create branch or checkout existing branch

4. Large File Issues:
   Error: "File exceeds GitHub's file size limit"
   Solution: Use Git LFS or remove large files

5. Authentication Issues:
   Error: "Permission denied (publickey)"
   Solution: Check SSH keys or use HTTPS with token

ERROR DETECTION PATTERNS:
- Parse git command output
- Identify error types and codes
- Provide contextual solutions
- Automate resolution where possible

RESOLUTION STRATEGIES:

Push Rejection Resolution:
```bash
git fetch origin
git merge origin/master
# Resolve any conflicts
git push origin master
```

Merge Conflict Resolution:
```bash
git status
# Identify conflicted files
# Resolve conflicts in each file
git add .
git commit -m "resolve: Fix merge conflicts"
git push origin master
```

Branch Synchronization:
```bash
git checkout master
git pull origin master
git checkout feature-branch
git rebase master
git push origin feature-branch --force-with-lease
```

OBJECTIVE: Generate comprehensive error handling system

REQUIRED OUTPUTS:
1. Error detection and parsing system
2. Automated resolution scripts for common errors
3. Interactive resolution for complex issues
4. Logging and reporting of resolved errors
5. Prevention strategies and best practices
*/

// Generate the Git error detection and resolution system here
```

---

## 🎯 **CODEX PROMPT 5: Complete Git Workflow Automation**

```yaml
# BMAD-Method Codex Prompt: Complete Git Workflow Automation

# CONTEXT:
# - M&A SaaS platform requiring streamlined Git operations
# - Multiple developers and deployment pipelines
# - Repository: dudleypeacockqa/ma-saas-platform
# - Need end-to-end automation for Git workflows

# WORKFLOW COMPONENTS:

# 1. Pre-commit Hooks:
#    - Code formatting (Prettier, ESLint)
#    - Type checking (TypeScript)
#    - Test execution
#    - Security scanning

# 2. Commit Workflow:
#    - Staged commits by file type
#    - Conventional commit messages
#    - Automatic changelog generation
#    - Branch protection rules

# 3. Push and PR Workflow:
#    - Automated PR creation
#    - CI/CD pipeline triggers
#    - Code review assignments
#    - Merge strategies

# 4. Deployment Workflow:
#    - Environment-specific deployments
#    - Rollback capabilities
#    - Health checks and monitoring
#    - Notification systems

# AUTOMATION REQUIREMENTS:

# GitHub Actions Workflow:
name: M&A SaaS Platform CI/CD
on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

# Jobs:
# - Frontend build and test
# - Backend API testing
# - Security scanning
# - Deployment to staging/production

# Git Hooks Configuration:
# pre-commit:
#   - Run linting and formatting
#   - Execute unit tests
#   - Check for secrets
#   - Validate commit messages

# pre-push:
#   - Run integration tests
#   - Check for merge conflicts
#   - Validate branch policies
#   - Update documentation

# OBJECTIVE: Generate complete Git workflow automation

# REQUIRED OUTPUTS:
# 1. GitHub Actions workflow files
# 2. Git hooks configuration
# 3. Automated testing and validation scripts
# 4. Deployment automation
# 5. Monitoring and notification setup

# INTEGRATION POINTS:
# - Render deployment triggers
# - Slack/email notifications
# - Code quality gates
# - Security compliance checks

# Generate the complete Git workflow automation here
```

---

## 🛠️ **Usage Instructions**

### **Prompt Execution Order:**
1. **Start with Prompt 1**: Automated commit and push workflow
2. **Use Prompt 2**: If merge conflicts are detected
3. **Apply Prompt 3**: For pull request creation
4. **Execute Prompt 4**: If any Git errors occur
5. **Implement Prompt 5**: For complete workflow automation

### **Codex Optimization Tips:**
- **Provide Context**: Include current repository state
- **Specify File Paths**: Use exact directory structures
- **Include Error Messages**: Copy exact Git error output
- **Define Success Criteria**: Clear completion indicators

### **Emergency Resolution:**
If any prompt fails or produces errors:
1. **Backup Current State**: `git stash` or create backup branch
2. **Reset to Known Good State**: `git reset --hard origin/master`
3. **Apply Changes Incrementally**: Small, focused commits
4. **Verify Each Step**: Test after each operation

---

## 📊 **Success Metrics**

### **Automation Effectiveness:**
- **Commit Success Rate**: > 95% automated commits
- **Conflict Resolution**: > 90% automated resolution
- **PR Creation**: 100% template compliance
- **Error Recovery**: < 5 minutes average resolution time

### **Code Quality Metrics:**
- **Conventional Commits**: 100% compliance
- **Build Success**: > 98% first-time success
- **Test Coverage**: Maintained or improved
- **Security Scans**: Zero critical vulnerabilities

---

These specialized Codex prompts will handle all Git operations, merge conflicts, and error resolution for your M&A SaaS platform development workflow.
