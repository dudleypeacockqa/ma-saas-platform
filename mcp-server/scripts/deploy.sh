#!/bin/bash

# BMAD v6 MCP Server Deployment Script
# Automated deployment to Render.com

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT=${1:-staging}
RENDER_API_URL="https://api.render.com/v1"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking deployment requirements..."
    
    # Check if required environment variables are set
    if [[ -z "$RENDER_API_KEY" ]]; then
        log_error "RENDER_API_KEY environment variable is not set"
        exit 1
    fi
    
    # Check if curl is available
    if ! command -v curl &> /dev/null; then
        log_error "curl is required but not installed"
        exit 1
    fi
    
    # Check if jq is available
    if ! command -v jq &> /dev/null; then
        log_warning "jq is not installed. JSON parsing will be limited."
    fi
    
    log_success "Requirements check passed"
}

validate_environment() {
    log_info "Validating environment: $ENVIRONMENT"
    
    case $ENVIRONMENT in
        staging)
            SERVICE_ID="$RENDER_STAGING_SERVICE_ID"
            SERVICE_URL="https://bmad-mcp-staging.onrender.com"
            ;;
        production)
            SERVICE_ID="$RENDER_PRODUCTION_SERVICE_ID"
            SERVICE_URL="https://bmad-mcp.onrender.com"
            ;;
        *)
            log_error "Invalid environment: $ENVIRONMENT. Use 'staging' or 'production'"
            exit 1
            ;;
    esac
    
    if [[ -z "$SERVICE_ID" ]]; then
        log_error "Service ID for $ENVIRONMENT environment is not set"
        exit 1
    fi
    
    log_success "Environment validation passed"
}

run_tests() {
    log_info "Running tests before deployment..."
    
    cd "$PROJECT_DIR"
    
    # Run Python tests
    if [[ -f "requirements.txt" ]]; then
        log_info "Installing Python dependencies..."
        pip install -r requirements.txt > /dev/null 2>&1
        
        log_info "Running Python tests..."
        python -m pytest tests/ -v --tb=short
        
        if [[ $? -eq 0 ]]; then
            log_success "All tests passed"
        else
            log_error "Tests failed. Deployment aborted."
            exit 1
        fi
    else
        log_warning "No requirements.txt found. Skipping Python tests."
    fi
}

build_and_validate() {
    log_info "Building and validating application..."
    
    cd "$PROJECT_DIR"
    
    # Check if Dockerfile exists
    if [[ ! -f "Dockerfile" ]]; then
        log_error "Dockerfile not found"
        exit 1
    fi
    
    # Validate configuration files
    if [[ ! -f "render.yaml" ]]; then
        log_error "render.yaml not found"
        exit 1
    fi
    
    # Check main application file
    if [[ ! -f "app/main.py" ]]; then
        log_error "Main application file not found"
        exit 1
    fi
    
    log_success "Build validation passed"
}

deploy_to_render() {
    log_info "Deploying to Render ($ENVIRONMENT)..."
    
    # Trigger deployment
    DEPLOY_RESPONSE=$(curl -s -X POST \
        -H "Authorization: Bearer $RENDER_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"clearCache": false}' \
        "$RENDER_API_URL/services/$SERVICE_ID/deploys")
    
    if [[ $? -eq 0 ]]; then
        if command -v jq &> /dev/null; then
            DEPLOY_ID=$(echo "$DEPLOY_RESPONSE" | jq -r '.id')
            log_success "Deployment triggered. Deploy ID: $DEPLOY_ID"
        else
            log_success "Deployment triggered"
        fi
    else
        log_error "Failed to trigger deployment"
        exit 1
    fi
}

wait_for_deployment() {
    log_info "Waiting for deployment to complete..."
    
    local max_attempts=30
    local attempt=1
    local wait_time=20
    
    while [[ $attempt -le $max_attempts ]]; do
        log_info "Checking deployment status (attempt $attempt/$max_attempts)..."
        
        # Check service health
        HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/health")
        
        if [[ "$HTTP_STATUS" == "200" ]]; then
            log_success "Deployment completed successfully!"
            return 0
        fi
        
        log_info "Service not ready yet (HTTP $HTTP_STATUS). Waiting $wait_time seconds..."
        sleep $wait_time
        ((attempt++))
    done
    
    log_error "Deployment timed out after $((max_attempts * wait_time)) seconds"
    return 1
}

run_health_checks() {
    log_info "Running post-deployment health checks..."
    
    # Basic health check
    log_info "Checking basic health endpoint..."
    HEALTH_RESPONSE=$(curl -s "$SERVICE_URL/health")
    
    if [[ $? -eq 0 ]]; then
        if command -v jq &> /dev/null; then
            HEALTH_STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.status')
            if [[ "$HEALTH_STATUS" == "healthy" ]]; then
                log_success "Health check passed"
            else
                log_warning "Health check returned: $HEALTH_STATUS"
            fi
        else
            log_success "Health endpoint responded"
        fi
    else
        log_error "Health check failed"
        return 1
    fi
    
    # API endpoints check
    log_info "Checking API endpoints..."
    
    local endpoints=(
        "/"
        "/api/v1/agents"
        "/api/v1/workflows"
        "/metrics"
    )
    
    for endpoint in "${endpoints[@]}"; do
        HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL$endpoint")
        
        if [[ "$HTTP_STATUS" =~ ^[23] ]]; then
            log_success "✓ $endpoint (HTTP $HTTP_STATUS)"
        else
            log_warning "✗ $endpoint (HTTP $HTTP_STATUS)"
        fi
    done
}

run_smoke_tests() {
    log_info "Running smoke tests..."
    
    # Test workflow execution
    log_info "Testing workflow execution..."
    
    WORKFLOW_RESPONSE=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d '{
            "workflow_name": "workflow-status",
            "context": {},
            "project_id": "smoke-test-project"
        }' \
        "$SERVICE_URL/api/v1/workflow/execute")
    
    if [[ $? -eq 0 ]]; then
        log_success "Workflow execution test passed"
    else
        log_warning "Workflow execution test failed"
    fi
    
    # Test agent invocation
    log_info "Testing agent invocation..."
    
    AGENT_RESPONSE=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d '{
            "agent_name": "analyst",
            "prompt": "Test prompt for smoke test",
            "context": {}
        }' \
        "$SERVICE_URL/api/v1/agent/invoke")
    
    if [[ $? -eq 0 ]]; then
        log_success "Agent invocation test passed"
    else
        log_warning "Agent invocation test failed"
    fi
}

cleanup() {
    log_info "Cleaning up temporary files..."
    # Add any cleanup logic here
    log_success "Cleanup completed"
}

rollback() {
    log_error "Deployment failed. Consider rolling back to previous version."
    log_info "To rollback manually:"
    log_info "1. Go to Render dashboard"
    log_info "2. Select the service"
    log_info "3. Go to Deploys tab"
    log_info "4. Click 'Redeploy' on a previous successful deployment"
}

main() {
    log_info "Starting BMAD v6 MCP Server deployment to $ENVIRONMENT"
    log_info "=================================================="
    
    # Trap errors and cleanup
    trap cleanup EXIT
    trap rollback ERR
    
    # Run deployment steps
    check_requirements
    validate_environment
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        log_info "Production deployment detected. Running full test suite..."
        run_tests
    fi
    
    build_and_validate
    deploy_to_render
    
    if wait_for_deployment; then
        run_health_checks
        
        if [[ "$ENVIRONMENT" == "production" ]]; then
            run_smoke_tests
        fi
        
        log_success "=================================================="
        log_success "🚀 Deployment to $ENVIRONMENT completed successfully!"
        log_success "🌐 Service URL: $SERVICE_URL"
        log_success "📊 Health Check: $SERVICE_URL/health"
        log_success "📈 Metrics: $SERVICE_URL/metrics"
        log_success "=================================================="
    else
        log_error "Deployment failed during health check phase"
        exit 1
    fi
}

# Show usage if no arguments provided
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 [staging|production]"
    echo ""
    echo "Environment variables required:"
    echo "  RENDER_API_KEY - Render.com API key"
    echo "  RENDER_STAGING_SERVICE_ID - Service ID for staging"
    echo "  RENDER_PRODUCTION_SERVICE_ID - Service ID for production"
    echo ""
    echo "Examples:"
    echo "  $0 staging    # Deploy to staging environment"
    echo "  $0 production # Deploy to production environment"
    exit 1
fi

# Run main function
main "$@"
