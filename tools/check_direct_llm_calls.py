#!/usr/bin/env python3
"""
Session 1098 PR #A2 — Direct-LLM-SDK lint checker.

Fails CI when Python source files outside ``core/services/llm_call_wrapper.py``,
``core/services/llm_provider_registry.py``, or the explicit whitelist make
direct calls to provider SDKs. Every LLM call must go through the Session
1098 wrapper (``llm_call_span`` / ``llm_call_async``) so we get:

- Per-call LLMCallEvent telemetry
- ``execution_id`` correlation back to AgentExecution
- Cooperative cancellation hooks (PR #3 will wire the token)
- Centralized provider-timeout enforcement

Usage::

    python tools/check_direct_llm_calls.py
    python tools/check_direct_llm_calls.py --root . --whitelist .ci/llm_whitelist.txt
    python tools/check_direct_llm_calls.py --warn-only   # CI log only, exit 0

Exit codes:
    0 — no violations (or --warn-only)
    1 — violations found
    2 — configuration error (missing whitelist file, bad patterns)

See docs/plans/SESSION_1098_FIX_B_FULL_TICKET.md for the broader Session
1098 rollout plan.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

# Conservative patterns. Goal: catch direct SDK use; avoid noisy false
# positives on unrelated `.create()` / `.messages` sites.
DEFAULT_PATTERNS: List[str] = [
    # OpenAI SDK:  client.chat.completions.create(...)
    r"\bclient\.chat\.completions\.create\b",
    # OpenAI SDK (legacy Responses API): client.responses.create(...)
    r"\bclient\.responses\.create\b",
    # OpenAI SDK on self: self.client.chat.completions.create(...)
    r"\bself\.client\.chat\.completions\.create\b",
    # OpenAI SDK on openai_client attribute: foo.openai_client.chat...
    r"\b(?:openai_client|_openai_client)\.chat\.completions\.create\b",
    # OpenAI SDK legacy: openai.ChatCompletion.create(...)
    r"\bopenai\.ChatCompletion\.create\b",
    # Anthropic SDK: client.messages.create(...)
    r"\bclient\.messages\.create\b",
    # Anthropic SDK on self: self.client.messages.create(...)
    r"\bself\.client\.messages\.create\b",
    # Anthropic SDK legacy: anthropic.messages.create(...)
    r"\banthropic\.messages\.create\b",
    # Anthropic client attribute: foo.anthropic_client.messages.create(...)
    r"\banthropic_client\.messages\.create\b",
]

TEXT_FILE_EXTS = {".py", ".pyi"}

# Directories we never scan even when listed under the root.
DEFAULT_IGNORE_DIRS = (
    ".venv", "venv", "venv_ml", "venv_*",
    ".git", ".eggs", "build", "dist",
    "node_modules", "__pycache__", ".mypy_cache", ".pytest_cache",
    "frontend/dist", "frontend/node_modules",
    "external-project-docs", "archive", "archive/scripts",
    "site-packages",
)


def load_whitelist(path: Path) -> List[str]:
    """Return whitelist path prefixes. Lines starting with ``#`` are comments.

    Whitelist entries are prefixes relative to the repo root. A directory
    suffix like ``core/tests/`` whitelists everything under it; an exact
    filename like ``core/services/llm_call_wrapper.py`` whitelists one file.
    """
    if not path.exists():
        return []
    lines: List[str] = []
    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            lines.append(line)
    return lines


def path_is_whitelisted(rel_path: str, whitelist: Iterable[str]) -> bool:
    """Match a posix-style relative path against whitelist prefixes.

    A directory prefix ends with ``/``; an exact file does not. Both forms
    are supported; directory entries match any file inside.
    """
    rel_posix = rel_path.replace(os.sep, "/")
    for entry in whitelist:
        entry_posix = entry.replace(os.sep, "/")
        if entry_posix.endswith("/"):
            if rel_posix.startswith(entry_posix):
                return True
        else:
            if rel_posix == entry_posix or rel_posix.startswith(entry_posix + "/"):
                return True
    return False


def compile_patterns(patterns: List[str]) -> List[re.Pattern[str]]:
    try:
        return [re.compile(p) for p in patterns]
    except re.error as exc:
        print(f"ERROR: invalid regex in pattern list: {exc}", file=sys.stderr)
        sys.exit(2)


def scan(
    root: Path,
    whitelist: List[str],
    patterns: List[re.Pattern[str]],
    ignore_dirs: Tuple[str, ...] = DEFAULT_IGNORE_DIRS,
) -> List[Tuple[str, int, str]]:
    """Walk ``root`` and return a list of ``(rel_path, lineno, matched_line)``."""
    matches: List[Tuple[str, int, str]] = []
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune traversal — modify dirnames in-place.
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir != "." and any(
            part in ignore_dirs for part in rel_dir.split(os.sep)
        ):
            continue

        for fn in filenames:
            ext = os.path.splitext(fn)[1]
            if ext not in TEXT_FILE_EXTS:
                continue
            abs_path = os.path.join(dirpath, fn)
            rel_path = os.path.relpath(abs_path, root)
            if path_is_whitelisted(rel_path, whitelist):
                continue

            try:
                with open(abs_path, "r", encoding="utf-8") as fh:
                    lines = fh.readlines()
                # Session 1098: track which lines are inside a
                # ``with llm_call_span(...)`` or ``llm_call_async(...)``
                # context so wrapped SDK calls don't trigger the lint.
                # A simple indent-tracking pass is enough — we flag a
                # line as "inside wrapper" if the most-recent less-
                # indented open-block was a wrapper call.
                wrapper_stack: List[int] = []  # indents that opened a wrapper block
                for lineno, raw_line in enumerate(lines, start=1):
                    stripped = raw_line.lstrip()
                    if stripped.startswith("#"):
                        continue
                    indent = len(raw_line) - len(stripped)

                    # Pop any wrapper contexts we've outdented past.
                    while wrapper_stack and indent <= wrapper_stack[-1]:
                        wrapper_stack.pop()

                    # Open a wrapper context on `with llm_call_span(` or
                    # `= llm_call_async(` or `await llm_call_async(`.
                    if (
                        "llm_call_span(" in raw_line
                        or "llm_call_async(" in raw_line
                    ) and ("def " not in raw_line and "import " not in raw_line):
                        wrapper_stack.append(indent)
                        continue

                    # Allow an explicit per-line suppression pragma.
                    if "# noqa: direct-llm-call" in raw_line:
                        continue

                    # Skip if we're inside a wrapper block.
                    if wrapper_stack:
                        continue

                    for cre in patterns:
                        if cre.search(raw_line):
                            matches.append(
                                (rel_path, lineno, raw_line.rstrip("\n"))
                            )
                            break
            except (UnicodeDecodeError, OSError):
                # Binary or permission issue — skip silently.
                continue
    return matches


def _format_report(matches: List[Tuple[str, int, str]]) -> str:
    """Human-readable match summary with adoption snippet."""
    lines: List[str] = []
    lines.append(
        "Direct LLM SDK calls detected — all LLM calls must route through "
        "core/services/llm_call_wrapper.py (Session 1098 PR #1):"
    )
    lines.append("")
    for rel, lineno, snippet in matches:
        lines.append(f"  {rel}:{lineno}: {snippet.strip()}")
    lines.append("")
    lines.append(f"Total violations: {len(matches)}")
    lines.append("")
    lines.append("How to fix — replace the direct call with the wrapper:")
    lines.append("")
    lines.append("  # sync sites:")
    lines.append("  from core.services.llm_call_wrapper import llm_call_span")
    lines.append("  with llm_call_span(")
    lines.append("      provider='openai', model='gpt-5-mini',")
    lines.append("      execution_id=ctx.get('execution_id'),")
    lines.append("      agent_name='MyAgent',")
    lines.append("  ) as span:")
    lines.append("      response = client.chat.completions.create(...)")
    lines.append("      span.attach_response(response)")
    lines.append("")
    lines.append("  # async sites:")
    lines.append("  from core.services.llm_call_wrapper import llm_call_async")
    lines.append("  response = await llm_call_async(")
    lines.append("      client.chat.completions.create,")
    lines.append("      model='gpt-5-mini', messages=[...],")
    lines.append("      provider='openai', model_name='gpt-5-mini',")
    lines.append("      execution_id=execution_id, agent_name='MyAgent',")
    lines.append("  )")
    lines.append("")
    lines.append(
        "If the hit is a legitimate exception (test harness, inside the "
        "wrapper itself), add the path to .ci/llm_whitelist.txt."
    )
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--root", default=".", help="Repo root to scan (default: CWD)",
    )
    ap.add_argument(
        "--whitelist",
        default=".ci/llm_whitelist.txt",
        help="Whitelist file of allowed paths (one per line). Lines starting "
             "with '#' are comments.",
    )
    ap.add_argument(
        "--patterns-file",
        default=None,
        help="Optional file with one regex per line to override DEFAULT_PATTERNS.",
    )
    ap.add_argument(
        "--warn-only",
        action="store_true",
        help="Print the report but exit 0. Use for staged rollout / soft-enforce.",
    )
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"ERROR: --root {root} does not exist", file=sys.stderr)
        return 2

    whitelist_path = root / args.whitelist
    whitelist = load_whitelist(whitelist_path)

    if args.patterns_file:
        patterns_path = root / args.patterns_file
        if not patterns_path.exists():
            print(
                f"ERROR: --patterns-file {patterns_path} does not exist",
                file=sys.stderr,
            )
            return 2
        with patterns_path.open("r", encoding="utf-8") as f:
            patterns_raw = [
                line.strip() for line in f
                if line.strip() and not line.startswith("#")
            ]
    else:
        patterns_raw = DEFAULT_PATTERNS

    patterns = compile_patterns(patterns_raw)
    matches = scan(root, whitelist, patterns)

    if not matches:
        print(
            f"✓ No direct LLM SDK calls detected "
            f"(scanned under {root}, whitelist={len(whitelist)} entries, "
            f"patterns={len(patterns)})."
        )
        return 0

    print(_format_report(matches))
    if args.warn_only:
        print()
        print("⚠  --warn-only set; exiting 0 despite violations.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
