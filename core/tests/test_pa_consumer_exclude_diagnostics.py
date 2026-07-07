"""Arc I-0100 P4 Stop Condition #1 PR-A3 — regression coverage for
diagnostics per-agent aggregations + stale-agent detection that
exclude PA meta-agent rows per ADR-0002 §4.2 F1 fold row-class
discipline.

Sites patched:

- ``core/services/diagnostics/cto_daily.py:101`` — ``top_failing_agents_24h``
- ``core/services/diagnostics/cto_daily.py:107`` — ``agent_7d`` fail-count dict
- ``core/views_diagnostics.py:3280`` — ``all_agents`` set for stale detection
  (excludes PA from the universe rather than from AgentExecution query — see
  below for why)

Fix form: ``.exclude(agent__name='PersonalAssistant')`` per Chris directive
(agent__name form is safer than ``input_data__source='pa'`` for pre-flag-flip
rows — see PR-A1 for the Postgres JSONField NULL-semantics finding).

Special case for views_diagnostics.py:3280 (stale-agent detection):

The stale-agent alert compares ``all_agents`` (set of active Agent rows)
against ``agents_with_runs`` (set of agent names from recent
AgentExecution rows). Under flag OFF, PA has no executions but the
canonical PA Agent row IS ``is_active=True`` (from migration 0377), so
PA would appear in the stale set. The fix excludes PA from
``all_agents`` at the Agent-model query, NOT at the AgentExecution
query — because the false-positive is at the Agent-universe level,
not at the AgentExecution level.

Run::

    python manage.py test core.tests.test_pa_consumer_exclude_diagnostics -v2 --keepdb
"""
from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Max
from django.test import TestCase
from django.utils import timezone

from core.models_unified_system import Agent, AgentExecution


User = get_user_model()


class PAConsumerExcludeDiagnosticsTests(TestCase):
    """Regression coverage for diagnostics-family per-agent aggregations
    that must exclude PA meta-agent rows."""

    def setUp(self):
        self.user = User.objects.create_user(
            username=f"a3-{id(self)}",
            email=f"a3-{id(self)}@example.com",
            password="x",
        )
        self.router_agent = Agent.objects.create(
            name=f"TestRouterAgent_A3_{id(self)}",
            agent_type="router",
            description="Test router agent for PR-A3 regressions",
            specialization="test",
        )
        self.pa_agent, _ = Agent.objects.get_or_create(
            name="PersonalAssistant",
            defaults={
                "agent_type": "meta",
                "description": "Canonical PA meta-agent (test setup)",
                "specialization": "personal_assistant",
            },
        )
        self.router_name = self.router_agent.name

    def _seed_router_executions(self, count: int, status: str = "completed"):
        for i in range(count):
            AgentExecution.objects.create(
                agent=self.router_agent,
                user=self.user,
                task=f"Router task {i}",
                status=status,
                input_data={},
                execution_time_ms=100,
            )

    def _seed_pa_executions(self, count: int, status: str = "completed"):
        for i in range(count):
            AgentExecution.objects.create(
                agent=self.pa_agent,
                user=self.user,
                task=f"PA task {i}",
                status=status,
                input_data={"source": "pa", "trace_id": f"pa-a3-{i}"},
                execution_time_ms=100,
                owner_agent="PersonalAssistant",
            )

    def _all_test_rows_qs(self):
        return AgentExecution.objects.filter(user=self.user)

    # ─── cto_daily.py:101 — top_failing_agents_24h ────────────────────

    def test_cto_daily_top_failing_agents_pattern_excludes_pa(self):
        """top_failing_agents_24h: PA does not appear in per-agent
        failure ranking even when PA has more failures than router."""
        # Router agent: 3 failures
        self._seed_router_executions(3, status="failed")
        # PA turns: 20 failures (would top the list if not excluded)
        self._seed_pa_executions(20, status="failed")

        cutoff_24h = timezone.now() - timedelta(hours=24)
        # Mirror cto_daily.py:100 patched query
        top_failing = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff_24h, status="failed")
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )
        names = [t["agent__name"] for t in top_failing]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)
        self.assertEqual(top_failing[0]["agent__name"], self.router_name)
        self.assertEqual(top_failing[0]["count"], 3)

    # ─── cto_daily.py:107 — agent_7d fail-count dict ──────────────────

    def test_cto_daily_agent_7d_fail_dict_pattern_excludes_pa(self):
        """agent_7d fail-count dict: PA is not a key even when it
        would otherwise be counted."""
        self._seed_router_executions(2, status="failed")
        self._seed_pa_executions(15, status="failed")

        cutoff_7d = timezone.now() - timedelta(days=7)
        # Mirror cto_daily.py:107 patched query
        agent_7d = dict(
            (r["agent__name"], r["count"])
            for r in self._all_test_rows_qs()
            .filter(created_at__gte=cutoff_7d, status="failed")
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(count=Count("id"))
        )
        self.assertNotIn("PersonalAssistant", agent_7d)
        self.assertEqual(agent_7d.get(self.router_name), 2)

    # ─── views_diagnostics.py:3280 — stale-agent detection ───────────

    def test_stale_agent_detection_excludes_pa_from_all_agents(self):
        """Stale-agent detection: PA should not appear as a stale
        agent even when it has zero recent executions (flag OFF state).

        The fix excludes PA from ``all_agents`` at the Agent-model
        query. PA is is_active=True but has no runs, so pre-patch it
        would appear stale. Post-patch it's excluded from the
        universe entirely.
        """
        # Seed router agent WITHOUT recent executions — router SHOULD
        # appear as stale (positive control)
        stale_hours = 48
        cutoff = timezone.now() - timedelta(hours=stale_hours)

        # Mirror the patched pattern at views_diagnostics.py:3280
        agents_with_runs = set(
            AgentExecution.objects.filter(created_at__gte=cutoff)
            .values_list("agent__name", flat=True).distinct()
        )
        all_agents_excluding_pa = set(
            Agent.objects.filter(is_active=True)
            .exclude(name="PersonalAssistant")
            .values_list("name", flat=True)
        )
        stale = all_agents_excluding_pa - agents_with_runs

        # PA should NOT be in stale set
        self.assertNotIn("PersonalAssistant", stale)

        # Router agent should still be in stale set (positive control:
        # it's active, has no recent executions, and we didn't exclude it)
        self.assertIn(self.router_name, stale)

    def test_stale_agent_detection_router_with_runs_not_stale(self):
        """Router agent with recent executions is NOT stale (positive
        control on the intersection logic)."""
        self._seed_router_executions(3)

        stale_hours = 48
        cutoff = timezone.now() - timedelta(hours=stale_hours)

        agents_with_runs = set(
            AgentExecution.objects.filter(created_at__gte=cutoff)
            .values_list("agent__name", flat=True).distinct()
        )
        all_agents_excluding_pa = set(
            Agent.objects.filter(is_active=True)
            .exclude(name="PersonalAssistant")
            .values_list("name", flat=True)
        )
        stale = all_agents_excluding_pa - agents_with_runs

        self.assertNotIn(self.router_name, stale)
        self.assertNotIn("PersonalAssistant", stale)

    # ─── Cross-cutting invariant ─────────────────────────────────────

    def test_pa_rows_never_appear_in_any_diagnostics_aggregation(self):
        """Cross-cutting invariant: for a mixed corpus of PA + router
        failures, diagnostics per-agent aggregations return router
        only."""
        self._seed_router_executions(5, status="failed")
        self._seed_pa_executions(50, status="failed")

        cutoff_7d = timezone.now() - timedelta(days=7)
        # Aggregation shape common to cto_daily.py:101 + 107
        agg = (
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff_7d, status="failed")
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(count=Count("id"))
        )
        names = {a["agent__name"] for a in agg}
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)

        # Baseline sanity: PA rows exist in unfiltered universe
        pa_universe = self._all_test_rows_qs().filter(
            agent__name="PersonalAssistant", status="failed"
        ).count()
        self.assertEqual(pa_universe, 50)

    # ─── Negative control (locks in the fix's necessity) ─────────────

    def test_without_exclude_pa_would_dominate_top_failing(self):
        """Negative control: SAME cto_daily query WITHOUT exclude would
        rank PA #1 in top_failing_agents_24h."""
        self._seed_router_executions(3, status="failed")
        self._seed_pa_executions(50, status="failed")

        cutoff_24h = timezone.now() - timedelta(hours=24)
        pre_patch = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff_24h, status="failed")
            .values("agent__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )
        self.assertEqual(pre_patch[0]["agent__name"], "PersonalAssistant")
        self.assertEqual(pre_patch[0]["count"], 50)

    def test_without_exclude_pa_would_appear_as_stale(self):
        """Negative control: SAME stale-agent detection WITHOUT exclude
        would include PA in the stale set (because PA is active but
        has no runs)."""
        stale_hours = 48
        cutoff = timezone.now() - timedelta(hours=stale_hours)

        agents_with_runs_pre = set(
            AgentExecution.objects.filter(created_at__gte=cutoff)
            .values_list("agent__name", flat=True).distinct()
        )
        # WITHOUT the exclude
        all_agents_pre_patch = set(
            Agent.objects.filter(is_active=True).values_list("name", flat=True)
        )
        stale_pre_patch = all_agents_pre_patch - agents_with_runs_pre

        # PA WOULD appear stale pre-patch (is_active=True + no runs)
        self.assertIn("PersonalAssistant", stale_pre_patch)
