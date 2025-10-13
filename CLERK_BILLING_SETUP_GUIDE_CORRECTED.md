# 🎯 Clerk Billing Setup Guide - Exact Step-by-Step

**Updated:** October 2025
**Based on:** Actual Clerk Dashboard Interface

---

## 📌 Before You Start

### ⚠️ Important Notes:

1. **Currency:** Verify your Stripe integration currency (USD vs GBP)
2. **All plans require 14-day free trial** - Set this for every plan
3. **Features are NOT hierarchical** - You must manually duplicate features from lower tiers
4. **Plan creation order matters** - Create in the order below for best display

---

## 🚀 Step 1: Access Clerk Dashboard

1. Navigate to: https://dashboard.clerk.com
2. Select your project: **BMAD / MA SaaS Platform**
3. Go to: **Configure** → **Billing** → **Subscription plans**
4. Click: **"Create Plan"** button (top right)

---

## 📝 Step 2: Create All 8 Plans

### ✅ PLAN 1: Solo Dealmaker (Monthly)

**Click "Create Plan" and fill in:**

```
┌─────────────────────────────────────────────┐
│ Basic information                           │
├─────────────────────────────────────────────┤
│ Name:                                       │
│ Solo Dealmaker (Monthly)                    │
│                                             │
│ Key:                                        │
│ solo_dealmaker_monthly                      │
│                                             │
│ Description:                                │
│ Full M&A platform access with essential     │
│ community membership and monthly            │
│ networking webinars                         │
│                                             │
│ Monthly base fee:                           │
│ $ 279.00                                    │
│ ☐ Customers will be charged in USD         │
│                                             │
│ ☐ Annual discount - Monthly base fee       │
│   (Leave UNCHECKED for monthly-only)        │
│                                             │
│ ☑ Free trial                                │
│   Delay billing new customers for a set     │
│   number of days.                           │
│   14 Days                                   │
│                                             │
│ ☑ Publicly available                        │
│   Will appear on the <PricingTable />       │
│   and <UserProfile /> components.           │
└─────────────────────────────────────────────┘
```

**Then scroll to Features section:**

Click **"+ Add feature"** button 5 times and fill in:

```
┌─────────────────────────────────────────────┐
│ Features                                    │
├─────────────────────────────────────────────┤
│                                             │
│ ═ Full M&A Platform Access              ⚙ ─│
│   Complete deal management and AI           │
│   analysis tools                            │
│                                             │
│ ═ Essential Community Membership        ⚙ ─│
│   Access to professional networking and     │
│   discussions                               │
│                                             │
│ ═ Monthly Networking Webinars           ⚙ ─│
│   Monthly live networking events and        │
│   masterclasses                             │
│                                             │
│ ═ AI-Powered Deal Analysis              ⚙ ─│
│   Claude + OpenAI integration for           │
│   intelligent insights                      │
│                                             │
│ ═ Basic Masterclass Library             ⚙ ─│
│   Access to archived educational content    │
│                                             │
│         + Add feature                       │
└─────────────────────────────────────────────┘
```

**Click "Create plan" button at the bottom**

---

### ✅ PLAN 2: Solo Dealmaker (Annual)

**Click "Create Plan" again:**

```
┌─────────────────────────────────────────────┐
│ Basic information                           │
├─────────────────────────────────────────────┤
│ Name:                                       │
│ Solo Dealmaker (Annual)                     │
│                                             │
│ Key:                                        │
│ solo_dealmaker_annual                       │
│                                             │
│ Description:                                │
│ Annual Solo Dealmaker plan with 17%         │
│ savings - Save £558 annually                │
│                                             │
│ Monthly base fee:                           │
│ $ 279.00                                    │
│ ☐ Customers will be charged in USD         │
│                                             │
│ ☑ Annual discount - Monthly base fee       │
│   $ 232.50                                  │
│   Based on a $232.50/mo fee, billed         │
│   annually as: $2,790.00/yr                 │
│                                             │
│ ☑ Free trial                                │
│   14 Days                                   │
│                                             │
│ ☑ Publicly available                        │
└─────────────────────────────────────────────┘
```

**Features:** Copy all 5 features from Solo Dealmaker (Monthly):

1. Full M&A Platform Access
2. Essential Community Membership
3. Monthly Networking Webinars
4. AI-Powered Deal Analysis
5. Basic Masterclass Library

**Click "Create plan"**

---

### ✅ PLAN 3: Growth Firm (Monthly)

**Click "Create Plan":**

```
┌─────────────────────────────────────────────┐
│ Basic information                           │
├─────────────────────────────────────────────┤
│ Name:                                       │
│ Growth Firm (Monthly)                       │
│                                             │
│ Key:                                        │
│ growth_firm_monthly                         │
│                                             │
│ Description:                                │
│ Advanced M&A platform with professional     │
│ community membership and VIP event access   │
│                                             │
│ Monthly base fee:                           │
│ $ 798.00                                    │
│                                             │
│ ☐ Annual discount - Monthly base fee       │
│   (Leave UNCHECKED)                         │
│                                             │
│ ☑ Free trial                                │
│   14 Days                                   │
│                                             │
│ ☑ Publicly available                        │
└─────────────────────────────────────────────┘
```

**Features:** Add all 12 features (5 from Solo + 7 new):

**First, copy these 5 from Solo Dealmaker:**

1. Full M&A Platform Access
2. Essential Community Membership
3. Monthly Networking Webinars
4. AI-Powered Deal Analysis
5. Basic Masterclass Library

**Then add these 7 NEW features:**

```
6. ═ Advanced Team Collaboration           ⚙ ─
   Multi-user workspaces and role-based
   permissions

7. ═ Professional Community Membership     ⚙ ─
   Priority networking and exclusive member
   connections

8. ═ All Events + VIP Networking          ⚙ ─
   Access to all events plus VIP networking
   opportunities

9. ═ Priority AI-Powered Introductions    ⚙ ─
   AI-matched strategic partnerships and
   connections

10. ═ Exclusive Deal Opportunities        ⚙ ─
    Access to member-only investment
    opportunities

11. ═ Monthly Mastermind Sessions         ⚙ ─
    Small group expert-led strategy sessions
```

**Click "Create plan"**

---

### ✅ PLAN 4: Growth Firm (Annual)

**Click "Create Plan":**

```
┌─────────────────────────────────────────────┐
│ Basic information                           │
├─────────────────────────────────────────────┤
│ Name:                                       │
│ Growth Firm (Annual)                        │
│                                             │
│ Key:                                        │
│ growth_firm_annual                          │
│                                             │
│ Description:                                │
│ Annual Growth Firm plan with 17% savings   │
│ - Save £1,596 annually                      │
│                                             │
│ Monthly base fee:                           │
│ $ 798.00                                    │
│                                             │
│ ☑ Annual discount - Monthly base fee       │
│   $ 665.00                                  │
│   Based on a $665.00/mo fee, billed         │
│   annually as: $7,980.00/yr                 │
│                                             │
│ ☑ Free trial                                │
│   14 Days                                   │
│                                             │
│ ☑ Publicly available                        │
└─────────────────────────────────────────────┘
```

**Features:** Copy all 12 features from Growth Firm (Monthly)

**Click "Create plan"**

---

### ✅ PLAN 5: Enterprise (Monthly)

**Click "Create Plan":**

```
┌─────────────────────────────────────────────┐
│ Basic information                           │
├─────────────────────────────────────────────┤
│ Name:                                       │
│ Enterprise (Monthly)                        │
│                                             │
│ Key:                                        │
│ enterprise_monthly                          │
│                                             │
│ Description:                                │
│ White-label M&A platform with executive     │
│ community membership and private event      │
│ hosting                                     │
│                                             │
│ Monthly base fee:                           │
│ $ 1598.00                                   │
│                                             │
│ ☐ Annual discount - Monthly base fee       │
│   (Leave UNCHECKED)                         │
│                                             │
│ ☑ Free trial                                │
│   14 Days                                   │
│                                             │
│ ☑ Publicly available                        │
└─────────────────────────────────────────────┘
```

**Features:** Add all 19 features (12 from Growth Firm + 7 new):

**First, copy all 12 features from Growth Firm**

**Then add these 7 NEW features:**

```
13. ═ White-Label Platform Access          ⚙ ─
    Custom branding and white-label
    deployment

14. ═ Executive Community Membership       ⚙ ─
    C-suite level networking and strategic
    connections

15. ═ Private Events + Hosting Rights      ⚙ ─
    Host exclusive events and access private
    sessions

16. ═ Custom Branding & API Access         ⚙ ─
    Full customization and programmatic
    access

17. ═ Direct Deal Syndication              ⚙ ─
    Lead and participate in exclusive deal
    syndication

18. ═ Investment Committee Access          ⚙ ─
    Direct access to investment committees
    and LPs
```

**Click "Create plan"**

---

### ✅ PLAN 6: Enterprise (Annual)

**Click "Create Plan":**

```
┌─────────────────────────────────────────────┐
│ Basic information                           │
├─────────────────────────────────────────────┤
│ Name:                                       │
│ Enterprise (Annual)                         │
│                                             │
│ Key:                                        │
│ enterprise_annual                           │
│                                             │
│ Description:                                │
│ Annual Enterprise plan with 17% savings    │
│ - Save £3,196 annually                      │
│                                             │
│ Monthly base fee:                           │
│ $ 1598.00                                   │
│                                             │
│ ☑ Annual discount - Monthly base fee       │
│   $ 1331.67                                 │
│   Based on a $1,331.67/mo fee, billed       │
│   annually as: $15,980.04/yr                │
│                                             │
│ ☑ Free trial                                │
│   14 Days                                   │
│                                             │
│ ☑ Publicly available                        │
└─────────────────────────────────────────────┘
```

**Features:** Copy all 19 features from Enterprise (Monthly)

**Click "Create plan"**

---

### ✅ PLAN 7: Community Leader (Monthly)

**Click "Create Plan":**

```
┌─────────────────────────────────────────────┐
│ Basic information                           │
├─────────────────────────────────────────────┤
│ Name:                                       │
│ Community Leader (Monthly)                  │
│                                             │
│ Key:                                        │
│ community_leader_monthly                    │
│                                             │
│ Description:                                │
│ Premium tier with revenue sharing,          │
│ leadership roles, and exclusive LP          │
│ introductions                               │
│                                             │
│ Monthly base fee:                           │
│ $ 2997.00                                   │
│                                             │
│ ☐ Annual discount - Monthly base fee       │
│   (Leave UNCHECKED)                         │
│                                             │
│ ☑ Free trial                                │
│   14 Days                                   │
│                                             │
│ ☑ Publicly available                        │
└─────────────────────────────────────────────┘
```

**Features:** Add all 25 features (19 from Enterprise + 6 new):

**First, copy all 19 features from Enterprise**

**Then add these 6 NEW features:**

```
20. ═ Revenue Share on Hosted Events       ⚙ ─
    Earn 20% revenue share on events you
    host

21. ═ Personal Deal Showcase Platform      ⚙ ─
    Dedicated platform to showcase your
    deals and expertise

22. ═ Mentor Program Leadership            ⚙ ─
    Lead mentor programs and guide other
    members

23. ═ Direct LP and Investor Introductions ⚙ ─
    Personal introductions to LPs and
    institutional investors

24. ═ Community Influence and Recognition  ⚙ ─
    Leadership status and community-wide
    recognition
```

**Click "Create plan"**

---

### ✅ PLAN 8: Community Leader (Annual)

**Click "Create Plan":**

```
┌─────────────────────────────────────────────┐
│ Basic information                           │
├─────────────────────────────────────────────┤
│ Name:                                       │
│ Community Leader (Annual)                   │
│                                             │
│ Key:                                        │
│ community_leader_annual                     │
│                                             │
│ Description:                                │
│ Annual Community Leader plan with 17%       │
│ savings - Save £5,994 annually              │
│                                             │
│ Monthly base fee:                           │
│ $ 2997.00                                   │
│                                             │
│ ☑ Annual discount - Monthly base fee       │
│   $ 2497.50                                 │
│   Based on a $2,497.50/mo fee, billed       │
│   annually as: $29,970.00/yr                │
│                                             │
│ ☑ Free trial                                │
│   14 Days                                   │
│                                             │
│ ☑ Publicly available                        │
└─────────────────────────────────────────────┘
```

**Features:** Copy all 25 features from Community Leader (Monthly)

**Click "Create plan"**

---

## ✅ Step 3: Verify Your Plans

Go back to **Configure** → **Billing** → **Subscription plans**

You should see this list:

```
┌──────────────────────────────────────────────────────────────┐
│ Subscription plans                         Create Plan        │
├──────────────────────────────────────────────────────────────┤
│ Plan                          Plan Key              Monthly   │
├──────────────────────────────────────────────────────────────┤
│ Solo Dealmaker (Monthly)      solo_dealmaker_monthly $279.00  │
│ ⟳ Billed monthly              14 days trial                   │
│                                                                │
│ Solo Dealmaker (Annual)       solo_dealmaker_annual  $232.50  │
│ ⟳ Billed monthly or annually  14 days trial                   │
│                                                                │
│ Growth Firm (Monthly)         growth_firm_monthly    $798.00  │
│ ⟳ Billed monthly              14 days trial                   │
│                                                                │
│ Growth Firm (Annual)          growth_firm_annual     $665.00  │
│ ⟳ Billed monthly or annually  14 days trial                   │
│                                                                │
│ Enterprise (Monthly)          enterprise_monthly    $1,598.00 │
│ ⟳ Billed monthly              14 days trial                   │
│                                                                │
│ Enterprise (Annual)           enterprise_annual     $1,331.67 │
│ ⟳ Billed monthly or annually  14 days trial                   │
│                                                                │
│ Community Leader (Monthly)    community_leader...   $2,997.00 │
│ ⟳ Billed monthly              14 days trial                   │
│                                                                │
│ Community Leader (Annual)     community_leader...   $2,497.50 │
│ ⟳ Billed monthly or annually  14 days trial                   │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔧 Step 4: Configure Global Settings

### Payment Settings

1. Go to **Configure** → **Billing** → **Stripe**
2. Ensure your Stripe account is connected
3. Verify payment methods are enabled

### Webhook Configuration

1. Go to **Configure** → **Webhooks**
2. Ensure these events are enabled:
   - `user.subscription.created`
   - `user.subscription.updated`
   - `user.subscription.deleted`

### Tax Settings (If applicable)

1. Go to your **Stripe Dashboard**
2. Navigate to **Settings** → **Tax**
3. Enable automatic tax collection if required

---

## 📊 Step 5: Test the Plans

### Frontend Integration

Add this to your pricing page:

```jsx
import { PricingTable } from '@clerk/clerk-react';

export default function PricingPage() {
  return (
    <div>
      <h1>Choose Your Plan</h1>
      <PricingTable />
    </div>
  );
}
```

### Test Flow:

1. ✅ Visit your pricing page
2. ✅ Verify all 8 plans appear
3. ✅ Click "Subscribe" on a plan
4. ✅ Confirm 14-day trial is offered
5. ✅ Complete test payment with Stripe test card: `4242 4242 4242 4242`
6. ✅ Verify subscription appears in user profile

---

## 📋 Quick Reference: Feature Count Per Plan

| Plan             | Total Features           |
| ---------------- | ------------------------ |
| Solo Dealmaker   | 5 features               |
| Growth Firm      | 12 features (5 + 7 new)  |
| Enterprise       | 19 features (12 + 7 new) |
| Community Leader | 25 features (19 + 6 new) |

---

## 🚨 Common Issues & Solutions

### Issue 1: Currency Mismatch

**Problem:** Plans show USD but you want GBP
**Solution:**

1. Go to Stripe Dashboard → Settings → Account details
2. Change default currency to GBP
3. Recreate plans in Clerk

### Issue 2: Annual Plans Not Linking

**Problem:** Monthly and annual plans don't show as related
**Solution:** Ensure plan keys follow the pattern:

- `plan_name_monthly`
- `plan_name_annual`

### Issue 3: Features Not Appearing

**Problem:** Features don't display in `<PricingTable />`
**Solution:**

1. Verify "Publicly available" is checked
2. Clear browser cache
3. Restart development server

---

## ✅ Completion Checklist

- [ ] All 8 plans created
- [ ] All features added to each plan
- [ ] 14-day trial set on all plans
- [ ] "Publicly available" enabled on all plans
- [ ] Stripe integration verified
- [ ] Webhooks configured
- [ ] Test subscription completed
- [ ] Plans appear in `<PricingTable />` component

---

## 🎉 You're Done!

Your Clerk billing is now fully configured with all 8 subscription plans. Users can now:

1. Browse plans on your pricing page
2. Start 14-day free trials
3. Subscribe via Stripe
4. Upgrade/downgrade between tiers
5. Switch between monthly and annual billing

---

## 🎯 Advanced Configuration Settings

### Feature Gating Setup

After creating plans, configure feature access in your application:

```typescript
// Check if user has specific feature access
const { user } = useUser();
const hasFeature = user?.publicMetadata?.subscription?.features?.includes('feature_name');

// Example: Check for AI analysis access
const hasAIAnalysis = user?.publicMetadata?.subscription?.features?.includes('ai_analysis');

// Example: Check subscription tier
const subscriptionTier = user?.publicMetadata?.subscription?.planSlug;
const isEnterprise = subscriptionTier?.includes('enterprise');
```

### Plan Display Order

Ensure plans display in this order on your pricing page:

1. Solo Dealmaker (Monthly/Annual)
2. Growth Firm (Monthly/Annual) - Mark as "Most Popular"
3. Enterprise (Monthly/Annual)
4. Community Leader (Monthly/Annual) - Mark as "Premium"

### Proration Settings

1. Go to **Configure** → **Billing** → **Settings**
2. Enable **"Proration"** for plan upgrades/downgrades
3. Set proration mode:
   - **Create prorations:** Charge/credit immediately when users change plans
   - **Always invoice:** Include proration in next invoice

---

## 🎪 Event Integration Setup

### Additional Event Pricing (Outside Subscriptions)

**Configure these as separate Eventbrite events:**

1. **M&A Masterclass Series:** £497/event
2. **Due Diligence Intensive:** £997/event
3. **Private Equity Bootcamp:** £1,997/event
4. **Deal Syndication Summit:** £2,997/event

### Event Access Logic

Implement this in your application code:

```typescript
// Event discount logic based on subscription tier
const getEventDiscount = (planSlug: string) => {
  if (planSlug?.includes('community_leader')) {
    return 1.0; // 100% discount (free) + hosting revenue share
  }
  if (planSlug?.includes('enterprise')) {
    return 1.0; // 100% discount (free access to most events)
  }
  if (planSlug?.includes('growth_firm') || planSlug?.includes('solo_dealmaker')) {
    return 0.5; // 50% discount on premium events
  }
  return 0; // No discount for free tier
};
```

**Event Access by Tier:**

- **Solo/Growth Members:** 50% discount on premium events
- **Enterprise Members:** Free access to most events
- **Community Leaders:** Free access + 20% hosting revenue share

---

## 🚀 Launch Checklist

### Pre-Launch Testing

- [ ] Test each plan subscription flow
- [ ] Verify annual discount calculations are correct (17% savings)
- [ ] Ensure all features are properly assigned to each plan
- [ ] Test plan upgrades (Solo → Growth → Enterprise → Community Leader)
- [ ] Test plan downgrades with proration
- [ ] Test trial period (14 days) → conversion flow
- [ ] Test payment with Stripe test cards:
  - Success: `4242 4242 4242 4242`
  - Decline: `4000 0000 0000 0002`
  - 3D Secure: `4000 0027 6000 3184`

### Post-Setup Configuration

- [ ] Configure feature gating in application code
- [ ] Update website pricing page with all 8 plans
- [ ] Test `<PricingTable />` component display
- [ ] Add "Most Popular" badge to Growth Firm plans
- [ ] Add "Premium" badge to Community Leader plans
- [ ] Set up conversion tracking and analytics
- [ ] Configure subscription confirmation emails
- [ ] Test webhook events (subscription.created, updated, deleted)
- [ ] Enable Stripe Customer Portal for self-service management

### Marketing & Display

- [ ] Add pricing comparison table to website
- [ ] Highlight annual savings (£558 - £5,994)
- [ ] Create FAQ section for billing questions
- [ ] Add testimonials near pricing tiers
- [ ] Set up A/B testing for pricing page
- [ ] Configure exit-intent offers for trial sign-ups

---

## 💡 Pro Tips for Setup

### 1. Plan Creation Order

Create in the exact order listed (Solo → Growth → Enterprise → Community Leader) for optimal customer flow and dashboard display.

### 2. Feature Naming Consistency

Use snake_case for all feature names (e.g., `ai_analysis`, `team_collaboration`) for easier code integration and consistency.

### 3. Description Best Practices

- Keep descriptions clear and benefit-focused
- Use action words (e.g., "Access", "Earn", "Lead")
- Highlight unique value proposition for each tier
- Mention specific numbers where relevant (e.g., "20% revenue share")

### 4. Annual Incentive Emphasis

Emphasize the substantial savings:

- Solo: Save £558 annually (17% discount)
- Growth: Save £1,596 annually (17% discount)
- Enterprise: Save £3,196 annually (17% discount)
- Community Leader: Save £5,994 annually (17% discount)

### 5. Trial Period Strategy

14 days provides enough time for:

- Full platform evaluation
- Attending 1-2 webinars/events
- Testing AI analysis features
- Experiencing community membership
- Making informed purchase decision

### 6. Upgrade Path Design

Make it frictionless to upgrade:

- Show "Upgrade" buttons prominently in user dashboard
- Display locked features with "Upgrade to unlock" messaging
- Offer prorated upgrades (pay only the difference)
- Send targeted upgrade emails at key moments

### 7. Currency Considerations

If targeting UK market primarily:

- Set Stripe default currency to GBP
- Display prices in £ throughout application
- Enable automatic VAT collection
- Consider adding USD pricing for international customers

---

## 📊 Revenue Projections with New Model

### Conservative Growth Scenario:

**Month 1:**

- 20 Solo Dealmaker × £279 = £5,580
- 10 Growth Firm × £798 = £7,980
- 2 Enterprise × £1,598 = £3,196
- **Total: £16,756 MRR** (vs £2,500 with basic SaaS)

**Month 3:**

- 50 Solo Dealmaker × £279 = £13,950
- 30 Growth Firm × £798 = £23,940
- 8 Enterprise × £1,598 = £12,784
- 2 Community Leader × £2,997 = £5,994
- **Total: £56,668 MRR** (vs £10,000 with basic SaaS)

**Month 12:**

- 150 Solo Dealmaker × £279 = £41,850
- 100 Growth Firm × £798 = £79,800
- 30 Enterprise × £1,598 = £47,940
- 10 Community Leader × £2,997 = £29,970
- **Total: £199,560 MRR (£2.4M ARR)**

### With Annual Conversions (30% of customers):

**Year 1 ARR:** £2.8M - £3.2M
**Year 2 ARR:** £8M - £10M
**Year 3 ARR:** £25M+ (With network effects and event revenue)

---

## 🎯 Success Metrics to Track

### Subscription KPIs:

- [ ] Free trial → paid conversion rate (target: 40%+)
- [ ] Monthly → annual conversion rate (target: 30%+)
- [ ] Upgrade rate (Solo → Growth) (target: 20%+)
- [ ] Upgrade rate (Growth → Enterprise) (target: 10%+)
- [ ] Churn rate per tier (target: <5% monthly)
- [ ] Average revenue per user (ARPU)
- [ ] Customer lifetime value (LTV)
- [ ] LTV:CAC ratio (target: 3:1 or higher)

### Community Engagement KPIs:

- [ ] Event attendance rate per tier
- [ ] Community forum participation
- [ ] Networking connection rate
- [ ] Deal flow activity
- [ ] Mentor-mentee matches (Community Leader tier)

---

## 🔧 Troubleshooting Advanced Issues

### Issue 4: Proration Not Working

**Problem:** Users don't see credits when downgrading
**Solution:**

1. Go to Stripe Dashboard → Settings → Billing
2. Enable "Proration"
3. Set to "Create prorations" mode
4. Test with Stripe test mode first

### Issue 5: Trial Not Counting Down

**Problem:** Trial days don't decrease
**Solution:**

1. Verify Stripe subscription object has `trial_end` timestamp
2. Check webhook event `customer.subscription.trial_will_end`
3. Ensure frontend calculates days remaining correctly

### Issue 6: Multiple Subscriptions per User

**Problem:** Users can subscribe to multiple plans
**Solution:**

```typescript
// Add check before allowing new subscription
const { user } = useUser();
const existingSubscription = user?.publicMetadata?.subscription;

if (existingSubscription?.status === 'active') {
  // Prompt user to upgrade/downgrade instead
  showUpgradeModal();
} else {
  // Allow new subscription
  proceedToCheckout();
}
```

### Issue 7: Feature Access Not Updating

**Problem:** Features don't unlock immediately after subscription
**Solution:**

1. Verify webhook `user.subscription.updated` is firing
2. Check webhook handler updates user metadata
3. Clear user session cache
4. Force session refresh with `await user.reload()`

---

## 📚 Additional Resources

### Clerk Documentation:

- Billing & Subscriptions: https://clerk.com/docs/billing
- Webhooks: https://clerk.com/docs/webhooks
- User Metadata: https://clerk.com/docs/users/metadata

### Stripe Documentation:

- Subscriptions: https://stripe.com/docs/billing/subscriptions
- Trials: https://stripe.com/docs/billing/subscriptions/trials
- Proration: https://stripe.com/docs/billing/subscriptions/prorations

### Implementation Examples:

```typescript
// Example: Check subscription status
import { useUser } from '@clerk/clerk-react';

export function useSubscription() {
  const { user } = useUser();

  const subscription = user?.publicMetadata?.subscription as {
    planSlug: string;
    status: 'active' | 'trialing' | 'canceled' | 'past_due';
    features: string[];
    trialEndsAt?: number;
  };

  const hasFeature = (feature: string) => {
    return subscription?.features?.includes(feature) ?? false;
  };

  const isTrialing = subscription?.status === 'trialing';
  const isActive = subscription?.status === 'active' || isTrialing;

  const trialDaysRemaining = subscription?.trialEndsAt
    ? Math.ceil((subscription.trialEndsAt - Date.now()) / (1000 * 60 * 60 * 24))
    : 0;

  return {
    subscription,
    hasFeature,
    isTrialing,
    isActive,
    trialDaysRemaining,
  };
}
```

---

## ✅ Final Setup Summary

**Total Setup Time:** 45-60 minutes
**Total Plans:** 8 (4 tiers × 2 billing cycles)
**Total Features:** 25 unique features
**Trial Period:** 14 days for all plans
**Annual Savings:** 17% across all tiers

**Expected Result:** Complete integrated billing system ready for:

- £2.4M+ ARR in Year 1
- £10M+ ARR in Year 2
- Scalable to £200M+ valuation growth
- Multiple revenue streams (SaaS + Community + Events)
- Network effects and viral growth potential

---

## 🎉 Next Steps After Setup

1. **Test everything** - Go through each plan purchase flow
2. **Configure webhooks** - Ensure all subscription events are captured
3. **Implement feature gating** - Lock/unlock features based on subscription
4. **Launch pricing page** - Make plans publicly available
5. **Set up analytics** - Track conversion metrics
6. **Create onboarding flow** - Guide new subscribers through platform
7. **Build upgrade prompts** - Encourage users to upgrade at key moments
8. **Plan marketing campaign** - Announce new pricing tiers
9. **Prepare support documentation** - Answer common billing questions
10. **Monitor and optimize** - Track metrics and adjust pricing/features

---

**Questions?** Check Clerk's documentation at: https://clerk.com/docs/billing

_This setup creates a revolutionary M&A ecosystem with multiple revenue streams, network effects, and premium positioning that justifies the enhanced pricing model._
