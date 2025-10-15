# BMAD v6 Codex Prompt: E2.P1.002 - Implement Deal Pipeline Kanban View

## 🎯 Story Context

- Epic: Deal Management
- Priority: P1 - HIGH
- Size: L (3-4 days)
- Sprint: 2 (2025-10-21 → 2025-10-27)

## 👤 User Story

As a M&A professional, I want to manage deals in a visual pipeline, so that I can monitor and update deal statuses efficiently.

## ✅ Acceptance Criteria

Given Deals exist, when I open pipeline view, then Deals appear in status columns with drag-and-drop, and:

- Status updates persist
- Column metrics show counts
- Filters/search behave correctly
- Real-time updates propagate to collaborators

## 🔧 Implementation Guidelines

### Frontend

# Create React components in frontend/src/components/ or features/

# Style with Tailwind/MUI and ensure accessibility

# Implement state management and props typing

### Backend

# Create/update FastAPI endpoints in backend/app/routers/

# Add request/response models in backend/app/schemas/

# Implement validation, error handling, and status codes

# Update OpenAPI documentation via FastAPI router metadata

### Integrations

# Integration validation per requirements: WebSocket push updates

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

- Column rendering
- Drag-drop handlers

### Integration Tests

- Status persistence
- Realtime sync

### User Tests

- Workflow usability

### Performance Tests

- View load < 2s
- Smooth drag
- Run full backend + frontend test suites

## 🚀 Deployment Checklist

- [ ] Merge PR after approvals
- [ ] Deploy to staging and run smoke tests
- [ ] Monitor logs/metrics post-deploy
- [ ] Announce availability to stakeholders
