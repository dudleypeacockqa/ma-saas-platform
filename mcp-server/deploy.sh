#!/bin/bash

# BMAD v6 MCP Server Deployment Script
# Deploys the MCP server to Render.com

set -e

echo "🚀 Starting BMAD v6 MCP Server deployment..."

# Check if we're in the correct directory
if [ ! -f "render.yaml" ]; then
    echo "❌ Error: render.yaml not found. Please run this script from the mcp-server directory."
    exit 1
fi

# Check if Render CLI is installed
if ! command -v render &> /dev/null; then
    echo "❌ Error: Render CLI not found. Please install it first:"
    echo "   npm install -g @render/cli"
    exit 1
fi

# Check if user is logged in to Render
if ! render auth whoami &> /dev/null; then
    echo "❌ Error: Not logged in to Render. Please run 'render auth login' first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Validate Python dependencies
echo "🔍 Validating Python dependencies..."
python3 -m pip install --dry-run -r requirements.txt > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Dependencies validation passed"
else
    echo "❌ Error: Dependencies validation failed"
    exit 1
fi

# Test the application locally (optional)
echo "🧪 Running quick local test..."
python3 -c "
import sys
sys.path.append('.')
try:
    from app.main import app
    print('✅ Application imports successfully')
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

# Deploy to Render
echo "🚀 Deploying to Render..."
render deploy

if [ $? -eq 0 ]; then
    echo "✅ Deployment initiated successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Monitor deployment progress in the Render dashboard"
    echo "2. Set up environment variables for API keys"
    echo "3. Test the deployed MCP server endpoints"
    echo "4. Update your M&A SaaS platform to use the new MCP server URL"
    echo ""
    echo "🔗 Useful commands:"
    echo "   render services list                 # List your services"
    echo "   render logs -s bmad-v6-mcp-server   # View logs"
    echo "   render shell -s bmad-v6-mcp-server  # Access shell"
else
    echo "❌ Deployment failed. Check the error messages above."
    exit 1
fi

echo "🎉 BMAD v6 MCP Server deployment script completed!"
