# Clerk Dashboard Configuration Guide

## Step-by-Step Setup for Subscription Billing

**Date**: October 12, 2025
**Status**: Ready for Configuration
**Estimated Time**: 30-45 minutes

---

## Prerequisites Checklist

Before starting, verify you have:

- ✅ Clerk account: https://dashboard.clerk.com
- ✅ Stripe account connected to Clerk
- ✅ Backend deployed at: https://ma-saas-backend.onrender.com
- ✅ Environment variables configured (already done)
- ✅ Webhook signing secret: `whsec_nBUKje3GC6+/XwtUtm1JERDNvXYnLgSO`

---

## Part 1: Enable Clerk Billing (5 minutes)

### Step 1: Access Billing Settings

1. Go to https://dashboard.clerk.com
2. Select your application: **"100daysandbeyond.com"**
3. In the left sidebar, click **"Billing"** (or "Subscriptions")
4. If you see a Beta banner, click **"Enable Clerk Billing (Beta)"**

### Step 2: Connect Stripe Account

1. Click **"Connect Stripe Account"** button
2. You'll be redirected to Stripe OAuth flow
3. Log in with your Stripe credentials
4. Grant Clerk permission to manage subscriptions
5. You'll be redirected back to Clerk Dashboard

**Verify**: You should see "Stripe Connected" with a green checkmark

---

## Part 2: Create 6 Pricing Plans (20 minutes)

You need to create **6 plans** (3 tiers × 2 billing intervals). Follow this exact structure:

---

### Plan 1: Solo Dealmaker (Monthly)

1. Click **"Create New Plan"** button
2. Fill in the details:

**Basic Information**:

- Plan Name: `Solo Dealmaker`
- Plan ID/Slug: `solo` or `solo_dealmaker`
- Description: `Perfect for individual dealmakers managing small pipelines`

**Pricing**:

- Amount: `$279`
- Currency: `USD`
- Billing Interval: `Monthly`
- Trial Period: `14 days`
- Trial Requires Payment Method: `Yes` ✅

**Features** (enter in features section):

```
✓ Up to 3 team members
✓ Manage 10 active deals
✓ 50GB secure document storage
✓ Basic analytics & reporting
✓ Deal pipeline management
✓ Email notifications
✓ Mobile app access
✓ Standard email support
```

**Permissions** (add these in permissions section):

```
org:deals:view
org:deals:create
org:deals:edit
org:analytics:basic
org:storage:50gb
org:support:email
org:export:basic
```

3. Click **"Save Plan"**

---

### Plan 2: Solo Dealmaker (Annual)

1. Click **"Create New Plan"** button
2. Fill in the details:

**Basic Information**:

- Plan Name: `Solo Dealmaker (Annual)`
- Plan ID/Slug: `solo` or `solo_annual`
- Description: `Annual plan - Save $558 per year (17% off)`

**Pricing**:

- Amount: `$2,790`
- Currency: `USD`
- Billing Interval: `Yearly` or `Annual`
- Trial Period: `14 days`
- Trial Requires Payment Method: `Yes` ✅

**Display Badge** (if available): `Save $558/year`

**Features** (same as monthly):

```
✓ Up to 3 team members
✓ Manage 10 active deals
✓ 50GB secure document storage
✓ Basic analytics & reporting
✓ Deal pipeline management
✓ Email notifications
✓ Mobile app access
✓ Standard email support
✓ SAVE $558 per year (17% off)
```

**Permissions** (same as monthly):

```
org:deals:view
org:deals:create
org:deals:edit
org:analytics:basic
org:storage:50gb
org:support:email
org:export:basic
```

3. Click **"Save Plan"**

---

### Plan 3: Growth Firm (Monthly)

1. Click **"Create New Plan"** button
2. Fill in the details:

**Basic Information**:

- Plan Name: `Growth Firm`
- Plan ID/Slug: `growth` or `growth_firm`
- Description: `For growing firms managing multiple deals simultaneously`

**Pricing**:

- Amount: `$798`
- Currency: `USD`
- Billing Interval: `Monthly`
- Trial Period: `14 days`
- Trial Requires Payment Method: `Yes` ✅

**Features**:

```
✓ Up to 15 team members
✓ Manage 50 active deals
✓ 200GB secure document storage
✓ Advanced analytics & custom reports
✓ AI-powered deal insights
✓ Team collaboration tools
✓ Priority email support
✓ API access
✓ Custom integrations
✓ Bulk data import/export
```

**Permissions**:

```
org:deals:view
org:deals:create
org:deals:edit
org:deals:delete
org:analytics:advanced
org:ai_analysis:use
org:ai_insights:view
org:team:collaborate
org:storage:200gb
org:support:priority
org:export:unlimited
org:integrations:basic
org:reports:generate
```

3. Click **"Save Plan"**

---

### Plan 4: Growth Firm (Annual)

1. Click **"Create New Plan"** button
2. Fill in the details:

**Basic Information**:

- Plan Name: `Growth Firm (Annual)`
- Plan ID/Slug: `growth` or `growth_annual`
- Description: `Annual plan - Save $1,596 per year (17% off)`

**Pricing**:

- Amount: `$7,980`
- Currency: `USD`
- Billing Interval: `Yearly` or `Annual`
- Trial Period: `14 days`
- Trial Requires Payment Method: `Yes` ✅

**Display Badge**: `Save $1,596/year`

**Features** (same as monthly + savings):

```
✓ Up to 15 team members
✓ Manage 50 active deals
✓ 200GB secure document storage
✓ Advanced analytics & custom reports
✓ AI-powered deal insights
✓ Team collaboration tools
✓ Priority email support
✓ API access
✓ Custom integrations
✓ Bulk data import/export
✓ SAVE $1,596 per year (17% off)
```

**Permissions** (same as monthly):

```
org:deals:view
org:deals:create
org:deals:edit
org:deals:delete
org:analytics:advanced
org:ai_analysis:use
org:ai_insights:view
org:team:collaborate
org:storage:200gb
org:support:priority
org:export:unlimited
org:integrations:basic
org:reports:generate
```

3. Click **"Save Plan"**

---

### Plan 5: Enterprise (Monthly)

1. Click **"Create New Plan"** button
2. Fill in the details:

**Basic Information**:

- Plan Name: `Enterprise`
- Plan ID/Slug: `enterprise`
- Description: `For large organizations requiring unlimited scale`

**Pricing**:

- Amount: `$1,598`
- Currency: `USD`
- Billing Interval: `Monthly`
- Trial Period: `14 days`
- Trial Requires Payment Method: `Yes` ✅

**Features**:

```
✓ Unlimited team members
✓ Unlimited active deals
✓ 1TB secure document storage
✓ Custom analytics & reporting
✓ Unlimited AI features
✓ Advanced team collaboration
✓ Dedicated account manager
✓ 24/7 priority support
✓ Custom integrations & API
✓ SSO & advanced security
✓ White-label options
✓ Custom SLA
✓ Onboarding & training
```

**Permissions**:

```
org:deals:unlimited
org:analytics:custom
org:ai:unlimited
org:team:unlimited
org:integrations:custom
org:sso:use
org:storage:1tb
org:support:dedicated
org:export:unlimited
org:reports:generate
org:white_label:use
org:billing:manage
```

3. Click **"Save Plan"**

---

### Plan 6: Enterprise (Annual)

1. Click **"Create New Plan"** button
2. Fill in the details:

**Basic Information**:

- Plan Name: `Enterprise (Annual)`
- Plan ID/Slug: `enterprise` or `enterprise_annual`
- Description: `Annual plan - Save $3,196 per year (17% off)`

**Pricing**:

- Amount: `$15,980`
- Currency: `USD`
- Billing Interval: `Yearly` or `Annual`
- Trial Period: `14 days`
- Trial Requires Payment Method: `Yes` ✅

**Display Badge**: `Save $3,196/year`

**Features** (same as monthly + savings):

```
✓ Unlimited team members
✓ Unlimited active deals
✓ 1TB secure document storage
✓ Custom analytics & reporting
✓ Unlimited AI features
✓ Advanced team collaboration
✓ Dedicated account manager
✓ 24/7 priority support
✓ Custom integrations & API
✓ SSO & advanced security
✓ White-label options
✓ Custom SLA
✓ Onboarding & training
✓ SAVE $3,196 per year (17% off)
```

**Permissions** (same as monthly):

```
org:deals:unlimited
org:analytics:custom
org:ai:unlimited
org:team:unlimited
org:integrations:custom
org:sso:use
org:storage:1tb
org:support:dedicated
org:export:unlimited
org:reports:generate
org:white_label:use
org:billing:manage
```

3. Click **"Save Plan"**

---

## Part 3: Configure Webhooks (10 minutes)

### Step 1: Navigate to Webhooks

1. In Clerk Dashboard, go to **"Webhooks"** in left sidebar
2. Click **"Add Endpoint"** button

### Step 2: Configure Subscription Webhook

Fill in the webhook details:

**Endpoint URL**:

```
https://ma-saas-backend.onrender.com/api/webhooks/clerk/subscription
```

**Description**: `Subscription lifecycle events for billing`

**Events to Subscribe** (select these):

- ✅ `subscription.created` - When a new subscription is created
- ✅ `subscription.updated` - When subscription changes (upgrade/downgrade)
- ✅ `subscription.deleted` - When subscription is canceled
- ✅ `subscription.cancelled` - When subscription is canceled (alternative spelling)
- ✅ `subscription.trial_will_end` - 3 days before trial ends
- ✅ `payment.succeeded` - When payment succeeds
- ✅ `invoice.payment_succeeded` - When invoice payment succeeds
- ✅ `payment.failed` - When payment fails
- ✅ `invoice.payment_failed` - When invoice payment fails

**Webhook Signing Secret** (already have this):

```
whsec_nBUKje3GC6+/XwtUtm1JERDNvXYnLgSO
```

**Status**: Set to `Enabled`

Click **"Create Endpoint"**

### Step 3: Test Webhook (Optional but Recommended)

1. In the webhook details page, find **"Send test event"** button
2. Select event type: `subscription.created`
3. Click **"Send Test"**
4. Verify response is `200 OK`

If you get an error:

- Check that backend is running: https://ma-saas-backend.onrender.com/health
- Check backend logs on Render for errors
- Verify webhook secret matches in backend `.env`

---

## Part 4: Update Render Environment Variables (5 minutes)

### Step 1: Access Render Dashboard

1. Go to https://dashboard.render.com
2. Select your backend service: **"ma-saas-backend"**

### Step 2: Update Environment Variables

1. Click **"Environment"** tab
2. Verify/Add these environment variables:

```bash
# Clerk Configuration
CLERK_SECRET_KEY=sk_live_[configured]
CLERK_PUBLISHABLE_KEY=pk_live_[configured]
CLERK_WEBHOOK_SECRET=whsec_[configured]

# Stripe Configuration (for Clerk Billing backend)
STRIPE_SECRET_KEY=sk_live_[configured]
STRIPE_PUBLISHABLE_KEY=pk_live_[configured]
```

**Note**: All keys are already configured in your backend `.env` file. These are reference placeholders.

3. Click **"Save Changes"**
4. Service will automatically redeploy

---

## Part 5: Verification Checklist

After completing all steps, verify the following:

### Clerk Dashboard Verification

- [ ] 6 pricing plans created (3 tiers × 2 intervals)
- [ ] All plans have 14-day free trial enabled
- [ ] All plans require payment method for trial
- [ ] Permissions configured for each plan
- [ ] Stripe account connected and active
- [ ] Webhook endpoint created and enabled
- [ ] Webhook signing secret matches backend

### Pricing Summary

- [ ] Solo Monthly: $279/mo
- [ ] Solo Annual: $2,790/yr (save $558)
- [ ] Growth Monthly: $798/mo
- [ ] Growth Annual: $7,980/yr (save $1,596)
- [ ] Enterprise Monthly: $1,598/mo
- [ ] Enterprise Annual: $15,980/yr (save $3,196)

### Backend Verification

- [ ] Backend deployed and running: https://ma-saas-backend.onrender.com
- [ ] Health check passes: https://ma-saas-backend.onrender.com/health
- [ ] Environment variables configured on Render
- [ ] Webhook endpoint accessible: https://ma-saas-backend.onrender.com/api/webhooks/clerk/subscription

### Frontend Verification

- [ ] Frontend environment variables configured
- [ ] VITE_CLERK_PUBLISHABLE_KEY set correctly
- [ ] Frontend deployed and accessible

---

## Part 6: Testing the Implementation (15 minutes)

### Test 1: View Pricing Page

1. Visit https://100daysandbeyond.com/pricing
2. Verify all 3 tiers display correctly
3. Toggle between Monthly and Annual
4. Verify annual savings display correctly

### Test 2: Test Subscription Flow (Use Stripe Test Mode First!)

1. **IMPORTANT**: Switch Stripe to Test Mode in Clerk Dashboard
2. Click "Subscribe" on Solo Dealmaker plan
3. You should be redirected to Clerk Checkout (powered by Stripe)
4. Use test card: `4242 4242 4242 4242`
5. Expiry: Any future date (e.g., `12/26`)
6. CVC: Any 3 digits (e.g., `123`)
7. Complete checkout
8. Verify redirect back to platform
9. Check `/subscription` page shows active subscription

### Test 3: Verify Webhook Processing

1. In Clerk Dashboard, go to Webhooks
2. Find your subscription webhook
3. Click "Recent Deliveries" tab
4. Find the `subscription.created` event from your test
5. Verify status is `200 OK`
6. Check backend logs on Render for webhook processing logs

### Test 4: Test Subscription Management

1. Visit https://100daysandbeyond.com/subscription
2. Verify UserProfile component loads
3. Click "Manage Subscription" tab
4. Verify can see subscription details
5. Test upgrade to Growth plan (test mode)
6. Test downgrade back to Solo plan
7. Test cancel subscription

---

## Troubleshooting

### Issue: Plans Not Showing on Pricing Page

**Cause**: PricingTable component not loading plans from Clerk
**Solution**:

1. Verify plans are published in Clerk Dashboard
2. Check browser console for errors
3. Verify VITE_CLERK_PUBLISHABLE_KEY is correct

### Issue: Webhook Returns 401 Unauthorized

**Cause**: Webhook signature verification failing
**Solution**:

1. Verify CLERK_WEBHOOK_SECRET matches in Render environment
2. Check backend logs for signature verification errors
3. Regenerate webhook secret in Clerk if needed

### Issue: Checkout Flow Fails

**Cause**: Stripe not properly connected or test mode issues
**Solution**:

1. Verify Stripe account is connected in Clerk
2. Ensure Stripe is in Test Mode for testing
3. Check Stripe Dashboard for error logs

### Issue: Permissions Not Working

**Cause**: Permissions not properly configured in plans
**Solution**:

1. Go back to each plan in Clerk Dashboard
2. Verify all permissions are added
3. Save plans again
4. Test with fresh subscription

---

## Production Launch Checklist

Before going live with real customers:

### Pre-Launch

- [ ] Test all 6 plans in Stripe Test Mode
- [ ] Test trial period (14 days) countdown
- [ ] Test trial ending notification
- [ ] Test payment success/failure scenarios
- [ ] Test upgrade/downgrade flows
- [ ] Test cancellation flow
- [ ] Test webhook delivery for all events
- [ ] Verify permissions work for all plan levels

### Launch

- [ ] Switch Stripe to Live Mode in Clerk Dashboard
- [ ] Update webhook URL to production (if needed)
- [ ] Update environment variables to production
- [ ] Test one real subscription with team member
- [ ] Monitor webhook logs for first 24 hours
- [ ] Set up alerts for payment failures

### Post-Launch Monitoring

- [ ] Monitor Clerk Dashboard for subscription metrics
- [ ] Monitor Stripe Dashboard for payment issues
- [ ] Monitor backend logs for webhook errors
- [ ] Track trial conversion rates
- [ ] Gather user feedback on checkout experience

---

## Support Resources

### Clerk Support

- Documentation: https://clerk.com/docs/billing
- Support Email: support@clerk.com
- Dashboard: https://dashboard.clerk.com

### Stripe Support

- Documentation: https://stripe.com/docs
- Support: https://support.stripe.com
- Dashboard: https://dashboard.stripe.com

### Your Backend

- API Health: https://ma-saas-backend.onrender.com/health
- Webhook Endpoint: https://ma-saas-backend.onrender.com/api/webhooks/clerk/subscription
- Render Dashboard: https://dashboard.render.com

---

## Summary

You're now ready to configure Clerk Billing! Here's what you need to do:

1. **Clerk Dashboard** (30 min):
   - Enable Clerk Billing
   - Create 6 pricing plans with exact specifications above
   - Configure webhook endpoint

2. **Render Dashboard** (5 min):
   - Verify environment variables are set
   - Service should already be configured

3. **Test Everything** (15 min):
   - Test pricing page
   - Test subscription flow (test mode)
   - Test webhooks
   - Verify subscription management

**Status**: All code is complete. Only dashboard configuration needed.

---

**Created**: October 12, 2025
**Last Updated**: October 12, 2025
**Next Review**: After configuration complete
