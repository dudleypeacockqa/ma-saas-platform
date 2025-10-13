# 🚀 Quick Launch Checklist - M&A SaaS Platform

**Target:** Generate clients and revenue
**Time to Launch:** 3-4 hours
**Current Status:** Infrastructure 100% complete, deployment pending environment setup

---

## ✅ **Already Deployed on Render**

Your services are already live:

- **Database:** `ma-saas-db` (PostgreSQL 17, Frankfurt, 256MB)
  - Status: ✅ Available
  - Connection: Internal + External URLs configured

- **Backend:** `ma-saas-backend` (Docker, Starter, 512MB)
  - URL: https://ma-saas-backend.onrender.com
  - Health Check: `/health`
  - Service ID: `srv-d3ii9qk9c44c73aqsli0`

- **Frontend:** `ma-saas-platform` (Node, Starter, 512MB)
  - URL: https://100daysandbeyond.com
  - Service ID: `srv-d3ihptbipnbc73e72ne0`
  - Auto-deploy: Enabled on master branch

---

## 🔥 **Critical Tasks (3-4 hours)**

### **Task 1: Set Environment Variables (1 hour)**

You need to configure environment variables in the Render dashboard for both backend and frontend services.

#### **Backend Environment Variables** (`srv-d3ii9qk9c44c73aqsli0`)

Go to: https://dashboard.render.com/web/srv-d3ii9qk9c44c73aqsli0 → Environment

```bash
# Database (Already configured via internal URL)
DATABASE_URL=postgresql://ma_saas_user:iJtvWyv5q5CcIUlBZD7IaYyHAvGk5M1t@dpg-d3ii7jjipnbc73e7chfg-a/ma_saas_platform

# Security
SECRET_KEY=<generate-new-random-32-char-string>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=false
ENVIRONMENT=production

# Clerk Authentication (Get from Clerk dashboard)
CLERK_SECRET_KEY=<your-clerk-secret-key>
CLERK_PUBLISHABLE_KEY=<your-clerk-publishable-key>
CLERK_WEBHOOK_SECRET=<your-clerk-webhook-secret>

# Anthropic Claude (Get from Anthropic console)
ANTHROPIC_API_KEY=<your-anthropic-key>
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# OpenAI (Get from OpenAI dashboard)
OPENAI_API_KEY=<your-openai-key>

# Stripe (Get NEW keys - old ones are exposed)
STRIPE_SECRET_KEY=<new-stripe-secret-key>
STRIPE_PUBLISHABLE_KEY=<new-stripe-publishable-key>
STRIPE_WEBHOOK_SECRET=<new-stripe-webhook-secret>

# Redis (Provision on Render or use external)
REDIS_URL=<redis-url-if-needed>

# Cloudflare R2 Storage (Get from Cloudflare dashboard)
R2_ACCOUNT_ID=<your-r2-account-id>
R2_ACCESS_KEY_ID=<your-r2-access-key>
R2_SECRET_ACCESS_KEY=<your-r2-secret-key>
R2_BUCKET_NAME=ma-saas-documents

# SendGrid Email (Get from SendGrid dashboard)
SENDGRID_API_KEY=<your-sendgrid-api-key>
SENDGRID_FROM_EMAIL=noreply@100daysandbeyond.com
SENDGRID_FROM_NAME="100 Days and Beyond"

# Sentry (Get from Sentry dashboard)
SENTRY_DSN=<your-sentry-backend-dsn>
SENTRY_ENVIRONMENT=production
GIT_COMMIT_SHA=<current-git-sha>

# Rate Limiting
ENABLE_RATE_LIMITING=true
RATE_LIMIT_PER_MINUTE=60

# Feature Flags
ENABLE_AI_INSIGHTS=true
ENABLE_ANALYTICS=true
```

#### **Frontend Environment Variables** (`srv-d3ihptbipnbc73e72ne0`)

Go to: https://dashboard.render.com/web/srv-d3ihptbipnbc73e72ne0 → Environment

```bash
# API
VITE_API_URL=https://ma-saas-backend.onrender.com
VITE_API_V1_URL=https://ma-saas-backend.onrender.com/api/v1

# Clerk
VITE_CLERK_PUBLISHABLE_KEY=<your-clerk-publishable-key>

# Sentry
VITE_SENTRY_DSN=<your-sentry-frontend-dsn>
VITE_ENVIRONMENT=production
VITE_GIT_COMMIT_SHA=<current-git-sha>

# App Info
VITE_APP_NAME="100 Days and Beyond"
VITE_APP_VERSION=2.0.0
VITE_APP_ENV=production

# Feature Flags
VITE_ENABLE_ANALYTICS=true
VITE_FEATURE_AI_INSIGHTS=true
VITE_FEATURE_DOCUMENTS=true
VITE_FEATURE_INTEGRATIONS=true
VITE_FEATURE_CONTENT=true
VITE_FEATURE_OPPORTUNITIES=true
VITE_FEATURE_VALUATIONS=true
VITE_FEATURE_ARBITRAGE=true
```

---

### **Task 2: Provision Redis (30 minutes)**

Option A: **Render Redis** (Recommended)

1. Go to: https://dashboard.render.com/create?type=redis
2. Create new Redis instance (Starter plan - Free)
3. Name: `ma-saas-redis`
4. Region: Frankfurt (same as other services)
5. Copy the **Internal Redis URL**
6. Add to backend environment: `REDIS_URL=<internal-redis-url>`

Option B: **External Redis** (Upstash, Redis Cloud)

- Use Upstash free tier
- Get connection URL
- Add to backend environment

---

### **Task 3: Security - Rotate Stripe Keys (15 minutes)**

⚠️ **CRITICAL:** Your Stripe keys are exposed in git history.

1. **Go to Stripe Dashboard:** https://dashboard.stripe.com/apikeys
2. **Revoke old keys:**
   - Find the exposed keys in git history
   - Click "Delete" on those keys
3. **Generate new keys:**
   - Create new Restricted Key for backend
   - Copy Secret Key and Publishable Key
4. **Update environment variables** (Step 1)
5. **Generate webhook secret:**
   - Go to: https://dashboard.stripe.com/webhooks
   - Add endpoint: `https://ma-saas-backend.onrender.com/api/webhooks/stripe`
   - Copy webhook signing secret

---

### **Task 4: Get API Keys (30-60 minutes)**

You need to obtain keys from these services:

#### **1. Clerk (Authentication)** - https://dashboard.clerk.com

- Navigate to: API Keys
- Copy:
  - Secret Key (starts with `sk_live_` or `sk_test_`)
  - Publishable Key (starts with `pk_live_` or `pk_test_`)
- Navigate to: Webhooks → Add Endpoint
  - URL: `https://ma-saas-backend.onrender.com/api/webhooks/clerk`
  - Subscribe to: `user.*` and `organization.*` events
  - Copy: Webhook Secret

#### **2. Anthropic Claude (AI)** - https://console.anthropic.com

- Navigate to: Settings → API Keys
- Click: Create Key
- Copy: API Key (starts with `sk-ant-`)

#### **3. OpenAI (Embeddings)** - https://platform.openai.com

- Navigate to: API Keys
- Click: Create new secret key
- Copy: API Key (starts with `sk-`)

#### **4. SendGrid (Email)** - https://app.sendgrid.com

- Navigate to: Settings → API Keys
- Click: Create API Key
- Permission: Full Access
- Copy: API Key (starts with `SG.`)
- Verify sender: `noreply@100daysandbeyond.com`

#### **5. Cloudflare R2 (Storage)** - https://dash.cloudflare.com

- Navigate to: R2 → Manage R2 API Tokens
- Click: Create API Token
- Permissions: Read & Write
- Copy: Access Key ID and Secret Access Key
- Create bucket: `ma-saas-documents`
- Copy: Account ID

#### **6. Sentry (Error Tracking)** - https://sentry.io

- Create account if needed
- Create new project for React (frontend)
- Create new project for Python (backend)
- Copy: DSN for each project (looks like `https://...@sentry.io/...`)

---

### **Task 5: Initialize Database (30 minutes)**

Once environment variables are set, you need to run database migrations:

#### **Option A: Via Render Shell** (Recommended)

1. Go to backend service: https://dashboard.render.com/web/srv-d3ii9qk9c44c73aqsli0
2. Click: "Shell" tab
3. Run migrations:

```bash
# Initialize database
alembic upgrade head

# Optional: Create admin user (if you have a script)
python -m app.scripts.create_admin
```

#### **Option B: Via Render Deploy with Pre-Deploy Command**

1. Go to: https://dashboard.render.com/web/srv-d3ii9qk9c44c73aqsli0 → Settings
2. Edit: "Pre-Deploy Command"
3. Set to: `alembic upgrade head`
4. Manual Deploy → Deploy latest commit

---

### **Task 6: Verify Deployment (30 minutes)**

#### **Backend Health Check**

```bash
curl https://ma-saas-backend.onrender.com/health
```

Expected: `{"status": "healthy", "database": "connected"}`

#### **Frontend Check**

- Visit: https://100daysandbeyond.com
- Should load without errors
- Check browser console for errors

#### **API Endpoint Test**

```bash
curl https://ma-saas-backend.onrender.com/api/v1/deals
```

Expected: `401 Unauthorized` (authentication required - this is correct!)

#### **Sentry Verification**

- Trigger a test error
- Check Sentry dashboard for event capture

---

## 🎯 **Post-Launch Tasks (Week 1)**

### **Day 1: Monitoring Setup**

- [ ] Set up Sentry alerts for critical errors
- [ ] Configure uptime monitoring (UptimeRobot or Render monitoring)
- [ ] Set up CloudFlare for frontend CDN
- [ ] Enable database backups on Render

### **Day 2: User Onboarding**

- [ ] Create admin account via Clerk
- [ ] Test complete user flow (signup → login → create deal)
- [ ] Verify email delivery (SendGrid)
- [ ] Test document upload (R2 storage)

### **Day 3: Security Hardening**

- [ ] Enable HTTPS enforcement
- [ ] Set up CORS properly
- [ ] Review rate limiting settings
- [ ] Test authentication flows

### **Day 4: Performance Optimization**

- [ ] Run Lighthouse audit
- [ ] Optimize bundle size
- [ ] Enable Redis caching
- [ ] Test with 10 concurrent users

### **Day 5: Analytics & Marketing**

- [ ] Set up Google Analytics
- [ ] Create landing page content
- [ ] Set up conversion tracking
- [ ] Launch marketing campaign

---

## 📊 **Success Metrics**

After deployment, track these metrics:

### **Technical Metrics** (via Sentry & Render)

- ✅ Uptime: > 99.9%
- ✅ Response time: < 300ms (p95)
- ✅ Error rate: < 0.1%
- ✅ Database connections: < 20 (max 50)

### **Business Metrics** (via Analytics)

- 🎯 User signups: Track in Clerk
- 🎯 Deals created: Track in database
- 🎯 Documents uploaded: Track in R2
- 🎯 API usage: Track via rate limiter logs

---

## 🆘 **Quick Troubleshooting**

### **Backend won't start**

- Check logs: https://dashboard.render.com/web/srv-d3ii9qk9c44c73aqsli0/logs
- Common issues:
  - Missing environment variables
  - Database connection failed
  - Port already in use

### **Frontend blank page**

- Check browser console
- Verify API_URL is correct
- Check Clerk publishable key
- Check CORS settings on backend

### **Database connection failed**

- Verify DATABASE_URL is correct
- Check database is running
- Verify IP allowlist (0.0.0.0/0 allows all)
- Test connection via psql command

### **Authentication not working**

- Verify Clerk keys are correct
- Check Clerk webhook is configured
- Verify CORS allows Clerk domains

---

## 🎁 **Quick Wins to Get First Client**

### **Week 1: Polish Core Features**

1. **Dashboard**: Make sure deal pipeline looks professional
2. **Demo Data**: Add sample deals for demos
3. **Email Templates**: Professional SendGrid templates
4. **Landing Page**: Clear value proposition on 100daysandbeyond.com

### **Week 2: Client Acquisition**

1. **LinkedIn Outreach**: Target M&A professionals
2. **Demo Video**: 2-minute walkthrough
3. **Free Trial**: 14-day trial for first 10 clients
4. **Case Study Ready**: Template for success stories

### **Week 3: Onboarding Excellence**

1. **Welcome Email**: Automated onboarding sequence
2. **Tutorial Tooltips**: Guide users through first deal
3. **Support Channel**: Slack or Intercom
4. **Feedback Loop**: Weekly check-ins with early users

---

## 🚀 **Ready to Launch Commands**

Once all environment variables are set:

```bash
# Trigger manual deploy for backend
curl -X POST https://api.render.com/deploy/srv-d3ii9qk9c44c73aqsli0?key=XW9ZoBe5F74

# Trigger manual deploy for frontend
curl -X POST https://api.render.com/deploy/srv-d3ihptbipnbc73e72ne0?key=2wugxge0amo

# Check backend health
curl https://ma-saas-backend.onrender.com/health

# Open frontend
open https://100daysandbeyond.com
```

---

## ✅ **Final Checklist**

Before announcing launch:

- [ ] All environment variables set (backend + frontend)
- [ ] Redis provisioned and connected
- [ ] Stripe keys rotated (new keys in place)
- [ ] All API keys obtained and configured
- [ ] Database migrations run successfully
- [ ] Backend health check returns 200
- [ ] Frontend loads without errors
- [ ] User can sign up via Clerk
- [ ] User can create a deal
- [ ] User can upload a document
- [ ] Emails are being sent (SendGrid)
- [ ] Errors are being tracked (Sentry)
- [ ] Monitoring alerts configured
- [ ] Landing page content is professional

---

**Time Investment:**

- Environment setup: 1 hour
- Redis provisioning: 30 minutes
- Stripe key rotation: 15 minutes
- API keys collection: 30-60 minutes
- Database initialization: 30 minutes
- Verification: 30 minutes

**Total: 3-4 hours** → **Platform Live & Generating Revenue**

---

**Need Help?**

- Render Dashboard: https://dashboard.render.com
- Render Docs: https://render.com/docs
- Your Workspace: https://dashboard.render.com/teams/tea-d38mt58gjchc73d6og9g

**Your Services:**

- Backend: srv-d3ii9qk9c44c73aqsli0
- Frontend: srv-d3ihptbipnbc73e72ne0
- Database: dpg-d3ii7jjipnbc73e7chfg-a
