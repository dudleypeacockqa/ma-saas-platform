# Billing Integration - Quick Reference

Quick access guide to all files related to the Clerk + Stripe billing integration.

## 📁 File Locations

### Components

- **CheckoutButton**: [frontend/src/components/billing/CheckoutButton.tsx](../frontend/src/components/billing/CheckoutButton.tsx)
- **SubscriptionManager**: [frontend/src/components/billing/SubscriptionManager.tsx](../frontend/src/components/billing/SubscriptionManager.tsx)

### Hooks

- **useSubscription**: [frontend/src/hooks/useSubscription.ts](../frontend/src/hooks/useSubscription.ts)

### Pages

- **PricingPage** (modified): [frontend/src/pages/PricingPage.jsx](../frontend/src/pages/PricingPage.jsx)
- **SubscriptionPage**: [frontend/src/pages/SubscriptionPage.jsx](../frontend/src/pages/SubscriptionPage.jsx)
- **SubscriptionSuccessPage**: [frontend/src/pages/SubscriptionSuccessPage.jsx](../frontend/src/pages/SubscriptionSuccessPage.jsx)
- **SubscriptionCancelPage**: [frontend/src/pages/SubscriptionCancelPage.jsx](../frontend/src/pages/SubscriptionCancelPage.jsx)

### Routing

- **App.jsx** (modified): [frontend/src/App.jsx](../frontend/src/App.jsx)

### Configuration

- **Environment Variables**: [frontend/.env.example](../frontend/.env.example)

### Documentation

- **Implementation Summary**: [docs/BILLING_INTEGRATION_IMPLEMENTATION_SUMMARY.md](./BILLING_INTEGRATION_IMPLEMENTATION_SUMMARY.md)
- **Testing Guide**: [docs/BILLING_INTEGRATION_TESTING_GUIDE.md](./BILLING_INTEGRATION_TESTING_GUIDE.md)
- **Quick Reference**: [docs/BILLING_INTEGRATION_QUICK_REFERENCE.md](./BILLING_INTEGRATION_QUICK_REFERENCE.md) (this file)

## 🔗 Routes Added

| Route                   | Component               | Access           | Purpose                       |
| ----------------------- | ----------------------- | ---------------- | ----------------------------- |
| `/pricing`              | PricingPage             | Public/Protected | View and select pricing plans |
| `/subscription`         | SubscriptionPage        | Protected        | Manage active subscription    |
| `/subscription/success` | SubscriptionSuccessPage | Public/Protected | Post-checkout success         |
| `/subscription/cancel`  | SubscriptionCancelPage  | Public/Protected | Checkout cancellation         |

## 🎯 Key Components Usage

### CheckoutButton

```jsx
import { CheckoutButton } from '@/components/billing/CheckoutButton';

<CheckoutButton
  planName="Growth Firm"
  planTier="growth_firm"
  price="$798"
  interval="month"
  isCurrentPlan={false}
  variant="default"
/>;
```

### SubscriptionManager

```jsx
import { SubscriptionManager } from '@/components/billing/SubscriptionManager';

<SubscriptionManager />;
```

### useSubscription Hook

```jsx
import { useSubscription } from '@/hooks/useSubscription';

const { subscription, isLoading, error, refetch, hasActiveSubscription, isCurrentPlan } =
  useSubscription();
```

## 🔑 Environment Variables

### Frontend (.env.local)

```env
# Required
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
VITE_API_URL=http://localhost:8000

# Optional (not currently used)
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

### Backend (.env)

```env
# Required for billing
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
CLERK_SECRET_KEY=sk_test_...
CLERK_WEBHOOK_SECRET=whsec_...
```

## 📊 Pricing Tiers

| Tier           | ID               | Price     | Stripe Price ID        |
| -------------- | ---------------- | --------- | ---------------------- |
| Solo Dealmaker | `solo_dealmaker` | $279/mo   | `price_solo_dealmaker` |
| Growth Firm    | `growth_firm`    | $798/mo   | `price_growth_firm`    |
| Enterprise     | `enterprise`     | $1,598/mo | `price_enterprise`     |

## 🔌 API Endpoints Used

| Method | Endpoint                             | Purpose                 |
| ------ | ------------------------------------ | ----------------------- |
| GET    | `/api/payments/subscription/current` | Get user's subscription |
| POST   | `/api/payments/checkout-session`     | Create checkout session |
| POST   | `/api/payments/portal-session`       | Create portal session   |
| POST   | `/api/payments/webhook`              | Handle Stripe webhooks  |

## 🧪 Testing Commands

### Start Development

```bash
# Backend
cd backend
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev
```

### Stripe CLI

```bash
# Login
stripe login

# Forward webhooks
stripe listen --forward-to localhost:8000/api/payments/webhook

# Trigger test events
stripe trigger customer.subscription.created
stripe trigger customer.subscription.updated
stripe trigger invoice.payment_succeeded
```

## 📝 Quick Start Checklist

### Development Setup

- [ ] Install dependencies (already done)
- [ ] Configure Clerk keys in frontend `.env.local`
- [ ] Configure Stripe keys in backend `.env`
- [ ] Create Stripe test products and prices
- [ ] Update price IDs in backend configuration
- [ ] Start backend server
- [ ] Start frontend dev server
- [ ] Start Stripe CLI webhook forwarding

### Testing

- [ ] Visit `/pricing` page
- [ ] Test unauthenticated checkout flow (sign up)
- [ ] Test authenticated checkout flow
- [ ] Complete test payment with card `4242 4242 4242 4242`
- [ ] Verify success page displays
- [ ] Check subscription in `/subscription` page
- [ ] Test Stripe Customer Portal access
- [ ] Test cancellation flow

### Production Deployment

- [ ] Switch to production Stripe keys
- [ ] Switch to production Clerk keys
- [ ] Create production Stripe products
- [ ] Configure production webhook URL
- [ ] Update CORS origins
- [ ] Deploy backend
- [ ] Deploy frontend
- [ ] Test complete flow in production
- [ ] Monitor for errors

## 🐛 Common Issues

### "No authentication token"

- **Solution:** User not signed in with Clerk. Clear browser cache and re-login.

### Checkout button not working

- **Solution:** Check `VITE_API_URL` in `.env.local` and ensure backend is running.

### Webhook not received

- **Solution:** Verify webhook URL in Stripe Dashboard and webhook secret in backend `.env`.

### Subscription not showing

- **Solution:** Check backend logs for webhook processing errors. Verify Stripe webhook events are enabled.

## 📚 Documentation Links

- [Full Implementation Summary](./BILLING_INTEGRATION_IMPLEMENTATION_SUMMARY.md)
- [Comprehensive Testing Guide](./BILLING_INTEGRATION_TESTING_GUIDE.md)
- [Clerk Documentation](https://clerk.com/docs)
- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Test Cards](https://stripe.com/docs/testing#cards)

## 🎨 UI Components Used

- **shadcn/ui Components:**
  - Card, CardHeader, CardTitle, CardDescription, CardContent
  - Button
  - Badge
  - Alert, AlertDescription
  - (All from `@radix-ui/*` packages)

- **Icons:** lucide-react
  - CheckCircle, Loader2, AlertCircle, CreditCard, LogIn, Check
  - ExternalLink, Calendar, DollarSign, Users, Database, Zap
  - ArrowRight, ArrowLeft, HelpCircle, MessageCircle, Sparkles

## 💡 Tips

1. **Use Stripe Test Mode** during development
2. **Test card:** `4242 4242 4242 4242` (any future expiry, any CVC)
3. **Webhook testing:** Use Stripe CLI for local development
4. **Error debugging:** Check browser console and backend logs
5. **Session expiry:** Stripe checkout sessions expire after 24 hours

## 🚀 Next Actions

1. **Immediate:** Run through testing guide
2. **Before Production:** Security audit and load testing
3. **Post-Launch:** Monitor webhook delivery and payment success rates
4. **Ongoing:** Implement enhancements from implementation summary

---

**Last Updated:** October 12, 2025
**Status:** Implementation Complete
