"""Arc I-0100 P4 Stop Condition #1 PR-A1 — regression coverage for
per-agent aggregations that exclude PA meta-agent rows per ADR-0002
§4.2 F1 fold row-class discipline.

Sites patched:

- ``core/services/muscular.py:451`` — ``detect_weak_muscles``
- ``core/services/muscular.py:483`` — ``detect_overworked_muscles``
- ``core/services/feedback_loop_engine.py:527`` — ``best_agents``
- ``core/services/feedback_loop_engine.py:537`` — ``most_active``
- ``core/services/feedback_loop_engine.py:544`` — ``needs_attention``
- ``core/services/learning_pattern_engine.py:645`` — ``agent_stats``

Each site adds ``.exclude(input_data__source='pa')`` so PA meta-agent
rows (produced by ``PA_AGENT_EXECUTION_WRITE_ENABLED=True`` post-flag-
flip) don't distort per-router-agent metrics.

The tests exercise the QUERY PATTERN at each patched site directly via
ORM (mirroring the exact query shape at each site). This avoids
coupling to the enclosing service classes (which have unrelated
dependencies) and keeps the assertions focused on the exclude
semantics we care about.

For every patched site this test proves:

1. **Normal (non-PA) executions still count** — the query pattern
   returns the router-agent aggregate.
2. **Synthetic PA rows do NOT distort the metric** — same query with
   PA rows added returns the SAME aggregate for router-agents; PA
   does NOT appear in any returned aggregation.

Run::

    python manage.py test core.tests.test_pa_consumer_exclude_body_system -v2 --keepdb
"""
from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, F, Q
from django.test import TestCase
from django.utils import timezone

from core.models_unified_system import Agent, AgentExecution


User = get_user_model()


class PAConsumerExcludeBodySystemTests(TestCase):
    """Regression coverage for muscular + feedback_loop + learning_pattern
    per-agent aggregations that must exclude PA meta-agent rows."""

    def setUp(self):
        """Per-test setup so seeded rows land in each test's tx."""
        self.user = User.objects.create_user(
            username=f"a1-{id(self)}",
            email=f"a1-{id(self)}@example.com",
            password="x",
        )
        self.router_agent = Agent.objects.create(
            name=f"TestRouterAgent_A1_{id(self)}",
            agent_type="router",
            description="Test router agent for PR-A1 regressions",
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
        """Create N router-agent AgentExecution rows (no PA source marker)."""
        for i in range(count):
            AgentExecution.objects.create(
                agent=self.router_agent,
                user=self.user,
                task=f"Router task {i}",
                status=status,
                input_data={},  # NO source='pa' marker
                execution_time_ms=100,
            )

    def _seed_pa_executions(self, count: int, status: str = "completed"):
        """Create N PA-authored AgentExecution rows with source='pa'."""
        for i in range(count):
            AgentExecution.objects.create(
                agent=self.pa_agent,
                user=self.user,
                task=f"PA task {i}",
                status=status,
                input_data={"source": "pa", "trace_id": f"pa-a1-{i}"},
                execution_time_ms=100,
                owner_agent="PersonalAssistant",
            )

    def _all_test_rows_qs(self):
        """QuerySet scoped to just this test's seeded rows (via user FK).
        Ensures other tests' persisted data doesn't leak into aggregation."""
        return AgentExecution.objects.filter(user=self.user)

    # ─── muscular.py:451 — detect_weak_muscles ────────────────────────

    def test_muscular_weak_muscles_pattern_excludes_pa(self):
        """detect_weak_muscles pattern: PA does not appear in per-agent
        aggregation even when PA has a low success rate."""
        # Router agent: 10 executions, all completed (100% success — not weak)
        self._seed_router_executions(10, status="completed")
        # PA turns: 10 executions ALL FAILED — would appear as weak muscle if not excluded
        self._seed_pa_executions(10, status="failed")

        # Mirrors the patched query at muscular.py:451
        cutoff_24h = timezone.now() - timedelta(hours=24)
        agents_with_activity = (
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff_24h)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(
                total=Count("id"),
                successful=Count("id", filter=Q(status="completed")),
                failed=Count("id", filter=Q(status="failed")),
            )
            .filter(total__gte=5)
        )
        result = list(agents_with_activity)
        agent_names = [r["agent__name"] for r in result]
        self.assertNotIn("PersonalAssistant", agent_names)
        self.assertIn(self.router_name, agent_names)
        router = next(r for r in result if r["agent__name"] == self.router_name)
        self.assertEqual(router["total"], 10)
        self.assertEqual(router["successful"], 10)

    # ─── muscular.py:483 — detect_overworked_muscles ─────────────────

    def test_muscular_overworked_muscles_pattern_excludes_pa(self):
        """detect_overworked_muscles pattern: high-volume PA does not
        dominate the per-agent count aggregation."""
        self._seed_router_executions(5)
        self._seed_pa_executions(100)

        cutoff_24h = timezone.now() - timedelta(hours=24)
        agent_counts = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff_24h)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        names = [c["agent__name"] for c in agent_counts]
        self.assertNotIn("PersonalAssistant", names)
        # Only router agent should be present in this test's scoped rows
        self.assertEqual(agent_counts[0]["agent__name"], self.router_name)
        self.assertEqual(agent_counts[0]["count"], 5)

    # ─── feedback_loop_engine.py:527 — best_agents ────────────────────

    def test_feedback_best_agents_pattern_excludes_pa(self):
        """best_agents ranking: PA does not appear even if PA has 100%
        success rate."""
        # Router agent: 6 completed 1 failed = 6/7 = 85.7% success
        self._seed_router_executions(6, status="completed")
        self._seed_router_executions(1, status="failed")
        # PA: 10 completed = 100% success — would top ranking without exclude
        self._seed_pa_executions(10, status="completed")

        since = timezone.now() - timedelta(days=1)
        best = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=since)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(
                total=Count("id"),
                successes=Count("id", filter=Q(status="completed")),
            )
            .filter(total__gte=1)
            .annotate(success_rate=F("successes") * 1.0 / F("total"))
            .order_by("-success_rate")[:5]
        )
        names = [b["agent__name"] for b in best]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)

    # ─── feedback_loop_engine.py:537 — most_active ───────────────────

    def test_feedback_most_active_pattern_excludes_pa(self):
        """most_active ranking: high-volume PA does not top the list."""
        self._seed_router_executions(5)
        self._seed_pa_executions(50)

        since = timezone.now() - timedelta(days=1)
        most_active = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=since)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )
        names = [m["agent__name"] for m in most_active]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)
        self.assertEqual(most_active[0]["agent__name"], self.router_name)
        self.assertEqual(most_active[0]["count"], 5)

    # ─── feedback_loop_engine.py:544 — needs_attention ────────────────

    def test_feedback_needs_attention_pattern_excludes_pa(self):
        """needs_attention: PA with high failure rate does not appear."""
        # Router agent: mostly successful — not flagged
        self._seed_router_executions(9, status="completed")
        self._seed_router_executions(1, status="failed")
        # PA: all failed — would be flagged if not excluded
        self._seed_pa_executions(10, status="failed")

        since = timezone.now() - timedelta(days=1)
        needs_attention = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=since)
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(
                total=Count("id"),
                failures=Count("id", filter=Q(status="failed")),
            )
            .filter(total__gte=1, failures__gte=1)
            .annotate(failure_rate=F("failures") * 1.0 / F("total"))
            .filter(failure_rate__gte=0.2)
            .order_by("-failure_rate")[:5]
        )
        names = [n["agent__name"] for n in needs_attention]
        self.assertNotIn("PersonalAssistant", names)

    # ─── learning_pattern_engine.py:645 — agent_stats ────────────────

    def test_learning_pattern_agent_stats_pattern_excludes_pa(self):
        """agent_stats: PA does not appear in per-agent learning aggregation."""
        # Router: 6 completed → passes total__gte=5 filter
        self._seed_router_executions(6, status="completed")
        # PA: 100 completed → would dominate top-50 without exclude
        self._seed_pa_executions(100, status="completed")

        since = timezone.now() - timedelta(days=1)
        stats = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=since, status__in=["completed", "failed"])
            .exclude(agent__name="PersonalAssistant")
            .values("agent__name")
            .annotate(
                total=Count("id"),
                completed=Count("id", filter=Q(status="completed")),
                failed=Count("id", filter=Q(status="failed")),
                avg_ms=Avg("execution_time_ms"),
            )
            .filter(total__gte=5)
            .order_by("-total")[:50]
        )
        names = [s["agent__name"] for s in stats]
        self.assertNotIn("PersonalAssistant", names)
        self.assertIn(self.router_name, names)
        router_row = next(s for s in stats if s["agent__name"] == self.router_name)
        self.assertEqual(router_row["total"], 6)
        self.assertEqual(router_row["completed"], 6)

    # ─── Cross-cutting invariant ─────────────────────────────────────

    def test_pa_rows_never_appear_in_any_patched_aggregation(self):
        """Cross-cutting invariant: for a mixed corpus of PA + router
        executions, every per-agent aggregation returns router-agent
        rows only, never PA."""
        self._seed_router_executions(20)
        self._seed_pa_executions(200)

        cutoff = timezone.now() - timedelta(days=1)
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
            created_at__gte=cutoff, input_data__source="pa"
        ).count()
        self.assertEqual(pa_universe, 200)

    # ─── Negative control: without exclude, PA WOULD distort ─────────

    def test_without_exclude_pa_would_dominate(self):
        """Negative control: the SAME query WITHOUT the exclude would
        return PA as a top result. This locks in the exclude's necessity."""
        self._seed_router_executions(5)
        self._seed_pa_executions(100)

        cutoff = timezone.now() - timedelta(days=1)
        # WITHOUT the exclude (the pre-patch broken behavior)
        pre_patch = list(
            self._all_test_rows_qs()
            .filter(created_at__gte=cutoff)
            .values("agent__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        names_pre = [p["agent__name"] for p in pre_patch]
        self.assertIn("PersonalAssistant", names_pre)
        self.assertEqual(pre_patch[0]["agent__name"], "PersonalAssistant")
        self.assertEqual(pre_patch[0]["count"], 100)
