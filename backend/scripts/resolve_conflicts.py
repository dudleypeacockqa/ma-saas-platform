#!/usr/bin/env python3
"""Automated merge conflict resolver for the M&A SaaS platform.

This script detects merge conflicts, applies opinionated resolution
strategies for the most common problem files, and produces a resolution
report. It is designed to be run from the repository root (the script
lives in backend/scripts/resolve_conflicts.py).

Capabilities
-----------
* Creates a backup patch before making changes (unless --no-backup).
* Detects conflicted files via `git ls-files -u`.
* Applies specialised resolvers for:
  - package.json style dependency merges
  - Python requirements.txt consolidation
  - React/TypeScript component files (import union + body preference)
  - FastAPI/Backend Python modules (simple heuristic merge)
  - render.yaml (if PyYAML is available, otherwise falls back to manual)
* Provides manual guidance for conflicts it cannot safely resolve.
* Optionally stages files, runs project test suites, and commits/pushes.

Usage examples
--------------
    # Dry run to inspect what would be resolved
    python backend/scripts/resolve_conflicts.py --dry-run

    # Resolve, stage, run tests, and commit
    python backend/scripts/resolve_conflicts.py --run-tests \
        --commit --commit-message "chore: resolve merge conflicts"

    # Resolve and push to origin/master once satisfied
    python backend/scripts/resolve_conflicts.py --commit --push
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class ConflictEntry:
    path: Path
    stages: Dict[int, str]


@dataclass
class Resolution:
    path: Path
    status: str  # resolved | skipped | manual
    message: str


class CommandError(RuntimeError):
    pass


def run_git(args: Sequence[str], *, capture: bool = True, check: bool = True) -> str:
    """Execute a git command in the repository root."""
    process = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=capture,
    )
    if check and process.returncode != 0:
        raise CommandError(process.stderr.strip() or process.stdout.strip())
    if capture:
        return process.stdout
    return ""


def create_backup_patch() -> Path:
    backup_dir = REPO_ROOT / ".git" / "conflict_backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = _dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    patch_path = backup_dir / f"conflict-backup-{timestamp}.patch"
    diff = run_git(["diff"], capture=True)
    with patch_path.open("w", encoding="utf-8") as fh:
        fh.write(diff)
    return patch_path


def detect_conflicts() -> List[ConflictEntry]:
    output = run_git(["ls-files", "-u"])
    if not output.strip():
        return []
    entries: Dict[str, Dict[int, str]] = {}
    for line in output.strip().splitlines():
        metadata, path = line.split("\t", 1)
        _mode, sha, stage_str = metadata.split()
        stage = int(stage_str)
        stages = entries.setdefault(path, {})
        blob = run_git(["show", f":{stage}:{path}"], capture=True)
        stages[stage] = blob
    return [ConflictEntry(Path(path), stages) for path, stages in entries.items()]


def normalise_dependency_version(raw: str) -> Tuple[str, Tuple[int, ...], str]:
    prefix = ""
    index = 0
    while index < len(raw) and raw[index] in "^~><=!*":
        prefix += raw[index]
        index += 1
    core = raw[index:]
    numeric_parts: List[int] = []
    for token in re.split(r"[._-]", core):
        if token.isdigit():
            numeric_parts.append(int(token))
        else:
            break
    suffix = core[len(".".join(str(p) for p in numeric_parts)) :]
    return prefix, tuple(numeric_parts), suffix


def choose_newer_version(a: str, b: str) -> str:
    if a == b:
        return a
    prefix_a, nums_a, suffix_a = normalise_dependency_version(a)
    prefix_b, nums_b, suffix_b = normalise_dependency_version(b)
    if nums_a == nums_b:
        # Prefer value with explicit prefix (caret/tilde) if one exists
        if prefix_b and not prefix_a:
            return b
        if prefix_a and not prefix_b:
            return a
        # Fall back to lexicographic comparison of suffix
        return a if suffix_a >= suffix_b else b
    if nums_a > nums_b:
        return a
    return b


def merge_dependency_maps(*maps: Dict[str, str]) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for mapping in maps:
        for dep, version in mapping.items():
            if dep in result:
                result[dep] = choose_newer_version(result[dep], version)
            else:
                result[dep] = version
    return dict(sorted(result.items()))


def json_loader(raw: str) -> Optional[Dict[str, object]]:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def resolve_package_json(entry: ConflictEntry) -> Resolution:
    base = json_loader(entry.stages.get(1, ""))
    ours = json_loader(entry.stages.get(2, ""))
    theirs = json_loader(entry.stages.get(3, ""))
    if ours is None or theirs is None:
        return Resolution(entry.path, "manual", "Unable to parse JSON for package.json")
    result = {}
    # start with base structure to preserve ordering where possible
    if base:
        result.update(base)
    for candidate in (ours, theirs):
        for key, value in candidate.items():
            if key in {
                "dependencies",
                "devDependencies",
                "peerDependencies",
                "optionalDependencies",
                "overrides",
                "resolutions",
            }:
                merged = merge_dependency_maps(
                    result.get(key, {}),
                    base.get(key, {}) if base else {},
                    ours.get(key, {}),
                    theirs.get(key, {}),
                )
                result[key] = merged
            elif key == "scripts":
                merged_scripts = {}
                if isinstance(result.get(key), dict):
                    merged_scripts.update(result[key])
                if isinstance(ours.get(key), dict):
                    merged_scripts.update(ours[key])
                if isinstance(theirs.get(key), dict):
                    merged_scripts.update(theirs[key])
                result[key] = merged_scripts
            else:
                result[key] = candidate[key]
    payload = json.dumps(result, indent=2, sort_keys=True)
    payload += "\n"
    return Resolution(entry.path, "resolved", payload)


def parse_requirements(raw: str) -> List[str]:
    lines = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append(stripped)
    return lines


def resolve_requirements(entry: ConflictEntry) -> Resolution:
    base_lines = parse_requirements(entry.stages.get(1, ""))
    ours_lines = parse_requirements(entry.stages.get(2, ""))
    theirs_lines = parse_requirements(entry.stages.get(3, ""))
    merged = sorted(set(base_lines) | set(ours_lines) | set(theirs_lines))
    content = "\n".join(merged) + "\n"
    return Resolution(entry.path, "resolved", content)


def union_imports(blocks: Iterable[str]) -> List[str]:
    seen: Dict[str, None] = {}
    order: List[str] = []
    for block in blocks:
        for line in block.splitlines():
            if line.strip().startswith("import") or line.strip().startswith("from"):
                if line not in seen:
                    seen[line] = None
                    order.append(line)
    return order


def strip_imports(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if line.strip().startswith("import") or line.strip().startswith("from"):
            continue
        lines.append(line)
    return "\n".join(lines).strip("\n")


def resolve_component(entry: ConflictEntry) -> Resolution:
    base = entry.stages.get(1, "")
    ours = entry.stages.get(2, "")
    theirs = entry.stages.get(3, "")
    if not ours or not theirs:
        return Resolution(entry.path, "manual", "Missing component bodies")
    if ours == theirs:
        return Resolution(entry.path, "resolved", ours)
    imports = union_imports([base, ours, theirs])
    ours_body = strip_imports(ours)
    theirs_body = strip_imports(theirs)
    # Prefer the side with richer JSX/TSX content (more components + hooks)
    preferred_body = theirs_body if len(theirs_body) >= len(ours_body) else ours_body
    combined = "\n".join(imports)
    if combined:
        combined += "\n\n"
    combined += preferred_body.strip() + "\n"
    return Resolution(entry.path, "resolved", combined)


def resolve_python_module(entry: ConflictEntry) -> Resolution:
    base = entry.stages.get(1, "")
    ours = entry.stages.get(2, "")
    theirs = entry.stages.get(3, "")
    if ours == theirs:
        return Resolution(entry.path, "resolved", ours)
    if base == ours:
        return Resolution(entry.path, "resolved", theirs)
    if base == theirs:
        return Resolution(entry.path, "resolved", ours)
    # Merge imports similarly to the component logic
    imports = union_imports([base, ours, theirs])
    ours_body = strip_imports(ours)
    theirs_body = strip_imports(theirs)
    # Prefer the longer body assuming it incorporates new logic
    preferred_body = theirs_body if len(theirs_body) >= len(ours_body) else ours_body
    combined = "\n".join(imports)
    if combined:
        combined += "\n\n"
    combined += preferred_body.strip() + "\n"
    return Resolution(entry.path, "resolved", combined)


def has_yaml_support() -> bool:
    try:
        import yaml  # type: ignore
    except Exception:
        return False
    return True


def resolve_yaml(entry: ConflictEntry) -> Resolution:
    if not has_yaml_support():
        return Resolution(entry.path, "manual", "PyYAML not available; manual merge required")
    import yaml  # type: ignore

    def load(raw: str) -> Optional[Dict[str, object]]:
        if not raw.strip():
            return None
        return yaml.safe_load(raw)

    base = load(entry.stages.get(1, "")) or {}
    ours = load(entry.stages.get(2, "")) or {}
    theirs = load(entry.stages.get(3, "")) or {}

    def deep_merge(dst: Dict[str, object], src: Dict[str, object]) -> Dict[str, object]:
        for key, value in src.items():
            if (
                key in dst
                and isinstance(dst[key], dict)
                and isinstance(value, dict)
            ):
                dst[key] = deep_merge(dict(dst[key]), value)
            else:
                dst[key] = value
        return dst

    merged = deep_merge(deep_merge(dict(base), ours), theirs)
    dumped = yaml.safe_dump(merged, sort_keys=False)
    return Resolution(entry.path, "resolved", dumped)


class ConflictManager:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.report: List[Resolution] = []

    def resolve(self) -> int:
        if not self.args.no_backup:
            backup = create_backup_patch()
            print(f"Created backup patch at {backup.relative_to(REPO_ROOT)}")
        conflicts = detect_conflicts()
        if not conflicts:
            print("No merge conflicts detected.")
            return 0
        print(f"Detected {len(conflicts)} conflicted file(s).")
        for entry in conflicts:
            resolution = self._dispatch(entry)
            self.report.append(resolution)
            if resolution.status == "resolved" and not self.args.dry_run:
                path = REPO_ROOT / entry.path
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("w", encoding="utf-8") as fh:
                    fh.write(resolution.message)
                if not self.args.no_stage:
                    run_git(["add", str(entry.path)], capture=True)
                print(f"✔ Resolved {entry.path}")
            elif resolution.status == "manual":
                print(f"⚠ Manual intervention required for {entry.path}: {resolution.message}")
            else:
                print(f"⏭ Skipped {entry.path}: {resolution.message}")
        self._write_report()
        if self.args.run_tests and not self.args.dry_run:
            self._run_tests()
        if self.args.commit and not self.args.dry_run:
            self._commit_changes()
        if self.args.push and not self.args.dry_run:
            self._push_changes()
        unresolved = [r for r in self.report if r.status != "resolved"]
        return 0 if not unresolved else 1

    def _dispatch(self, entry: ConflictEntry) -> Resolution:
        path = entry.path
        if path.name == "package.json":
            return resolve_package_json(entry)
        if path.name == "requirements.txt":
            return resolve_requirements(entry)
        if path.suffix in {".js", ".jsx", ".ts", ".tsx"}:
            return resolve_component(entry)
        if path.suffix == ".py":
            return resolve_python_module(entry)
        if path.suffix in {".yaml", ".yml"}:
            return resolve_yaml(entry)
        return Resolution(path, "manual", "No resolver available for this file type")

    def _write_report(self) -> None:
        timestamp = _dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
        lines = [
            "# Merge Conflict Resolution Report",
            "",
            f"Generated at {timestamp} UTC",
            "",
            "## Summary",
            "",
        ]
        resolved = [r for r in self.report if r.status == "resolved"]
        manual = [r for r in self.report if r.status == "manual"]
        skipped = [r for r in self.report if r.status == "skipped"]
        lines.append(f"- Resolved automatically: {len(resolved)}")
        lines.append(f"- Needs manual review: {len(manual)}")
        lines.append(f"- Skipped: {len(skipped)}")
        lines.append("")
        lines.append("## File Details")
        lines.append("")
        for item in self.report:
            lines.append(f"- **{item.path}** — {item.status}: {item.message if item.status != 'resolved' else 'resolved via automation'}")
        report_path = REPO_ROOT / self.args.report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Report written to {report_path.relative_to(REPO_ROOT)}")

    def _run_tests(self) -> None:
        print("Running verification commands...")
        commands = [
            ("pytest", ["pytest"], REPO_ROOT / "backend"),
            ("pnpm test", ["pnpm", "test"], REPO_ROOT / "frontend"),
        ]
        for label, cmd, cwd in commands:
            try:
                print(f"→ {label}")
                subprocess.run(cmd, cwd=cwd, check=True)
            except FileNotFoundError:
                print(f"  ! Skipped {label} (command not found)")
            except subprocess.CalledProcessError:
                print(f"  ! {label} failed; check output above")

    def _commit_changes(self) -> None:
        status = run_git(["status", "--porcelain"])
        if not status.strip():
            print("No staged changes to commit.")
            return
        message = self.args.commit_message or "chore: resolve merge conflicts"
        run_git(["commit", "-m", message], capture=True)
        print(f"Committed with message: {message}")

    def _push_changes(self) -> None:
        remote = self.args.remote
        branch = self.args.branch
        run_git(["push", remote, branch], capture=True)
        print(f"Pushed to {remote}/{branch}")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Automate merge conflict resolution across common file types.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Analyse conflicts without writing changes")
    parser.add_argument("--no-backup", action="store_true", help="Skip creation of a pre-resolution patch backup")
    parser.add_argument("--no-stage", action="store_true", help="Do not stage files after automatic resolution")
    parser.add_argument("--run-tests", action="store_true", help="Execute pytest and pnpm test after resolving")
    parser.add_argument("--commit", action="store_true", help="Create a commit after successful resolution")
    parser.add_argument("--commit-message", help="Custom commit message to use with --commit")
    parser.add_argument("--push", action="store_true", help="Push the branch after committing")
    parser.add_argument("--remote", default="origin", help="Remote to push to (default: origin)")
    parser.add_argument("--branch", default="master", help="Branch to push to (default: master)")
    parser.add_argument("--report", default="conflict_resolution_report.md", help="Report output path")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    os.chdir(REPO_ROOT)
    args = parse_args(argv)
    manager = ConflictManager(args)
    try:
        exit_code = manager.resolve()
    except CommandError as exc:
        print(f"Git command failed: {exc}")
        return 2
    except KeyboardInterrupt:
        print("Interrupted by user")
        return 130
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
