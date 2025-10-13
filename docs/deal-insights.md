# Deal Insights Service

## Overview
The /api/deals/{deal_id}/insights endpoint returns heuristic AI-style guidance for each deal:
- **win_probability** – percentage likelihood of closing derived from stage, priority, risk signals, and probability metadata
- **confidence** – low/medium/high based on data completeness and probability
- **risk_factors** – aggregated risks (risk level, overdue close date, missing documents, key risk notes)
- **recommended_actions** – prioritized follow-up suggestions
- **next_milestone** – surfaced from deal metadata

## Inputs
- Relies on existing Deal record and related collections (documents, risk tags).
- No external API calls, so response is fast and deterministic.

## Monitoring & Evaluation
- Track event deal_insight_viewed (added in frontend) for adoption analytics.
- Add backend logging via Sentry breadcrumbs for insight generation failures.
- Recommended KPIs:
  - % of deals with insights viewed per week
  - Correlation between high-risk insights and eventual outcomes
  - Feedback loop: enable Success to flag incorrect recommendations

## Future Enhancements
- Blend with ML scores once predictive models are launched.
- Trigger Slack/Email alerts when win probability drops >15 pts week-over-week.
- Auto-refresh insights after key events (document upload, stage change) using webhooks.

