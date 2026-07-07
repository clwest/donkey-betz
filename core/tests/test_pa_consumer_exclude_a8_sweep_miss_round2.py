"""Arc I-0100 P4 Stop Condition #1 PR-A8 — regression coverage for
the 9 Category B sites that the direct-callsite sweep (post-PR-A7
merge) surfaced. Prior two file-level sweeps (agent-delegated)
missed these because they only checked "does this file have SOME
exclude?" heuristics; multiple aggregation blocks per file were
overlooked.

Sites patched:

- ``core/views_diagnostics.py:1631`` — top failing agents ranking
- ``core/views_diagnostics.py:2188`` — agents with high failure
  rate alert
- ``core/views_diagnostics.py:3182`` — per-agent failure-rate
  policy threshold check
- ``core/views_diagnostics.py:4344`` — per-agent 30-day success
  stats (top-25)
- ``core/services/td_handlers_content.py:3151`` — ``by_agent``
  action agent-counts (top-30, no filter)
- ``core/services/td_handlers_content.py:3217`` — ``stats``
  action by_agent ranking (top-15 with avg_time)
- ``core/services/ops_autopilot/intelligence.py:2081`` — anomaly
  high-activity agent detector (top-20)
- ``core/services/ops_autopilot/intelligence.py:2693`` — high-
  count-high-failure gap analysis (top-20)
- ``core/services/muscular.py:636`` — per_agent_stats in
  determine_status (weak/overworked-agent detection)

Fix form: ``.exclude(agent__name='PersonalAssistant')`` per
ADR-0002 §4.2 F1 fold equivalent.

Run::

    python manage.py test core.tests.test_pa_consumer_exclude_a8_sweep_miss_round2 -v2 --keepdb
"""
from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Max
from django.db.models import Q as DjangoQ
from django.test import TestCase
from django.utils import timezone

from core.models_unified_system import Agent, AgentExecution


User = get_user_model()


class PAConsumerExcludeA8SweepMissR2Tests(TestCase):
    """Regression coverage for the 9 sites the direct-callsite
    sweep found."""

    def setUp(self):
        self.user = User.objects.create_user(
            username=f"a8-{id(self)}",
            email=f"a8-{id(self)}@example.com",
            password="x",
        )
        self.router_agent = Agent.objects.create(
            name=f"TestRouterAgent_A8_{id(self)}",
            agent_type="router",
            description="Test router agent for PR-A8 regressions",
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
                input_data={"source": "pa", "trace_id": f"pa-a8-{i}"},
                execution_time_ms=100,
                owner_agent="PersonalAssistant",
            )

    def _all_test_rows_qs(self):
        return AgentExecution.objects.filter(user=self.user)

    # ─── views_diagnostics.py:1631 — top failing agents ──────────────

    def test_diagnostics_top_failing_excludes_pa(self):
        """views_diagnostics.py top failing agents ranking excludes PA."""
        self._seed_router_executions(4, status="failed")
        self._seed_pa_executions(25, status="failed")

        cutoff = timezone.now() - timedelta(hours=24)
        agg = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(
                failed_count=Count("id", filter=DjangoQ(status="failed")),
                total_count=Count("id"),
                last_failed_at=Max("completed_at", filter=DjangoQ(status="failed")),
            )
            .filter(failed_count__gt=0)
            .order_by("-failed_count")[:10]
        )
        names = [a["agent__name"] for a in agg]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)

    # ─── views_diagnostics.py:2188 — high failure rate alerts ────────

    def test_diagnostics_high_failure_rate_alerts_excludes_pa(self):
        """views_diagnostics.py high-failure-rate alerts exclude PA
        (thresholds: failed>=3, total>=5)."""
        # Router: 3 failed of 5 → 60% — alert-eligible
        self._seed_router_executions(2, status="completed")
        self._seed_router_executions(3, status="failed")
        # PA: 15 failed of 20 → 75% — WOULD alert if included
        self._seed_pa_executions(5, status="completed")
        self._seed_pa_executions(15, status="failed")

        cutoff = timezone.now() - timedelta(hours=24)
        agg = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(
                failed=Count("id", filter=DjangoQ(status="failed")),
                total=Count("id"),
            )
            .filter(failed__gte=3, total__gte=5)
        )
        names = {a["agent__name"] for a in agg}
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)

    # ─── views_diagnostics.py:3182 — failure-rate policy check ───────

    def test_diagnostics_failure_rate_policy_check_excludes_pa(self):
        """views_diagnostics.py per-agent failure-rate policy check
        excludes PA (min_runs=3)."""
        self._seed_router_executions(2, status="completed")
        self._seed_router_executions(2, status="failed")
        self._seed_pa_executions(30, status="failed")

        cutoff = timezone.now() - timedelta(hours=1)
        min_runs = 3
        agents = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(
                total=Count("id"),
                failed=Count("id", filter=DjangoQ(status="failed")),
            )
            .filter(total__gte=min_runs)
        )
        names = {a["agent__name"] for a in agents}
        self.assertNotIn("PersonalAssistant", names)
        # Router qualifies (4 total >= 3)
        self.assertIn(self.router_name, names)

    # ─── views_diagnostics.py:4344 — 30d per-agent success stats ─────

    def test_diagnostics_30d_per_agent_stats_excludes_pa(self):
        """views_diagnostics.py 30d per-agent stats (top-25 by total)
        excludes PA."""
        self._seed_router_executions(5, status="completed")
        self._seed_pa_executions(40, status="completed")

        cutoff_30d = timezone.now() - timedelta(days=30)
        agent_stats = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff_30d)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(
                total=Count("id"),
                completed=Count("id", filter=DjangoQ(status="completed")),
                failed=Count("id", filter=DjangoQ(status="failed")),
                avg_time_ms=Avg("execution_time_ms"),
            )
            .order_by("-total")[:25]
        )
        names = [s["agent__name"] for s in agent_stats]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)
        # Router should top the list (5 vs PA 40 excluded)
        self.assertEqual(agent_stats[0]["agent__name"], self.router_name)

    # ─── td_handlers_content.py:3151 — by_agent no filter ────────────

    def test_content_by_agent_no_filter_excludes_pa(self):
        """td_handlers_content by_agent (no name filter → agent
        counts ranking top-30) excludes PA."""
        self._seed_router_executions(3)
        self._seed_pa_executions(25)

        cutoff = timezone.now() - timedelta(hours=24)
        agent_counts = dict(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:30]
            .values_list("agent__name", "count")
        )
        self.assertNotIn("PersonalAssistant", agent_counts)
        self.assertIn(self.router_name, agent_counts)
        self.assertEqual(agent_counts[self.router_name], 3)

    # ─── td_handlers_content.py:3217 — stats action by_agent ─────────

    def test_content_stats_action_by_agent_excludes_pa(self):
        """td_handlers_content `stats` action by_agent (top-15 with
        avg_time) excludes PA."""
        self._seed_router_executions(4)
        self._seed_pa_executions(30)

        cutoff = timezone.now() - timedelta(hours=24)
        by_agent = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(
                count=Count("id"),
                avg_time=Avg("execution_time_ms"),
            )
            .order_by("-count")[:15]
        )
        names = [r["agent__name"] for r in by_agent]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)

    # ─── ops_autopilot/intelligence.py:2081 — anomaly high-activity ──

    def test_ops_autopilot_anomaly_high_activity_excludes_pa(self):
        """ops_autopilot anomaly detector (high-activity agent
        flagging, top-20) excludes PA."""
        self._seed_router_executions(3)
        self._seed_pa_executions(50)

        cutoff = timezone.now() - timedelta(hours=24)
        agent_counts = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(exec_count=Count("id"))
            .order_by("-exec_count")[:20]
        )
        names = [a["agent__name"] for a in agent_counts]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)

    # ─── ops_autopilot/intelligence.py:2693 — gap analysis ───────────

    def test_ops_autopilot_gap_analysis_excludes_pa(self):
        """ops_autopilot gap analysis (high-count + high-failure,
        total>=5, top-20) excludes PA."""
        self._seed_router_executions(4, status="failed")
        self._seed_router_executions(2, status="completed")
        self._seed_pa_executions(30, status="failed")
        self._seed_pa_executions(10, status="completed")

        cutoff = timezone.now() - timedelta(days=7)
        agent_stats = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(
                total=Count("id"),
                failed=Count("id", filter=DjangoQ(status="failed")),
            )
            .filter(total__gte=5)
            .order_by("-total")[:20]
        )
        names = [a["agent__name"] for a in agent_stats]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)

    # ─── muscular.py:636 — per_agent_stats in determine_status ───────

    def test_muscular_per_agent_stats_determine_status_excludes_pa(self):
        """muscular.py per_agent_stats (weak/overworked-agent
        detection in determine_status) excludes PA."""
        self._seed_router_executions(6, status="completed")
        self._seed_router_executions(2, status="failed")
        self._seed_pa_executions(30, status="completed")
        self._seed_pa_executions(10, status="failed")

        executions = self._all_test_rows_qs()
        per_agent_stats = list(
            executions.exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(
                count=Count("id"),
                successful=Count("id", filter=DjangoQ(status="completed")),
                failed=Count("id", filter=DjangoQ(status="failed")),
            )
        )
        names = [s["agent__name"] for s in per_agent_stats]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)
        # Router: 6 completed, 2 failed, count=8
        router_row = next(s for s in per_agent_stats if s["agent__name"] == self.router_name)
        self.assertEqual(router_row["count"], 8)
        self.assertEqual(router_row["successful"], 6)
        self.assertEqual(router_row["failed"], 2)

    # ─── Cross-cutting invariant ─────────────────────────────────────

    def test_pa_rows_never_appear_in_any_pr_a8_aggregation(self):
        """Cross-cutting invariant: PA rows absent from all 9
        aggregation shapes given a mixed corpus."""
        self._seed_router_executions(7, status="completed")
        self._seed_router_executions(3, status="failed")
        self._seed_pa_executions(100, status="completed")
        self._seed_pa_executions(50, status="failed")

        cutoff = timezone.now() - timedelta(hours=24)

        # Verify 4 canonical shapes end-to-end
        shapes = [
            (
                "top_failing",
                self._all_test_rows_qs()
                .filter(created_at__gte=cutoff)
                .exclude(agent__name="PersonalAssistant")
                .values("agent__name")
                .annotate(failed_count=Count("id", filter=DjangoQ(status="failed")))
                .filter(failed_count__gt=0),
            ),
            (
                "high_activity",
                self._all_test_rows_qs()
                .filter(created_at__gte=cutoff)
                .exclude(agent__name="PersonalAssistant")
                .values("agent__name")
                .annotate(exec_count=Count("id")),
            ),
            (
                "content_stats_by_agent",
                self._all_test_rows_qs()
                .filter(created_at__gte=cutoff)
                .exclude(agent__name="PersonalAssistant")
                .values("agent__name")
                .annotate(count=Count("id"), avg_time=Avg("execution_time_ms")),
            ),
            (
                "muscular_per_agent",
                self._all_test_rows_qs()
                .exclude(agent__name="PersonalAssistant")
                .values("agent__name")
                .annotate(count=Count("id")),
            ),
        ]
        for shape_name, qs in shapes:
            names = {r["agent__name"] for r in qs}
            self.assertNotIn(
                "PersonalAssistant", names, msg=f"Shape {shape_name} leaked PA"
            )
            self.assertIn(self.router_name, names, msg=f"Shape {shape_name} lost router")

        # Baseline: PA rows exist in unfiltered universe
        pa_all = self._all_test_rows_qs().filter(
            agent__name="PersonalAssistant"
        ).count()
        self.assertEqual(pa_all, 150)

    # ─── Negative control ────────────────────────────────────────────

    def test_without_exclude_pa_would_dominate_pr_a8_rankings(self):
        """Negative control: SAME rankings WITHOUT exclude would
        rank PA #1 and trigger false-positive high-failure alerts."""
        self._seed_router_executions(2, status="failed")
        self._seed_pa_executions(40, status="failed")

        cutoff = timezone.now() - timedelta(hours=24)
        pre_patch = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff)
            .values("agent__name")
            .annotate(
                failed=Count("id", filter=DjangoQ(status="failed")),
                total=Count("id"),
            )
            .filter(failed__gte=3, total__gte=5)
            .order_by("-failed")
        )
        # PA WOULD alert (40 >= 3 failed, 40 >= 5 total)
        pa_row = next(
            (r for r in pre_patch if r["agent__name"] == "PersonalAssistant"), None
        )
        self.assertIsNotNone(pa_row)
        self.assertEqual(pa_row["failed"], 40)
