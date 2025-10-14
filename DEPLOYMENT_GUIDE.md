# Deployment Guide - 100daysandbeyond.com

## Overview

This guide covers deploying the M&A SaaS Platform to Render with the custom domain `100daysandbeyond.com` and integrating Clerk authentication and Stripe payments.

## Current Status

- **Render Service**: `ma-saas-platform.onrender.com` (Service ID: `srv-d3ihptbipnbc73e72ne0`)
- **Target Domain**: `100daysandbeyond.com`
- **Account Portal**: `accounts.100daysandbeyond.com`

## Step 1: Configure Render Custom Domain

### 1.1 Add Custom Domain in Render

1. Go to your Render dashboard: https://dashboard.render.com
2. Select your service: `ma-saas-platform`
3. Go to **Settings** → **Custom Domains**
4. Click **Add Custom Domain**
5. Enter: `100daysandbeyond.com`
6. Optionally add: `www.100daysandbeyond.com`
7. Render will provide DNS records to configure

### 1.2 Expected DNS Records for Render

You'll need to add these records in your domain registrar (e.g., GoDaddy, Namecheap, Cloudflare):

**For root domain (100daysandbeyond.com):**

```
Type: A or ALIAS
Name: @ (or leave blank)
Value: [IP provided by Render]
```

**For www subdomain:**

```
Type: CNAME
Name: www
Value: ma-saas-platform.onrender.com
```

## Step 2: Configure Clerk DNS Records

You MUST configure these 5 CNAME records in your DNS provider for Clerk to work:

### 2.1 Frontend API

```
Type: CNAME
Name: clerk
Value: frontend-api.clerk.services
TTL: 3600
```

### 2.2 Account Portal

```
Type: CNAME
Name: accounts
Value: accounts.clerk.services
TTL: 3600
```

### 2.3 Email DNS Records (3 records)

**Email Service:**

```
Type: CNAME
Name: clkmail
Value: mail.8bmeyc5edpm9.clerk.services
TTL: 3600
```

**DKIM 1:**

```
Type: CNAME
Name: clk._domainkey
Value: dkim1.8bmeyc5edpm9.clerk.services
TTL: 3600
```

**DKIM 2:**

```
Type: CNAME
Name: clk2._domainkey
Value: dkim2.8bmeyc5edpm9.clerk.services
TTL: 3600
```

### 2.4 Verify DNS Records

After adding records, verify them in Clerk Dashboard:

1. Go to: Configure → Satellites → DNS Configuration
2. Wait for DNS propagation (can take 24-48 hours)
3. SSL certificates will be issued automatically after verification

## Step 3: Configure Render Environment Variables

### 3.1 Backend Environment Variables

Set these in Render Dashboard → Environment:

```bash
# Database (should already be set)
DATABASE_URL=[your-postgres-url-from-render]

# Security
SECRET_KEY=[generate-a-strong-secret-key]
DEBUG=false

# Clerk Authentication
# Get from: https://dashboard.clerk.com → API Keys
CLERK_SECRET_KEY=[your-clerk-secret-key]
CLERK_PUBLISHABLE_KEY=[your-clerk-publishable-key]

# Stripe Payment Integration
# Get from: https://dashboard.stripe.com/apikeys
STRIPE_SECRET_KEY=[your-stripe-secret-key]
STRIPE_PUBLISHABLE_KEY=[your-stripe-publishable-key]
STRIPE_WEBHOOK_SECRET=[get-from-stripe-dashboard-after-creating-webhook]

# CORS Settings
ALLOWED_ORIGINS=https://100daysandbeyond.com,https://www.100daysandbeyond.com

# Claude MCP (if needed)
ANTHROPIC_API_KEY=[your-anthropic-api-key]
```

### 3.2 Frontend Environment Variables

If deploying frontend separately, set these:

```bash
# API URL (use custom domain after DNS is configured)
VITE_API_URL=https://100daysandbeyond.com

# Clerk
# Get from: https://dashboard.clerk.com → API Keys
VITE_CLERK_PUBLISHABLE_KEY=[your-clerk-publishable-key]

# Stripe
# Get from: https://dashboard.stripe.com/apikeys
VITE_STRIPE_PUBLISHABLE_KEY=[your-stripe-publishable-key]
```

## Step 4: Configure Stripe Webhooks

### 4.1 Create Webhook Endpoint

1. Go to Stripe Dashboard: https://dashboard.stripe.com/webhooks
2. Click **Add endpoint**
3. Enter endpoint URL: `https://100daysandbeyond.com/api/webhooks/stripe`
4. Select events to listen for:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`

### 4.2 Get Webhook Secret

1. After creating webhook, click to reveal **Signing secret**
2. Copy the secret (starts with `whsec_`)
3. Add to Render environment variables as `STRIPE_WEBHOOK_SECRET`

## Step 5: Clerk Configuration Updates

### 5.1 Update Clerk Application URLs

In Clerk Dashboard → Paths:

**Home URL:**

```
https://100daysandbeyond.com
```

**Unauthorized sign in URL:**

```
https://100daysandbeyond.com/unauthorised-sign-in
```

**Sign-in page:**

```
https://accounts.100daysandbeyond.com/sign-in
```

**Sign-up page:**

```
https://accounts.100daysandbeyond.com/sign-up
```

**After sign out:**

```
https://accounts.100daysandbeyond.com/sign-in
```

### 5.2 Update Allowed Origins

In Clerk Dashboard → API Keys → Advanced → Allowed Origins:

```
https://100daysandbeyond.com
https://www.100daysandbeyond.com
```

## Step 6: Deploy and Test

### 6.1 Deploy to Render

```bash
git add .
git commit -m "Configure production environment for 100daysandbeyond.com"
git push origin master
```

Render will automatically deploy on push.

### 6.2 Verification Checklist

After DNS propagates and deployment completes:

- [ ] Site accessible at `https://100daysandbeyond.com`
- [ ] Site accessible at `https://www.100daysandbeyond.com`
- [ ] Clerk authentication working
- [ ] Account portal accessible at `https://accounts.100daysandbeyond.com`
- [ ] Sign in/Sign up flows working
- [ ] Stripe checkout working
- [ ] Webhooks receiving events from Stripe
- [ ] All 5 Clerk DNS records verified
- [ ] SSL certificates issued for all domains

## Troubleshooting

### DNS Not Propagating

- DNS changes can take 24-48 hours
- Check status: https://dnschecker.org
- Use `dig` or `nslookup` to verify records

### Clerk Not Working

- Verify all 5 DNS records are correct
- Check SSL certificates are issued
- Ensure publishable keys match your domain
- Check browser console for CORS errors

### Stripe Webhooks Failing

- Verify webhook URL is correct
- Check webhook secret is set in environment
- Review webhook logs in Stripe Dashboard
- Ensure endpoint is publicly accessible

### CORS Errors

- Update `ALLOWED_ORIGINS` in backend
- Restart Render service after environment changes
- Check browser console for specific origin being blocked

## Security Notes

⚠️ **IMPORTANT**:

- Never commit `.env` files with production keys to git
- Production keys are in `.env.example` for reference only
- Set all keys as environment variables in Render Dashboard
- Rotate keys if they are exposed
- Use Stripe test mode keys for development

## Next Steps After Deployment

1. **Set up monitoring**: Configure uptime monitoring (e.g., UptimeRobot)
2. **Enable backups**: Set up database backups in Render
3. **Add analytics**: Integrate Google Analytics or Plausible
4. **Performance**: Enable caching, CDN if needed
5. **Documentation**: Update API documentation with production URLs
6. **Testing**: Run end-to-end tests on production environment

## Support Resources

- **Render Docs**: https://render.com/docs
- **Clerk Docs**: https://clerk.com/docs
- **Stripe Docs**: https://stripe.com/docs
- **DNS Help**: https://dnschecker.org

## Summary of URLs

| Service          | URL                                   |
| ---------------- | ------------------------------------- |
| Main App         | https://100daysandbeyond.com          |
| Account Portal   | https://accounts.100daysandbeyond.com |
| Frontend API     | https://clerk.100daysandbeyond.com    |
| Render Service   | https://ma-saas-platform.onrender.com |
| Stripe Dashboard | https://dashboard.stripe.com          |
| Clerk Dashboard  | https://dashboard.clerk.com           |
