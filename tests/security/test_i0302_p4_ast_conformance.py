"""
tests/security/test_i0302_p4_ast_conformance.py — I-0302 Phase 4 Sub-phase 3
AST conformance harness for security-critical view-file patterns.

Ships in REPORT-ONLY mode per Chris D-verdict at S2749 open (path 2 fallback
after Rigby LLM-boundary jam on the rule proposal — see I-030204 §6).

Current rule: Http404-swallow anti-pattern (I-0302 §14 codification).
    A try block calling get_object_or_404 whose except handlers catch broad
    Exception without a preceding `except Http404: raise` guard converts
    Django's Http404 into 500 responses. 5 sites documented in §5.1.b tail;
    §14 two-triggers-plus threshold MET decisively.

Design contract: docs/research/implementation/tenant_boundary_lockdown/
                 I-030204_ast_conformance_rule_spec.md

Mode switch: to flip enforcing mode, change ENFORCE_HTTP404_SWALLOW to True.
See I-030204 §5 for enforcement-flip acceptance criteria.
"""
from __future__ import annotations

import ast
import json
import warnings
from datetime import datetime, timezone
from pathlib import Path

import pytest

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = REPO_ROOT / "test_reports"
REPORT_PATH = REPORT_DIR / "i0302_p4_ast_conformance.json"

INCLUDED_GLOBS = (
    "core/views*.py",
    "core/views/**/*.py",
    "apps/*/views*.py",
    "apps/*/views/**/*.py",
)

EXCLUDED_SUBSTRINGS = (
    "/tests/",
    "/migrations/",
    "/management/commands/",
    "/__pycache__/",
    "/.venv/",
    "/venv/",
    "/env/",
    "/site-packages/",
)

# Mode switch — flip to True post batch-fix per I-030204 §5.
ENFORCE_HTTP404_SWALLOW = False


# --------------------------------------------------------------------------
# File discovery
# --------------------------------------------------------------------------


def _discover_view_files() -> list[Path]:
    """Return sorted list of view files matching the allowlist glob spec."""
    seen: set[Path] = set()
    for pattern in INCLUDED_GLOBS:
        for path in REPO_ROOT.glob(pattern):
            if not path.is_file() or path.suffix != ".py":
                continue
            posix = path.as_posix()
            if any(sub in posix for sub in EXCLUDED_SUBSTRINGS):
                continue
            seen.add(path)
    return sorted(seen)


# --------------------------------------------------------------------------
# AST inspection — Http404-swallow rule
# --------------------------------------------------------------------------


def _collect_g404_aliases(tree: ast.Module) -> set[str]:
    """Collect local names bound to `get_object_or_404` at module scope.

    Per I-030204 §3.3: recognizes direct import, aliased import, and
    module-level rebinding. Function-local rebinding is out of scope.
    """
    aliases: set[str] = {"get_object_or_404"}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "django.shortcuts":
            for name in node.names:
                if name.name == "get_object_or_404":
                    aliases.add(name.asname or name.name)
        # Module-level rebinding: `g404 = get_object_or_404`
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            value = node.value
            if (
                isinstance(target, ast.Name)
                and isinstance(value, ast.Name)
                and value.id in aliases
            ):
                aliases.add(target.id)
    return aliases


def _call_is_g404(node: ast.Call, aliases: set[str]) -> bool:
    """Return True if this Call node invokes get_object_or_404."""
    func = node.func
    if isinstance(func, ast.Name):
        return func.id in aliases
    if isinstance(func, ast.Attribute):
        return func.attr == "get_object_or_404"
    return False


def _try_body_calls_g404(try_node: ast.Try, aliases: set[str]) -> bool:
    """Return True if any Call to get_object_or_404 lives in the try body subtree.

    Scoped to `try_node.body` — nested Try nodes are inspected independently.
    """
    for stmt in try_node.body:
        for descendant in ast.walk(stmt):
            if isinstance(descendant, ast.Call) and _call_is_g404(descendant, aliases):
                return True
    return False


def _handler_type_names(handler: ast.ExceptHandler) -> tuple[list[str], bool]:
    """Return (list-of-type-names, catches_broad_bool) for a handler.

    catches_broad is True when the handler catches Exception, BaseException,
    or is a bare `except:` — all of which swallow Http404.
    """
    if handler.type is None:  # bare `except:`
        return [], True

    def _resolve(node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return "<unknown>"

    if isinstance(handler.type, ast.Tuple):
        names = [_resolve(elt) for elt in handler.type.elts]
    else:
        names = [_resolve(handler.type)]

    catches_broad = any(n in ("Exception", "BaseException") for n in names)
    return names, catches_broad


def _handler_body_raises_bare_or_http404(handler: ast.ExceptHandler) -> bool:
    """Return True if the handler's body raises Http404 (bare re-raise counts)."""
    for stmt in handler.body:
        if isinstance(stmt, ast.Raise):
            if stmt.exc is None:  # bare `raise`
                return True
            if isinstance(stmt.exc, ast.Name) and stmt.exc.id == "Http404":
                return True
            if isinstance(stmt.exc, ast.Call) and isinstance(stmt.exc.func, ast.Name):
                if stmt.exc.func.id == "Http404":
                    return True
    return False


def _enclosing_fqname(try_node: ast.Try, parents: dict[int, ast.AST]) -> str:
    """Walk parent chain to build a qualified name like `ClassName.method_name`."""
    parts: list[str] = []
    current: ast.AST | None = parents.get(id(try_node))
    while current is not None:
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            parts.append(current.name)
        current = parents.get(id(current))
    return ".".join(reversed(parts)) if parts else "<module>"


def _build_parent_map(tree: ast.Module) -> dict[int, ast.AST]:
    parents: dict[int, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[id(child)] = parent
    return parents


def _first_g404_call_line(try_node: ast.Try, aliases: set[str]) -> int | None:
    for stmt in try_node.body:
        for descendant in ast.walk(stmt):
            if isinstance(descendant, ast.Call) and _call_is_g404(descendant, aliases):
                return descendant.lineno
    return None


def _snippet(source_lines: list[str], try_line: int) -> list[str]:
    """Return up to 3 lines of context around the try line (1-indexed)."""
    start = max(0, try_line - 1)
    end = min(len(source_lines), try_line + 2)
    return [source_lines[i].rstrip("\n") for i in range(start, end)]


def _inspect_file(path: Path) -> tuple[list[dict], list[dict]]:
    """Return (violations, info_rows) for a single file."""
    try:
        source = path.read_text(encoding="utf-8")
    except OSError:
        return [], []

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return [], []

    aliases = _collect_g404_aliases(tree)
    parents = _build_parent_map(tree)
    source_lines = source.splitlines()
    rel_path = path.relative_to(REPO_ROOT).as_posix()

    violations: list[dict] = []
    info_rows: list[dict] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        if not _try_body_calls_g404(node, aliases):
            continue

        # Walk handlers in order to determine guard vs broad
        broad_handler: ast.ExceptHandler | None = None
        http404_guard_present = False
        http404_intentional_handler: ast.ExceptHandler | None = None

        for handler in node.handlers:
            names, catches_broad = _handler_type_names(handler)
            if broad_handler is None and catches_broad:
                broad_handler = handler
            catches_http404_specifically = "Http404" in names and not catches_broad
            if catches_http404_specifically:
                if _handler_body_raises_bare_or_http404(handler):
                    if broad_handler is None:
                        http404_guard_present = True
                else:
                    http404_intentional_handler = handler

        if broad_handler is not None and not http404_guard_present:
            call_line = _first_g404_call_line(node, aliases)
            violations.append(
                {
                    "file": rel_path,
                    "try_line": node.lineno,
                    "call_line": call_line,
                    "broad_handler_line": broad_handler.lineno,
                    "enclosing": _enclosing_fqname(node, parents),
                    "snippet": _snippet(source_lines, node.lineno),
                    "fix_hint": (
                        f"insert 'except Http404: raise' before line "
                        f"{broad_handler.lineno}"
                    ),
                }
            )
        elif http404_intentional_handler is not None:
            info_rows.append(
                {
                    "file": rel_path,
                    "try_line": node.lineno,
                    "handler_line": http404_intentional_handler.lineno,
                    "reason": (
                        "Http404 handler present but body does not raise "
                        "(custom 404 response) — informational"
                    ),
                }
            )

    return violations, info_rows


# --------------------------------------------------------------------------
# Report writer
# --------------------------------------------------------------------------


def _write_report(payload: dict) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True))


def _head_sha() -> str:
    """Best-effort HEAD sha for report provenance; falls back to 'unknown'."""
    try:
        head_file = REPO_ROOT / ".git" / "HEAD"
        head_ref = head_file.read_text().strip()
        if head_ref.startswith("ref: "):
            ref_path = REPO_ROOT / ".git" / head_ref[5:]
            return ref_path.read_text().strip()[:12]
        return head_ref[:12]
    except OSError:
        return "unknown"


# --------------------------------------------------------------------------
# Pytest tests
# --------------------------------------------------------------------------


def test_http404_swallow_pattern_scan() -> None:
    """Scan Django view files for the Http404-swallow anti-pattern.

    Report-only by default (ENFORCE_HTTP404_SWALLOW = False):
      - Emits JSON report at test_reports/i0302_p4_ast_conformance.json
      - Warns per violation via warnings.warn
      - Passes with exit code 0 regardless of violation count

    Enforcing (ENFORCE_HTTP404_SWALLOW = True):
      - Same report + warnings
      - pytest.fail with structured summary if any violations
    """
    files = _discover_view_files()
    all_violations: list[dict] = []
    all_info_rows: list[dict] = []

    for path in files:
        violations, info_rows = _inspect_file(path)
        all_violations.extend(violations)
        all_info_rows.extend(info_rows)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "head_sha": _head_sha(),
        "rule_id": "i0302-p4-http404-swallow",
        "mode": "enforcing" if ENFORCE_HTTP404_SWALLOW else "report-only",
        "scan_scope": {
            "included_globs": list(INCLUDED_GLOBS),
            "excluded_substrings": list(EXCLUDED_SUBSTRINGS),
            "files_scanned": len(files),
        },
        "violations": all_violations,
        "info_rows": all_info_rows,
        "summary": {
            "violations_total": len(all_violations),
            "info_rows_total": len(all_info_rows),
            "files_with_violations": len({v["file"] for v in all_violations}),
        },
    }
    _write_report(payload)

    for v in all_violations:
        line = (
            f"[HTTP404-SWALLOW] {v['file']}:{v['try_line']} in {v['enclosing']} — "
            f"{v['fix_hint']}"
        )
        print(line)
        warnings.warn(line, stacklevel=1)

    if ENFORCE_HTTP404_SWALLOW and all_violations:
        preview = "\n".join(
            f"  {v['file']}:{v['try_line']} in {v['enclosing']} — {v['fix_hint']}"
            for v in all_violations[:5]
        )
        pytest.fail(
            f"Http404-swallow violations: {len(all_violations)} across "
            f"{payload['summary']['files_with_violations']} files.\n"
            f"Report: {REPORT_PATH}\n"
            f"First 5:\n{preview}"
        )


def test_report_file_written_and_shape_ok() -> None:
    """Confirm the JSON report was written on the previous test and shape is valid."""
    assert REPORT_PATH.exists(), (
        f"Expected report at {REPORT_PATH}. Run the swallow scan test first."
    )
    payload = json.loads(REPORT_PATH.read_text())
    assert payload["rule_id"] == "i0302-p4-http404-swallow"
    assert "violations" in payload
    assert "info_rows" in payload
    assert "summary" in payload
    assert payload["summary"]["violations_total"] == len(payload["violations"])
    assert payload["summary"]["info_rows_total"] == len(payload["info_rows"])


def test_no_false_positive_on_fixed_deliverable_sites() -> None:
    """The 5 §5.1.b sites (delete/link/record/unsave/templateize + get) should NOT
    appear as violations post-hotfix — they all have `except Http404: raise` guards.

    If any of them appears in violations, the guard-detection logic has a bug.
    """
    payload = json.loads(REPORT_PATH.read_text()) if REPORT_PATH.exists() else None
    if payload is None:
        pytest.skip("Report not written yet — run the scan test first.")

    fixed_sites = {
        "get_deliverable",
        "delete_deliverable",
        "link_deliverable_workspace",
        "record_deliverable_event",
        "unsave_deliverable",
        "templateize_deliverable",
    }
    offending = [
        v
        for v in payload["violations"]
        if v["file"] == "core/views_deliverables.py"
        and v["enclosing"] in fixed_sites
    ]
    assert not offending, (
        f"§5.1.b fixed sites should not appear as violations post-hotfix; "
        f"guard-detection bug suspected. Offenders: "
        f"{[(v['enclosing'], v['try_line']) for v in offending]}"
    )
