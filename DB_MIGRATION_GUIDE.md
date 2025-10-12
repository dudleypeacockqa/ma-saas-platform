\_# Database Migration Guide for M&A SaaS Platform

**Date**: October 11, 2025  
**Platform**: "100 Days and Beyond" M&A Ecosystem  
**Issue**: Database Migration Failure

## 1. Overview

This guide provides instructions for running the database migrations for the M&A SaaS platform on Render. The migrations are failing when run from the local sandbox environment because the Render database is not publicly accessible. To resolve this, we will use the Render shell to run the migrations from within the Render network.

## 2. Instructions

1.  **Open a Shell on Render**: Navigate to your `ma-saas-backend` service in the Render dashboard and open a shell.
2.  **Navigate to the Backend Directory**: Once in the shell, navigate to the backend directory:

    ```bash
    cd ma-saas-platform/backend
    ```

3.  **Run the Migrations**: Now, run the following command to execute the database migrations. The necessary environment variables, including the `DATABASE_URL`, are already available in the Render service environment.

    ```bash
    alembic upgrade head
    ```

## 3. Verification

After running the command, you should see output from Alembic indicating that the migrations have been successfully applied. If you encounter any errors, please copy and paste the output so I can assist you further.
\_
