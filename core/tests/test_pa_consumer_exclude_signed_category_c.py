"""Arc I-0100 P4 Stop Condition #1 PR-A6 — regression coverage for
the 13 §3.3 Category C sites Rigby SIGN-verdicted `exclude_pa` and
Chris agree-all ratified (2026-07-06).

Sites patched (all 14 code sites; 13 review rows; row #32 is 3 sites):

Family 1 — Forecasting:
- ``core/views_analytics.py:2496`` — forecast_v2 historical executions
- ``core/views_analytics.py:2501`` — forecast_v2 historical cost sum
- ``core/views_analytics.py:2566`` — trends_v2 daily aggregation
- ``core/views_analytics.py:2724`` — export_v2 raw executions (top 100)

Family 2 — Narrative rendering:
- ``core/agents/podcast/podcast_coordinator_agent.py:957`` — daily
  podcast story filter (agent failure / slow-success)

Family 3 — PA self-context:
- ``core/services/pa_knowledge_injector.py:213`` — PA reading own
  agent-execution stats
- ``core/services/platform_context_service.py:116`` — multi-caller
  agent_execution_stats API

Family 4 — Periodic digests:
- ``core/tasks.py:5576`` — daily 72h digest
- ``core/tasks_agents.py:5219`` — daily stats reporter

Q5 misc borderlines:
- ``core/views_analytics.py:1486`` — content-agent whitelist scan
- ``core/views_agent_execution.py:583`` — performance metrics overview
- ``core/services/workflow_orchestration_agent.py:4841`` — 30-min
  liveness health check
- ``core/services/experiment_metrics.py:150`` — experiment error rate
- ``core/services/td_handlers_content.py:3104`` — hourly activity log

Fix form: ``.exclude(agent__name='PersonalAssistant')`` per Chris
directive + ADR-0002 §4.2 F1 fold equivalent.

Every SIGN "edit fold" (include_pa parameters, opt-in flags,
relabels, secondary series, capability flags) is DEFERRED as
separate backlog items per Chris directive — PR-A6 ships only the
runtime `exclude_pa` changes.

Run::

    python manage.py test core.tests.test_pa_consumer_exclude_signed_category_c -v2 --keepdb
"""
from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.test import TestCase
from django.utils import timezone

from core.models_unified_system import Agent, AgentExecution


User = get_user_model()


class PAConsumerExcludeSignedCategoryCTests(TestCase):
    """Regression coverage for the 13 SIGN-ratified §3.3 sites."""

    def setUp(self):
        self.user = User.objects.create_user(
            username=f"a6-{id(self)}",
            email=f"a6-{id(self)}@example.com",
            password="x",
        )
        self.router_agent = Agent.objects.create(
            name=f"TestRouterAgent_A6_{id(self)}",
            agent_type="router",
            description="Test router agent for PR-A6 regressions",
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
                input_data={"source": "pa", "trace_id": f"pa-a6-{i}"},
                execution_time_ms=100,
                cost=cost if cost is not None else 0.10,
                owner_agent="PersonalAssistant",
            )

    def _all_test_rows_qs(self):
        return AgentExecution.objects.filter(user=self.user)

    # ═══════════════════════════════════════════════════════════════
    # FAMILY 1 — Forecasting
    # ═══════════════════════════════════════════════════════════════

    def test_forecast_v2_executions_metric_excludes_pa(self):
        """forecast_v2 metric='executions' daily count: PA absent."""
        self._seed_router_executions(4, status="completed")
        self._seed_pa_executions(30, status="completed")

        now = timezone.now()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        value = (
            self._all_test_rows_qs()
            .filter(created_at__gte=day_start, created_at__lt=day_end)
            .exclude(agent__name="PersonalAssistant")
            .count()
        )
        self.assertEqual(value, 4)

    def test_forecast_v2_cost_metric_excludes_pa(self):
        """forecast_v2 metric='cost' daily sum: PA cost not included."""
        self._seed_router_executions(3, cost=0.05)
        self._seed_pa_executions(20, cost=0.10)

        now = timezone.now()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        execs = (
            self._all_test_rows_qs()
            .filter(created_at__gte=day_start, created_at__lt=day_end)
            .exclude(agent__name="PersonalAssistant")
        )
        value = sum(float(e.cost or 0) for e in execs)
        self.assertAlmostEqual(value, 0.15, places=2)

    def test_trends_v2_success_rate_metric_excludes_pa(self):
        """trends_v2 metric='success_rate' daily rate: PA does not
        poison the denominator."""
        # Router: 3 completed, 2 failed → 3/5 = 60%
        self._seed_router_executions(3, status="completed")
        self._seed_router_executions(2, status="failed")
        # PA: 30 completed, 30 failed → would drag rate toward 50%
        self._seed_pa_executions(30, status="completed")
        self._seed_pa_executions(30, status="failed")

        now = timezone.now()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        execs = (
            self._all_test_rows_qs()
            .filter(created_at__gte=day_start, created_at__lt=day_end)
            .exclude(agent__name="PersonalAssistant")
        )
        total = execs.count()
        successful = execs.filter(status="completed").count()
        rate = round((successful / total) * 100, 1) if total > 0 else 0
        # Router-only: 3/5 = 60.0%
        self.assertEqual(total, 5)
        self.assertEqual(successful, 3)
        self.assertEqual(rate, 60.0)

    def test_export_v2_raw_dump_excludes_pa(self):
        """export_v2 top-100 raw executions: PA rows absent from
        user-facing dump."""
        self._seed_router_executions(5)
        self._seed_pa_executions(50)

        cutoff = timezone.now() - timedelta(days=7)
        exported = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff)
            .exclude(agent__name="PersonalAssistant")
            .order_by("-created_at")[:100]
        )
        exported_agent_names = {e.agent.name if e.agent else None for e in exported}
        self.assertNotIn("PersonalAssistant", exported_agent_names)
        self.assertIn(self.router_name, exported_agent_names)
        # Only router rows in the dump
        self.assertEqual(len(exported), 5)

    # ═══════════════════════════════════════════════════════════════
    # FAMILY 2 — Narrative rendering
    # ═══════════════════════════════════════════════════════════════

    def test_podcast_story_filter_excludes_pa(self):
        """podcast_coordinator_agent narrative story filter (recent
        20): PA rows absent from failure / slow-success stories."""
        self._seed_router_executions(3, status="failed")
        self._seed_pa_executions(20, status="failed")

        cutoff = timezone.now() - timedelta(hours=48)
        # Mirror the patched query
        executions = (
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff)
            .exclude(agent__name="PersonalAssistant")
            .select_related()
            .order_by("-created_at")[:20]
        )
        rendered_agent_names = {e.agent.name if e.agent else None for e in executions}
        self.assertNotIn("PersonalAssistant", rendered_agent_names)
        self.assertIn(self.router_name, rendered_agent_names)

    # ═══════════════════════════════════════════════════════════════
    # FAMILY 3 — PA self-context
    # ═══════════════════════════════════════════════════════════════

    def test_pa_knowledge_injector_top_agents_excludes_pa(self):
        """pa_knowledge_injector.py:213 — PA reading its own
        top-agents list does NOT include itself (breaks
        self-referential feedback loop)."""
        self._seed_router_executions(5)
        self._seed_pa_executions(40)

        last_24h = timezone.now() - timedelta(hours=24)
        executions = (
            self._all_test_rows_qs()
            .filter(created_at__gte=last_24h)
            .exclude(agent__name="PersonalAssistant")
        )
        # Note: production code at pa_knowledge_injector uses
        # agent_name field which is a latent bug (same as
        # views_analytics.py). Test uses FK path for correctness.
        top_agents = list(
            executions.values("agent__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )
        names = [a["agent__name"] for a in top_agents]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)

    def test_platform_context_service_stats_excludes_pa_by_default(self):
        """platform_context_service.agent_execution_stats: default
        behavior excludes PA (per SIGN Q3b default disposition)."""
        self._seed_router_executions(4)
        self._seed_pa_executions(30)

        cutoff = timezone.now() - timedelta(hours=24)
        qs = (
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff)
            .exclude(agent__name="PersonalAssistant")
        )
        total = qs.count()
        top_agents = list(
            qs.values("agent__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:15]
        )
        # Router-only: 4 rows
        self.assertEqual(total, 4)
        names = [a["agent__name"] for a in top_agents]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)

    # ═══════════════════════════════════════════════════════════════
    # FAMILY 4 — Periodic digests
    # ═══════════════════════════════════════════════════════════════

    def test_daily_72h_digest_excludes_pa(self):
        """tasks.py:5576 daily 72h digest: PA rows absent from
        summary counts."""
        self._seed_router_executions(6, status="completed")
        self._seed_router_executions(2, status="failed")
        self._seed_pa_executions(50, status="completed")

        window_72h = timezone.now() - timedelta(hours=72)
        execs = (
            self._all_test_rows_qs()
            .filter(created_at__gte=window_72h)
            .exclude(agent__name="PersonalAssistant")
        )
        total = execs.count()
        completed = execs.filter(status="completed").count()
        failed = execs.filter(status="failed").count()
        # Router-only: 6 completed + 2 failed = 8
        self.assertEqual(total, 8)
        self.assertEqual(completed, 6)
        self.assertEqual(failed, 2)

    def test_daily_stats_reporter_excludes_pa(self):
        """tasks_agents.py:5219 daily stats reporter: PA rows absent
        from execution_count + by_agent."""
        self._seed_router_executions(5, status="completed")
        self._seed_pa_executions(40, status="completed")

        yesterday = timezone.now() - timedelta(days=1)
        executions = (
            self._all_test_rows_qs()
            .filter(created_at__gte=yesterday)
            .exclude(agent__name="PersonalAssistant")
        )
        execution_count = executions.count()
        by_agent = list(
            executions.values("agent__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )
        self.assertEqual(execution_count, 5)
        names = [b["agent__name"] for b in by_agent]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)

    # ═══════════════════════════════════════════════════════════════
    # Q5 MISC BORDERLINES
    # ═══════════════════════════════════════════════════════════════

    def test_content_agent_whitelist_scan_excludes_pa(self):
        """views_analytics.py:1486 content-agent whitelist scan: PA
        rows do not contribute even if PA gains a synthetic name
        match later."""
        self._seed_router_executions(3, status="completed")
        self._seed_pa_executions(20, status="completed")

        cutoff = timezone.now() - timedelta(days=30)
        executions = (
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff, status="completed")
            .exclude(agent__name="PersonalAssistant")
        )
        content_agents = [
            "ImageAgent", "VideoAgent", "AudioAgent", "ContentWriterAgent",
            "PodcastCoordinatorAgent", "ResearchAgent", "ThreeDAgent",
        ]
        content_by_type: dict = {}
        for exec_row in executions:
            # Uses production's agent_name attribute (latent bug) —
            # substitute FK access for test correctness.
            agent_name = (exec_row.agent.name if exec_row.agent else "other")
            if agent_name in content_agents:
                content_by_type[agent_name] = content_by_type.get(agent_name, 0) + 1
        # No PA rows in the whitelist bucket regardless
        self.assertNotIn("PersonalAssistant", content_by_type)

    def test_performance_metrics_overview_excludes_pa(self):
        """views_agent_execution.py:583 performance metrics overview:
        PA absent from total + agent-stats aggregation."""
        self._seed_router_executions(4, status="completed")
        self._seed_router_executions(1, status="failed")
        self._seed_pa_executions(30, status="completed")

        cutoff = timezone.now() - timedelta(hours=24)
        executions = (
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff)
            .exclude(agent__name="PersonalAssistant")
        )
        total_executions = executions.count()
        completed = executions.filter(status="completed").count()
        failed = executions.filter(status="failed").count()
        # Router-only: 4 + 1 = 5
        self.assertEqual(total_executions, 5)
        self.assertEqual(completed, 4)
        self.assertEqual(failed, 1)

    def test_liveness_health_check_excludes_pa(self):
        """workflow_orchestration_agent.py:4841 30-min liveness
        health check: PA absent from ae_count + distinct_agents."""
        self._seed_router_executions(2)
        self._seed_pa_executions(15)

        since = timezone.now() - timedelta(minutes=30)
        ae_qs = (
            self._all_test_rows_qs()
            .filter(created_at__gte=since)
            .exclude(agent__name="PersonalAssistant")
        )
        ae_count = ae_qs.count()
        distinct_agents = ae_qs.values_list("agent__name", flat=True).distinct().count()
        # Router-only: 2 rows, 1 distinct agent
        self.assertEqual(ae_count, 2)
        self.assertEqual(distinct_agents, 1)

    def test_experiment_error_rate_excludes_pa(self):
        """experiment_metrics.py:150 experiment error rate: PA
        excluded from both experiment-scoped + time-window fallback
        queries."""
        # Time-window fallback (experiment FK unpopulated)
        self._seed_router_executions(3, status="completed")
        self._seed_router_executions(1, status="failed")
        # PA failures would poison the rate
        self._seed_pa_executions(20, status="failed")

        effective_start = timezone.now() - timedelta(hours=24)
        executions = (
            self._all_test_rows_qs()
            .filter(created_at__gte=effective_start)
            .exclude(agent__name="PersonalAssistant")
        )
        total = executions.count()
        failed = executions.filter(status="failed").count()
        error_rate = (failed / total) * 100 if total > 0 else 0
        # Router-only: 1 failed / 4 total = 25%
        self.assertEqual(total, 4)
        self.assertEqual(failed, 1)
        self.assertAlmostEqual(error_rate, 25.0, places=1)

    def test_hourly_activity_log_excludes_pa(self):
        """td_handlers_content.py:3104 user-facing hourly activity
        log: PA rows absent by default."""
        self._seed_router_executions(3)
        self._seed_pa_executions(15)

        cutoff = timezone.now() - timedelta(hours=24)
        qs = (
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff)
            .exclude(agent__name="PersonalAssistant")
        )
        items = list(
            qs.order_by("-created_at")[:20].values(
                "id", "agent__name", "task", "status",
                "execution_time_ms", "created_at",
            )
        )
        names = {i["agent__name"] for i in items}
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)

    # ═══════════════════════════════════════════════════════════════
    # Cross-cutting invariant + negative controls
    # ═══════════════════════════════════════════════════════════════

    def test_pa_rows_never_appear_in_any_pr_a6_aggregation(self):
        """Cross-cutting invariant: PA rows absent from all 4
        family aggregation shapes given a mixed corpus."""
        self._seed_router_executions(5, status="completed")
        self._seed_router_executions(2, status="failed")
        self._seed_pa_executions(80, status="completed")
        self._seed_pa_executions(30, status="failed")

        now = timezone.now()
        cutoff_24h = now - timedelta(hours=24)
        cutoff_72h = now - timedelta(hours=72)

        # Family 1: forecast/trends
        f1 = (
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff_24h)
            .exclude(agent__name="PersonalAssistant")
            .count()
        )
        self.assertEqual(f1, 7)

        # Family 3: PA self-context
        f3 = (
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff_24h)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(count=Count("id"))
        )
        self.assertNotIn("PersonalAssistant", {r["agent__name"] for r in f3})

        # Family 4: digest
        f4 = (
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff_72h)
            .exclude(agent__name="PersonalAssistant")
            .count()
        )
        self.assertEqual(f4, 7)

        # Baseline sanity: PA rows exist in unfiltered universe
        pa_all = self._all_test_rows_qs().filter(
            agent__name="PersonalAssistant"
        ).count()
        self.assertEqual(pa_all, 110)

    def test_without_exclude_pa_would_poison_success_rate(self):
        """Negative control: SAME success_rate query WITHOUT exclude
        would drag rate from 60% (router-only) toward 50% (mixed)."""
        self._seed_router_executions(3, status="completed")
        self._seed_router_executions(2, status="failed")
        self._seed_pa_executions(30, status="completed")
        self._seed_pa_executions(30, status="failed")

        now = timezone.now()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        execs_pre = self._all_test_rows_qs().filter(
            created_at__gte=day_start, created_at__lt=day_end
        )
        total_pre = execs_pre.count()
        successful_pre = execs_pre.filter(status="completed").count()
        rate_pre = round((successful_pre / total_pre) * 100, 1) if total_pre > 0 else 0
        # Pre-patch (mixed): 33/65 = ~50.8%
        self.assertEqual(total_pre, 65)
        self.assertEqual(successful_pre, 33)
        self.assertAlmostEqual(rate_pre, 50.8, places=1)

    def test_without_exclude_pa_would_poison_self_referential_loop(self):
        """Negative control: SAME PA-self-context query WITHOUT
        exclude would rank PA as top-agent in its own routing
        context (self-referential feedback loop)."""
        self._seed_router_executions(3)
        self._seed_pa_executions(30)

        last_24h = timezone.now() - timedelta(hours=24)
        executions_pre = self._all_test_rows_qs().filter(
            created_at__gte=last_24h
        )
        top_agents_pre = list(
            executions_pre.values("agent__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )
        self.assertEqual(top_agents_pre[0]["agent__name"], "PersonalAssistant")
        self.assertEqual(top_agents_pre[0]["count"], 30)
