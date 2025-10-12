# CI/CD Pipeline Design - Microservices Deployment Automation

**Objective**: Zero-downtime deployments with enterprise-grade quality gates
**Target**: Sub-10 minute end-to-end pipeline, 99.9% deployment success rate
**Strategy**: GitOps-driven, automated testing, progressive deployment

---

## 🚀 **PIPELINE OVERVIEW**

### **Multi-Service Pipeline Architecture**

```mermaid
graph TD
    A[Git Push] --> B[Code Quality Gates]
    B --> C[Unit Tests]
    C --> D[Integration Tests]
    D --> E[Security Scans]
    E --> F[Build & Package]
    F --> G[Staging Deployment]
    G --> H[E2E Tests]
    H --> I[Performance Tests]
    I --> J[Production Deployment]
    J --> K[Health Checks]
    K --> L[Rollback/Success]

    subgraph "Quality Gates"
    B1[ESLint/Prettier]
    B2[Black/Flake8]
    B3[Type Checking]
    B4[Code Coverage]
    end

    subgraph "Security"
    E1[SAST Scanning]
    E2[Dependency Audit]
    E3[Secret Detection]
    E4[Container Scanning]
    end

    subgraph "Deployment Strategy"
    J1[Blue-Green Deploy]
    J2[Health Monitoring]
    J3[Automated Rollback]
    end
```

---

## 🔧 **GITHUB ACTIONS WORKFLOWS**

### **Main CI/CD Workflow**

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # Service Change Detection
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      frontend: ${{ steps.changes.outputs.frontend }}
      deal-service: ${{ steps.changes.outputs.deal-service }}
      financial-service: ${{ steps.changes.outputs.financial-service }}
      template-service: ${{ steps.changes.outputs.template-service }}
      document-service: ${{ steps.changes.outputs.document-service }}
      matching-service: ${{ steps.changes.outputs.matching-service }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v2
        id: changes
        with:
          filters: |
            frontend:
              - 'frontend/**'
            deal-service:
              - 'services/deal-service/**'
              - 'shared/**'
            financial-service:
              - 'services/financial-intelligence/**'
              - 'shared/**'
            template-service:
              - 'services/template-engine/**'
              - 'shared/**'
            document-service:
              - 'services/document-service/**'
              - 'shared/**'
            matching-service:
              - 'services/deal-matching/**'
              - 'shared/**'

  # Code Quality Gates
  code-quality:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [frontend, deal-service, financial-service, template-service]
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js (Frontend)
        if: matrix.service == 'frontend'
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: 'frontend/package-lock.json'

      - name: Setup Python (Backend Services)
        if: matrix.service != 'frontend'
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Dependencies (Frontend)
        if: matrix.service == 'frontend'
        run: |
          cd frontend
          npm ci

      - name: Install Dependencies (Backend)
        if: matrix.service != 'frontend'
        run: |
          cd services/${{ matrix.service }}
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt

      - name: Code Quality - Frontend
        if: matrix.service == 'frontend'
        run: |
          cd frontend
          npm run lint
          npm run type-check
          npm run format:check

      - name: Code Quality - Backend
        if: matrix.service != 'frontend'
        run: |
          cd services/${{ matrix.service }}
          black --check .
          flake8 --max-line-length=88 --extend-ignore=E203,W503 .
          isort --check-only .
          mypy .

  # Unit Tests
  unit-tests:
    runs-on: ubuntu-latest
    needs: [detect-changes, code-quality]
    strategy:
      matrix:
        service: [frontend, deal-service, financial-service, template-service]
    steps:
      - uses: actions/checkout@v4

      - name: Setup Test Environment
        run: |
          # Start test dependencies
          docker-compose -f docker-compose.test.yml up -d postgres redis
          # Wait for services
          ./scripts/wait-for-test-services.sh

      - name: Run Unit Tests - Frontend
        if: matrix.service == 'frontend' && needs.detect-changes.outputs.frontend == 'true'
        run: |
          cd frontend
          npm ci
          npm run test:ci

      - name: Run Unit Tests - Backend
        if: matrix.service != 'frontend'
        run: |
          cd services/${{ matrix.service }}
          pip install -r requirements-dev.txt
          pytest tests/unit -v --cov=app --cov-report=xml --cov-fail-under=80

      - name: Upload Coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: ${{ matrix.service }}

  # Security Scanning
  security-scan:
    runs-on: ubuntu-latest
    needs: [detect-changes]
    steps:
      - uses: actions/checkout@v4

      - name: Run SAST Scan
        uses: github/super-linter@v4
        env:
          DEFAULT_BRANCH: main
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          VALIDATE_ALL_CODEBASE: false

      - name: Scan Dependencies (Frontend)
        if: needs.detect-changes.outputs.frontend == 'true'
        run: |
          cd frontend
          npm audit --audit-level=high

      - name: Scan Dependencies (Python)
        run: |
          pip install safety
          find . -name "requirements*.txt" -exec safety check -r {} \;

      - name: Secret Detection
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: main
          head: HEAD

  # Build and Package
  build-images:
    runs-on: ubuntu-latest
    needs: [unit-tests, security-scan]
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'
    strategy:
      matrix:
        service:
          [
            frontend,
            deal-service,
            financial-service,
            template-service,
            document-service,
            matching-service,
          ]
    steps:
      - uses: actions/checkout@v4

      - name: Setup Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract Metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/${{ matrix.service }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and Push Image
        uses: docker/build-push-action@v5
        with:
          context: ./services/${{ matrix.service }}
          file: ./services/${{ matrix.service }}/Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64,linux/arm64

  # Integration Tests
  integration-tests:
    runs-on: ubuntu-latest
    needs: [build-images]
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'
    steps:
      - uses: actions/checkout@v4

      - name: Setup Test Environment
        run: |
          # Use built images for integration testing
          export IMAGE_TAG=${GITHUB_SHA::7}
          docker-compose -f docker-compose.integration.yml up -d
          ./scripts/wait-for-integration-services.sh

      - name: Run Integration Tests
        run: |
          # Run comprehensive integration test suite
          pytest tests/integration -v --timeout=300

      - name: Run API Contract Tests
        run: |
          # Validate API contracts between services
          newman run tests/api/postman-collection.json \
            --environment tests/api/integration-environment.json \
            --reporters cli,junit \
            --reporter-junit-export integration-test-results.xml

      - name: Upload Test Results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: integration-test-results
          path: integration-test-results.xml

  # Staging Deployment
  deploy-staging:
    runs-on: ubuntu-latest
    needs: [integration-tests]
    if: github.ref == 'refs/heads/develop'
    environment: staging
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Staging
        run: |
          # Deploy to Render staging environment
          ./scripts/deploy-staging.sh ${{ github.sha }}

      - name: Run Smoke Tests
        run: |
          # Basic smoke tests on staging
          curl -f https://staging-api.ma-platform.com/health
          pytest tests/smoke -v --base-url=https://staging.ma-platform.com

  # E2E Tests
  e2e-tests:
    runs-on: ubuntu-latest
    needs: [deploy-staging]
    if: github.ref == 'refs/heads/develop'
    steps:
      - uses: actions/checkout@v4

      - name: Setup Playwright
        uses: microsoft/playwright-github-action@v1

      - name: Run E2E Tests
        run: |
          cd frontend
          npm ci
          npx playwright test --config=playwright.config.staging.ts

      - name: Upload E2E Results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: e2e-test-results
          path: frontend/test-results/

  # Production Deployment
  deploy-production:
    runs-on: ubuntu-latest
    needs: [e2e-tests]
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Production
        run: |
          # Blue-green deployment to production
          ./scripts/deploy-production.sh ${{ github.sha }}

      - name: Health Check
        run: |
          # Verify production deployment health
          ./scripts/production-health-check.sh

      - name: Rollback on Failure
        if: failure()
        run: |
          # Automatic rollback on deployment failure
          ./scripts/rollback-production.sh
```

---

## 🧪 **TESTING PIPELINE**

### **Comprehensive Test Suite Configuration**

```yaml
# docker-compose.test.yml - Test environment
version: '3.8'

services:
  postgres-test:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ma_platform_test
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_password
    ports:
      - '5433:5432'
    tmpfs:
      - /var/lib/postgresql/data # Use tmpfs for faster tests

  redis-test:
    image: redis:7-alpine
    ports:
      - '6380:6379'
    tmpfs:
      - /data

  test-runner:
    build:
      context: .
      dockerfile: Dockerfile.test
    environment:
      DATABASE_URL: postgresql://test_user:test_password@postgres-test:5432/ma_platform_test
      REDIS_URL: redis://redis-test:6379
      ENV: test
    depends_on:
      - postgres-test
      - redis-test
    volumes:
      - .:/app
      - test_coverage:/app/coverage
    command: pytest tests/ -v --cov=app --cov-report=html --cov-report=xml

volumes:
  test_coverage:
```

### **Parallel Test Execution**

```python
# tests/conftest.py - Optimized test configuration
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import pytest_asyncio

# Configure pytest for async tests
pytest_asyncio.asyncio_mode = "auto"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db_engine():
    """Create test database engine"""
    engine = create_async_engine(
        "postgresql+asyncpg://test_user:test_password@localhost:5433/ma_platform_test",
        echo=False,
        pool_size=20,  # Higher pool for parallel tests
        max_overflow=0
    )
    yield engine
    await engine.dispose()

@pytest.fixture(scope="function")
async def db_session(test_db_engine):
    """Create isolated database session per test"""
    async_session = sessionmaker(
        test_db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Start transaction
        trans = await session.begin()
        yield session
        # Rollback transaction to isolate tests
        await trans.rollback()

@pytest.fixture(scope="function")
async def test_client(db_session):
    """Create test client with database session"""
    from app.main import app
    from app.database import get_db_session

    app.dependency_overrides[get_db_session] = lambda: db_session

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()

# Parallel test configuration
class TestConfig:
    """Test configuration for parallel execution"""

    # Database configuration
    TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5433/ma_platform_test"
    TEST_REDIS_URL = "redis://localhost:6380"

    # Test execution settings
    PARALLEL_WORKERS = 4
    TEST_TIMEOUT = 30

    # Coverage targets
    COVERAGE_THRESHOLD = 80
    COVERAGE_FAIL_UNDER = 75

# Performance test fixtures
@pytest.fixture
def performance_test_config():
    """Configuration for performance tests"""
    return {
        "concurrent_users": 100,
        "test_duration_seconds": 60,
        "ramp_up_time_seconds": 10,
        "acceptable_response_time_ms": 2000,
        "acceptable_error_rate": 0.01
    }
```

---

## 🚀 **DEPLOYMENT SCRIPTS**

### **Blue-Green Deployment Script**

```bash
#!/bin/bash
# scripts/deploy-production.sh

set -e

COMMIT_SHA=$1
RENDER_API_KEY=${RENDER_API_KEY}
RENDER_SERVICE_IDS=(
    "srv-deal-service-prod"
    "srv-financial-service-prod"
    "srv-template-service-prod"
    "srv-document-service-prod"
    "srv-matching-service-prod"
    "srv-frontend-prod"
)

echo "🚀 Starting production deployment for commit: $COMMIT_SHA"

# Function to deploy a single service
deploy_service() {
    local service_id=$1
    local image_tag=$2

    echo "📦 Deploying $service_id with image tag: $image_tag"

    # Trigger deployment via Render API
    curl -X POST \
        -H "Authorization: Bearer $RENDER_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"clearCache\": \"clear\"}" \
        "https://api.render.com/v1/services/$service_id/deploys"

    echo "✅ Deployment triggered for $service_id"
}

# Function to check service health
check_service_health() {
    local service_url=$1
    local max_attempts=30
    local attempt=1

    echo "🔍 Checking health of $service_url"

    while [ $attempt -le $max_attempts ]; do
        if curl -sf "$service_url/health" > /dev/null 2>&1; then
            echo "✅ Service is healthy"
            return 0
        fi

        echo "⏳ Waiting for service to be healthy... (attempt $attempt/$max_attempts)"
        sleep 10
        attempt=$((attempt + 1))
    done

    echo "❌ Service failed health check"
    return 1
}

# Update environment variable with new image tag
update_image_tag() {
    local service_id=$1
    local image_tag=$2

    curl -X PATCH \
        -H "Authorization: Bearer $RENDER_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"envVars\": [{\"key\": \"IMAGE_TAG\", \"value\": \"$image_tag\"}]}" \
        "https://api.render.com/v1/services/$service_id"
}

# Main deployment process
main() {
    echo "🏗️  Starting blue-green deployment process..."

    # Phase 1: Update image tags
    echo "📝 Phase 1: Updating image tags..."
    for service_id in "${RENDER_SERVICE_IDS[@]}"; do
        update_image_tag "$service_id" "$COMMIT_SHA"
    done

    # Phase 2: Deploy services in order
    echo "🚀 Phase 2: Deploying services..."

    # Deploy backend services first
    for service_id in "${RENDER_SERVICE_IDS[@]:0:5}"; do
        deploy_service "$service_id" "$COMMIT_SHA"

        # Wait a bit between service deployments
        sleep 30
    done

    # Wait for backend services to be healthy
    echo "⏳ Waiting for backend services to be healthy..."
    sleep 120

    # Check backend service health
    check_service_health "https://api.ma-platform.com"

    # Deploy frontend last
    deploy_service "${RENDER_SERVICE_IDS[5]}" "$COMMIT_SHA"

    # Phase 3: Final health checks
    echo "🔍 Phase 3: Final health checks..."
    sleep 60

    check_service_health "https://ma-platform.com"
    check_service_health "https://api.ma-platform.com"

    # Phase 4: Run post-deployment tests
    echo "🧪 Phase 4: Post-deployment validation..."
    ./scripts/post-deployment-tests.sh

    echo "🎉 Production deployment completed successfully!"
}

# Error handling
trap 'echo "❌ Deployment failed! Check logs and consider rollback."; exit 1' ERR

# Run deployment
main
```

### **Automated Rollback Script**

```bash
#!/bin/bash
# scripts/rollback-production.sh

set -e

RENDER_API_KEY=${RENDER_API_KEY}
ROLLBACK_COMMIT=${1:-"previous"}

echo "🔄 Starting production rollback..."

# Get previous successful deployment
get_previous_deployment() {
    local service_id=$1

    # Get last successful deployment from Render API
    curl -s -H "Authorization: Bearer $RENDER_API_KEY" \
        "https://api.render.com/v1/services/$service_id/deploys?status=live" \
        | jq -r '.deploys[1].id' 2>/dev/null || echo ""
}

# Rollback single service
rollback_service() {
    local service_id=$1
    local deploy_id=$2

    if [ -z "$deploy_id" ]; then
        echo "❌ No previous deployment found for $service_id"
        return 1
    fi

    echo "🔄 Rolling back $service_id to deployment: $deploy_id"

    # Trigger rollback via Render API
    curl -X POST \
        -H "Authorization: Bearer $RENDER_API_KEY" \
        -H "Content-Type: application/json" \
        "https://api.render.com/v1/services/$service_id/deploys/$deploy_id/rollback"
}

# Main rollback process
main() {
    echo "🚨 Initiating emergency rollback procedure..."

    # Rollback all services
    for service_id in "${RENDER_SERVICE_IDS[@]}"; do
        previous_deploy=$(get_previous_deployment "$service_id")
        rollback_service "$service_id" "$previous_deploy"
    done

    # Wait for rollback to complete
    echo "⏳ Waiting for rollback to complete..."
    sleep 180

    # Verify rollback success
    ./scripts/production-health-check.sh

    echo "✅ Rollback completed successfully!"

    # Notify team of rollback
    ./scripts/notify-rollback.sh "$ROLLBACK_COMMIT"
}

main
```

---

## 📊 **PIPELINE MONITORING**

### **GitHub Actions Dashboard Configuration**

```yaml
# .github/workflows/pipeline-metrics.yml
name: Pipeline Metrics

on:
  workflow_run:
    workflows: ['CI/CD Pipeline']
    types: [completed]

jobs:
  collect-metrics:
    runs-on: ubuntu-latest
    steps:
      - name: Collect Pipeline Metrics
        run: |
          # Collect metrics from completed pipeline run
          WORKFLOW_RUN_ID=${{ github.event.workflow_run.id }}

          # Get pipeline duration
          START_TIME=$(gh api "/repos/${{ github.repository }}/actions/runs/$WORKFLOW_RUN_ID" --jq '.created_at')
          END_TIME=$(gh api "/repos/${{ github.repository }}/actions/runs/$WORKFLOW_RUN_ID" --jq '.updated_at')

          # Calculate duration in seconds
          DURATION=$(( $(date -d "$END_TIME" +%s) - $(date -d "$START_TIME" +%s) ))

          # Send metrics to monitoring system
          curl -X POST https://metrics.ma-platform.com/pipeline \
            -H "Authorization: Bearer ${{ secrets.METRICS_API_KEY }}" \
            -d "{
              \"pipeline_duration\": $DURATION,
              \"commit_sha\": \"${{ github.event.workflow_run.head_sha }}\",
              \"branch\": \"${{ github.event.workflow_run.head_branch }}\",
              \"status\": \"${{ github.event.workflow_run.conclusion }}\",
              \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
            }"

  update-dashboard:
    runs-on: ubuntu-latest
    needs: collect-metrics
    steps:
      - name: Update Pipeline Dashboard
        run: |
          # Update deployment dashboard with latest metrics
          ./scripts/update-pipeline-dashboard.sh
```

### **Pipeline Performance Targets**

```python
# Pipeline SLA Configuration
class PipelineSLA:
    """Service Level Agreements for CI/CD pipeline"""

    # Performance targets
    TOTAL_PIPELINE_TIME_TARGET = 600  # 10 minutes
    UNIT_TEST_TIME_TARGET = 120       # 2 minutes
    INTEGRATION_TEST_TIME_TARGET = 300 # 5 minutes
    DEPLOYMENT_TIME_TARGET = 180      # 3 minutes

    # Quality targets
    BUILD_SUCCESS_RATE_TARGET = 0.95  # 95%
    TEST_COVERAGE_TARGET = 0.80       # 80%
    SECURITY_SCAN_PASS_RATE = 1.0     # 100%

    # Deployment targets
    DEPLOYMENT_SUCCESS_RATE = 0.999   # 99.9%
    ROLLBACK_TIME_TARGET = 300        # 5 minutes
    ZERO_DOWNTIME_REQUIREMENT = True

    # Monitoring thresholds
    ALERT_THRESHOLDS = {
        "pipeline_duration_exceeded": TOTAL_PIPELINE_TIME_TARGET * 1.5,
        "build_failure_rate_high": 0.1,  # 10% failure rate triggers alert
        "deployment_failure": 1,          # Any deployment failure triggers alert
        "test_coverage_low": 0.75         # Below 75% coverage triggers alert
    }
```

This CI/CD pipeline design ensures rapid, reliable deployments with comprehensive quality gates, enabling your team to deploy the world's most irresistible M&A platform with confidence and speed.
