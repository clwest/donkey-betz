"""S2794 — TenantBoundaryHealthReport.

Stores one row per run of the cross-tenant regression suite (the umbrella
harness at ``tests/security/test_cross_tenant_regression.py``). Consumed
by the Tenant Boundary Health Workspace sub-tab via
``/api/governance/tenant-boundary-health/``.

**Advisory posture (S2794 F1 mitigation):** Rows are longitudinal signal
for operator triage. They are NOT a launch gate. Chris ratification
remains the explicit gate for opening alpha cohort, flipping runtime
flags, or promoting the platform out of the single-user pre-prod
operating context. The consuming UI + REST envelope both repeat this
advisory framing.

Provenance fields (S2794 F3 mitigation): ``env`` + ``git_sha`` +
``runner_identity`` + ``created_at`` + ``elapsed_secs`` so the reader can
distinguish a fresh CI-blessed result from a stale hand-crafted local run.

Coverage metadata (S2794 F2 mitigation): explicit per-surface bucket
(sync HTTP / async Celery / WebSocket / …) with values
``covered`` / ``not_yet_covered`` / ``partial`` so a green suite result
cannot be mistaken for full-platform tenant boundary confidence.

Constitutional posture: this is Real User Readiness Campaign (RUR-C1)
substrate. RUR-C1 parent close requires I-0301 + I-0302 + I-0303 all
pass this suite (per Chris D-verdict at parent ratification, recorded
in ``docs/research/implementation/RATIFICATION_2026-07-10_real_user_readiness.md``).
"""
from __future__ import annotations

import uuid
from django.db import models


class TenantBoundaryHealthReport(models.Model):
    """One run of the cross-tenant regression suite (S2794 N23).

    Append-only history. Consumers query ``.order_by('-created_at').first()``
    for latest. Trend analysis + gap-close tracking uses the tail window.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # ── S2794 F3 mitigation — provenance ─────────────────────────────
    env = models.CharField(
        max_length=32,
        help_text="Execution environment: 'local' / 'ci' / 'prod'. "
                  "Populated from PLATFORM_ENV or best-effort autodetect.",
    )
    git_sha = models.CharField(
        max_length=40,
        help_text="git HEAD SHA at run time. Empty string if not resolvable.",
    )
    runner_identity = models.CharField(
        max_length=64,
        help_text="Who ran the suite: username / 'celery-beat' / 'ci' / etc.",
    )

    # ── Result counts + timing ───────────────────────────────────────
    elapsed_secs = models.FloatField(help_text="Wall-clock seconds for the full suite run.")
    total_tests = models.IntegerField(help_text="Total tests discovered + executed.")
    passed = models.IntegerField(help_text="Tests that passed cleanly.")
    failed = models.IntegerField(help_text="Tests that asserted-false (contract violation).")
    errored = models.IntegerField(
        default=0,
        help_text="Tests that raised an unexpected exception (infra issue).",
    )
    skipped = models.IntegerField(
        default=0,
        help_text="Tests explicitly skipped (e.g., DB-required in DB-free env).",
    )

    failing_test_ids = models.JSONField(
        default=list,
        help_text="List of dotted test IDs that failed or errored, "
                  "e.g. ['tests.security.test_bucket_a_public_endpoints.TestX.test_y'].",
    )

    # ── S2794 F2 mitigation — coverage metadata ──────────────────────
    coverage_metadata = models.JSONField(
        default=dict,
        help_text="Per-surface coverage: "
                  "{'sync_http_bucket_a': 'covered', ..., "
                  "'async_celery_task_boundary': 'not_yet_covered (I-0303 not opened)'}",
    )

    # ── Full serialized shape for consumers that need everything ─────
    summary_json = models.JSONField(
        help_text="Full serialized summary shape as emitted by the runner. "
                  "Fields above are denormalized for query efficiency; "
                  "this JSONB is the canonical record.",
    )

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at'], name='tbhr_created_desc_idx'),
        ]
        verbose_name = 'Tenant Boundary Health Report'
        verbose_name_plural = 'Tenant Boundary Health Reports'

    def __str__(self):
        return (
            f"TenantBoundaryHealthReport[{self.env}@{self.git_sha[:8]}"
            f" total={self.total_tests} pass={self.passed} fail={self.failed}"
            f" @{self.created_at.isoformat() if self.created_at else 'unsaved'}]"
        )

    @property
    def overall_status(self) -> str:
        """Advisory status label — NOT a gate.

        Values: 'green' (0 failed + 0 errored) / 'red' (any failed/errored)
        / 'unknown' (0 total_tests). Read-only advisory per S2794 F1.
        """
        if self.total_tests == 0:
            return 'unknown'
        if self.failed == 0 and self.errored == 0:
            return 'green'
        return 'red'
