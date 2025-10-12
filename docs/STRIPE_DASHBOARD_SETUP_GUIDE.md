# Stripe Dashboard Setup Guide

Complete step-by-step guide to configure Stripe for the M&A SaaS Platform billing integration.

## Prerequisites

- Stripe account (sign up at https://stripe.com if you don't have one)
- Access to Stripe Dashboard
- Backend deployment URL (for webhook configuration)

## Part 1: Create Products and Prices

### Step 1: Access Products Section

1. Log in to [Stripe Dashboard](https://dashboard.stripe.com)
2. Ensure you're in **Test mode** (toggle in top right)
3. Navigate to **Products** in the left sidebar
4. Click **+ Add product**

### Step 2: Create Solo Dealmaker Product

**Product Details:**

1. **Name:** `Solo Dealmaker`
2. **Description:** `Perfect for individual professionals starting their M&A journey`
3. Click **Add pricing**

**Pricing Details:**

1. **Pricing model:** Standard pricing
2. **Price:** `279.00`
3. **Currency:** `USD` (or your preferred currency)
4. **Billing period:** `Monthly`
5. **Payment type:** `Recurring`
6. **Free trial:** _(Optional)_ `14 days`
7. Click **Add product**

**Important:** After creation, click on the price to view details and **copy the Price ID**. It will look like:

```
price_XXXXXXXXXXXXXXXXXXXXXXXXX
```

Save this as: **Solo Dealmaker Price ID**

### Step 3: Create Growth Firm Product

**Product Details:**

1. Click **+ Add product**
2. **Name:** `Growth Firm`
3. **Description:** `For growing M&A teams and mid-size firms`
4. Click **Add pricing**

**Pricing Details:**

1. **Pricing model:** Standard pricing
2. **Price:** `798.00`
3. **Currency:** `USD`
4. **Billing period:** `Monthly`
5. **Payment type:** `Recurring`
6. **Free trial:** _(Optional)_ `14 days`
7. Click **Add product**

**Copy Price ID** and save as: **Growth Firm Price ID**

### Step 4: Create Enterprise Product

**Product Details:**

1. Click **+ Add product**
2. **Name:** `Enterprise`
3. **Description:** `For large firms and investment banks`
4. Click **Add pricing**

**Pricing Details:**

1. **Pricing model:** Standard pricing
2. **Price:** `1598.00`
3. **Currency:** `USD`
4. **Billing period:** `Monthly`
5. **Payment type:** `Recurring`
6. **Free trial:** _(Optional)_ `14 days`
7. Click **Add product**

**Copy Price ID** and save as: **Enterprise Price ID**

### Step 5: Record Your Price IDs

You should now have three Price IDs that look like:

```
Solo Dealmaker:  price_1QXXXXXXXXXXXXXXXXXXXXXX
Growth Firm:     price_1QXXXXXXXXXXXXXXXXXXXXXX
Enterprise:      price_1QXXXXXXXXXXXXXXXXXXXXXX
```

**⚠️ Important:** You'll need to update your backend code to use these actual Price IDs instead of the placeholder strings.

## Part 2: Configure Backend with Price IDs

### Update Backend Configuration

You need to map the tier identifiers to actual Stripe Price IDs.

**Option 1: Environment Variables (Recommended)**

Add to your `backend/.env`:

```env
STRIPE_PRICE_SOLO_DEALMAKER=price_1QXXXXXXXXXXXXXXXXXXXXXX
STRIPE_PRICE_GROWTH_FIRM=price_1QXXXXXXXXXXXXXXXXXXXXXX
STRIPE_PRICE_ENTERPRISE=price_1QXXXXXXXXXXXXXXXXXXXXXX
```

**Option 2: Backend Configuration File**

Update your backend code where checkout sessions are created:

```python
# In app/api/payments.py or appropriate file
PRICE_ID_MAPPING = {
    "solo_dealmaker": "price_1QXXXXXXXXXXXXXXXXXXXXXX",
    "growth_firm": "price_1QXXXXXXXXXXXXXXXXXXXXXX",
    "enterprise": "price_1QXXXXXXXXXXXXXXXXXXXXXX"
}

# In checkout session creation
price_id = PRICE_ID_MAPPING.get(plan_tier)
```

**Update CheckoutButton Component (if needed)**

If you're building the price_id in the frontend, update:

```typescript
// In CheckoutButton.tsx, change:
body: JSON.stringify({
  price_id: `price_${planTier}`,  // OLD
  // to:
  price_id: planTier,  // NEW (backend will map it)
  ...
})
```

## Part 3: Configure Webhooks

Webhooks allow Stripe to notify your backend when subscription events occur (payments, cancellations, etc.).

### Step 1: Access Webhooks Section

1. In Stripe Dashboard, navigate to **Developers** → **Webhooks**
2. Click **+ Add endpoint**

### Step 2: Configure Webhook Endpoint

**For Development (Local Testing):**

```
http://localhost:8000/api/payments/webhook
```

_(Note: You'll use Stripe CLI for local webhook forwarding)_

**For Production:**

```
https://your-backend-domain.com/api/payments/webhook
```

**Example:**

```
https://ma-platform-backend.render.com/api/payments/webhook
```

### Step 3: Select Events to Listen

Select the following events (click "Select events" button):

**Customer Events:**

- [x] `customer.created`
- [x] `customer.updated`
- [x] `customer.deleted`

**Subscription Events:**

- [x] `customer.subscription.created`
- [x] `customer.subscription.updated`
- [x] `customer.subscription.deleted`
- [x] `customer.subscription.trial_will_end`

**Invoice Events:**

- [x] `invoice.created`
- [x] `invoice.finalized`
- [x] `invoice.paid`
- [x] `invoice.payment_failed`
- [x] `invoice.payment_succeeded`

**Payment Intent Events:**

- [x] `payment_intent.succeeded`
- [x] `payment_intent.payment_failed`

**Checkout Events:**

- [x] `checkout.session.completed`
- [x] `checkout.session.expired`

### Step 4: Save and Get Signing Secret

1. Click **Add endpoint**
2. The webhook is now created
3. Click on the webhook to view details
4. Under **Signing secret**, click **Reveal**
5. Copy the secret - it looks like: `whsec_XXXXXXXXXXXXXXXXXXXXXXXXX`

### Step 5: Update Backend with Webhook Secret

Add to your `backend/.env`:

```env
STRIPE_WEBHOOK_SECRET=whsec_XXXXXXXXXXXXXXXXXXXXXXXXX
```

**⚠️ Critical:** The webhook secret is used to verify that webhook events actually come from Stripe. Never skip signature verification!

## Part 4: Configure Customer Portal

The Customer Portal allows users to manage their subscriptions, update payment methods, and view invoices.

### Step 1: Access Customer Portal Settings

1. In Stripe Dashboard, navigate to **Settings** → **Customer portal**
2. Click **Activate** if not already activated

### Step 2: Configure Portal Settings

**Features to Enable:**

- [x] **Update payment methods** - Let customers update their cards
- [x] **Cancel subscriptions** - Let customers cancel
- [x] **Update subscriptions** _(Optional)_ - Let customers upgrade/downgrade
- [x] **Invoice history** - Show past invoices

**Cancellation Settings:**

- **Cancel subscription immediately** _(OR)_ **At the end of billing period**
- **Cancellation reasons** - Enable to gather feedback
- **Cancellation survey** - Optional custom questions

**Business Information:**

- **Business name:** M&A SaaS Platform
- **Support email:** support@ma-platform.com _(update to your email)_
- **Privacy policy URL:** _(optional)_
- **Terms of service URL:** _(optional)_

### Step 3: Customize Appearance (Optional)

1. **Brand color:** Choose your brand color
2. **Logo:** Upload company logo (recommended: 512x512 PNG)
3. **Font:** Choose font family
4. **Button style:** Select button style

### Step 4: Save Settings

Click **Save** to apply customer portal settings.

## Part 5: Test the Integration

### Local Development Testing

#### Step 1: Install Stripe CLI

Download from: https://stripe.com/docs/stripe-cli

**macOS (Homebrew):**

```bash
brew install stripe/stripe-cli/stripe
```

**Windows:**
Download the installer from the Stripe CLI page

**Linux:**

```bash
# See Stripe CLI documentation
```

#### Step 2: Authenticate Stripe CLI

```bash
stripe login
```

This opens a browser window to authorize the CLI.

#### Step 3: Forward Webhooks to Local Backend

```bash
stripe listen --forward-to localhost:8000/api/payments/webhook
```

**Important:** This command outputs a webhook signing secret for local testing:

```
> Ready! Your webhook signing secret is whsec_XXXXXXXXXXXXXXXXXXX (^C to quit)
```

Update your local `backend/.env` with this secret while testing locally.

#### Step 4: Test Checkout Flow

1. Start your backend server
2. Start your frontend dev server
3. Navigate to `/pricing`
4. Click "Choose Plan"
5. Use Stripe test card: **4242 4242 4242 4242**
6. Complete checkout
7. Watch Stripe CLI output for webhook events
8. Verify subscription created in your database

### Test Cards

Stripe provides many test cards. Most common:

| Card Number           | Description                         |
| --------------------- | ----------------------------------- |
| `4242 4242 4242 4242` | Succeeds                            |
| `4000 0000 0000 9995` | Declined (insufficient funds)       |
| `4000 0000 0000 0002` | Declined (generic decline)          |
| `4000 0000 0000 9987` | Declined (lost card)                |
| `4000 0025 0000 3155` | Requires authentication (3D Secure) |

**For all test cards:**

- **Expiry:** Any future date (e.g., `12/34`)
- **CVC:** Any 3 digits (e.g., `123`)
- **ZIP:** Any 5 digits (e.g., `12345`)

More test cards: https://stripe.com/docs/testing#cards

## Part 6: Production Deployment

### Step 1: Switch to Live Mode

1. In Stripe Dashboard, toggle from **Test mode** to **Live mode** (top right)
2. You'll need to complete Stripe account activation if not already done:
   - Provide business details
   - Verify bank account
   - Complete identity verification

### Step 2: Create Production Products

**⚠️ Important:** Test mode and Live mode have separate products!

Repeat **Part 1** (Create Products and Prices) in **Live mode**:

- Create Solo Dealmaker product with $279/month price
- Create Growth Firm product with $798/month price
- Create Enterprise product with $1,598/month price
- Copy the **Live mode Price IDs**

### Step 3: Create Production Webhook

Repeat **Part 3** (Configure Webhooks) in **Live mode**:

- Add webhook endpoint with your production URL
- Select the same events
- Copy the **Live mode webhook signing secret**

### Step 4: Update Production Environment Variables

Update your production `backend/.env`:

```env
# Switch to live keys
STRIPE_SECRET_KEY=sk_live_[YOUR_LIVE_SECRET_KEY]
STRIPE_PUBLISHABLE_KEY=pk_live_[YOUR_LIVE_PUBLISHABLE_KEY]
STRIPE_WEBHOOK_SECRET=whsec_[YOUR_WEBHOOK_SECRET]

# Production price IDs
STRIPE_PRICE_SOLO_DEALMAKER=price_[YOUR_PRICE_ID]  # Live mode price
STRIPE_PRICE_GROWTH_FIRM=price_[YOUR_PRICE_ID]     # Live mode price
STRIPE_PRICE_ENTERPRISE=price_[YOUR_PRICE_ID]      # Live mode price

# Update other settings
ENVIRONMENT=production
DEBUG=false
```

### Step 5: Deploy and Test

1. Deploy backend with updated environment variables
2. Deploy frontend
3. **Test with real payment:**
   - Use a real card or Stripe test card in live mode
   - Complete a real checkout (you can refund it afterward)
   - Verify subscription created
   - Verify webhook received
   - Test customer portal access
   - Test cancellation flow

### Step 6: Refund Test Transaction

1. In Stripe Dashboard → **Payments**
2. Find your test payment
3. Click **Refund** to refund the test charge

## Part 7: Monitoring and Maintenance

### Monitor Webhook Delivery

1. Navigate to **Developers** → **Webhooks**
2. Click on your webhook endpoint
3. View **Webhook attempts** to see delivery success/failure
4. Check **Event logs** for details on each event

### Handling Failed Webhooks

If webhooks fail:

1. Check backend logs for errors
2. Verify webhook secret is correct
3. Ensure endpoint is accessible (not blocked by firewall)
4. Check webhook signature verification code
5. Retry failed events from Stripe Dashboard if needed

### View Logs

- **Events:** Developers → Events (all Stripe events)
- **Webhook logs:** Developers → Webhooks → [Your endpoint] → Attempts
- **Payment logs:** Payments → View payment details

### Set Up Alerts (Optional)

1. Navigate to **Settings** → **Notifications**
2. Configure email alerts for:
   - Failed payments
   - Subscription cancellations
   - High-value transactions
   - Dispute notifications

## Troubleshooting

### Webhook Not Received

**Check:**

1. Webhook URL is correct and accessible
2. Backend endpoint is not behind authentication
3. Webhook secret is correct in backend config
4. Webhook events are enabled in Stripe Dashboard
5. Backend server is running and reachable

**Test:**

```bash
# Test webhook endpoint manually
curl -X POST https://your-backend.com/api/payments/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

### Signature Verification Failed

**Common causes:**

1. Wrong webhook secret in backend
2. Request body parsed as JSON before verification (should be raw)
3. Using test secret with live webhook or vice versa

**Solution:**

- Verify you're using the correct secret for the environment
- Ensure raw request body is used for verification
- Check Stripe library is up to date

### Price Not Found

**Common causes:**

1. Using test Price ID in live mode
2. Using live Price ID in test mode
3. Price ID typo in configuration

**Solution:**

- Verify you're using the correct Price IDs for your current mode
- Check Price IDs in Stripe Dashboard
- Ensure Price IDs are properly configured in backend

## Security Best Practices

- ✅ **Never** commit Stripe keys to version control
- ✅ **Always** verify webhook signatures
- ✅ Use environment variables for sensitive data
- ✅ Rotate webhook secrets periodically
- ✅ Use HTTPS in production
- ✅ Restrict API key permissions (use restricted keys if possible)
- ✅ Monitor webhook attempts for suspicious activity
- ✅ Enable Stripe Radar for fraud detection

## Additional Resources

- **Stripe Dashboard:** https://dashboard.stripe.com
- **Stripe Documentation:** https://stripe.com/docs
- **Stripe API Reference:** https://stripe.com/docs/api
- **Webhook Documentation:** https://stripe.com/docs/webhooks
- **Testing Guide:** https://stripe.com/docs/testing
- **Stripe CLI:** https://stripe.com/docs/stripe-cli
- **Customer Portal Docs:** https://stripe.com/docs/billing/subscriptions/integrating-customer-portal

## Checklist

### Test Mode Setup

- [ ] Create Solo Dealmaker product and price
- [ ] Create Growth Firm product and price
- [ ] Create Enterprise product and price
- [ ] Copy all test Price IDs
- [ ] Update backend with test Price IDs
- [ ] Create webhook endpoint (for Stripe CLI)
- [ ] Copy webhook signing secret
- [ ] Update backend with webhook secret
- [ ] Configure customer portal settings
- [ ] Test with Stripe CLI
- [ ] Complete test checkout flow

### Live Mode Setup

- [ ] Activate Stripe account (complete verification)
- [ ] Switch to Live mode
- [ ] Create Solo Dealmaker product and price
- [ ] Create Growth Firm product and price
- [ ] Create Enterprise product and price
- [ ] Copy all live Price IDs
- [ ] Update production backend with live Price IDs
- [ ] Create production webhook endpoint
- [ ] Copy production webhook signing secret
- [ ] Update production backend with webhook secret
- [ ] Test complete flow with real card
- [ ] Refund test transaction
- [ ] Set up monitoring alerts
- [ ] Monitor webhook delivery

---

**Last Updated:** October 12, 2025
**Version:** 1.0
