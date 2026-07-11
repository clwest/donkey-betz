"""
tests/security/test_i0302_p4_ops_aggregate_decorator.py — I-0302 Phase 4
smoke test for the `@ops_aggregate_allowed` decorator codified at Phase 4
open (2026-07-10, S2748).

Contract refs:
  docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md §11
  Rigby SIGN F3.1-F3.3 (pin `pa-59d27abadeed4411`)
  Chris D-verdict "agree all + ship bonus tightening" 2026-07-10 S2748

Coverage:
  1. Decorator is importable from the canonical path only.
  2. Decorator is a request-time no-op — request/response unchanged.
  3. Wrapped callable exposes `_ops_aggregate_allowed = True` (belt-and-
     suspenders marker; AST tree is still primary detection).
  4. `functools.wraps` preserves __name__ + __doc__ of the wrapped view.
  5. Stacking with `@superuser_required` composes cleanly (both markers
     survive; superuser gating remains intact — anonymous 401, non-super
     403, super proceeds).
"""
from __future__ import annotations

import uuid

import pytest
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory

from core.security.decorators import ops_aggregate_allowed, superuser_required

User = get_user_model()


@pytest.fixture
def rf():
    return RequestFactory()


@pytest.fixture
def anon_user():
    from django.contrib.auth.models import AnonymousUser

    return AnonymousUser()


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        username=f"reg-{uuid.uuid4().hex[:6]}",
        email=f"r-{uuid.uuid4().hex[:6]}@example.com",
        password="pw",
    )


@pytest.fixture
def superuser(db):
    return User.objects.create_user(
        username=f"super-{uuid.uuid4().hex[:6]}",
        email=f"s-{uuid.uuid4().hex[:6]}@example.com",
        password="pw",
        is_superuser=True,
        is_staff=True,
    )


def test_ops_aggregate_allowed_importable_from_canonical_path():
    """§11.2 rule 2: single canonical import path."""
    from core.security import decorators

    assert decorators.ops_aggregate_allowed is ops_aggregate_allowed


def test_decorator_is_request_time_noop(rf, regular_user):
    """Decorator does not intercept requests — semantic gating is the view's job."""

    @ops_aggregate_allowed
    def my_view(request):
        return HttpResponse("ok", status=200)

    request = rf.get("/ops/aggregate/")
    request.user = regular_user
    response = my_view(request)

    assert response.status_code == 200
    assert response.content == b"ok"


def test_wrapped_function_exposes_marker_attribute():
    """§11.1 belt-and-suspenders attribute for defensive detection."""

    @ops_aggregate_allowed
    def my_view(request):
        return HttpResponse("ok")

    assert getattr(my_view, "_ops_aggregate_allowed", False) is True


def test_functools_wraps_preserves_metadata():
    """`@wraps` keeps __name__ / __doc__ intact so AST + introspection tools work."""

    @ops_aggregate_allowed
    def specifically_named_view(request):
        """The docstring should survive decoration."""
        return HttpResponse("ok")

    assert specifically_named_view.__name__ == "specifically_named_view"
    assert specifically_named_view.__doc__ == "The docstring should survive decoration."


def test_stack_with_superuser_required_anon_gets_401(rf, anon_user):
    """§11.4 composition: anonymous is rejected by superuser_required, ops_aggregate never runs."""

    @superuser_required
    @ops_aggregate_allowed
    def my_view(request):
        return HttpResponse("aggregate", status=200)

    request = rf.get("/ops/aggregate/")
    request.user = anon_user
    response = my_view(request)

    assert response.status_code == 401


def test_stack_with_superuser_required_non_super_gets_403(rf, regular_user):
    """§11.4 composition: authenticated non-superuser rejected before view runs."""

    @superuser_required
    @ops_aggregate_allowed
    def my_view(request):
        return HttpResponse("aggregate", status=200)

    request = rf.get("/ops/aggregate/")
    request.user = regular_user
    response = my_view(request)

    assert response.status_code == 403


def test_stack_with_superuser_required_super_reaches_view(rf, superuser):
    """§11.4 composition: superuser proceeds; ops_aggregate marker still present."""

    @superuser_required
    @ops_aggregate_allowed
    def my_view(request):
        return HttpResponse("aggregate", status=200)

    request = rf.get("/ops/aggregate/")
    request.user = superuser
    response = my_view(request)

    assert response.status_code == 200
    assert response.content == b"aggregate"
    assert getattr(my_view, "_ops_aggregate_allowed", False) is True


def test_reversed_stack_ordering_preserves_auth_and_marker(rf, anon_user, regular_user, superuser):
    """§11.1 ordering not semantically significant.

    Rigby SIGN-WITH-EDITS Q3 (2026-07-10): verify that placing
    @ops_aggregate_allowed OUTER and @superuser_required INNER still yields
    the same three-role auth posture (anon 401, non-super 403, super 200)
    AND that the marker attribute survives.
    """

    @ops_aggregate_allowed
    @superuser_required
    def my_view(request):
        return HttpResponse("aggregate", status=200)

    assert getattr(my_view, "_ops_aggregate_allowed", False) is True

    anon_request = rf.get("/ops/aggregate/")
    anon_request.user = anon_user
    assert my_view(anon_request).status_code == 401

    reg_request = rf.get("/ops/aggregate/")
    reg_request.user = regular_user
    assert my_view(reg_request).status_code == 403

    super_request = rf.get("/ops/aggregate/")
    super_request.user = superuser
    super_response = my_view(super_request)
    assert super_response.status_code == 200
    assert super_response.content == b"aggregate"
