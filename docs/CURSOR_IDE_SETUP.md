# Cursor IDE Setup Guide for 100daysandbeyond.com

## Overview

Complete setup guide for using Cursor IDE with Claude Code CLI and OpenAI Codex for building the M&A SaaS Platform.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Install Cursor IDE](#install-cursor-ide)
3. [Clone Repository](#clone-repository)
4. [Configure AI Assistants](#configure-ai-assistants)
5. [Project Structure Overview](#project-structure-overview)
6. [Development Workflow](#development-workflow)
7. [AI Prompt Templates](#ai-prompt-templates)

---

## Prerequisites

### Required Software

- **Git**: https://git-scm.com/downloads
- **Node.js 18+**: https://nodejs.org/
- **pnpm**: `npm install -g pnpm`
- **PostgreSQL 14+**: https://www.postgresql.org/download/
- **Cursor IDE**: https://cursor.sh/

### Required Accounts

- ✅ GitHub account (you have this)
- ✅ Cloudflare account (configured)
- ✅ Clerk account (configured)
- ✅ Stripe account (configured)
- ✅ Render account (configured)
- ✅ Anthropic API key (for Claude)
- ⚠️ OpenAI API key (for Codex) - **Get this from https://platform.openai.com/api-keys**

---

## Install Cursor IDE

### Step 1: Download and Install

**Windows:**

```powershell
# Download from https://cursor.sh/
# Run the installer
# Follow installation wizard
```

**Mac:**

```bash
# Download from https://cursor.sh/
# Drag to Applications folder
```

**Linux:**

```bash
# Download .AppImage from https://cursor.sh/
chmod +x cursor-*.AppImage
./cursor-*.AppImage
```

### Step 2: Initial Setup

1. **Launch Cursor**
2. **Sign in** with GitHub account
3. **Skip** the sample project
4. **Go to Settings** → **Features** → Enable:
   - AI Code Completion
   - AI Chat
   - Terminal
   - Git Integration

### Step 3: Configure AI Models

#### Claude Code (Primary)

1. Open Cursor Settings (`Ctrl+,` or `Cmd+,`)
2. Go to **Features** → **AI**
3. Click **Add Model**
4. Select **Anthropic Claude**
5. Enter your Anthropic API key
6. Select Model: **Claude 3.5 Sonnet** (best for coding)
7. Set as **Default Model**

#### OpenAI Codex (Secondary)

1. In AI settings, click **Add Model**
2. Select **OpenAI**
3. Enter your OpenAI API key
4. Select Model: **GPT-4 Turbo**
5. Enable for **Code Completion**

### Step 4: Configure Terminal

1. Go to **Settings** → **Terminal**
2. Set shell:
   - **Windows**: PowerShell or Git Bash
   - **Mac/Linux**: zsh or bash
3. Enable **Terminal Suggestions**

---

## Clone Repository

### Method 1: Using Cursor's Git Integration

1. Open Cursor
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Type: `Git: Clone`
4. Enter URL: `https://github.com/dudleypeacockqa/ma-saas-platform.git`
5. Select folder: `C:\Projects` (or your preferred location)
6. Click **Open** when clone completes

### Method 2: Using Terminal

```powershell
# Windows PowerShell
cd C:\Projects
git clone https://github.com/dudleypeacockqa/ma-saas-platform.git
cd ma-saas-platform

# Open in Cursor
cursor .
```

```bash
# Mac/Linux
cd ~/Projects
git clone https://github.com/dudleypeacockqa/ma-saas-platform.git
cd ma-saas-platform

# Open in Cursor
cursor .
```

---

## Configure AI Assistants

### Claude Code CLI Integration

#### Install Claude Code CLI

```bash
# Install globally
npm install -g @anthropic-ai/claude-code-cli

# Verify installation
claude-code --version
```

#### Configure Claude Code

```bash
# Set up API key
claude-code config set apiKey YOUR_ANTHROPIC_API_KEY

# Set default model
claude-code config set model claude-3-5-sonnet-20241022

# Enable MCP servers
claude-code config set mcpEnabled true
```

#### Test Claude Code

```bash
# Test with simple command
claude-code "create a hello world function in JavaScript"
```

### OpenAI Codex CLI Integration

#### Install OpenAI CLI

```bash
npm install -g openai-cli

# Configure API key
openai api_key set YOUR_OPENAI_API_KEY
```

### MCP Server Configuration

Create `~/.claude-code/mcp-config.json`:

```json
{
  "mcpServers": {
    "render": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-render"],
      "env": {
        "RENDER_API_KEY": "rnd_WKg7bCrlyQXiNdEABsjB8uV82s0N"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "your_database_url_here"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "env": {
        "ALLOWED_DIRECTORIES": ["/Projects/ma-saas-platform"]
      }
    }
  }
}
```

---

## Project Structure Overview

```
ma-saas-platform/
├── frontend/              # React + Vite frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── lib/          # Utilities and helpers
│   │   ├── hooks/        # Custom React hooks
│   │   └── App.jsx       # Main app component
│   ├── public/           # Static assets
│   ├── server.js         # Express server for production
│   ├── package.json
│   └── vite.config.js
│
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── models/       # Database models
│   │   ├── routers/      # API routes
│   │   ├── services/     # Business logic
│   │   └── main.py       # FastAPI app
│   ├── migrations/       # Database migrations
│   ├── tests/            # Backend tests
│   ├── requirements.txt
│   └── .env             # Backend environment variables
│
├── docs/                 # Documentation
│   ├── CURSOR_IDE_SETUP.md (this file)
│   ├── CLOUDFLARE_DNS_SETUP.md
│   ├── PHASE2_EXECUTION_GUIDE.md
│   └── API_DOCUMENTATION.md
│
├── .github/              # GitHub Actions workflows
│   └── workflows/
│       ├── deploy-frontend.yml
│       └── deploy-backend.yml
│
└── README.md             # Project overview
```

---

## Development Workflow

### 1. Start Development Environment

#### Terminal 1: Frontend

```powershell
cd frontend
pnpm install
pnpm run dev
```

Frontend runs on: http://localhost:5173

#### Terminal 2: Backend

```powershell
cd backend
pip install -r requirements.txt
python run.py
```

Backend runs on: http://localhost:8000

#### Terminal 3: Database

```powershell
# Start PostgreSQL (if not running as service)
pg_ctl start

# Run migrations
cd backend
python -m alembic upgrade head
```

### 2. Use AI Assistants in Cursor

#### Quick Commands

- **Ctrl+K** (Cmd+K): AI code generation in current file
- **Ctrl+L** (Cmd+L): Open AI chat sidebar
- **Ctrl+Shift+K**: AI terminal commands
- **Ctrl+Space**: AI code completion

#### AI Chat Commands

```
@claude Create a new React component for deal listing
@claude Explain this function
@claude Refactor this code to use async/await
@claude Add error handling to this API route
@claude Generate tests for this component
```

### 3. Git Workflow with AI

```powershell
# AI-assisted commit messages
git add .
cursor commit  # AI generates commit message

# Or manually
git commit -m "feat: Add deal listing component"
git push origin master
```

---

## AI Prompt Templates

### Frontend Development Prompts

#### 1. Create New React Component

```
Create a new React component in frontend/src/components/ called DealCard.jsx that:
- Displays deal information (title, company name, value, stage)
- Uses shadcn/ui Card component
- Has hover effects and animations
- Includes action buttons (View, Edit, Delete)
- Follows the existing design system in the project
- Uses Tailwind CSS for styling
- Includes PropTypes for type checking
```

#### 2. Build Dashboard Page

```
Create a dashboard page in frontend/src/pages/Dashboard.jsx that:
- Fetches deal data from /api/deals endpoint
- Displays key metrics (total deals, total value, active deals)
- Shows a data table using shadcn/ui Table component
- Includes filtering and sorting
- Has responsive design (mobile, tablet, desktop)
- Uses React Query for data fetching
- Implements loading states and error handling
- Follows accessibility best practices (ARIA labels, keyboard navigation)
```

#### 3. Implement Authentication Flow

```
Implement Clerk authentication in the frontend:
- Wrap App.jsx with ClerkProvider
- Create protected routes using SignedIn/SignedOut components
- Add sign-in and sign-up pages using Clerk UI components
- Implement user profile page
- Add sign-out functionality
- Store user data in React Context
- Handle authentication state in API calls
- Test authentication flow end-to-end
```

### Backend Development Prompts

#### 1. Create API Endpoint

```
Create a new FastAPI endpoint in backend/app/routers/deals.py:
- POST /api/deals - Create new deal
- GET /api/deals - List all deals with pagination
- GET /api/deals/{deal_id} - Get single deal
- PUT /api/deals/{deal_id} - Update deal
- DELETE /api/deals/{deal_id} - Delete deal

Requirements:
- Use Pydantic models for request/response validation
- Implement authentication with Clerk JWT tokens
- Add authorization (users can only access their own deals)
- Include database transactions
- Add comprehensive error handling
- Log all operations
- Write API documentation (OpenAPI)
- Include unit tests
```

#### 2. Create Database Models

```
Create SQLAlchemy models in backend/app/models/deal.py:
- Deal model with fields: id, title, company_name, value, stage, user_id, created_at, updated_at
- Include relationships to User model
- Add indexes for frequently queried fields
- Implement soft delete (deleted_at field)
- Add validation methods
- Create Alembic migration
- Write model tests
```

#### 3. Implement Stripe Integration

```
Create Stripe subscription system in backend/app/services/stripe_service.py:
- Create customer on user signup
- Create subscription plans (Starter, Pro, Enterprise)
- Handle subscription creation
- Implement webhook handlers for:
  - customer.subscription.created
  - customer.subscription.updated
  - customer.subscription.deleted
  - invoice.payment_succeeded
  - invoice.payment_failed
- Update user subscription status in database
- Handle trial periods
- Implement subscription upgrades/downgrades
- Add subscription status checks to API endpoints
- Test with Stripe test mode
```

### Database Prompts

#### 1. Create Migration

```
Create an Alembic migration for the deals table:
- Table name: deals
- Columns:
  - id (UUID, primary key)
  - user_id (UUID, foreign key to users table)
  - title (VARCHAR 255, not null)
  - company_name (VARCHAR 255, not null)
  - value (DECIMAL 15,2, not null)
  - stage (ENUM: 'lead', 'qualification', 'proposal', 'negotiation', 'closed')
  - created_at (TIMESTAMP, default now())
  - updated_at (TIMESTAMP, default now())
  - deleted_at (TIMESTAMP, nullable)
- Indexes:
  - idx_deals_user_id
  - idx_deals_stage
  - idx_deals_created_at
- Generate migration: alembic revision --autogenerate -m "Create deals table"
```

#### 2. Complex Query

```
Write a SQL query using SQLAlchemy ORM to:
- Get all deals for a specific user
- Filter by stage and date range
- Include aggregated metrics (total value, count by stage)
- Sort by value (descending)
- Paginate results (20 per page)
- Include soft-deleted check
- Optimize for performance
```

### Testing Prompts

#### 1. Frontend Tests

```
Create Jest tests for the DealCard component:
- Test rendering with different prop combinations
- Test button click handlers
- Test hover states
- Test accessibility (ARIA labels, keyboard navigation)
- Mock API calls
- Test error states
- Achieve 80%+ code coverage
```

#### 2. Backend Tests

```
Create pytest tests for the deals API endpoints:
- Test CRUD operations
- Test authentication and authorization
- Test input validation
- Test error handling
- Test pagination
- Mock database calls
- Use fixtures for test data
- Achieve 80%+ code coverage
```

### Deployment Prompts

#### 1. Deploy Frontend

```
Deploy the frontend to Render:
- Build production bundle: pnpm run build
- Test production build locally: pnpm start
- Commit changes to GitHub
- Verify automatic deployment on Render
- Check deployment logs for errors
- Test live site: https://100daysandbeyond.com
- Verify environment variables are set
- Test authentication flow
- Check CSP headers
```

#### 2. Deploy Backend

```
Deploy the backend to Render:
- Run database migrations
- Build Docker image
- Test Docker container locally
- Push to GitHub
- Monitor deployment logs
- Verify health check: https://api.100daysandbeyond.com/health
- Test API endpoints
- Check database connections
- Verify environment variables
```

---

## Advanced Features

### 1. Multi-File Editing with AI

Select multiple files in sidebar, then:

```
Refactor the deal management system across these files to:
- Use React Query for all API calls
- Implement optimistic updates
- Add proper TypeScript types
- Improve error handling
- Add loading skeletons
```

### 2. AI-Powered Code Review

Before committing:

```
@claude Review this code for:
- Security vulnerabilities
- Performance issues
- Best practices violations
- Missing error handling
- Accessibility issues
- Generate suggestions for improvements
```

### 3. Documentation Generation

```
@claude Generate comprehensive documentation for this API endpoint including:
- Endpoint description
- Request parameters
- Response format
- Error codes
- Usage examples
- cURL examples
```

---

## Troubleshooting

### AI Not Responding

1. Check API key in Settings → AI
2. Verify internet connection
3. Check API quota/billing
4. Restart Cursor IDE

### Code Completion Not Working

1. Enable AI Code Completion in settings
2. Check language server is running
3. Verify file type is supported
4. Try `Ctrl+Space` to trigger manually

### Terminal Issues

1. Restart integrated terminal
2. Check shell configuration
3. Verify PATH environment variable

### Git Integration Issues

1. Verify Git is installed: `git --version`
2. Configure Git credentials
3. Check repository status: `git status`

---

## Best Practices

### 1. Use AI for Repetitive Tasks

- Generating boilerplate code
- Writing tests
- Creating documentation
- Formatting code

### 2. Review AI-Generated Code

- Always review before committing
- Test thoroughly
- Check for security issues
- Verify best practices

### 3. Iterative Prompts

- Start with high-level description
- Refine with specific requirements
- Ask for improvements
- Request explanations

### 4. Save Custom Prompts

Create `.cursor/prompts/` directory with templates:

```
ma-saas-platform/
└── .cursor/
    └── prompts/
        ├── component-template.md
        ├── api-endpoint-template.md
        └── test-template.md
```

---

## Next Steps

1. ✅ Complete Cursor IDE setup
2. ✅ Clone repository
3. ✅ Configure AI models
4. ✅ Test development environment
5. 📝 Start building with AI prompts (see next section)
6. 📝 Deploy first feature
7. 📝 Iterate and improve

---

## Resources

- **Cursor Documentation**: https://cursor.sh/docs
- **Claude Code CLI**: https://github.com/anthropics/claude-code
- **Anthropic API**: https://console.anthropic.com/
- **OpenAI API**: https://platform.openai.com/
- **Project Documentation**: [../docs/](../docs/)

---

**Last Updated:** 2025-10-11
**Status:** Ready for use
