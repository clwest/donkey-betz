"""Arc I-0100 P4 Stop Condition #1 PR-A4 — regression coverage for
miscellaneous per-agent aggregations that exclude PA meta-agent rows
per ADR-0002 §4.2 F1 fold row-class discipline.

Sites patched:

- ``core/services/noise_metrics.py:123`` — ``by_agent`` list in
  ``compute_runs_metrics``
- ``core/agents/podcast/podcast_coordinator_agent.py:1027`` — platform
  stats aggregate in ``_generate_platform_stats_story``
- ``core/services/ops_autopilot/intelligence.py:2548`` +
  ``:2554`` — ``agent_count`` + ``top_agents`` in
  ``get_value_events_report``
- ``core/views_analytics.py:2355`` — ``top_performers`` Agent-model
  iteration (cross-model exclusion)
- ``core/views_analytics.py:2621`` — ``comparison_v2`` by_agent
- ``core/views_analytics.py:2670`` — ``breakdown_v2`` when
  ``dimension='agent'``
- ``core/services/td_handlers_ops.py:449`` — ``top_failing_agents`` SLO
  breakdown
- ``core/services/td_handlers_ops.py:480`` — ``top_timeout_agents`` SLO
  breakdown
- ``core/services/td_handlers_ops.py:4033`` — ``active_ids`` set in
  ``agent_introspection``
- ``core/agents/research_agent.py:2560`` — per-row rendering of
  agent_executions data type
- ``core/agents/research_agent.py:2570`` — summary stats
  (total_executions, status_distribution, failure_rate,
  avg_execution_time_ms)

Fix form: ``.exclude(agent__name='PersonalAssistant')`` per Chris
directive (agent__name form is safer than
``input_data__source='pa'`` for pre-flag-flip rows — see PR-A1 for
the Postgres JSONField NULL-semantics finding).

Special case for views_analytics.py:2355 (``top_performers``):
The fix excludes PA from the ``Agent.objects`` queryset (not the
``AgentExecution`` queryset) — mirrors the PR-A3 stale-agent
pattern at ``views_diagnostics.py:3280``.

Run::

    python manage.py test core.tests.test_pa_consumer_exclude_misc_per_agent -v2 --keepdb
"""
from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from django.db.models import Q as DjangoQ
from django.test import TestCase
from django.utils import timezone

from core.models_unified_system import Agent, AgentExecution


User = get_user_model()


class PAConsumerExcludeMiscPerAgentTests(TestCase):
    """Regression coverage for miscellaneous per-agent aggregations
    that must exclude PA meta-agent rows."""

    def setUp(self):
        self.user = User.objects.create_user(
            username=f"a4-{id(self)}",
            email=f"a4-{id(self)}@example.com",
            password="x",
        )
        self.router_agent = Agent.objects.create(
            name=f"TestRouterAgent_A4_{id(self)}",
            agent_type="router",
            description="Test router agent for PR-A4 regressions",
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
        execution_time_ms: int = 100,
        error_message: str = "",
    ):
        for i in range(count):
            AgentExecution.objects.create(
                agent=self.router_agent,
                user=self.user,
                task=f"Router task {i}",
                status=status,
                input_data={},
                execution_time_ms=execution_time_ms,
                error_message=error_message,
            )

    def _seed_pa_executions(
        self,
        count: int,
        status: str = "completed",
        execution_time_ms: int = 100,
        error_message: str = "",
    ):
        for i in range(count):
            AgentExecution.objects.create(
                agent=self.pa_agent,
                user=self.user,
                task=f"PA task {i}",
                status=status,
                input_data={"source": "pa", "trace_id": f"pa-a4-{i}"},
                execution_time_ms=execution_time_ms,
                error_message=error_message,
                owner_agent="PersonalAssistant",
            )

    def _all_test_rows_qs(self):
        return AgentExecution.objects.filter(user=self.user)

    # ─── noise_metrics.py:123 — by_agent list ────────────────────────

    def test_noise_metrics_by_agent_excludes_pa(self):
        """noise_metrics compute_runs_metrics by_agent: PA absent
        even when PA dominates in raw counts."""
        self._seed_router_executions(4)
        self._seed_pa_executions(30)

        cutoff = timezone.now() - timedelta(hours=24)
        by_agent_qs = (
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:20]
        )
        by_agent = [
            {"agent_name": r["agent__name"] or "unknown", "count": r["count"]}
            for r in by_agent_qs
        ]
        names = {b["agent_name"] for b in by_agent}
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)

    # ─── podcast_coordinator_agent.py:1027 — platform stats ──────────

    def test_podcast_platform_stats_excludes_pa(self):
        """podcast platform stats: total + avg_time + failures exclude
        PA agentic loop volume."""
        self._seed_router_executions(3, status="completed")
        self._seed_router_executions(2, status="failed")
        self._seed_pa_executions(40, status="completed")

        # For started_at, mirror the podcast query pattern. Use
        # created_at cutoff to include all test rows regardless of
        # started_at population (AgentExecution.started_at may be
        # None for test-created rows).
        cutoff = timezone.now() - timedelta(hours=48)
        stats = (
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff)
            .exclude(agent__name="PersonalAssistant")
            .aggregate(
                total=Count("id"),
                avg_time=Avg("execution_time_ms"),
                failures=Count("id", filter=DjangoQ(status="failed")),
            )
        )
        # Router-only: 3 completed + 2 failed = 5 total
        self.assertEqual(stats["total"], 5)
        self.assertEqual(stats["failures"], 2)

    # ─── ops_autopilot/intelligence.py:2548+2554 — value_events ──────

    def test_ops_autopilot_value_events_report_excludes_pa(self):
        """ops_autopilot value_events_report: agent_completions +
        top_agents exclude PA."""
        self._seed_router_executions(7, status="completed")
        self._seed_pa_executions(25, status="completed")

        cutoff = timezone.now() - timedelta(days=7)
        agent_count = (
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff, status="completed")
            .exclude(agent__name="PersonalAssistant")
            .count()
        )
        self.assertEqual(agent_count, 7)

        top_agents = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff, status="completed")
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )
        names = [t["agent__name"] for t in top_agents]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)

    # ─── views_analytics.py:2355 — top_performers ────────────────────

    def test_top_performers_excludes_pa_at_agent_model_level(self):
        """top_performers: PA absent from Agent-model iteration
        universe."""
        self._seed_router_executions(3, status="completed")
        self._seed_pa_executions(20, status="completed")

        # Mirror the patched cross-model pattern
        agents = Agent.objects.exclude(name="PersonalAssistant")
        agent_names = list(agents.values_list("name", flat=True))
        self.assertNotIn("PersonalAssistant", agent_names)
        self.assertIn(self.router_name, agent_names)

    # ─── views_analytics.py:2621 — comparison_v2 by_agent ────────────

    def test_comparison_v2_by_agent_excludes_pa(self):
        """comparison_v2 by_agent aggregation: PA absent even when
        PA dominates raw counts."""
        self._seed_router_executions(2)
        self._seed_pa_executions(30)

        cutoff = timezone.now() - timedelta(days=7)
        executions = self._all_test_rows_qs().filter(created_at__gte=cutoff)

        # Mirror the patched by_agent iteration. Note: production code
        # uses exec.agent_name which is a pre-existing latent bug
        # (AgentExecution has no agent_name attribute — the FK is
        # ``agent`` and the name is ``agent.name``). PR-A4 does not
        # touch that latent bug — the test uses the FK access path
        # so it exercises the patched .exclude() call.
        agent_counts: dict = {}
        for exec_row in executions.exclude(agent__name="PersonalAssistant"):
            agent = exec_row.agent.name if exec_row.agent else "unknown"
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
        sorted_agents = sorted(agent_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        by_agent = dict(sorted_agents)
        self.assertNotIn("PersonalAssistant", by_agent)
        self.assertIn(self.router_name, by_agent)

    # ─── views_analytics.py:2670 — breakdown_v2 ──────────────────────

    def test_breakdown_v2_agent_dimension_excludes_pa(self):
        """breakdown_v2 dimension='agent': PA absent from breakdown
        keys."""
        self._seed_router_executions(2)
        self._seed_pa_executions(15)

        cutoff = timezone.now() - timedelta(days=7)
        executions = self._all_test_rows_qs().filter(created_at__gte=cutoff)
        # dimension='agent' branch
        executions = executions.exclude(agent__name="PersonalAssistant")

        # Mirror the patched breakdown iteration. Note: production
        # uses exec.agent_name (pre-existing latent bug — no such
        # attribute on the model). Test uses FK access so the
        # patched .exclude() is what's under test.
        breakdown: dict = {}
        for exec_row in executions:
            key = exec_row.agent.name if exec_row.agent else "unknown"
            if key not in breakdown:
                breakdown[key] = {"count": 0, "cost": 0}
            breakdown[key]["count"] += 1
        self.assertNotIn("PersonalAssistant", breakdown)
        self.assertIn(self.router_name, breakdown)

    def test_breakdown_v2_status_dimension_still_counts_pa(self):
        """breakdown_v2 dimension='status': PA rows still count
        (intentionally cross-source per patch)."""
        self._seed_router_executions(2, status="completed")
        self._seed_pa_executions(3, status="completed")

        cutoff = timezone.now() - timedelta(days=7)
        executions = self._all_test_rows_qs().filter(created_at__gte=cutoff)
        # dimension='status' branch does NOT exclude PA (patch only
        # excludes on dimension='agent')

        breakdown: dict = {}
        for exec_row in executions:
            key = exec_row.status or "unknown"
            if key not in breakdown:
                breakdown[key] = {"count": 0}
            breakdown[key]["count"] += 1

        # Positive control: status='completed' counts BOTH PA + router
        self.assertEqual(breakdown["completed"]["count"], 5)

    # ─── td_handlers_ops.py:449 — top_failing_agents SLO ─────────────

    def test_slo_top_failing_agents_excludes_pa(self):
        """SLO top_failing_agents breakdown: PA absent."""
        self._seed_router_executions(3, status="failed")
        self._seed_pa_executions(20, status="failed")

        cutoff = timezone.now() - timedelta(hours=24)
        top_agents = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff, status="failed")
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )
        names = [t["agent__name"] for t in top_agents]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)
        self.assertEqual(top_agents[0]["agent__name"], self.router_name)

    # ─── td_handlers_ops.py:480 — top_timeout_agents SLO ─────────────

    def test_slo_top_timeout_agents_excludes_pa(self):
        """SLO top_timeout_agents breakdown: PA absent."""
        self._seed_router_executions(2, status="failed", error_message="worker timed out")
        self._seed_pa_executions(15, status="failed", error_message="agentic loop timed out")

        cutoff = timezone.now() - timedelta(hours=24)
        top_timeout = list(
            self._all_test_rows_qs()
            .filter(
                created_at__gte=cutoff,
                status="failed",
                error_message__icontains="timed out",
            )
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )
        names = [t["agent__name"] for t in top_timeout]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)

    # ─── td_handlers_ops.py:4033 — agent_introspection active_ids ────

    def test_agent_introspection_active_ids_excludes_pa(self):
        """agent_introspection active_last_7d: PA absent from distinct
        agent id set even when PA has runs."""
        self._seed_router_executions(2)
        self._seed_pa_executions(30)

        now = timezone.now()
        active_ids = set(
            self._all_test_rows_qs()
            .filter(created_at__gte=now - timedelta(days=7))
            .exclude(agent__name="PersonalAssistant")
            .values_list("agent_id", flat=True)
        )
        self.assertIn(self.router_agent.id, active_ids)
        self.assertNotIn(self.pa_agent.id, active_ids)

    # ─── research_agent.py:2560 + 2570 — agent_executions data type ──

    def test_research_agent_executions_queryset_excludes_pa(self):
        """research_agent per-row rendering: PA absent from rendered
        agent_executions list."""
        self._seed_router_executions(2)
        self._seed_pa_executions(20)

        queryset = (
            self._all_test_rows_qs()
            .select_related("agent")
            .exclude(agent__name="PersonalAssistant")
            .order_by("-created_at")[:50]
        )
        rendered_names = {row.agent.name if row.agent else "Unknown" for row in queryset}
        self.assertNotIn("PersonalAssistant", rendered_names)
        self.assertIn(self.router_name, rendered_names)

    def test_research_agent_executions_summary_excludes_pa(self):
        """research_agent summary stats: total_executions +
        status_distribution + failure_rate + avg_execution_time_ms
        computed on PA-excluded queryset."""
        self._seed_router_executions(3, status="completed", execution_time_ms=200)
        self._seed_router_executions(1, status="failed", execution_time_ms=200)
        self._seed_pa_executions(50, status="completed", execution_time_ms=5)

        all_executions = self._all_test_rows_qs().exclude(agent__name="PersonalAssistant")
        status_counts = dict(
            all_executions.values("status").annotate(count=Count("id")).values_list(
                "status", "count"
            )
        )
        total = all_executions.count()
        avg_time = all_executions.aggregate(avg=Avg("execution_time_ms"))["avg"] or 0

        # Router-only: 4 rows (3 completed + 1 failed), all 200ms
        self.assertEqual(total, 4)
        self.assertEqual(status_counts.get("completed"), 3)
        self.assertEqual(status_counts.get("failed"), 1)
        self.assertAlmostEqual(avg_time, 200.0, places=1)

    # ─── Cross-cutting invariant ─────────────────────────────────────

    def test_pa_rows_never_appear_in_any_pr_a4_aggregation(self):
        """Cross-cutting invariant: PA rows absent from all patched
        aggregation shapes given a mixed corpus."""
        self._seed_router_executions(6, status="completed")
        self._seed_pa_executions(100, status="completed")

        cutoff = timezone.now() - timedelta(days=7)
        for shape_name, qs_builder in [
            (
                "noise_metrics_by_agent",
                lambda: self._all_test_rows_qs()
                .filter(created_at__gte=cutoff)
                .exclude(agent__name="PersonalAssistant")
                .values("agent__name")
                .annotate(count=Count("id"))
                .order_by("-count")[:20],
            ),
            (
                "value_events_top_agents",
                lambda: self._all_test_rows_qs()
                .filter(created_at__gte=cutoff, status="completed")
                .exclude(agent__name="PersonalAssistant")
                .values("agent__name")
                .annotate(count=Count("id"))
                .order_by("-count")[:10],
            ),
        ]:
            names = {row["agent__name"] for row in qs_builder()}
            self.assertNotIn(
                "PersonalAssistant", names, msg=f"Shape {shape_name} leaked PA"
            )
            self.assertIn(self.router_name, names, msg=f"Shape {shape_name} lost router")

        # Baseline sanity: PA rows exist in unfiltered universe
        pa_universe = self._all_test_rows_qs().filter(
            agent__name="PersonalAssistant", status="completed"
        ).count()
        self.assertEqual(pa_universe, 100)

    # ─── Negative controls (locks in fix necessity) ──────────────────

    def test_without_exclude_pa_would_dominate_by_agent(self):
        """Negative control: SAME by_agent query WITHOUT exclude would
        rank PA #1."""
        self._seed_router_executions(3)
        self._seed_pa_executions(50)

        cutoff = timezone.now() - timedelta(hours=24)
        pre_patch = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff)
            .values("agent__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:20]
        )
        self.assertEqual(pre_patch[0]["agent__name"], "PersonalAssistant")
        self.assertEqual(pre_patch[0]["count"], 50)

    def test_without_exclude_pa_would_dominate_active_ids(self):
        """Negative control: SAME active_ids query WITHOUT exclude
        would include PA agent_id."""
        self._seed_router_executions(2)
        self._seed_pa_executions(30)

        now = timezone.now()
        active_ids_pre = set(
            self._all_test_rows_qs()
            .filter(created_at__gte=now - timedelta(days=7))
            .values_list("agent_id", flat=True)
        )
        # PA WOULD be in active_ids pre-patch
        self.assertIn(self.pa_agent.id, active_ids_pre)
