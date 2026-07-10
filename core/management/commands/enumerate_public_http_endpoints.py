"""
Enumerate every routed HTTP endpoint with its permission + authentication
classes for the I-0301 Phase 4 Coverage Denominator Machinery.

Contract ref:
    docs/research/implementation/tenant_boundary_lockdown/failure_data_safety_contract.md
    docs/research/implementation/tenant_boundary_lockdown/I-0301_scoping.md §5, §7.1

Purpose: prevent new AllowAny endpoints from silently entering the
codebase without a corresponding classification in
``tests/security/endpoints_covered.txt``. The snapshot at
``tests/security/http_endpoint_snapshot.json`` is the pinned truth;
``test_endpoint_drift.py`` diffs live enumeration against it.

Rigby S2742 Phase 4 SIGN amendments folded in:
    * Q1: emit ALL routes (not filtered) + include ``namespace`` +
      ``url_name`` for disambiguation
    * Q2: capture ``authentication_classes`` and ``throttle_classes`` so
      A2 (token+throttle-gated) classification can be verified from the
      snapshot alone
    * Q3 refinement: no policy decisions here; drift test owns that
    * Must-have 1: deterministic ordering by ``(url_pattern, namespace,
      url_name, view)`` — snapshot diffs must not flap across machines
    * Must-have 2: import-safe — reads resolver metadata only, does
      NOT execute view code
    * Must-have 3: captures DRF ViewSet router-generated routes
      including ``@action`` methods

Usage:

    python manage.py enumerate_public_http_endpoints
    python manage.py enumerate_public_http_endpoints --output snapshot.json

Output is deterministic JSON; safe to check in.

Exit codes:
- 0 — enumeration succeeded
- 1 — enumeration error (missing view import, etc.)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Optional

from django.core.management.base import BaseCommand
from django.urls import URLPattern, URLResolver, get_resolver

DEFAULT_OUTPUT_PATH = Path("tests/security/http_endpoint_snapshot.json")

# Routes we don't want in the security snapshot. These are Django built-in
# admin / debug / static routes that are configured via settings, not by
# our code, and are outside the safety-contract scope.
_EXCLUDED_URL_PREFIXES: tuple[str, ...] = (
    "admin/",
    "static/",
    "media/",
    "__debug__/",
)


def _classes_to_names(classes) -> list[str]:
    """Serialize a tuple/list of Python classes to dotted-path strings.

    Returns an empty list if ``classes`` is None or empty. Sorted for
    deterministic output.
    """
    if not classes:
        return []
    names: list[str] = []
    for cls in classes:
        # Instance vs class handling — DRF sometimes returns instances
        target = cls if isinstance(cls, type) else type(cls)
        module = getattr(target, "__module__", "") or ""
        qualname = getattr(target, "__qualname__", None) or getattr(
            target, "__name__", ""
        )
        names.append(f"{module}.{qualname}" if module else qualname)
    return sorted(names)


def _inspect_view_callback(callback) -> dict[str, Any]:
    """Extract permission_classes + authentication_classes + throttle_classes
    + view identity from a URLPattern callback.

    Import-safe: only reads attributes set at class-definition time.
    Does NOT instantiate the view or execute any handler.
    """
    result: dict[str, Any] = {
        "view": None,
        "permission_classes": [],
        "authentication_classes": [],
        "throttle_classes": [],
        "http_methods": [],
    }

    # Class-based views (DRF APIView, ViewSet, generic views) attach the
    # class to the callback function as ``cls`` (DRF) or ``view_class``
    # (Django's as_view).
    view_class = getattr(callback, "cls", None) or getattr(
        callback, "view_class", None
    )

    if view_class is not None:
        module = getattr(view_class, "__module__", "") or ""
        qualname = getattr(view_class, "__qualname__", None) or getattr(
            view_class, "__name__", ""
        )
        result["view"] = f"{module}:{qualname}" if module else qualname
        result["permission_classes"] = _classes_to_names(
            getattr(view_class, "permission_classes", None)
        )
        result["authentication_classes"] = _classes_to_names(
            getattr(view_class, "authentication_classes", None)
        )
        result["throttle_classes"] = _classes_to_names(
            getattr(view_class, "throttle_classes", None)
        )

        # For DRF, http_method_names lists supported methods
        http_methods = getattr(view_class, "http_method_names", None) or []
        # Filter to the actual HTTP verbs (drop 'options', 'head' unless
        # they are the only ones — keeping snapshot signal high)
        http_methods = [m.upper() for m in http_methods]
        result["http_methods"] = sorted(
            m for m in http_methods if m in {"GET", "POST", "PUT", "PATCH", "DELETE"}
        )
    else:
        # Function-based view or unknown callback shape.
        module = getattr(callback, "__module__", "") or ""
        qualname = getattr(callback, "__qualname__", None) or getattr(
            callback, "__name__", ""
        )
        result["view"] = f"{module}:{qualname}" if module else qualname
        # Function views may have @api_view + @permission_classes decorators
        # DRF attaches the resulting handlers to the callback; permission
        # classes can be reached via the wrapper's ``cls`` in some cases
        # but that's already covered above.
        # http_method_names is not attached to function views in general.
        result["http_methods"] = []

    return result


def _walk_urlpatterns(
    patterns,
    prefix: str = "",
    namespace: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Recursively walk urlpatterns; yield one dict per URLPattern."""
    endpoints: list[dict[str, Any]] = []

    for entry in patterns:
        if isinstance(entry, URLPattern):
            url_pattern = f"{prefix}{entry.pattern}"
            # Skip excluded prefixes (admin/debug/static)
            if any(
                url_pattern.startswith(excluded)
                for excluded in _EXCLUDED_URL_PREFIXES
            ):
                continue

            inspected = _inspect_view_callback(entry.callback)
            endpoints.append(
                {
                    "url_pattern": url_pattern,
                    "namespace": namespace or "",
                    "url_name": entry.name or "",
                    **inspected,
                }
            )

        elif isinstance(entry, URLResolver):
            # Recurse into included URLconfs
            nested_namespace: Optional[str]
            if entry.namespace:
                nested_namespace = (
                    f"{namespace}:{entry.namespace}" if namespace else entry.namespace
                )
            else:
                nested_namespace = namespace

            endpoints.extend(
                _walk_urlpatterns(
                    entry.url_patterns,
                    prefix=f"{prefix}{entry.pattern}",
                    namespace=nested_namespace,
                )
            )

    return endpoints


def enumerate_endpoints() -> list[dict[str, Any]]:
    """Enumerate all routed HTTP endpoints with permission + auth metadata.

    Return list is deterministically sorted by
    ``(url_pattern, namespace, url_name, view)`` per Rigby SIGN Must-have 1.
    """
    resolver = get_resolver()
    endpoints = _walk_urlpatterns(resolver.url_patterns)
    endpoints.sort(
        key=lambda e: (
            e["url_pattern"],
            e.get("namespace") or "",
            e.get("url_name") or "",
            e.get("view") or "",
        )
    )
    return endpoints


class Command(BaseCommand):
    help = (
        "Enumerate all routed HTTP endpoints with their permission + "
        "authentication metadata. Used by the I-0301 Phase 4 Coverage "
        "Denominator Machinery to detect drift. See file docstring."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default=None,
            help=(
                "Write output to this path as JSON. If omitted, prints to "
                "stdout."
            ),
        )
        parser.add_argument(
            "--pretty",
            action="store_true",
            help="Pretty-print JSON with indent=2 (default for --output).",
        )

    def handle(self, *args, **options):
        try:
            endpoints = enumerate_endpoints()
        except Exception as exc:
            self.stderr.write(
                self.style.ERROR(
                    f"Endpoint enumeration failed: {type(exc).__name__}: {exc}"
                )
            )
            sys.exit(1)

        payload = {"endpoint_count": len(endpoints), "endpoints": endpoints}

        indent = 2 if options.get("pretty") or options.get("output") else None
        serialized = json.dumps(payload, indent=indent, sort_keys=True)

        if options.get("output"):
            Path(options["output"]).write_text(serialized + "\n")
            self.stdout.write(
                f"Wrote {len(endpoints)} endpoints → {options['output']}"
            )
        else:
            self.stdout.write(serialized)
