#!/usr/bin/env python3
"""Automated pull request workflow helper for ma-saas-platform.

This script analyzes the current branch, categorizes file changes, validates
repository conventions, generates a pull request title and body, and can submit
PRs via the GitHub CLI (gh).

Usage examples
--------------
- Analyze the current branch against origin/master (default base):
    python tools/pr_workflow.py analyze

- Analyze against a custom base branch:
    python tools/pr_workflow.py analyze --base release/2025-10-13

- Create a PR (dry run by default, pass --create to execute gh):
    python tools/pr_workflow.py create --create

The script reads optional configuration overrides from .github/pr_workflow_config.json.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_CONFIG = {
    "base_branch": "master",
    "labels": {
        "frontend": ["frontend"],
        "mobile": ["frontend", "mobile"],
        "backend": ["backend"],
        "docs": ["documentation"],
        "infra": ["deploy"],
        "tests": ["testing"],
        "tooling": ["tooling"],
        "data": ["data"],
        "other": ["maintenance"],
    },
    "reviewers": {
        "frontend": ["dudleypeacockqa"],
        "mobile": ["dudleypeacockqa"],
        "backend": ["dudleypeacockqa"],
        "docs": ["dudleypeacockqa"],
        "infra": ["dudleypeacockqa"],
        "tests": ["dudleypeacockqa"],
        "tooling": ["dudleypeacockqa"],
    },
    "branch_prefix_map": {
        "feature": "feat",
        "fix": "fix",
        "hotfix": "fix",
        "docs": "docs",
        "deploy": "deploy",
        "chore": "chore",
        "refactor": "refactor",
        "perf": "perf",
    },
}

CATEGORY_DISPLAY = {
    "frontend": "frontend UI",
    "backend": "backend APIs",
    "mobile": "mobile app",
    "docs": "documentation",
    "infra": "deployment configuration",
    "tests": "test suites",
    "tooling": "developer tooling",
    "data": "data pipelines",
    "other": "auxiliary assets",
}
BUILD_BUCKETS = {"frontend", "backend", "mobile", "tooling"}
MANAGE_BUCKETS = {"tests", "data"}
ALIGN_BUCKETS = {"docs", "other"}
DEPLOY_BUCKETS = {"infra"}

COMMIT_PATTERN = re.compile(
    r"^(feat|fix|docs|style|refactor|test|chore|deploy|perf|build|ci|revert)(" r"\(.*\))?: .+"
)

ENV_PATTERNS = [
    re.compile(r"process\.env\.([A-Z][A-Z0-9_]+)"),
    re.compile(r"os\.environ(?:\.get)?\(\s*['\"]([A-Z][A-Z0-9_]+)['\"]"),
]


@dataclass
class FileChange:
    status: str
    path: str
    orig_path: Optional[str] = None


class WorkflowError(RuntimeError):
    """Raised when the workflow encounters a blocking issue."""


def run_command(
    args: Sequence[str],
    *,
    cwd: Optional[Path] = None,
    check: bool = True,
    capture: bool = True,
) -> subprocess.CompletedProcess:
    """Run a command and return the completed process."""

    result = subprocess.run(
        args,
        cwd=str(cwd or REPO_ROOT),
        check=check,
        capture_output=capture,
        text=True,
    )
    return result


def run_git(args: Sequence[str], *, allow_fail: bool = False) -> str:
    try:
        completed = run_command(["git", *args])
    except subprocess.CalledProcessError as exc:  # pragma: no cover - defensive
        if allow_fail:
            return exc.stdout or ""
        raise WorkflowError(f"git {' '.join(args)} failed: {exc.stderr.strip()}") from exc
    return (completed.stdout or "").strip()


def load_config() -> Dict:
    config_path = REPO_ROOT / ".github" / "pr_workflow_config.json"
    if config_path.exists():
        try:
            loaded = json.loads(config_path.read_text())
            return merge_config(DEFAULT_CONFIG, loaded)
        except json.JSONDecodeError as exc:
            raise WorkflowError(f"Invalid JSON in {config_path}: {exc}") from exc
    return DEFAULT_CONFIG


def merge_config(base: Dict, override: Dict) -> Dict:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            merged[key] = {**base[key], **value}
        else:
            merged[key] = value
    return merged


def ensure_base_branch(base_branch: str) -> str:
    remote_ref = f"origin/{base_branch}"
    fetch_cmd = ["git", "fetch", "origin", base_branch]
    try:
        run_command(fetch_cmd, capture=True)
        if run_git(["rev-parse", "--verify", remote_ref], allow_fail=True):
            return remote_ref
    except WorkflowError:
        pass
    except subprocess.CalledProcessError:
        pass

    if run_git(["rev-parse", "--verify", base_branch], allow_fail=True):
        return base_branch
    raise WorkflowError(
        f"Unable to resolve base branch '{base_branch}'. Fetch origin/{base_branch} first."
    )


def get_current_branch() -> str:
    branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    if branch == "HEAD":
        raise WorkflowError("Detached HEAD detected. Checkout a branch before creating a PR.")
    return branch


def parse_name_status(diff_text: str) -> List[FileChange]:
    changes: List[FileChange] = []
    for raw_line in diff_text.splitlines():
        if not raw_line:
            continue
        parts = raw_line.split("\t")
        status = parts[0]
        if status.startswith("R") or status.startswith("C"):
            if len(parts) >= 3:
                changes.append(FileChange(status=status, path=parts[2], orig_path=parts[1]))
        else:
            if len(parts) >= 2:
                changes.append(FileChange(status=status, path=parts[1]))
    return changes


def detect_changes(base_ref: str) -> List[FileChange]:
    diff_output = run_git(["diff", f"{base_ref}...HEAD", "--name-status"])
    return parse_name_status(diff_output)


def categorize_path(path: str) -> str:
    normalized = path.replace("\\", "/")
    if normalized.startswith("frontend/"):
        return "frontend"
    if normalized.startswith("mobile/"):
        return "mobile"
    if normalized.startswith("backend/"):
        return "backend"
    if normalized.startswith("docs/") or normalized.endswith(".md") or normalized.endswith(".rst"):
        return "docs"
    infra_names = (
        "render.yaml",
        "render.yml",
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        "requirements.txt",
        "requirements-dev.txt",
        "runtime.txt",
        "pnpm-lock.yaml",
        "package.json",
        "package-lock.json",
        "tsconfig.json",
        "eslint.config.js",
        "prettier.config.mjs",
        ".env",
        ".env.example",
        ".env.production",
        "docker-compose.dev.yml",
    )
    if normalized in infra_names or normalized.startswith("infra/") or normalized.startswith("ops/"):
        return "infra"
    if "/tests" in normalized or normalized.startswith("tests/") or normalized.endswith("_test.py"):
        return "tests"
    if normalized.startswith("tools/") or normalized.startswith("scripts/"):
        return "tooling"
    data_dirs = ("data/", "fixtures/", "seed/", "migrations/")
    if any(normalized.startswith(prefix) for prefix in data_dirs):
        return "data"
    return "other"


def group_by_category(changes: Iterable[FileChange]) -> Dict[str, List[FileChange]]:
    grouped: Dict[str, List[FileChange]] = {}
    for change in changes:
        category = categorize_path(change.path)
        grouped.setdefault(category, []).append(change)
    return grouped


def summarize_paths(changes: List[FileChange], limit: int = 5) -> List[str]:
    focus: List[str] = []
    seen: Set[str] = set()
    for change in changes:
        parts = change.path.split("/")
        snippet = "/".join(parts[: min(len(parts), 3)])
        if snippet not in seen:
            seen.add(snippet)
            focus.append(snippet)
        if len(focus) >= limit:
            break
    return focus


def infer_action(changes: Iterable[FileChange]) -> str:
    added = any(change.status.startswith("A") or change.status.startswith("R") for change in changes)
    removed = any(change.status.startswith("D") for change in changes)
    if added and not removed:
        return "Add"
    if removed and not added:
        return "Remove"
    if added and removed:
        return "Revise"
    return "Update"


def infer_pr_title(
    branch: str,
    grouped: Dict[str, List[FileChange]],
    branch_prefix_map: Dict[str, str],
) -> str:
    action = infer_action([item for bucket in grouped.values() for item in bucket])
    branch_slug = branch.replace("_", "-")
    scope = branch_slug
    prefix = "chore"
    if "/" in branch_slug:
        prefix_key, remainder = branch_slug.split("/", 1)
        prefix = branch_prefix_map.get(prefix_key, "chore")
        scope = remainder
    else:
        prefix = branch_prefix_map.get(branch_slug.split("-", 1)[0], "chore")
        scope = branch_slug

    cleaned_scope = " ".join(part.capitalize() for part in scope.split("-"))
    if not cleaned_scope:
        cleaned_scope = "Project"

    return f"{prefix}: {action} {cleaned_scope}"


def build_summary_lines(grouped: Dict[str, List[FileChange]]) -> List[str]:
    lines: List[str] = []
    for category, items in sorted(grouped.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        focus = summarize_paths(items)
        focus_text = ", ".join(focus) if focus else "multiple updates"
        lines.append(f"- **{category}**: {len(items)} files touched · {focus_text}")
    return lines


def collect_env_templates() -> Set[str]:
    templates: Set[str] = set()
    for path in REPO_ROOT.rglob(".env.example"):
        try:
            content = path.read_text().splitlines()
        except OSError:
            continue
        for line in content:
            if not line or line.strip().startswith("#") or "=" not in line:
                continue
            key = line.split("=", 1)[0].strip()
            if key:
                templates.add(key)
    return templates


def extract_env_refs(diff_text: str) -> Set[str]:
    refs: Set[str] = set()
    for line in diff_text.splitlines():
        if not line.startswith("+") or line.startswith("+++"):
            continue
        for pattern in ENV_PATTERNS:
            for match in pattern.findall(line):
                refs.add(match)
    return refs


def validate_env_docs(diff_text: str, template_keys: Set[str]) -> List[str]:
    refs = extract_env_refs(diff_text)
    missing = sorted(ref for ref in refs if ref not in template_keys)
    if not missing:
        return []
    return [
        "Undocumented environment variables detected: "
        + ", ".join(missing)
        + ". Update the appropriate .env.example files."
    ]


def validate_commit_messages(base_ref: str) -> List[str]:
    log_output = run_git(["log", f"{base_ref}..HEAD", "--pretty=%s"], allow_fail=True)
    if not log_output:
        return []
    violations = []
    for line in log_output.splitlines():
        if not COMMIT_PATTERN.match(line.strip()):
            violations.append(line.strip())
    if not violations:
        return []
    return [
        "Commit messages missing conventional format:",
        *[f"  - {entry}" for entry in violations],
    ]


def detect_conflict_status() -> List[str]:
    status_output = run_git(["status", "--porcelain"], allow_fail=True)
    if not status_output:
        return []
    conflicts = []
    for line in status_output.splitlines():
        if line.startswith("UU") or line.startswith("AA") or line.startswith("DD"):
            conflicts.append(line)
    if not conflicts:
        return []
    return ["Merge conflicts detected:"] + [f"  - {entry}" for entry in conflicts]


def collect_test_recommendations(grouped: Dict[str, List[FileChange]]) -> List[str]:
    recommendations: Set[str] = set()
    category_commands = {
        "frontend": ["pnpm lint", "pnpm test"],
        "mobile": ["pnpm lint", "pnpm test"],
        "backend": ["cd backend && pytest"],
        "tests": ["cd backend && pytest", "pnpm test"],
        "infra": ["pnpm build", "Render deployment dry run"],
        "tooling": ["npm run lint --if-present"],
    }
    for category in grouped:
        for command in category_commands.get(category, []):
            recommendations.add(command)
    if not recommendations:
        return ["- [ ] Tests not applicable"]
    sorted_commands = sorted(recommendations)
    return [f"- [ ] `{command}`" for command in sorted_commands]


def collect_deployment_notes(grouped: Dict[str, List[FileChange]]) -> List[str]:
    notes: List[str] = []
    if "infra" in grouped:
        notes.append("- Review Render deployment plan and update docs if needed.")
    if "backend" in grouped:
        notes.append("- Confirm Alembic migrations and production compatibility.")
    if "frontend" in grouped or "mobile" in grouped:
        notes.append("- Coordinate frontend rollout (cache busting, CDN invalidation).")
    if not notes:
        notes.append("- N/A")
    return notes


def describe_categories(categories: Iterable[str]) -> str:
    names = [CATEGORY_DISPLAY.get(cat, cat) for cat in sorted(categories)]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + f" and {names[-1]}"


def strip_bullet(text: str) -> str:
    return text.lstrip('- ').strip()


def extract_commands(test_lines: List[str]) -> List[str]:
    commands: List[str] = []
    for line in test_lines:
        match = re.search(r"`([^`]+)`", line)
        if match:
            commands.append(match.group(1))
    return commands


def build_bmad_lines(
    grouped: Dict[str, List[FileChange]],
    tests: List[str],
    deployment_notes: List[str],
    warnings: List[str],
    reviewers: List[str],
) -> List[str]:
    build_categories = {cat for cat in grouped if cat in BUILD_BUCKETS}
    manage_categories = {cat for cat in grouped if cat in MANAGE_BUCKETS}
    align_categories = {cat for cat in grouped if cat in ALIGN_BUCKETS}

    lines: List[str] = []

    if build_categories:
        focus = describe_categories(build_categories)
        lines.append(f"- **Build**: Implementation updates touch {focus}.")
    else:
        lines.append("- **Build**: No implementation changes detected.")

    manage_fragments: List[str] = []
    if manage_categories:
        manage_fragments.append(f"Governance covers {describe_categories(manage_categories)}.")
    commands = extract_commands([line for line in tests if "Tests not applicable" not in line])
    if commands:
        manage_fragments.append("Run " + ", ".join(commands))
    if any("commit messages" in warning.lower() for warning in warnings):
        manage_fragments.append("Fix Conventional Commit formatting before proceeding")
    if not manage_fragments:
        manage_fragments.append("No QA or governance follow-ups flagged.")
    manage_text = "; ".join(manage_fragments)
    if not manage_text.endswith('.'):
        manage_text += '.'
    lines.append(f"- **Manage**: {manage_text}")

    align_fragments: List[str] = []
    if align_categories:
        align_fragments.append(f"Share updates covering {describe_categories(align_categories)}")
    if reviewers:
        align_fragments.append("Coordinate reviews with " + ", ".join(reviewers))
    if any("merge conflicts" in warning.lower() for warning in warnings):
        align_fragments.append("Resolve outstanding merge conflicts")
    if not align_fragments:
        align_fragments.append("No cross-team alignment required.")
    align_text = "; ".join(align_fragments)
    if not align_text.endswith('.'):
        align_text += '.'
    lines.append(f"- **Align**: {align_text}")

    deploy_fragments: List[str] = []
    actionable_deploy = [strip_bullet(note) for note in deployment_notes if note.strip() != "- N/A"]
    if actionable_deploy:
        deploy_fragments.append("; ".join(actionable_deploy))
    if any("environment" in warning.lower() for warning in warnings):
        deploy_fragments.append("Document new environment variables before shipping")
    if not deploy_fragments:
        deploy_fragments.append("No deployment follow-ups flagged.")
    deploy_text = "; ".join(deploy_fragments)
    if not deploy_text.endswith('.'):
        deploy_text += '.'
    lines.append(f"- **Deploy**: {deploy_text}")

    return lines


def suggested_labels(grouped: Dict[str, List[FileChange]], config: Dict) -> List[str]:
    labels: Set[str] = set()
    label_map: Dict[str, List[str]] = config.get("labels", {})
    for category in grouped:
        for label in label_map.get(category, []):
            labels.add(label)
    if not labels:
        labels.add("maintenance")
    return sorted(labels)


def suggested_reviewers(grouped: Dict[str, List[FileChange]], config: Dict) -> List[str]:
    reviewers: Set[str] = set()
    reviewer_map: Dict[str, List[str]] = config.get("reviewers", {})
    for category in grouped:
        for reviewer in reviewer_map.get(category, []):
            reviewers.add(reviewer)
    return sorted(reviewers)


def analyze_branch(base_branch: str, config: Dict) -> Tuple[
    str,
    Dict[str, List[FileChange]],
    List[str],
    List[str],
    List[str],
    List[str],
    str,
    List[str],
    List[str],
]:
    base_ref = ensure_base_branch(base_branch)
    changes = detect_changes(base_ref)
    grouped = group_by_category(changes)
    summary_lines = build_summary_lines(grouped)
    diff_text = run_git(["diff", f"{base_ref}...HEAD"])
    env_template_keys = collect_env_templates()
    env_warnings = validate_env_docs(diff_text, env_template_keys)
    commit_warnings = validate_commit_messages(base_ref)
    conflict_warnings = detect_conflict_status()
    warnings = env_warnings + commit_warnings + conflict_warnings

    branch = get_current_branch()
    title = infer_pr_title(branch, grouped, config.get("branch_prefix_map", {}))
    labels = suggested_labels(grouped, config)
    reviewers = suggested_reviewers(grouped, config)
    tests = collect_test_recommendations(grouped)
    deployment = collect_deployment_notes(grouped)

    return (
        branch,
        grouped,
        summary_lines,
        tests,
        deployment,
        warnings,
        title,
        labels,
        reviewers,
    )


def build_pr_body(
    summary_lines: List[str],
    tests: List[str],
    deployment_notes: List[str],
    warnings: List[str],
) -> str:
    summary_section = "\n".join(summary_lines) if summary_lines else "- Minor housekeeping"
    tests_section = "\n".join(tests)
    deployment_section = "\n".join(deployment_notes)
    warning_block = ""
    if warnings:
        warning_lines = "\n".join(f"- {line}" for line in warnings)
        warning_block = f"\n\n## Automated Checks\n{warning_lines}"

    body = f"""## Summary
{summary_section}

## Technical Details
- Ensure related services and schemas stay synchronized.
- Add deeper technical notes if reviewers need extra context.

## Testing
{tests_section}

## Deployment Considerations
{deployment_section}

## Screenshots
- Attach updated UI captures if applicable before merging.{warning_block}
"""
    return textwrap.dedent(body).strip() + "\n"


def print_analysis(
    branch: str,
    summary: List[str],
    tests: List[str],
    deployment: List[str],
    warnings: List[str],
    title: str,
    labels: List[str],
    reviewers: List[str],
    body: str,
) -> None:
    print(f"Branch: {branch}")
    print(f"Suggested title: {title}")
    print(f"Suggested labels: {', '.join(labels)}")
    if reviewers:
        print(f"Suggested reviewers: {', '.join(reviewers)}")
    print("\nSummary:")
    for line in summary:
        print(f"  {line}")
    print("\nTesting recommendations:")
    for line in tests:
        print(f"  {line}")
    print("\nDeployment considerations:")
    for line in deployment:
        print(f"  {line}")
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  {warning}")
    print("\nGenerated body:\n")
    print(body)


def create_pull_request(
    base_branch: str,
    title: str,
    body: str,
    labels: List[str],
    reviewers: List[str],
    draft: bool,
) -> None:
    import tempfile

    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tmp:
        tmp.write(body)
        tmp_path = tmp.name

    cmd = ["gh", "pr", "create", "--base", base_branch, "--title", title, "--body-file", tmp_path]
    for label in labels:
        cmd.extend(["--label", label])
    for reviewer in reviewers:
        cmd.extend(["--reviewer", reviewer])
    if draft:
        cmd.append("--draft")

    try:
        run_command(cmd, capture=False)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    number = run_git(["pr", "view", "--json", "number", "--jq", ".number"], allow_fail=True)
    if number:
        print(f"PR #{number} created.")
        checks_cmd = f"gh pr checks {number} --watch"
        print(f"Use '{checks_cmd}' to monitor status checks.")


def main(argv: Optional[Sequence[str]] = None) -> int:
    config = load_config()
    parser = argparse.ArgumentParser(description="Automate PR analysis and creation.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze branch and print suggestions")
    analyze_parser.add_argument("--base", default=config.get("base_branch", "master"), help="Base branch")

    create_parser = subparsers.add_parser("create", help="Generate or create a PR via gh")
    create_parser.add_argument("--base", default=config.get("base_branch", "master"), help="Base branch")
    create_parser.add_argument("--draft", action="store_true", help="Create the PR as a draft")
    create_parser.add_argument("--create", action="store_true", help="Execute gh pr create (omit for dry run)")

    args = parser.parse_args(argv)

    try:
        (
            branch,
            grouped,
            summary_lines,
            tests,
            deployment_notes,
            warnings,
            title,
            labels,
            reviewers,
        ) = analyze_branch(args.base, config)
    except WorkflowError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    body = build_pr_body(summary_lines, tests, deployment_notes, warnings)

    if args.command == "analyze":
        print_analysis(branch, summary_lines, tests, deployment_notes, warnings, title, labels, reviewers, body)
        return 0

    # create command
    print_analysis(branch, summary_lines, tests, deployment_notes, warnings, title, labels, reviewers, body)
    if getattr(args, "create"):
        print("\nCreating PR via GitHub CLI...")
        try:
            create_pull_request(args.base, title, body, labels, reviewers, args.draft)
        except WorkflowError as exc:
            print(f"PR creation failed: {exc}", file=sys.stderr)
            return 1
        except subprocess.CalledProcessError as exc:
            print("GitHub CLI reported an error.", file=sys.stderr)
            if exc.stderr:
                print(exc.stderr, file=sys.stderr)
            return 1
    else:
        print("\nDry run only. Re-run with --create to submit the PR via gh.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
