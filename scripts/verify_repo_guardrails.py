#!/usr/bin/env python3
"""Non-blocking repository guardrails for drift visibility.

TODO(Phase 4B): selected checks in this script can become blocking once the
repo is ready for stricter enforcement.
"""

from __future__ import annotations

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


def git_short_head() -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git rev-parse failed")
    return proc.stdout.strip()


def check_platform_inventory_freshness() -> tuple[bool, str]:
    if not PLATFORM_INVENTORY.exists():
        return False, "docs/PLATFORM_INVENTORY.md is missing"

    content = PLATFORM_INVENTORY.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"\*\*Git HEAD:\*\*\s*`([^`]+)`", content)
    if not match:
        return False, "docs/PLATFORM_INVENTORY.md does not declare a Git HEAD"

    recorded_head = match.group(1).strip()
    current_head = git_short_head()
    if recorded_head != current_head:
        return False, f"inventory head {recorded_head} != repo head {current_head}"
    return True, f"inventory head matches repo head {current_head}"


def main() -> int:
    print("Repository guardrails (non-blocking)")
    print(f"Repository: {REPO_ROOT}")

    inspect_result = run_command(["context-kit", "inspect"], "context-kit inspect")
    print_block(inspect_result.label, inspect_result.stdout + inspect_result.stderr)
    if inspect_result.returncode != 0:
        print(f"WARNING: {inspect_result.label} exited with {inspect_result.returncode}")

    verify_result = run_command(["context-kit", "verify", "--json"], "context-kit verify --json")
    print_block(
        verify_result.label,
        summarize_json(verify_result.stdout)
        + (f"\n[stderr]\n{verify_result.stderr.rstrip()}" if verify_result.stderr.strip() else ""),
    )
    if verify_result.returncode != 0:
        print(f"WARNING: {verify_result.label} exited with {verify_result.returncode}")

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

    if tracked:
        print("WARNING: tracked generated paths were found.")
    else:
        print("OK: no tracked generated paths found in the scoped checks.")

    if not inventory_fresh:
        print("WARNING: platform inventory freshness check failed.")
    else:
        print("OK: platform inventory matches the current repo head.")

    print("\nSummary")
    print(f"- context-kit inspect exit: {inspect_result.returncode}")
    print(f"- context-kit verify --json exit: {verify_result.returncode}")
    print(f"- tracked generated paths: {len(tracked)}")
    print(f"- platform inventory fresh: {inventory_fresh}")
    print("- This script is intentionally non-blocking in Phase 4A.")
    print("- Phase 4B can promote selected warnings to failures once the repo is ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
