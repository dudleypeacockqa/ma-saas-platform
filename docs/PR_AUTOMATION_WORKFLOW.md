# Automated Pull Request Workflow

This guide documents the `tools/pr_workflow.py` helper used to analyze local
changes, generate consistent pull request metadata, and submit PRs through the
GitHub CLI for the `ma-saas-platform` repository.

## Prerequisites

- Python 3.11 (matches the repository baseline).
- Git installed and authenticated.
- GitHub CLI (`gh`) authenticated with permissions to create PRs.
- The repository checked out with your feature branch up to date with `master`.

## Quick Start

1. Run an analysis for your branch:

   ```bash
   python tools/pr_workflow.py analyze
   ```

   The command summarizes changed files, recommends labels/reviewers, and prints a
   ready-to-use PR body.

2. When ready to open a PR, perform a dry run to confirm the metadata:

   ```bash
   python tools/pr_workflow.py create
   ```

   Review the suggested title, labels, reviewers, and generated body. Resolve any
   warnings (e.g., commit message formatting or missing env vars).

3. Submit the PR via GitHub CLI:
   ```bash
   python tools/pr_workflow.py create --create
   ```
   Add `--draft` to open the PR as a draft. After creation, the script prints the
   PR number and the `gh pr checks` command to monitor status checks.

## What the Script Does

- **Branch analysis**: fetches the base branch (defaults to `origin/master`),
  inspects `git diff`, and categorizes files (frontend, backend, docs, infra,
  tests, tooling, mobile, data, other).
- **Title generation**: infers an action verb from the diff (Add/Update/Remove)
  and pairs it with branch naming conventions to create a conventional PR title.
- **Template assembly**: produces the required sections (Summary, Technical
  Details, Testing, Deployment Considerations, Screenshots) with tailored bullet
  points and command checklists.
- **Policy checks**:
  - Ensures commit messages between the base branch and `HEAD` follow the
    repository's Conventional Commits pattern.
  - Scans diff additions for new environment variable references and confirms
    they appear in `.env.example` files.
  - Flags unresolved merge conflicts reported by `git status`.
- **Label & reviewer assignment**: maps categories to labels and reviewers using
  `.github/pr_workflow_config.json` (overrides defaults when present).
- **Post-creation guidance**: reminds maintainers to watch GitHub checks via
  `gh pr checks <number> --watch`.

## Configuration

The script loads optional overrides from `.github/pr_workflow_config.json`. You
can adjust:

- `base_branch`: default branch to diff against.
- `labels`: mapping of categories to label names.
- `reviewers`: default reviewers per category.
- `branch_prefix_map`: branch prefixes (e.g., `feature/`) mapped to commit/PR
  prefixes (e.g., `feat`).

Example excerpt:

```json
{
  "labels": {
    "frontend": ["frontend", "ui"],
    "backend": ["backend", "api"]
  },
  "reviewers": {
    "frontend": ["dudleypeacockqa"]
  }
}
```

## Recommended Workflow Checklist

- Run `python tools/pr_workflow.py analyze` before staging commits to catch the
  warnings early.
- Address all warnings:
  - Fix non-conforming commit messages (`git commit --amend` or reorder).
  - Document any new env vars in the example files.
  - Resolve merge conflicts before creating the PR.
- After the PR is created, monitor CI/CD checks with:
  ```bash
  gh pr checks <pr-number> --watch
  ```
- Update the PR body with screenshots whenever frontend or mobile files change.

Keeping this workflow in daily use ensures reviewers receive complete context
and that automated checks succeed on the first pass.
