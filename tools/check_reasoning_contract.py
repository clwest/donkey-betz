#!/usr/bin/env python3
"""Session 1216 Phase E — Reasoning-contract CI lint.

Fails CI when a PR adds a direct OpenAI SDK call that passes a forbidden
kwarg (``max_tokens``, ``temperature``, ``top_p``, ``frequency_penalty``,
``presence_penalty``) against a gpt-5.x reasoning model.

Sibling to ``tools/check_direct_llm_calls.py``. That lint enforces the
provider-SDK-wrapper boundary; this one enforces the gpt-5.x reasoning
contract — runtime-equivalent of ``OPENAI_REASONING_GUARD=error`` for
new code, caught at PR time.

Detection method
----------------
AST parsing, not regex. The lint only fires on actual call expressions:

- ``client.chat.completions.create(model=..., max_tokens=...)``
- ``client.chat.completions.create(model=..., temperature=...)``
- ...and the other 3 forbidden kwargs

Docstrings, comments, and references that mention the call pattern in
prose don't trip the lint.

Triggering rules:
1. The call must look like ``*.chat.completions.create(...)``.
2. The ``model=`` kwarg must be a string literal containing ``"gpt-5"``,
   or a Subscript access against a name containing ``OPENAI_CONFIG``
   (e.g., ``OPENAI_CONFIG['model']``).
3. At least one forbidden kwarg must be passed in the call.

Anything that doesn't match all three is silently allowed.

Exclusions
----------
- ``archive/`` (any subpath)
- ``tests/``, ``scripts/`` (testing + ad-hoc)
- ``core/services/llm_provider_registry.py`` — the abstraction layer
  intentionally passes ``max_tokens`` through ``_call_chat_api`` for
  non-reasoning models. It's correct there.
- Anything listed in ``.ci/reasoning_guard_whitelist.txt`` (created by
  this lint on first run if not present).

Usage
-----
::

    python tools/check_reasoning_contract.py
    python tools/check_reasoning_contract.py --warn-only   # CI log only

Exit codes
----------
- 0 — no violations
- 1 — violations found
- 2 — configuration error
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

FORBIDDEN_KWARGS = (
    "max_tokens",
    "temperature",
    "top_p",
    "frequency_penalty",
    "presence_penalty",
)

REASONING_MODEL_SUBSTRING = "gpt-5"

# Directories never scanned.
EXCLUDED_DIRS = (
    "archive/",
    ".venv/",
    "node_modules/",
    "__pycache__/",
    "frontend/",
    "tests/",
    "scripts/",
)

# Files where direct max_tokens / temperature passing is correct
# regardless of model (abstraction layer mapping it correctly per model).
EXCLUDED_FILES = (
    "core/services/llm_provider_registry.py",
)


class _ReasoningContractVisitor(ast.NodeVisitor):
    """Walk the AST. For every ``.chat.completions.create(...)`` call,
    inspect kwargs and report if the model looks gpt-5.x and any
    forbidden param is passed."""

    def __init__(self) -> None:
        self.violations: List[Tuple[int, str, List[str]]] = []

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802 (AST visitor protocol)
        if not self._is_chat_completions_create(node):
            self.generic_visit(node)
            return

        model_name = self._extract_model_kwarg(node)
        if not self._is_reasoning_model(model_name):
            self.generic_visit(node)
            return

        present_forbidden = [
            kw.arg for kw in node.keywords
            if kw.arg in FORBIDDEN_KWARGS
        ]
        if present_forbidden:
            self.violations.append(
                (node.lineno, model_name or "<unknown>", present_forbidden)
            )

        self.generic_visit(node)

    @staticmethod
    def _is_chat_completions_create(node: ast.Call) -> bool:
        """Detect ``*.chat.completions.create(...)`` shape via attribute
        chain. Matches both ``client.chat.completions.create`` and
        ``self.client.chat.completions.create`` regardless of receiver."""
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr != "create":
            return False
        completions = func.value
        if not isinstance(completions, ast.Attribute) or completions.attr != "completions":
            return False
        chat = completions.value
        if not isinstance(chat, ast.Attribute) or chat.attr != "chat":
            return False
        return True

    @staticmethod
    def _extract_model_kwarg(node: ast.Call) -> Optional[str]:
        """Return the model name if it's a string literal kwarg, or a
        flag string when it's an OPENAI_CONFIG-style lookup so the lint
        treats it as gpt-5.x. Returns None for fully-dynamic models the
        lint can't reason about."""
        for kw in node.keywords:
            if kw.arg != "model":
                continue
            if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                return kw.value.value
            # OPENAI_CONFIG['model'] — assume gpt-5.x by default since
            # config/api_settings.py defaults to gpt-5-mini.
            if isinstance(kw.value, ast.Subscript):
                src = ast.unparse(kw.value)
                if "OPENAI_CONFIG" in src:
                    return "<OPENAI_CONFIG['model']:assumed-gpt-5>"
            return None
        return None

    @staticmethod
    def _is_reasoning_model(model_name: Optional[str]) -> bool:
        if not model_name:
            return False
        return REASONING_MODEL_SUBSTRING in model_name.lower()


def _load_whitelist(path: Path) -> set[str]:
    if not path.exists():
        return set()
    entries = set()
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            entries.add(line)
    return entries


def _should_scan(rel_path: str, whitelist: set[str]) -> bool:
    if rel_path in EXCLUDED_FILES:
        return False
    for excluded in EXCLUDED_DIRS:
        if rel_path.startswith(excluded):
            return False
    if rel_path in whitelist:
        return False
    return True


def iter_py_files(root: Path) -> Iterable[Path]:
    return sorted(root.rglob("*.py"))


def scan_file(path: Path) -> List[Tuple[int, str, List[str]]]:
    try:
        source = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []
    visitor = _ReasoningContractVisitor()
    visitor.visit(tree)
    return visitor.violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."),
                        help="Repo root to scan (default: cwd)")
    parser.add_argument("--whitelist", type=Path,
                        default=Path(".ci/reasoning_guard_whitelist.txt"),
                        help="Path to whitelist file (one rel-path per line)")
    parser.add_argument("--warn-only", action="store_true",
                        help="Print violations but exit 0")
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        print(f"error: --root {root} is not a directory", file=sys.stderr)
        return 2

    whitelist = _load_whitelist(args.whitelist)

    total_violations = 0
    findings: List[Tuple[str, int, str, List[str]]] = []

    for py_file in iter_py_files(root):
        rel = py_file.relative_to(root).as_posix()
        if not _should_scan(rel, whitelist):
            continue
        for lineno, model, forbidden in scan_file(py_file):
            findings.append((rel, lineno, model, forbidden))
            total_violations += 1

    if not findings:
        print("Reasoning-contract check: no violations.")
        return 0

    print(
        "Reasoning-contract violations detected — gpt-5.x models reject "
        "max_tokens/temperature/top_p/frequency_penalty/presence_penalty:\n"
    )
    for rel, lineno, model, forbidden in findings:
        print(
            f"  {rel}:{lineno}: model={model!r} passes forbidden "
            f"{forbidden!r}"
        )

    print(f"\nTotal violations: {total_violations}")
    print(
        "\nHow to fix:\n"
        "  - Replace 'max_tokens=N' with 'max_completion_tokens=N'.\n"
        "  - Remove 'temperature', 'top_p', 'frequency_penalty', "
        "'presence_penalty' for gpt-5.x callers.\n"
        "  - For optional sampling-aware sites, build kwargs conditionally:\n"
        "      kwargs = {'model': model, ...}\n"
        "      if 'gpt-5' not in model.lower():\n"
        "          kwargs['temperature'] = temperature\n"
        "  - If the site is a legitimate exception (test harness, "
        "abstraction layer mapping per model), add the path to "
        f"{args.whitelist!s}.\n"
    )

    return 0 if args.warn_only else 1


if __name__ == "__main__":
    sys.exit(main())
