# BMAD v6 Codex Prompt: E4.P2.001 - Implement Community Networking Interface

## 🎯 Story Context

- Epic: Community Platform
- Priority: P2 - MEDIUM
- Size: L (3-4 days)
- Sprint: 3 (2025-10-28 → 2025-11-03)

## 👤 User Story

As a Platform member, I want to connect with other professionals, so that I can expand my network and share insights.

## ✅ Acceptance Criteria

Given I am verified, when I open community section, then I can search members, request connections, join discussions, and:

- Member directory supports filters
- Connection requests notify recipients
- Forums organized by topic
- Private messaging functional

## 🔧 Implementation Guidelines

### Frontend

# Create React components in frontend/src/components/ or features/

# Style with Tailwind/MUI and ensure accessibility

# Implement state management and props typing

# Add page under frontend/src/pages/

# Register route and navigation links

# Implement layout and breadcrumb metadata

### Backend

# Create/update FastAPI endpoints in backend/app/routers/

# Add request/response models in backend/app/schemas/

# Implement validation, error handling, and status codes

# Update OpenAPI documentation via FastAPI router metadata

### Integrations

# No external integrations required

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

- Search filtering
- Request lifecycle

### Integration Tests

- Messaging realtime
- Notification delivery

### User Tests

- Beta user feedback

### Performance Tests

- Directory load < 3s
- Message latency < 2s
- Run full backend + frontend test suites

## 🚀 Deployment Checklist

- [ ] Merge PR after approvals
- [ ] Deploy to staging and run smoke tests
- [ ] Monitor logs/metrics post-deploy
- [ ] Announce availability to stakeholders
