# BMAD Git Automation Workflow

This guide documents the automated commit-and-push script introduced for the BMAD development environment. The workflow reinforces BMAD's disciplined delivery loop by turning large change sets into scoped commits with reliable branch synchronization.

## Purpose

- Provide a repeatable BMAD-aligned path from review to deployment for local changes.
- Surface scope boundaries automatically (frontend, backend, docs, config, other) so each commit maps to the proper agent or epic.
- Guard against risky pushes by enforcing conflict resolution and remote synchronization before deployment.

## Workflow Overview

1. **Pre-flight checks** - verifies the current branch matches the intended target (`master` by default), confirms the staging area is clean, and blocks execution if merge conflicts are outstanding.
2. **Change categorization** - scans `git status --porcelain` output and groups files into BMAD-aligned buckets (`frontend`, `backend`, `docs`, `config`, `other`). Each bucket tracks whether files are new, deleted, or renamed to inform commit intent.
3. **Commit synthesis** - stages each bucket independently, builds Conventional Commit messages (`feat`, `refactor`, `chore`, `docs`) based on the detected change pattern, and commits in sequence so platform history remains traceable.
4. **Branch validation** - fetches `origin/<branch>` and halts if the local branch is behind, prompting a `git pull --rebase` before continuing.
5. **Push & verification** - pushes to `origin/<branch>` and reports any residual working tree changes so the operator can address them immediately.

## BMAD Alignment

- **Build**: Automated categorization keeps deliverables tied to BMAD epics/modules (frontend UI, backend services, documentation, platform configuration).
- **Manage**: Commit narrative is generated from focus areas, enabling BMAD agents (Analyst, PM, Architect, SM) to trace change intent with minimal manual bookkeeping.
- **Align**: Remote divergence checks prevent unsynchronized deployments, preserving the integrity of BMAD sprint cadences and release gates.
- **Deploy**: The final push step mirrors BMAD's deploy stage while warning about any leftover work, supporting rapid yet safe delivery cycles.

## Usage

```bash
./tools/git-auto-commit-push.sh            # assumes master branch
./tools/git-auto-commit-push.sh feature-xyz
```

### Requirements

- Bash 4.3+ (for nameref support via `declare -n`).
- Git CLI available in `PATH`.
- Run from within the repository with an empty staging area.

### Recommended Practice

1. Review `git status` to ensure the detected categories align with your intention.
2. Optionally run project test suites (`pytest`, `pnpm lint`, `pnpm test`) before invoking the automation to keep BMAD quality gates intact.
3. After the push, follow BMAD release documentation to update any deployment checklists or PR templates.

## File Reference

- Script location: `tools/git-auto-commit-push.sh`
- Documentation: `docs/BMAD_GIT_AUTOMATION_WORKFLOW.md` (this file)

Keep this workflow under version control alongside other BMAD assets so agents and collaborators can rely on a consistent commit-and-push process.
