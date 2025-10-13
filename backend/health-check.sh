#!/bin/bash
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
