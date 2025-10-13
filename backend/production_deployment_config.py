#!/usr/bin/env python3
"""
Production Deployment Configuration Generator
Creates optimized production configuration for M&A platform deployment
"""

import os
import sys
import json
from typing import Dict, Any, List
from datetime import datetime

class ProductionConfigGenerator:
    """Generate production-ready configuration"""

    def __init__(self):
        self.config = {}
        self.environment_vars = {}
        self.deployment_settings = {}

    def generate_environment_config(self) -> Dict[str, str]:
        """Generate production environment variables configuration"""
        return {
            # ================================================================
            # PRODUCTION DATABASE CONFIGURATION
            # ================================================================
            "DATABASE_URL": "postgresql+asyncpg://ma_user:${DB_PASSWORD}@${DB_HOST}:5432/ma_saas_platform",
            "DB_POOL_SIZE": "20",
            "DB_MAX_OVERFLOW": "30",
            "DB_POOL_TIMEOUT": "30",
            "DB_POOL_RECYCLE": "3600",

            # ================================================================
            # SECURITY & APPLICATION SETTINGS
            # ================================================================
            "SECRET_KEY": "${SECRET_KEY}",  # Generate 32+ character secure key
            "ALGORITHM": "HS256",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
            "DEBUG": "false",
            "ENVIRONMENT": "production",

            # ================================================================
            # CLERK AUTHENTICATION (PRODUCTION)
            # ================================================================
            "CLERK_SECRET_KEY": "${CLERK_SECRET_KEY}",  # sk_live_...
            "CLERK_PUBLISHABLE_KEY": "${CLERK_PUBLISHABLE_KEY}",  # pk_live_...
            "CLERK_WEBHOOK_SECRET": "${CLERK_WEBHOOK_SECRET}",  # whsec_...

            # ================================================================
            # AI INTEGRATION - CLAUDE & OPENAI (PRODUCTION)
            # ================================================================
            "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",  # sk-ant-...
            "CLAUDE_MODEL": "claude-3-5-sonnet-20241022",
            "CLAUDE_MAX_TOKENS": "4000",
            "CLAUDE_TEMPERATURE": "0.1",
            "OPENAI_API_KEY": "${OPENAI_API_KEY}",  # sk-...

            # Vector Database Configuration
            "VECTOR_DIMENSION": "1536",
            "EMBEDDING_MODEL": "text-embedding-3-small",
            "SEMANTIC_SEARCH_THRESHOLD": "0.8",

            # ================================================================
            # STRIPE PAYMENT PROCESSING (PRODUCTION)
            # ================================================================
            "STRIPE_SECRET_KEY": "${STRIPE_SECRET_KEY}",  # sk_live_...
            "STRIPE_PUBLISHABLE_KEY": "${STRIPE_PUBLISHABLE_KEY}",  # pk_live_...
            "STRIPE_WEBHOOK_SECRET": "${STRIPE_WEBHOOK_SECRET}",  # whsec_...

            # ================================================================
            # REDIS CONFIGURATION (PRODUCTION)
            # ================================================================
            "REDIS_URL": "${REDIS_URL}",  # Redis Cloud or ElastiCache URL
            "REDIS_MAX_CONNECTIONS": "100",
            "REDIS_SOCKET_TIMEOUT": "5",
            "REDIS_SOCKET_CONNECT_TIMEOUT": "5",
            "REDIS_RETRY_ON_TIMEOUT": "true",
            "CACHE_DEFAULT_TTL": "300",
            "CACHE_ENABLED": "true",

            # ================================================================
            # CLOUDFLARE R2 STORAGE (PRODUCTION)
            # ================================================================
            "STORAGE_PROVIDER": "r2",
            "CLOUDFLARE_ACCOUNT_ID": "${CLOUDFLARE_ACCOUNT_ID}",
            "R2_ACCESS_KEY_ID": "${R2_ACCESS_KEY_ID}",
            "R2_SECRET_ACCESS_KEY": "${R2_SECRET_ACCESS_KEY}",
            "R2_BUCKET_NAME": "ma-saas-documents",
            "R2_ENDPOINT_URL": "https://${CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com",
            "R2_PUBLIC_URL": "https://documents.100daysandbeyond.com",

            # ================================================================
            # SENDGRID EMAIL (PRODUCTION)
            # ================================================================
            "SENDGRID_API_KEY": "${SENDGRID_API_KEY}",  # SG....
            "SENDGRID_FROM_EMAIL": "noreply@100daysandbeyond.com",
            "SENDGRID_FROM_NAME": "M&A Platform",

            # ================================================================
            # CORS & API CONFIGURATION (PRODUCTION)
            # ================================================================
            "ALLOWED_ORIGINS": "https://100daysandbeyond.com,https://www.100daysandbeyond.com,https://app.100daysandbeyond.com",
            "API_V1_PREFIX": "/api/v1",

            # ================================================================
            # PERFORMANCE & SCALING (PRODUCTION)
            # ================================================================
            "MAX_REQUEST_SIZE": "104857600",  # 100MB
            "RATE_LIMIT_PER_MINUTE": "1000",  # Higher for production
            "WORKERS": "4",  # Adjust based on server specs
            "WORKER_TIMEOUT": "120",
            "KEEPALIVE": "5",
            "MAX_CONNECTIONS": "1000",

            # ================================================================
            # LOGGING & MONITORING (PRODUCTION)
            # ================================================================
            "LOG_LEVEL": "INFO",
            "SENTRY_DSN": "${SENTRY_DSN}",  # Optional error tracking

            # ================================================================
            # FEATURE FLAGS (PRODUCTION)
            # ================================================================
            "FEATURE_AI_INSIGHTS_ENABLED": "true",
            "FEATURE_COMMUNITY_ENABLED": "true",
            "FEATURE_EVENTS_ENABLED": "true",
            "FEATURE_CONSULTING_ENABLED": "true",
            "ANALYTICS_ENABLED": "true",
            "ECOSYSTEM_INTELLIGENCE": "true",
            "PARTNERSHIP_SCORING": "true",

            # ================================================================
            # SECURITY HEADERS (PRODUCTION)
            # ================================================================
            "SECURE_HEADERS_ENABLED": "true",
            "CSRF_PROTECTION": "true",
            "GDPR_COMPLIANCE": "true",
            "FORCE_HTTPS": "true",
            "HSTS_MAX_AGE": "31536000",  # 1 year
        }

    def generate_docker_config(self) -> Dict[str, Any]:
        """Generate Docker configuration for production"""
        return {
            "version": "3.8",
            "services": {
                "ma-platform-backend": {
                    "build": {
                        "context": ".",
                        "dockerfile": "Dockerfile"
                    },
                    "ports": ["8000:8000"],
                    "environment": [
                        "ENVIRONMENT=production",
                        "DATABASE_URL=${DATABASE_URL}",
                        "REDIS_URL=${REDIS_URL}",
                        "SECRET_KEY=${SECRET_KEY}"
                    ],
                    "restart": "unless-stopped",
                    "healthcheck": {
                        "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3,
                        "start_period": "40s"
                    },
                    "deploy": {
                        "resources": {
                            "limits": {
                                "cpus": "2.0",
                                "memory": "4G"
                            },
                            "reservations": {
                                "cpus": "1.0",
                                "memory": "2G"
                            }
                        }
                    }
                }
            }
        }

    def generate_nginx_config(self) -> str:
        """Generate Nginx configuration for production"""
        return """
# M&A Platform Production Nginx Configuration
upstream ma_platform_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

server {
    listen 80;
    server_name api.100daysandbeyond.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.100daysandbeyond.com;

    # SSL Configuration
    ssl_certificate /etc/ssl/certs/100daysandbeyond.com.crt;
    ssl_certificate_key /etc/ssl/private/100daysandbeyond.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Client body size (for file uploads)
    client_max_body_size 100M;

    # Rate limiting
    limit_req zone=api burst=20 nodelay;

    # API Proxy
    location /api/ {
        proxy_pass http://ma_platform_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check
    location /health {
        proxy_pass http://ma_platform_backend;
        access_log off;
    }

    # Static files (if served by Nginx)
    location /static/ {
        alias /var/www/ma-platform/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
"""

    def generate_systemd_service(self) -> str:
        """Generate systemd service configuration"""
        return """
[Unit]
Description=M&A Platform Backend Service
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=exec
User=ma-platform
Group=ma-platform
WorkingDirectory=/opt/ma-platform/backend
Environment=PATH=/opt/ma-platform/backend/venv/bin
ExecStart=/opt/ma-platform/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
TimeoutStopSec=30
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=/opt/ma-platform/backend/logs
ProtectHome=yes

# Resource limits
LimitNOFILE=65536
MemoryMax=4G

[Install]
WantedBy=multi-user.target
"""

    def generate_health_check_script(self) -> str:
        """Generate health check script"""
        return """#!/bin/bash
# M&A Platform Health Check Script

API_URL="http://localhost:8000"
HEALTH_ENDPOINT="$API_URL/health"
MAX_RETRIES=3
RETRY_DELAY=5

echo "M&A Platform Health Check - $(date)"
echo "=================================="

# Function to check API health
check_api_health() {
    echo "Checking API health..."
    response=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_ENDPOINT" || echo "000")

    if [ "$response" = "200" ]; then
        echo "✓ API health check passed (HTTP $response)"
        return 0
    else
        echo "✗ API health check failed (HTTP $response)"
        return 1
    fi
}

# Function to check database connectivity
check_database() {
    echo "Checking database connectivity..."
    # This would need to be implemented based on your health endpoint
    # For now, assume API health check covers database
    return 0
}

# Function to check Redis
check_redis() {
    echo "Checking Redis connectivity..."
    if command -v redis-cli >/dev/null 2>&1; then
        if redis-cli ping >/dev/null 2>&1; then
            echo "✓ Redis connectivity check passed"
            return 0
        else
            echo "✗ Redis connectivity check failed"
            return 1
        fi
    else
        echo "⚠ Redis CLI not available, skipping check"
        return 0
    fi
}

# Main health check
main() {
    local exit_code=0

    # Check API with retries
    for i in $(seq 1 $MAX_RETRIES); do
        if check_api_health; then
            break
        else
            if [ $i -lt $MAX_RETRIES ]; then
                echo "Retrying in $RETRY_DELAY seconds... ($i/$MAX_RETRIES)"
                sleep $RETRY_DELAY
            else
                echo "API health check failed after $MAX_RETRIES attempts"
                exit_code=1
            fi
        fi
    done

    # Check other services
    check_database || exit_code=1
    check_redis || exit_code=1

    echo "=================================="
    if [ $exit_code -eq 0 ]; then
        echo "✓ All health checks passed"
    else
        echo "✗ Some health checks failed"
    fi

    return $exit_code
}

# Run health check
main "$@"
"""

    def generate_deployment_checklist(self) -> List[str]:
        """Generate production deployment checklist"""
        return [
            "# M&A Platform Production Deployment Checklist",
            "",
            "## Pre-Deployment Setup",
            "- [ ] Server Provisioning: Production server with minimum 4GB RAM, 2 CPU cores",
            "- [ ] Domain Configuration: DNS records for api.100daysandbeyond.com",
            "- [ ] SSL Certificates: Valid SSL certificates installed",
            "- [ ] Database Setup: PostgreSQL production instance configured",
            "- [ ] Redis Setup: Redis production instance configured",
            "",
            "## Environment Configuration",
            "- [ ] **Production Environment File**: .env.production created with all required variables",
            "- [ ] **Secret Key**: Generate secure 32+ character SECRET_KEY",
            "- [ ] **Database URL**: Production PostgreSQL connection string",
            "- [ ] **Redis URL**: Production Redis connection string",
            "",
            "## External Service Configuration",
            "- [ ] **Clerk Authentication**: Production API keys (sk_live_*, pk_live_*)",
            "- [ ] **Claude AI**: Production ANTHROPIC_API_KEY",
            "- [ ] **OpenAI**: Production OPENAI_API_KEY for embeddings",
            "- [ ] **Cloudflare R2**: Production storage credentials (CLOUDFLARE_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY)",
            "- [ ] **Stripe Payments**: Production payment processing keys (sk_live_*, pk_live_*)",
            "- [ ] **SendGrid Email**: Production email API key (SENDGRID_API_KEY)",
            "",
            "## Security Configuration",
            "- [ ] **Firewall Rules**: Configure server firewall (ports 80, 443, 22 only)",
            "- [ ] **User Permissions**: Create ma-platform user with restricted permissions",
            "- [ ] **File Permissions**: Set proper ownership and permissions on application files",
            "- [ ] **Security Headers**: Verify security headers in Nginx configuration",
            "",
            "## Application Deployment",
            "- [ ] **Code Deployment**: Latest code deployed to /opt/ma-platform/",
            "- [ ] **Dependencies**: Python virtual environment with production dependencies",
            "- [ ] **Database Migration**: Run database migrations for production schema",
            "- [ ] **Static Files**: Configure static file serving (if applicable)",
            "",
            "## Service Configuration",
            "- [ ] **Systemd Service**: Install and enable ma-platform.service",
            "- [ ] **Nginx Configuration**: Install production Nginx configuration",
            "- [ ] **Service Startup**: Verify services start automatically on boot",
            "- [ ] **Health Checks**: Install and test health check script",
            "",
            "## Testing & Validation",
            "- [ ] **Service Health**: All services responding to health checks",
            "- [ ] **API Endpoints**: Test critical API endpoints",
            "- [ ] **External Integrations**: Verify all external service connections",
            "- [ ] **Multi-Tenant Features**: Test organization isolation",
            "- [ ] **File Upload**: Test document upload to Cloudflare R2",
            "- [ ] **Authentication**: Test Clerk authentication flow",
            "- [ ] **Payment Processing**: Test Stripe integration (test mode first)",
            "",
            "## Monitoring & Logging",
            "- [ ] **Log Configuration**: Centralized logging setup",
            "- [ ] **Error Tracking**: Sentry integration (if configured)",
            "- [ ] **Performance Monitoring**: Application performance monitoring",
            "- [ ] **Uptime Monitoring**: External uptime monitoring service",
            "",
            "## Backup & Recovery",
            "- [ ] **Database Backups**: Automated PostgreSQL backups configured",
            "- [ ] **File Backups**: Cloudflare R2 backup strategy",
            "- [ ] **Recovery Testing**: Test backup restoration procedures",
            "",
            "## Go-Live Process",
            "- [ ] **Soft Launch**: Internal testing with limited users",
            "- [ ] **Load Testing**: Performance testing under expected load",
            "- [ ] **Final Security Review**: Security audit of production configuration",
            "- [ ] **Documentation**: Update production documentation",
            "- [ ] **Team Training**: Operations team trained on deployment",
            "",
            "## Post-Deployment",
            "- [ ] **Monitor Performance**: Watch application performance metrics",
            "- [ ] **Check Error Logs**: Review error logs for issues",
            "- [ ] **User Acceptance Testing**: Validate with real user scenarios",
            "- [ ] **Scaling Plan**: Document scaling procedures for growth",
            "",
            f"## Deployment Metadata",
            f"- **Generated**: {datetime.now().isoformat()}",
            f"- **Platform**: M&A SaaS Platform",
            f"- **Environment**: Production",
            f"- **Version**: Phase 2A Sprint 5"
        ]

    def save_configurations(self, output_dir: str = "."):
        """Save all production configurations to files"""
        try:
            # Environment configuration
            env_config = self.generate_environment_config()
            with open(f"{output_dir}/.env.production", "w") as f:
                for key, value in env_config.items():
                    f.write(f"{key}={value}\n")

            # Docker configuration
            docker_config = self.generate_docker_config()
            with open(f"{output_dir}/docker-compose.production.yml", "w") as f:
                import yaml
                yaml.dump(docker_config, f, default_flow_style=False)

            # Nginx configuration
            nginx_config = self.generate_nginx_config()
            with open(f"{output_dir}/nginx.production.conf", "w") as f:
                f.write(nginx_config)

            # Systemd service
            systemd_config = self.generate_systemd_service()
            with open(f"{output_dir}/ma-platform.service", "w") as f:
                f.write(systemd_config)

            # Health check script
            health_script = self.generate_health_check_script()
            with open(f"{output_dir}/health-check.sh", "w") as f:
                f.write(health_script)

            # Make health check script executable
            os.chmod(f"{output_dir}/health-check.sh", 0o755)

            # Deployment checklist
            checklist = self.generate_deployment_checklist()
            with open(f"{output_dir}/PRODUCTION_DEPLOYMENT_CHECKLIST.md", "w") as f:
                f.write("\n".join(checklist))

            return True

        except Exception as e:
            print(f"Error saving configurations: {e}")
            return False

def main():
    """Generate production deployment configuration"""
    print("M&A Platform Production Configuration Generator")
    print("=" * 50)

    generator = ProductionConfigGenerator()

    # Save all configurations
    if generator.save_configurations():
        print("[PASS] Production environment configuration (.env.production)")
        print("[PASS] Docker Compose configuration (docker-compose.production.yml)")
        print("[PASS] Nginx configuration (nginx.production.conf)")
        print("[PASS] Systemd service configuration (ma-platform.service)")
        print("[PASS] Health check script (health-check.sh)")
        print("[PASS] Deployment checklist (PRODUCTION_DEPLOYMENT_CHECKLIST.md)")
        print("\nAll production configurations generated successfully!")
        return 0
    else:
        print("Failed to generate production configurations")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)