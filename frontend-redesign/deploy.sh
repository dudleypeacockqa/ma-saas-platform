#!/bin/bash

# M&A SaaS Platform - Frontend Redesign Deployment Script
# This script handles the deployment of the redesigned multipage website

set -e

echo "🚀 M&A SaaS Platform - Frontend Redesign Deployment"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    print_error "package.json not found. Please run this script from the frontend-redesign directory."
    exit 1
fi

# Check for required environment variables
check_env_vars() {
    print_status "Checking environment variables..."
    
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating template..."
        cat > .env << EOF
# Clerk Authentication
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your_clerk_publishable_key_here

# API Configuration
VITE_API_URL=http://localhost:8000

# Stripe Configuration (for subscription management)
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key_here
EOF
        print_warning "Please update .env file with your actual keys before deployment."
    fi
    
    print_success "Environment configuration ready"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    if command -v pnpm &> /dev/null; then
        pnpm install
    elif command -v npm &> /dev/null; then
        npm install
    else
        print_error "Neither pnpm nor npm found. Please install Node.js and npm/pnpm."
        exit 1
    fi
    
    print_success "Dependencies installed successfully"
}

# Run linting and formatting
lint_and_format() {
    print_status "Running linting and formatting..."
    
    if command -v pnpm &> /dev/null; then
        pnpm run lint --fix || print_warning "Linting completed with warnings"
    else
        npm run lint --fix || print_warning "Linting completed with warnings"
    fi
    
    print_success "Code formatting completed"
}

# Build the application
build_app() {
    print_status "Building application for production..."
    
    if command -v pnpm &> /dev/null; then
        pnpm run build
    else
        npm run build
    fi
    
    print_success "Application built successfully"
}

# Start development server
start_dev() {
    print_status "Starting development server..."
    
    if command -v pnpm &> /dev/null; then
        pnpm run dev --host
    else
        npm run dev -- --host
    fi
}

# Preview production build
preview_build() {
    print_status "Starting preview server for production build..."
    
    if command -v pnpm &> /dev/null; then
        pnpm run preview --host
    else
        npm run preview -- --host
    fi
}

# Main deployment function
deploy() {
    print_status "Starting deployment process..."
    
    check_env_vars
    install_dependencies
    lint_and_format
    build_app
    
    print_success "🎉 Deployment completed successfully!"
    print_status "Build files are available in the 'dist' directory"
    print_status "You can preview the build by running: ./deploy.sh preview"
}

# Handle command line arguments
case "${1:-deploy}" in
    "dev")
        print_status "Starting development mode..."
        check_env_vars
        install_dependencies
        start_dev
        ;;
    "build")
        print_status "Building application only..."
        check_env_vars
        install_dependencies
        build_app
        ;;
    "preview")
        print_status "Previewing production build..."
        if [ ! -d "dist" ]; then
            print_error "No build found. Run './deploy.sh build' first."
            exit 1
        fi
        preview_build
        ;;
    "install")
        print_status "Installing dependencies only..."
        install_dependencies
        ;;
    "lint")
        print_status "Running linting only..."
        lint_and_format
        ;;
    "deploy"|"")
        deploy
        ;;
    *)
        echo "Usage: $0 {deploy|dev|build|preview|install|lint}"
        echo ""
        echo "Commands:"
        echo "  deploy  - Full deployment (default)"
        echo "  dev     - Start development server"
        echo "  build   - Build for production"
        echo "  preview - Preview production build"
        echo "  install - Install dependencies only"
        echo "  lint    - Run linting and formatting"
        exit 1
        ;;
esac
