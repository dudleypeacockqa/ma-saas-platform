# Onboarding Automation Blueprint

## In-App Journey
1. **Checklist Activation** – OnboardingChecklist renders for every authenticated user on /dashboard.
   - Progress persisted in localStorage keyed by Clerk user ID.
   - Events: onboarding_connect_data, onboarding_create_deal, onboarding_invite_team, onboarding_upload_document, onboarding_schedule_strategy.
   - Completion of all tasks raises 	rackEvent('onboarding_schedule_strategy', { action: 'complete' }) enabling concierge outreach.

2. **Progress Signals**
   - When a step is marked complete, analytics emit GA/Segment events with 	ask_id, enabling funnel dashboards to track activation.
   - Segment can trigger downstream workflows (e.g., Customer.io, HubSpot) based on these events.

## Email / Lifecycle Cadence
| Timing | Trigger | Subject / Content | Goal |
| --- | --- | --- | --- |
| Day 0 | 	rial_started | "Welcome to 100 Days & Beyond" overview, link to checklist | Encourage first login and data connection |
| Day 1 | onboarding_connect_data incomplete | Best practices for connecting accounting + case study | Accelerate data sync |
| Day 3 | No onboarding_create_deal event | Video walkthrough of pipeline setup, CTA "Create first deal" | Drive core action |
| Day 5 | Invite not sent (onboarding_invite_team pending) | Collaboration benefits, highlight permissions + security | Encourage team invites |
| Day 7 | Completed =3 steps | Share AI insights demo, promote strategy session booking | Upsell to Growth plan |
| Day 10 | onboarding_schedule_strategy incomplete | Offer office hours with CSM | Increase engagement |
| Day 14 | Checklist complete | Congratulate, share advanced resources, prompt upgrade if on Solo | Conversion push |
| Day 18 | Checklist incomplete | Escalation to Success team for manual outreach | Reduce churn risk |

## Automation Stack
- **Segment**: capture events and fan out to destinations.
- **Lifecycle Platform**: Customer.io or HubSpot sequences referencing Segment event triggers.
- **Calendaring**: integrate with Chili Piper/Calendly for schedule_strategy CTA.
- **CRM Sync**: push onboarding score into HubSpot/Salesforce for SDR prioritization.

## Metrics & Alerting
- Activation Rate = users completing =3 steps / total trials.
- Time-to-activation tracked by difference between 	rial_started and first completion event.
- Alert if activation rate falls below 60% over 7-day rolling window; create automated Slack notification for Success.

## Future Enhancements
- Replace localStorage with backend persistence (multi-device support).
- Auto-complete tasks via webhooks (e.g., Stripe subscription upgrade marks strategy call done).
- Personalized checklist ordering based on segment (PE vs Corporate Dev).

