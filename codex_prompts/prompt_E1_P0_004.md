# BMAD v6 Codex Prompt: E1.P0.004 - Create Welcome Dashboard for New Users

## 🎯 Story Context

- Epic: Customer Onboarding
- Priority: P0 - CRITICAL
- Size: M (2-3 days)
- Sprint: 2 (2025-10-21 → 2025-10-27)

## 👤 User Story

As a Newly registered user, I want to see a guided welcome dashboard, so that I can discover features quickly and finish onboarding.

## ✅ Acceptance Criteria

Given I login after registration, when I visit my dashboard, then I see welcome messaging, quick actions, and onboarding steps, and:

- Progress tracker updates
- Quick actions deep-link to core features
- Help / docs links accessible
- Analytics event logged

## 🔧 Implementation Guidelines

### Frontend

# Build dashboard layout with responsive grid

# Surface CTAs, onboarding checklist, and help links

# Instrument analytics events for interaction tracking

### Backend

# Create/update FastAPI endpoints in backend/app/routers/

# Add request/response models in backend/app/schemas/

# Implement validation, error handling, and status codes

# Update OpenAPI documentation via FastAPI router metadata

### Integrations

# Integration validation per requirements: Analytics instrumentation

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

- Dashboard rendering
- Progress updates

### Integration Tests

- Analytics events
- State persistence

### User Tests

- First-session walkthrough

### Performance Tests

- Dashboard load < 2s
- Run full backend + frontend test suites

## 🚀 Deployment Checklist

- [ ] Merge PR after approvals
- [ ] Deploy to staging and run smoke tests
- [ ] Monitor logs/metrics post-deploy
- [ ] Announce availability to stakeholders
