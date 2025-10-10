#!/bin/bash

# Production Deployment Script
# M&A SaaS Platform

set -e

echo "🚀 Starting production deployment..."

# Check environment
if [ "$RENDER" != "true" ]; then
    echo "⚠️  This script should only run on Render"
    exit 1
fi

# Run database migrations
echo "📊 Running database migrations..."
cd backend
alembic upgrade head

# Create pgvector extension if not exists
echo "🔧 Ensuring pgvector extension..."
python -c "
import asyncio
from app.core.database import engine

async def setup_pgvector():
    async with engine.begin() as conn:
        await conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
        await conn.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')
        print('✅ Extensions created/verified')

asyncio.run(setup_pgvector())
"

# Warm up the cache
echo "🔥 Warming up cache..."
python -c "
import asyncio
from app.services.claude_mcp import ClaudeMCPService
from app.services.embeddings import EmbeddingService

async def warmup():
    # Initialize services to preload models
    claude = ClaudeMCPService()
    embeddings = EmbeddingService()
    print('✅ Services initialized')

asyncio.run(warmup())
"

# Verify critical environment variables
echo "🔒 Verifying environment configuration..."
python -c "
import os
import sys

required_vars = [
    'DATABASE_URL',
    'SECRET_KEY',
    'ANTHROPIC_API_KEY',
    'OPENAI_API_KEY',
    'STRIPE_SECRET_KEY',
    'CLERK_SECRET_KEY'
]

missing = []
for var in required_vars:
    if not os.getenv(var):
        missing.append(var)

if missing:
    print(f'❌ Missing required environment variables: {missing}')
    sys.exit(1)
else:
    print('✅ All required environment variables present')
"

# Create initial Stripe products and prices if needed
echo "💳 Setting up Stripe products..."
python scripts/setup_stripe_products.py

# Health check
echo "🏥 Running health check..."
python -c "
import requests
import time

# Wait for service to be ready
time.sleep(5)

try:
    response = requests.get('http://localhost:10000/health', timeout=10)
    if response.status_code == 200:
        print('✅ Health check passed')
    else:
        print(f'⚠️  Health check returned {response.status_code}')
except Exception as e:
    print(f'⚠️  Health check failed: {e}')
"

echo "✨ Deployment complete!"
echo "📊 Monitoring available at: https://dashboard.render.com"