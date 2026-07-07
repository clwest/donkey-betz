"""Arc I-0100 P4 Stop Condition #1 PR-A5 — regression coverage for
the 6 §3.1 Category C sites Chris ratified as `exclude_pa` in PR-B1.

Sites patched:

- ``core/views_analytics.py:1507`` — daily execution counts
  (executions_by_day) in ``get_chart_content_production``
- ``core/views_analytics.py:1559`` — daily cost rollup
  (daily_costs) in ``get_chart_revenue``
- ``core/views_agent_analytics.py:146`` — recent-failures top-agents
  list (7d) in ``get_agents_needing_attention``
- ``core/services/td_handlers_content.py:3167`` + ``:3171`` —
  per-agent success rate in the ``by_agent`` action of the content
  handlers
- ``core/tasks.py:10456`` — top failing agents (7d) in the periodic
  system SLO report
- ``core/services/ops_autopilot/budget.py:599`` — ROI outcome
  attribution (defensive exclude; allowlist already excludes PA
  naturally, but explicit exclude locks in the semantic)

Fix form: ``.exclude(agent__name='PersonalAssistant')`` per Chris
directive + ADR-0002 §4.2 F1 fold equivalent (agent__name form is
safer than ``input_data__source='pa'`` for pre-flag-flip rows —
Postgres JSONField NULL-semantics).

Run::

    python manage.py test core.tests.test_pa_consumer_exclude_ratified_category_c -v2 --keepdb
"""
from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.test import TestCase
from django.utils import timezone

from core.models_unified_system import Agent, AgentExecution


User = get_user_model()


class PAConsumerExcludeRatifiedCategoryCTests(TestCase):
    """Regression coverage for the 6 ratified Category C sites."""

    def setUp(self):
        self.user = User.objects.create_user(
            username=f"a5-{id(self)}",
            email=f"a5-{id(self)}@example.com",
            password="x",
        )
        self.router_agent = Agent.objects.create(
            name=f"TestRouterAgent_A5_{id(self)}",
            agent_type="router",
            description="Test router agent for PR-A5 regressions",
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
        self,
        count: int,
        status: str = "completed",
        cost=None,
    ):
        for i in range(count):
            AgentExecution.objects.create(
                agent=self.router_agent,
                user=self.user,
                task=f"Router task {i}",
                status=status,
                input_data={},
                execution_time_ms=100,
                cost=cost if cost is not None else 0.05,
            )

    def _seed_pa_executions(
        self,
        count: int,
        status: str = "completed",
        cost=None,
    ):
        for i in range(count):
            AgentExecution.objects.create(
                agent=self.pa_agent,
                user=self.user,
                task=f"PA task {i}",
                status=status,
                input_data={"source": "pa", "trace_id": f"pa-a5-{i}"},
                execution_time_ms=100,
                cost=cost if cost is not None else 0.10,
                owner_agent="PersonalAssistant",
            )

    def _all_test_rows_qs(self):
        return AgentExecution.objects.filter(user=self.user)

    # ─── views_analytics.py:1507 — daily execution counts ────────────

    def test_content_production_daily_count_excludes_pa(self):
        """get_chart_content_production per-day count: PA absent even
        when PA dominates raw count."""
        self._seed_router_executions(3, status="completed")
        self._seed_pa_executions(25, status="completed")

        now = timezone.now()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        count = (
            self._all_test_rows_qs()
            .filter(
                created_at__gte=day_start,
                created_at__lt=day_end,
                status="completed",
            )
            .exclude(agent__name="PersonalAssistant")
            .count()
        )
        self.assertEqual(count, 3)

    # ─── views_analytics.py:1559 — daily cost rollup ─────────────────

    def test_revenue_daily_cost_excludes_pa(self):
        """get_chart_revenue per-day cost: PA cost not included."""
        # Router: 3 rows × $0.05 = $0.15
        self._seed_router_executions(3, cost=0.05)
        # PA: 20 rows × $0.10 = $2.00 — WOULD dominate cost chart
        self._seed_pa_executions(20, cost=0.10)

        now = timezone.now()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        executions = (
            self._all_test_rows_qs()
            .filter(created_at__gte=day_start, created_at__lt=day_end)
            .exclude(agent__name="PersonalAssistant")
        )
        day_cost = sum(float(e.cost or 0) for e in executions)
        self.assertAlmostEqual(day_cost, 0.15, places=2)

    # ─── views_agent_analytics.py:146 — needs-attention feed ─────────

    def test_needs_attention_recent_failures_excludes_pa(self):
        """get_agents_needing_attention: PA absent from recent-failure
        top-agents feed."""
        self._seed_router_executions(3, status="failed")
        self._seed_pa_executions(20, status="failed")

        week_ago = timezone.now() - timedelta(days=7)
        recent_failures = (
            self._all_test_rows_qs()
            .filter(status="failed", created_at__gte=week_ago)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__id", "agent__name", "agent__agent_type")
            .annotate(failure_count=Count("id"))
            .order_by("-failure_count")[:5]
        )
        rows = list(recent_failures)
        names = [r["agent__name"] for r in rows]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)
        # Router should top the list at 3 (PA at 20 is excluded)
        self.assertEqual(rows[0]["agent__name"], self.router_name)
        self.assertEqual(rows[0]["failure_count"], 3)

    # ─── td_handlers_content.py:3167 — per-agent success rate ────────

    def test_content_handlers_by_agent_success_rate_excludes_pa(self):
        """content handlers by_agent success rate for 'assistant'-like
        agent_name: PA excluded via explicit exclude (guards against
        icontains substring match)."""
        # Seed PA: 5 completed, 5 failed
        self._seed_pa_executions(5, status="completed")
        self._seed_pa_executions(5, status="failed")

        cutoff = timezone.now() - timedelta(days=7)
        # User queries for "assistant" — this would match
        # 'PersonalAssistant' via icontains WITHOUT the exclude.
        agent_name = "assistant"
        total = (
            self._all_test_rows_qs()
            .filter(agent__name__icontains=agent_name, created_at__gte=cutoff)
            .exclude(agent__name="PersonalAssistant")
            .count()
        )
        successes = (
            self._all_test_rows_qs()
            .filter(
                agent__name__icontains=agent_name,
                created_at__gte=cutoff,
                status="completed",
            )
            .exclude(agent__name="PersonalAssistant")
            .count()
        )
        # PA excluded → no rows match "assistant"
        self.assertEqual(total, 0)
        self.assertEqual(successes, 0)

    # ─── tasks.py:10456 — top failing agents in system SLO report ────

    def test_system_metrics_top_failing_agents_excludes_pa(self):
        """metrics['errors']['top_failing_agents']: PA absent from
        7d top-failures ranking."""
        self._seed_router_executions(4, status="failed")
        self._seed_pa_executions(30, status="failed")

        last_7d = timezone.now() - timedelta(days=7)
        recent_failures = list(
            self._all_test_rows_qs()
            .filter(status="failed", created_at__gte=last_7d)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )
        names = [r["agent__name"] for r in recent_failures]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)
        self.assertEqual(recent_failures[0]["agent__name"], self.router_name)
        self.assertEqual(recent_failures[0]["count"], 4)

    # ─── ops_autopilot/budget.py:599 — ROI outcome attribution ───────

    def test_roi_outcome_attribution_excludes_pa_when_in_allowlist(self):
        """compute_roi_scores AgentExecution outcomes: PA excluded
        even if allowlist accidentally includes PA (defensive)."""
        self._seed_router_executions(5, status="completed")
        self._seed_pa_executions(20, status="completed")

        # Simulate a buggy or future caller that passes both agents
        # in the allowlist. Without the exclude, PA would dominate
        # the ROI attribution.
        agent_names = [self.router_name, "PersonalAssistant"]
        window_start = timezone.now() - timedelta(days=7)
        outcomes = list(
            self._all_test_rows_qs()
            .filter(
                created_at__gte=window_start,
                status="completed",
                agent__name__in=agent_names,
            )
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(completed=Count("id"))
        )
        names = {o["agent__name"] for o in outcomes}
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)

    # ─── Cross-cutting invariant ─────────────────────────────────────

    def test_pa_rows_never_appear_in_any_pr_a5_aggregation(self):
        """Cross-cutting invariant: PA rows absent from all ratified
        §3.1 aggregations given a mixed corpus."""
        self._seed_router_executions(4, status="completed")
        self._seed_router_executions(2, status="failed")
        self._seed_pa_executions(60, status="completed")
        self._seed_pa_executions(20, status="failed")

        now = timezone.now()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        week_ago = now - timedelta(days=7)

        # #1 daily completion count
        n1 = (
            self._all_test_rows_qs()
            .filter(created_at__gte=day_start, created_at__lt=day_end, status="completed")
            .exclude(agent__name="PersonalAssistant")
            .count()
        )
        self.assertEqual(n1, 4)

        # #3 needs-attention recent failures
        rf = (
            self._all_test_rows_qs()
            .filter(status="failed", created_at__gte=week_ago)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(count=Count("id"))
        )
        self.assertNotIn("PersonalAssistant", {r["agent__name"] for r in rf})

        # #5 top-failing agents (7d)
        tfa = (
            self._all_test_rows_qs()
            .filter(status="failed", created_at__gte=week_ago)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )
        self.assertNotIn("PersonalAssistant", {r["agent__name"] for r in tfa})

        # Baseline sanity: PA rows exist in unfiltered universe
        pa_completed = self._all_test_rows_qs().filter(
            agent__name="PersonalAssistant", status="completed"
        ).count()
        self.assertEqual(pa_completed, 60)

    # ─── Negative controls (locks in fix necessity) ──────────────────

    def test_without_exclude_pa_would_dominate_needs_attention(self):
        """Negative control: SAME needs-attention query WITHOUT
        exclude would rank PA #1."""
        self._seed_router_executions(3, status="failed")
        self._seed_pa_executions(50, status="failed")

        week_ago = timezone.now() - timedelta(days=7)
        pre_patch = list(
            self._all_test_rows_qs()
            .filter(status="failed", created_at__gte=week_ago)
            .values("agent__id", "agent__name")
            .annotate(failure_count=Count("id"))
            .order_by("-failure_count")[:5]
        )
        self.assertEqual(pre_patch[0]["agent__name"], "PersonalAssistant")
        self.assertEqual(pre_patch[0]["failure_count"], 50)

    def test_without_exclude_pa_would_dominate_daily_cost(self):
        """Negative control: SAME daily-cost query WITHOUT exclude
        would inflate day_cost with PA cost."""
        self._seed_router_executions(3, cost=0.05)
        self._seed_pa_executions(20, cost=0.10)

        now = timezone.now()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        executions_pre = self._all_test_rows_qs().filter(
            created_at__gte=day_start, created_at__lt=day_end
        )
        day_cost_pre = sum(float(e.cost or 0) for e in executions_pre)
        # 3 × $0.05 + 20 × $0.10 = $0.15 + $2.00 = $2.15
        self.assertAlmostEqual(day_cost_pre, 2.15, places=2)
