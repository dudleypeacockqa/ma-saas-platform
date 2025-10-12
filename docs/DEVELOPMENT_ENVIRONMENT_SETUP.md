# Development Environment Setup Guide - M&A Platform

**Objective**: One-command setup for world-class development experience
**Target**: Developer productive in <15 minutes from git clone
**Strategy**: Docker-first, IDE-optimized, debugging-friendly environment

---

## 🚀 **QUICK START (TL;DR)**

```bash
# Clone and setup in one command
git clone https://github.com/your-org/ma-saas-platform.git
cd ma-saas-platform
make dev-setup

# Start development environment
make dev-up

# Verify everything works
make dev-test

# Open development URLs:
# Frontend: http://localhost:3000
# API Gateway: http://localhost:8000
# Database Admin: http://localhost:8080
# Redis Admin: http://localhost:8081
```

---

## 🛠️ **PREREQUISITES**

### **Required Software**

```bash
# Check if you have the required tools
./scripts/check-prerequisites.sh

# Required versions:
# Docker: 24.0+
# Docker Compose: 2.21+
# Node.js: 18.0+
# Python: 3.11+
# Git: 2.30+
```

### **Recommended IDE Setup**

```json
// .vscode/extensions.json - Auto-install recommended extensions
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.flake8",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "ms-vscode-remote.remote-containers",
    "ms-vscode.thunder-client",
    "cweijan.vscode-postgresql-client2"
  ]
}
```

```json
// .vscode/settings.json - Optimal development settings
{
  "python.defaultInterpreterPath": "./backend/.venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "tailwindCSS.includeLanguages": {
    "javascript": "javascript",
    "typescript": "typescript"
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/node_modules": true,
    "**/.pytest_cache": true
  }
}
```

---

## 🐳 **DOCKER DEVELOPMENT ENVIRONMENT**

### **Complete Docker Setup**

```yaml
# docker-compose.dev.yml - Complete development environment
version: '3.8'

services:
  # Database Services
  postgres:
    image: postgres:15-alpine
    container_name: ma-postgres-dev
    environment:
      POSTGRES_DB: ma_platform_dev
      POSTGRES_USER: dev_user
      POSTGRES_PASSWORD: dev_password
      POSTGRES_MULTIPLE_DATABASES: platform_core
    ports:
      - '5432:5432'
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data
      - ./scripts/postgres-init:/docker-entrypoint-initdb.d
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U dev_user -d ma_platform_dev']
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: ma-redis-dev
    ports:
      - '6379:6379'
    volumes:
      - redis_dev_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ['CMD', 'redis-cli', 'ping']
      interval: 10s
      timeout: 5s
      retries: 3

  # Development Tools
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: ma-pgadmin-dev
    environment:
      PGADMIN_DEFAULT_EMAIL: dev@ma-platform.com
      PGADMIN_DEFAULT_PASSWORD: dev_password
      PGADMIN_CONFIG_SERVER_MODE: 'False'
    ports:
      - '8080:80'
    volumes:
      - pgadmin_dev_data:/var/lib/pgadmin
    depends_on:
      postgres:
        condition: service_healthy

  redis-commander:
    image: rediscommander/redis-commander:latest
    container_name: ma-redis-commander-dev
    environment:
      REDIS_HOSTS: local:redis:6379
    ports:
      - '8081:8081'
    depends_on:
      - redis

  # Local Development Proxy (for HTTPS)
  caddy:
    image: caddy:2-alpine
    container_name: ma-caddy-dev
    ports:
      - '80:80'
      - '443:443'
    volumes:
      - ./configs/Caddyfile.dev:/etc/caddy/Caddyfile
      - caddy_dev_data:/data
      - caddy_dev_config:/config

  # File Storage (MinIO for local S3-compatible storage)
  minio:
    image: minio/minio:latest
    container_name: ma-minio-dev
    environment:
      MINIO_ROOT_USER: dev_access_key
      MINIO_ROOT_PASSWORD: dev_secret_key
    ports:
      - '9000:9000'
      - '9001:9001'
    volumes:
      - minio_dev_data:/data
    command: server /data --console-address ":9001"

  # Microservices (Development Mode)
  deal-service:
    build:
      context: ./services/deal-service
      dockerfile: Dockerfile.dev
    container_name: ma-deal-service-dev
    environment:
      - ENV=development
      - DATABASE_URL=postgresql://dev_user:dev_password@postgres:5432/ma_platform_dev
      - REDIS_URL=redis://redis:6379
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
    ports:
      - '8001:8000'
    volumes:
      - ./services/deal-service:/app
      - deal_service_node_modules:/app/node_modules
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    develop:
      watch:
        - action: sync
          path: ./services/deal-service
          target: /app
        - action: rebuild
          path: ./services/deal-service/requirements.txt

  financial-intelligence-service:
    build:
      context: ./services/financial-intelligence
      dockerfile: Dockerfile.dev
    container_name: ma-financial-service-dev
    environment:
      - ENV=development
      - DATABASE_URL=postgresql://dev_user:dev_password@postgres:5432/ma_platform_dev
      - REDIS_URL=redis://redis:6379
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - XERO_CLIENT_ID=${XERO_CLIENT_ID}
      - QUICKBOOKS_CLIENT_ID=${QUICKBOOKS_CLIENT_ID}
    ports:
      - '8002:8000'
    volumes:
      - ./services/financial-intelligence:/app
    depends_on:
      - postgres
      - redis

  template-service:
    build:
      context: ./services/template-engine
      dockerfile: Dockerfile.dev
    container_name: ma-template-service-dev
    environment:
      - ENV=development
      - DATABASE_URL=postgresql://dev_user:dev_password@postgres:5432/ma_platform_dev
      - REDIS_URL=redis://redis:6379
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - STORAGE_URL=http://minio:9000
    ports:
      - '8003:8000'
    volumes:
      - ./services/template-engine:/app
      - ./templates:/app/templates
    depends_on:
      - postgres
      - minio

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: ma-frontend-dev
    environment:
      - NODE_ENV=development
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=${NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}
    ports:
      - '3000:3000'
    volumes:
      - ./frontend:/app
      - frontend_node_modules:/app/node_modules
    develop:
      watch:
        - action: sync
          path: ./frontend
          target: /app
        - action: rebuild
          path: ./frontend/package.json

volumes:
  postgres_dev_data:
  redis_dev_data:
  pgadmin_dev_data:
  caddy_dev_data:
  caddy_dev_config:
  minio_dev_data:
  deal_service_node_modules:
  frontend_node_modules:
```

### **Development Dockerfiles**

```dockerfile
# services/deal-service/Dockerfile.dev
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Install development tools
RUN pip install debugpy ipdb

# Copy source code
COPY . .

# Development command with hot reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]
```

```dockerfile
# frontend/Dockerfile.dev
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code
COPY . .

# Development command with hot reload
EXPOSE 3000
CMD ["npm", "run", "dev"]
```

---

## 🔧 **MAKEFILE AUTOMATION**

```makefile
# Makefile - One-command development workflows
.PHONY: dev-setup dev-up dev-down dev-test dev-clean dev-logs dev-shell

# Colors for output
YELLOW := \033[1;33m
GREEN := \033[1;32m
RED := \033[1;31m
NC := \033[0m # No Color

dev-setup: ## Complete development environment setup
	@echo "$(YELLOW)Setting up M&A Platform development environment...$(NC)"
	@./scripts/check-prerequisites.sh
	@./scripts/setup-environment.sh
	@echo "$(GREEN)Development environment setup complete!$(NC)"

dev-up: ## Start all development services
	@echo "$(YELLOW)Starting development environment...$(NC)"
	@docker-compose -f docker-compose.dev.yml up -d --build
	@./scripts/wait-for-services.sh
	@./scripts/setup-dev-data.sh
	@echo "$(GREEN)Development environment is ready!$(NC)"
	@echo "Frontend: http://localhost:3000"
	@echo "API: http://localhost:8000"
	@echo "PgAdmin: http://localhost:8080"
	@echo "Redis Commander: http://localhost:8081"

dev-down: ## Stop all development services
	@echo "$(YELLOW)Stopping development environment...$(NC)"
	@docker-compose -f docker-compose.dev.yml down
	@echo "$(GREEN)Development environment stopped$(NC)"

dev-test: ## Run all tests
	@echo "$(YELLOW)Running all tests...$(NC)"
	@./scripts/run-tests.sh
	@echo "$(GREEN)All tests completed$(NC)"

dev-clean: ## Clean up development environment
	@echo "$(YELLOW)Cleaning development environment...$(NC)"
	@docker-compose -f docker-compose.dev.yml down -v
	@docker system prune -f
	@echo "$(GREEN)Development environment cleaned$(NC)"

dev-logs: ## View logs from all services
	@docker-compose -f docker-compose.dev.yml logs -f

dev-shell: ## Access shell in specified service (make dev-shell SERVICE=deal-service)
	@docker exec -it ma-$(SERVICE)-dev /bin/bash

dev-db-shell: ## Access PostgreSQL shell
	@docker exec -it ma-postgres-dev psql -U dev_user -d ma_platform_dev

dev-redis-shell: ## Access Redis CLI
	@docker exec -it ma-redis-dev redis-cli

dev-migrate: ## Run database migrations
	@./scripts/run-migrations.sh

dev-seed: ## Seed database with test data
	@./scripts/seed-database.sh

dev-reset: ## Reset database and reseed
	@./scripts/reset-database.sh

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
```

---

## 📜 **AUTOMATION SCRIPTS**

### **Environment Setup Script**

```bash
#!/bin/bash
# scripts/setup-environment.sh

set -e

echo "🔧 Setting up M&A Platform development environment..."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your API keys and credentials"
fi

# Setup backend Python environment
echo "🐍 Setting up Python environment..."
cd backend
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
cd ..

# Setup frontend Node environment
echo "📦 Setting up Node.js environment..."
cd frontend
npm install
cd ..

# Setup git hooks
echo "🎣 Setting up git hooks..."
cp scripts/pre-commit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Create development directories
echo "📁 Creating development directories..."
mkdir -p logs
mkdir -p uploads
mkdir -p exports
mkdir -p backups

echo "✅ Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your API keys"
echo "2. Run 'make dev-up' to start the development environment"
echo "3. Run 'make dev-test' to verify everything works"
```

### **Service Health Check Script**

```bash
#!/bin/bash
# scripts/wait-for-services.sh

set -e

echo "⏳ Waiting for services to be ready..."

# Function to wait for a service to be healthy
wait_for_service() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1

    echo "🔍 Checking $service..."

    while [ $attempt -le $max_attempts ]; do
        if curl -sf "$url" > /dev/null 2>&1; then
            echo "✅ $service is ready"
            return 0
        fi

        echo "⏳ Waiting for $service... (attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done

    echo "❌ $service failed to start within $((max_attempts * 2)) seconds"
    return 1
}

# Wait for database
echo "🔍 Checking PostgreSQL..."
until docker exec ma-postgres-dev pg_isready -U dev_user -d ma_platform_dev; do
    echo "⏳ Waiting for PostgreSQL..."
    sleep 2
done
echo "✅ PostgreSQL is ready"

# Wait for Redis
echo "🔍 Checking Redis..."
until docker exec ma-redis-dev redis-cli ping | grep PONG; do
    echo "⏳ Waiting for Redis..."
    sleep 2
done
echo "✅ Redis is ready"

# Wait for services
wait_for_service "Deal Service" "http://localhost:8001/health"
wait_for_service "Financial Intelligence Service" "http://localhost:8002/health"
wait_for_service "Template Service" "http://localhost:8003/health"
wait_for_service "Frontend" "http://localhost:3000"

echo "🎉 All services are ready!"
```

### **Test Runner Script**

```bash
#!/bin/bash
# scripts/run-tests.sh

set -e

echo "🧪 Running M&A Platform test suite..."

# Backend tests
echo "🐍 Running backend tests..."
cd backend

# Activate virtual environment
source .venv/bin/activate

# Run linting
echo "🔍 Running linting..."
flake8 --max-line-length=88 --extend-ignore=E203,W503 .
black --check .
isort --check-only .

# Run type checking
echo "🔬 Running type checking..."
mypy .

# Run unit tests
echo "🧪 Running unit tests..."
pytest tests/unit -v --cov=app --cov-report=term-missing

# Run integration tests
echo "🔗 Running integration tests..."
pytest tests/integration -v

cd ..

# Frontend tests
echo "📦 Running frontend tests..."
cd frontend

# Run linting
echo "🔍 Running ESLint..."
npm run lint

# Run type checking
echo "🔬 Running TypeScript checks..."
npm run type-check

# Run unit tests
echo "🧪 Running Jest tests..."
npm run test:ci

# Run end-to-end tests
echo "🎭 Running Playwright tests..."
npm run test:e2e

cd ..

echo "✅ All tests passed!"
```

---

## 🐛 **DEBUGGING SETUP**

### **VS Code Debugging Configuration**

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Deal Service",
      "type": "python",
      "request": "attach",
      "connect": {
        "host": "localhost",
        "port": 5678
      },
      "localRoot": "${workspaceFolder}/services/deal-service",
      "remoteRoot": "/app",
      "justMyCode": false
    },
    {
      "name": "Debug Frontend",
      "type": "node",
      "request": "attach",
      "port": 9229,
      "restart": true,
      "localRoot": "${workspaceFolder}/frontend",
      "remoteRoot": "/app",
      "skipFiles": ["<node_internals>/**"]
    },
    {
      "name": "Debug Tests",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/backend/.venv/bin/pytest",
      "args": ["${workspaceFolder}/backend/tests", "-v", "--capture=no"],
      "cwd": "${workspaceFolder}/backend",
      "env": {
        "DATABASE_URL": "postgresql://dev_user:dev_password@localhost:5432/ma_platform_test"
      }
    }
  ]
}
```

### **Debug-Enabled Service Configuration**

```python
# services/deal-service/debug_config.py
import os
import debugpy

if os.getenv("ENV") == "development":
    # Enable debugpy for remote debugging
    debugpy.listen(("0.0.0.0", 5678))
    print("🐛 Debug server listening on port 5678")

    # Optional: Wait for debugger to attach
    if os.getenv("WAIT_FOR_DEBUGGER") == "true":
        print("⏳ Waiting for debugger to attach...")
        debugpy.wait_for_client()
        print("🔗 Debugger attached!")
```

---

## 📊 **PERFORMANCE MONITORING**

### **Local Performance Dashboard**

```yaml
# monitoring/docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: ma-prometheus-dev
    ports:
      - '9090:9090'
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_dev_data:/prometheus

  grafana:
    image: grafana/grafana:latest
    container_name: ma-grafana-dev
    ports:
      - '3001:3000'
    environment:
      GF_SECURITY_ADMIN_PASSWORD: dev_password
    volumes:
      - grafana_dev_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources

  jaeger:
    image: jaegertracing/all-in-one:latest
    container_name: ma-jaeger-dev
    ports:
      - '14268:14268'
      - '16686:16686'
    environment:
      COLLECTOR_OTLP_ENABLED: true

volumes:
  prometheus_dev_data:
  grafana_dev_data:
```

This development environment setup ensures that any developer can be productive within 15 minutes of cloning the repository, with full debugging capabilities, automated testing, and performance monitoring - essential for building your world-class M&A platform efficiently.
