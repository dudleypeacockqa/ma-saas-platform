# Alerting Setup Guide

Complete guide to setting up Slack, email, and webhook alerts for your M&A SaaS Platform.

## Overview

The application includes built-in alerting for:

- **High Error Rates**: When error rate exceeds 5%
- **Slow Response Times**: When responses exceed 1000ms
- **High Memory Usage**: When heap memory exceeds 500MB
- **Service Health**: Automatic monitoring and alerts

## Alert Channels

### 1. Slack Alerts (Recommended)

Slack integration provides real-time notifications in your team channel.

#### Step 1: Create Slack Webhook

1. Go to your Slack workspace
2. Navigate to **Apps** → **Incoming Webhooks**
3. Click **Add to Slack**
4. Select channel for alerts (e.g., `#platform-alerts`)
5. Copy the Webhook URL

#### Step 2: Configure in Render

1. Go to https://dashboard.render.com/web/srv-d3ihptbipnbc73e72ne0
2. Navigate to **Environment** tab
3. Add environment variable:
   ```
   Key: ALERT_WEBHOOK_URL
   Value: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```
4. Click **Save Changes**
5. Service will auto-deploy with new configuration

#### Alert Format

```
🚨 *High Error Rate*: Error rate is 7.50%
───────────────────────────
threshold: 5%
current: 7.50%
totalErrors: 15
totalRequests: 200
───────────────────────────
M&A SaaS Platform
```

### 2. Discord Alerts

Discord webhooks work similarly to Slack.

#### Step 1: Create Discord Webhook

1. Open Discord server settings
2. Go to **Integrations** → **Webhooks**
3. Click **New Webhook**
4. Name it "Platform Alerts"
5. Select channel
6. Copy webhook URL

#### Step 2: Configure

Add to Render environment:

```
ALERT_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL
```

### 3. Email Alerts

Email alerts are sent via the backend API.

#### Step 1: Configure Email Service

The backend must have email sending capability. Add to backend environment:

```
# Backend .env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASS=YOUR_SENDGRID_API_KEY
ALERT_FROM_EMAIL=alerts@100daysandbeyond.com
```

#### Step 2: Configure Frontend

Add to frontend environment in Render:

```
BACKEND_API_URL=https://ma-saas-backend.onrender.com
ALERT_EMAIL=your-team@company.com
```

### 4. Custom Webhooks

You can send alerts to any webhook endpoint.

#### Example: Microsoft Teams

```javascript
// Custom webhook format
{
  "@type": "MessageCard",
  "@context": "https://schema.org/extensions",
  "summary": "Platform Alert",
  "themeColor": "FF0000",
  "title": "🚨 High Error Rate",
  "sections": [{
    "facts": [
      { "name": "Threshold", "value": "5%" },
      { "name": "Current", "value": "7.50%" }
    ]
  }]
}
```

## Performance Budgets

Default thresholds can be customized in the code:

```javascript
// frontend/server.js
const performanceBudgets = {
  maxResponseTime: 1000, // 1 second
  errorRateThreshold: 5, // 5% error rate
  memoryThreshold: 500 * 1024 * 1024, // 500 MB
  minUptime: 60 * 60 * 1000, // 1 hour
};
```

### Customizing Budgets

To adjust thresholds:

1. Edit `frontend/server.js`
2. Modify the `performanceBudgets` object
3. Commit and push changes
4. Render will auto-deploy

#### Recommended Thresholds

**Production (High Traffic)**:

```javascript
{
  maxResponseTime: 500,         // 500ms
  errorRateThreshold: 1,        // 1% error rate
  memoryThreshold: 400 * 1024 * 1024, // 400 MB
}
```

**Development**:

```javascript
{
  maxResponseTime: 2000,        // 2 seconds
  errorRateThreshold: 10,       // 10% error rate
  memoryThreshold: 1024 * 1024 * 1024, // 1 GB
}
```

## Alert Cooldown

To prevent alert spam, there's a 5-minute cooldown between alerts.

### Adjusting Cooldown

Edit `frontend/server.js`:

```javascript
alerts: {
  lastAlertTime: 0,
  alertCooldown: 5 * 60 * 1000, // 5 minutes
}
```

Change to your preferred cooldown:

- `1 * 60 * 1000` = 1 minute
- `10 * 60 * 1000` = 10 minutes
- `30 * 60 * 1000` = 30 minutes

## Testing Alerts

### Test Slack Webhook

```bash
curl -X POST YOUR_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "🚨 Test Alert",
    "attachments": [{
      "color": "danger",
      "fields": [{
        "title": "Test",
        "value": "This is a test",
        "short": true
      }]
    }]
  }'
```

### Trigger Test Alert

Create high error rate to test:

```bash
# Generate 100 requests to non-existent endpoint
for i in {1..100}; do
  curl https://ma-saas-platform.onrender.com/non-existent &
done
wait
```

## Alert Types

### 1. High Error Rate

**Trigger**: Error rate exceeds threshold
**Default**: 5%
**Data Included**:

- Current error rate
- Threshold
- Total errors
- Total requests

### 2. Slow Response Time

**Trigger**: Maximum response time exceeds budget
**Default**: 1000ms
**Data Included**:

- Current max response time
- Threshold
- Average response time

### 3. High Memory Usage

**Trigger**: Heap memory exceeds threshold
**Default**: 500 MB
**Data Included**:

- Current heap used
- Threshold
- Total RSS memory

## Monitoring Dashboard

Access real-time metrics without alerts:

**URL**: https://ma-saas-platform.onrender.com/metrics

**Endpoint**: `GET /metrics`

**Response**:

```json
{
  "uptime": { "seconds": 3600, "human": "1h 0m 0s" },
  "requests": {
    "total": 1000,
    "byStatus": { "2xx": 950, "4xx": 45, "5xx": 5 }
  },
  "performance": {
    "avgResponseTime": 45.2,
    "maxResponseTime": 523,
    "minResponseTime": 12
  },
  "errors": {
    "count": 5,
    "recent": [...]
  },
  "memory": {...},
  "cpu": {...}
}
```

## Integration with Monitoring Tools

### Datadog

```javascript
// Send metrics to Datadog
const dd = require('dd-trace');
dd.init();

// In server.js, after metrics update
dd.dogstatsd.increment('requests.total');
dd.dogstatsd.histogram('response.time', duration);
```

### New Relic

```javascript
// Add to server.js
require('newrelic');

// Metrics are automatically collected
```

### Prometheus

```javascript
// Install prom-client
npm install prom-client

// Add to server.js
const promClient = require('prom-client');
const register = new promClient.Registry();

// Expose metrics endpoint
app.get('/prometheus', (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(register.metrics());
});
```

## Best Practices

### 1. Alert Fatigue

- Set appropriate thresholds
- Use cooldown periods
- Group related alerts
- Prioritize critical alerts

### 2. On-Call Rotation

- Use PagerDuty or Opsgenie integration
- Route critical alerts to on-call person
- Non-critical to team channel

### 3. Alert Escalation

```
Level 1: Slack notification (warning)
Level 2: Email to team (error rate > 10%)
Level 3: PagerDuty alert (service down)
```

### 4. Regular Testing

- Test alerts monthly
- Verify all channels work
- Update contact information

## Troubleshooting

### Alerts Not Firing

1. Check environment variables are set:

   ```bash
   # In Render dashboard, verify
   ALERT_WEBHOOK_URL
   BACKEND_API_URL
   ALERT_EMAIL
   ```

2. Check server logs:

   ```bash
   # Look for alert messages
   grep "ALERT" logs
   ```

3. Verify webhook URL:
   ```bash
   curl -X POST $ALERT_WEBHOOK_URL \
     -H 'Content-Type: application/json' \
     -d '{"text": "Test"}'
   ```

### Too Many Alerts

1. Increase cooldown period
2. Raise thresholds
3. Filter specific error types

### Missing Alerts

1. Lower thresholds temporarily
2. Check metrics endpoint
3. Verify performance budgets

## Alert Runbook

### High Error Rate Alert

1. Check `/metrics` endpoint
2. Review recent errors
3. Check backend logs
4. Verify database connectivity
5. Check third-party services (Clerk, Stripe)

### Slow Response Time

1. Check server load
2. Review slow queries
3. Check database performance
4. Verify caching is working
5. Consider scaling

### High Memory Usage

1. Check for memory leaks
2. Review long-running operations
3. Restart service if needed
4. Increase memory limits
5. Optimize code

## Support

For issues:

- Slack: #platform-alerts
- Email: dev-team@100daysandbeyond.com
- Dashboard: https://ma-saas-platform.onrender.com/metrics
