# Analytics Event Taxonomy

## Overview
This taxonomy standardizes revenue funnel and engagement events captured by GA4 and Segment. All events originate from rontend/src/lib/analytics.ts helpers and flow into GA4 (via gtag) and Segment destinations (Mixpanel, data warehouse, HubSpot).

## Core Events
| Event Name | Trigger | Properties |
| --- | --- | --- |
| page_view | Router navigation | page_path, page_title, utm_source, utm_campaign |
| cta_clicked | Primary CTA presses (trial, demo) | cta_location, cta_label, plan |
| 	rial_started | Clerk account created + Stripe checkout session initiated | plan, source, organization_id |
| 	rial_activated | First key action (deal created or doc uploaded) | plan, 	ime_to_activation, 	eam_size |
| subscription_upgraded | Stripe subscription transitions tiers | rom_plan, 	o_plan, nnual_value |
| checkout_abandoned | Checkout session created but no payment in 24h | plan, step |
| eature_adopted | First use of premium feature (AI insight, collaboration) | eature_name, plan, 	ime_from_signup |
| churn_warning | Usage health score drops below threshold | plan, health_score, eason |
| support_ticket_created | Zendesk/Intercom ticket sync | priority, category, esponse_time |

## User Identification
When a Clerk user signs in, identifyUser publishes traits:
- email
- irstName, lastName
- organizationIds
- ole (when available)

## Implementation Notes
- Environment variables: VITE_GA_MEASUREMENT_ID, VITE_SEGMENT_WRITE_KEY must be set for production/staging.
- Custom event calls should use 	rackEvent('event_name', { ... }) for consistency.
- Maintain this taxonomy when adding new destinations to Segment or warehouse tables.

## Reporting
- Funnel dashboards (visitor ? trial ? paid) pull directly from these events.
- Alerting thresholds (MRR drop, churn spike) rely on the accuracy of subscription_upgraded and churn_warning events.

