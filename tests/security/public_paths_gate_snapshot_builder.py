"""S3018 (Fold A from S3017): PUBLIC_PATHS gate-status snapshot builder.

Ratified S3017 Fold A `1st trigger` (Rigby T1 SIGN zoom-out 5a): per-view
gating under a bare-prefix in `PUBLIC_PATHS` is *correct but brittle*.
One missed endpoint = another F-2/F-3-shape class bug. This module
snapshots the current gate status of every URL pattern under a
`PUBLIC_PATHS` bare-prefix so the invariant test catches new drift at PR
review time.

**Design (T0-ratified 2026-07-28 Rigby SIGN):**
- Variant B (snapshot-lock, not strict-must-gate). Adopting the audit
  backlog as-is is prohibitive (~700 currently-ungated views); the
  snapshot locks CURRENT STATE and forces visible diffs for any new
  under-prefix view or gate change.
- Marker attribute (`_auth_gate`) + `__wrapped__` unwrap traversal (both,
  not either/or) — robust to stacked decorators.
- DRF class-based views detected via `view_class.permission_classes`
  (labeled `drf:<classes>` in snapshot).
- MVP scope: `PUBLIC_PATHS` bare-prefix + `PUBLIC_PATHS_EXACT` (near-free
  coverage extension). `OPTIONAL_AUTH_PATHS` deferred (classification
  ambiguity per Rigby T0 §3).
- Excluded: `/admin/` (Django admin has its own auth stack), `/api-auth/`
  (DRF browsable auth).

**Known limitations of gate detection (documented — not fixed in MVP):**
- `@method_decorator(superuser_required)` on class methods is not caught
  by the marker traversal (the marker lives on the method, not on
  `.as_view()` output). Such views appear as `gate: none` even though
  they're properly gated. Fold-in candidate for a future arc.
- Inline `request.user.is_authenticated` checks inside view bodies are
  not detected. `gate: none` for those too.
- Custom auth decorators outside `token_auth_required` /
  `superuser_required` are unrecognized. Add markers to them + regen the
  snapshot.

Reason `gate: none` != "insecure": the snapshot captures the CURRENT state
of the codebase. Many `gate: none` views are legitimately public
(health, login, webhooks, read-only stats). The invariant is that the
count and identity of these views doesn't drift silently.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver

from core.auth_middleware import UnifiedTokenAuthenticationMiddleware


SNAPSHOT_PATH = Path(__file__).parent / "public_paths_gate_snapshot.json"


# Prefixes explicitly out of scope for the invariant (own auth stack).
_EXCLUDED_PREFIXES = ("/admin/", "/api-auth/")

# Max chain-walk depth (guards against pathological decorator chains).
_MAX_UNWRAP_DEPTH = 12


def _in_scope_public_prefixes() -> list[str]:
    """Return PUBLIC_PATHS + PUBLIC_PATHS_EXACT minus explicit exclusions,
    de-duplicated and sorted."""
    MW = UnifiedTokenAuthenticationMiddleware
    seen: set[str] = set()
    for prefix in list(MW.PUBLIC_PATHS) + list(MW.PUBLIC_PATHS_EXACT):
        if any(prefix.startswith(x) for x in _EXCLUDED_PREFIXES):
            continue
        seen.add(prefix)
    return sorted(seen)


def _walk_url_patterns(resolver: Any, prefix: str = "") -> Any:
    """Yield (path_str, callback, name) for every URLPattern in the tree."""
    for pat in resolver.url_patterns:
        if isinstance(pat, URLResolver):
            yield from _walk_url_patterns(pat, prefix + str(pat.pattern))
        elif isinstance(pat, URLPattern):
            yield prefix + str(pat.pattern), pat.callback, getattr(pat, "name", None)


def _normalize_path(path: str) -> str:
    """Normalize a URL pattern string to a `/`-prefixed lookup form.

    Strips leading `^` regex anchor. Leaves converters (`<uuid:id>`) intact
    since they only appear at match-time and are irrelevant for prefix
    matching against PUBLIC_PATHS.
    """
    p = path.lstrip("^")
    if not p.startswith("/"):
        p = "/" + p
    return p


def _detect_gate(view: Any) -> str:
    """Detect the auth gate on a view callable.

    Walks `__wrapped__` chain looking for `_auth_gate` marker (set by
    `token_auth_required` / `superuser_required`). Falls back to DRF
    `permission_classes` inspection on `view_class` for class-based views.
    Returns a stable string label used as the snapshot key.
    """
    # Marker + unwrap traversal (Rigby T0 §2).
    cur = view
    depth = 0
    while cur is not None and depth < _MAX_UNWRAP_DEPTH:
        marker = getattr(cur, "_auth_gate", None)
        if isinstance(marker, str) and marker:
            return f"decorator:{marker}"
        cur = getattr(cur, "__wrapped__", None)
        depth += 1

    # DRF class-based view detection.
    view_class = getattr(view, "view_class", None) or getattr(view, "cls", None)
    if view_class is not None:
        perms = getattr(view_class, "permission_classes", None)
        if perms:
            names = sorted({p.__name__ for p in perms})
            # AllowAny alone is functionally "no gate".
            non_public = [n for n in names if n != "AllowAny"]
            if non_public:
                return f"drf:{'+'.join(non_public)}"

    return "none"


def build_snapshot() -> dict[str, Any]:
    """Snapshot every in-scope URL pattern that matches a PUBLIC_PATHS
    bare-prefix. Deterministic (sorted keys) so diffs are review-friendly.
    """
    prefixes = _in_scope_public_prefixes()
    routes: dict[str, dict[str, Any]] = {}

    for raw_path, view, name in _walk_url_patterns(get_resolver()):
        normalized = _normalize_path(raw_path)
        # First matching prefix wins (deterministic if we iterate sorted).
        matched_prefix = next(
            (p for p in prefixes if normalized.startswith(p)),
            None,
        )
        if matched_prefix is None:
            continue

        view_class = getattr(view, "view_class", None) or getattr(view, "cls", None)
        module = view_class.__module__ if view_class is not None else getattr(view, "__module__", "")
        view_name = (
            view_class.__name__
            if view_class is not None
            else getattr(view, "__name__", str(view))
        )

        routes[normalized] = {
            "prefix": matched_prefix,
            "module": module,
            "view": view_name,
            "url_name": name or "",
            "gate": _detect_gate(view),
            "is_cbv": view_class is not None,
        }

    return {
        "schema_version": 1,
        "excluded_prefixes": list(_EXCLUDED_PREFIXES),
        "in_scope_prefixes_count": len(prefixes),
        "routes": dict(sorted(routes.items())),
    }


def read_snapshot() -> dict[str, Any]:
    """Read the checked-in snapshot from disk."""
    return json.loads(SNAPSHOT_PATH.read_text())


def write_snapshot(snapshot: dict[str, Any]) -> None:
    """Persist a snapshot (used by the regen management command)."""
    SNAPSHOT_PATH.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
