# Security: Key Rotation Guide

## Response to GitHub Secret Scanning Alert

**Date**: October 12, 2025
**Issue**: Stripe API keys detected in git history
**Status**: ⚠️ **ACTION REQUIRED**

---

## What Happened

GitHub's secret scanning detected Stripe API keys in the git repository history. While we've already **removed and replaced these keys with placeholders** in recent commits, the keys still exist in the git commit history and should be considered potentially compromised.

**Affected Commits**:

- Commits before `e52377e` contained actual Stripe API keys in documentation
- Keys were replaced with `[configured]` placeholders in commits:
  - `e52377e` - Clerk billing migration
  - `ec300f3` - Context directory gitignore
  - `a414bed` - Deployment status summary
  - `41c92b0` - Final deployment report

---

## Security Assessment

### Risk Level: **MEDIUM** ⚠️

**Why Medium Risk**:

- Keys were in **public documentation files** (not `.env` files)
- Keys are now in **public git history** (even though replaced in current files)
- Repository is **public** or accessible to others
- Keys were **live/production keys** (sk*live*_, pk*live*_)

**Mitigating Factors**:

- Keys are already removed from current files ✅
- Keys are replaced with placeholders in recent commits ✅
- Repository may be private (check GitHub settings)

---

## Required Actions

### IMMEDIATE ACTION REQUIRED ⚠️

You **MUST** rotate (regenerate) the exposed Stripe API keys:

#### Step 1: Rotate Stripe Keys (15 minutes)

1. **Log into Stripe Dashboard**: https://dashboard.stripe.com

2. **Navigate to API Keys**:
   - Click "Developers" in left sidebar
   - Click "API keys"

3. **Roll (Rotate) Secret Key**:
   - Find "Secret key" section
   - Click "⋮" (three dots) next to the key
   - Click "Roll key"
   - Confirm the action
   - **Copy the new key immediately** (you won't see it again)

4. **Create New Publishable Key** (if needed):
   - Click "Create restricted key" or "Reveal live key token"
   - Copy the new publishable key

5. **Important**: Keep your Stripe Dashboard open - you'll need these new keys

#### Step 2: Update Local Environment Variables (5 minutes)

Update your **local** `.env` files with the NEW keys:

**Backend** (`backend/.env`):

```bash
# Update these with NEW keys from Stripe Dashboard
STRIPE_SECRET_KEY=sk_live_[NEW_KEY_FROM_STRIPE]
STRIPE_PUBLISHABLE_KEY=pk_live_[NEW_KEY_FROM_STRIPE]
```

**Frontend** (`frontend/.env`):

```bash
# Update with NEW publishable key
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_[NEW_KEY_FROM_STRIPE]
```

**IMPORTANT**: Do **NOT** commit these files to git!

#### Step 3: Update Render Environment Variables (10 minutes)

1. **Log into Render Dashboard**: https://dashboard.render.com

2. **Update Backend Service**:
   - Click on your backend service: "ma-saas-backend"
   - Click "Environment" tab
   - Find `STRIPE_SECRET_KEY`
   - Click "Edit" (pencil icon)
   - Paste the NEW secret key
   - Find `STRIPE_PUBLISHABLE_KEY`
   - Click "Edit"
   - Paste the NEW publishable key
   - Click "Save Changes"

3. **Wait for Auto-Deploy**:
   - Render will automatically redeploy with new keys
   - Wait 2-3 minutes
   - Verify deployment completes successfully

4. **Update Frontend Service** (if Cloudflare):
   - Go to Cloudflare Pages dashboard
   - Navigate to your project
   - Go to Settings → Environment variables
   - Update `VITE_STRIPE_PUBLISHABLE_KEY`
   - Trigger a new deployment

#### Step 4: Test the New Keys (10 minutes)

1. **Test Backend Health**:

   ```bash
   curl https://ma-saas-backend.onrender.com/health
   ```

   Verify: `"status":"healthy"`

2. **Test Frontend**:
   - Visit: https://100daysandbeyond.com/pricing
   - Check browser console for errors
   - Verify Clerk checkout loads correctly

3. **Test a Small Transaction** (Optional):
   - Use Stripe test mode if available
   - Or test with real card (refund immediately)

#### Step 5: Revoke Old Keys in Stripe (CRITICAL)

1. **Back in Stripe Dashboard**
2. **Navigate to API keys**
3. **Find the OLD secret key** (the one that was exposed)
4. **Click "⋮" (three dots)**
5. **Click "Delete key"** or "Revoke key"
6. **Confirm deletion**

**This makes the exposed keys completely useless!** ✅

---

## Verification Checklist

After completing all steps, verify:

- [ ] New Stripe keys generated in Stripe Dashboard
- [ ] Local `.env` files updated with new keys
- [ ] Render environment variables updated with new keys
- [ ] Backend service redeployed successfully
- [ ] Frontend service redeployed (if applicable)
- [ ] Health check passing: https://ma-saas-backend.onrender.com/health
- [ ] Frontend loading correctly: https://100daysandbeyond.com
- [ ] Old keys deleted/revoked in Stripe Dashboard
- [ ] Test transaction completed successfully

---

## GitHub Secret Scanning Resolution

### Option 1: Acknowledge and Close Alert (Recommended)

After rotating keys:

1. Go to the GitHub alert URL provided
2. Click "Close as" → "Revoked" or "False positive"
3. Add comment: "Keys have been rotated and old keys revoked in Stripe Dashboard"
4. Close the alert

**Do NOT click "Allow secret"** - that would be insecure!

### Option 2: Remove from Git History (Advanced)

If you want to completely remove keys from git history:

**WARNING**: This requires force-pushing and may break others' clones!

```bash
# Install BFG Repo-Cleaner
# Download from: https://rtyley.github.io/bfg-repo-cleaner/

# Create a text file with the exposed key patterns
echo "sk_live_51QwSgkFVol9SKsek" > passwords.txt
echo "pk_live_51QwSgkFVol9SKsek" >> passwords.txt

# Run BFG to remove from history
java -jar bfg.jar --replace-text passwords.txt ma-saas-platform/

# Force push to rewrite history
cd ma-saas-platform
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push origin master --force
```

**Only do this if**:

- You're the only developer
- No one else has cloned the repo
- You understand force-push implications

---

## Prevention for Future

### Best Practices Implemented ✅

Already implemented in this repository:

1. ✅ `.env` files in `.gitignore`
2. ✅ `.context/` directory in `.gitignore` for sensitive instructions
3. ✅ Documentation uses placeholders: `[configured]` instead of real keys
4. ✅ Secrets stored in environment variables on hosting platforms
5. ✅ GitHub secret scanning enabled (caught this issue)

### Additional Recommendations

1. **Use `.env.example` files**:
   Create template files with placeholder values:

   ```bash
   STRIPE_SECRET_KEY=sk_live_[YOUR_KEY_HERE]
   STRIPE_PUBLISHABLE_KEY=pk_live_[YOUR_KEY_HERE]
   ```

2. **Pre-commit Hooks**:
   Install `detect-secrets` or similar:

   ```bash
   pip install detect-secrets
   detect-secrets scan
   ```

3. **Environment Variable Management**:
   - Use Render's environment variables (not hardcoded)
   - Use Clerk's secret management
   - Consider HashiCorp Vault for larger teams

4. **Documentation Policy**:
   - Never include real keys in docs
   - Always use placeholders
   - Reference environment variables

---

## Timeline

| Step                       | Estimated Time | Status     |
| -------------------------- | -------------- | ---------- |
| 1. Rotate Stripe keys      | 15 min         | ⏸️ Pending |
| 2. Update local .env files | 5 min          | ⏸️ Pending |
| 3. Update Render env vars  | 10 min         | ⏸️ Pending |
| 4. Test new keys           | 10 min         | ⏸️ Pending |
| 5. Revoke old keys         | 5 min          | ⏸️ Pending |
| 6. Close GitHub alert      | 2 min          | ⏸️ Pending |
| **Total**                  | **~45 min**    | ⏸️         |

---

## Support & Resources

### Stripe

- **Dashboard**: https://dashboard.stripe.com
- **API Keys**: https://dashboard.stripe.com/apikeys
- **Documentation**: https://stripe.com/docs/keys
- **Support**: https://support.stripe.com

### Render

- **Dashboard**: https://dashboard.render.com
- **Docs**: https://render.com/docs/environment-variables
- **Support**: Via dashboard

### GitHub

- **Secret Scanning**: https://docs.github.com/code-security/secret-scanning
- **Security Advisories**: https://github.com/dudleypeacockqa/ma-saas-platform/security

---

## Important Notes

### What NOT to Do ❌

1. ❌ **Do NOT click "Allow secret" in GitHub alert**
   - This would mark the key as safe when it's not
   - The key is still exposed in git history

2. ❌ **Do NOT commit the new keys to git**
   - Keep them in `.env` files only
   - Never in documentation or code

3. ❌ **Do NOT ignore this issue**
   - Exposed keys can be used maliciously
   - Stripe charges could accrue on your account
   - Potential data breach risk

### What TO Do ✅

1. ✅ **Rotate keys immediately** (within 24 hours)
2. ✅ **Update all environments** (local, Render, Cloudflare)
3. ✅ **Revoke old keys** in Stripe Dashboard
4. ✅ **Test thoroughly** after rotation
5. ✅ **Close GitHub alert** after resolution

---

## After Key Rotation

Once you've rotated the keys and updated all environments:

1. **Test Everything**:
   - Pricing page loads
   - Clerk checkout works
   - Webhooks process correctly
   - No console errors

2. **Monitor for 24 Hours**:
   - Check Stripe Dashboard for suspicious activity
   - Monitor Render logs
   - Check error tracking

3. **Document Completion**:
   - Update this file with completion date
   - Note any issues encountered
   - Mark GitHub alert as resolved

---

## Completion

**Key Rotation Completed**: ⏸️ Pending
**Date Completed**: **\*\***\_**\*\***
**Completed By**: **\*\***\_**\*\***
**Issues Encountered**: None / [List any issues]
**GitHub Alert Closed**: ⏸️ Pending

---

**Status**: ⚠️ **AWAITING KEY ROTATION**
**Priority**: **HIGH** - Complete within 24 hours
**Next Action**: Rotate Stripe API keys in dashboard

---

_Document Version_: 1.0
_Created_: October 12, 2025
_Last Updated_: October 12, 2025
