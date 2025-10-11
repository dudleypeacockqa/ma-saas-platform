# CDN Setup Guide for 100 Days and Beyond

This guide explains how to set up a CDN (Content Delivery Network) for the frontend application to improve performance and reduce server load.

## Why Use a CDN?

- **Faster Load Times**: Content served from edge locations closer to users
- **Reduced Bandwidth**: Offload static assets from origin server
- **Better Availability**: CDN handles traffic spikes and DDoS protection
- **Global Performance**: Consistent experience worldwide

## Recommended CDN Providers

### 1. Cloudflare (Recommended - Free Tier Available)

**Benefits:**

- Free SSL certificates
- DDoS protection
- Web Application Firewall (WAF)
- Analytics and monitoring
- Easy DNS management

**Setup Steps:**

1. **Sign up for Cloudflare**
   - Go to https://cloudflare.com
   - Create account and add your domain

2. **Update DNS Settings**
   - Point your domain nameservers to Cloudflare
   - Cloudflare will provide nameserver addresses

3. **Configure Caching Rules**

   ```
   Cache Rules:
   - *.js, *.css, *.png, *.jpg, *.svg, *.woff, *.woff2: Cache Everything
   - *.html: Bypass Cache
   ```

4. **Enable Features**
   - SSL/TLS: Full (strict)
   - Always Use HTTPS: On
   - Automatic HTTPS Rewrites: On
   - Brotli Compression: On
   - HTTP/2: On
   - HTTP/3 (QUIC): On

5. **Page Rules** (Optional - Pro plan)

   ```
   Rule 1: 100daysandbeyond.com/assets/*
   - Cache Level: Cache Everything
   - Edge Cache TTL: 1 year

   Rule 2: 100daysandbeyond.com/*
   - Cache Level: Standard
   - Browser Cache TTL: 4 hours
   ```

### 2. AWS CloudFront

**Benefits:**

- Deep integration with AWS services
- Low latency worldwide
- Pay-as-you-go pricing

**Setup Steps:**

1. **Create CloudFront Distribution**

   ```bash
   Origin Domain: ma-saas-platform.onrender.com
   Origin Protocol: HTTPS only
   Viewer Protocol: Redirect HTTP to HTTPS
   ```

2. **Cache Behaviors**

   ```
   Path Pattern: /assets/*
   - Cache Policy: CachingOptimized
   - Origin Request Policy: CORS-S3Origin

   Path Pattern: /*.js, /*.css
   - Cache Policy: CachingOptimized
   - Compress Objects: Yes
   ```

3. **Custom Domain**
   - Add alternate domain names (CNAMEs)
   - Request or import SSL certificate
   - Update DNS records

### 3. Vercel (For Static Sites)

**Benefits:**

- Zero configuration
- Automatic HTTPS
- Built-in analytics

**Setup Steps:**

1. Import GitHub repository
2. Configure build settings:
   ```
   Build Command: pnpm install && pnpm run build
   Output Directory: dist
   Install Command: pnpm install
   ```

## Server Configuration (Already Done)

Our Express server is CDN-ready with these headers:

```javascript
// CDN cache headers for static assets
CDN-Cache-Control: public, max-age=31536000, immutable

// Response timing for monitoring
X-Response-Time: [timestamp]

// Standard cache control
Cache-Control: public, max-age=31536000, immutable (for assets)
Cache-Control: no-cache, no-store, must-revalidate (for HTML)
```

## Testing CDN Setup

### 1. Check Headers

```bash
curl -I https://100daysandbeyond.com/assets/index.js

# Should see:
# cf-cache-status: HIT (Cloudflare)
# x-cache: Hit from cloudfront (AWS)
# cache-control: public, max-age=31536000, immutable
```

### 2. Test Performance

```bash
# Before CDN
curl -w "@curl-format.txt" -o /dev/null -s https://ma-saas-platform.onrender.com

# After CDN
curl -w "@curl-format.txt" -o /dev/null -s https://100daysandbeyond.com
```

Create `curl-format.txt`:

```
     time_namelookup:  %{time_namelookup}s\n
        time_connect:  %{time_connect}s\n
     time_appconnect:  %{time_appconnect}s\n
    time_pretransfer:  %{time_pretransfer}s\n
       time_redirect:  %{time_redirect}s\n
  time_starttransfer:  %{time_starttransfer}s\n
                     ----------\n
          time_total:  %{time_total}s\n
```

### 3. Use Online Tools

- https://www.webpagetest.org
- https://gtmetrix.com
- https://tools.pingdom.com

## Cloudflare Setup (Detailed)

Since Cloudflare is recommended, here's a step-by-step guide:

### Step 1: Add Site to Cloudflare

1. Log in to Cloudflare Dashboard
2. Click "Add Site"
3. Enter: `100daysandbeyond.com`
4. Select Free plan
5. Click "Continue"

### Step 2: Review DNS Records

Cloudflare will scan existing DNS records. Verify:

```
Type: A
Name: @
Content: [Render IP]
Proxy: Enabled (Orange Cloud)

Type: CNAME
Name: www
Content: 100daysandbeyond.com
Proxy: Enabled (Orange Cloud)
```

### Step 3: Update Nameservers

Update your domain registrar with Cloudflare nameservers:

```
ns1.cloudflare.com
ns2.cloudflare.com
```

Wait for propagation (can take up to 24 hours).

### Step 4: Configure SSL/TLS

1. Go to SSL/TLS → Overview
2. Set encryption mode: **Full (strict)**
3. Go to SSL/TLS → Edge Certificates
4. Enable:
   - Always Use HTTPS
   - Automatic HTTPS Rewrites
   - Minimum TLS Version: 1.2

### Step 5: Enable Speed Optimization

1. Go to Speed → Optimization
2. Enable:
   - Auto Minify: JavaScript, CSS, HTML
   - Brotli
   - Early Hints
   - Rocket Loader (optional, test first)

### Step 6: Set Caching Rules

1. Go to Caching → Configuration
2. Set Browser Cache TTL: Respect Existing Headers
3. Add Cache Rules (Rules → Cache Rules):

```
Rule Name: Cache Static Assets
When incoming requests match: Custom filter expression
Expression: (http.request.uri.path matches "^/assets/.*")
Then:
  - Eligible for cache
  - Edge TTL: 1 year
  - Browser TTL: 1 year
```

### Step 7: Configure Firewall (Optional)

1. Go to Security → WAF
2. Enable managed rules
3. Consider adding rate limiting rules

## Monitoring CDN Performance

### Cloudflare Analytics

Available in the dashboard:

- Requests over time
- Bandwidth saved
- Cache hit ratio
- Response time

### Custom Monitoring

Our `/metrics` endpoint provides:

```json
{
  "requests": {
    "total": 10000,
    "byStatus": { "2xx": 9950, "4xx": 45, "5xx": 5 }
  },
  "performance": {
    "avgResponseTime": 45.2,
    "maxResponseTime": 523,
    "minResponseTime": 12
  }
}
```

## Troubleshooting

### Assets Not Caching

1. Check headers: `curl -I [asset-url]`
2. Verify CDN-Cache-Control header is present
3. Purge CDN cache and retry

### SSL Certificate Issues

1. Ensure SSL mode is "Full (strict)"
2. Verify origin server has valid certificate
3. Check Cloudflare SSL/TLS settings

### Slow First Load

1. Check "Always Online" is enabled
2. Verify HTTP/2 and HTTP/3 are enabled
3. Consider enabling Early Hints

## Cost Estimates

### Cloudflare (Recommended)

- Free Plan: $0/month
  - Unlimited bandwidth
  - Basic DDoS protection
  - Shared SSL certificate
  - 100k requests/day

- Pro Plan: $20/month
  - Everything in Free
  - Page rules
  - WAF
  - Image optimization

### AWS CloudFront

- Pay as you go
- ~$0.085/GB (US/Europe)
- ~$0.01/10,000 requests
- Free tier: 1TB data transfer/month (first 12 months)

### Estimated Monthly Cost (10k daily users)

Cloudflare Free: **$0**
CloudFront: **~$15-30**

## Next Steps

1. Choose CDN provider (recommend starting with Cloudflare Free)
2. Follow setup steps above
3. Test with curl and online tools
4. Monitor performance via CDN dashboard
5. Consider upgrading plan if needed

## Support

For issues:

- Cloudflare: https://support.cloudflare.com
- AWS CloudFront: https://aws.amazon.com/support
- Internal metrics: https://ma-saas-platform.onrender.com/metrics
