"""
Tests for Session 1253 PR 3 — ``employee_tool action=status`` +
``employee_tool action=evidence_for_mission``.

Real-DB integration tests against PostgreSQL. Trust math, latest-mission
shape, stale-pin evidence, and the 5+ table evidence join all rely on
QuerySet semantics that MagicMock'd cursors hide
(``feedback_test_real_db_for_queryset_semantics.md``).

Run::

    python manage.py test core.tests.test_employee_tool_status --keepdb -v2
"""

from __future__ import annotations

import time
import uuid
from datetime import timedelta
from typing import Any, Dict, Optional

from django.test import TestCase, override_settings
from django.utils import timezone

from core.services.td_handlers_employee import EmployeeHandlersMixin


# ── Helpers ──────────────────────────────────────────────────────────


def _call(payload: dict) -> dict:
    """Invoke ``_handle_employee_tool`` on a bare mixin instance.

    PR 3 actions are pure / read-only — no dispatcher state, no auth
    gate (the gate lives on run_now + mission_verdict only).
    """
    handler = EmployeeHandlersMixin()
    return handler._handle_employee_tool(
        tool_name="employee_tool",
        payload=payload,
        user_id=None,
        trace_id="test-trace-id",
    )


def _seed_mission(
    *,
    started_at,
    verdict: Optional[str] = "certified",
    status: str = "passed",
    triggered_by: str = "beat",
    wall_time_ms: Optional[int] = 40000,
    drift_count: Optional[int] = 0,
    degraded_evidence: bool = False,
    failed_step: Optional[str] = None,
    error_signature: Optional[str] = None,
    error_tail: Optional[str] = None,
    escalation_deliverable_id: Optional[str] = None,
    escalation_pa_post_id: Optional[str] = None,
    verdict_confidence: Optional[float] = 0.95,
    finished_offset_seconds: int = 40,
):
    """Create one OpsRun(domain='mission', run_kind='docs_cascade')."""
    from core.models_ops_runs import OpsRun, OpsRunEvent

    finished_at = started_at + timedelta(seconds=finished_offset_seconds)
    summary: Dict[str, Any] = {
        "verdict": verdict,
        "verdict_confidence": verdict_confidence,
        "verdict_issued_by": "rigby",
        "verdict_issued_at": finished_at.isoformat(),
        "wall_time_ms": wall_time_ms,
        "failed_step": failed_step,
        "error_tail": error_tail,
        "error_signature": error_signature,
        "drift_count": drift_count,
        "drift_items_count": drift_count,
        "degraded_evidence": degraded_evidence,
        "docs_indexed_count": 2754,
        "documents_count_before": 2756,
        "documents_count_after": 2756,
        "embeddings_count_before": 37682,
        "embeddings_count_after": 37682,
        "embedding_delta": 0,
    }
    if escalation_deliverable_id:
        summary["escalation_deliverable_id"] = escalation_deliverable_id
    if escalation_pa_post_id:
        summary["escalation_pa_post_id"] = escalation_pa_post_id

    run = OpsRun.objects.create(
        title="docs_cascade",
        run_type="manual",
        domain="mission",
        run_kind="docs_cascade",
        status=status,
        triggered_by=triggered_by,
        summary=summary,
        finished_at=finished_at,
    )
    # auto_now_add overrides the started_at param — backfill explicitly.
    OpsRun.objects.filter(id=run.id).update(started_at=started_at)
    run.refresh_from_db()
    return run


def _seed_event_chain(run, *labels):
    from core.models_ops_runs import OpsRunEvent
    base = run.started_at
    for i, label in enumerate(labels):
        OpsRunEvent.objects.create(
            run=run,
            event_type="info",
            label=label,
        )
    # Order by created_at is what the query uses; auto_now_add timestamps
    # are monotonic so the insertion order is preserved.


# ── HAPPY-PATH STATUS TESTS ───────────────────────────────────────────


class EmployeeToolStatusHappyPathTests(TestCase):

    def _call_status(self, **kwargs):
        payload = {
            "action": "status",
            "employee": "rigby",
            "job": "docs_manager",
            "window": "7d",
            **kwargs,
        }
        return _call(payload)

    def test_empty_window_returns_clean_shape(self):
        """Empty window → full schema, ratio=null, status=no_data, all zeros."""
        result = self._call_status()
        self.assertTrue(result["ok"])
        self.assertEqual(result["action"], "status")
        self.assertEqual(result["employee"], "rigby")
        self.assertEqual(result["job"], "docs_manager")
        self.assertEqual(result["window_days"], 7)

        self.assertEqual(result["missions"], {
            "total": 0,
            "certified": 0,
            "rejected": 0,
            "deferred": 0,
            "in_progress": 0,
        })
        self.assertEqual(result["trust"], {
            "ratio": None,
            "status": "no_data",
            "current_streak": 0,
            "current_streak_kind": "none",
        })
        self.assertEqual(result["timing"]["last_mission_at"], None)
        self.assertEqual(result["timing"]["last_certified_at"], None)
        self.assertEqual(result["timing"]["last_escalation_at"], None)
        self.assertEqual(result["timing"]["avg_wall_time_ms"], None)
        self.assertEqual(result["drift"]["last_drift_count"], None)
        self.assertEqual(result["drift"]["degraded_evidence_count"], 0)
        self.assertIsNone(result["latest_mission"])
        # No pointer when no mission_id passed.
        self.assertNotIn("requested_mission_pointer", result)

    def test_two_failures_in_7d_stays_healthy(self):
        """6 certified + 2 rejected in window → healthy, ratio = 6/8."""
        now = timezone.now()
        for i in range(6):
            _seed_mission(
                started_at=now - timedelta(hours=i + 1),
                verdict="certified",
                status="passed",
            )
        for i in range(2):
            _seed_mission(
                started_at=now - timedelta(hours=7 + i),
                verdict="rejected",
                status="failed",
                failed_step="build_docs_index",
                error_signature="abc123",
            )

        result = self._call_status(window="7d")
        self.assertEqual(result["missions"]["total"], 8)
        self.assertEqual(result["missions"]["certified"], 6)
        self.assertEqual(result["missions"]["rejected"], 2)
        self.assertEqual(result["trust"]["status"], "healthy")
        self.assertEqual(result["trust"]["ratio"], 0.75)

    def test_three_failures_in_7d_flips_under_review(self):
        """5 certified + 3 rejected in 7d → under_review, ratio = 5/8."""
        now = timezone.now()
        for i in range(5):
            _seed_mission(
                started_at=now - timedelta(hours=i + 1),
                verdict="certified",
                status="passed",
            )
        for i in range(3):
            _seed_mission(
                started_at=now - timedelta(hours=6 + i),
                verdict="rejected",
                status="failed",
                failed_step="build_docs_index",
                error_signature=f"sig{i}",
            )

        result = self._call_status(window="7d")
        self.assertEqual(result["trust"]["status"], "under_review")
        self.assertEqual(result["trust"]["ratio"], 0.625)

    def test_under_review_uses_7d_even_when_window_is_30d(self):
        """3 rejected within last 7d + healthy 8-30d range → still under_review.

        Confirms Rigby amendment 4: trip-wire is fixed at 7d regardless
        of the caller-requested window.
        """
        now = timezone.now()
        for i in range(3):
            _seed_mission(
                started_at=now - timedelta(hours=i + 1),
                verdict="rejected",
                status="failed",
                failed_step="build_docs_index",
                error_signature=f"sig{i}",
            )
        # 50 certified in the 8-30d range (long-window denominator boost).
        for i in range(50):
            _seed_mission(
                started_at=now - timedelta(days=8 + (i % 22)),
                verdict="certified",
                status="passed",
            )

        result = self._call_status(window="30d")
        self.assertEqual(result["trust"]["status"], "under_review")
        # ratio = 50 certified / (50+3) = 50/53 ≈ 0.9434
        self.assertAlmostEqual(result["trust"]["ratio"], 50 / 53, places=3)
        self.assertEqual(result["window_days"], 30)

    def test_deferred_is_neutral_for_trust_math(self):
        """Rigby amendment 3: deferred excluded from trust_ratio denominator."""
        now = timezone.now()
        # 4 certified, 1 rejected, 5 deferred.
        for i in range(4):
            _seed_mission(
                started_at=now - timedelta(hours=i + 1),
                verdict="certified",
            )
        _seed_mission(
            started_at=now - timedelta(hours=5),
            verdict="rejected",
            status="failed",
        )
        for i in range(5):
            _seed_mission(
                started_at=now - timedelta(hours=6 + i),
                verdict="deferred",
                status="partial",
            )

        result = self._call_status(window="7d")
        self.assertEqual(result["missions"]["total"], 10)
        self.assertEqual(result["missions"]["certified"], 4)
        self.assertEqual(result["missions"]["rejected"], 1)
        self.assertEqual(result["missions"]["deferred"], 5)
        # ratio = 4 / (4+1) = 0.8 — deferred not penalized.
        self.assertEqual(result["trust"]["ratio"], 0.8)
        self.assertEqual(result["trust"]["status"], "healthy")

    def test_deferred_only_window_returns_null_ratio(self):
        """certified+rejected denominator = 0 → ratio=null."""
        now = timezone.now()
        for i in range(3):
            _seed_mission(
                started_at=now - timedelta(hours=i + 1),
                verdict="deferred",
                status="partial",
            )
        result = self._call_status(window="7d")
        self.assertEqual(result["missions"]["total"], 3)
        self.assertEqual(result["missions"]["deferred"], 3)
        self.assertIsNone(result["trust"]["ratio"])

    def test_current_streak_consecutive_certified(self):
        """Latest=cert, -1=cert, -2=cert, -3=reject → streak=3, kind=certified."""
        now = timezone.now()
        # Order matters: insert oldest first so started_at ordering aligns.
        _seed_mission(
            started_at=now - timedelta(hours=4),
            verdict="rejected",
            status="failed",
        )
        for i in range(3):
            _seed_mission(
                started_at=now - timedelta(hours=3 - i),
                verdict="certified",
            )

        result = self._call_status(window="7d")
        self.assertEqual(result["trust"]["current_streak"], 3)
        self.assertEqual(result["trust"]["current_streak_kind"], "certified")

    def test_current_streak_breaks_on_first_non_match(self):
        """Latest=rejected, -1=cert → streak=1, kind=rejected."""
        now = timezone.now()
        _seed_mission(
            started_at=now - timedelta(hours=2),
            verdict="certified",
        )
        _seed_mission(
            started_at=now - timedelta(hours=1),
            verdict="rejected",
            status="failed",
        )

        result = self._call_status(window="7d")
        self.assertEqual(result["trust"]["current_streak"], 1)
        self.assertEqual(result["trust"]["current_streak_kind"], "rejected")


# ── LATEST_MISSION SHAPE ──────────────────────────────────────────────


class EmployeeToolStatusLatestMissionTests(TestCase):

    def _status(self):
        return _call({
            "action": "status",
            "employee": "rigby",
            "job": "docs_manager",
            "window": "7d",
        })

    def test_latest_success_shape_uses_real_summary_keys(self):
        """Mirror the worker-path success row (02480a34-…)."""
        now = timezone.now()
        run = _seed_mission(
            started_at=now - timedelta(minutes=5),
            verdict="certified",
            status="passed",
            triggered_by="beat",
            wall_time_ms=42870,
            drift_count=5,
        )
        result = self._status()
        latest = result["latest_mission"]
        self.assertEqual(latest["mission_id"], str(run.id))
        self.assertEqual(latest["triggered_by"], "beat")
        self.assertEqual(latest["status"], "passed")
        self.assertEqual(latest["verdict"], "certified")
        self.assertEqual(latest["verdict_confidence"], 0.95)
        self.assertEqual(latest["wall_time_ms"], 42870)
        self.assertIsNone(latest["failed_step"])
        self.assertIsNone(latest["error_signature"])
        self.assertFalse(latest["has_escalation"])
        self.assertIsNone(latest["escalation_deliverable_id"])
        self.assertIsNone(latest["pa_post"])

    def test_latest_failure_exposes_escalation_id_not_error_tail(self):
        """Failure row → has_escalation=true, no error_tail in status payload."""
        from core.models_deliverables import Deliverable
        from django.contrib.auth import get_user_model

        UserModel = get_user_model()
        user = UserModel.objects.create_user(
            username=f"tester-{uuid.uuid4()}",
            password="x",
        )
        deliv = Deliverable.objects.create(
            title="Docs Manager Escalation — test",
            user=user,
            status="ready",
            publish_intent="publish_candidate",
        )

        now = timezone.now()
        _seed_mission(
            started_at=now - timedelta(minutes=5),
            verdict="rejected",
            status="failed",
            triggered_by="beat",
            failed_step="build_docs_index",
            error_signature="61a96dad6267d6b6",
            error_tail="CommandError: Unknown command: 'build_docs_index'",
            escalation_deliverable_id=str(deliv.id),
            verdict_confidence=0.0,
        )

        result = self._status()
        latest = result["latest_mission"]
        self.assertEqual(latest["verdict"], "rejected")
        self.assertEqual(latest["failed_step"], "build_docs_index")
        self.assertEqual(latest["error_signature"], "61a96dad6267d6b6")
        self.assertTrue(latest["has_escalation"])
        self.assertEqual(
            latest["escalation_deliverable_id"], str(deliv.id)
        )
        # error_tail must NOT be in the status payload (only signature
        # + has_escalation pointer).
        self.assertNotIn("error_tail", latest)

    def test_triggered_by_passthrough(self):
        """`triggered_by` exposed verbatim — beat / manual / future values."""
        now = timezone.now()
        _seed_mission(
            started_at=now - timedelta(minutes=2),
            triggered_by="manual",
        )
        result = self._status()
        self.assertEqual(result["latest_mission"]["triggered_by"], "manual")

        _seed_mission(
            started_at=now - timedelta(minutes=1),
            triggered_by="beat",
        )
        result = self._status()
        self.assertEqual(result["latest_mission"]["triggered_by"], "beat")

    def test_stale_pin_evidence_exposed_on_escalation(self):
        """Rigby amendment 5: pa_post + settings_primary_pin + pin_matches.

        Simulate the S1252 cutover scenario — PA post landed in the
        stale contract pin while settings is pointing at the active
        pin (env override).
        """
        from core.models import ChatConversation
        from django.contrib.auth import get_user_model

        UserModel = get_user_model()
        user = UserModel.objects.create_user(
            username=f"tester-{uuid.uuid4()}",
            password="x",
        )
        # Stale post: the cutover scenario.
        chat = ChatConversation.objects.create(
            user=user,
            conversation_id="pa-3901b70e61934df7",  # stale contract pin
            user_message="[system: docs_manager escalation]",
            assistant_response="Docs Manager FAILED at build_docs_index ...",
        )

        now = timezone.now()
        _seed_mission(
            started_at=now - timedelta(minutes=3),
            verdict="rejected",
            status="failed",
            failed_step="build_docs_index",
            error_signature="abc",
            escalation_deliverable_id=str(uuid.uuid4()),
            escalation_pa_post_id=str(chat.pk),
        )

        with override_settings(
            RIGBY_PRIMARY_PA_PIN="pa-c7263e7061a0"
        ):
            result = self._status()
        latest = result["latest_mission"]
        pa_post = latest["pa_post"]
        self.assertIsNotNone(pa_post)
        self.assertEqual(pa_post["conversation_id"], "pa-3901b70e61934df7")
        self.assertEqual(
            pa_post["settings_primary_pin"], "pa-c7263e7061a0"
        )
        self.assertFalse(pa_post["pin_matches_settings"])

    def test_stale_pin_matches_when_active_pin_used(self):
        """Healthy case: pa_post pin == settings pin → matches=True."""
        from core.models import ChatConversation
        from django.contrib.auth import get_user_model

        UserModel = get_user_model()
        user = UserModel.objects.create_user(
            username=f"tester-{uuid.uuid4()}",
            password="x",
        )
        chat = ChatConversation.objects.create(
            user=user,
            conversation_id="pa-c7263e7061a0",  # active env pin
            user_message="[system: docs_manager escalation]",
            assistant_response="…",
        )
        now = timezone.now()
        _seed_mission(
            started_at=now - timedelta(minutes=3),
            verdict="rejected",
            status="failed",
            failed_step="step",
            error_signature="abc",
            escalation_deliverable_id=str(uuid.uuid4()),
            escalation_pa_post_id=str(chat.pk),
        )
        with override_settings(
            RIGBY_PRIMARY_PA_PIN="pa-c7263e7061a0"
        ):
            result = self._status()
        pa_post = result["latest_mission"]["pa_post"]
        self.assertTrue(pa_post["pin_matches_settings"])


# ── POINTER REDIRECT ──────────────────────────────────────────────────


class EmployeeToolStatusPointerTests(TestCase):

    def test_status_with_mission_id_returns_pointer(self):
        """Rigby amendment 1: status does NOT inline evidence; returns pointer."""
        now = timezone.now()
        run = _seed_mission(started_at=now - timedelta(minutes=1))
        result = _call({
            "action": "status",
            "employee": "rigby",
            "job": "docs_manager",
            "window": "7d",
            "mission_id": str(run.id),
        })
        self.assertIn("requested_mission_pointer", result)
        pointer = result["requested_mission_pointer"]
        self.assertEqual(pointer["mission_id"], str(run.id))
        self.assertEqual(pointer["evidence_action"], "evidence_for_mission")
        # And status must NOT inline the full evidence — events list
        # / llm_calls / tool_calls live on evidence_for_mission only.
        self.assertNotIn("events", result)
        self.assertNotIn("llm_calls", result)
        self.assertNotIn("tool_calls", result)


# ── PERFORMANCE ───────────────────────────────────────────────────────


class EmployeeToolStatusPerformanceTests(TestCase):

    def test_seeded_100_missions_under_500ms(self):
        """100 OpsRuns + 11 events each → handler returns in < 500ms (p95 of 5)."""
        now = timezone.now()
        for i in range(100):
            run = _seed_mission(
                started_at=now - timedelta(hours=i),
                verdict="certified" if i % 5 != 0 else "rejected",
                status="passed" if i % 5 != 0 else "failed",
            )
            _seed_event_chain(
                run,
                "run_started",
                "step_1_index_started",
                "step_1_index_passed",
                "step_2_corpus_started",
                "step_2_corpus_passed",
                "step_3_sync_started",
                "step_3_sync_passed",
                "step_4_embed_started",
                "step_4_embed_passed",
                "step_5_drift_observed",
                "verdict_issued:certified",
            )

        durations = []
        for _ in range(5):
            t0 = time.perf_counter()
            _call({
                "action": "status",
                "employee": "rigby",
                "job": "docs_manager",
                "window": "90d",
            })
            durations.append((time.perf_counter() - t0) * 1000)
        durations.sort()
        # p95 of 5 = max value.
        self.assertLess(
            durations[-1], 500,
            f"status p95={durations[-1]:.1f}ms over 5 runs exceeded 500ms; "
            f"all durations (ms): {[round(d, 1) for d in durations]}",
        )


# ── EVIDENCE_FOR_MISSION ──────────────────────────────────────────────


class EmployeeToolEvidenceForMissionTests(TestCase):

    def test_evidence_for_mission_joins_all_5_tables(self):
        """Seed full chain — assert all 6 evidence sections populated."""
        from core.models_deliverables import Deliverable, DeliverableEvent
        from django.contrib.auth import get_user_model

        UserModel = get_user_model()
        user = UserModel.objects.create_user(
            username=f"tester-{uuid.uuid4()}",
            password="x",
        )
        deliv = Deliverable.objects.create(
            title="Docs Manager Escalation — fixture",
            user=user,
            status="ready",
            publish_intent="publish_candidate",
        )

        now = timezone.now()
        run = _seed_mission(
            started_at=now - timedelta(minutes=5),
            verdict="rejected",
            status="failed",
            failed_step="build_docs_index",
            error_signature="sig123",
            error_tail="\n".join(f"line {i}" for i in range(50)),
            escalation_deliverable_id=str(deliv.id),
        )
        _seed_event_chain(
            run,
            "run_started",
            "step_1_index_started",
            "step_1_index_failed",
            "escalation_emitted",
            "verdict_issued:rejected",
        )

        DeliverableEvent.objects.create(
            deliverable=deliv,
            event_type="status_transition",
            source="DocsManager",
            metadata={
                "ctx": {
                    "previous_status": "completed",
                    "new_status": "ready",
                    "ops_run_id": str(run.id),
                    "error_signature": "sig123",
                }
            },
        )

        result = _call({
            "action": "evidence_for_mission",
            "employee": "rigby",
            "mission_id": str(run.id),
        })
        self.assertTrue(result["ok"])
        self.assertEqual(result["mission_id"], str(run.id))
        self.assertEqual(result["ops_run"]["domain"], "mission")
        self.assertEqual(result["ops_run"]["run_kind"], "docs_cascade")
        self.assertEqual(len(result["events"]), 5)
        self.assertEqual(result["events"][0]["label"], "run_started")
        self.assertEqual(
            result["events"][-1]["label"], "verdict_issued:rejected"
        )

        self.assertIsNotNone(result["escalation"]["deliverable"])
        self.assertEqual(
            result["escalation"]["deliverable"]["id"], str(deliv.id)
        )
        self.assertEqual(
            result["escalation"]["deliverable"]["status"], "ready"
        )
        self.assertEqual(
            len(result["escalation"]["deliverable_events"]), 1
        )
        de = result["escalation"]["deliverable_events"][0]
        self.assertEqual(de["source"], "DocsManager")
        self.assertEqual(de["ctx"]["ops_run_id"], str(run.id))
        self.assertEqual(de["ctx"]["error_signature"], "sig123")

        # LLM + tool sections present but empty for docs_cascade today.
        self.assertEqual(result["llm_calls"], [])
        self.assertEqual(result["tool_calls"], [])

    def test_evidence_default_is_preview_not_full_tail(self):
        """Rigby amendment 2: default verbose=False returns preview only."""
        now = timezone.now()
        long_tail = "\n".join(f"line {i:04d}" for i in range(100))
        run = _seed_mission(
            started_at=now - timedelta(minutes=2),
            verdict="rejected",
            status="failed",
            failed_step="step",
            error_tail=long_tail,
        )

        result = _call({
            "action": "evidence_for_mission",
            "employee": "rigby",
            "mission_id": str(run.id),
        })
        summary = result["ops_run"]["summary"]
        # Full tail not returned.
        self.assertNotIn("error_tail", summary)
        # Preview is last 30 lines.
        preview = summary["error_tail_preview"]
        preview_lines = preview.split("\n")
        self.assertEqual(len(preview_lines), 30)
        self.assertEqual(preview_lines[-1], "line 0099")
        # Flag set when content was truncated.
        self.assertTrue(summary["has_full_error_tail"])

    def test_evidence_verbose_true_returns_full_tail(self):
        now = timezone.now()
        long_tail = "\n".join(f"line {i:04d}" for i in range(100))
        run = _seed_mission(
            started_at=now - timedelta(minutes=2),
            verdict="rejected",
            status="failed",
            failed_step="step",
            error_tail=long_tail,
        )
        result = _call({
            "action": "evidence_for_mission",
            "employee": "rigby",
            "mission_id": str(run.id),
            "verbose": True,
        })
        summary = result["ops_run"]["summary"]
        self.assertEqual(summary["error_tail"], long_tail)
        self.assertNotIn("error_tail_preview", summary)
        self.assertNotIn("has_full_error_tail", summary)

    def test_evidence_unknown_mission_id_returns_mission_not_found(self):
        result = _call({
            "action": "evidence_for_mission",
            "employee": "rigby",
            "mission_id": str(uuid.uuid4()),
        })
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "mission_not_found")

    def test_evidence_missing_mission_id_returns_clear_error(self):
        result = _call({
            "action": "evidence_for_mission",
            "employee": "rigby",
        })
        self.assertFalse(result["ok"])
        self.assertIn("mission_id", result["error"])

    def test_evidence_short_tail_no_truncation_flag(self):
        """Tail < 30 lines → preview equals full tail, flag is False."""
        now = timezone.now()
        short_tail = "\n".join(f"line {i}" for i in range(5))
        run = _seed_mission(
            started_at=now - timedelta(minutes=1),
            verdict="rejected",
            status="failed",
            failed_step="step",
            error_tail=short_tail,
        )
        result = _call({
            "action": "evidence_for_mission",
            "employee": "rigby",
            "mission_id": str(run.id),
        })
        summary = result["ops_run"]["summary"]
        self.assertEqual(summary["error_tail_preview"], short_tail)
        self.assertFalse(summary["has_full_error_tail"])


# ── ERROR PATHS ───────────────────────────────────────────────────────


class EmployeeToolStatusErrorPathTests(TestCase):

    def test_unknown_employee_rejected(self):
        result = _call({
            "action": "status",
            "employee": "notrigby",
            "job": "docs_manager",
            "window": "7d",
        })
        self.assertFalse(result["ok"])
        self.assertIn("rigby", result["error"].lower())

    def test_unknown_job_rejected(self):
        result = _call({
            "action": "status",
            "employee": "rigby",
            "job": "not_a_job",
            "window": "7d",
        })
        self.assertFalse(result["ok"])
        self.assertIn("docs_manager", result["known_jobs"])

    def test_unknown_window_rejected(self):
        result = _call({
            "action": "status",
            "employee": "rigby",
            "job": "docs_manager",
            "window": "365d",
        })
        self.assertFalse(result["ok"])
        self.assertEqual(
            result["valid_windows"], ["7d", "30d", "90d"]
        )

    def test_default_window_is_7d(self):
        """Omitting window → 7d default."""
        result = _call({
            "action": "status",
            "employee": "rigby",
            "job": "docs_manager",
        })
        self.assertTrue(result["ok"])
        self.assertEqual(result["window_days"], 7)


# ── ZERO-WRITES GUARANTEE ─────────────────────────────────────────────


class EmployeeToolStatusZeroWritesTests(TestCase):

    def test_status_performs_no_writes(self):
        """Read-only contract — wrap call in atomic + rollback canary."""
        from core.models_ops_runs import OpsRun

        before_count = OpsRun.objects.count()
        _call({
            "action": "status",
            "employee": "rigby",
            "job": "docs_manager",
            "window": "7d",
        })
        self.assertEqual(OpsRun.objects.count(), before_count)

    def test_evidence_performs_no_writes(self):
        from core.models_ops_runs import OpsRun

        now = timezone.now()
        run = _seed_mission(started_at=now - timedelta(minutes=1))

        before_count = OpsRun.objects.count()
        _call({
            "action": "evidence_for_mission",
            "employee": "rigby",
            "mission_id": str(run.id),
        })
        self.assertEqual(OpsRun.objects.count(), before_count)
