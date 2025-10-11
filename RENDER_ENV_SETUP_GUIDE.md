_# Render Environment Setup Guide for M&A SaaS Platform

**Date**: October 11, 2025  
**Platform**: "100 Days and Beyond" M&A Ecosystem  
**Issue**: Backend API 502 Bad Gateway Error Resolution  

## 1. Overview

This guide provides instructions for setting up the necessary environment variables for the backend service of the M&A SaaS platform on Render. A 502 Bad Gateway error typically indicates that the application is failing to start or is unresponsive. A common cause for this is missing or misconfigured environment variables.

## 2. Required Environment Variables

The following environment variables must be set in the Render dashboard for the `ma-saas-backend` service. The `render.yaml` file is configured to not sync these secrets, so they must be set manually.

### 2.1. Clerk Authentication

*   `CLERK_SECRET_KEY`: Your Clerk secret key.
*   `CLERK_PUBLISHABLE_KEY`: Your Clerk publishable key.
*   `CLERK_WEBHOOK_SECRET`: Your Clerk webhook secret.

### 2.2. Stripe Payments

*   `STRIPE_SECRET_KEY`: Your Stripe secret key.
*   `STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key.
*   `STRIPE_WEBHOOK_SECRET`: Your Stripe webhook secret for handling events.

### 2.3. Anthropic (Claude) API

*   `ANTHROPIC_API_KEY`: Your Anthropic API key for Claude integration.

### 2.4. Database

*   `DATABASE_URL`: This is automatically provisioned by Render and linked from the PostgreSQL database service (`ma-saas-db`). You should not need to set this manually if the `render.yaml` file is correctly configured.

## 3. How to Set Environment Variables in Render

1.  Navigate to your service in the Render dashboard.
2.  Go to the "Environment" tab.
3.  Under "Secret Files & Environment Variables", click on "Add Environment Variable" or "Add Secret File".
4.  Enter the key and value for each of the environment variables listed above.
5.  For secrets, it is recommended to use the "Secret File" option to avoid exposing them in the Render UI.
6.  After adding or updating the environment variables, you will need to trigger a new deployment for the changes to take effect.

## 4. Verification

Once the environment variables are set and the service is redeployed, you can check the application logs for any startup errors. A successful startup should show log entries indicating that the application is listening on the configured port.

If the 502 error persists after correctly setting all the environment variables, the next step is to investigate the application logs for more specific error messages.
_
