"""Phase 1 — generate a unified diff that pins every Celery task name in
``core/tasks.py``.

Reads ``core/tasks.py``, finds every task whose decorator does not already
carry an explicit ``name=`` kwarg, and constructs the in-place rewrite
that adds ``name="core.tasks.<function_name>"``. Output is a unified
diff to stdout (default) or an in-place rewrite (``--write``).

Read-only by default. The ``--write`` flag mutates ``core/tasks.py``; it
refuses to run when ``git status`` shows the file as modified, so a dirty
working tree can't be silently overwritten.

Safety contract:
  * No imports of project code (no Django bootstrap).
  * No Celery interactions (worker isn't pinged).
  * No DB queries.
  * Already-pinned tasks are skipped — including ``backfill_signal_scores``,
    which carries a non-standard registered name that Phase 3 must preserve
    verbatim.

Decorator rewrite rules:
  1. Bare ``@shared_task``                → ``@shared_task(name="core.tasks.X")``
  2. ``@shared_task()``                   → ``@shared_task(name="core.tasks.X")``
  3. ``@shared_task(bind=True)``          → ``@shared_task(bind=True, name="core.tasks.X")``
  4. Multi-line with trailing comma       → new kwarg appended on its own line
                                            with the existing per-arg indent
  5. Multi-line without trailing comma    → new kwarg appended; trailing comma
                                            added to the previous arg

Run from anywhere:
    python3 scripts/phase1_pin_task_names.py            # diff to stdout
    python3 scripts/phase1_pin_task_names.py --write    # apply in-place
"""

from __future__ import annotations

import argparse
import ast
import difflib
import re
import subprocess
import sys
from pathlib import Path


PROJECT = Path(__file__).resolve().parent.parent
TASKS_FILE = PROJECT / "core" / "tasks.py"


# ---------------------------------------------------------------------------
# Decorator detection (mirror Phase 0 helpers; kept local for self-contained
# operation — Phase 1 doesn't import from Phase 0).
# ---------------------------------------------------------------------------


def _is_celery_decorator(deco: ast.expr) -> bool:
    if isinstance(deco, ast.Name):
        return deco.id == "shared_task"
    if isinstance(deco, ast.Attribute):
        return deco.attr == "task"
    if isinstance(deco, ast.Call):
        return _is_celery_decorator(deco.func)
    return False


def _has_explicit_name_kwarg(deco: ast.expr) -> bool:
    if not isinstance(deco, ast.Call):
        return False
    for kw in deco.keywords:
        if kw.arg == "name" and isinstance(kw.value, ast.Constant):
            return True
    return False


# ---------------------------------------------------------------------------
# Rewrite plan — one entry per unpinned task.
# ---------------------------------------------------------------------------


class RewriteFailure(Exception):
    """Raised when a decorator can't be rewritten safely."""


def _abs_offset(source: str, lineno: int, col_offset: int) -> int:
    """Translate a 1-indexed (lineno, col_offset) AST position into an
    absolute character offset into ``source``."""
    lines = source.splitlines(keepends=True)
    return sum(len(l) for l in lines[: lineno - 1]) + col_offset


def _rewrite_decorator(source: str, deco: ast.expr, func_name: str) -> str:
    """Return ``source`` with the celery decorator rewritten to include
    ``name="core.tasks.<func_name>"``. Raises ``RewriteFailure`` if the AST
    span isn't usable (older Python missing end positions, etc.)."""
    new_kwarg = f'name="core.tasks.{func_name}"'

    # Sanity: AST must carry end positions (Python 3.8+). After this guard,
    # ``end_lineno`` / ``end_col_offset`` are guaranteed non-None ints.
    end_lineno = deco.end_lineno
    end_col_offset = deco.end_col_offset
    if end_lineno is None or end_col_offset is None:
        raise RewriteFailure("AST decorator node missing end position info")

    # Bare decorator (Name / Attribute, never called).
    if not isinstance(deco, ast.Call):
        end_abs = _abs_offset(source, end_lineno, end_col_offset)
        return source[:end_abs] + f"({new_kwarg})" + source[end_abs:]

    # Called decorator — locate the closing ).
    end_abs = _abs_offset(source, end_lineno, end_col_offset)
    paren_pos = end_abs - 1
    if paren_pos < 0 or source[paren_pos] != ")":
        raise RewriteFailure(
            f"expected ')' at end of decorator at line {end_lineno}, "
            f"col {end_col_offset}; got {source[paren_pos]!r}"
        )

    has_args = bool(deco.args) or bool(deco.keywords)
    if not has_args:
        # @shared_task() — insert kwarg between ()
        return source[:paren_pos] + new_kwarg + source[paren_pos:]

    # Has existing args. Find the last non-whitespace char before ).
    i = paren_pos - 1
    while i >= 0 and source[i] in " \t\r\n":
        i -= 1
    if i < 0:
        raise RewriteFailure("malformed decorator: closing ')' with no preceding content")

    last_char = source[i]
    is_multiline = deco.lineno != end_lineno

    if last_char == ",":
        # Trailing comma already.
        if is_multiline:
            # Match the indent of the line containing the trailing comma.
            comma_line_start = source.rfind("\n", 0, i) + 1
            indent_match = re.match(r"[ \t]*", source[comma_line_start:i])
            indent = indent_match.group(0) if indent_match else "    "
            return (
                source[: i + 1]
                + f"\n{indent}{new_kwarg},"
                + source[i + 1 : paren_pos]
                + source[paren_pos:]
            )
        # Single-line trailing comma — rare but possible: (bind=True,)
        return source[: paren_pos] + f" {new_kwarg}," + source[paren_pos:]

    # No trailing comma.
    if is_multiline:
        # Add comma + new line + new kwarg + trailing comma, matching the
        # last-argument's indentation.
        last_arg_line_start = source.rfind("\n", 0, i) + 1
        indent_match = re.match(r"[ \t]*", source[last_arg_line_start:i])
        indent = indent_match.group(0) if indent_match else "    "
        return (
            source[: i + 1]
            + f",\n{indent}{new_kwarg},"
            + source[i + 1 : paren_pos]
            + source[paren_pos:]
        )

    # Single-line, no trailing comma — the common case for most tasks.
    return source[: paren_pos] + f", {new_kwarg}" + source[paren_pos:]


# ---------------------------------------------------------------------------
# Plan + apply
# ---------------------------------------------------------------------------


def _walk_unpinned_tasks(tree: ast.Module) -> list[tuple[ast.FunctionDef | ast.AsyncFunctionDef, ast.expr]]:
    """Return (funcdef, decorator) pairs for every unpinned Celery task."""
    out: list[tuple[ast.FunctionDef | ast.AsyncFunctionDef, ast.expr]] = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        celery_deco: ast.expr | None = None
        for d in node.decorator_list:
            if _is_celery_decorator(d):
                celery_deco = d
                break
        if celery_deco is None:
            continue
        if _has_explicit_name_kwarg(celery_deco):
            continue
        out.append((node, celery_deco))
    return out


def _build_rewritten_source(source: str, tree: ast.Module) -> tuple[str, dict]:
    """Apply all rewrites in reverse order (so positions of earlier rewrites
    aren't disturbed). Returns (new_source, stats)."""
    targets = _walk_unpinned_tasks(tree)
    # Sort by start position descending so each rewrite operates on positions
    # that haven't been shifted by later rewrites.
    targets_sorted = sorted(
        targets,
        key=lambda fd_d: (fd_d[1].lineno, fd_d[1].col_offset),
        reverse=True,
    )

    stats = {
        "total_unpinned": len(targets),
        "would_pin": 0,
        "failed": [],  # list of (func_name, error)
    }

    new_source = source
    for funcdef, deco in targets_sorted:
        try:
            new_source = _rewrite_decorator(new_source, deco, funcdef.name)
        except RewriteFailure as exc:
            stats["failed"].append((funcdef.name, str(exc)))
            continue
        stats["would_pin"] += 1
    return new_source, stats


def _count_already_pinned(tree: ast.Module) -> int:
    n = 0
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for d in node.decorator_list:
            if _is_celery_decorator(d) and _has_explicit_name_kwarg(d):
                n += 1
                break
    return n


# ---------------------------------------------------------------------------
# --write safety
# ---------------------------------------------------------------------------


def _git_clean_for_tasks_file() -> bool:
    """Return True if `git status --porcelain core/tasks.py` is empty."""
    try:
        result = subprocess.run(
            ["git", "-C", str(PROJECT), "status", "--porcelain", str(TASKS_FILE.relative_to(PROJECT))],
            capture_output=True,
            check=False,
            text=True,
        )
    except (OSError, FileNotFoundError):
        return False
    return result.returncode == 0 and result.stdout.strip() == ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--write",
        action="store_true",
        help=(
            "Apply the rewrite in-place. Default is read-only (diff to stdout). "
            "Refuses to run when core/tasks.py has uncommitted changes."
        ),
    )
    args = parser.parse_args()

    if not TASKS_FILE.is_file():
        print(f"phase1_pin_task_names: source file not found: {TASKS_FILE}", file=sys.stderr)
        return 1

    src = TASKS_FILE.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        print(f"phase1_pin_task_names: syntax error in {TASKS_FILE}: {exc}", file=sys.stderr)
        return 1

    new_src, stats = _build_rewritten_source(src, tree)
    already_pinned = _count_already_pinned(tree)

    # Header summary on stderr (so it doesn't pollute the diff if piped).
    print(
        f"phase1_pin_task_names: target file {TASKS_FILE.relative_to(PROJECT)}",
        file=sys.stderr,
    )
    print(f"  already pinned (skipped):  {already_pinned}", file=sys.stderr)
    print(f"  would pin (new name=):     {stats['would_pin']}", file=sys.stderr)
    print(f"  rewrite failures:          {len(stats['failed'])}", file=sys.stderr)
    if stats["failed"]:
        for func_name, err in stats["failed"]:
            print(f"    ! {func_name}: {err}", file=sys.stderr)

    if new_src == src:
        print("  (no changes — every task already has an explicit name=)", file=sys.stderr)
        return 0

    if args.write:
        if not _git_clean_for_tasks_file():
            print(
                f"phase1_pin_task_names: refusing to overwrite {TASKS_FILE.relative_to(PROJECT)} "
                "while it has uncommitted changes. Stage / commit / stash first, then re-run.",
                file=sys.stderr,
            )
            return 2
        TASKS_FILE.write_text(new_src, encoding="utf-8")
        print(f"phase1_pin_task_names: wrote {TASKS_FILE.relative_to(PROJECT)}", file=sys.stderr)
        return 0

    # Default: emit unified diff to stdout.
    rel = TASKS_FILE.relative_to(PROJECT)
    diff = difflib.unified_diff(
        src.splitlines(keepends=True),
        new_src.splitlines(keepends=True),
        fromfile=f"a/{rel}",
        tofile=f"b/{rel}",
        n=3,
    )
    sys.stdout.writelines(diff)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
