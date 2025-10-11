# Render Deployment Update Guide - Cloudflare R2 Integration

## Overview
This guide will help you update your existing Render deployment to include Cloudflare R2 storage configuration for document management in your M&A SaaS platform.

## 🎯 What We're Adding
- Cloudflare R2 storage provider configuration
- Document upload/download capabilities
- Multi-tenant file organization
- Enterprise-grade security settings

## 📋 Step-by-Step Update Process

### Option 1: Update via Render Dashboard (Recommended)

#### 1. Access Your Render Service
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Navigate to your `ma-saas-backend` service
3. Click on **"Environment"** tab

#### 2. Add R2 Environment Variables
Add these new environment variables one by one:

**Storage Provider:**
```
STORAGE_PROVIDER = r2
```

**Cloudflare R2 Credentials:**
```
CLOUDFLARE_ACCOUNT_ID = 8424f73b33106452fa180d53b6cc128b
CLOUDFLARE_R2_ACCESS_KEY_ID = fc23212e9240e3fdb61f90bde1c3844f
CLOUDFLARE_R2_SECRET_ACCESS_KEY = c0ccf727fd530d84c56f82a9433fb619f56099897b9eb73760dae9ddcd05872c
CLOUDFLARE_R2_BUCKET_NAME = ma-platform-documents
CLOUDFLARE_R2_ENDPOINT = https://8424f73b33106452fa180d53b6cc128b.r2.cloudflarestorage.com
```

**R2 Configuration:**
```
R2_REGION = auto
R2_PUBLIC_URL = https://documents.100daysandbeyond.com
R2_MAX_FILE_SIZE = 100MB
R2_ALLOWED_EXTENSIONS = pdf,doc,docx,xls,xlsx,ppt,pptx,txt,csv,jpg,jpeg,png,gif
R2_SIGNED_URL_EXPIRY = 3600
R2_CORS_ORIGINS = https://100daysandbeyond.com,https://www.100daysandbeyond.com
R2_ENCRYPTION_ENABLED = true
```

#### 3. Update Existing Variables
Update these existing environment variables:

**ALLOWED_ORIGINS:** (Update to include production domains)
```
ALLOWED_ORIGINS = https://100daysandbeyond.com,https://www.100daysandbeyond.com,http://localhost:3000,http://localhost:5173
```

#### 4. Deploy Changes
1. Click **"Save Changes"**
2. Render will automatically redeploy your service
3. Monitor the deployment logs for any issues

### Option 2: Update via render.yaml (Alternative)

#### 1. Replace render.yaml
```bash
# In your local project
cd ma-saas-platform/backend
cp render-r2-update.yaml render.yaml
```

#### 2. Commit and Push
```bash
git add render.yaml
git commit -m "Add Cloudflare R2 storage configuration"
git push origin main
```

#### 3. Manual Environment Variables
You'll still need to manually set these sensitive variables in Render dashboard:
- `CLOUDFLARE_R2_ACCESS_KEY_ID`
- `CLOUDFLARE_R2_SECRET_ACCESS_KEY`
- `CLOUDFLARE_ACCOUNT_ID`

## 🔍 Verification Steps

### 1. Check Deployment Status
1. Monitor deployment logs in Render dashboard
2. Ensure service starts without errors
3. Check that all environment variables are loaded

### 2. Test R2 Integration
```bash
# Test API endpoint (replace with your actual backend URL)
curl -X GET https://ma-saas-backend.onrender.com/health

# Test document upload endpoint
curl -X POST https://ma-saas-backend.onrender.com/api/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test-document.pdf"
```

### 3. Verify in Cloudflare Dashboard
1. Go to Cloudflare R2 → `ma-platform-documents` bucket
2. Check for test uploads in the Objects tab
3. Monitor usage in the Metrics tab

## 🚨 Troubleshooting

### Common Issues:

**1. Service Won't Start**
- Check deployment logs for missing environment variables
- Verify all R2 credentials are correctly set
- Ensure no typos in variable names

**2. File Upload Fails**
- Verify R2 bucket permissions
- Check CORS configuration
- Confirm file size limits

**3. Authentication Errors**
- Verify R2 API token has correct permissions
- Check account ID matches your Cloudflare account
- Ensure bucket name is exactly: `ma-platform-documents`

### Debug Commands:
```bash
# Check environment variables in Render shell
echo $STORAGE_PROVIDER
echo $CLOUDFLARE_R2_BUCKET_NAME

# Test R2 connection
python -c "import boto3; print('R2 client created successfully')"
```

## 🎉 Success Indicators

✅ **Deployment Complete:** Service shows "Live" status in Render
✅ **Environment Variables:** All R2 variables visible in Environment tab
✅ **API Health:** `/health` endpoint returns 200 OK
✅ **File Upload:** Document upload API works without errors
✅ **R2 Storage:** Files appear in Cloudflare R2 bucket

## 📊 Cost Benefits Achieved

After successful deployment:
- **Zero storage costs** (10GB free forever)
- **Unlimited bandwidth** (no egress charges)
- **Enterprise security** (encryption, signed URLs)
- **Global performance** (Cloudflare edge network)

## 🚀 Next Steps

1. **Test Document Upload** via your frontend
2. **Configure CORS** if needed for browser uploads
3. **Set up Custom Domain** for R2 public access (optional)
4. **Monitor Usage** in Cloudflare R2 dashboard
5. **Launch Beta Program** with document management features

Your M&A platform now has enterprise-grade document storage integrated with your Render deployment!

---

**Need Help?** 
- Check Render deployment logs for specific error messages
- Verify R2 credentials in Cloudflare dashboard
- Test local R2 connection first using `test_r2_setup.py`
