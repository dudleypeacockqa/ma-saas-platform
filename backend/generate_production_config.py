#!/usr/bin/env python3
"""
Simple Production Configuration Generator
Creates production deployment files without Unicode issues
"""

import os
import sys
from datetime import datetime

def create_env_production():
    """Create production environment file"""
    env_content = """# M&A Platform Production Environment Configuration
# Generated: {timestamp}

# Database Configuration
DATABASE_URL=postgresql+asyncpg://ma_user:${{DB_PASSWORD}}@${{DB_HOST}}:5432/ma_saas_platform
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30

# Security
SECRET_KEY=${{SECRET_KEY}}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=false
ENVIRONMENT=production

# Clerk Authentication
CLERK_SECRET_KEY=${{CLERK_SECRET_KEY}}
CLERK_PUBLISHABLE_KEY=${{CLERK_PUBLISHABLE_KEY}}
CLERK_WEBHOOK_SECRET=${{CLERK_WEBHOOK_SECRET}}

# AI Integration
ANTHROPIC_API_KEY=${{ANTHROPIC_API_KEY}}
CLAUDE_MODEL=claude-3-5-sonnet-20241022
CLAUDE_MAX_TOKENS=4000
CLAUDE_TEMPERATURE=0.1
OPENAI_API_KEY=${{OPENAI_API_KEY}}

# Stripe Payments
STRIPE_SECRET_KEY=${{STRIPE_SECRET_KEY}}
STRIPE_PUBLISHABLE_KEY=${{STRIPE_PUBLISHABLE_KEY}}
STRIPE_WEBHOOK_SECRET=${{STRIPE_WEBHOOK_SECRET}}

# Redis Cache
REDIS_URL=${{REDIS_URL}}
REDIS_MAX_CONNECTIONS=100
CACHE_ENABLED=true

# Cloudflare R2 Storage
STORAGE_PROVIDER=r2
CLOUDFLARE_ACCOUNT_ID=${{CLOUDFLARE_ACCOUNT_ID}}
R2_ACCESS_KEY_ID=${{R2_ACCESS_KEY_ID}}
R2_SECRET_ACCESS_KEY=${{R2_SECRET_ACCESS_KEY}}
R2_BUCKET_NAME=ma-saas-documents

# SendGrid Email
SENDGRID_API_KEY=${{SENDGRID_API_KEY}}
SENDGRID_FROM_EMAIL=noreply@100daysandbeyond.com

# CORS Configuration
ALLOWED_ORIGINS=https://100daysandbeyond.com,https://www.100daysandbeyond.com,https://app.100daysandbeyond.com

# Performance Settings
MAX_REQUEST_SIZE=104857600
RATE_LIMIT_PER_MINUTE=1000
WORKERS=4
WORKER_TIMEOUT=120

# Logging
LOG_LEVEL=INFO

# Feature Flags
FEATURE_AI_INSIGHTS_ENABLED=true
FEATURE_COMMUNITY_ENABLED=true
ANALYTICS_ENABLED=true

# Security Headers
SECURE_HEADERS_ENABLED=true
CSRF_PROTECTION=true
GDPR_COMPLIANCE=true
""".format(timestamp=datetime.now().isoformat())

    with open('.env.production', 'w') as f:
        f.write(env_content)

def create_deployment_checklist():
    """Create deployment checklist"""
    checklist_content = """# M&A Platform Production Deployment Checklist

## Pre-Deployment Setup
- [ ] Server Provisioning: Production server with minimum 4GB RAM, 2 CPU cores
- [ ] Domain Configuration: DNS records for api.100daysandbeyond.com
- [ ] SSL Certificates: Valid SSL certificates installed
- [ ] Database Setup: PostgreSQL production instance configured
- [ ] Redis Setup: Redis production instance configured

## Environment Configuration
- [ ] Production Environment File: .env.production created with all required variables
- [ ] Secret Key: Generate secure 32+ character SECRET_KEY
- [ ] Database URL: Production PostgreSQL connection string
- [ ] Redis URL: Production Redis connection string

## External Service Configuration
- [ ] Clerk Authentication: Production API keys (sk_live_*, pk_live_*)
- [ ] Claude AI: Production ANTHROPIC_API_KEY
- [ ] OpenAI: Production OPENAI_API_KEY for embeddings
- [ ] Cloudflare R2: Production storage credentials
- [ ] Stripe Payments: Production payment processing keys
- [ ] SendGrid Email: Production email API key

## Security Configuration
- [ ] Firewall Rules: Configure server firewall (ports 80, 443, 22 only)
- [ ] User Permissions: Create ma-platform user with restricted permissions
- [ ] File Permissions: Set proper ownership and permissions
- [ ] Security Headers: Verify security headers in Nginx configuration

## Application Deployment
- [ ] Code Deployment: Latest code deployed to /opt/ma-platform/
- [ ] Dependencies: Python virtual environment with production dependencies
- [ ] Database Migration: Run database migrations for production schema
- [ ] Static Files: Configure static file serving

## Service Configuration
- [ ] Systemd Service: Install and enable ma-platform.service
- [ ] Nginx Configuration: Install production Nginx configuration
- [ ] Service Startup: Verify services start automatically on boot
- [ ] Health Checks: Install and test health check script

## Testing & Validation
- [ ] Service Health: All services responding to health checks
- [ ] API Endpoints: Test critical API endpoints
- [ ] External Integrations: Verify all external service connections
- [ ] Multi-Tenant Features: Test organization isolation
- [ ] File Upload: Test document upload to Cloudflare R2
- [ ] Authentication: Test Clerk authentication flow
- [ ] Payment Processing: Test Stripe integration

## Monitoring & Logging
- [ ] Log Configuration: Centralized logging setup
- [ ] Error Tracking: Sentry integration (if configured)
- [ ] Performance Monitoring: Application performance monitoring
- [ ] Uptime Monitoring: External uptime monitoring service

## Backup & Recovery
- [ ] Database Backups: Automated PostgreSQL backups configured
- [ ] File Backups: Cloudflare R2 backup strategy
- [ ] Recovery Testing: Test backup restoration procedures

## Go-Live Process
- [ ] Soft Launch: Internal testing with limited users
- [ ] Load Testing: Performance testing under expected load
- [ ] Final Security Review: Security audit of production configuration
- [ ] Documentation: Update production documentation
- [ ] Team Training: Operations team trained on deployment

## Post-Deployment
- [ ] Monitor Performance: Watch application performance metrics
- [ ] Check Error Logs: Review error logs for issues
- [ ] User Acceptance Testing: Validate with real user scenarios
- [ ] Scaling Plan: Document scaling procedures for growth

Generated: {timestamp}
""".format(timestamp=datetime.now().isoformat())

    with open('PRODUCTION_DEPLOYMENT_CHECKLIST.md', 'w') as f:
        f.write(checklist_content)

def create_health_check():
    """Create health check script"""
    health_script = """#!/bin/bash
# M&A Platform Health Check Script

API_URL="http://localhost:8000"
HEALTH_ENDPOINT="$API_URL/health"

echo "M&A Platform Health Check - $(date)"
echo "=================================="

# Check API health
response=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_ENDPOINT" || echo "000")

if [ "$response" = "200" ]; then
    echo "[PASS] API health check (HTTP $response)"
    exit 0
else
    echo "[FAIL] API health check (HTTP $response)"
    exit 1
fi
"""

    with open('health-check.sh', 'w') as f:
        f.write(health_script)

    # Make executable on Unix systems
    try:
        os.chmod('health-check.sh', 0o755)
    except:
        pass

def main():
    """Generate production configuration files"""
    print("M&A Platform Production Configuration Generator")
    print("=" * 50)

    try:
        create_env_production()
        print("[PASS] Production environment configuration (.env.production)")

        create_deployment_checklist()
        print("[PASS] Deployment checklist (PRODUCTION_DEPLOYMENT_CHECKLIST.md)")

        create_health_check()
        print("[PASS] Health check script (health-check.sh)")

        print("\nAll production configurations generated successfully!")
        print("\nNext Steps:")
        print("1. Review .env.production and replace ${VARIABLE} placeholders with actual values")
        print("2. Follow PRODUCTION_DEPLOYMENT_CHECKLIST.md for deployment")
        print("3. Use health-check.sh to monitor service health")

        return 0

    except Exception as e:
        print(f"Error generating configurations: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)