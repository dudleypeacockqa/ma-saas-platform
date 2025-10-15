# BMAD v6 Codex Prompt: E1.P0.001 - Restore Customer Access to Platform Landing Page

## 🎯 Story Context

- Epic: Customer Onboarding
- Priority: P0 - CRITICAL
- Size: M (2-3 days)
- Sprint: 1 (2025-10-14 → 2025-10-20)

## 👤 User Story

As a Potential customer visiting the platform, I want to see a professional landing page with clear value proposition, so that I can understand the platform benefits and sign up for services.

## ✅ Acceptance Criteria

Given I navigate to https://ma-saas-platform.onrender.com, when the page loads, then I see a professional landing page with navigation, hero section, and clear CTAs, and:

- Page load times under 3 seconds
- All images/assets render correctly
- Layout is responsive on mobile
- Navigation links to login and pricing

## 🔧 Implementation Guidelines

### Frontend

# Verify responsive breakpoints (mobile/tablet/desktop)

# Add touch-friendly interactions where applicable

# Optimize for Core Web Vitals

### Backend

# Backend implementation per requirements: Ensure static hosting / CDN config

### Integrations

# Configure CDN/asset pipeline

# Validate caching headers and performance

# Optimize images and static resources

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

- Component rendering
- Navigation links
- Responsive layout

### Integration Tests

- Page load performance
- Asset delivery

### User Tests

- Manual QA on desktop/mobile

### Performance Tests

- Lighthouse score >90
- TTFB < 500ms
- Run full backend + frontend test suites

## 🚀 Deployment Checklist

- [ ] Merge PR after approvals
- [ ] Deploy to staging and run smoke tests
- [ ] Monitor logs/metrics post-deploy
- [ ] Announce availability to stakeholders
