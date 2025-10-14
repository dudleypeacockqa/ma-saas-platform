# Cloudflare Setup Checklist

Use this checklist to set up Cloudflare CDN for your M&A SaaS Platform.

## Prerequisites

- [ ] Domain ownership confirmed: `100daysandbeyond.com`
- [ ] Access to domain registrar (for nameserver changes)
- [ ] Cloudflare account created: https://dash.cloudflare.com/sign-up
- [ ] Application deployed and accessible

## Phase 1: Initial Setup (15 minutes)

### Step 1: Add Site to Cloudflare

- [ ] Log in to Cloudflare Dashboard
- [ ] Click **"Add a Site"** button
- [ ] Enter domain: `100daysandbeyond.com`
- [ ] Select **Free** plan
- [ ] Click **"Continue"**

### Step 2: Review DNS Records

Cloudflare will scan your existing DNS. Verify these records:

- [ ] **A Record**

  ```
  Type: A
  Name: @
  Content: [Current Render IP or use CNAME]
  Proxy: ☁️ Proxied (Orange cloud)
  ```

- [ ] **CNAME Record**

  ```
  Type: CNAME
  Name: www
  Content: ma-saas-platform.onrender.com
  Proxy: ☁️ Proxied (Orange cloud)
  ```

- [ ] Click **"Continue"**

### Step 3: Update Nameservers

Cloudflare will provide nameservers like:

```
ns1.cloudflare.com
ns2.cloudflare.com
```

**Action Required:**

- [ ] Log in to your domain registrar
- [ ] Find DNS or Nameserver settings
- [ ] Replace existing nameservers with Cloudflare's
- [ ] Save changes
- [ ] Wait for propagation (can take up to 24 hours, usually ~1 hour)

**Check Status:**

- [ ] Return to Cloudflare dashboard
- [ ] Wait for "Active" status
- [ ] You'll receive email confirmation

## Phase 2: SSL/TLS Configuration (5 minutes)

### SSL/TLS Settings

- [ ] Go to **SSL/TLS** → **Overview**
- [ ] Set encryption mode: **Full (strict)**
  ```
  Full (strict) = Secure connection to origin server
  ```

### Edge Certificates

- [ ] Go to **SSL/TLS** → **Edge Certificates**
- [ ] Enable **Always Use HTTPS** ✅
- [ ] Enable **Automatic HTTPS Rewrites** ✅
- [ ] Set **Minimum TLS Version**: **TLS 1.2**
- [ ] Enable **TLS 1.3** ✅
- [ ] Enable **HTTP Strict Transport Security (HSTS)**
  - Max Age: 6 months
  - Include subdomains: Yes
  - Preload: No (for now)

## Phase 3: Speed Optimization (10 minutes)

### Auto Optimize

- [ ] Go to **Speed** → **Optimization**
- [ ] Enable **Auto Minify**:
  - [x] JavaScript
  - [x] CSS
  - [x] HTML
- [ ] Enable **Brotli** ✅
- [ ] Enable **Early Hints** ✅
- [ ] **Rocket Loader**: Leave OFF (test first)

### Caching Configuration

- [ ] Go to **Caching** → **Configuration**
- [ ] **Browser Cache TTL**: Respect Existing Headers
- [ ] **Crawlers Hints**: Enabled

### Cache Rules

- [ ] Go to **Rules** → **Cache Rules**
- [ ] Click **Create Rule**

**Rule 1: Cache Static Assets**

```
Rule name: Cache Static Assets
When incoming requests match: Custom filter expression

Expression:
(http.request.uri.path matches "^/assets/.*") or
(http.request.uri.path matches ".*\\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$")

Then:
✅ Eligible for cache
- Edge TTL: 1 year
- Browser TTL: 1 year
```

- [ ] Click **Deploy**

**Rule 2: Bypass Cache for HTML**

```
Rule name: Bypass HTML Cache
When incoming requests match: Custom filter expression

Expression:
(http.request.uri.path matches ".*\\.html$") or
(http.request.uri.path eq "/")

Then:
✅ Bypass cache
```

- [ ] Click **Deploy**

## Phase 4: Security Configuration (10 minutes)

### Firewall

- [ ] Go to **Security** → **WAF**
- [ ] Enable **Managed Rules** ✅
- [ ] Review and enable recommended rulesets

### DDoS Protection

- [ ] Go to **Security** → **DDoS**
- [ ] Verify **HTTP DDoS Attack Protection**: Enabled (automatic)
- [ ] Verify **Network DDoS Attack Protection**: Enabled (automatic)

### Bot Protection (Free Plan)

- [ ] Go to **Security** → **Bots**
- [ ] Enable **Bot Fight Mode** ✅

### Rate Limiting (Optional - Pro Plan)

If you have Pro plan, set up rate limiting:

```
Rule: API Rate Limit
Path: /api/*
Requests: 1000 per 15 minutes
Action: Block
```

## Phase 5: Performance Features (5 minutes)

### HTTP/2 & HTTP/3

- [ ] Go to **Network**
- [ ] Enable **HTTP/2** ✅ (should be on by default)
- [ ] Enable **HTTP/3 (with QUIC)** ✅
- [ ] Enable **0-RTT Connection Resumption** ✅

### IPv6

- [ ] Enable **IPv6 Compatibility** ✅

### WebSockets

- [ ] Enable **WebSockets** ✅

## Phase 6: Analytics & Monitoring (5 minutes)

### Analytics

- [ ] Go to **Analytics & Logs** → **Traffic**
- [ ] Bookmark dashboard for monitoring

### Metrics to Watch

- [ ] **Requests**: Total traffic
- [ ] **Bandwidth**: Data transfer
- [ ] **Cache Hit Ratio**: Should be >80% after warmup
- [ ] **Response Time**: Should decrease
- [ ] **Threats Blocked**: Security events

## Phase 7: Testing & Verification (15 minutes)

### DNS Propagation

```bash
# Check DNS propagation
dig 100daysandbeyond.com

# Should show Cloudflare IPs
# Example: 104.21.x.x or 172.67.x.x
```

- [ ] DNS resolves to Cloudflare IPs
- [ ] www subdomain works
- [ ] Root domain works

### SSL Certificate

```bash
# Check SSL
curl -I https://100daysandbeyond.com

# Should show:
# server: cloudflare
# cf-cache-status: MISS or HIT
```

- [ ] HTTPS works without warnings
- [ ] Certificate is valid
- [ ] HTTP redirects to HTTPS

### Caching

```bash
# Test static asset caching
curl -I https://100daysandbeyond.com/assets/index.js

# Should show:
# cf-cache-status: HIT (after first request)
# cache-control: public, max-age=31536000, immutable
```

- [ ] First request: `cf-cache-status: MISS`
- [ ] Second request: `cf-cache-status: HIT`
- [ ] Cache headers present

### Performance Test

- [ ] Run https://www.webpagetest.org
- [ ] Test location: Choose closest to your users
- [ ] Compare before/after CDN

**Expected Improvements:**

- [ ] First Byte Time: 30-50% faster
- [ ] Total Load Time: 20-40% faster
- [ ] Asset Delivery: 50-70% faster

### Application Functionality

- [ ] Home page loads
- [ ] Sign in works
- [ ] Dashboard accessible
- [ ] API calls work
- [ ] Images display
- [ ] Fonts load correctly
- [ ] No console errors

## Phase 8: Optimization (Ongoing)

### Week 1: Monitor

- [ ] Check analytics daily
- [ ] Monitor error rates
- [ ] Verify cache hit ratio >80%
- [ ] Review security threats

### Week 2: Tune

- [ ] Adjust cache rules based on traffic
- [ ] Review and block suspicious IPs
- [ ] Optimize page rules if needed

### Month 1: Analyze

- [ ] Review monthly analytics
- [ ] Calculate bandwidth savings
- [ ] Evaluate need for Pro plan features

## Common Issues & Solutions

### Issue: Site Not Loading

**Solution:**

1. Check DNS propagation: `dig 100daysandbeyond.com`
2. Verify nameservers updated at registrar
3. Check SSL mode is "Full (strict)"
4. Temporarily pause Cloudflare

### Issue: Low Cache Hit Ratio

**Solution:**

1. Review cache rules
2. Check query strings aren't breaking cache
3. Verify cache-control headers
4. Purge cache and retest

### Issue: Mixed Content Warnings

**Solution:**

1. Enable "Automatic HTTPS Rewrites"
2. Check for hardcoded http:// URLs
3. Update all assets to relative URLs

### Issue: API Errors

**Solution:**

1. Check firewall rules
2. Verify SSL mode is correct
3. Review origin server logs
4. Temporarily disable Bot Fight Mode

## Performance Metrics

Track these before and after:

### Before CDN

```
TTFB (Time to First Byte): ~800ms
Page Load: ~3.5s
Asset Delivery: ~2.5s
Bandwidth: 100%
```

### After CDN (Expected)

```
TTFB: ~150ms (82% improvement)
Page Load: ~1.5s (57% improvement)
Asset Delivery: ~300ms (88% improvement)
Bandwidth Saved: ~70% (from cache)
```

## Cost Savings

**Without CDN:**

- Origin bandwidth: 100 GB/month
- Cost: Render bandwidth included

**With Cloudflare Free:**

- Origin bandwidth: ~30 GB/month (70% cached)
- Cloudflare bandwidth: 70 GB/month
- Cost: $0 (Free tier)
- Additional: DDoS protection, WAF, SSL

## Upgrade Path

### When to Upgrade to Pro ($20/month)

- [ ] Need page rules (advanced routing)
- [ ] Want image optimization
- [ ] Need advanced DDoS protection
- [ ] Require 24/7 email support
- [ ] Need advanced analytics

## Completion Checklist

- [ ] Cloudflare active status confirmed
- [ ] DNS propagated globally
- [ ] SSL certificate valid and trusted
- [ ] Cache hit ratio >70%
- [ ] All pages load correctly
- [ ] No mixed content warnings
- [ ] Performance improved >30%
- [ ] Security features enabled
- [ ] Analytics dashboard bookmarked
- [ ] Team trained on purge cache process

## Next Steps

1. **Week 1**: Monitor daily, fine-tune settings
2. **Week 2**: Set up alerting for downtime
3. **Month 1**: Review analytics, evaluate Pro plan
4. **Ongoing**: Keep Cloudflare features updated

## Support Resources

- **Cloudflare Docs**: https://developers.cloudflare.com
- **Community**: https://community.cloudflare.com
- **Status**: https://www.cloudflarestatus.com
- **Support**: support@cloudflare.com

## Rollback Plan

If issues arise:

1. **Pause Cloudflare**: Orange cloud → Gray cloud in DNS
2. **Verify Origin**: Test direct access to Render URL
3. **Re-enable Gradually**: Enable features one by one
4. **Contact Support**: If persistent issues

---

## Sign-off

- [ ] CDN setup complete
- [ ] Team notified
- [ ] Documentation updated
- [ ] Monitoring in place

**Setup Date**: **\*\***\_\_\_**\*\***
**Completed By**: **\*\***\_\_\_**\*\***
**Verified By**: **\*\***\_\_\_**\*\***
