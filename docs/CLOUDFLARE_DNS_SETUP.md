# Cloudflare DNS Configuration for 100daysandbeyond.com

## Overview

This guide configures all required DNS records for your complete application infrastructure.

## Required DNS Records

### 1. Clerk Authentication DNS Records

**These 5 records MUST be configured for Clerk to work:**

| Type  | Name              | Target                              | Proxy Status          | TTL  |
| ----- | ----------------- | ----------------------------------- | --------------------- | ---- |
| CNAME | `clerk`           | `frontend-api.clerk.services`       | DNS only (grey cloud) | Auto |
| CNAME | `accounts`        | `accounts.clerk.services`           | DNS only (grey cloud) | Auto |
| CNAME | `clkmail`         | `mail.8bmeyc5edpm9.clerk.services`  | DNS only (grey cloud) | Auto |
| CNAME | `clk._domainkey`  | `dkim1.8bmeyc5edpm9.clerk.services` | DNS only (grey cloud) | Auto |
| CNAME | `clk2._domainkey` | `dkim2.8bmeyc5edpm9.clerk.services` | DNS only (grey cloud) | Auto |

**Result URLs:**

- Frontend API: `https://clerk.100daysandbeyond.com`
- Account Portal: `https://accounts.100daysandbeyond.com`
- Email: `clkmail.100daysandbeyond.com`

### 2. Application DNS Records

| Type  | Name   | Target                                                      | Proxy Status           | TTL  |
| ----- | ------ | ----------------------------------------------------------- | ---------------------- | ---- |
| CNAME | `@`    | `ma-saas-platform.onrender.com`                             | Proxied (orange cloud) | Auto |
| CNAME | `www`  | `ma-saas-platform.onrender.com`                             | Proxied (orange cloud) | Auto |
| CNAME | `api`  | `ma-saas-backend.onrender.com`                              | Proxied (orange cloud) | Auto |
| CNAME | `docs` | `8424f73b33106452fa180d53b6cc128b.r2.cloudflarestorage.com` | Proxied (orange cloud) | Auto |

**Result URLs:**

- Main app: `https://100daysandbeyond.com`
- WWW redirect: `https://www.100daysandbeyond.com`
- API: `https://api.100daysandbeyond.com`
- Documents: `https://docs.100daysandbeyond.com`

## Step-by-Step Configuration

### Step 1: Access Cloudflare DNS Dashboard

1. Go to https://dash.cloudflare.com
2. Select your account
3. Click on `100daysandbeyond.com` domain
4. Click **DNS** in the left sidebar

### Step 2: Add Clerk DNS Records

For each Clerk record:

1. Click **Add record**
2. Select **CNAME** as type
3. Enter the **Name** (e.g., `clerk`)
4. Enter the **Target** (e.g., `frontend-api.clerk.services`)
5. **IMPORTANT**: Click the orange cloud to turn it **grey** (DNS only)
6. Click **Save**

**Why DNS only?** Clerk requires direct DNS resolution without Cloudflare proxy for SSL certificate validation.

### Step 3: Add Application DNS Records

For each application record:

1. Click **Add record**
2. Select **CNAME** as type
3. Enter the **Name** (e.g., `api`)
4. Enter the **Target** (e.g., `ma-saas-backend.onrender.com`)
5. Keep the orange cloud **proxied** (for CDN and security)
6. Click **Save**

### Step 4: Verify DNS Propagation

Wait 5-10 minutes, then verify each record:

```bash
# Verify Clerk Frontend API
nslookup clerk.100daysandbeyond.com

# Verify Clerk Accounts
nslookup accounts.100daysandbeyond.com

# Verify Main Application
nslookup 100daysandbeyond.com

# Verify API
nslookup api.100daysandbeyond.com
```

### Step 5: SSL Certificate Verification

After DNS records are verified:

1. Go back to **Clerk Dashboard** → **Domains** → **100daysandbeyond.com**
2. Wait for all 5 DNS records to show **Verified** (green checkmark)
3. SSL certificates will be automatically issued (takes 5-15 minutes)
4. Once complete, you'll see **SSL: Active** for both Frontend API and Account Portal

## Clerk Dashboard Configuration

### Paths Configuration

Set these in Clerk Dashboard → **Paths**:

**Application Paths:**

- Home URL: `https://100daysandbeyond.com`
- Unauthorized sign-in URL: `https://100daysandbeyond.com/unauthorised-sign-in`

**Component Paths:**

- Sign-in page: Use **Account Portal** → `https://accounts.100daysandbeyond.com/sign-in`
- Sign-up page: Use **Account Portal** → `https://accounts.100daysandbeyond.com/sign-up`
- After sign-out: Use **Account Portal** → `https://accounts.100daysandbeyond.com/sign-in`

## Cloudflare SSL/TLS Configuration

### Recommended Settings

1. Go to **SSL/TLS** in Cloudflare dashboard
2. Set **SSL/TLS encryption mode** to **Full (strict)**
3. Enable **Always Use HTTPS**
4. Enable **Automatic HTTPS Rewrites**
5. Enable **Minimum TLS Version**: TLS 1.2

### Universal SSL Certificate

Cloudflare automatically provisions SSL certificates for:

- `100daysandbeyond.com`
- `*.100daysandbeyond.com` (wildcard)

This covers all your subdomains.

## Testing After Configuration

### 1. Test Clerk Authentication

```bash
# Should return Clerk's API response
curl https://clerk.100daysandbeyond.com/.well-known/jwks.json
```

### 2. Test Account Portal

Visit: `https://accounts.100daysandbeyond.com/sign-in`

- Should load Clerk's sign-in page
- Should show your app branding

### 3. Test Main Application

Visit: `https://100daysandbeyond.com`

- Should load your frontend
- Should not show SSL errors

### 4. Test API

```bash
curl https://api.100daysandbeyond.com/health
```

## Troubleshooting

### DNS Records Not Verifying in Clerk

**Problem:** Clerk shows "Unverified" after adding DNS records

**Solutions:**

1. Wait 10-15 minutes for DNS propagation
2. Verify records are set to **DNS only** (grey cloud), not proxied
3. Check for typos in CNAME targets
4. Use `nslookup` or `dig` to verify DNS resolution

### SSL Certificate Not Issuing

**Problem:** Clerk shows "Certificates will be issued after DNS records are configured"

**Solutions:**

1. Ensure ALL 5 DNS records are verified (green checkmarks)
2. Wait 15-30 minutes after verification
3. Try clicking "Retry" in Clerk dashboard if available

### Application Not Loading

**Problem:** `https://100daysandbeyond.com` shows errors

**Solutions:**

1. Check Render deployment status
2. Verify CNAME target points to correct Render URL
3. Check Cloudflare SSL/TLS mode is **Full (strict)**
4. Clear browser cache and try incognito mode

### Mixed Content Errors

**Problem:** Browser shows "Mixed content" warnings

**Solutions:**

1. Enable **Automatic HTTPS Rewrites** in Cloudflare
2. Update all hardcoded URLs in code to use `https://`
3. Use relative URLs where possible

## Security Best Practices

### 1. Enable Cloudflare Security Features

- **Firewall Rules**: Block suspicious traffic
- **Rate Limiting**: Prevent abuse (already configured in app)
- **Bot Fight Mode**: Free bot protection
- **Under Attack Mode**: Use during DDoS attacks

### 2. Configure Page Rules

Create these page rules in Cloudflare:

1. **Cache Everything** for static assets:
   - URL: `100daysandbeyond.com/assets/*`
   - Settings: Cache Level = Cache Everything, Edge Cache TTL = 1 month

2. **Bypass Cache** for API:
   - URL: `api.100daysandbeyond.com/*`
   - Settings: Cache Level = Bypass

3. **Bypass Cache** for authentication:
   - URL: `clerk.100daysandbeyond.com/*`
   - Settings: Cache Level = Bypass

### 3. Enable Email Security

- **DMARC**: Add TXT record for email authentication
- **SPF**: Configure SPF record for email sending
- Both are already configured via Clerk's DKIM records

## Monitoring

### Cloudflare Analytics

Monitor your application:

1. Go to **Analytics & Logs** in Cloudflare
2. View:
   - Request count
   - Bandwidth usage
   - Threats blocked
   - SSL/TLS traffic percentage

### DNS Analytics

Check DNS query patterns:

1. Go to **DNS** → **Analytics**
2. Monitor NXDOMAIN errors (missing records)
3. Track query volume per subdomain

## Complete DNS Record Checklist

Use this checklist to verify all records are configured:

- [ ] `clerk.100daysandbeyond.com` → `frontend-api.clerk.services` (DNS only)
- [ ] `accounts.100daysandbeyond.com` → `accounts.clerk.services` (DNS only)
- [ ] `clkmail.100daysandbeyond.com` → `mail.8bmeyc5edpm9.clerk.services` (DNS only)
- [ ] `clk._domainkey.100daysandbeyond.com` → `dkim1.8bmeyc5edpm9.clerk.services` (DNS only)
- [ ] `clk2._domainkey.100daysandbeyond.com` → `dkim2.8bmeyc5edpm9.clerk.services` (DNS only)
- [ ] `100daysandbeyond.com` → `ma-saas-platform.onrender.com` (Proxied)
- [ ] `www.100daysandbeyond.com` → `ma-saas-platform.onrender.com` (Proxied)
- [ ] `api.100daysandbeyond.com` → `ma-saas-backend.onrender.com` (Proxied)
- [ ] `docs.100daysandbeyond.com` → `8424f73b33106452fa180d53b6cc128b.r2.cloudflarestorage.com` (Proxied)

## Next Steps

After DNS is configured:

1. ✅ Wait for all DNS records to verify
2. ✅ Wait for Clerk SSL certificates to issue
3. ✅ Test authentication flow
4. ✅ Configure Stripe webhooks with `https://api.100daysandbeyond.com/webhooks/stripe`
5. ✅ Deploy application updates
6. ✅ Test end-to-end user flows

## Support Resources

- **Clerk Documentation**: https://clerk.com/docs
- **Cloudflare DNS Docs**: https://developers.cloudflare.com/dns/
- **Render Custom Domains**: https://render.com/docs/custom-domains

---

**Last Updated:** 2025-10-11
**Status:** Ready for implementation
