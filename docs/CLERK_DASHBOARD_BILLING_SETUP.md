# Clerk Dashboard Billing Setup Guide

**Date:** October 12, 2025
**Purpose:** Step-by-step guide to configure billing in Clerk Dashboard
**Approach:** Clerk Native Billing with Stripe Integration

## Prerequisites

Before starting, ensure you have:

- ✅ Clerk account with application created
- ✅ Stripe account (test or live mode)
- ✅ Admin access to both dashboards
- ✅ Understanding of your pricing structure

## Overview

This guide will walk you through:

1. Connecting your Stripe account to Clerk
2. Creating pricing plans (3 tiers × 2 intervals = 6 plans)
3. Configuring features and entitlements
4. Setting up 14-day free trials
5. Enabling billing in your application
6. Testing the complete flow

---

## Part 1: Connect Stripe to Clerk

### Step 1: Navigate to Billing Configuration

1. Log in to [Clerk Dashboard](https://dashboard.clerk.com)
2. Select your application
3. Go to **Configure** → **Billing** (left sidebar)
4. Click **"Connect Stripe"**

### Step 2: Authorize Stripe Connection

1. You'll be redirected to Stripe authorization page
2. Log in to your Stripe account
3. Select the Stripe account to connect
4. Click **"Connect"** to authorize

**Important:**

- Use **Test Mode** for development/testing
- Use **Live Mode** for production
- You can connect both test and live Stripe accounts

### Step 3: Verify Connection

After authorization:

- ✅ You should see "Stripe Connected" in Clerk Dashboard
- ✅ Clerk will have permission to create products/prices in Stripe
- ✅ You can now create billing plans

---

## Part 2: Create Pricing Plans

You'll create **6 plans total** (3 tiers × 2 billing intervals):

### Plan 1: Solo Dealmaker (Monthly)

1. In Clerk Dashboard → Billing → Plans
2. Click **"Create Plan"**

**Configuration:**

```
Plan Name: Solo Dealmaker (Monthly)
Description: Perfect for individual professionals starting their M&A journey
Price: $279.00
Currency: USD
Billing Interval: Monthly
Trial Period: 14 days (enable checkbox)
```

**Features to Add:**
Click "Add Feature" for each:

```
- max_users = 3
- max_deals = 10
- max_storage_gb = 50
- analytics_level = basic
- support_level = email
- deal_pipeline = true
- document_management = true
```

**Entitlements/Permissions:**

```
- tier:solo_dealmaker
- feature:deal_pipeline
- feature:document_management
```

3. Click **"Create Plan"**

### Plan 2: Solo Dealmaker (Annual)

1. Click **"Create Plan"** again

**Configuration:**

```
Plan Name: Solo Dealmaker (Annual)
Description: Perfect for individual professionals - Save 17% with annual billing
Price: $2,790.00
Currency: USD
Billing Interval: Yearly
Trial Period: 14 days (enable checkbox)
```

**Features:** (Same as monthly)

```
- max_users = 3
- max_deals = 10
- max_storage_gb = 50
- analytics_level = basic
- support_level = email
- deal_pipeline = true
- document_management = true
- annual_billing = true
```

**Entitlements:** (Same as monthly)

```
- tier:solo_dealmaker
- feature:deal_pipeline
- feature:document_management
```

3. Click **"Create Plan"**

### Plan 3: Growth Firm (Monthly)

**Configuration:**

```
Plan Name: Growth Firm (Monthly)
Description: For growing M&A teams and mid-size firms
Price: $798.00
Currency: USD
Billing Interval: Monthly
Trial Period: 14 days (enable checkbox)
```

**Features:**

```
- max_users = 15
- max_deals = 50
- max_storage_gb = 200
- analytics_level = advanced
- support_level = priority
- deal_pipeline = true
- document_management = true
- ai_insights = true
- team_collaboration = true
- workflow_automation = true
- due_diligence = true
```

**Entitlements:**

```
- tier:growth_firm
- feature:deal_pipeline
- feature:document_management
- feature:ai_insights
- feature:team_collaboration
- feature:workflow_automation
- feature:advanced_analytics
- feature:due_diligence
```

### Plan 4: Growth Firm (Annual)

**Configuration:**

```
Plan Name: Growth Firm (Annual)
Description: For growing M&A teams - Save 17% with annual billing
Price: $7,980.00
Currency: USD
Billing Interval: Yearly
Trial Period: 14 days (enable checkbox)
```

**Features:** (Same as monthly + annual_billing = true)

**Entitlements:** (Same as monthly)

### Plan 5: Enterprise (Monthly)

**Configuration:**

```
Plan Name: Enterprise (Monthly)
Description: For large firms and investment banks
Price: $1,598.00
Currency: USD
Billing Interval: Monthly
Trial Period: 14 days (enable checkbox)
```

**Features:**

```
- max_users = -1 (unlimited)
- max_deals = -1 (unlimited)
- max_storage_gb = 1024
- analytics_level = custom
- support_level = dedicated
- deal_pipeline = true
- document_management = true
- ai_insights = true
- team_collaboration = true
- workflow_automation = true
- due_diligence = true
- white_labeling = true
- sso_integration = true
- custom_integrations = true
- audit_logs = true
- advanced_security = true
```

**Entitlements:**

```
- tier:enterprise
- feature:deal_pipeline
- feature:document_management
- feature:ai_insights
- feature:team_collaboration
- feature:workflow_automation
- feature:advanced_analytics
- feature:due_diligence
- feature:white_labeling
- feature:sso_integration
- feature:custom_integrations
- feature:audit_logs
- feature:advanced_security
```

### Plan 6: Enterprise (Annual)

**Configuration:**

```
Plan Name: Enterprise (Annual)
Description: For large firms - Save 17% with annual billing
Price: $15,980.00
Currency: USD
Billing Interval: Yearly
Trial Period: 14 days (enable checkbox)
```

**Features:** (Same as monthly + annual_billing = true)

**Entitlements:** (Same as monthly)

---

## Part 3: Configure Plan Display Order

1. In Plans page, you'll see all 6 plans listed
2. Drag and drop to reorder:
   - Solo Dealmaker (Monthly/Annual)
   - Growth Firm (Monthly/Annual) - Mark as "Recommended"
   - Enterprise (Monthly/Annual)
3. Mark "Growth Firm" plans as **"Most Popular"**

---

## Part 4: Configure Billing Settings

### General Settings

1. Go to **Billing** → **Settings**

**Configuration:**

```
Trial Behavior:
  ☑ Require credit card to start trial
  ☑ Auto-charge after trial ends
  ☑ Send trial expiration reminders (3 days before)

Cancellation:
  ○ Effective immediately
  ● At end of billing period (recommended)

Notifications:
  ☑ Send payment success emails
  ☑ Send payment failure emails
  ☑ Send subscription change emails
  ☑ Send cancellation confirmation
```

### Tax Settings

```
Tax Collection: (Optional)
  ☐ Enable automatic tax calculation
  Note: Currently limited support - check Clerk docs
```

### Invoice Settings

```
Invoice Branding:
  Company Name: M&A SaaS Platform
  Support Email: support@ma-platform.com
  Logo: [Upload your logo]
```

---

## Part 5: Enable Billing in Application

### Step 1: Update Frontend Environment

Ensure these environment variables are set:

**frontend/.env.local:**

```env
VITE_CLERK_PUBLISHABLE_KEY=pk_test_[YOUR_KEY]
```

### Step 2: Install/Update Clerk Package

```bash
cd frontend
pnpm install @clerk/clerk-react@latest
```

**Recommended:** Pin to specific version to avoid beta breaking changes:

```bash
pnpm install @clerk/clerk-react@5.51.0
```

### Step 3: Import PricingTable Component

In your pricing page:

```jsx
import { PricingTable } from '@clerk/clerk-react';

export default function PricingPage() {
  return (
    <div>
      <PricingTable />
    </div>
  );
}
```

### Step 4: Configure Clerk Provider

Ensure ClerkProvider wraps your app (should already be set up):

```jsx
import { ClerkProvider } from '@clerk/clerk-react';

function App() {
  return (
    <ClerkProvider publishableKey={process.env.VITE_CLERK_PUBLISHABLE_KEY}>
      {/* Your app */}
    </ClerkProvider>
  );
}
```

---

## Part 6: Set Up Webhooks (Optional but Recommended)

### Why Webhooks?

Webhooks allow your backend to:

- Sync subscription data to your database
- Update user permissions based on plan
- Send custom notifications
- Track subscription lifecycle

### Configuration

1. In Clerk Dashboard → Webhooks
2. Click **"Add Endpoint"**

**Configuration:**

```
Endpoint URL: https://your-backend.com/api/webhooks/clerk
Description: Subscription events
```

**Events to Subscribe:**

```
☑ subscription.created
☑ subscription.updated
☑ subscription.deleted
☑ subscription.trial_will_end
☑ user.updated
```

3. Copy the **Signing Secret**
4. Add to backend `.env`:

```env
CLERK_WEBHOOK_SECRET=whsec_[YOUR_SECRET]
```

### Backend Webhook Handler

```python
# backend/app/api/webhooks/clerk.py

@router.post("/webhooks/clerk")
async def clerk_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    headers = request.headers

    # Verify webhook signature
    webhook = Webhook(os.getenv("CLERK_WEBHOOK_SECRET"))
    try:
        event = webhook.verify(payload, headers)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]

    if event_type == "subscription.created":
        user_id = event["data"]["user_id"]
        plan_data = event["data"]["plan"]
        # Update user subscription in database

    elif event_type == "subscription.updated":
        # Handle subscription changes
        pass

    elif event_type == "subscription.deleted":
        # Handle cancellation
        pass

    return {"success": True}
```

---

## Part 7: Testing the Integration

### Test in Development

1. **Start your development server:**

   ```bash
   cd frontend
   pnpm run dev
   ```

2. **Navigate to pricing page:**

   ```
   http://localhost:5173/pricing
   ```

3. **Verify Clerk Pricing Table appears:**
   - All 6 plans should be visible
   - Monthly/Annual toggle should work
   - Prices should display correctly
   - Features should be listed

### Test Subscription Flow

1. **Click "Subscribe" on Solo Dealmaker (Monthly)**
2. **Sign up/Sign in** with Clerk
3. **Complete Stripe checkout:**
   - Use test card: `4242 4242 4242 4242`
   - Expiry: Any future date (12/34)
   - CVC: Any 3 digits (123)
   - ZIP: Any 5 digits (12345)
4. **Verify trial starts:**
   - Should see "14-day trial" in confirmation
   - Access to all Solo Dealmaker features
5. **Check subscription in Clerk Dashboard:**
   - Go to Users → [Your User] → Subscriptions
   - Should see active trial

### Test in Stripe Dashboard

1. Log in to Stripe Dashboard
2. Go to **Customers**
3. Find your test customer
4. Verify:
   - Subscription created
   - Status: `trialing`
   - Trial end date: 14 days from now
   - Plan: Solo Dealmaker (Monthly)
   - Amount: $279.00

### Test Feature Access

Use Clerk's `has()` helper:

```jsx
import { useUser } from '@clerk/clerk-react';

function AdvancedAnalytics() {
  const { user } = useUser();

  // Check if user has advanced analytics feature
  if (!user?.has?.({ permission: 'feature:advanced_analytics' })) {
    return <UpgradePrompt />;
  }

  return <AnalyticsDashboard />;
}
```

---

## Part 8: Production Deployment

### Pre-Deployment Checklist

- [ ] All 6 plans created in Clerk Dashboard (Live mode)
- [ ] Stripe live account connected
- [ ] Webhooks configured with production URL
- [ ] Frontend using Clerk live publishable key
- [ ] Backend using Clerk live secret key
- [ ] Webhook secrets configured in production
- [ ] Test subscription flow in staging
- [ ] Email notifications working

### Switch to Live Mode

1. **In Clerk Dashboard:**
   - Toggle from **Test** to **Live** mode (top right)
   - Repeat all plan creation steps in Live mode

2. **Update Environment Variables:**

**Production Frontend:**

```env
VITE_CLERK_PUBLISHABLE_KEY=pk_live_[YOUR_LIVE_KEY]
```

**Production Backend:**

```env
CLERK_SECRET_KEY=sk_live_[YOUR_LIVE_KEY]
CLERK_WEBHOOK_SECRET=whsec_[YOUR_LIVE_SECRET]
```

3. **Deploy to Production:**

   ```bash
   git add .
   git commit -m "feat: Enable Clerk Billing with annual options"
   git push origin master
   ```

4. **Verify Deployment:**
   - Visit production pricing page
   - Test with real card (small amount)
   - Immediately cancel to avoid charge
   - Verify all flows work

---

## Troubleshooting

### Issue: PricingTable Not Showing

**Possible Causes:**

1. Clerk publishable key not set
2. No plans created in Clerk Dashboard
3. Billing not enabled for application

**Solution:**

- Verify `VITE_CLERK_PUBLISHABLE_KEY` is set
- Check Clerk Dashboard → Billing → Plans
- Ensure Stripe is connected

### Issue: "Billing not available" Error

**Cause:** Billing feature not enabled

**Solution:**

1. Go to Clerk Dashboard → Billing
2. Click "Enable Billing"
3. Complete Stripe connection

### Issue: Trial Not Starting

**Cause:** Credit card requirement setting

**Solution:**

- Check Billing Settings → Trial Behavior
- Ensure "Require credit card" is enabled

### Issue: Wrong Plans Showing

**Cause:** Mode mismatch (test vs live)

**Solution:**

- Verify you're in correct mode (test/live)
- Ensure frontend key matches mode
- Check plans exist in current mode

---

## Monitoring and Analytics

### In Clerk Dashboard

**View Subscription Metrics:**

1. Go to **Analytics** → **Billing**
2. See:
   - Active subscriptions
   - MRR (Monthly Recurring Revenue)
   - ARR (Annual Recurring Revenue)
   - Churn rate
   - Trial conversion rate

### In Stripe Dashboard

**View Payment Data:**

1. Go to **Billing** → **Subscriptions**
2. Monitor:
   - Payment success rate
   - Failed payments
   - Dunning management
   - Revenue reports

---

## Best Practices

### 1. **Always Test in Test Mode First**

- Create test subscriptions
- Test all flows thoroughly
- Only switch to live when confident

### 2. **Pin SDK Versions**

- Clerk Billing is in beta
- Pin `@clerk/clerk-react` version
- Review changelogs before upgrading

### 3. **Monitor Trial Conversions**

- Track trial→paid conversion rate
- Optimize trial length if needed
- Send reminder emails before trial ends

### 4. **Handle Failed Payments**

- Set up Stripe dunning
- Send payment failure notifications
- Provide grace period before downgrade

### 5. **Regular Backups**

- Export subscription data regularly
- Keep backup of plan configurations
- Document all custom settings

---

## Support Resources

- **Clerk Billing Docs:** https://clerk.com/docs/billing/overview
- **Clerk Dashboard:** https://dashboard.clerk.com
- **Stripe Dashboard:** https://dashboard.stripe.com
- **Clerk Discord:** https://clerk.com/discord
- **Support Email:** support@clerk.com

---

## Summary

You've now:
✅ Connected Stripe to Clerk
✅ Created 6 pricing plans (3 tiers × 2 intervals)
✅ Configured 14-day free trials
✅ Set up features and entitlements
✅ Integrated PricingTable component
✅ Configured webhooks
✅ Tested the complete flow
✅ Deployed to production

**Next Steps:**

1. Monitor subscription metrics
2. Gather user feedback
3. Optimize pricing based on data
4. Add more features to higher tiers

---

**Last Updated:** October 12, 2025
**Version:** 1.0
**Status:** Ready for Implementation
