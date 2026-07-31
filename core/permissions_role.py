"""S3052 PR 4 — Role-based access primitives.

Discharges Gap 6 of the S3049 RaaS UI arc: pre-PR-4 the auth stack only
checked `isAuthenticated`, never `platform_role`. Any authenticated user
could reach any authenticated endpoint.

Two shapes exported so both DRF views and plain Django views can gate on
role without duplicating the predicate:

- `IsOperatorRole` — DRF `BasePermission`. Apply via
  `@permission_classes([IsOperatorRole])` on `@api_view` handlers or via
  `permission_classes = [IsOperatorRole]` on class-based views.
- `require_operator_role` — plain-Django view decorator. Returns 403 when
  the user is customer-role.

MVP taxonomy (Rigby T1 AGREE, Chris ratifying at PR envelope):
    reviewer  → customer surface
    admin | sports_analyst | content_creator | agent_manager |
    unified_user  → operator surface

The reviewer=customer treatment mirrors the existing
`frontend/src/components/layout/Sidebar.tsx:343` precedent. A first-class
`platform_role='customer'` value (or a dedicated field) is deferred to
Phase 3+ ACL work.
"""
from __future__ import annotations

from functools import wraps
from typing import Callable

from django.http import HttpRequest, JsonResponse
from rest_framework.permissions import BasePermission

CUSTOMER_PLATFORM_ROLES: frozenset[str] = frozenset({"reviewer"})
OPERATOR_PLATFORM_ROLES: frozenset[str] = frozenset(
    {"admin", "sports_analyst", "content_creator", "agent_manager", "unified_user"}
)


def _has_operator_role(user) -> bool:
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    role = getattr(user, "platform_role", None)
    return role in OPERATOR_PLATFORM_ROLES


class IsOperatorRole(BasePermission):
    """Reject requests from customer-role users on operator-only DRF endpoints.

    Combine with IsAuthenticated by listing both — this class does NOT imply
    authentication; it only checks the role once authentication succeeded.
    """

    message = "Operator role required — customer accounts cannot access this endpoint."

    def has_permission(self, request, view) -> bool:  # noqa: D401
        return _has_operator_role(getattr(request, "user", None))


def require_operator_role(view_func: Callable) -> Callable:
    """Decorator for plain Django views (`def view(request): ...`).

    Returns HTTP 403 with a structured JSON body when the caller is
    customer-role. Passes through unchanged when the caller is operator-role.
    """

    @wraps(view_func)
    def _wrapped(request: HttpRequest, *args, **kwargs):
        if not _has_operator_role(getattr(request, "user", None)):
            return JsonResponse(
                {
                    "detail": "Operator role required — customer accounts cannot access this endpoint.",
                    "error_code": "operator_role_required",
                },
                status=403,
            )
        return view_func(request, *args, **kwargs)

    return _wrapped
