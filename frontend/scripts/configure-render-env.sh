#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   export RENDER_API_KEY=your_api_token
#   export RENDER_FRONTEND_SERVICE_ID=srv-xxxxxxxxxxxxxxxxxxxx
#   ./frontend/scripts/configure-render-env.sh
#
# The script upserts the production-ready environment variables
# for the Render static site bound to the master branch.

if [ -z "" ]; then
  echo "RENDER_API_KEY env var must be set" >&2
  exit 1
fi

if [ -z "" ]; then
  echo "RENDER_FRONTEND_SERVICE_ID env var must be set" >&2
  exit 1
fi

read -r -d '' PAYLOAD <<'JSON'
{
  "envVars": [
    {"key": "VITE_API_URL", "value": "https://ma-saas-backend.onrender.com"},
    {"key": "VITE_CLERK_PUBLISHABLE_KEY", "value": "pk_live_Y2xlcmsuMTAwZGF5c2FuZGJleW9uZC5jb20k"},
    {"key": "VITE_STRIPE_PUBLISHABLE_KEY", "value": "pk_live_51QwSgkFVol9SKsekxmCj4lDnvd1T6XZPi9VWuI7eKkxNopxC1N60ypXZzwQdyk64AuAQJMvQxuIJ1VuLeOdbeWQC00mV7ZDNB1"},
    {"key": "VITE_ENVIRONMENT", "value": "production"},
    {"key": "VITE_APP_NAME", "value": "100 Days and Beyond"},
    {"key": "VITE_APP_VERSION", "value": "2.0.0"},
    {"key": "NODE_VERSION", "value": "18"}
  ]
}
JSON

curl -sS -X PUT "https://api.render.com/v1/services//env-vars"   -H "Authorization: Bearer "   -H "Content-Type: application/json"   -d ""
