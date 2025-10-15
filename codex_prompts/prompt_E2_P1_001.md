# BMAD v6 Codex Prompt: E2.P1.001 - Implement Deal Creation Interface

## 🎯 Story Context

- Epic: Deal Management
- Priority: P1 - HIGH
- Size: L (3-4 days)
- Sprint: 2 (2025-10-21 → 2025-10-27)

## 👤 User Story

As a M&A professional, I want to create and configure new deals, so that I can track transactions comprehensively.

## ✅ Acceptance Criteria

Given I am logged in, when I submit the deal creation form, then A deal record is created and visible in pipeline, and:

- Form validations enforce required data
- Files attach successfully
- User redirected to detail page
- Event logged for analytics

## 🔧 Implementation Guidelines

### Frontend

# Use React Hook Form + Zod for validation

# Handle submission, error, and success states

# Provide user feedback (loading, toasts)

### Backend

# Create/update FastAPI endpoints in backend/app/routers/

# Add request/response models in backend/app/schemas/

# Implement validation, error handling, and status codes

# Update OpenAPI documentation via FastAPI router metadata

# Update SQLAlchemy models in backend/app/models/

# Create Alembic migration: alembic revision --autogenerate -m 'describe change'

# Apply migration: alembic upgrade head

# Update CRUD/service layer to use new fields

### Integrations

# Integration validation per requirements: File storage service

## 🛠️ Execution Steps

1. Checkout feature branch and ensure clean working tree.
2. Implement frontend components/pages per guidelines.
3. Implement backend logic, migrations, and services.
4. Integrate external services and update configuration.
5. Run unit/integration tests and linting.
6. Capture screenshots/demos and update documentation.
7. Open PR summarizing changes and attach test results.

## ✅ Testing Plan

### Unit Tests

- Field validation
- API create

### Integration Tests

- File storage integration
- Activity log

### User Tests

- Usability review

### Performance Tests

- Submission < 3s
- Upload progress
- Run full backend + frontend test suites

## 🚀 Deployment Checklist

- [ ] Merge PR after approvals
- [ ] Deploy to staging and run smoke tests
- [ ] Monitor logs/metrics post-deploy
- [ ] Announce availability to stakeholders
