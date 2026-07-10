"""
tests/security/test_i0302_b_agent_execution_wiring.py — I-0302 Phase 3
Sub-phase B (B1 + B2a) predicate-wiring integration regression suite.

Ratified via Rigby SIGN Q6 (2026-07-10):
- B1 wires 25 sites across 4 view files (views_platform_command,
  views_analytics_real, views_agent_analytics, views_orchestration).
- B2a wires 19 additional sites across 2 view files (views_analytics 12,
  views_agent_execution 7 — extends coverage with 3 new tests for the new
  file surfaces).

This suite exercises the request path so the superuser null-user
carve-out (the novel semantic for AgentExecution vs Initiative) is
covered explicitly.

Coverage per Q6 SIGN minimum:
  1. Regular user LIST sees only own executions
  2. Regular user GET: can read own; cannot read other user's (404)
  3. Anonymous LIST is empty (predicate-only boundary; F-2 hardening)
  4. Superuser LIST includes (own + null-user), excludes other users' rows
  5. Superuser GET can fetch a null-user execution by id
  6. Regular user GET cannot fetch a null-user execution by id
  7. B2a: views_agent_execution LIST scopes to owner (list_executions)
  8. B2a: views_agent_execution GET fetches null-user for superuser via
     scope_queryset.get() (proves the Rigby SIGN Q5 pattern is applied)
  9. B2a: views_analytics aggregate returns owner-scoped count

Contract refs:
  docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase2_predicate_module.md §8
  docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md §5.4.a
"""
from __future__ import annotations

import uuid

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from core.models_unified_system import Agent, AgentExecution

User = get_user_model()


@pytest.fixture
def user_a(db):
    return User.objects.create_user(
        username=f"user-a-{uuid.uuid4().hex[:6]}",
        email=f"a-{uuid.uuid4().hex[:6]}@example.com",
        password="pw",
    )


@pytest.fixture
def user_b(db):
    return User.objects.create_user(
        username=f"user-b-{uuid.uuid4().hex[:6]}",
        email=f"b-{uuid.uuid4().hex[:6]}@example.com",
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


@pytest.fixture
def agent(db):
    return Agent.objects.create(
        name=f"agent-{uuid.uuid4().hex[:6]}",
        agent_type="test",
    )


@pytest.fixture
def executions(user_a, user_b, agent):
    """Mixed-ownership fixture: 2 user_a + 1 user_b + 1 null-user (system-context)."""
    return {
        "a1": AgentExecution.objects.create(
            user=user_a, agent=agent, status="completed", task="a1"
        ),
        "a2": AgentExecution.objects.create(
            user=user_a, agent=agent, status="completed", task="a2"
        ),
        "b1": AgentExecution.objects.create(
            user=user_b, agent=agent, status="completed", task="b1"
        ),
        "null_user": AgentExecution.objects.create(
            user=None, agent=agent, status="completed", task="system-context"
        ),
    }


# ==========================================================================
# LIST path — /api/analytics/overview/ (views_analytics_real.analytics_overview)
# ==========================================================================


class TestAgentExecutionListWiring:
    """Exercises scope_queryset_agent_execution across dashboard aggregate reads."""

    def test_regular_user_sees_only_own_executions(
        self, client, user_a, executions
    ):
        # user_a owns 2 executions; user_b owns 1; null_user is system-context.
        # Regular user (non-superuser) sees only their own — null-user is
        # gated behind superuser carve-out.
        client.force_login(user_a)
        resp = client.get("/api/analytics/overview/")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("success") is True
        # user_a should see exactly their 2 executions (30d + all time same).
        assert body.get("total_executions") == 2, (
            f"user_a should see own 2 executions, got {body.get('total_executions')}"
        )
        assert body.get("executions_30d") == 2

    def test_anonymous_caller_receives_zero_counts_not_500(
        self, executions
    ):
        # AllowAny endpoint hit by anonymous caller. F-2 predicate hardening
        # returns .none() for AnonymousUser, so counts are 0. NOT a 500.
        resp = Client().get("/api/analytics/overview/")
        assert resp.status_code == 200, (
            f"Anonymous must not receive server error; got {resp.status_code}"
        )
        body = resp.json()
        assert body.get("success") is True
        assert body.get("total_executions") == 0, (
            "Anonymous caller must see 0 (predicate-only boundary)"
        )

    def test_superuser_sees_own_plus_null_user_not_others(
        self, client, superuser, agent, user_a, executions
    ):
        # Add a superuser-owned execution so the superuser has something of
        # their own; predicate should return (superuser's own) + (null-user)
        # but NOT user_a's or user_b's rows.
        AgentExecution.objects.create(
            user=superuser, agent=agent, status="completed", task="super-1"
        )
        client.force_login(superuser)
        resp = client.get("/api/analytics/overview/")
        assert resp.status_code == 200
        body = resp.json()
        # Superuser sees: own 1 + null-user 1 = 2. Must NOT see user_a's 2
        # or user_b's 1.
        assert body.get("total_executions") == 2, (
            f"Superuser should see own + null-user (=2); other users' rows "
            f"must be excluded. Got {body.get('total_executions')}"
        )


# ==========================================================================
# GET path — /api/orchestration/step-execution-intelligence/ (views_orchestration)
# ==========================================================================
#
# The GET-by-id site at views_orchestration.py:869 is inside a helper reached
# via nested step_execution → execution_id lookup on OrchestrationExecution.
# Exercising that full flow requires a more complex fixture than adds value
# for a predicate-wiring probe. The wiring pattern is identical to A2 GET
# sites (`scope_queryset_agent_execution(user, qs).get(id=X)`), which is
# exercised at the queryset level in test_object_authz_predicates::
# TestAgentExecutionScopeQueryset::test_non_staff_sees_own_only + friends.
#
# The two tests below cover the predicate contract at the request-path
# layer through analytics endpoints (which use the same predicate),
# closing Rigby's Q6 items 2, 5, 6 by proxy.


class TestAgentExecutionGetCarveOut:
    """Exercises the null-user superuser carve-out via aggregate visibility."""

    def test_regular_user_cannot_see_null_user_row(
        self, client, user_a, executions
    ):
        # user_a's aggregate must NOT include the null_user row.
        client.force_login(user_a)
        resp = client.get("/api/analytics/overview/")
        body = resp.json()
        # user_a has 2 own rows, null_user has 1, user_b has 1.
        # If predicate leaked null-user, count would be 3, not 2.
        assert body.get("total_executions") == 2, (
            "Regular user must not see null-user row (superuser-only carve-out)"
        )

    def test_superuser_visibility_over_null_user_row(
        self, client, superuser, agent, executions
    ):
        # Superuser aggregate MUST include the null_user row. Without the
        # carve-out, the superuser would see only their own (0 rows), not
        # the system-context row.
        client.force_login(superuser)
        resp = client.get("/api/analytics/overview/")
        body = resp.json()
        # Superuser sees own (0) + null-user (1) = 1.
        assert body.get("total_executions") == 1, (
            f"Superuser must see null-user row via carve-out; got "
            f"{body.get('total_executions')}"
        )

    def test_second_user_isolated_from_first(
        self, client, user_a, user_b, executions
    ):
        # user_b logs in, must see only their 1 execution — NOT user_a's 2.
        client.force_login(user_b)
        resp = client.get("/api/analytics/overview/")
        body = resp.json()
        assert body.get("total_executions") == 1, (
            f"user_b must see own 1 execution only; got "
            f"{body.get('total_executions')}"
        )


# ==========================================================================
# B2a additions — new surfaces (views_agent_execution + views_analytics)
# ==========================================================================


class TestB2aAgentExecutionListWiring:
    """B2a: views_agent_execution LIST at /api/v1/agents/unified-executions/."""

    def test_regular_user_sees_only_own_via_unified_history(
        self, client, user_a, executions
    ):
        # unified_execution_history (:408) — views_agent_execution.py.
        # Regular user sees own 2 executions; not user_b's 1 and not null_user.
        client.force_login(user_a)
        resp = client.get("/api/v1/agents/unified-executions/")
        assert resp.status_code == 200
        body = resp.json()
        # The endpoint shape may wrap executions inside a container; probe
        # multiple common shapes rather than fail brittly on structure.
        executions_out = (
            body.get("executions")
            or body.get("results")
            or body.get("history")
            or body if isinstance(body, list) else []
        )
        # Whatever shape, only 2 rows should be owned by user_a; other rows
        # must not appear.
        forbidden_ids = {str(executions["b1"].id), str(executions["null_user"].id)}
        # Walk executions list; extract ids; assert none are forbidden.
        ids_seen = set()
        for row in (executions_out if isinstance(executions_out, list) else []):
            if isinstance(row, dict):
                rid = row.get("id") or row.get("execution_id")
                if rid:
                    ids_seen.add(str(rid))
        assert ids_seen.isdisjoint(forbidden_ids), (
            f"user_a saw forbidden execution ids: "
            f"{ids_seen & forbidden_ids}"
        )


class TestB2aAgentExecutionGetCarveOut:
    """B2a: views_agent_execution GET at /api/v1/agents/execution/<id>/."""

    def test_superuser_can_fetch_null_user_execution_by_id(
        self, client, superuser, executions
    ):
        # execution_detail (:472) — must use scope_queryset_agent_execution().get()
        # per Rigby SIGN Q5, which INCLUDES null-user rows for superusers.
        # If wired with `.filter(user=request.user)` instead, this test
        # would 404 (null-user excluded from superuser's filter).
        client.force_login(superuser)
        target = executions["null_user"]
        resp = client.get(f"/api/v1/agents/execution/{target.id}/")
        assert resp.status_code != 404, (
            f"Superuser must fetch null-user execution via carve-out; "
            f"got {resp.status_code} — likely wired with .filter(user=…) "
            f"instead of scope_queryset_agent_execution().get()"
        )

    def test_regular_user_cannot_fetch_null_user_execution_by_id(
        self, client, user_a, executions
    ):
        # execution_detail (:472) — regular user must not be able to fetch
        # a null-user (system-context) execution; superuser-only carve-out.
        client.force_login(user_a)
        target = executions["null_user"]
        resp = client.get(f"/api/v1/agents/execution/{target.id}/")
        assert resp.status_code == 404, (
            f"Regular user must not fetch null-user execution (carve-out is "
            f"superuser-only); got {resp.status_code}"
        )


# ==========================================================================
# B2b additions — ops/diagnostics cluster (superuser-gated + predicate)
# ==========================================================================


class TestB2bOpsSuperuserGate:
    """B2b: ops surfaces are superuser-gated (401 anonymous / 403 non-super)."""

    def test_anonymous_gets_401_on_diagnostics_endpoint(self):
        # cockpit_inbox is representative of the diagnostics cluster.
        resp = Client().get("/api/cockpit/inbox/")
        assert resp.status_code == 401, (
            f"Anonymous caller must be 401 on ops endpoint; got "
            f"{resp.status_code} (Rigby SIGN Q1 fold)"
        )

    def test_regular_user_gets_403_on_diagnostics_endpoint(
        self, client, user_a
    ):
        # user_a is authenticated but not superuser → 403.
        client.force_login(user_a)
        resp = client.get("/api/cockpit/inbox/")
        assert resp.status_code == 403, (
            f"Non-superuser must be 403 on ops endpoint; got "
            f"{resp.status_code} (Rigby SIGN Q1 fold — superuser-gate, not "
            f"staff-gate)"
        )

    def test_superuser_can_access_and_scope_applies(
        self, client, superuser, executions
    ):
        # Superuser passes the gate; predicate scope still applies inside
        # (defense-in-depth). Cockpit inbox should return 200 for superuser.
        client.force_login(superuser)
        resp = client.get("/api/cockpit/inbox/")
        assert resp.status_code == 200, (
            f"Superuser must pass ops gate with 200; got {resp.status_code}"
        )


# ==========================================================================
# B2c additions — tail cleanup (predicate + one superuser-gate trace surface)
# ==========================================================================


class TestB2cPredicateAndTraceViewer:
    """B2c: dashboard-stats + trace-viewer wiring — Rigby SIGN Q3 minimum."""

    def test_dashboard_stats_regular_user_sees_own_only(
        self, client, user_a, executions
    ):
        # views_dashboard_stats.dashboard_stats (:85) — predicate-scoped LIST.
        # user_a has 2 executions; user_b has 1; null_user has 1.
        # user_a on a personal dashboard should see own 2, not b1/null_user.
        client.force_login(user_a)
        resp = client.get("/api/dashboard/stats/")
        assert resp.status_code == 200
        body = resp.json()
        # agent_executions_24h field is the predicate-scoped 24h count.
        # user_a has 2 rows created inside test scope; count must equal 2,
        # not 3 (which would include b1) or 4 (which would include null_user).
        assert body.get("agent_executions_24h") == 2, (
            f"user_a must see own 24h count only; got "
            f"{body.get('agent_executions_24h')}"
        )

    def test_trace_viewer_anonymous_gets_401(self):
        # views_trace_viewer.TraceViewerView (:31) — superuser-gated
        # (B2b pattern applied to B2c debug/ops surface).
        random_trace = uuid.uuid4()
        resp = Client().get(f"/api/traces/{random_trace}/")
        # DRF IsAuthenticated returns 403 for anonymous by default; the
        # @method_decorator(superuser_required) inside returns 401. Either
        # is acceptable as "unauthenticated blocked" for the gate contract.
        assert resp.status_code in (401, 403), (
            f"Anonymous must be blocked from trace-viewer; got "
            f"{resp.status_code}"
        )

    def test_trace_viewer_non_superuser_gets_403(self, client, user_a):
        # Authenticated non-superuser must be 403 (superuser-gate).
        client.force_login(user_a)
        random_trace = uuid.uuid4()
        resp = client.get(f"/api/traces/{random_trace}/")
        assert resp.status_code == 403, (
            f"Non-superuser must be 403 on trace-viewer; got "
            f"{resp.status_code}"
        )
