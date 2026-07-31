"""S3052 PR 4 — role-gate primitives for RaaS UI Phase 2 Gap 6.

Covers:
- `IsOperatorRole` DRF permission class (customer / operator / anonymous / staff)
- `require_operator_role` plain-Django decorator (customer / operator / anonymous)
- `all_agents_list` endpoint gated end-to-end (200 for operator, 403 for reviewer)
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
import json

from django.test import Client, RequestFactory, TestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from core.permissions_role import (
    CUSTOMER_PLATFORM_ROLES,
    OPERATOR_PLATFORM_ROLES,
    IsOperatorRole,
    require_operator_role,
)

User = get_user_model()


class TestIsOperatorRoleDRF(TestCase):
    """DRF BasePermission subclass gates only customer-role users."""

    def setUp(self) -> None:  # noqa: D401
        self.permission = IsOperatorRole()
        self.factory = APIRequestFactory()

    def _drf_request_for(self, user):
        raw = self.factory.get("/anywhere/")
        request = Request(raw)
        request.user = user  # type: ignore[assignment]
        return request

    def test_operator_role_allowed(self) -> None:
        for role in sorted(OPERATOR_PLATFORM_ROLES):
            user = User.objects.create_user(
                username=f"op_{role}", password="x", platform_role=role
            )
            self.assertTrue(
                self.permission.has_permission(self._drf_request_for(user), view=None),
                f"operator role {role!r} should pass IsOperatorRole",
            )

    def test_customer_role_denied(self) -> None:
        for role in sorted(CUSTOMER_PLATFORM_ROLES):
            user = User.objects.create_user(
                username=f"cust_{role}", password="x", platform_role=role
            )
            self.assertFalse(
                self.permission.has_permission(self._drf_request_for(user), view=None),
                f"customer role {role!r} should be blocked by IsOperatorRole",
            )

    def test_anonymous_denied(self) -> None:
        from django.contrib.auth.models import AnonymousUser

        request = self._drf_request_for(AnonymousUser())
        self.assertFalse(self.permission.has_permission(request, view=None))

    def test_unknown_role_denied(self) -> None:
        user = User.objects.create_user(username="unknown_role", password="x")
        user.platform_role = "totally_made_up"  # bypass field choices for the test
        self.assertFalse(
            self.permission.has_permission(self._drf_request_for(user), view=None)
        )


class TestRequireOperatorRoleDecorator(TestCase):
    """`require_operator_role` gates plain Django views the same way."""

    def setUp(self) -> None:  # noqa: D401
        self.factory = RequestFactory()

        @require_operator_role
        def probe(_request):
            from django.http import JsonResponse
            return JsonResponse({"ok": True})

        self.probe = probe

    def test_operator_passes_through(self) -> None:
        user = User.objects.create_user(
            username="op", password="x", platform_role="unified_user"
        )
        request = self.factory.get("/probe/")
        request.user = user  # type: ignore[assignment]
        resp = self.probe(request)
        self.assertEqual(resp.status_code, 200)

    def test_customer_returns_403(self) -> None:
        user = User.objects.create_user(
            username="rev", password="x", platform_role="reviewer"
        )
        request = self.factory.get("/probe/")
        request.user = user  # type: ignore[assignment]
        resp = self.probe(request)
        self.assertEqual(resp.status_code, 403)
        body = json.loads(resp.content)
        self.assertEqual(body["error_code"], "operator_role_required")

    def test_anonymous_returns_403(self) -> None:
        from django.contrib.auth.models import AnonymousUser

        request = self.factory.get("/probe/")
        request.user = AnonymousUser()  # type: ignore[assignment]
        resp = self.probe(request)
        self.assertEqual(resp.status_code, 403)


class TestOperatorGatedAgentEndpoints(TestCase):
    """MVP-scope `/api/agents/*` endpoints all return 200 for operator, 403 for reviewer.

    Rigby A2 SIGN Dim (ii) NEEDS COVERAGE fold: `all_agents_list` alone
    doesn't close the class — `agents_assigned` (DRF) and `get_agent_profile`
    (plain-Django) are adjacent operator surfaces on the same `/api/agents/*`
    boundary and MUST be gated to fully close the drift-closure class.
    """

    def setUp(self) -> None:  # noqa: D401
        self.operator = User.objects.create_user(
            username="op_e2e", password="secret", platform_role="unified_user"
        )
        self.customer = User.objects.create_user(
            username="rev_e2e", password="secret", platform_role="reviewer"
        )
        self.op_client = Client()
        self.op_client.force_login(self.operator)
        self.cust_client = Client()
        self.cust_client.force_login(self.customer)

    def _assert_gated(self, path: str, method: str = "get") -> None:
        op_resp = getattr(self.op_client, method)(path)
        self.assertEqual(op_resp.status_code, 200, f"operator should reach {path}, got {op_resp.status_code}")
        cust_resp = getattr(self.cust_client, method)(path)
        self.assertEqual(cust_resp.status_code, 403, f"customer should be blocked from {path}, got {cust_resp.status_code}")

    def test_all_agents_list_gated(self) -> None:
        # /api/agents/ → all_agents_list (plain Django + require_operator_role)
        # Literal path — `agents-list` URL name is shadowed by later registration at
        # `/api/v1/agents/list/` (core/urls.py:3138).
        self._assert_gated("/api/agents/")

    def test_agents_assigned_gated(self) -> None:
        # /api/agents/assigned/ → agents_assigned (DRF @api_view + IsOperatorRole)
        self._assert_gated("/api/agents/assigned/")

    def test_agent_profile_gated(self) -> None:
        # /api/agents/<uuid>/profile/ → get_agent_profile (plain Django + require_operator_role).
        # Uses a nonexistent agent_id — the role gate runs before the DB lookup so
        # a 404 (from missing agent) proves the gate passed; a 403 proves the gate blocked.
        # Any real agent_id would work too, but we don't need one to prove the gate.
        import uuid as _uuid
        fake_id = _uuid.uuid4()
        path = f"/api/agents/{fake_id}/profile/"
        cust_resp = self.cust_client.get(path)
        self.assertEqual(cust_resp.status_code, 403)
        op_resp = self.op_client.get(path)
        # Operator gets past the role gate — actual response is 404 (or 200 if agent exists).
        # Only 403 would indicate the gate rejected them, which is what we're checking against.
        self.assertNotEqual(op_resp.status_code, 403)
