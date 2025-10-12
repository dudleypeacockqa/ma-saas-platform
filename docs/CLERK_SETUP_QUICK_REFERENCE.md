# Clerk Billing Setup - Quick Reference Card

**🚀 Your Configuration Credentials**

---

## 1. Webhook Configuration

```
Endpoint URL:
https://ma-saas-backend.onrender.com/api/webhooks/clerk/subscription

Signing Secret:
whsec_nBUKje3GC6+/XwtUtm1JERDNvXYnLgSO

Events to Enable:
✅ subscription.created
✅ subscription.updated
✅ subscription.deleted
✅ subscription.trial_will_end
✅ payment.succeeded
✅ payment.failed
```

---

## 2. Pricing Plans Summary

### Solo Dealmaker

- **Monthly**: $279/mo | Plan ID: `solo`
- **Annual**: $2,790/yr | Save $558 (17% off)
- **Trial**: 14 days (payment required)
- **Features**: 3 users, 10 deals, 50GB storage
- **Permissions**: `org:deals:view, org:deals:create, org:deals:edit, org:analytics:basic, org:storage:50gb, org:support:email, org:export:basic`

### Growth Firm

- **Monthly**: $798/mo | Plan ID: `growth`
- **Annual**: $7,980/yr | Save $1,596 (17% off)
- **Trial**: 14 days (payment required)
- **Features**: 15 users, 50 deals, 200GB storage, AI insights
- **Permissions**: `org:deals:*, org:analytics:advanced, org:ai_analysis:use, org:ai_insights:view, org:team:collaborate, org:storage:200gb, org:support:priority, org:export:unlimited, org:integrations:basic, org:reports:generate`

### Enterprise

- **Monthly**: $1,598/mo | Plan ID: `enterprise`
- **Annual**: $15,980/yr | Save $3,196 (17% off)
- **Trial**: 14 days (payment required)
- **Features**: Unlimited users/deals, 1TB storage, dedicated support
- **Permissions**: `org:deals:unlimited, org:analytics:custom, org:ai:unlimited, org:team:unlimited, org:integrations:custom, org:sso:use, org:storage:1tb, org:support:dedicated, org:export:unlimited, org:reports:generate, org:white_label:use, org:billing:manage`

---

## 3. Stripe Test Cards

For testing subscriptions in Stripe Test Mode:

```
Success:        4242 4242 4242 4242
Payment Fails:  4000 0000 0000 0002
Requires Auth:  4000 0025 0000 3155

Expiry: Any future date (e.g., 12/26)
CVC: Any 3 digits (e.g., 123)
ZIP: Any 5 digits (e.g., 12345)
```

---

## 4. Quick Links

**Clerk Dashboard**: https://dashboard.clerk.com
**Stripe Dashboard**: https://dashboard.stripe.com
**Render Dashboard**: https://dashboard.render.com

**Your API**: https://ma-saas-backend.onrender.com
**Health Check**: https://ma-saas-backend.onrender.com/health
**Webhook Endpoint**: https://ma-saas-backend.onrender.com/api/webhooks/clerk/subscription

**Your Frontend**: https://100daysandbeyond.com
**Pricing Page**: https://100daysandbeyond.com/pricing
**Subscription Page**: https://100daysandbeyond.com/subscription

---

## 5. Configuration Checklist

### In Clerk Dashboard:

- [ ] Enable Clerk Billing (Beta)
- [ ] Connect Stripe account
- [ ] Create 6 pricing plans (see above)
- [ ] Set all plans to 14-day trial
- [ ] Add permissions to each plan
- [ ] Create webhook endpoint with events
- [ ] Verify webhook signing secret

### In Render Dashboard:

- [ ] Environment variables already configured ✅
- [ ] Backend already deployed ✅

### Testing:

- [ ] Switch Stripe to Test Mode
- [ ] Test subscription flow with test card
- [ ] Verify webhook delivers successfully
- [ ] Test subscription management UI
- [ ] Test plan upgrades/downgrades

---

## 6. Environment Variables (Already Configured ✅)

**Frontend** (.env):

```bash
VITE_CLERK_PUBLISHABLE_KEY=pk_live_Y2xlcmsuMTAwZGF5c2FuZGJleW9uZC5jb20k
VITE_API_URL=https://api.100daysandbeyond.com
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_51QwSgkFVol9SKsekxmCj4lDnvd1T6XZPi9VWuI7eKkxNopxC1N60ypXZzwQdyk64AuAQJMvQxuIJ1VuLeOdbeWQC00mV7ZDNB1
```

**Backend** (.env):

```bash
CLERK_SECRET_KEY=sk_live_[configured]
CLERK_PUBLISHABLE_KEY=pk_live_[configured]
CLERK_WEBHOOK_SECRET=whsec_[configured]
STRIPE_SECRET_KEY=sk_live_[configured]
STRIPE_PUBLISHABLE_KEY=pk_live_[configured]
```

**Note**: Actual keys are stored securely in `backend/.env` file.

---

## 7. What You Need To Do

### Step 1: Configure Clerk Dashboard (30 minutes)

Open this file for detailed instructions:
📄 `docs/CLERK_DASHBOARD_SETUP_GUIDE.md`

### Step 2: Test Everything (15 minutes)

1. Visit https://100daysandbeyond.com/pricing
2. Test subscription with Stripe test card: `4242 4242 4242 4242`
3. Verify webhook receives events (200 OK)
4. Test subscription management at /subscription

### Step 3: Go Live

1. Switch Stripe from Test Mode to Live Mode in Clerk
2. Test with a real card (small amount)
3. Monitor for 24 hours

---

## 8. Support

**Need Help?**

- Clerk Docs: https://clerk.com/docs/billing
- Stripe Docs: https://stripe.com/docs/billing
- Full Setup Guide: `docs/CLERK_DASHBOARD_SETUP_GUIDE.md`
- Migration Details: `docs/CLERK_BILLING_MIGRATION_COMPLETED.md`

---

**Status**: ✅ Code complete. Ready for Clerk Dashboard configuration.
**Estimated Time**: 45 minutes total (30 min config + 15 min testing)
