"""
core.security.decorators — view-layer authorization decorators.

Ratified via I-0302 Phase 3 Sub-phase B2b (2026-07-10) — Rigby SIGN Q1
'gate should be authentication-safe and consistent': all ops surfaces
(views_diagnostics, views_integration_health, views_celery_api) uniformly
gate anonymous → 401, authenticated-non-superuser → 403, superuser →
proceed. Predicate module (`object_authz`) still runs inside the gate for
defense-in-depth (superuser sees own + null-user Celery runs per Session 642).

**Import contract:** this module MAY import Django's HTTP layer (JsonResponse
is view-adjacent, not view-internal). It MUST NOT import DRF, Celery, models,
or view files — same leaf-module discipline as `object_authz` per scoping §6.1.
"""
from __future__ import annotations

from functools import wraps
from typing import Callable

from django.http import JsonResponse


def superuser_required(view_func: Callable) -> Callable:
    """Reject anonymous callers with 401 and non-superusers with 403.

    Applied to ops/diagnostics surfaces in Sub-phase B2b to align endpoint
    access with the predicate module's superuser carve-out for null-user
    Celery system-context AgentExecution rows.

    Usage::

        @superuser_required
        def my_ops_endpoint(request):
            ...
    """

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        user = getattr(request, "user", None)
        if not getattr(user, "is_authenticated", False):
            return JsonResponse(
                {"success": False, "error": "Authentication required"},
                status=401,
            )
        if not getattr(user, "is_superuser", False):
            return JsonResponse(
                {"success": False, "error": "Superuser required"},
                status=403,
            )
        return view_func(request, *args, **kwargs)

    return _wrapped
