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

Usage:
    python scripts/lint_no_deprecated_family_b.py           # exit 1 on violations
    python scripts/lint_no_deprecated_family_b.py --list    # show tracked files
"""
from __future__ import annotations

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
    "core/auth_middleware.py",
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


def main(argv: list[str]) -> int:
    if "--list" in argv:
        print("T-ENVELOPE-2-DEPRECATION migrated files (zero-tolerance):")
        for f in MIGRATED_FILES:
            print(f"  {f}")
        return 0

    all_violations: list[str] = []
    for rel in MIGRATED_FILES:
        all_violations.extend(_check_file(REPO_ROOT / rel))

    if all_violations:
        print("❌ ADR-0007 Family B deprecation lint FAILED:", file=sys.stderr)
        for v in all_violations:
            print(f"  {v}", file=sys.stderr)
        print(
            "\nMigrated files MUST NOT use deprecated Family B error helpers or import them.",
            file=sys.stderr,
        )
        print(
            "Replace with `build_user_facing_envelope(reason_code=...)` per ADR-0007 §3.1.",
            file=sys.stderr,
        )
        return 1

    print(f"✅ ADR-0007 Family B deprecation lint OK ({len(MIGRATED_FILES)} files checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
