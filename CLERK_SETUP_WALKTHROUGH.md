# 🎯 Clerk Billing Setup - Interactive Walkthrough

**Estimated Time:** 45-60 minutes
**Last Updated:** October 2025

---

## 📌 Pre-Flight Checklist

Before starting, ensure you have:

- [ ] Clerk Dashboard access: https://dashboard.clerk.com
- [ ] Your project selected (BMAD / MA SaaS Platform)
- [ ] Stripe account connected to Clerk
- [ ] This guide open in a second window/monitor

---

## 🚀 PART 1: SETUP PREPARATION (5 minutes)

### Step 1.1: Access Billing Section

1. Open browser: https://dashboard.clerk.com
2. Click your project name (top left)
3. Navigate: **Configure** → **Billing** → **Subscription plans**
4. You should see: "Create Plan" button (top right)

**Screenshot checkpoint:** You should see a page titled "Subscription plans" with an empty list or existing plans.

---

### Step 1.2: Open Reference Document

Keep this guide open alongside your Clerk dashboard. I recommend:

- **Left side:** Clerk Dashboard (browser)
- **Right side:** This guide (VSCode or second browser window)

Or print out the plan configurations below for quick reference.

---

## 📝 PART 2: CREATE PLANS (30-40 minutes)

### Plan Creation Strategy

We'll create plans in this order:

1. Solo Dealmaker (Monthly) ← **Start here** (5 features)
2. Solo Dealmaker (Annual) ← Copy from #1
3. Growth Firm (Monthly) ← Copy 5 from #1 + add 6 new = 11 total
4. Growth Firm (Annual) ← Copy from #3
5. Enterprise (Monthly) ← Copy 11 from #3 + add 7 new = 18 total
6. Enterprise (Annual) ← Copy from #5
7. Community Leader (Monthly) ← Copy 18 from #5 + add 6 new = 24 total
8. Community Leader (Annual) ← Copy from #7

---

## 🔵 PLAN 1 OF 8: Solo Dealmaker (Monthly)

**⏱️ Time: 5-7 minutes**

### Click "Create Plan" Button

**Fill in these fields EXACTLY:**

```
Name: Solo Dealmaker (Monthly)
```

**Copy this:** `Solo Dealmaker (Monthly)`

```
Key: solo_dealmaker_monthly
```

**Copy this:** `solo_dealmaker_monthly`

```
Description:
Full M&A platform access with essential community membership and monthly networking webinars
```

**Copy this entire paragraph:**

```
Full M&A platform access with essential community membership and monthly networking webinars
```

```
Monthly base fee: $ 279.00
☐ Customers will be charged in USD
```

**Type:** `279` (or `279.00`)

**Annual discount checkbox:** ☐ Leave UNCHECKED

**Free trial:** ☑ CHECK THIS BOX
**Days:** `14`

**Publicly available:** ☑ CHECK THIS BOX

---

### Add 5 Features to Plan 1

**Click "+ Add feature" button 5 times**

**Feature 1:**

```
Name: Full M&A Platform Access
Description: Complete deal management and AI analysis tools
```

**Feature 2:**

```
Name: Essential Community Membership
Description: Access to professional networking and discussions
```

**Feature 3:**

```
Name: Monthly Networking Webinars
Description: Monthly live networking events and masterclasses
```

**Feature 4:**

```
Name: AI-Powered Deal Analysis
Description: Claude + OpenAI integration for intelligent insights
```

**Feature 5:**

```
Name: Basic Masterclass Library
Description: Access to archived educational content
```

**Click "Create plan" button at bottom**

✅ **Plan 1 Complete!** Take a 30-second break.

---

## 🔵 PLAN 2 OF 8: Solo Dealmaker (Annual)

**⏱️ Time: 4-5 minutes** (Faster - you're copying features)

### Click "Create Plan" Button Again

```
Name: Solo Dealmaker (Annual)
Key: solo_dealmaker_annual
Description: Annual Solo Dealmaker plan with 17% savings - Save £558 annually
Monthly base fee: $ 279.00
```

**Annual discount:** ☑ CHECK THIS BOX

```
Discounted rate: $ 232.50
```

(Clerk will calculate: $232.50/mo × 12 = $2,790/year)

**Free trial:** ☑ `14` Days

**Publicly available:** ☑ CHECK

**Features:** Copy all 5 features from Plan 1 (same text)

**Click "Create plan"**

✅ **Plan 2 Complete!** Plans 1 & 2 done. Take a 1-minute break.

---

## 🟢 PLAN 3 OF 8: Growth Firm (Monthly)

**⏱️ Time: 8-10 minutes** (More features)

### Click "Create Plan"

```
Name: Growth Firm (Monthly)
Key: growth_firm_monthly
Description: Advanced M&A platform with professional community membership and VIP event access
Monthly base fee: $ 798.00
```

**Annual discount:** ☐ UNCHECKED

**Free trial:** ☑ `14` Days

**Publicly available:** ☑ CHECK

---

### Add 11 Features (5 existing + 6 new)

**First, copy these 5 from Solo Dealmaker:**

✅ Full M&A Platform Access
✅ Essential Community Membership
✅ Monthly Networking Webinars
✅ AI-Powered Deal Analysis
✅ Basic Masterclass Library

**Then add these 6 NEW features:**

**Feature 6:**

```
Name: Advanced Team Collaboration
Description: Multi-user workspaces and role-based permissions
```

**Feature 7:**

```
Name: Professional Community Membership
Description: Priority networking and exclusive member connections
```

**Feature 8:**

```
Name: All Events + VIP Networking
Description: Access to all events plus VIP networking opportunities
```

**Feature 9:**

```
Name: Priority AI-Powered Introductions
Description: AI-matched strategic partnerships and connections
```

**Feature 10:**

```
Name: Exclusive Deal Opportunities
Description: Access to member-only investment opportunities
```

**Click "Create plan"**

✅ **Plan 3 Complete!** Halfway there! Take a 2-minute break.

---

## 🟢 PLAN 4 OF 8: Growth Firm (Annual)

**⏱️ Time: 5-6 minutes**

```
Name: Growth Firm (Annual)
Key: growth_firm_annual
Description: Annual Growth Firm plan with 17% savings - Save £1,596 annually
Monthly base fee: $ 798.00
```

**Annual discount:** ☑ CHECK

```
Discounted rate: $ 665.00
```

(Clerk calculates: $665/mo × 12 = $7,980/year)

**Free trial:** ☑ `14` Days

**Publicly available:** ☑ CHECK

**Features:** Copy all 11 features from Plan 3

**Click "Create plan"**

✅ **Plan 4 Complete!** Plans 1-4 done. Take a 2-minute break and stretch.

---

## 🟡 PLAN 5 OF 8: Enterprise (Monthly)

**⏱️ Time: 10-12 minutes** (Most features so far)

```
Name: Enterprise (Monthly)
Key: enterprise_monthly
Description: White-label M&A platform with executive community membership and private event hosting
Monthly base fee: $ 1598.00
```

**Annual discount:** ☐ UNCHECKED

**Free trial:** ☑ `14` Days

**Publicly available:** ☑ CHECK

---

### Add 18 Features (11 existing + 7 new)

**First, copy all 11 features from Growth Firm**

**Then add these 7 NEW features:**

**Feature 12:**

```
Name: White-Label Platform Access
Description: Custom branding and white-label deployment
```

**Feature 13:**

```
Name: Executive Community Membership
Description: C-suite level networking and strategic connections
```

**Feature 14:**

```
Name: Private Events + Hosting Rights
Description: Host exclusive events and access private sessions
```

**Feature 15:**

```
Name: Custom Branding & API Access
Description: Full customization and programmatic access
```

**Feature 16:**

```
Name: Direct Deal Syndication
Description: Lead and participate in exclusive deal syndication
```

**Feature 17:**

```
Name: Investment Committee Access
Description: Direct access to investment committees and LPs
```

**Feature 18:**

```
Name: Dedicated Support
Description: Priority support and account management
```

**Click "Create plan"**

✅ **Plan 5 Complete!** Take a 3-minute break. You're doing great!

---

## 🟡 PLAN 6 OF 8: Enterprise (Annual)

**⏱️ Time: 6-7 minutes**

```
Name: Enterprise (Annual)
Key: enterprise_annual
Description: Annual Enterprise plan with 17% savings - Save £3,196 annually
Monthly base fee: $ 1598.00
```

**Annual discount:** ☑ CHECK

```
Discounted rate: $ 1331.67
```

(Clerk calculates: $1,331.67/mo × 12 = $15,980.04/year)

**Free trial:** ☑ `14` Days

**Publicly available:** ☑ CHECK

**Features:** Copy all 18 features from Plan 5

**Click "Create plan"**

✅ **Plan 6 Complete!** Almost there! Take a 2-minute break.

---

## 🔴 PLAN 7 OF 8: Community Leader (Monthly)

**⏱️ Time: 12-15 minutes** (Maximum features)

```
Name: Community Leader (Monthly)
Key: community_leader_monthly
Description: Premium tier with revenue sharing, leadership roles, and exclusive LP introductions
Monthly base fee: $ 2997.00
```

**Annual discount:** ☐ UNCHECKED

**Free trial:** ☑ `14` Days

**Publicly available:** ☑ CHECK

---

### Add 24 Features (18 existing + 6 new)

**First, copy all 18 features from Enterprise**

**Then add these 6 NEW features:**

**Feature 19:**

```
Name: Revenue Share on Hosted Events
Description: Earn 20% revenue share on events you host
```

**Feature 20:**

```
Name: Personal Deal Showcase Platform
Description: Dedicated platform to showcase your deals and expertise
```

**Feature 21:**

```
Name: Mentor Program Leadership
Description: Lead mentor programs and guide other members
```

**Feature 22:**

```
Name: Direct LP and Investor Introductions
Description: Personal introductions to LPs and institutional investors
```

**Feature 23:**

```
Name: Community Influence and Recognition
Description: Leadership status and community-wide recognition
```

**Feature 24:**

```
Name: StreamYard Studio Access
Description: Professional podcast recording and live streaming capabilities
```

**Click "Create plan"**

✅ **Plan 7 Complete!** ONE MORE TO GO!

---

## 🔴 PLAN 8 OF 8: Community Leader (Annual) - FINAL PLAN!

**⏱️ Time: 7-8 minutes**

```
Name: Community Leader (Annual)
Key: community_leader_annual
Description: Annual Community Leader plan with 17% savings - Save £5,994 annually
Monthly base fee: $ 2997.00
```

**Annual discount:** ☑ CHECK

```
Discounted rate: $ 2497.50
```

(Clerk calculates: $2,497.50/mo × 12 = $29,970/year)

**Free trial:** ☑ `14` Days

**Publicly available:** ☑ CHECK

**Features:** Copy all 24 features from Plan 7

**Click "Create plan"**

✅ ✅ ✅ **ALL 8 PLANS COMPLETE!!!** 🎉🎉🎉

---

## ✅ PART 3: VERIFICATION (5 minutes)

### Step 3.1: Visual Check

Go back to: **Configure** → **Billing** → **Subscription plans**

You should see 8 plans listed:

```
✅ Solo Dealmaker (Monthly)      - $279.00/mo   - 14 days trial
✅ Solo Dealmaker (Annual)       - $232.50/mo   - 14 days trial
✅ Growth Firm (Monthly)         - $798.00/mo   - 14 days trial
✅ Growth Firm (Annual)          - $665.00/mo   - 14 days trial
✅ Enterprise (Monthly)          - $1,598.00/mo - 14 days trial
✅ Enterprise (Annual)           - $1,331.67/mo - 14 days trial
✅ Community Leader (Monthly)    - $2,997.00/mo - 14 days trial
✅ Community Leader (Annual)     - $2,497.50/mo - 14 days trial
```

---

### Step 3.2: Feature Count Verification

Click into each plan and verify feature counts:

- [ ] Solo Dealmaker: 5 features
- [ ] Growth Firm: 11 features
- [ ] Enterprise: 18 features
- [ ] Community Leader: 24 features

---

### Step 3.3: Settings Verification

Check each plan has:

- [ ] ☑ Free trial: 14 Days
- [ ] ☑ Publicly available: Enabled
- [ ] ☑ Plan key follows format: `tier_name_monthly/annual`

---

## 🧪 PART 4: TESTING (10 minutes)

### Step 4.1: Test Frontend Integration

1. Open your local dev server: `http://localhost:5173`
2. Navigate to `/pricing` page
3. Verify `<PricingTable />` component displays all 8 plans

**Expected:** All plans visible with correct pricing

---

### Step 4.2: Test Subscription Flow

1. Click "Subscribe" on Solo Dealmaker (Monthly)
2. Use Stripe test card: `4242 4242 4242 4242`
3. Expiry: Any future date (e.g., `12/28`)
4. CVC: Any 3 digits (e.g., `123`)
5. ZIP: Any 5 digits (e.g., `12345`)

**Expected:**

- Payment succeeds
- Subscription appears in Clerk user profile
- 14-day trial is active

---

### Step 4.3: Verify Webhook Processing

1. Check Clerk Dashboard → **Configure** → **Webhooks**
2. Look for recent `user.subscription.created` event
3. Status should be: ✅ Delivered

---

## 🎉 CONGRATULATIONS!

You've successfully set up all 8 Clerk subscription plans!

### What You've Accomplished:

✅ **8 subscription plans** created and configured
✅ **24 unique features** distributed across 4 tiers
✅ **14-day free trials** enabled on all plans
✅ **17% annual discounts** configured correctly
✅ **Stripe integration** verified and working
✅ **Frontend ready** to display plans via `<PricingTable />`

---

## 📊 Quick Reference Summary

| Plan             | Monthly | Annual       | Features | Savings     |
| ---------------- | ------- | ------------ | -------- | ----------- |
| Solo Dealmaker   | $279    | $232.50/mo   | 5        | $558/year   |
| Growth Firm      | $798    | $665/mo      | 11       | $1,596/year |
| Enterprise       | $1,598  | $1,331.67/mo | 18       | $3,196/year |
| Community Leader | $2,997  | $2,497.50/mo | 24       | $5,994/year |

---

## 🚀 Next Steps

### Immediate (Today):

1. **Test all plans** - Subscribe with test card to each tier
2. **Verify feature access** - Check `useSubscription()` hook returns correct data
3. **Test upgrades** - Upgrade from Solo → Growth → Enterprise
4. **Test downgrades** - Downgrade Enterprise → Growth → Solo
5. **Test cancellations** - Cancel and verify access continues until period end

### This Week:

1. **Update pricing page** with tier comparison table
2. **Add subscription badges** ("Most Popular", "Best Value")
3. **Configure email notifications** for trial ending, payment failed, etc.
4. **Set up analytics** to track conversion rates
5. **Create internal dashboard** for subscription metrics

### Before Launch:

1. **Switch to live Stripe mode** (Settings → API Keys)
2. **Update environment variables** with live keys
3. **Test live payment flow** with real credit card
4. **Set up monitoring** for failed payments and churned users
5. **Prepare customer support** documentation for subscription issues

---

## 🆘 Need Help?

### Common Issues:

**Plans not showing in `<PricingTable />`:**

- Check "Publicly available" is enabled
- Clear browser cache
- Restart dev server

**Annual discount not calculating:**

- Verify checkbox is checked
- Ensure discounted rate is less than base rate
- Try refreshing the page

**Features not appearing:**

- Verify features were saved (click into plan to check)
- Ensure feature names don't have trailing spaces
- Check browser console for errors

### Support Resources:

- Clerk Documentation: https://clerk.com/docs/billing
- Clerk Support: support@clerk.com
- Discord Community: https://clerk.com/discord

---

## 📝 Post-Setup Checklist

Print this out and check off as you complete each item:

- [ ] All 8 plans created in Clerk Dashboard
- [ ] All features added to respective plans
- [ ] Stripe integration verified
- [ ] Webhooks configured and tested
- [ ] Frontend displays all plans correctly
- [ ] Test subscription completed successfully
- [ ] Trial period (14 days) verified
- [ ] Upgrade/downgrade flows tested
- [ ] Cancellation flow tested
- [ ] Analytics/tracking configured
- [ ] Support documentation prepared
- [ ] Team trained on subscription management

---

**Setup Complete!** 🎊

You're now ready to start generating revenue with your subscription platform!

**Estimated ARR Potential:** £2.4M+ in Year 1

---

**Questions?** Open an issue or contact support at: support@100daysandbeyond.com
