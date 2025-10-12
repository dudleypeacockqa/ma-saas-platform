# 🔐 Render Environment Variables Configuration

**IMPORTANT:** Fill in this file with your actual API keys, then I'll help you set them via Render API.

**⚠️ DO NOT COMMIT THIS FILE TO GIT** - Add to .gitignore after filling in values.

---

## Backend Environment Variables (srv-d3ii9qk9c44c73aqsli0)

### Database (Already configured)

```bash
DATABASE_URL=postgresql://ma_saas_user:iJtvWyv5q5CcIUlBZD7IaYyHAvGk5M1t@dpg-d3ii7jjipnbc73e7chfg-a/ma_saas_platform
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
```

### Security & Application

```bash
SECRET_KEY=Qzx^O.-RyjzoZPC=Mb`2CY&j&<!XX"6=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=false
ENVIRONMENT=production
```

### Clerk Authentication

**Get from:** https://dashboard.clerk.com → API Keys

```bash
CLERK_SECRET_KEY=
CLERK_PUBLISHABLE_KEY=
CLERK_WEBHOOK_SECRET=
```

**Action:**

1. Go to https://dashboard.clerk.com → API Keys
2. Copy Secret Key (starts with `sk_live_` or `sk_test_`)
3. Copy Publishable Key (starts with `pk_live_` or `pk_test_`)
4. Go to Webhooks → Add Endpoint: `https://ma-saas-backend.onrender.com/api/webhooks/clerk`
5. Subscribe to: `user.*`, `organization.*`, `session.*`
6. Copy Webhook Secret

### Anthropic Claude

**Get from:** https://console.anthropic.com/settings/keys

```bash
ANTHROPIC_API_KEY=
CLAUDE_MODEL=claude-3-5-sonnet-20241022
CLAUDE_MAX_TOKENS=4000
CLAUDE_TEMPERATURE=0.1
```

**Action:**

1. Go to https://console.anthropic.com/settings/keys
2. Click "Create Key"
3. Copy API Key (starts with `sk-ant-`)

### OpenAI

**Get from:** https://platform.openai.com/api-keys

```bash
OPENAI_API_KEY=
VECTOR_DIMENSION=1536
EMBEDDING_MODEL=text-embedding-3-small
SEMANTIC_SEARCH_THRESHOLD=0.8
```

**Action:**

1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy API Key (starts with `sk-`)

### Stripe (MUST ROTATE - OLD KEYS EXPOSED!)

**Get from:** https://dashboard.stripe.com/apikeys

```bash
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=
```

**Action:**

1. Go to https://dashboard.stripe.com/apikeys
2. **IMPORTANT:** Delete/revoke any old exposed keys first!
3. Create new Restricted Key
4. Copy new Secret Key and Publishable Key
5. Go to Webhooks → Add endpoint: `https://ma-saas-backend.onrender.com/api/webhooks/stripe`
6. Select events: `customer.*`, `payment_intent.*`, `subscription.*`, `invoice.*`
7. Copy Webhook signing secret

### Redis

**Option 1 - Render Redis (Recommended):**

```bash
REDIS_URL=
```

**Action:**

1. I'll create this for you using Render API
2. Or go to: https://dashboard.render.com/create?type=redis
3. Create instance, copy Internal Redis URL

**Option 2 - Upstash (Alternative):**

1. Go to https://console.upstash.com/redis
2. Create database
3. Copy Redis URL

### Cloudflare R2 Storage

**Get from:** https://dash.cloudflare.com → R2

```bash
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=ma-saas-documents
R2_PUBLIC_URL=
```

**Action:**

1. Go to https://dash.cloudflare.com → R2
2. Click "Manage R2 API Tokens"
3. Create API Token with Read & Write permissions
4. Copy: Account ID, Access Key ID, Secret Access Key
5. Create bucket: `ma-saas-documents`
6. Copy bucket public URL if using public access

### SendGrid Email

**Get from:** https://app.sendgrid.com

```bash
SENDGRID_API_KEY=
SENDGRID_FROM_EMAIL=noreply@100daysandbeyond.com
SENDGRID_FROM_NAME=100 Days and Beyond
```

**Action:**

1. Go to https://app.sendgrid.com/settings/api_keys
2. Create API Key with "Full Access"
3. Copy API Key (starts with `SG.`)
4. Verify sender email: `noreply@100daysandbeyond.com`

### Sentry Error Tracking

**Get from:** https://sentry.io

```bash
SENTRY_DSN=
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.01
GIT_COMMIT_SHA=main
```

**Action:**

1. Go to https://sentry.io/organizations
2. Create project for "Python/FastAPI" (backend)
3. Copy DSN (looks like `https://...@sentry.io/...`)

### Rate Limiting & Features

```bash
ENABLE_RATE_LIMITING=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
RATE_LIMIT_PER_DAY=10000

ENABLE_AI_INSIGHTS=true
ENABLE_ANALYTICS=true
ENABLE_WEBSOCKET=false
```

---

## Frontend Environment Variables (srv-d3ihptbipnbc73e72ne0)

### API Configuration

```bash
VITE_API_URL=https://ma-saas-backend.onrender.com
VITE_API_V1_URL=https://ma-saas-backend.onrender.com/api/v1
```

### Clerk Authentication

```bash
VITE_CLERK_PUBLISHABLE_KEY=
```

**Action:** Use the same Clerk Publishable Key from backend section above

### Sentry Error Tracking

```bash
VITE_SENTRY_DSN=
VITE_ENVIRONMENT=production
VITE_GIT_COMMIT_SHA=main
```

**Action:**

1. Create separate Sentry project for "React" (frontend)
2. Copy DSN (different from backend DSN)

### Application Settings

```bash
VITE_APP_NAME=100 Days and Beyond
VITE_APP_DESCRIPTION=Comprehensive M&A Deal Management Platform
VITE_APP_VERSION=2.0.0
VITE_APP_ENV=production
```

### Feature Flags

```bash
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_WEBSOCKET=false
VITE_FEATURE_AI_INSIGHTS=true
VITE_FEATURE_DOCUMENTS=true
VITE_FEATURE_INTEGRATIONS=true
VITE_FEATURE_CONTENT=true
VITE_FEATURE_OPPORTUNITIES=true
VITE_FEATURE_VALUATIONS=true
VITE_FEATURE_ARBITRAGE=true
```

### Development Settings

```bash
VITE_ENABLE_DEV_TOOLS=false
VITE_ENABLE_REDUX_DEVTOOLS=false
VITE_USE_MOCK_DATA=false
```

---

## 🔴 CRITICAL - Security Checklist

Before I set these variables, please complete:

- [ ] **Stripe Keys Rotated** - New keys generated, old keys deleted
- [ ] **All API Keys Fresh** - No keys from git history
- [ ] **Clerk Webhook Configured** - Points to production URL
- [ ] **Stripe Webhook Configured** - Points to production URL
- [ ] **SendGrid Sender Verified** - Can send from noreply@100daysandbeyond.com
- [ ] **Sentry Projects Created** - Separate projects for backend and frontend
- [ ] **R2 Bucket Created** - Named `ma-saas-documents`
- [ ] **This File Not Committed** - Added to .gitignore

---

## 📝 Instructions for Me

Once you've filled in all the values above:

1. **Reply with:** "Keys ready" (don't paste the keys in chat!)
2. **I'll read this file** and set environment variables via Render API
3. **I'll configure CORS** for production domains
4. **I'll update security settings** and HTTPS enforcement
5. **I'll trigger deployments** for both services

---

## 🚀 What Happens Next

After variables are set:

1. Backend redeploys automatically (~5 minutes)
2. Frontend redeploys automatically (~3 minutes)
3. Services restart with new configuration
4. Database migrations run (if configured in pre-deploy)
5. Health checks verify services are running
6. Platform is live at https://100daysandbeyond.com

---

**Estimated Setup Time:** 30-60 minutes to collect all keys
**Deployment Time:** 8-10 minutes after keys are set
**Total Time to Live:** ~1 hour

---

## ⚠️ Security Note

After I set the variables:

- They are stored securely in Render's encrypted vault
- Only accessible via Render dashboard by team members
- Never exposed in logs or API responses
- Can be rotated anytime via dashboard
- Automatically available to service at runtime

**DO NOT:**

- ❌ Commit this file to git
- ❌ Share keys in chat/email
- ❌ Store keys in code files
- ❌ Use test keys in production

**DO:**

- ✅ Store this file securely offline
- ✅ Use password manager for keys
- ✅ Rotate keys periodically
- ✅ Use separate keys per environment
