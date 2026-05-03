#!/usr/bin/env python3
"""Repository guardrails for drift visibility.

TODO(Phase 4B): selected checks in this script can become blocking once the
repo is ready for stricter enforcement.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PATHS = [
    "venv_ml/",
    "frontend/dist/",
    "dist/",
    "docs/_index.json",
    "tests/artifacts/*.png",
    ".pyright-after.txt",
]

PLATFORM_INVENTORY = REPO_ROOT / "docs" / "PLATFORM_INVENTORY.md"


@dataclass
class CommandResult:
    label: str
    returncode: int
    stdout: str
    stderr: str


def run_command(args: list[str], label: str) -> CommandResult:
    proc = subprocess.run(
        args,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return CommandResult(label, proc.returncode, proc.stdout, proc.stderr)


def print_block(title: str, body: str) -> None:
    print(f"\n== {title} ==")
    if body.strip():
        print(body.rstrip())
    else:
        print("(no output)")


def summarize_json(output: str) -> str:
    if not output.strip():
        return "(no JSON output)"
    try:
        payload = json.loads(output)
    except json.JSONDecodeError:
        return output.rstrip()

    if isinstance(payload, dict):
        keys = ", ".join(sorted(payload.keys()))
        summary = [f"JSON object keys: {keys or '(none)'}"]
        findings = payload.get("findings")
        if isinstance(findings, list):
            summary.append(f"findings: {len(findings)}")
            counts: dict[str, int] = {}
            for item in findings:
                if isinstance(item, dict):
                    label = (
                        item.get("severity")
                        or item.get("level")
                        or item.get("status")
                        or item.get("kind")
                        or "unknown"
                    )
                    counts[str(label)] = counts.get(str(label), 0) + 1
            if counts:
                grouped = ", ".join(f"{key}={counts[key]}" for key in sorted(counts))
                summary.append(f"finding groups: {grouped}")
        for field in ("warnings", "conflicts", "issues", "errors"):
            value = payload.get(field)
            if isinstance(value, list):
                summary.append(f"{field}: {len(value)}")
        return "\n".join(summary)
    if isinstance(payload, list):
        return f"JSON array length: {len(payload)}"
    return f"JSON value type: {type(payload).__name__}"


def parse_findings(output: str) -> tuple[int, int, list[str], str]:
    if not output.strip():
        return 0, 0, [], "(no JSON output)"
    try:
        payload = json.loads(output)
    except json.JSONDecodeError:
        return 0, 0, [], output.rstrip()

    if not isinstance(payload, dict):
        return 0, 0, [], f"JSON value type: {type(payload).__name__}"

    findings = payload.get("findings")
    conflict_count = 0
    doc_only_count = 0
    messages: list[str] = []
    if isinstance(findings, list):
        for item in findings:
            if not isinstance(item, dict):
                continue
            severity = str(
                item.get("severity")
                or item.get("level")
                or item.get("status")
                or item.get("kind")
                or "unknown"
            ).upper()
            message = (
                item.get("message")
                or item.get("summary")
                or item.get("title")
                or item.get("name")
                or severity
            )
            if severity == "CONFLICT":
                conflict_count += 1
                messages.append(f"CONFLICT: {message}")
            elif severity == "DOC_ONLY":
                doc_only_count += 1
                messages.append(f"DOC_ONLY: {message}")
            else:
                messages.append(f"{severity}: {message}")
    return conflict_count, doc_only_count, messages, summarize_json(output)


def git_ls_files(patterns: Iterable[str]) -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files", "--", *patterns],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git ls-files failed")
    return [line for line in proc.stdout.splitlines() if line.strip()]


def git_short_head(ref: str = "HEAD") -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "--short", ref],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git rev-parse failed")
    return proc.stdout.strip()


def git_commit_files(ref: str = "HEAD") -> list[str]:
    proc = subprocess.run(
        ["git", "show", "--name-only", "--format=", "--no-renames", ref],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git show failed")
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def classify_platform_inventory_freshness(
    recorded_head: str,
    current_head: str,
    current_commit_files: list[str],
    parent_head: str | None,
) -> tuple[bool, str]:
    if recorded_head == current_head:
        return True, f"inventory head matches repo head {current_head}"

    if (
        parent_head
        and recorded_head == parent_head
        and current_commit_files == ["docs/PLATFORM_INVENTORY.md"]
    ):
        return (
            True,
            "inventory reflects parent HEAD; current HEAD is inventory-only "
            f"({current_head})",
        )

    return False, f"inventory head {recorded_head} != repo head {current_head}"


def check_platform_inventory_freshness() -> tuple[bool, str]:
    if not PLATFORM_INVENTORY.exists():
        return False, "docs/PLATFORM_INVENTORY.md is missing"

    content = PLATFORM_INVENTORY.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"\*\*Git HEAD:\*\*\s*`([^`]+)`", content)
    if not match:
        return False, "docs/PLATFORM_INVENTORY.md does not declare a Git HEAD"

    recorded_head = match.group(1).strip()
    current_head = git_short_head()
    parent_head = None
    try:
        parent_head = git_short_head("HEAD^")
    except RuntimeError:
        parent_head = None
    current_commit_files = git_commit_files("HEAD")
    return classify_platform_inventory_freshness(
        recorded_head=recorded_head,
        current_head=current_head,
        current_commit_files=current_commit_files,
        parent_head=parent_head,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run repository guardrails")
    strict_group = parser.add_mutually_exclusive_group()
    strict_group.add_argument(
        "--strict",
        dest="strict",
        action="store_true",
        default=True,
        help="Fail on stale inventory, tracked generated files, and CONFLICT findings (default).",
    )
    strict_group.add_argument(
        "--no-strict",
        dest="strict",
        action="store_false",
        help="Warn only, matching the Phase 4A behavior.",
    )
    args = parser.parse_args()

    print(f"Repository guardrails (strict={'on' if args.strict else 'off'})")
    print(f"Repository: {REPO_ROOT}")

    inspect_result = run_command(["context-kit", "inspect"], "context-kit inspect")
    print_block(inspect_result.label, inspect_result.stdout + inspect_result.stderr)
    if inspect_result.returncode != 0:
        print(f"WARNING: {inspect_result.label} exited with {inspect_result.returncode}")

    verify_result = run_command(["context-kit", "verify", "--json"], "context-kit verify --json")
    conflict_count, doc_only_count, finding_messages, verify_summary = parse_findings(verify_result.stdout)
    print_block(
        verify_result.label,
        verify_summary
        + (f"\n[stderr]\n{verify_result.stderr.rstrip()}" if verify_result.stderr.strip() else ""),
    )
    if verify_result.returncode != 0:
        print(f"WARNING: {verify_result.label} exited with {verify_result.returncode}")
    if finding_messages:
        print_block("context-kit verify findings", "\n".join(finding_messages))

    tracked = git_ls_files(FORBIDDEN_PATHS)
    print_block(
        "tracked generated paths",
        "\n".join(f"tracked: {path}" for path in tracked) if tracked else "none",
    )

    inventory_fresh, inventory_message = check_platform_inventory_freshness()
    print_block(
        "platform inventory freshness",
        inventory_message,
    )

    tracked_blocking = bool(tracked)
    if tracked:
        print("WARNING: tracked generated paths were found.")
    else:
        print("OK: no tracked generated paths found in the scoped checks.")

    inventory_blocking = not inventory_fresh
    if not inventory_fresh:
        print("WARNING: platform inventory freshness check failed.")
    else:
        print("OK: platform inventory matches the current repo head.")

    conflict_blocking = conflict_count > 0
    if conflict_count:
        print(f"WARNING: context-kit reported {conflict_count} CONFLICT finding(s).")
    if doc_only_count:
        print(f"WARNING: context-kit reported {doc_only_count} DOC_ONLY finding(s) (advisory).")

    failures: list[str] = []
    if args.strict and tracked_blocking:
        failures.append("tracked generated paths are present")
    if args.strict and inventory_blocking:
        failures.append("platform inventory is stale")
    if args.strict and conflict_blocking:
        failures.append("context-kit has CONFLICT findings")

    pass_fail = "FAIL" if failures else "PASS"
    print(f"\n{pass_fail} summary")
    if failures:
        for failure in failures:
            print(f"- {failure}")
        print("Next step: regenerate the inventory, remove tracked generated artifacts, and clear doc/runtime conflicts before re-running.")
    else:
        print("- No blocking guardrail rules were triggered.")
        if doc_only_count:
            print("- DOC_ONLY findings remain advisory.")
        if not args.strict:
            print("- Strict mode is disabled, so blocking rules were reported as warnings only.")

    print("\nSummary")
    print(f"- context-kit inspect exit: {inspect_result.returncode}")
    print(f"- context-kit verify --json exit: {verify_result.returncode}")
    print(f"- tracked generated paths: {len(tracked)}")
    print(f"- platform inventory fresh: {inventory_fresh}")
    print(f"- context-kit CONFLICT findings: {conflict_count}")
    print(f"- context-kit DOC_ONLY findings: {doc_only_count}")
    print(f"- strict mode: {'on' if args.strict else 'off'}")
    print("- Phase 4B keeps strict mode on by default and leaves DOC_ONLY/inspect/large-file checks advisory.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
