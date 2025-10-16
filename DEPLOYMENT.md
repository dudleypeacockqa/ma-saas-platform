# M&A SaaS Platform Deployment Guide

## Overview

This guide covers deploying the M&A SaaS Platform to Render.com with PostgreSQL database, multi-tenant architecture, and Claude MCP integration.

## Architecture

- **Frontend**: React SPA deployed as Static Site on Render
- **Backend**: FastAPI application deployed as Web Service on Render
- **Database**: PostgreSQL database on Render
- **AI Integration**: Claude MCP server and Hugging Face MCP server

## Prerequisites

1. GitHub repository: https://github.com/dudleypeacockqa/ma-saas-platform
2. Render.com account
3. Anthropic API key for Claude integration
4. Environment variables configured

## Deployment Steps

### 1. Database Setup

1. **Create PostgreSQL Database on Render**:
   - Go to Render Dashboard → New → PostgreSQL
   - Name: `ma-saas-db`
   - Plan: Starter (can upgrade later)
   - Database Name: `ma_saas_platform`
   - User: `ma_saas_user`

2. **Note the connection details**:
   - Internal Database URL (for backend service)
   - External Database URL (for local development)

### 2. Backend Deployment

1. **Create Web Service**:
   - Go to Render Dashboard → New → Web Service
   - Connect GitHub repository: `dudleypeacockqa/ma-saas-platform`
   - Name: `ma-saas-backend`
   - Root Directory: `backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. **Environment Variables**:

   ```
   DATABASE_URL=<from_postgresql_service>
   SECRET_KEY=<generate_secure_key>
   ANTHROPIC_API_KEY=<your_anthropic_key>
   DEBUG=false
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

3. **Advanced Settings**:
   - Plan: Starter (can upgrade for production)
   - Auto-Deploy: Yes
   - Health Check Path: `/health`

### 3. Frontend Deployment

1. **Create Static Site**:
   - Go to Render Dashboard → New → Static Site
   - Connect same GitHub repository
   - Name: `ma-saas-frontend`
   - Root Directory: `frontend`
   - Build Command: `pnpm install && pnpm run build`
   - Publish Directory: `dist`

2. **Environment Variables**:
   ```
   VITE_API_URL=https://ma-saas-backend.onrender.com
   NODE_ENV=production
   ```

### 4. Database Migration

After backend deployment, run database migrations:

```bash
# Connect to your backend service terminal in Render
alembic upgrade head
```

Or create initial migration:

```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 5. Custom Domain (Optional)

1. **Backend Custom Domain**:
   - Go to backend service → Settings → Custom Domains
   - Add: `api.your-domain.com`

2. **Frontend Custom Domain**:
   - Go to frontend service → Settings → Custom Domains
   - Add: `app.your-domain.com`

3. **Update Environment Variables**:
   - Update `VITE_API_URL` to use custom domain

## Configuration Files

### Backend render.yaml

```yaml
services:
  - type: web
    name: ma-saas-backend
    env: python
    plan: starter
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: ma-saas-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: DEBUG
        value: false

databases:
  - name: ma-saas-db
    plan: starter
    databaseName: ma_saas_platform
    user: ma_saas_user
```

### Frontend render.yaml

```yaml
services:
  - type: static_site
    name: ma-saas-frontend
    buildCommand: pnpm install && pnpm run build
    staticPublishPath: ./dist
    envVars:
      - key: VITE_API_URL
        value: https://ma-saas-backend.onrender.com
      - key: NODE_ENV
        value: production
```

## Multi-Tenant Configuration

The application is configured for multi-tenancy:

1. **Database Level**: All tables include `tenant_id` for data isolation
2. **API Level**: All endpoints validate tenant access
3. **Authentication**: JWT tokens include tenant information
4. **Master Admin**: Can access all tenants for subscription management

## Monitoring and Maintenance

### Health Checks

- Backend: `https://ma-saas-backend.onrender.com/health`
- Frontend: Standard static site monitoring

### Logs

- Backend logs available in Render dashboard
- Database logs available in PostgreSQL service

### Scaling

- **Starter Plan**: Good for development and initial users
- **Standard Plan**: Recommended for production with multiple tenants
- **Pro Plan**: For high-traffic enterprise usage

## Security Considerations

1. **Environment Variables**: Never commit secrets to repository
2. **HTTPS**: Render provides SSL certificates automatically
3. **CORS**: Configured for frontend domain only
4. **Authentication**: JWT tokens with expiration
5. **Database**: Connection pooling and SSL enabled

## Backup Strategy

1. **Database**: Render provides automated backups on paid plans
2. **Code**: GitHub repository serves as code backup
3. **Environment**: Document all environment variables

## Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check Python version compatibility
   - Verify all dependencies in requirements.txt
   - Check build logs in Render dashboard

2. **Database Connection**:
   - Verify DATABASE_URL format
   - Check database service status
   - Ensure migrations are applied

3. **API Connectivity**:
   - Verify CORS settings
   - Check VITE_API_URL in frontend
   - Test API endpoints directly

### Support Resources

- Render Documentation: https://render.com/docs
- FastAPI Documentation: https://fastapi.tiangolo.com
- React Documentation: https://react.dev

## Cost Estimation

### Development/Testing

- PostgreSQL Starter: $7/month
- Backend Web Service Starter: $7/month
- Frontend Static Site: Free
- **Total**: ~$14/month

### Production

- PostgreSQL Standard: $20/month
- Backend Web Service Standard: $25/month
- Frontend Static Site: Free
- **Total**: ~$45/month

## Next Steps

1. Deploy to Render following this guide
2. Test all functionality in production environment
3. Set up monitoring and alerting
4. Configure custom domains
5. Implement backup procedures
6. Plan scaling strategy based on user growth

The platform is now ready for production deployment and can support the bootstrap wealth-building strategy through subscription sales and M&A deal management.
