# BMAD v6 Codex Prompt: E3.P1.001 - Implement AI-Powered Deal Analysis Interface

## 🎯 Story Context

- Epic: AI Intelligence
- Priority: P1 - HIGH
- Size: L (3-4 days)
- Sprint: 3 (2025-10-28 → 2025-11-03)

## 👤 User Story

As a M&A professional, I want to request AI-driven deal analysis, so that I can make data-driven decisions.

## ✅ Acceptance Criteria

Given Deal contains required financial data, when I request analysis, then An AI report returns with valuation, risks, recommendations, and:

- DCF outputs included
- Risk scoring explained
- Comparable analysis displayed
- PDF export works

## 🔧 Implementation Guidelines

### Frontend

# Create React components in frontend/src/components/ or features/

# Style with Tailwind/MUI and ensure accessibility

# Implement state management and props typing

### Backend

# Backend implementation per requirements: AI service orchestration, report persistence

### Integrations

# Configure AI service API keys and client

# Test prompt/response flow, handle errors

# Add streaming responses where needed

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

- Request payload
- Response parsing

### Integration Tests

- AI API integration
- PDF export

### User Tests

- Report review with SMEs

### Performance Tests

- Analysis < 30s
- PDF < 10s
- Run full backend + frontend test suites

## 🚀 Deployment Checklist

- [ ] Merge PR after approvals
- [ ] Deploy to staging and run smoke tests
- [ ] Monitor logs/metrics post-deploy
- [ ] Announce availability to stakeholders
