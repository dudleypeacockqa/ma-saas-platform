# Intelligent Merge Conflict Resolution Guide

This guide supports the automation in `backend/scripts/resolve_conflicts.py` and
covers detection, automated playbooks, manual fallbacks, verification, and the
post-resolution workflow for the M&A SaaS platform.

## 1. Detecting Conflicts
- Run `git status --short` to confirm files marked with `UU` (unmerged) status.
- Use the automation: `python backend/scripts/resolve_conflicts.py --dry-run` to
  produce a summary report (`conflict_resolution_report.md`) without altering
  files.
- Inspect conflicted files via `git diff --name-only --diff-filter=U`.

## 2. Automated Resolution Playbooks
The resolver applies targeted strategies:
- `package.json`: merges dependency maps, keeps the newest semantic version and
  unions scripts, overrides, and related maps.
- `requirements.txt`: unions pinned packages, preserving unique entries.
- Frontend components (`*.js`, `*.jsx`, `*.ts`, `*.tsx`): merges import blocks
  and prefers the richer component implementation while keeping shared imports.
- Backend modules (`*.py`): merges imports and selects the implementation that
  diverged most from base; useful for FastAPI routes/services.
- YAML (e.g., `render.yaml`): deep merges when PyYAML is available, otherwise
  flags the file for manual work.

Invoke automated resolution (including staging):
```
python backend/scripts/resolve_conflicts.py
```
Optional flags:
- `--run-tests` to execute `pytest` (backend) and `pnpm test` (frontend).
- `--commit --commit-message "chore: resolve merge conflicts"` to create the
  commit.
- `--push --branch master` to push once satisfied.

## 3. Manual Resolution Guidance
When the report lists `manual` status, follow these steps:
1. Open the file and inspect the conflict markers (`<<<<<<<`, `=======`,
   `>>>>>>>`).
2. Compare `git show :2:path` (ours) and `git show :3:path` (theirs) to
   understand each side.
3. For Render configuration files, keep production-safe defaults (CSP, HSTS,
   locked dependency builds) and ensure new environment variables are captured.
4. For complex React merges (multiple feature additions), reconstruct the final
   component by retaining all hooks, state, and effect blocks from both sides.
5. After manual edits, remove conflict markers, save, and run
   `git add <path>` to mark the file resolved.

## 4. Verification and Testing Checklist
After conflicts are resolved:
- Backend: `cd backend && pytest`
- Frontend: `cd frontend && pnpm lint` and `pnpm test`
- Static build smoke test: `pnpm build`
- Optional API check: `uvicorn app.main:app --reload` and hit `/health`

The automation can execute pytest/pnpm tests with `--run-tests`, but rerun
manually if they fail.

## 5. Commit and Push Workflow
1. Review the generated `conflict_resolution_report.md` for any manual items.
2. Stage resolved files: `git add <paths>` (automation does this unless
   `--no-stage` is used).
3. Commit: `git commit -m "chore: resolve merge conflicts"`
4. Push to the integration branch: `git push origin <branch>`
5. Open/Update the PR on GitHub, including the test outputs and mention of the
   automation.

## Rollback Strategy
- Apply the generated backup patch to revert automated changes:
  - Backup location: `.git/conflict_backups/conflict-backup-<timestamp>.patch`
  - Revert via `git apply -R <patch>`
- Alternatively, run `git restore --source=HEAD -- <paths>` for selective
  rollback.

By following this guide with the automation script, teams can quickly reconcile
feature branches with `master` while preserving sophisticated frontend UI,
backend APIs, and deployment infrastructure.
