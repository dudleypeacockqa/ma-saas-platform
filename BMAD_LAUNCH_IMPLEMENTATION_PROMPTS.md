## M&A SaaS Platform: BMAD-Method Launch Implementation Prompts for Claude Code CLI

**Objective:** To systematically resolve all outstanding deployment and configuration issues, ensuring the M&A SaaS platform is robust, secure, and ready for a successful business launch and immediate revenue generation. These prompts are designed to be executed in the Claude Code CLI within your Cursor environment.

---

### **Prompt 1: Systematic Environment & Dependency Resolution**

**Objective:** To achieve a stable and reproducible build environment by resolving all dependency and configuration errors identified in the initial test run. This is the foundational step for all subsequent launch activities.

**BMAD Context:** This action directly addresses the critical blockers identified in the *Business Launch Readiness Report*. By applying the BMAD principle of **Systematic Resolution**, we are eliminating the root causes of deployment failure, ensuring we meet the **Quality Gate** for a stable build before proceeding. This aligns with the strategic objective of a reliable and professional platform launch.

**Claude Code CLI Prompt:**

```
/bmad:mmm:agents:dev

**Objective:** Resolve Critical Environment & Dependency Failures for M&A SaaS Platform Launch.

**Context:** The initial deployment test (`./deploy.sh test`) failed due to two primary root causes:
1.  A `ModuleNotFoundError` for `aiohttp` during backend test collection.
2.  An `Invalid requirement` error for `aiohttp==` in `requirements.txt` due to a missing version specifier.
3.  Persistent `sqlalchemy.exc.ArgumentError` and `ValueError` related to missing `DATABASE_URL` and `STORAGE_PROVIDER` configurations during testing, indicating the test environment is not loading environment variables correctly.

**Systematic Resolution Steps:**

1.  **Analyze `requirements.txt`:** Open `ma-saas-platform/backend/requirements.txt`. Find the line `aiohttp==` and correct it by adding a compatible version. A safe, recent version like `aiohttp==3.9.5` should be used. Ensure there are no other syntax errors in the file.

2.  **Analyze Test Environment Configuration:** The test failures indicate that `pytest` is not loading the necessary environment variables from the `.env.example` file. The backend tests require a valid `DATABASE_URL` and the full set of `STORAGE_PROVIDER` variables to initialize the application context. Modify the backend testing process to ensure these variables are loaded before tests are run. A common solution is to use a pytest plugin like `pytest-dotenv` or to modify the test setup to load the `.env.example` file.

3.  **Update `deploy.sh` for Robust Testing:** Modify the `test_backend` function in `ma-saas-platform/deploy.sh`. Before the `python -m pytest -v` command, add steps to:
    a. Copy `ma-saas-platform/backend/.env.example` to `ma-saas-platform/backend/.env` if it doesn't exist.
    b. Ensure the test runner uses this `.env` file. You might need to install and use `pytest-dotenv` which automatically loads `.env` files.

4.  **Execute and Verify:** Run the `setup_python_env` and `test_backend` functions from the `deploy.sh` script to confirm that all dependencies are correctly installed and all backend tests now pass without configuration or import errors.

**Quality Gate:** All backend tests must pass successfully. The output should show `============================= no tests ran in X.XXs =============================` or a successful run of all collected tests, with no `ERROR` or `FAIL` summaries.
```

---

### **Prompt 2: Comprehensive QA & Test Suite Hardening**

**Objective:** To implement a comprehensive Quality Assurance (QA) process by creating and passing a full suite of unit, integration, and end-to-end tests. This ensures all business-critical functionalities are working as expected before launch.

**BMAD Context:** This prompt embodies the BMAD principle of **Quality Gate Validation**. By building and verifying a complete test suite, we are de-risking the launch and ensuring the platform meets the enterprise-grade standards required for customer acquisition. This directly supports the strategic objective of delivering a high-quality, reliable service to generate revenue.

**Claude Code CLI Prompt:**

```
/bmad:mmm:agents:dev

**Objective:** Implement and Pass a Comprehensive QA Test Suite for the M&A SaaS Platform.

**Context:** With the environment stabilized, we now need to ensure the functional completeness and correctness of the application. The current test suite is basic and was created by the deployment script. We need to build it out to cover all critical business workflows.

**Systematic Implementation Steps:**

1.  **Analyze API Structure:** Review all API routers in `ma-saas-platform/backend/app/api/` (master_admin, subscription_management, content_creation, etc.).

2.  **Develop Backend Integration Tests:** Create new test files in `ma-saas-platform/backend/tests/` for each major feature. The tests should use the `TestClient` from FastAPI to make requests to the API endpoints and assert the expected responses. Cover the following scenarios:
    *   **Authentication:** Test that protected endpoints return 401/403 errors for unauthenticated users.
    *   **Master Admin:** Test creation, retrieval, and updating of core business data.
    *   **Subscriptions:** Test the creation of a subscription checkout session and the handling of Stripe webhooks (mocking the Stripe API).
    *   **Content Creation:** Test uploading a media file and creating a content project.
    *   **Events & Leads:** Test the creation of events and leads.

3.  **Develop Frontend Unit Tests:** Review the components in `ma-saas-platform/frontend/src/pages/`. Create new test files in `ma-saas-platform/frontend/src/` for each main page component. Use `@testing-library/react` to:
    *   Render each component.
    *   Assert that key UI elements are present.
    *   Simulate user interactions (e.g., clicking buttons, filling forms) and assert the expected outcome.

4.  **Execute Full Test Suite:** Modify the `deploy.sh` script's `test` command to run both `test_backend` and `test_frontend` functions sequentially.

5.  **Execute and Verify:** Run `./deploy.sh test` and ensure all newly created tests pass for both the backend and frontend.

**Quality Gate:** 100% pass rate for all unit and integration tests. The test coverage report should show a significant increase in code coverage for both the backend and frontend applications.
```

---

### **Prompt 3: Production Readiness & Final Deployment**

**Objective:** To configure the platform for a production environment, perform a final end-to-end deployment, and verify its operational status, making it ready for live customer traffic.

**BMAD Context:** This is the final **Strategic Validation** phase before launch. We are confirming that all systematically resolved issues and quality-gated features translate into a fully operational, revenue-ready platform. This action directly aligns with the primary business objective of launching the M&A SaaS platform to start acquiring clients.

**Claude Code CLI Prompt:**

```
/bmad:mmm:agents:dev

**Objective:** Finalize Production Configuration and Execute Live Deployment of the M&A SaaS Platform.

**Context:** The platform has passed all local tests and is now ready for the final push to a production environment. This involves finalizing the deployment script, configuring production environment variables, and running a live deployment.

**Systematic Implementation Steps:**

1.  **Finalize Deployment Script:** Open `ma-saas-platform/deploy.sh`. Create a new `deploy_production` function. This function should:
    a. Run all checks and tests (`check_requirements`, `test_backend`, `test_frontend`).
    b. Build the frontend for production (`build_frontend`).
    c. Include commands to push the code to a production hosting service (e.g., Render, Vercel). Since we are using Render, this would involve using the Render CLI or a Git-based deployment trigger. For now, simulate this by printing the steps.
    d. Add a final verification step that curls the live production URL to confirm the deployment was successful.

2.  **Create Production Environment Files:**
    a. Create `ma-saas-platform/backend/.env.production` with placeholder values for the real production database, Stripe, Clerk, and other services.
    b. Create `ma-saas-platform/frontend/.env.production` with the production `VITE_API_URL` and `VITE_CLERK_PUBLISHABLE_KEY`.

3.  **Update Application Code for Production:**
    a. In `ma-saas-platform/backend/app/core/config.py`, ensure that settings are loaded from `.env.production` when `ENVIRONMENT=production`.
    b. In `ma-saas-platform/frontend/src/App_complete.js`, ensure the Clerk `publishableKey` is loaded from the environment variable.

4.  **Execute Final Verification:** Run the new `deploy_production` function from the `deploy.sh` script. While it won't perform a real cloud deployment, it will execute all steps and checks in the correct order.

5.  **Generate Operational Documentation:** Create a `LAUNCH_OPERATIONS_GUIDE.md` file. Document the final steps required to go live:
    *   How to populate the production environment variables on the hosting provider (e.g., Render).
    *   The command to trigger the final deployment.
    *   How to monitor the application logs.
    *   A rollback plan in case of failure.

**Quality Gate:** The `deploy_production` script runs to completion without errors. The `LAUNCH_OPERATIONS_GUIDE.md` is comprehensive and provides a clear, actionable path for the final launch.
```

