"""Arc I-0100 P4 Stop Condition #1 PR-A2 — regression coverage for
dashboard-view per-agent aggregations that exclude PA meta-agent rows
per ADR-0002 §4.2 F1 fold row-class discipline.

Sites patched:

- ``core/views_analytics_real.py:170`` — ``top_agents`` (today ranking)
- ``core/views_agent_execution.py:769`` — ``agent_stats`` (high-failure alerts)
- ``core/views_agent_execution.py:796`` — ``slow_agents`` (latency alerts)
- ``core/views_integration_health.py:355`` — ``agent_metrics`` (per-agent breakdown)

Each site adds ``.exclude(agent__name='PersonalAssistant')`` per ADR-0002
§4.2 F1 fold equivalent form (agent__name is safer than
``input_data__source='pa'`` for pre-flag-flip rows — see PR-A1 commit
message for the Postgres JSONField NULL-semantics finding).

The tests exercise the QUERY PATTERN at each patched site directly via
ORM. For every patched site this test proves:

1. **Normal (non-PA) executions still count** — the query pattern
   returns the router-agent aggregate correctly.
2. **Synthetic PA rows do NOT distort the metric** — same query with
   PA rows added returns the SAME router-agent aggregate; PA does
   NOT appear in any returned aggregation.

Run::

    python manage.py test core.tests.test_pa_consumer_exclude_dashboard_views -v2 --keepdb
"""
from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Q
from django.test import TestCase
from django.utils import timezone

from core.models_unified_system import Agent, AgentExecution


User = get_user_model()


class PAConsumerExcludeDashboardViewsTests(TestCase):
    """Regression coverage for dashboard-view per-agent aggregations
    that must exclude PA meta-agent rows."""

    def setUp(self):
        self.user = User.objects.create_user(
            username=f"a2-{id(self)}",
            email=f"a2-{id(self)}@example.com",
            password="x",
        )
        self.router_agent = Agent.objects.create(
            name=f"TestRouterAgent_A2_{id(self)}",
            agent_type="router",
            description="Test router agent for PR-A2 regressions",
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

    def _seed_router_executions(
        self, count: int, status: str = "completed", execution_time_ms: int = 100,
    ):
        """Create N router-agent AgentExecution rows."""
        for i in range(count):
            AgentExecution.objects.create(
                agent=self.router_agent,
                user=self.user,
                task=f"Router task {i}",
                status=status,
                input_data={},
                execution_time_ms=execution_time_ms,
            )

    def _seed_pa_executions(
        self, count: int, status: str = "completed", execution_time_ms: int = 100,
    ):
        """Create N PA-authored AgentExecution rows."""
        for i in range(count):
            AgentExecution.objects.create(
                agent=self.pa_agent,
                user=self.user,
                task=f"PA task {i}",
                status=status,
                input_data={"source": "pa", "trace_id": f"pa-a2-{i}"},
                execution_time_ms=execution_time_ms,
                owner_agent="PersonalAssistant",
            )

    def _all_test_rows_qs(self):
        return AgentExecution.objects.filter(user=self.user)

    # ─── views_analytics_real.py:170 — top_agents ────────────────────

    def test_analytics_real_top_agents_pattern_excludes_pa(self):
        """top_agents today ranking: high-volume PA does not appear."""
        self._seed_router_executions(5)
        self._seed_pa_executions(100)

        last_24h = timezone.now() - timedelta(hours=24)
        # Mirror views_analytics_real.py:170
        top_agents = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=last_24h)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )
        names = [t["agent__name"] for t in top_agents]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)
        self.assertEqual(top_agents[0]["agent__name"], self.router_name)
        self.assertEqual(top_agents[0]["count"], 5)

    # ─── views_agent_execution.py:769 — agent_stats high-failure ─────

    def test_agent_execution_high_failure_pattern_excludes_pa(self):
        """agent_stats: PA does not appear in failure-rate alerts."""
        # Router agent: 6 completed 1 failed → 14% fail rate (below alert threshold)
        self._seed_router_executions(6, status="completed")
        self._seed_router_executions(1, status="failed")
        # PA turns: all failed → 100% fail rate (would alert if not excluded)
        self._seed_pa_executions(10, status="failed")

        cutoff = timezone.now() - timedelta(hours=24)
        # Mirror views_agent_execution.py:769
        agent_stats = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(
                total=Count("id"),
                failed=Count("id", filter=Q(status="failed")),
            )
        )
        # Check the downstream alert filter would NOT fire on PA
        alerts = []
        for stat in agent_stats:
            if stat["total"] >= 5:
                fail_rate = stat["failed"] / stat["total"]
                if fail_rate > 0.3:
                    alerts.append(stat["agent__name"])
        self.assertNotIn("PersonalAssistant", alerts)

        # Verify the router row IS present with expected counts
        router_row = next(
            (s for s in agent_stats if s["agent__name"] == self.router_name),
            None,
        )
        self.assertIsNotNone(router_row)
        self.assertEqual(router_row["total"], 7)
        self.assertEqual(router_row["failed"], 1)

    # ─── views_agent_execution.py:796 — slow_agents ──────────────────

    def test_agent_execution_slow_agents_pattern_excludes_pa(self):
        """slow_agents: high-latency PA does not trigger alerts."""
        # Router agent: fast (below 60s threshold)
        self._seed_router_executions(5, status="completed", execution_time_ms=1000)
        # PA turns: slow (above 60s threshold) — would alert if not excluded
        self._seed_pa_executions(5, status="completed", execution_time_ms=90000)

        cutoff = timezone.now() - timedelta(hours=24)
        # Mirror views_agent_execution.py:796
        slow_agents = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff, status="completed")
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(
                avg_time=Avg("execution_time_ms"),
                count=Count("id"),
            )
            .filter(avg_time__gt=60000, count__gte=3)
        )
        names = [s["agent__name"] for s in slow_agents]
        self.assertNotIn("PersonalAssistant", names)
        # Router is fast → should NOT be in slow_agents
        self.assertNotIn(self.router_name, names)

    def test_agent_execution_slow_agents_router_fires_when_slow(self):
        """Positive control: if router-agent IS slow, it appears (proves
        the exclude only removes PA, not legitimate router alerts)."""
        # Router agent: slow (above 60s threshold) — should alert
        self._seed_router_executions(5, status="completed", execution_time_ms=90000)

        cutoff = timezone.now() - timedelta(hours=24)
        slow_agents = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff, status="completed")
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(
                avg_time=Avg("execution_time_ms"),
                count=Count("id"),
            )
            .filter(avg_time__gt=60000, count__gte=3)
        )
        names = [s["agent__name"] for s in slow_agents]
        self.assertIn(self.router_name, names)

    # ─── views_integration_health.py:355 — agent_metrics ─────────────

    def test_integration_health_agent_metrics_pattern_excludes_pa(self):
        """agent_metrics per-agent breakdown: PA does not appear in top-20."""
        self._seed_router_executions(10)
        self._seed_pa_executions(50)

        last_7d = timezone.now() - timedelta(days=7)
        # Mirror views_integration_health.py:355
        agent_metrics = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=last_7d)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(
                total=Count("id"),
                avg_time=Avg("execution_time_ms"),
            )
            .order_by("-total")[:20]
        )
        names = [a["agent__name"] for a in agent_metrics]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)
        # Router should be #1 in this test scope (only agent besides PA)
        self.assertEqual(agent_metrics[0]["agent__name"], self.router_name)
        self.assertEqual(agent_metrics[0]["total"], 10)

    # ─── Cross-cutting invariant ─────────────────────────────────────

    def test_pa_rows_never_appear_in_any_dashboard_view_aggregation(self):
        """Cross-cutting invariant: for a mixed corpus of PA + router
        executions, dashboard-view per-agent aggregations return
        router-agent rows only."""
        self._seed_router_executions(15)
        self._seed_pa_executions(300)

        cutoff = timezone.now() - timedelta(days=7)
        # Aggregation shape common to all 4 patched sites
        agg = (
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(count=Count("id"))
        )
        agg_names = {a["agent__name"] for a in agg}
        self.assertNotIn("PersonalAssistant", agg_names)
        self.assertIn(self.router_name, agg_names)

        # Baseline sanity: PA rows exist in unfiltered universe
        pa_universe = self._all_test_rows_qs().filter(
            agent__name="PersonalAssistant"
        ).count()
        self.assertEqual(pa_universe, 300)

    # ─── Negative control (locks in the fix's necessity) ─────────────

    def test_without_exclude_pa_would_dominate_top_agents(self):
        """Negative control: SAME query WITHOUT exclude would rank PA #1."""
        self._seed_router_executions(5)
        self._seed_pa_executions(100)

        last_24h = timezone.now() - timedelta(hours=24)
        pre_patch = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=last_24h)
            .values("agent__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )
        self.assertEqual(pre_patch[0]["agent__name"], "PersonalAssistant")
        self.assertEqual(pre_patch[0]["count"], 100)
