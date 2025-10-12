# M&A SaaS Platform Backend Documentation

**Generated**: October 12, 2025
**Version**: 2.0.0
**Project Type**: Backend API (FastAPI)
**Scan Level**: Quick
**Documentation Tool**: BMad document-project workflow v1.2.0

---

## Project Overview

### Quick Reference

- **Type**: Backend API Service (Python FastAPI)
- **Primary Language**: Python 3.11+
- **Framework**: FastAPI 0.115.0
- **Architecture**: Multi-tenant RESTful API with Clerk Authentication
- **Database**: PostgreSQL with pgvector extension
- **Entry Point**: `app/main.py`
- **Lines of Code**: ~15,000+ (estimated)

### Technology Stack Summary

| Category           | Technology       | Version | Purpose                              |
| ------------------ | ---------------- | ------- | ------------------------------------ |
| **Framework**      | FastAPI          | 0.115.0 | High-performance async API framework |
| **Server**         | Uvicorn          | 0.32.0  | ASGI server                          |
| **Database ORM**   | SQLAlchemy       | 2.0.36  | Database ORM with async support      |
| **Database**       | PostgreSQL       | Latest  | Primary data store                   |
| **Vector DB**      | pgvector         | 0.3.6   | AI/ML vector embeddings              |
| **Migrations**     | Alembic          | 1.14.0  | Database schema migrations           |
| **Authentication** | Clerk            | 3.2.0+  | User auth & organization management  |
| **AI Integration** | Anthropic Claude | 0.37.1  | AI agent capabilities                |
| **AI Integration** | OpenAI           | 1.58.1  | Additional AI features               |
| **Payments**       | Stripe           | 8.8.0   | Payment processing                   |
| **Cloud Storage**  | AWS S3 (boto3)   | 1.35.56 | Document storage                     |
| **Validation**     | Pydantic         | 2.x     | Data validation                      |

---

## Architecture Pattern

**Type**: Multi-tenant SaaS Backend API
**Pattern**: Layered architecture with service-oriented design

### Architectural Layers

1. **API Layer** (`app/api/`, `app/routers/`) - RESTful endpoints
2. **Service Layer** (`app/services/`) - Business logic
3. **Model Layer** (`app/models/`) - Data models & ORM
4. **Database Layer** (`app/core/database.py`) - DB connections & sessions
5. **Authentication Layer** (`app/auth/`) - Clerk integration & tenant isolation
6. **Integration Layer** (`app/integrations/`) - External service integrations
7. **AI Agents** (`app/agents/`) - Intelligent automation

### Key Architectural Features

- **Multi-tenancy**: Organization-based data isolation
- **Async/Await**: Full async support for high performance
- **Middleware Stack**: Authentication, CORS, tenant isolation
- **Webhook Handling**: Clerk user/org sync webhooks
- **Vector Search**: pgvector for AI-powered semantic search
- **Modular Routers**: Clean separation of API concerns

---

## Generated Documentation

### Core Documentation

- [Architecture Overview](./backend-architecture.md) - System architecture & patterns
- [Source Tree Analysis](./backend-source-tree.md) - Directory structure & organization
- [API Endpoints](./backend-api-endpoints.md) _(To be generated)_
- [Data Models](./backend-data-models.md) _(To be generated)_
- [Development Guide](./backend-development-guide.md) _(To be generated)_

### Feature-Specific Documentation

- **Deal Management**: Comprehensive M&A deal tracking
- **Due Diligence**: Checklists, documents, and analysis
- **Document Management**: Version control, approvals, collaboration
- **Analytics**: Pipeline analytics, advanced reporting
- **Negotiations**: Term sheets, deal structuring
- **Integrations**: Multi-platform connectivity
- **AI Agents**: Intelligent deal sourcing, content generation

---

## Project Structure Summary

```
backend/
├── app/                      # Application source code
│   ├── main.py              # FastAPI application entry point
│   ├── agents/              # AI agents for automation
│   │   ├── acquisition_agent.py
│   │   ├── deal_sourcing_agent.py
│   │   └── content_agent.py
│   ├── api/                 # API endpoints (v1 & legacy)
│   │   ├── v1/              # Version 1 API endpoints
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── deals.py         # Deal management
│   │   ├── documents.py     # Document handling
│   │   └── [31 API modules total]
│   ├── auth/                # Clerk authentication & tenant isolation
│   │   ├── clerk_auth.py    # Clerk integration
│   │   ├── tenant_isolation.py  # Multi-tenant data isolation
│   │   └── webhooks.py      # Clerk webhook handlers
│   ├── core/                # Core application configuration
│   │   ├── config.py        # Settings & environment
│   │   ├── database.py      # DB connection & session
│   │   ├── db_init.py       # Schema initialization
│   │   └── deps.py          # Dependency injection
│   ├── middleware/          # Request/response middleware
│   │   ├── auth_middleware.py
│   │   └── permission_middleware.py
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── base.py          # Base model class
│   │   ├── organization.py  # Multi-tenant organizations
│   │   ├── user.py          # User management
│   │   ├── deal.py          # Deal tracking
│   │   ├── documents.py     # Document management
│   │   ├── negotiations.py  # Term sheets & negotiations
│   │   └── [22 model modules total]
│   ├── routers/             # FastAPI routers
│   │   ├── deals.py
│   │   ├── due_diligence.py
│   │   ├── organizations.py
│   │   └── users.py
│   ├── schemas/             # Pydantic validation schemas
│   ├── services/            # Business logic layer
│   │   ├── analytics/       # Analytics services
│   │   ├── marketing/       # Marketing automation
│   │   ├── podcast/         # Podcast production
│   │   └── community/       # Community features
│   ├── integrations/        # External service integrations
│   ├── intelligence/        # AI/ML capabilities
│   ├── coordination/        # Multi-agent coordination
│   └── utils/               # Utility functions
├── alembic/                 # Database migrations
│   ├── versions/            # Migration scripts
│   └── env.py              # Alembic configuration
├── requirements.txt         # Python dependencies
├── alembic.ini             # Alembic configuration
├── .env.example            # Environment variable template
└── README_CLERK_BACKEND.md  # Clerk integration docs
```

---

## Critical Directories

### API Layer (`app/api/` & `app/routers/`)

**Purpose**: RESTful API endpoints and route handlers
**Key Files**:

- `app/api/v1/` - Version 1 API (31 modules)
- `app/routers/` - Core routers (4 modules)
  **Integration Points**: Calls services layer, uses authentication middleware

### Model Layer (`app/models/`)

**Purpose**: SQLAlchemy ORM models defining database schema
**Key Files**:

- `base.py` - Base model with common fields
- `organization.py` - Multi-tenant organization model
- `user.py` - User management
- `deal.py` - Deal tracking
- `documents.py` - Document management
- `negotiations.py` - Term sheets & deal structuring
  **Note**: 22 model modules defining comprehensive M&A domain

### Authentication (`app/auth/`)

**Purpose**: Clerk authentication & multi-tenant isolation
**Key Features**:

- Clerk user/org synchronization
- Webhook handling for user events
- Tenant-aware database queries
- Role-based access control (RBAC)

### Services Layer (`app/services/`)

**Purpose**: Business logic and domain services
**Modules**:

- `analytics/` - Data analysis & reporting
- `marketing/` - Marketing automation
- `podcast/` - Podcast production
- `community/` - Community management

### AI Agents (`app/agents/`)

**Purpose**: Intelligent automation and AI-powered features
**Agents**:

- `deal_sourcing_agent.py` - Automated deal discovery
- `acquisition_agent.py` - M&A opportunity analysis
- `content_agent.py` - Content generation
- `deal_execution_agent.py` - Deal workflow automation
- `integration_agent.py` - Integration management

---

## Development Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ with pgvector extension
- pip or poetry for dependency management
- Clerk account for authentication
- Stripe account for payments (optional)

### Environment Setup

1. Copy `.env.example` to `.env`
2. Configure required variables:
   ```
   CLERK_SECRET_KEY=<your-clerk-secret>
   DATABASE_URL=postgresql://user:pass@localhost/dbname
   CLERK_WEBHOOK_SECRET=<webhook-secret>
   ```

### Installation

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head  # Run migrations
```

### Running Locally

```bash
uvicorn app.main:app --reload --port 8000
```

### API Documentation

- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

---

## Integration Points

### External Services

- **Clerk**: User authentication & organization management
- **Stripe**: Payment processing & subscriptions
- **Anthropic Claude**: AI-powered agents & analysis
- **OpenAI**: Additional AI capabilities
- **AWS S3**: Document storage & retrieval

### Internal Integration

- **Frontend**: React SPA consuming REST API
- **Database**: PostgreSQL with async SQLAlchemy
- **Webhooks**: Clerk user/org synchronization
- **Background Tasks**: (Planned) Celery + Redis

---

## Key Features Implemented

### Core M&A Features

✅ Deal Management (tracking, pipeline, stages)
✅ Due Diligence (checklists, document management)
✅ Document Management (versioning, approvals, collaboration)
✅ Negotiations (term sheets, deal structuring)
✅ Analytics (pipeline metrics, advanced reporting)
✅ Teams (workflow orchestration, permissions)

### Platform Features

✅ Multi-tenant Architecture (organization-based isolation)
✅ Clerk Authentication (SSO, user management)
✅ AI Agents (deal sourcing, content generation)
✅ Integrations (multi-platform connectivity)
✅ Advanced Analytics (data export, reporting)

### Infrastructure

✅ FastAPI async framework
✅ PostgreSQL with pgvector
✅ Alembic migrations
✅ Comprehensive API documentation
✅ Middleware stack (auth, CORS, tenant isolation)

---

## Technical Debt & Improvements

### Identified Issues

⚠️ Some API modules temporarily disabled (see `main.py` comments)
⚠️ Legacy `models.py` conflicts with new organization/user models
⚠️ Payment processing needs StripeCustomer/Payment/WebhookEvent models
⚠️ Arbitrage module requires pandas dependency (currently commented out)

### Future Enhancements

- Background task processing (Celery + Redis)
- Web scraping capabilities (BeautifulSoup, Selenium)
- Advanced ML/AI features (scikit-learn)
- Media processing (movie py, ffmpeg)
- Transcription services (Whisper, AssemblyAI)

---

## Testing

### Test Files Location

- Integration tests: `backend/test_*.py`
- Sprint verification: `backend/sprint*_verification.py`

### Running Tests

```bash
pytest
pytest -v  # Verbose output
pytest backend/test_sprint3_complete.py  # Specific test
```

---

## Deployment

### Production Considerations

- Environment variables must be configured
- Database migrations must be run
- Clerk webhooks must be configured
- Stripe webhooks must be set up (if payments enabled)
- CORS origins must be properly configured

### Deployment Script

```bash
./deploy.sh  # Automated deployment script
```

---

## Documentation Status

✅ **Complete**:

- Project overview
- Technology stack
- Architecture pattern
- Directory structure
- Development quick start

📝 **To Be Generated** (run Deep scan for these):

- Complete API endpoint catalog
- Detailed data model documentation
- Comprehensive development guide
- API integration examples
- Deployment architecture

---

## Next Steps

### For AI-Assisted Development

1. Use this documentation as context for new features
2. Reference model files when creating new endpoints
3. Follow existing patterns in API modules
4. Maintain tenant isolation in all queries

### For Team Onboarding

1. Read this index for project overview
2. Review architecture documentation
3. Set up local development environment
4. Explore API documentation at `/api/docs`

### For Epic Planning

1. Use this baseline as reference for current state
2. Identify gaps and improvement areas
3. Plan new features with architectural consistency
4. Reference existing patterns for implementation

---

**Documentation Tool**: BMad Method document-project workflow v1.2.0
**Scan Type**: Quick (pattern-based analysis)
**Generated**: October 12, 2025
**Next Update**: Run Deep scan when detailed API/model docs needed

For complete documentation generation, run:

```bash
bmad analyst document-project
# Select: Deep scan
# Directory: backend/
```
