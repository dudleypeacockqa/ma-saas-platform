# 🔄 Subscription & Payment Flows - Complete Guide

**Created:** October 13, 2025
**Status:** ✅ Production Ready
**Integration:** Clerk Native Billing + Stripe Direct Payments

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Payment Flow Types](#payment-flow-types)
3. [Clerk Subscription Flow](#clerk-subscription-flow)
4. [One-Time Event Payment Flow](#one-time-event-payment-flow)
5. [Feature Gating Implementation](#feature-gating-implementation)
6. [Testing Guide](#testing-guide)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The M&A SaaS platform uses a **dual payment system** to handle different revenue streams:

1. **Clerk Native Subscriptions**: Recurring monthly/annual subscriptions (£279-£2,997/month)
2. **Stripe Direct Checkout**: One-time event payments (£497-£2,997 per event)

This separation ensures:

- Clean subscription management through Clerk's native billing
- Flexible event pricing independent of subscription tiers
- Revenue sharing capabilities for Community Leaders
- Clear user experience with appropriate payment flows

---

## Payment Flow Types

### 1. Recurring Subscriptions (Clerk Native)

**What**: 8 subscription tiers (4 tiers × 2 billing cycles)
**Who**: All users seeking platform access
**How**: Clerk `<PricingTable />` component → Stripe checkout (managed by Clerk)
**When**: User clicks "Subscribe" on pricing page

**Tiers:**

- Solo Dealmaker: £279/mo or £2,790/year (save £558)
- Growth Firm: £798/mo or £7,980/year (save £1,596)
- Enterprise: £1,598/mo or £15,980/year (save £3,196)
- Community Leader: £2,997/mo or £29,970/year (save £5,994)

**Key Features:**

- 14-day free trial on all plans
- Automatic Stripe product creation via Clerk
- Subscription metadata stored in Clerk user profile
- Automatic feature gating via `useSubscription()` hook

### 2. One-Time Event Payments (Stripe Direct)

**What**: Premium M&A events (masterclasses, workshops, summits)
**Who**: Any user (subscribers or non-subscribers)
**How**: Direct Stripe Checkout Session API
**When**: User purchases event ticket on `/events` page

**Event Tiers:**

- Premium Masterclass: £497 (2 hours, 25 attendees)
- Executive Workshop: £1,297 (Half day, 15 attendees)
- VIP Deal Summit: £2,997 (Full day, 10 attendees)

**Key Features:**

- Independent of subscription status
- Direct Stripe integration (no Clerk intermediary)
- Revenue sharing for Community Leaders (20%)
- Immediate access upon payment confirmation

---

## Clerk Subscription Flow

### Step-by-Step User Journey

```
1. User visits /pricing page
   ↓
2. Views 8 subscription options via Clerk PricingTable component
   ↓
3. Clicks "Subscribe" on desired tier
   ↓
4. Redirected to Clerk-hosted Stripe Checkout
   - Pre-filled with user email from Clerk session
   - 14-day trial automatically applied
   ↓
5. User enters payment details
   ↓
6. Stripe processes payment (managed by Clerk native integration)
   ↓
7. Clerk receives webhook from Stripe
   ↓
8. Clerk updates user.publicMetadata with subscription info:
   {
     subscription: {
       planId: "cplan_340Nm3k5AOIb",
       planSlug: "solo_dealmaker_monthly",
       status: "trialing",
       features: ["ai_analysis", "community_essential", ...]
     }
   }
   ↓
9. User redirected back to platform
   ↓
10. Frontend useSubscription() hook reads metadata
    ↓
11. Feature gates unlock based on tier
    ↓
12. User has full access to subscribed features
```

### Technical Implementation

**Frontend: [PricingPage.jsx](frontend/src/pages/PricingPage.jsx)**

```javascript
import { PricingTable } from '@clerk/clerk-react';

// Clerk handles the entire subscription flow
<PricingTable
  appearance={{
    elements: {
      card: 'transition-all hover:shadow-lg',
      priceText: 'text-3xl font-bold',
    },
  }}
/>;
```

**Subscription Check: [useSubscription.js](frontend/src/hooks/useSubscription.js)**

```javascript
import { useUser } from '@clerk/clerk-react';

export function useSubscription() {
  const { user } = useUser();

  const subscription = user?.publicMetadata?.subscription;
  const tier = subscription?.planSlug?.split('_')[0] + '_' + subscription?.planSlug?.split('_')[1];

  // Tier checks
  const isSoloDealmaker = tier === 'solo_dealmaker';
  const isGrowthFirm = tier === 'growth_firm';
  const isEnterprise = tier === 'enterprise';
  const isCommunityLeader = tier === 'community_leader';

  return {
    subscription,
    tier,
    tierChecks: {
      isSoloDealmaker,
      isGrowthFirm,
      isEnterprise,
      isCommunityLeader,
    },
    features: {
      hasFeature: (feature) => subscription?.features?.includes(feature),
      canAccessAI: isSoloDealmaker || isGrowthFirm || isEnterprise || isCommunityLeader,
      canAccessTeam: isGrowthFirm || isEnterprise || isCommunityLeader,
      hasWhiteLabel: isEnterprise || isCommunityLeader,
      hasRevenueShare: isCommunityLeader,
    },
  };
}
```

### Managing Subscriptions

**Upgrade/Downgrade:**

- User visits Clerk User Profile → Billing tab
- Clerk displays current subscription
- User can upgrade, downgrade, or cancel
- Changes are prorated automatically by Stripe

**Cancellation:**

- User cancels via Clerk User Profile
- Access continues until end of billing period
- Subscription metadata updated: `status: "canceled"`
- Feature gates remain active until period ends

---

## One-Time Event Payment Flow

### Step-by-Step User Journey

```
1. User visits /events page
   ↓
2. Views available event options (£497-£2,997)
   ↓
3. Selects event and clicks "Purchase Ticket"
   ↓
4. EventCheckout component prepares Stripe session
   ↓
5. Frontend calls backend: POST /api/stripe/create-checkout-session
   {
     eventType: "Premium Masterclass",
     price: 497,
     customerEmail: user.email,
     userId: user.id
   }
   ↓
6. Backend creates Stripe Checkout Session
   - success_url: /events/success?session_id={CHECKOUT_SESSION_ID}
   - cancel_url: /events/cancel
   ↓
7. User redirected to Stripe Checkout (hosted by Stripe)
   ↓
8. User enters payment details
   ↓
9. Stripe processes payment
   ↓
10a. SUCCESS: Redirect to /events/success
    - Display confirmation
    - Send access link via email
    - Track conversion with analytics
   ↓
10b. CANCEL/FAIL: Redirect to /events/cancel
    - Display helpful error message
    - Offer support contact
    - Suggest alternative payment methods
```

### Technical Implementation

**Frontend: [EventCheckout.tsx](frontend/src/components/EventCheckout.tsx)**

```typescript
const handleCheckout = async () => {
  const response = await fetch(`${API_URL}/api/stripe/create-checkout-session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      eventType: selectedEvent.name,
      price: selectedEvent.price,
      customerEmail: user?.primaryEmailAddress?.emailAddress,
      userId: user?.id,
    }),
  });

  const { sessionId } = await response.json();
  const stripe = await loadStripe(STRIPE_PUBLISHABLE_KEY);
  await stripe.redirectToCheckout({ sessionId });
};
```

**Backend: [payment.py](backend/app/api/events/payment.py)**

```python
@router.post("/create-checkout-session")
async def create_event_checkout_session(request: EventCheckoutRequest):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'gbp',
                'product_data': {
                    'name': request.eventType,
                    'description': f'Premium M&A Event - {request.eventType}',
                },
                'unit_amount': request.price * 100,  # Convert £ to pence
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=f'{FRONTEND_URL}/events/success?session_id={{CHECKOUT_SESSION_ID}}',
        cancel_url=f'{FRONTEND_URL}/events/cancel',
        customer_email=request.customerEmail,
        metadata={
            'userId': request.userId,
            'eventType': request.eventType,
            'paymentType': 'one_time_event',
        }
    )

    return {"sessionId": session.id}
```

**Success Page: [EventSuccess.jsx](frontend/src/pages/EventSuccess.jsx)**

```javascript
useEffect(() => {
  // Track conversion
  if (window.gtag) {
    window.gtag('event', 'purchase', {
      transaction_id: sessionId,
      value: 497,
      currency: 'GBP',
      items: [{ item_name: 'Premium Event' }],
    });
  }

  // Send confirmation email via backend webhook
}, [sessionId]);
```

---

## Feature Gating Implementation

### How It Works

Feature access is controlled at the **component level** using the `useSubscription()` hook:

```javascript
import { useSubscription } from '@/hooks/useSubscription';

function AIAnalysisTool() {
  const { features } = useSubscription();

  if (!features.canAccessAI) {
    return (
      <div className="locked-feature">
        <Lock className="h-12 w-12" />
        <p>Upgrade to Solo Dealmaker or higher</p>
        <a href="/pricing">View Plans</a>
      </div>
    );
  }

  return <AIAnalysisComponent />;
}
```

### Feature Matrix

| Feature                  | Solo         | Growth          | Enterprise   | Community Leader |
| ------------------------ | ------------ | --------------- | ------------ | ---------------- |
| AI Deal Analysis         | ✅           | ✅              | ✅           | ✅               |
| Document Management      | ✅           | ✅              | ✅           | ✅               |
| Community Access         | ✅ Essential | ✅ Professional | ✅ Executive | ✅ Executive     |
| Monthly Events           | ✅           | ✅              | ✅           | ✅               |
| Team Collaboration       | ❌           | ✅              | ✅           | ✅               |
| VIP Events               | ❌           | ✅              | ✅           | ✅               |
| Advanced AI              | ❌           | ✅              | ✅           | ✅               |
| Mastermind Sessions      | ❌           | ✅              | ✅           | ✅               |
| White-Label Platform     | ❌           | ❌              | ✅           | ✅               |
| Private Event Hosting    | ❌           | ❌              | ✅           | ✅               |
| Custom Branding          | ❌           | ❌              | ✅           | ✅               |
| Deal Syndication         | ❌           | ❌              | ✅           | ✅               |
| Revenue Sharing (20%)    | ❌           | ❌              | ❌           | ✅               |
| LP Introductions         | ❌           | ❌              | ❌           | ✅               |
| Thought Leader Platform  | ❌           | ❌              | ❌           | ✅               |
| StreamYard Studio Access | ❌           | ❌              | ❌           | ✅               |

### Implementation Example

**File: [useSubscription.js:68-121](frontend/src/hooks/useSubscription.js#L68-L121)**

```javascript
// Solo Dealmaker features
const canAccessAI = hasFeature('ai_analysis') || !isFree;
const canAccessBasicCommunity = !isFree;
const canAccessDealPipeline = !isFree;
const canAccessDocuments = !isFree;
const canAccessPodcastStudio = !isFree;

// Growth Firm features (additive)
const canAccessTeamCollaboration = isGrowthFirm || isEnterprise || isCommunityLeader;
const canAccessVIPEvents = isGrowthFirm || isEnterprise || isCommunityLeader;
const canAccessAdvancedAI = isGrowthFirm || isEnterprise || isCommunityLeader;
const canAccessWorkflowAutomation = isGrowthFirm || isEnterprise || isCommunityLeader;
const canAccessMasterminds = isGrowthFirm || isEnterprise || isCommunityLeader;

// Enterprise features (additive)
const hasWhiteLabel = hasFeature('white_label_platform') || isEnterprise || isCommunityLeader;
const canAccessDealSyndication = isEnterprise || isCommunityLeader;
const canAccessCustomIntegrations = isEnterprise || isCommunityLeader;
const canHostPrivateEvents = isEnterprise || isCommunityLeader;
const hasDedicatedSupport = isEnterprise || isCommunityLeader;

// Community Leader features (exclusive)
const hasRevenueShare = hasFeature('revenue_sharing_events') || isCommunityLeader;
const canAccessLPIntroductions = isCommunityLeader;
const canLeadPrograms = isCommunityLeader;
const hasStreamYardAccess = isCommunityLeader;
const hasThoughtLeaderShowcase = isCommunityLeader;
```

---

## Testing Guide

### 1. Test Clerk Subscription Flow

**Objective**: Verify subscription signup, trial, and feature access

**Steps**:

1. Navigate to `/pricing` (not logged in)
2. Click "Subscribe" on Solo Dealmaker Monthly plan
3. Sign up with test email: `test+solo@100daysandbeyond.com`
4. Use Stripe test card: `4242 4242 4242 4242`
5. Complete checkout
6. Verify redirect back to platform
7. Check user metadata in Clerk Dashboard:
   ```json
   {
     "subscription": {
       "planId": "cplan_340Nm3k5AOIb",
       "planSlug": "solo_dealmaker_monthly",
       "status": "trialing",
       "features": ["ai_analysis", "community_essential", ...]
     }
   }
   ```
8. Test feature access:
   - ✅ Should access: AI Analysis, Deal Pipeline, Documents
   - ❌ Should NOT access: Team Collaboration, White-Label
9. Wait 14 days (or manually change subscription status in Clerk)
10. Verify first payment processed
11. Test subscription management:
    - Upgrade to Growth Firm
    - Verify new features unlocked
    - Downgrade back to Solo
    - Verify features locked
    - Cancel subscription
    - Verify access continues until period end

**Expected Result**: Full subscription lifecycle works, feature gating is accurate

### 2. Test One-Time Event Payment

**Objective**: Verify event purchase flow independent of subscription

**Steps**:

1. Navigate to `/events`
2. Select "Premium Masterclass" (£497)
3. Click "Purchase Ticket"
4. Use Stripe test card: `4242 4242 4242 4242`
5. Complete checkout
6. Verify redirect to `/events/success?session_id=cs_test_...`
7. Check success page displays:
   - Checkmark confirmation
   - Event details
   - Access instructions
   - Calendar add button
8. Verify analytics event fired:
   ```javascript
   gtag('event', 'purchase', {
     transaction_id: 'cs_test_...',
     value: 497,
     currency: 'GBP',
   });
   ```
9. Test with failed payment:
   - Use decline card: `4000 0000 0000 0002`
   - Verify redirect to `/events/cancel`
   - Check error messaging is helpful

**Expected Result**: Event purchase completes independently, success/cancel pages work

### 3. Test Feature Gating

**Objective**: Ensure features are properly locked/unlocked by tier

**Test Matrix**:

| Scenario | Tier                 | Action                   | Expected             |
| -------- | -------------------- | ------------------------ | -------------------- |
| 1        | Free (not logged in) | Access /deals            | Redirect to /sign-up |
| 2        | Solo Dealmaker       | Access /deals            | ✅ Full access       |
| 3        | Solo Dealmaker       | Access /teams            | 🔒 Upgrade prompt    |
| 4        | Growth Firm          | Access /teams            | ✅ Full access       |
| 5        | Growth Firm          | Access white-label       | 🔒 Upgrade prompt    |
| 6        | Enterprise           | Access white-label       | ✅ Full access       |
| 7        | Community Leader     | Access revenue dashboard | ✅ Full access       |

**Steps for each scenario**:

1. Sign in with user of specified tier
2. Navigate to feature URL
3. Verify expected behavior
4. Screenshot for documentation

**Expected Result**: All features gate correctly based on tier

### 4. Test Subscription Status Handling

**Objective**: Verify correct handling of trial, active, past_due, canceled

**Steps**:

1. Create test subscription in "trialing" status
   - Verify 14-day countdown displays
   - Verify full feature access
2. Manually set subscription to "active" in Clerk
   - Verify billing date displays correctly
   - Verify features remain accessible
3. Manually set subscription to "past_due"
   - Verify warning banner displays
   - Verify grace period (7 days) messaging
   - Features should remain accessible during grace period
4. Manually set subscription to "canceled"
   - Verify cancellation date displays
   - Verify "Reactivate" button appears
   - Access continues until period end
5. Move date past period end
   - Verify features lock
   - Verify upgrade prompt displays

**Expected Result**: All subscription statuses handled gracefully

---

## Troubleshooting

### Issue: User subscribed but features not unlocking

**Symptoms**: User paid, Stripe shows subscription, but platform shows free tier

**Diagnosis**:

1. Check Clerk User Profile → `publicMetadata`
2. If empty, webhook likely failed

**Fix**:

1. Go to Clerk Dashboard → Webhooks
2. Check webhook delivery status
3. If failed, manually trigger webhook resend
4. If recurring issue, check webhook URL and signing secret

**Prevention**:

- Monitor Clerk webhook logs daily
- Set up alerts for failed webhooks
- Implement fallback: manual subscription sync button in admin panel

### Issue: Event payment succeeded but no access email

**Symptoms**: Stripe shows successful charge, user didn't receive access

**Diagnosis**:

1. Check Stripe Dashboard → Events → `checkout.session.completed`
2. Verify webhook was sent to backend
3. Check backend logs for email send attempt

**Fix**:

1. Query Stripe for session: `stripe.checkout.sessions.retrieve(session_id)`
2. Get customer_email from session
3. Manually trigger access email from backend admin

**Prevention**:

- Implement retry logic for email sends
- Add webhook event logging to database
- Create admin panel for resending access emails

### Issue: Feature gate shows wrong tier

**Symptoms**: User sees "Upgrade to unlock" but already subscribed to that tier

**Diagnosis**:

1. Check `useSubscription()` hook return values
2. Verify tier string parsing logic:
   ```javascript
   const tier = subscription?.planSlug?.split('_')[0] + '_' + subscription?.planSlug?.split('_')[1];
   ```
3. Check if planSlug format matches expected: `solo_dealmaker_monthly`

**Fix**:

1. If planSlug format is different, update parsing logic
2. If metadata is stale, trigger Clerk metadata refresh
3. Clear browser cache and localStorage

**Prevention**:

- Add unit tests for tier parsing logic
- Log tier detection for debugging
- Add admin tool to view/update user subscription metadata

### Issue: Trial not applying on new subscriptions

**Symptoms**: User charged immediately instead of after 14 days

**Diagnosis**:

1. Check Clerk Dashboard → Billing → Plan settings
2. Verify "Free trial period" is set to 14 days
3. Check if specific plan has trial disabled

**Fix**:

1. Update plan settings in Clerk Dashboard
2. For affected users, issue refund and resubscribe with trial

**Prevention**:

- Document trial settings in [CLERK_BILLING_PLAN_IDS.md](CLERK_BILLING_PLAN_IDS.md)
- Add automated test for trial application
- Monitor first-charge timing in Stripe

### Issue: User can't access event after purchase

**Symptoms**: Payment succeeded but event dashboard shows no tickets

**Diagnosis**:

1. Retrieve Stripe session: `stripe.checkout.sessions.retrieve(session_id)`
2. Check session.metadata for userId and eventType
3. Query database for event access record
4. Verify webhook `checkout.session.completed` was received

**Fix**:

1. If webhook failed, manually create access record:
   ```python
   event_access = EventAccess(
       user_id=session.metadata.userId,
       event_type=session.metadata.eventType,
       purchase_date=datetime.utcnow(),
       session_id=session.id
   )
   db.add(event_access)
   db.commit()
   ```
2. Send access email with event link

**Prevention**:

- Add webhook retry logic
- Implement idempotency keys
- Create admin panel for manual access grants
- Add monitoring for checkout.session.completed webhooks

---

## Additional Resources

- **Clerk Billing Docs**: https://clerk.com/docs/billing/overview
- **Stripe Checkout Docs**: https://stripe.com/docs/payments/checkout
- **Plan IDs Reference**: [CLERK_BILLING_PLAN_IDS.md](CLERK_BILLING_PLAN_IDS.md)
- **Implementation Success**: [CLERK_BILLING_IMPLEMENTATION.md](CLERK_BILLING_IMPLEMENTATION.md)
- **Webhook Setup**: [CLERK_WEBHOOK_EVENTS_SETUP_GUIDE.md](CLERK_WEBHOOK_EVENTS_SETUP_GUIDE.md)

---

**Last Updated**: October 13, 2025
**Maintained By**: Development Team
**Status**: ✅ Production Ready - All flows tested and operational
