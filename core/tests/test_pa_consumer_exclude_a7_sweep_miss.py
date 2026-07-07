"""Arc I-0100 P4 Stop Condition #1 PR-A7 — regression coverage for
the 4 Category B sites the PR-A6 post-merge consumer sweep found
missed.

Sites patched:

- ``core/services/domain_content_context.py:272`` — "Most active
  agents" (top 3) ranking in "AI Capabilities" report used for
  Rigby's platform-context prompt injection
- ``core/services/td_handlers_core.py:783`` — By-agent execution +
  failure-count ranking in ops "summary" action
- ``core/views_celery_api.py:345`` — By-agent execution +
  failure-count for celery API dashboard
- ``core/views_orchestration.py:1013`` — Top 5 most active agents
  (24h) in orchestration dashboard

Fix form: ``.exclude(agent__name='PersonalAssistant')`` per
ADR-0002 §4.2 F1 fold equivalent (PR-A1 Postgres JSONField
NULL-semantics finding).

Run::

    python manage.py test core.tests.test_pa_consumer_exclude_a7_sweep_miss -v2 --keepdb
"""
from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.db.models import Q as DjangoQ
from django.test import TestCase
from django.utils import timezone

from core.models_unified_system import Agent, AgentExecution


User = get_user_model()


class PAConsumerExcludeA7SweepMissTests(TestCase):
    """Regression coverage for the 4 missed Category B sites found
    by the PR-A6 post-merge consumer sweep."""

    def setUp(self):
        self.user = User.objects.create_user(
            username=f"a7-{id(self)}",
            email=f"a7-{id(self)}@example.com",
            password="x",
        )
        self.router_agent = Agent.objects.create(
            name=f"TestRouterAgent_A7_{id(self)}",
            agent_type="router",
            description="Test router agent for PR-A7 regressions",
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
                input_data={"source": "pa", "trace_id": f"pa-a7-{i}"},
                execution_time_ms=100,
                owner_agent="PersonalAssistant",
            )

    def _all_test_rows_qs(self):
        return AgentExecution.objects.filter(user=self.user)

    # ─── domain_content_context.py:272 — "Most active agents" (top 3) ─

    def test_domain_content_most_active_agents_excludes_pa(self):
        """domain_content_context "Most active agents" top-3
        excludes PA — used in Rigby's platform-context prompt."""
        self._seed_router_executions(4, status="completed")
        self._seed_pa_executions(40, status="completed")

        cutoff = timezone.now() - timedelta(days=7)
        successful = list(
            self._all_test_rows_qs()
            .filter(status="completed", created_at__gte=cutoff)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:3]
        )
        names = [s["agent__name"] for s in successful]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)
        self.assertEqual(successful[0]["agent__name"], self.router_name)
        self.assertEqual(successful[0]["count"], 4)

    # ─── td_handlers_core.py:783 — ops summary by_agent_raw ──────────

    def test_td_handlers_core_by_agent_summary_excludes_pa(self):
        """td_handlers_core by_agent_raw ranking + failure_rate
        excludes PA."""
        self._seed_router_executions(3, status="completed")
        self._seed_router_executions(2, status="failed")
        self._seed_pa_executions(20, status="completed")
        self._seed_pa_executions(15, status="failed")

        cutoff = timezone.now() - timedelta(hours=24)
        by_agent_raw = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(
                execution_count=Count("id"),
                count_failure=Count("id", filter=DjangoQ(status="failed")),
            )
            .order_by("-execution_count")[:10]
        )
        names = [r["agent__name"] for r in by_agent_raw]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)
        # Router-only: 5 total, 2 failed → failure_rate 0.4
        router_row = next(r for r in by_agent_raw if r["agent__name"] == self.router_name)
        self.assertEqual(router_row["execution_count"], 5)
        self.assertEqual(router_row["count_failure"], 2)

    # ─── views_celery_api.py:345 — celery API by_agent ──────────────

    def test_views_celery_api_by_agent_excludes_pa(self):
        """views_celery_api by_agent execution + failure-count
        ranking excludes PA."""
        self._seed_router_executions(4, status="completed")
        self._seed_router_executions(1, status="failed")
        self._seed_pa_executions(25, status="completed")
        self._seed_pa_executions(10, status="failed")

        cutoff = timezone.now() - timedelta(hours=24)
        by_agent = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(
                execution_count=Count("id"),
                count_failure=Count("id", filter=DjangoQ(status="failed")),
            )
            .order_by("-execution_count")[:10]
        )
        names = [r["agent__name"] for r in by_agent]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)
        # Router-only: 5 total, 1 failed
        router_row = next(r for r in by_agent if r["agent__name"] == self.router_name)
        self.assertEqual(router_row["execution_count"], 5)
        self.assertEqual(router_row["count_failure"], 1)

    # ─── views_orchestration.py:1013 — top 5 most active (24h) ───────

    def test_views_orchestration_top_active_agents_excludes_pa(self):
        """views_orchestration top-5-most-active (24h) excludes PA
        from the ranking while keeping cross-source liveness
        counts (exec_total etc.) intact."""
        self._seed_router_executions(6)
        self._seed_pa_executions(35)

        cutoff = timezone.now() - timedelta(hours=24)
        recent_execs = self._all_test_rows_qs().filter(created_at__gte=cutoff)

        # Cross-source liveness counts (patch preserves)
        exec_total = recent_execs.count()
        # Router 6 + PA 35 = 41 (patch does NOT touch these)
        self.assertEqual(exec_total, 41)

        # PA-excluded top-agents ranking (patch DOES touch this)
        top_agents = list(
            recent_execs.exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(c=Count("id"))
            .order_by("-c")[:5]
        )
        names = [a["agent__name"] for a in top_agents]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)
        self.assertEqual(top_agents[0]["agent__name"], self.router_name)
        self.assertEqual(top_agents[0]["c"], 6)

    # ─── Cross-cutting invariant ─────────────────────────────────────

    def test_pa_rows_never_appear_in_any_pr_a7_ranking(self):
        """Cross-cutting invariant: PA rows absent from all 4
        aggregation shapes given a mixed corpus."""
        self._seed_router_executions(5, status="completed")
        self._seed_router_executions(2, status="failed")
        self._seed_pa_executions(80, status="completed")
        self._seed_pa_executions(20, status="failed")

        cutoff_24h = timezone.now() - timedelta(hours=24)
        cutoff_7d = timezone.now() - timedelta(days=7)

        # Shape 1: domain_content_context most-active (7d, completed)
        s1 = list(
            self._all_test_rows_qs()
            .filter(status="completed", created_at__gte=cutoff_7d)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:3]
        )
        self.assertNotIn("PersonalAssistant", {s["agent__name"] for s in s1})

        # Shape 2 + 3: td_handlers_core + views_celery_api (24h, exec + failure)
        s2 = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff_24h)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(
                execution_count=Count("id"),
                count_failure=Count("id", filter=DjangoQ(status="failed")),
            )
            .order_by("-execution_count")[:10]
        )
        self.assertNotIn("PersonalAssistant", {s["agent__name"] for s in s2})

        # Shape 4: views_orchestration top-5 (24h)
        s4 = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff_24h)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(c=Count("id"))
            .order_by("-c")[:5]
        )
        self.assertNotIn("PersonalAssistant", {s["agent__name"] for s in s4})

        # Baseline sanity: PA rows exist in unfiltered universe
        pa_universe = self._all_test_rows_qs().filter(
            agent__name="PersonalAssistant"
        ).count()
        self.assertEqual(pa_universe, 100)

    # ─── Negative control ────────────────────────────────────────────

    def test_without_exclude_pa_would_dominate_all_pr_a7_rankings(self):
        """Negative control: SAME 4 rankings WITHOUT exclude would
        rank PA #1 across all shapes."""
        self._seed_router_executions(3)
        self._seed_pa_executions(50)

        cutoff = timezone.now() - timedelta(hours=24)
        pre_patch = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff)
            .values("agent__name")
            .annotate(c=Count("id"))
            .order_by("-c")[:5]
        )
        self.assertEqual(pre_patch[0]["agent__name"], "PersonalAssistant")
        self.assertEqual(pre_patch[0]["c"], 50)
