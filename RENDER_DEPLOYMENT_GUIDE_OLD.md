# Render Deployment Guide for 100daysandbeyond.com

## Current Render Setup Status

**Service ID**: srv-d3ihptbipnbc73e72ne0  
**Current URL**: https://ma-saas-platform.onrender.com  
**Target Domain**: 100daysandbeyond.com  
**API Key**: rnd_7cK6Tcaqek5sZ4WSZ5Y3Xqbq2hZ4

## 1. Fix Current Frontend Deployment

Your current service is configured as a Node.js web service, but it should be a static site for the React frontend.

### Step 1: Create New Static Site Service

1. **Go to Render Dashboard** → New → Static Site
2. **Connect Repository**: dudleypeacockqa/ma-saas-platform
3. **Service Name**: ma-saas-frontend
4. **Root Directory**: `frontend`
5. **Build Command**: `pnpm install && pnpm run build`
6. **Publish Directory**: `dist`

### Step 2: Environment Variables for Frontend

```
VITE_API_URL=https://api.100daysandbeyond.com
NODE_ENV=production
```

## 2. Create Backend API Service

### Step 1: Create Web Service for Backend

1. **Go to Render Dashboard** → New → Web Service
2. **Connect Repository**: dudleypeacockqa/ma-saas-platform
3. **Service Name**: ma-saas-backend
4. **Root Directory**: `backend`
5. **Environment**: Python 3
6. **Build Command**: `pip install -r requirements.txt`
7. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 2: Environment Variables for Backend

```
DATABASE_URL=<from_postgresql_service>
SECRET_KEY=<generate_secure_random_key>
ANTHROPIC_API_KEY=<your_anthropic_api_key>
DEBUG=false
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=https://100daysandbeyond.com,https://www.100daysandbeyond.com
```

## 3. Create PostgreSQL Database

1. **Go to Render Dashboard** → New → PostgreSQL
2. **Database Name**: ma-saas-db
3. **Plan**: Starter
4. **Database**: ma_saas_platform
5. **User**: ma_saas_user

## 4. Domain Configuration

### Step 1: Configure Custom Domains

**Frontend (Static Site)**:

- Primary Domain: `100daysandbeyond.com`
- WWW Domain: `www.100daysandbeyond.com`

**Backend (Web Service)**:

- API Domain: `api.100daysandbeyond.com`

### Step 2: DNS Configuration

Add these DNS records to your domain provider:

```
Type    Name    Value
A       @       216.24.57.1
A       www     216.24.57.1
CNAME   api     ma-saas-backend.onrender.com
```

**Alternative CNAME Setup**:

```
Type    Name    Value
CNAME   @       ma-saas-frontend.onrender.com
CNAME   www     ma-saas-frontend.onrender.com
CNAME   api     ma-saas-backend.onrender.com
```

## 5. Update Current Service

Since you already have a service running, you can either:

**Option A: Convert Current Service**

1. Go to your current service settings
2. Change **Root Directory** to `frontend`
3. Change **Build Command** to `pnpm install && pnpm run build`
4. Change **Start Command** to `pnpm start`
5. Add custom domain: `100daysandbeyond.com`

**Option B: Delete and Recreate** (Recommended)

1. Delete current service
2. Create new Static Site for frontend
3. Create new Web Service for backend

## 6. Environment Variables Setup

### Frontend (.env for local development)

```bash
VITE_API_URL=http://localhost:8000
```

### Backend (.env for local development)

```bash
DATABASE_URL=postgresql://username:password@localhost:5432/ma_saas_db
SECRET_KEY=your-super-secret-key-change-in-production
ANTHROPIC_API_KEY=your-anthropic-api-key
DEBUG=true
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 7. Deployment Commands

### Manual Deploy via Git

```bash
cd /path/to/ma-saas-platform
git add .
git commit -m "Configure for Render deployment with custom domain"
git push origin master
```

### Using Deploy Hook

```bash
curl -X POST "https://api.render.com/deploy/srv-d3ihptbipnbc73e72ne0?key=2wugxge0amo"
```

## 8. Health Check Configuration

### Frontend Health Check

- **Path**: `/` (default for static sites)

### Backend Health Check

- **Path**: `/health`

Make sure your FastAPI backend has a health endpoint:

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}
```

## 9. SSL Certificate

Render automatically provides SSL certificates for custom domains. Once DNS is configured:

1. Add custom domain in Render dashboard
2. Wait for DNS propagation (up to 48 hours)
3. SSL certificate will be automatically issued

## 10. Monitoring and Logs

### Access Logs

- Frontend: Render Dashboard → Static Site → Logs
- Backend: Render Dashboard → Web Service → Logs
- Database: Render Dashboard → PostgreSQL → Logs

### Monitoring URLs

- Frontend: https://100daysandbeyond.com
- Backend API: https://api.100daysandbeyond.com/health
- Database: Monitor via backend logs

## 11. Troubleshooting

### Common Issues

**Build Failures**:

- Check Node.js version compatibility
- Verify pnpm is available (Render supports it)
- Check build logs for specific errors

**Domain Not Working**:

- Verify DNS records are correct
- Wait for DNS propagation (24-48 hours)
- Check SSL certificate status

**API Connection Issues**:

- Verify CORS settings in backend
- Check VITE_API_URL in frontend
- Ensure backend health endpoint responds

### Support Resources

- Render Status: https://status.render.com
- Render Docs: https://render.com/docs
- Community: https://community.render.com

## 12. Cost Breakdown

### Current Setup Cost (Monthly)

- Static Site (Frontend): **Free**
- Web Service Starter (Backend): **$7**
- PostgreSQL Starter: **$7**
- **Total**: ~$14/month

### Production Scaling

- Web Service Standard: $25/month
- PostgreSQL Standard: $20/month
- **Total**: ~$45/month

## Next Steps

1. **Create the backend service** following Step 2
2. **Create PostgreSQL database** following Step 3
3. **Configure custom domains** following Step 4
4. **Update DNS records** with your domain provider
5. **Test the complete application** at 100daysandbeyond.com

The platform will be fully operational once these steps are completed!
