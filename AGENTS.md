# Repository Guidelines

## Project Structure & Modules
- `backend/app` hosts FastAPI routers, services, and models; migrations stay under `backend/alembic`, automation in `backend/scripts`.
- Pytest suites live in `backend/tests` (API and models) with shared fixtures in `conftest.py`; place new data builders there.
- `frontend/src` is organized into `features`, `pages`, `components`, and `services`; public assets live in `frontend/public`, and architectural notes belong in `docs/`.

## Build, Test & Development Commands
- Backend: create a venv, `pip install -r requirements.txt`, then run `uvicorn app.main:app --reload --port 8000` for local development.
- Execute `pytest` from `backend/`; the config layers coverage, strict warnings, and writes reports to `coverage_html` and `coverage.xml`.
- Frontend: `pnpm install`, `pnpm dev` (http://localhost:5173), `pnpm build`/`pnpm preview` for releases, `pnpm lint` before commits, `pnpm test` for JSDOM-powered Jest suites, and `pnpm start` to exercise the SSR bundle.

## Coding Style & Naming
- Python targets PEP 8 with four-space indents; keep modules snake_case and suffix coordinating services with `_service.py`.
- Define request and response contracts with Pydantic models in `app/schemas`; FastAPI routers should stay thin and delegate to services.
- Prettier (`prettier.config.mjs`) and ESLint enforce width 100, two-space indents, single quotes, and React Hooks rules; name components in PascalCase (e.g., `Dashboard.tsx`) and hooks in camelCase (e.g., `useMobile.ts`).

## Testing Expectations
- Pytest enforces coverage >= 60% per `pytest.ini`; tag long-running suites with existing markers such as `@pytest.mark.integration` or `@pytest.mark.slow`.
- Keep API and model assertions under `backend/tests/test_api` and `backend/tests/test_models`; share fixtures via `conftest.py` instead of ad hoc setup.
- Frontend specs run with Jest (`pnpm test`) using `src/tests/setupTests.js` for shared mocks; update `frontend/test_validation.cjs` only if you rely on the quick sanity checker.

## Commit & PR Process
- Follow Conventional Commits seen in history (`fix:`, `docs:`, `feat:`); keep subjects imperative and under roughly 72 characters.
- PR descriptions should outline problem, solution, and risk, link related issues or deployment checklists, and paste `pytest`/`pnpm lint`/`pnpm test` output.
- Attach UI screenshots for visual updates and call out configuration deltas (env vars, Render settings) while updating the matching guide in `docs/`.

## Security & Configuration
- Use the provided templates (`backend/.env.example`, `frontend/.env.example`) and never commit populated `.env` files; keep production variants local.
- Align backend CORS origins with the active frontend host (localhost:5173 in development) and keep Clerk and Stripe credentials synchronized across services.
- Target Python 3.11.11 (`runtime.txt`) and pin new dependencies in `requirements.txt` or `pnpm-lock.yaml` to preserve reproducible builds.

