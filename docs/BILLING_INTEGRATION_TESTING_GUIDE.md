# Billing Integration Testing Guide

This guide outlines the complete testing process for the Clerk + Stripe billing integration implemented in the M&A SaaS Platform.

## Overview

The billing integration includes:

- Clerk authentication with user management
- Stripe payment processing and subscription management
- Custom React components for seamless checkout experience
- Subscription lifecycle management

## Prerequisites

Before testing, ensure you have:

1. **Backend Requirements:**
   - Stripe account with test API keys configured
   - Backend `.env` file with:
     - `STRIPE_SECRET_KEY`
     - `STRIPE_PUBLISHABLE_KEY`
     - `STRIPE_WEBHOOK_SECRET`
     - `CLERK_SECRET_KEY`
     - `CLERK_WEBHOOK_SECRET`

2. **Frontend Requirements:**
   - Clerk publishable key in `.env.local`:
     - `VITE_CLERK_PUBLISHABLE_KEY`
     - `VITE_API_URL` (pointing to backend)

3. **Stripe Dashboard Setup:**
   - Create three products/prices in Stripe Dashboard:
     - Solo Dealmaker: $279/month (price_id: `price_solo_dealmaker`)
     - Growth Firm: $798/month (price_id: `price_growth_firm`)
     - Enterprise: $1,598/month (price_id: `price_enterprise`)
   - Configure webhook endpoint: `https://your-backend-url/api/payments/webhook`
   - Select relevant webhook events (see Backend Setup section)

## Test Scenarios

### 1. Pricing Page - Unauthenticated User

**Test Steps:**

1. Navigate to `/pricing` page
2. Verify all three pricing tiers are displayed:
   - Solo Dealmaker ($279/month)
   - Growth Firm ($798/month) - marked as "Most Popular"
   - Enterprise ($1,598/month)
3. Verify each plan shows correct features
4. Click "Sign Up & Choose Plan" button on any plan

**Expected Results:**

- All plans display correctly with proper styling
- "Most Popular" badge appears on Growth Firm plan
- Clicking button redirects to Clerk sign-up page
- Toast notification shows: "Please sign up to choose a plan"

### 2. User Registration Flow

**Test Steps:**

1. Complete Clerk sign-up process
2. Verify email confirmation (if enabled)
3. After sign-up, user should be redirected back to app

**Expected Results:**

- User successfully creates account
- User is authenticated via Clerk
- Backend creates corresponding user record via webhook
- User can access authenticated routes

### 3. Pricing Page - Authenticated User

**Test Steps:**

1. Sign in to the application
2. Navigate to `/pricing` page
3. Verify button text changed to "Choose [Plan Name]"
4. Verify current subscription banner appears if user has active subscription

**Expected Results:**

- Buttons show "Choose Solo Dealmaker", "Choose Growth Firm", "Choose Enterprise"
- Credit card icon appears on buttons
- If user has active subscription, banner shows at top with plan details
- Current plan button is disabled and shows "Current Plan" with checkmark

### 4. Checkout Flow - New Subscription

**Test Steps:**

1. As authenticated user, click "Choose [Plan Name]" button
2. Observe loading state ("Creating checkout...")
3. Verify redirect to Stripe Checkout page
4. On Stripe Checkout:
   - Verify correct plan name and price displayed
   - Use Stripe test card: `4242 4242 4242 4242`
   - Use any future expiry date (e.g., 12/34)
   - Use any 3-digit CVC (e.g., 123)
   - Use any ZIP code (e.g., 12345)
5. Complete checkout
6. Verify redirect to success page

**Expected Results:**

- Smooth redirect to Stripe Checkout
- Checkout session contains correct plan details
- Test payment completes successfully
- User redirected to `/subscription/success?session_id=...`
- Success page shows celebration message and next steps
- Subscription is created in Stripe
- Backend receives webhook and creates subscription record

### 5. Success Page Verification

**Test Steps:**

1. After checkout, verify success page displays:
   - Green checkmark with animation
   - "Welcome Aboard! 🎉" message
   - "What's Next?" section with feature list
   - "Go to Dashboard" button
   - "Manage Subscription" button
2. Click "Go to Dashboard"
3. Verify user is redirected to main dashboard

**Expected Results:**

- Success page displays correctly with all elements
- Session verification happens in background
- Toast notification: "Subscription activated successfully!"
- Navigation buttons work correctly

### 6. Subscription Management Page

**Test Steps:**

1. Navigate to `/subscription` page (or click from success page)
2. Verify subscription overview card shows:
   - Plan name (e.g., "Growth Firm Plan")
   - Status badge (e.g., "Active" or "Trial")
   - Amount (e.g., "$798.00 USD")
   - Billing cycle (e.g., "Monthly")
   - Next billing date
3. Verify plan features card shows:
   - Team members limit
   - Active deals limit
   - Storage amount
   - AI credits
   - Additional features list
4. Click "Manage Billing" button

**Expected Results:**

- All subscription details display correctly
- Data matches what's in Stripe Dashboard
- Features are formatted properly (showing "Unlimited" where applicable)
- "Manage Billing" button redirects to Stripe Customer Portal

### 7. Stripe Customer Portal

**Test Steps:**

1. From subscription page, click "Manage Billing"
2. Verify redirect to Stripe Customer Portal
3. In portal, verify user can:
   - View invoice history
   - Update payment method
   - Cancel subscription
   - Change plan (if configured)
4. Test canceling subscription:
   - Click "Cancel Plan"
   - Confirm cancellation
   - Verify redirect back to `/subscription`
5. Verify cancellation warning appears on subscription page

**Expected Results:**

- Portal session created successfully
- User sees their subscription details in Stripe portal
- All portal features work correctly
- Cancellation processed successfully
- Backend receives webhook about cancellation
- Subscription page shows "Cancels at period end" badge

### 8. Cancel Checkout Flow

**Test Steps:**

1. Start checkout process for a plan
2. On Stripe Checkout page, click "Back" or close tab
3. Verify redirect to `/subscription/cancel` page
4. Verify page shows:
   - Orange warning icon
   - "Checkout Canceled" message
   - "No charges were made" alert
   - Common questions section
   - "Back to Pricing" button
   - "Contact Support" button
5. Click "Back to Pricing"

**Expected Results:**

- Cancel page displays correctly
- User informed no charges were made
- All sections render properly
- Navigation buttons work correctly
- User can restart checkout process

### 9. Existing Subscription - Pricing Page Behavior

**Test Steps:**

1. As user with active subscription, visit `/pricing`
2. Verify current plan shows:
   - "Current Plan" button (disabled)
   - Checkmark icon
   - Different styling (outline variant)
3. Verify other plans show "Choose [Plan Name]" button
4. Click button on different plan
5. Verify user can upgrade/change subscription

**Expected Results:**

- Current plan clearly indicated
- Cannot re-subscribe to same plan
- Can initiate change to different plan
- Checkout session created for plan change

### 10. Subscription Status Indicators

**Test Steps:**
Test various subscription statuses:

**Active Subscription:**

- Status badge shows "Active" (green)
- Full access to features
- "Manage Billing" button enabled

**Trial Subscription:**

- Status badge shows "Trial" (gray)
- Plan name appends "(Trial)"
- Full access to features during trial

**Past Due Subscription:**

- Status badge shows "Past Due" (red)
- Warning message about payment failure
- Prompt to update payment method

**Canceled Subscription:**

- Status badge shows "Canceled" (red)
- Alert: "Your subscription will be canceled on [date]"
- Access continues until period end

**Expected Results:**

- Each status displays correct badge color and label
- Appropriate warnings/messages for each state
- User actions available match subscription status

## API Endpoint Testing

### Test Backend Endpoints Directly

Using tools like Postman, cURL, or Bruno:

**1. Get Current Subscription**

```bash
GET /api/payments/subscription/current
Headers: Authorization: Bearer {clerk_jwt_token}

Expected: 200 OK with subscription data or 404 if no subscription
```

**2. Create Checkout Session**

```bash
POST /api/payments/checkout-session
Headers:
  Authorization: Bearer {clerk_jwt_token}
  Content-Type: application/json
Body:
{
  "price_id": "price_solo_dealmaker",
  "success_url": "http://localhost:5173/subscription/success?session_id={CHECKOUT_SESSION_ID}",
  "cancel_url": "http://localhost:5173/subscription/cancel",
  "mode": "subscription"
}

Expected: 200 OK with session_url
```

**3. Create Portal Session**

```bash
POST /api/payments/portal-session
Headers:
  Authorization: Bearer {clerk_jwt_token}
  Content-Type: application/json
Body:
{
  "return_url": "http://localhost:5173/subscription"
}

Expected: 200 OK with portal_url
```

**4. Webhook Handling**

```bash
POST /api/payments/webhook
Headers:
  Content-Type: application/json
  Stripe-Signature: {stripe_signature}
Body: {stripe_event_payload}

Expected: 200 OK
```

## Webhook Testing

### Using Stripe CLI

1. **Install Stripe CLI:**

   ```bash
   # Download from: https://stripe.com/docs/stripe-cli
   ```

2. **Login to Stripe:**

   ```bash
   stripe login
   ```

3. **Forward Webhooks to Local Backend:**

   ```bash
   stripe listen --forward-to localhost:8000/api/payments/webhook
   ```

4. **Trigger Test Events:**

   ```bash
   # Test subscription created
   stripe trigger customer.subscription.created

   # Test subscription updated
   stripe trigger customer.subscription.updated

   # Test subscription deleted
   stripe trigger customer.subscription.deleted

   # Test payment succeeded
   stripe trigger invoice.payment_succeeded

   # Test payment failed
   stripe trigger invoice.payment_failed
   ```

5. **Verify Backend Logs:**
   - Check backend logs for webhook receipt
   - Verify database updates
   - Confirm user subscription records updated

## Error Scenarios

### Test Error Handling

**1. Invalid API Token:**

- Remove or corrupt authentication token
- Attempt API call
- Expected: 401 Unauthorized error

**2. Invalid Price ID:**

- Use non-existent price_id in checkout
- Expected: Proper error message displayed to user

**3. Network Failure:**

- Disconnect internet during checkout
- Expected: User-friendly error message, retry option

**4. Webhook Signature Failure:**

- Send webhook with invalid signature
- Expected: Backend rejects webhook (400 error)

**5. Expired Checkout Session:**

- Start checkout, wait 24+ hours
- Try to complete expired session
- Expected: Stripe shows error, user redirected back

## Performance Testing

### Load Testing Considerations

1. **Concurrent Checkouts:**
   - Multiple users initiating checkout simultaneously
   - Verify no race conditions

2. **Subscription API Response Time:**
   - Measure `/subscription/current` endpoint latency
   - Should respond within 500ms

3. **Webhook Processing:**
   - Verify webhooks processed quickly
   - Check for any blocking operations

## Security Testing

### Security Checklist

- [ ] Clerk JWT tokens validated on all protected endpoints
- [ ] Stripe webhook signatures verified
- [ ] No sensitive keys exposed in frontend code
- [ ] CORS properly configured for API
- [ ] HTTPS enforced in production
- [ ] Rate limiting enabled on API endpoints
- [ ] SQL injection protection (using ORMs)
- [ ] XSS protection in React components

## Browser Compatibility

Test on multiple browsers:

- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge
- [ ] Mobile browsers (iOS Safari, Chrome Mobile)

## Mobile Responsiveness

Test on various device sizes:

- [ ] Desktop (1920x1080)
- [ ] Laptop (1366x768)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

## Accessibility Testing

- [ ] Keyboard navigation works throughout checkout
- [ ] Screen reader compatibility
- [ ] Proper ARIA labels on interactive elements
- [ ] Color contrast meets WCAG standards
- [ ] Focus indicators visible

## Production Deployment Checklist

Before deploying to production:

1. **Environment Variables:**
   - [ ] Switch to production Stripe keys
   - [ ] Switch to production Clerk keys
   - [ ] Update CORS_ORIGINS to production domain
   - [ ] Set FRONTEND_URL to production URL
   - [ ] Configure production webhook URL

2. **Stripe Configuration:**
   - [ ] Create production products/prices
   - [ ] Update price IDs in backend configuration
   - [ ] Configure production webhook endpoint
   - [ ] Test webhook with production endpoint
   - [ ] Enable required webhook events

3. **Testing:**
   - [ ] Complete full checkout flow in production
   - [ ] Verify webhooks received in production
   - [ ] Test subscription management in production
   - [ ] Verify email notifications (if configured)

4. **Monitoring:**
   - [ ] Set up error tracking (Sentry, etc.)
   - [ ] Configure logging for payment events
   - [ ] Set up alerts for failed payments
   - [ ] Monitor webhook delivery

## Troubleshooting

### Common Issues

**Issue: "No authentication token" error**

- **Cause:** User not properly authenticated with Clerk
- **Solution:** Check Clerk session, force re-login

**Issue: Checkout button not working**

- **Cause:** Invalid API_URL or backend not running
- **Solution:** Verify VITE_API_URL env var, check backend status

**Issue: Webhook not received**

- **Cause:** Incorrect webhook URL or signature mismatch
- **Solution:** Verify webhook URL in Stripe Dashboard, check webhook secret

**Issue: Subscription not showing after payment**

- **Cause:** Webhook processing delay or failure
- **Solution:** Check backend logs, verify webhook events enabled

**Issue: Portal session creation fails**

- **Cause:** User doesn't have Stripe customer ID
- **Solution:** Ensure user has completed at least one checkout

## Support Resources

- **Clerk Documentation:** https://clerk.com/docs
- **Stripe Documentation:** https://stripe.com/docs
- **Stripe Testing:** https://stripe.com/docs/testing
- **Stripe Webhooks:** https://stripe.com/docs/webhooks

## Verification Checklist

After completing implementation, verify:

- [x] CheckoutButton component created
- [x] useSubscription hook created
- [x] PricingPage updated with authentication
- [x] SubscriptionManager component created
- [x] SubscriptionPage created
- [x] SubscriptionSuccessPage created
- [x] SubscriptionCancelPage created
- [x] App.jsx routes updated
- [x] Environment variables documented
- [ ] All test scenarios passed
- [ ] Error handling verified
- [ ] Security checklist completed
- [ ] Browser compatibility tested
- [ ] Mobile responsiveness confirmed
- [ ] Production deployment checklist completed

## Next Steps

1. Set up Stripe products and prices in Dashboard
2. Configure webhook endpoint in Stripe Dashboard
3. Run through all test scenarios
4. Fix any issues discovered during testing
5. Perform security audit
6. Deploy to staging environment
7. Final production testing
8. Deploy to production
9. Monitor initial production usage

---

**Document Version:** 1.0
**Last Updated:** 2025-10-12
**Status:** Implementation Complete, Testing Pending
