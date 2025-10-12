# Clerk Native Billing Implementation Plan

**Date:** October 12, 2025
**Status:** Planning
**Approach:** Using Clerk's Native Billing with Stripe Integration

## Overview

This document outlines the plan to implement subscription billing using Clerk's native billing functionality instead of custom Stripe integration. This approach provides:

- ✅ Built-in billing UI components
- ✅ Native integration with Clerk authentication
- ✅ Automatic subscription management
- ✅ Simplified entitlement checks
- ✅ Monthly and annual billing options
- ✅ 14-day free trial support
- ✅ Managed by Clerk Dashboard

## Why Clerk Billing?

### Advantages Over Custom Stripe Integration

1. **Zero Custom Backend Code**
   - No payment API endpoints to build
   - No webhook handlers to maintain
   - No subscription state management logic

2. **Built-in UI Components**
   - `<PricingTable />` - Displays plans with instant subscribe
   - `<UserProfile />` - Subscription management built-in
   - No custom checkout flow needed

3. **Automatic Entitlement Management**
   - Use `has()` helper to check user's plan/features
   - Automatic access control based on subscription
   - Real-time subscription status updates

4. **Simplified Developer Experience**
   - Configure plans in Clerk Dashboard
   - Drop in components - no complex integration
   - Clerk handles all billing logic

5. **Same Stripe Processing**
   - Still uses Stripe for payments
   - Clerk handles the UI/UX layer
   - You get Stripe's reliability with Clerk's simplicity

## Pricing Structure

### Tier Configuration

| Tier               | Monthly   | Annual       | Annual Discount  | Savings        |
| ------------------ | --------- | ------------ | ---------------- | -------------- |
| **Solo Dealmaker** | $279/mo   | $2,790/year  | 17% ($558 off)   | ~2 months free |
| **Growth Firm**    | $798/mo   | $7,980/year  | 17% ($1,596 off) | ~2 months free |
| **Enterprise**     | $1,598/mo | $15,980/year | 17% ($3,196 off) | ~2 months free |

**All plans include:**

- 14-day free trial (requires credit card)
- Cancel anytime
- Automatic billing
- Access to all tier features
- Stripe-powered payments

### Annual Discount Strategy

**17% discount** = Approximately 2 months free

- Industry-standard SaaS annual discount
- Compelling value proposition
- Predictable annual revenue
- Lower churn for annual subscribers

### Tier Features

#### Solo Dealmaker

- Up to 3 team members
- 10 active deals
- 50GB storage
- Basic analytics
- Email support
- Deal pipeline management
- Document management

#### Growth Firm (Most Popular)

- Up to 15 team members
- 50 active deals
- 200GB storage
- Advanced analytics
- Priority support
- AI-powered insights
- Team collaboration tools
- Workflow automation
- Due diligence management

#### Enterprise

- Unlimited team members
- Unlimited deals
- 1TB storage
- Custom analytics
- Dedicated support
- White labeling
- SSO integration
- Custom integrations
- Audit logs
- Advanced security features

## Implementation Steps

### Phase 1: Clerk Dashboard Setup

#### 1.1 Connect Stripe Account

1. Navigate to Clerk Dashboard → Configure → Billing
2. Click "Connect Stripe"
3. Authorize Clerk to access your Stripe account
4. Clerk will create necessary Stripe products/prices

#### 1.2 Create Pricing Plans

**For Each Tier (Solo Dealmaker, Growth Firm, Enterprise):**

1. Go to Clerk Dashboard → Billing → Plans
2. Click "Create Plan"

**Monthly Plan Configuration:**

```yaml
Name: Solo Dealmaker (Monthly)
Price: $279
Interval: Monthly
Trial Period: 14 days
Features:
  - max_users: 3
  - max_deals: 10
  - max_storage_gb: 50
  - analytics_level: basic
  - support_level: email
  - deal_pipeline: true
  - document_management: true
```

**Annual Plan Configuration:**

```yaml
Name: Solo Dealmaker (Annual)
Price: $2,790
Interval: Yearly
Trial Period: 14 days
Features:
  - max_users: 3
  - max_deals: 10
  - max_storage_gb: 50
  - analytics_level: basic
  - support_level: email
  - deal_pipeline: true
  - document_management: true
  - annual_billing: true
```

Repeat for **Growth Firm** and **Enterprise** tiers.

#### 1.3 Configure Features (Entitlements)

For each plan, add features that can be checked with `has()`:

```javascript
// User tier features
-'tier:solo_dealmaker' -
  'tier:growth_firm' -
  'tier:enterprise' -
  // Capability features
  'feature:advanced_analytics' -
  'feature:ai_insights' -
  'feature:workflow_automation' -
  'feature:white_labeling' -
  'feature:sso' -
  'feature:custom_integrations';
```

### Phase 2: Frontend Implementation

#### 2.1 Install/Verify Clerk Package

```bash
cd frontend
# Verify @clerk/clerk-react is installed and up to date
pnpm list @clerk/clerk-react
```

Current version: **v5.51.0**
Recommended: Pin to specific version to avoid beta breaking changes

#### 2.2 Update PricingPage Component

Replace custom implementation with Clerk's `<PricingTable />`:

```jsx
import { PricingTable } from '@clerk/clerk-react';

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Page Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Choose Your Plan
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            Start with a 14-day free trial. No credit card required initially.
          </p>
          <p className="text-lg text-gray-500 dark:text-gray-400 mt-2">
            Save 17% with annual billing (~2 months free)
          </p>
        </div>

        {/* Clerk Pricing Table */}
        <PricingTable
          appearance={{
            elements: {
              card: 'border-2 hover:border-blue-500 transition-all',
              cardHeader: 'text-center',
              priceText: 'text-3xl font-bold',
              featuresContainer: 'space-y-3',
            },
          }}
        />

        {/* Additional Info */}
        <div className="mt-12 text-center">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            All plans include a 14-day free trial • Cancel anytime • Secure payment by Stripe
          </p>
        </div>
      </div>
    </div>
  );
}
```

#### 2.3 Add Interval Toggle (Optional)

If you want a manual monthly/annual toggle:

```jsx
import { useState } from 'react';
import { PricingTable } from '@clerk/clerk-react';

export default function PricingPage() {
  const [interval, setInterval] = useState('monthly'); // or 'yearly'

  return (
    <div>
      {/* Interval Toggle */}
      <div className="flex justify-center mb-8">
        <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
          <button
            onClick={() => setInterval('monthly')}
            className={`px-6 py-2 rounded-md transition-all ${
              interval === 'monthly'
                ? 'bg-white dark:bg-gray-700 shadow-md'
                : 'text-gray-600 dark:text-gray-400'
            }`}
          >
            Monthly
          </button>
          <button
            onClick={() => setInterval('yearly')}
            className={`px-6 py-2 rounded-md transition-all ${
              interval === 'yearly'
                ? 'bg-white dark:bg-gray-700 shadow-md'
                : 'text-gray-600 dark:text-gray-400'
            }`}
          >
            Annual
            <span className="ml-2 text-sm text-green-600 font-semibold">Save 17%</span>
          </button>
        </div>
      </div>

      {/* Pricing Table - Clerk will show appropriate plans */}
      <PricingTable />
    </div>
  );
}
```

#### 2.4 Subscription Management

Update SubscriptionPage to use Clerk's built-in profile:

```jsx
import { UserProfile } from '@clerk/clerk-react';

export default function SubscriptionPage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Manage Subscription</h1>

        {/* Clerk's UserProfile includes subscription management */}
        <UserProfile
          appearance={{
            elements: {
              rootBox: 'w-full',
              card: 'w-full shadow-lg',
            },
          }}
        />
      </div>
    </div>
  );
}
```

#### 2.5 Feature Gating with `has()`

Check user's subscription tier and features:

```jsx
import { useUser } from '@clerk/clerk-react';

export function FeatureGuard({ feature, children, fallback }) {
  const { user } = useUser();

  // Check if user has the required feature
  const hasFeature =
    user?.publicMetadata?.subscription?.features?.includes(feature) ||
    user?.has?.({ permission: feature });

  if (!hasFeature) {
    return (
      fallback || (
        <div className="p-4 bg-gray-100 rounded-lg text-center">
          <p className="text-gray-600">Upgrade to access this feature</p>
          <button
            onClick={() => (window.location.href = '/pricing')}
            className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-md"
          >
            View Plans
          </button>
        </div>
      )
    );
  }

  return children;
}

// Usage
<FeatureGuard feature="feature:ai_insights">
  <AIInsightsPanel />
</FeatureGuard>;
```

### Phase 3: Backend Integration (Minimal)

Since Clerk handles billing, backend needs minimal changes:

#### 3.1 Clerk Webhook Handler

Keep existing Clerk webhook handler, add subscription event handling:

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
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]

    # Handle subscription events
    if event_type == "subscription.created":
        user_id = event["data"]["user_id"]
        plan = event["data"]["plan"]
        # Update user's subscription in your database
        update_user_subscription(db, user_id, plan)

    elif event_type == "subscription.updated":
        user_id = event["data"]["user_id"]
        plan = event["data"]["plan"]
        update_user_subscription(db, user_id, plan)

    elif event_type == "subscription.deleted":
        user_id = event["data"]["user_id"]
        remove_user_subscription(db, user_id)

    return {"success": True}
```

#### 3.2 Subscription Check Middleware (Optional)

Add middleware to check subscription status:

```python
from functools import wraps
from fastapi import HTTPException

def require_subscription(tier: str = None, feature: str = None):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user from request context
            user = kwargs.get('current_user')

            if tier:
                if user.subscription_tier != tier:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Requires {tier} subscription"
                    )

            if feature:
                if feature not in user.subscription_features:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Requires {feature} feature"
                    )

            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@router.get("/api/v1/advanced-analytics")
@require_subscription(feature="feature:advanced_analytics")
async def get_advanced_analytics(current_user: User = Depends(get_current_user)):
    # Only users with advanced_analytics feature can access
    pass
```

### Phase 4: Testing

#### 4.1 Test Monthly Subscriptions

1. Navigate to `/pricing`
2. Select "Solo Dealmaker (Monthly)"
3. Complete checkout (use Stripe test card)
4. Verify 14-day trial starts
5. Check subscription in user profile
6. Verify features are accessible

#### 4.2 Test Annual Subscriptions

1. Navigate to `/pricing`
2. Toggle to "Annual" billing
3. Select "Growth Firm (Annual)"
4. Verify price shows $7,980/year with discount
5. Complete checkout
6. Verify annual subscription created

#### 4.3 Test Trial Period

1. Start new subscription with trial
2. Verify access to paid features during trial
3. Check trial expiration date
4. Test trial cancellation
5. Verify downgrade to free plan after cancellation

#### 4.4 Test Upgrades/Downgrades

1. Subscribe to Solo Dealmaker
2. Upgrade to Growth Firm
3. Verify immediate access to new features
4. Downgrade back to Solo Dealmaker
5. Verify downgrade takes effect at period end

### Phase 5: Deployment

#### 5.1 Environment Variables

**Frontend (.env.local):**

```env
VITE_CLERK_PUBLISHABLE_KEY=pk_live_[YOUR_KEY]
```

**Backend (.env):**

```env
CLERK_SECRET_KEY=sk_live_[YOUR_KEY]
CLERK_WEBHOOK_SECRET=whsec_[YOUR_SECRET]
```

#### 5.2 Clerk Dashboard Configuration

- [ ] Stripe account connected
- [ ] All plans created (6 total: 3 tiers × 2 intervals)
- [ ] Features/entitlements configured
- [ ] Trial period set to 14 days
- [ ] Webhooks configured
- [ ] Billing enabled for production

#### 5.3 Deploy to Render

```bash
git add .
git commit -m "feat: Migrate to Clerk native billing with annual options"
git push origin master
```

## Migration from Custom Stripe Integration

### Files to Remove/Update

**Remove (No longer needed):**

- `frontend/src/components/billing/CheckoutButton.tsx` - Replaced by Clerk's PricingTable
- `frontend/src/components/billing/SubscriptionManager.tsx` - Replaced by UserProfile
- `frontend/src/hooks/useSubscription.ts` - Use Clerk's useUser() instead
- `frontend/src/pages/SubscriptionSuccessPage.jsx` - Clerk handles this
- `frontend/src/pages/SubscriptionCancelPage.jsx` - Clerk handles this
- `backend/app/api/payments.py` - Clerk handles payments

**Update:**

- `frontend/src/pages/PricingPage.jsx` - Use `<PricingTable />`
- `frontend/src/pages/SubscriptionPage.jsx` - Use `<UserProfile />`
- `frontend/src/App.jsx` - Remove custom subscription routes

### Data Migration

If you have existing subscribers:

1. Export subscription data from Stripe
2. Import into Clerk Dashboard
3. Clerk will sync with Stripe automatically
4. Users can manage subscriptions through Clerk UI

## Pricing Calculations

### Monthly Pricing

- **Solo Dealmaker:** $279/month
- **Growth Firm:** $798/month
- **Enterprise:** $1,598/month

### Annual Pricing (17% discount)

- **Solo Dealmaker:** $2,790/year ($279 × 10 months)
- **Growth Firm:** $7,980/year ($798 × 10 months)
- **Enterprise:** $15,980/year ($1,598 × 10 months)

### Savings Breakdown

- **Solo Dealmaker:** Save $558/year (2 months free)
- **Growth Firm:** Save $1,596/year (2 months free)
- **Enterprise:** Save $3,196/year (2 months free)

## Benefits Summary

### For Users

✅ 14-day free trial on all plans
✅ Simple one-click subscription
✅ Manage billing in familiar Clerk interface
✅ Save 17% with annual billing
✅ Cancel anytime, no hassle
✅ Secure Stripe payment processing

### For Developers

✅ No custom payment backend code
✅ No webhook handlers to maintain
✅ Drop-in UI components
✅ Automatic entitlement management
✅ Built-in subscription management
✅ Clerk Dashboard for plan configuration

### For Business

✅ Predictable annual revenue with annual plans
✅ Lower churn from annual subscribers
✅ Competitive pricing with trial period
✅ Industry-standard 17% annual discount
✅ Professional billing UX
✅ Faster time to market

## Timeline

- **Phase 1 (Clerk Setup):** 1-2 hours
- **Phase 2 (Frontend):** 2-3 hours
- **Phase 3 (Backend):** 1 hour
- **Phase 4 (Testing):** 2-3 hours
- **Phase 5 (Deployment):** 30 minutes

**Total Estimated Time:** 6-10 hours

## Next Steps

1. ✅ Review this implementation plan
2. ⏳ Set up pricing plans in Clerk Dashboard
3. ⏳ Update frontend components to use Clerk Billing
4. ⏳ Test in development
5. ⏳ Deploy to production
6. ⏳ Monitor and iterate

---

**Status:** Ready for Implementation
**Last Updated:** October 12, 2025
**Approach:** Clerk Native Billing (Beta)
