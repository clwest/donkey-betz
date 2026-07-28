#!/usr/bin/env python3
"""File-scoped zero-tolerance lint for ADR-0007 Family B error-helper deprecation.

ADR-0007 §4.2 obligates a lint gate preventing new usages of the deprecated
Family B error helpers (`APIResponseEnvelope.error` + adjacent + module-level
`api_error` / `api_unauthorized` / etc.) in files that have already been
migrated to Family E (`build_user_facing_envelope`, safety-contract §3.1).

Contract:
- MIGRATED_FILES lists paths that MUST NOT contain any deprecated helper
  usage or deprecated import.
- The list grows as T-ENVELOPE-2-DEPRECATION batches ship (append per batch).
- A file entering the list becomes zero-tolerance — CI fails if any match
  is found.

Scope explicitly excludes `core/api_helpers.py` (separate substrate; ADR-0007
§4.3 out-of-scope note). Also excludes `core/api_responses.py` itself
(definition site).

S3011 extension — str(e) body-leak detection (AST-based):
- Scans MIGRATED_FILES for `return JsonResponse(...)` / `return Response(...)`
  calls whose arguments include `str(e)` or an f-string with `{e}` / `{str(e)}`.
- These leak raw exception text to user-facing bodies (safety-contract §3.1).
- Existing leaks (pre-S3011) are grandfathered via STR_E_LEAK_GRANDFATHER;
  new leaks fail. Regenerate the grandfather set with `--regenerate-grandfather`
  when known leaks are drained.

Usage:
    python scripts/lint_no_deprecated_family_b.py                       # exit 1 on violations
    python scripts/lint_no_deprecated_family_b.py --list                # show tracked files
    python scripts/lint_no_deprecated_family_b.py --regenerate-grandfather  # print fresh set
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# T-ENVELOPE-2-DEPRECATION migrated file list. Append per batch as files
# complete Family B → Family E migration. Files listed here are locked
# zero-tolerance for the deprecated helpers below.
MIGRATED_FILES: tuple[str, ...] = (
    # Batch 1 (S3006, ADR-0007 §4.3)
    "core/views_odds_sports.py",
    "core/views_revenue_analytics.py",
    # Batch 2 (S3007, ADR-0007 §4.3) — 10 sites in auth middleware +
    # token_auth_required decorator (same file, file-scoped lint).
    # S3009 B1 completed the file to 0 raw-pattern sites (helper only).
    "core/auth_middleware.py",
    # Batch 3 (S3009, ADR-0007 §4.3) — 25 sites in auto-distribution views
    # (create/batch/reschedule/cancel/settings/apply_template). All sites
    # use emit_error_envelope() helper.
    "core/views_auto_distribution.py",
    # Batch 4 (S3010, ADR-0007 §4.3) — 62 sites in platform integrations
    # views (oauth_connect/callback/refresh + etsy/shutterstock/gumroad
    # CRUD + sync + disconnect). Split across PR A (16 auth-surface) +
    # PR B (46 platform-CRUD). All 62 sites use emit_error_envelope()
    # helper. gumroad_webhook (3 sites w/ raw JsonResponse) deferred
    # to S3011 pending verification of Gumroad webhook body-shape
    # sensitivity.
    "core/views_platform_integrations.py",
    # T-ENVELOPE-3 PR 1 (S3012, ADR-0007 §4.4) — 36 sites in A/B testing
    # views (~26 in dead-code A/B test handlers per Session 1103c dead-
    # code note + 10 in wired goals handlers). All 36 sites migrated to
    # emit_error_envelope(). Dead handlers retained pending follow-up
    # deletion PR (HALF_BUILT_FEATURES_AUDIT scope).
    "core/views_ab_testing.py",
)

# Deprecated helper usages (regex matched as function calls with open paren).
DEPRECATED_USAGES: tuple[str, ...] = (
    r"\bAPIResponseEnvelope\.error\s*\(",
    r"\bAPIResponseEnvelope\.unauthorized\s*\(",
    r"\bAPIResponseEnvelope\.forbidden\s*\(",
    r"\bAPIResponseEnvelope\.not_found\s*\(",
    r"\bAPIResponseEnvelope\.validation_error\s*\(",
    r"\bAPIResponseEnvelope\.rate_limited\s*\(",
    r"\bAPIResponseEnvelope\.server_error\s*\(",
    r"\bapi_error\s*\(",
    r"\bapi_unauthorized\s*\(",
    r"\bapi_forbidden\s*\(",
    r"\bapi_not_found\s*\(",
    r"\bapi_validation_error\s*\(",
)

# Deprecated import surface — even a dead import is a regression signal
# per Rigby A2 STRENGTHEN (S3006). Match `from core.api_responses import ...`
# lines where the import list contains any of the deprecated names.
DEPRECATED_IMPORT_NAMES: tuple[str, ...] = (
    "api_error",
    "api_unauthorized",
    "api_forbidden",
    "api_not_found",
    "api_validation_error",
    # APIResponseEnvelope class itself is NOT banned (still needed for
    # success/paginated methods per ADR-0007 §3.2).
)

_USAGE_RE = re.compile("|".join(DEPRECATED_USAGES))
_IMPORT_RE = re.compile(
    r"^\s*from\s+core\.api_responses\s+import\s+(.+?)$",
    re.MULTILINE,
)


# S3011: grandfather list of pre-existing str(e) body-leak sites in MIGRATED_FILES.
# Each tuple = (relative_path, lineno). New leaks not in this set fail the lint;
# existing leaks are cataloged as tech debt to be drained by a follow-up arc
# (e.g., "sports odds leak drain" — Rigby S3011 B2 A1 zoom-out).
#
# When a leak is fixed, remove its entry from this set. To regenerate after
# significant churn, run: python scripts/lint_no_deprecated_family_b.py --regenerate-grandfather
STR_E_LEAK_GRANDFATHER: frozenset[tuple[str, int]] = frozenset({
    # core/views_odds_sports.py — 32 sites (S3006 Batch 1 file; DRF Response
    # error paths not migrated in that batch — surfaced by S3011 B2 discovery)
    ("core/views_odds_sports.py", 378),
    ("core/views_odds_sports.py", 509),
    ("core/views_odds_sports.py", 924),
    ("core/views_odds_sports.py", 1035),
    ("core/views_odds_sports.py", 1081),
    ("core/views_odds_sports.py", 1118),
    ("core/views_odds_sports.py", 1158),
    ("core/views_odds_sports.py", 1282),
    ("core/views_odds_sports.py", 1361),
    ("core/views_odds_sports.py", 1508),
    ("core/views_odds_sports.py", 1575),
    ("core/views_odds_sports.py", 1739),
    ("core/views_odds_sports.py", 1877),
    ("core/views_odds_sports.py", 1883),
    ("core/views_odds_sports.py", 1953),
    ("core/views_odds_sports.py", 1958),
    ("core/views_odds_sports.py", 2064),
    ("core/views_odds_sports.py", 2208),
    ("core/views_odds_sports.py", 2307),
    ("core/views_odds_sports.py", 2418),
    ("core/views_odds_sports.py", 2426),
    ("core/views_odds_sports.py", 2627),
    ("core/views_odds_sports.py", 2696),
    ("core/views_odds_sports.py", 2755),
    ("core/views_odds_sports.py", 2807),
    ("core/views_odds_sports.py", 2939),
    ("core/views_odds_sports.py", 3018),
    ("core/views_odds_sports.py", 3247),
    ("core/views_odds_sports.py", 3280),
    ("core/views_odds_sports.py", 3327),
    ("core/views_odds_sports.py", 3536),
    ("core/views_odds_sports.py", 3604),
})


def _is_str_of_e(node: ast.AST) -> bool:
    """Match `str(e)` where `e` is a bare Name."""
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "str"
        and len(node.args) == 1
        and isinstance(node.args[0], ast.Name)
        and node.args[0].id == "e"
    )


def _call_has_leak(call_node: ast.Call) -> bool:
    """True if any nested node in call args is `str(e)` or an f-string with `{e}` / `{str(e)}`."""
    for n in ast.walk(call_node):
        if _is_str_of_e(n):
            return True
        if isinstance(n, ast.JoinedStr):
            for val in n.values:
                if isinstance(val, ast.FormattedValue):
                    expr = val.value
                    if isinstance(expr, ast.Name) and expr.id == "e":
                        return True
                    if _is_str_of_e(expr):
                        return True
    return False


def _call_fn_name(call: ast.Call) -> str | None:
    fn = call.func
    if isinstance(fn, ast.Name):
        return fn.id
    if isinstance(fn, ast.Attribute):
        return fn.attr
    return None


def _scan_str_e_leaks(path: Path, rel: str) -> list[tuple[str, int]]:
    """Return list of (rel_path, lineno) tuples for str(e) leaks in return JsonResponse/Response calls."""
    try:
        tree = ast.parse(path.read_text())
    except (FileNotFoundError, SyntaxError):
        return []

    leaks: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Call):
            call = node.value
            fn_name = _call_fn_name(call)
            if fn_name in ("JsonResponse", "Response") and _call_has_leak(call):
                leaks.append((rel, node.lineno))
    return sorted(leaks)


def _check_file(path: Path) -> list[str]:
    """Return list of violation strings for a single file."""
    violations: list[str] = []
    try:
        text = path.read_text()
    except FileNotFoundError:
        violations.append(f"{path}: MIGRATED_FILES entry not found on disk")
        return violations

    for lineno, line in enumerate(text.splitlines(), start=1):
        if _USAGE_RE.search(line):
            violations.append(f"{path}:{lineno}: deprecated helper usage → {line.strip()}")

    for match in _IMPORT_RE.finditer(text):
        import_list = match.group(1)
        for banned in DEPRECATED_IMPORT_NAMES:
            if re.search(rf"\b{banned}\b", import_list):
                lineno = text[: match.start()].count("\n") + 1
                violations.append(
                    f"{path}:{lineno}: deprecated import of `{banned}` from core.api_responses"
                )

    return violations


def _check_str_e_leaks() -> tuple[list[str], list[tuple[str, int]]]:
    """Scan MIGRATED_FILES for str(e) body leaks. Return (new_violations, stale_grandfather_entries)."""
    all_leaks: list[tuple[str, int]] = []
    for rel in MIGRATED_FILES:
        all_leaks.extend(_scan_str_e_leaks(REPO_ROOT / rel, rel))

    detected = frozenset(all_leaks)
    new_leaks = detected - STR_E_LEAK_GRANDFATHER
    stale_grandfather = sorted(STR_E_LEAK_GRANDFATHER - detected)

    new_violations = [
        f"{rel}:{lineno}: str(e) body-leak in return JsonResponse/Response call"
        for rel, lineno in sorted(new_leaks)
    ]
    return new_violations, stale_grandfather


def _regenerate_grandfather() -> int:
    """Print a fresh STR_E_LEAK_GRANDFATHER set from current scan; copy-paste into the lint file."""
    all_leaks: list[tuple[str, int]] = []
    for rel in MIGRATED_FILES:
        all_leaks.extend(_scan_str_e_leaks(REPO_ROOT / rel, rel))

    by_file: dict[str, list[int]] = {}
    for rel, lineno in sorted(all_leaks):
        by_file.setdefault(rel, []).append(lineno)

    print("# Regenerated STR_E_LEAK_GRANDFATHER (paste into scripts/lint_no_deprecated_family_b.py):")
    print("STR_E_LEAK_GRANDFATHER: frozenset[tuple[str, int]] = frozenset({")
    for rel, linenos in by_file.items():
        print(f"    # {rel} — {len(linenos)} sites")
        for ln in linenos:
            print(f'    ("{rel}", {ln}),')
    print("})")
    return 0


def main(argv: list[str]) -> int:
    if "--list" in argv:
        print("T-ENVELOPE-2-DEPRECATION migrated files (zero-tolerance):")
        for f in MIGRATED_FILES:
            print(f"  {f}")
        return 0

    if "--regenerate-grandfather" in argv:
        return _regenerate_grandfather()

    all_violations: list[str] = []
    for rel in MIGRATED_FILES:
        all_violations.extend(_check_file(REPO_ROOT / rel))

    str_e_violations, stale_grandfather = _check_str_e_leaks()
    all_violations.extend(str_e_violations)

    if all_violations:
        print("❌ ADR-0007 Family B deprecation lint FAILED:", file=sys.stderr)
        for v in all_violations:
            print(f"  {v}", file=sys.stderr)
        print(
            "\nMigrated files MUST NOT use deprecated Family B error helpers or import them.",
            file=sys.stderr,
        )
        print(
            "Replace with `emit_error_envelope(reason_code=..., request=request, hint=...)`\n"
            "(wrapper over `build_user_facing_envelope`) per ADR-0007 §3.1.",
            file=sys.stderr,
        )
        if str_e_violations:
            print(
                "\nstr(e) body-leaks: replace `return JsonResponse/Response({..., 'error': str(e), ...})`\n"
                "with `emit_error_envelope(reason_code='internal_error', request=request, hint=...)`\n"
                "per ADR-0007 safety-contract §3.1. Log exception via `logger.exception(...)` for\n"
                "operator diagnosis; user body should carry no raw exception text.",
                file=sys.stderr,
            )
        return 1

    msg = f"✅ ADR-0007 Family B deprecation lint OK ({len(MIGRATED_FILES)} files checked"
    msg += f", {len(STR_E_LEAK_GRANDFATHER)} grandfathered str(e) leaks"
    if stale_grandfather:
        msg += f", {len(stale_grandfather)} stale grandfather entries (safe to remove)"
    msg += ")"
    print(msg)
    if stale_grandfather:
        print("\nStale grandfather entries (leak has been fixed — remove from set):")
        for rel, lineno in stale_grandfather:
            print(f"  {rel}:{lineno}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
