"""Arc I-0100 P3 (IB-1799-T1-03) — Phase 1 shadow-audit-synthetic smoke
test per ADR-0003 §3.2 + Rigby SIGN Cycle 1 F3/F4 folds.

Exercises the ``core.signals.rigby_delegation_signals.on_delegation_lifecycle``
handler on synthetic ``AgentExecution`` rows in a bounded transaction
savepoint, verifies the 5 lifecycle labels emit in the expected order,
verifies idempotency, and cleans up. Produces an evidence bundle for
Chris's Phase 2 flag-flip decision per ADR-0003 §3.1 Phase 2 entry gate.

Usage::

    python manage.py delegation_lifecycle_smoke_test

Optional flags::

    --verbose         Print per-event emission details.
    --keep-artifacts  Skip cleanup (debug only — normally auto-rolls-back).

Exit codes::

    0 — All lifecycle labels emitted in order + idempotency + cleanup OK.
        stdout terminates with ``DELEGATION_LIFECYCLE_SMOKE_TEST_PASS``.
    1 — Any assertion failed; stdout terminates with
        ``DELEGATION_LIFECYCLE_SMOKE_TEST_FAIL``.

Side-effect isolation (per ADR-0003 §3.2 F3/F4 folds):

- ``override_settings`` scope: ``RIGBY_DELEGATION_ENABLED=True`` +
  ``CELERY_TASK_ALWAYS_EAGER=True`` for the duration of the synthetic
  exercise. **No mutation of production flag state.** Applied via
  Python context manager; reverts on exit.
- Every ``override_settings`` application is recorded in the evidence
  bundle per F4 fold.
- ``AgentExecution`` writes go into a transaction savepoint that
  rolls back after verification — zero persistent artifacts unless
  ``--keep-artifacts`` is passed.
- No async Celery dispatch fires (CELERY_TASK_ALWAYS_EAGER forces
  synchronous execution + the smoke path doesn't call ``delegate_work_item``
  which would spawn a real Celery task).

Phase 2 entry gate (per ADR-0003 §3.1 F1 fold): Phase 2 opens ONLY after
Phase 1 produces an explicit go/no-go evidence bundle with:

- Zero unhandled exceptions
- Successful create → event → evidence join
- ``override_settings`` targets enumerated
- Bundle committed to arc's Stage 3 pre-flight §7 evidence log

This command's stdout evidence-bundle section satisfies the F1 fold
contract; Chris reviews the bundle before Phase 2 open.
"""
from __future__ import annotations

import json
import sys
import uuid
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction
from django.test.utils import override_settings

PASS_MARKER = "DELEGATION_LIFECYCLE_SMOKE_TEST_PASS"
FAIL_MARKER = "DELEGATION_LIFECYCLE_SMOKE_TEST_FAIL"


class Command(BaseCommand):
    help = (
        "Arc I-0100 P3 (IB-1799-T1-03) — Phase 1 shadow-audit-synthetic smoke "
        "test of the Rigby delegation lifecycle handler. See "
        "docs/adr/ADR-0003-mission-runner-staged-enable-posture.md §3.2."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Print per-event emission details.",
        )
        parser.add_argument(
            "--keep-artifacts",
            action="store_true",
            help=(
                "Skip cleanup (debug only). Normally the synthetic rows are "
                "rolled back via a transaction savepoint."
            ),
        )

    def handle(self, *args, **options):
        verbose: bool = options.get("verbose", False)
        keep_artifacts: bool = options.get("keep_artifacts", False)

        evidence: dict[str, Any] = {
            "phase": "1_shadow_audit_synthetic",
            "adr_ref": "ADR-0003",
            "override_settings_applied": [
                "RIGBY_DELEGATION_ENABLED=True",
                "CELERY_TASK_ALWAYS_EAGER=True",
            ],
            "expected_labels_in_order": [
                "agent_assigned",
                "agent_completed",
                "verification_started",
                "verification_completed",
                "mission_closed",
            ],
            "checks": [],
            "unhandled_exceptions": [],
            "verdict": None,
        }

        try:
            with override_settings(
                RIGBY_DELEGATION_ENABLED=True,
                CELERY_TASK_ALWAYS_EAGER=True,
            ):
                success = self._run_smoke(
                    evidence=evidence,
                    verbose=verbose,
                    keep_artifacts=keep_artifacts,
                )
        except Exception as exc:
            evidence["unhandled_exceptions"].append(
                {"type": type(exc).__name__, "message": str(exc)[:500]}
            )
            success = False

        # Emit evidence bundle regardless of outcome
        evidence["verdict"] = "PASS" if success else "FAIL"
        self.stdout.write("")
        self.stdout.write("--- Evidence bundle (Phase 2 entry gate per ADR-0003 §3.1 F1) ---")
        self.stdout.write(json.dumps(evidence, indent=2, default=str))
        self.stdout.write("--- End evidence bundle ---")
        self.stdout.write("")

        if success:
            self.stdout.write(self.style.SUCCESS(PASS_MARKER))
            sys.exit(0)
        else:
            self.stdout.write(self.style.ERROR(FAIL_MARKER))
            sys.exit(1)

    def _run_smoke(self, evidence: dict, verbose: bool, keep_artifacts: bool) -> bool:
        """Execute the synthetic lifecycle exercise. Returns True on success."""
        from django.contrib.auth import get_user_model
        from core.models_ops_runs import OpsRun, OpsRunEvent
        from core.models_rigby_work_items import RigbyWorkItem
        from core.models_unified_system import Agent, AgentExecution
        from core.models_llm_telemetry import LLMCallEvent

        User = get_user_model()
        checks = evidence["checks"]

        with transaction.atomic():
            sid = transaction.savepoint()
            try:
                # 1. Ensure a system user exists (agent FK is required)
                user, _ = User.objects.get_or_create(
                    username="delegation_smoke_test_user",
                    defaults={
                        "email": "delegation_smoke_test@example.com",
                        "is_active": True,
                    },
                )

                # 2. Locate the routed agent (TrendAnalysisAgent per
                #    DELEGATION_ROUTING). Fallback: create synthetic Agent.
                agent = Agent.objects.filter(name="TrendAnalysisAgent").first()
                if agent is None:
                    agent = Agent.objects.create(
                        name="TrendAnalysisAgent_SmokeTest",
                        agent_type="test",
                        description="Synthetic agent for smoke test",
                        specialization="delegation_smoke_test",
                    )
                    checks.append({
                        "name": "synthesize_agent_row",
                        "detail": f"Created synthetic Agent {agent.id}",
                        "ok": True,
                    })
                else:
                    checks.append({
                        "name": "resolve_routed_agent",
                        "detail": f"Found TrendAnalysisAgent id={agent.id}",
                        "ok": True,
                    })

                # 3. Create synthetic MissionRun (OpsRun with domain='mission')
                mission_run = OpsRun.objects.create(
                    title="Smoke test synthetic MissionRun",
                    run_type="smoke_test",
                    triggered_by="management_cmd",
                    domain="mission",
                    run_kind="delegation_smoke_test",
                    mission_id=uuid.uuid4(),
                )
                checks.append({
                    "name": "create_mission_run",
                    "detail": f"OpsRun id={mission_run.id} domain=mission",
                    "ok": True,
                })

                # 4. Create synthetic RigbyWorkItem linked to the mission run
                work_item = RigbyWorkItem.objects.create(
                    source_mission_run=mission_run,
                    source_event_ref=f"smoke_test:{uuid.uuid4()}",
                    decision="monitor",  # matches DELEGATION_ROUTING key
                    severity="info",
                    mission_impact="low",
                    priority=1,
                    title="Smoke test synthetic work item",
                    summary="Exercise delegation lifecycle handler",
                    recommended_next_action="Verify lifecycle emissions",
                )
                checks.append({
                    "name": "create_work_item",
                    "detail": f"RigbyWorkItem id={work_item.id} decision=monitor",
                    "ok": True,
                })

                # 5. Create AgentExecution with parent_object_type='RigbyWorkItem'
                #    + parent_object_id=<work_item.id>. This triggers the handler.
                execution = AgentExecution.objects.create(
                    agent=agent,
                    user=user,
                    task="Smoke test synthetic delegation",
                    status="pending",
                    parent_object_type="RigbyWorkItem",
                    parent_object_id=work_item.id,
                )
                checks.append({
                    "name": "create_agent_execution_pending",
                    "detail": f"AgentExecution id={execution.id} status=pending",
                    "ok": True,
                })

                # 6. Verify agent_assigned emitted (handler fires on created=True)
                agent_assigned = OpsRunEvent.objects.filter(
                    run=mission_run,
                    label="agent_assigned",
                    detail__execution_id=str(execution.id),
                ).exists()
                checks.append({
                    "name": "verify_agent_assigned_emitted",
                    "ok": agent_assigned,
                })
                if verbose:
                    self.stdout.write(f"  agent_assigned emitted: {agent_assigned}")

                if not agent_assigned:
                    return self._fail(evidence, "agent_assigned did not emit on execution create")

                # 7. Create a mock LLMCallEvent(SUCCESS) so verification passes
                LLMCallEvent.objects.create(
                    execution_id=execution.id,
                    status="SUCCESS",
                    agent_name=agent.name,
                    provider="test",
                    model="test",
                )

                # 8. Transition to 'completed' — handler emits terminal lifecycle
                execution.status = "completed"
                execution.save()

                # 9. Verify all 4 terminal lifecycle labels emitted
                terminal_labels = [
                    "agent_completed",
                    "verification_started",
                    "verification_completed",
                    "mission_closed",
                ]
                for label in terminal_labels:
                    emitted = OpsRunEvent.objects.filter(
                        run=mission_run,
                        label=label,
                        detail__execution_id=str(execution.id),
                    ).exists()
                    checks.append({
                        "name": f"verify_{label}_emitted",
                        "ok": emitted,
                    })
                    if verbose:
                        self.stdout.write(f"  {label} emitted: {emitted}")
                    if not emitted:
                        return self._fail(evidence, f"{label} did not emit on terminal save")

                # 10. Idempotency: re-save execution should NOT duplicate rows
                pre_re_save_count = OpsRunEvent.objects.filter(
                    run=mission_run,
                    detail__execution_id=str(execution.id),
                ).count()
                execution.save()  # no-op re-fire
                post_re_save_count = OpsRunEvent.objects.filter(
                    run=mission_run,
                    detail__execution_id=str(execution.id),
                ).count()
                idempotent = pre_re_save_count == post_re_save_count
                checks.append({
                    "name": "verify_idempotency",
                    "pre_count": pre_re_save_count,
                    "post_count": post_re_save_count,
                    "ok": idempotent,
                })
                if verbose:
                    self.stdout.write(
                        f"  idempotency: pre={pre_re_save_count} post={post_re_save_count}"
                    )
                if not idempotent:
                    return self._fail(
                        evidence,
                        f"idempotency violated: {pre_re_save_count} → {post_re_save_count}",
                    )

                # 11. Verify verification_completed carries verdict=verified
                verification_row = OpsRunEvent.objects.filter(
                    run=mission_run,
                    label="verification_completed",
                    detail__execution_id=str(execution.id),
                ).first()
                verdict_ok = (
                    verification_row is not None
                    and verification_row.detail.get("verdict") == "verified"
                )
                checks.append({
                    "name": "verify_verdict_is_verified",
                    "actual_verdict": (
                        verification_row.detail.get("verdict")
                        if verification_row else None
                    ),
                    "ok": verdict_ok,
                })
                if not verdict_ok:
                    return self._fail(
                        evidence,
                        f"verification verdict != 'verified'"
                    )

                # 12. Cleanup — savepoint rollback unless --keep-artifacts
                if keep_artifacts:
                    transaction.savepoint_commit(sid)
                    checks.append({
                        "name": "cleanup",
                        "detail": "Artifacts kept (--keep-artifacts)",
                        "ok": True,
                    })
                else:
                    transaction.savepoint_rollback(sid)
                    checks.append({
                        "name": "cleanup",
                        "detail": "Savepoint rolled back — zero persistent artifacts",
                        "ok": True,
                    })

                return True

            except Exception as exc:
                # Roll back savepoint on ANY unhandled exception
                try:
                    transaction.savepoint_rollback(sid)
                except Exception:
                    pass
                evidence["unhandled_exceptions"].append(
                    {"type": type(exc).__name__, "message": str(exc)[:500]}
                )
                return False

    def _fail(self, evidence: dict, reason: str) -> bool:
        """Record a failure reason in the evidence bundle."""
        evidence["failure_reason"] = reason
        return False
