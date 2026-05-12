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
DOCS_INDEX = REPO_ROOT / "docs" / "INDEX.md"
DOCS_INDEX_AUTOGEN_PATTERN = re.compile(
    r"<!--\s*DOC-AUTOGEN:.*build_docs_index", re.IGNORECASE
)

# Session 1115 — extra DOC-AUTOGEN files emitted by the capability audits.
# Each has its own `build_<x>_audit` command; CI/strict mode catches
# hand-edits to any of them by requiring the first non-blank line to carry
# a DOC-AUTOGEN marker that references the regenerating command.
AUDIT_AUTOGEN_FILES: list[tuple[Path, str]] = [
    (REPO_ROOT / "docs" / "CAPABILITY_AUDIT.md",  "build_capability_audit"),
    (REPO_ROOT / "docs" / "SPIDER_AUDIT.md",      "build_spider_audit"),
    (REPO_ROOT / "docs" / "PA_TOOL_AUDIT.md",     "build_pa_tool_audit"),
    (REPO_ROOT / "docs" / "BEAT_AUDIT.md",        "build_beat_audit"),
    (REPO_ROOT / "docs" / "ADVISOR_AUDIT.md",     "build_advisor_audit"),
    (REPO_ROOT / "docs" / "DISCORD_AUDIT.md",     "build_discord_audit"),
    (REPO_ROOT / "docs" / "BODY_SYSTEM_AUDIT.md", "build_body_system_audit"),
    (REPO_ROOT / "docs" / "LEARNING_BRIDGE_AUDIT.md", "build_learning_bridge_audit"),
    (REPO_ROOT / "docs" / "ML_AUDIT.md", "build_ml_audit"),
]
AUDIT_AUTOGEN_PATTERN = re.compile(r"<!--\s*DOC-AUTOGEN", re.IGNORECASE)


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


def classify_docs_index_autogen(first_nonblank_line: str) -> tuple[bool, str]:
    """Return (ok, message) given the first non-blank line of docs/INDEX.md.

    Pure function so tests can exercise it without filesystem access.
    Tolerant of minor wording drift: matches any HTML comment line that
    contains both ``DOC-AUTOGEN`` and ``build_docs_index``.
    """
    line = first_nonblank_line.strip()
    if not line:
        return False, (
            "docs/INDEX.md is empty or its first non-blank line is missing "
            "the DOC-AUTOGEN marker (fix: python manage.py build_docs_index)"
        )
    if DOCS_INDEX_AUTOGEN_PATTERN.search(line):
        return True, "docs/INDEX.md carries the DOC-AUTOGEN marker"
    return (
        False,
        "docs/INDEX.md is missing the DOC-AUTOGEN marker on its first "
        "non-blank line (fix: python manage.py build_docs_index)",
    )


def check_docs_index_autogen_marker() -> tuple[bool, str]:
    if not DOCS_INDEX.exists():
        return False, (
            "docs/INDEX.md is missing "
            "(fix: python manage.py build_docs_index)"
        )
    first_line = ""
    with DOCS_INDEX.open("r", encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            stripped = raw.strip()
            if stripped:
                first_line = stripped
                break
    return classify_docs_index_autogen(first_line)


def check_audit_autogen_markers() -> tuple[bool, list[str]]:
    """Confirm every Session-1115 audit doc still carries its DOC-AUTOGEN marker.

    Each entry is checked against the same first-non-blank-line rule used
    for ``docs/INDEX.md``. Missing files report `missing`; present-but-no-
    marker files report `hand-edited`. Returns ``(all_ok, per-file messages)``.
    """
    messages: list[str] = []
    all_ok = True
    for path, command_hint in AUDIT_AUTOGEN_FILES:
        rel = path.relative_to(REPO_ROOT)
        if not path.exists():
            all_ok = False
            messages.append(
                f"{rel}: missing "
                f"(fix: python manage.py {command_hint})"
            )
            continue
        first_line = ""
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                stripped = raw.strip()
                if stripped:
                    first_line = stripped
                    break
        if AUDIT_AUTOGEN_PATTERN.search(first_line):
            messages.append(f"{rel}: marker present")
        else:
            all_ok = False
            messages.append(
                f"{rel}: missing DOC-AUTOGEN marker on first non-blank line "
                f"(fix: python manage.py {command_hint})"
            )
    return all_ok, messages


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


def classify_failures(
    *,
    strict: bool,
    inventory_advisory: bool,
    tracked_blocking: bool,
    inventory_blocking: bool,
    autogen_blocking: bool,
    conflict_blocking: bool,
    audit_autogen_blocking: bool = False,
) -> list[str]:
    """Return the strict-mode failure list given the per-check booleans.

    Pure function so tests can exercise the decision matrix without
    spinning up ``main()`` or running the underlying checks.

    ``inventory_advisory`` only carves out the inventory-freshness
    check: when set, a stale inventory does not fail strict mode but
    is still surfaced in the report (the caller still prints the
    WARNING line). Every other strict check is unaffected — the goal
    is to enforce gates that CI can actually verify (tracked-paths,
    autogen marker, CONFLICT findings) while letting freshness, which
    is DB-gated and unsatisfiable from a CI runner without DB access,
    remain reportable but non-blocking.
    """
    failures: list[str] = []
    if strict and tracked_blocking:
        failures.append("tracked generated paths are present")
    if strict and inventory_blocking and not inventory_advisory:
        failures.append("platform inventory is stale")
    if strict and autogen_blocking:
        failures.append("docs/INDEX.md is missing the DOC-AUTOGEN marker")
    if strict and audit_autogen_blocking:
        failures.append(
            "one or more capability-audit docs are missing the DOC-AUTOGEN marker"
        )
    if strict and conflict_blocking:
        failures.append("context-kit has CONFLICT findings")
    return failures


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
    parser.add_argument(
        "--inventory-advisory",
        action="store_true",
        help=(
            "Treat platform-inventory freshness as advisory (never blocks) "
            "even in strict mode. Other strict checks (tracked-paths, "
            "DOC-AUTOGEN marker, CONFLICT findings) continue to block. "
            "Intended for PR-time CI where the inventory regenerator "
            "(`python manage.py generate_platform_inventory`) needs DB "
            "access that the runner does not have. Local strict runs "
            "should not need this flag."
        ),
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

    autogen_ok, autogen_message = check_docs_index_autogen_marker()
    print_block(
        "docs/INDEX.md autogen marker",
        autogen_message,
    )

    audit_autogen_ok, audit_autogen_messages = check_audit_autogen_markers()
    print_block(
        "audit DOC-AUTOGEN markers",
        "\n".join(audit_autogen_messages),
    )

    tracked_blocking = bool(tracked)
    if tracked:
        print("WARNING: tracked generated paths were found.")
    else:
        print("OK: no tracked generated paths found in the scoped checks.")

    inventory_blocking = not inventory_fresh
    if not inventory_fresh:
        if args.strict and args.inventory_advisory:
            print(
                "WARNING: platform inventory freshness check failed "
                "(advisory under --inventory-advisory; will not fail strict mode)."
            )
        else:
            print("WARNING: platform inventory freshness check failed.")
    else:
        print("OK: platform inventory matches the current repo head.")

    autogen_blocking = not autogen_ok
    if not autogen_ok:
        print("WARNING: docs/INDEX.md is missing or has lost its DOC-AUTOGEN marker.")
    else:
        print("OK: docs/INDEX.md carries the DOC-AUTOGEN marker.")

    audit_autogen_blocking = not audit_autogen_ok
    if not audit_autogen_ok:
        print(
            "WARNING: one or more capability-audit DOC-AUTOGEN files are "
            "missing or hand-edited (see the 'audit DOC-AUTOGEN markers' "
            "block above for which)."
        )
    else:
        print("OK: all capability-audit docs carry their DOC-AUTOGEN marker.")

    conflict_blocking = conflict_count > 0
    if conflict_count:
        print(f"WARNING: context-kit reported {conflict_count} CONFLICT finding(s).")
    if doc_only_count:
        print(f"WARNING: context-kit reported {doc_only_count} DOC_ONLY finding(s) (advisory).")

    failures = classify_failures(
        strict=args.strict,
        inventory_advisory=args.inventory_advisory,
        tracked_blocking=tracked_blocking,
        inventory_blocking=inventory_blocking,
        autogen_blocking=autogen_blocking,
        audit_autogen_blocking=audit_autogen_blocking,
        conflict_blocking=conflict_blocking,
    )

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
    print(f"- platform inventory fresh: {inventory_fresh}{' (advisory)' if args.inventory_advisory else ''}")
    print(f"- docs/INDEX.md autogen marker: {autogen_ok}")
    print(f"- context-kit CONFLICT findings: {conflict_count}")
    print(f"- context-kit DOC_ONLY findings: {doc_only_count}")
    print(f"- strict mode: {'on' if args.strict else 'off'}")
    print("- Phase 4B keeps strict mode on by default and leaves DOC_ONLY/inspect/large-file checks advisory.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
