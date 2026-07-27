"""
Doc-research finding model — S2989 Phase B.

Named `DocResearchFinding` (not `AuditFinding`) because the pre-existing
`AuditFinding` in `models_audit_tracking.py` covers a different lifecycle
(manual security-audit reports parented to `AuditReport`, with P0-P3
priorities and verification flow). This model is scoped narrowly to
docs/research/ bullet extraction.

A `DocResearchFinding` row represents ONE actionable bullet extracted
from a `docs/research/` audit or canonical-summary or
implementation-debt doc. The row is the single source of truth for
status (open|fixed|dismissed); the source doc is evidence, never the
authority.

Backed by the `index_doc_research_findings` management command which
walks a narrow allowlist of `docs/research/**/*.md` sources and upserts
by `(doc_path, text_hash)` — reindexing is idempotent, and findings
that disappear from source are marked `last_seen_at` stale rather than
deleted (so status history is preserved).

Rigby SIGN Cycle 1 folds applied inline:
- F-B1: DocResearchFinding rows are truth; doc markers are evidence only
- F-B2: `confidence` + `source_heading` tags so noisy sections don't
  poison the list
- F-B3: narrow v1 scope enforced at the ingest layer
"""
from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class DocResearchFinding(models.Model):
    """Actionable bullet lifted from a docs/research/ audit.

    Lifecycle:
    - `open`      — surfaced by ingest, no action taken
    - `fixed`     — Chris ticked in the UI OR routed through send-to-rigby
    - `dismissed` — Chris ticked "not actionable" (e.g. duplicate, stale)

    Uniqueness: `(doc_path, text_hash)` — same bullet re-observed on a
    subsequent index is upserted (last_seen_at bumps).
    """

    STATUS_OPEN = "open"
    STATUS_FIXED = "fixed"
    STATUS_DISMISSED = "dismissed"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_FIXED, "Fixed"),
        (STATUS_DISMISSED, "Dismissed"),
    ]

    # S2991 close-mode taxonomy (orthogonal to `status`; nullable).
    # Rigby SIGN caught: status is lifecycle, close_mode is closure mechanism.
    # Freshness (e.g., "stale-corrected") stays in resolution_note until a
    # second trigger justifies a dedicated freshness axis.
    CLOSE_MODE_FIXED_VIA_PR = "fixed_via_pr"
    CLOSE_MODE_EVIDENCE_DELIVERED = "evidence_delivered"
    CLOSE_MODE_DEFERRED_TO_ARC = "deferred_to_arc"
    CLOSE_MODE_INFORMATIONAL = "informational"
    CLOSE_MODE_CHOICES = [
        (CLOSE_MODE_FIXED_VIA_PR, "Fixed via PR"),
        (CLOSE_MODE_EVIDENCE_DELIVERED, "Evidence delivered"),
        (CLOSE_MODE_DEFERRED_TO_ARC, "Deferred to arc"),
        (CLOSE_MODE_INFORMATIONAL, "Informational"),
    ]

    CONFIDENCE_HIGH = "high"
    CONFIDENCE_MEDIUM = "medium"
    CONFIDENCE_LOW = "low"
    CONFIDENCE_CHOICES = [
        (CONFIDENCE_HIGH, "High"),
        (CONFIDENCE_MEDIUM, "Medium"),
        (CONFIDENCE_LOW, "Low"),
    ]

    # S2992 v2 item #2 — finding-type classifier at ingest.
    # Orthogonal to status and close_mode: classifies what SHAPE of work the
    # finding represents so the spec-generator (item #3) can branch template,
    # and Rigby-SIGN UI (item #6) can nudge on decision_evidence rows.
    # Applied at ingest via _classify_finding_type in the index command; new
    # rows always get a classification, existing 900 default to `unknown`
    # until `--reclassify-existing --apply` runs (deferred to PR (b)).
    FINDING_TYPE_DECISION_EVIDENCE = "decision_evidence"
    FINDING_TYPE_EXECUTABLE = "executable"
    FINDING_TYPE_UNKNOWN = "unknown"
    FINDING_TYPE_CHOICES = [
        (FINDING_TYPE_DECISION_EVIDENCE, "Decision Evidence"),
        (FINDING_TYPE_EXECUTABLE, "Executable"),
        (FINDING_TYPE_UNKNOWN, "Unknown"),
    ]

    SOURCE_TYPE_AUDIT = "audit"
    SOURCE_TYPE_CANONICAL_SUMMARY = "canonical_summary"
    SOURCE_TYPE_IMPLEMENTATION_DEBT = "implementation_debt"
    SOURCE_TYPE_CHOICES = [
        (SOURCE_TYPE_AUDIT, "Audit"),
        (SOURCE_TYPE_CANONICAL_SUMMARY, "Canonical Summary"),
        (SOURCE_TYPE_IMPLEMENTATION_DEBT, "Implementation Debt"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    doc_path = models.CharField(max_length=500, db_index=True)
    domain_slug = models.CharField(max_length=100, db_index=True, blank=True, default="")
    source_type = models.CharField(
        max_length=32,
        choices=SOURCE_TYPE_CHOICES,
        db_index=True,
        default=SOURCE_TYPE_AUDIT,
    )
    source_heading = models.CharField(max_length=500, blank=True, default="")

    text = models.TextField()
    text_hash = models.CharField(max_length=64, db_index=True)
    confidence = models.CharField(
        max_length=16,
        choices=CONFIDENCE_CHOICES,
        default=CONFIDENCE_MEDIUM,
    )
    tags = models.JSONField(default=list, blank=True)

    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
        db_index=True,
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resolved_audit_findings",
    )
    resolution_note = models.TextField(blank=True, default="")
    close_mode = models.CharField(
        max_length=32,
        choices=CLOSE_MODE_CHOICES,
        null=True,
        blank=True,
        default=None,
    )
    finding_type = models.CharField(
        max_length=32,
        choices=FINDING_TYPE_CHOICES,
        default=FINDING_TYPE_UNKNOWN,
        db_index=True,
    )

    # S2995 v2 item #4 — staleness detector.
    # Orthogonal to status/close_mode/finding_type — a decision_evidence
    # finding can still be `suspected` if its cited file:line drifted at
    # HEAD. New rows get `_check_staleness_at_head` at ingest; the
    # existing 900 default to `fresh` until the PR (b) backfill migration
    # runs. When suspected, the failed refs land in
    # metadata['staleness_failed_refs'] so v2 item #8 (wire-through smoke
    # check) can consume without a second schema field.
    STALENESS_FRESH = "fresh"
    STALENESS_SUSPECTED = "suspected"
    STALENESS_CHOICES = [
        (STALENESS_FRESH, "Fresh"),
        (STALENESS_SUSPECTED, "Suspected stale"),
    ]
    staleness = models.CharField(
        max_length=16,
        choices=STALENESS_CHOICES,
        default=STALENESS_FRESH,
        db_index=True,
    )

    deliverable_id = models.CharField(max_length=64, blank=True, default="")

    first_seen_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)

    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "core_doc_research_finding"
        constraints = [
            models.UniqueConstraint(
                fields=["doc_path", "text_hash"],
                name="uniq_doc_research_finding_doc_hash",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "doc_path"], name="drf_status_docpath_idx"),
            models.Index(fields=["status", "domain_slug"], name="drf_status_domain_idx"),
        ]

    def __str__(self) -> str:
        preview = (self.text or "")[:80].replace("\n", " ")
        return f"DocResearchFinding({self.status}) {self.doc_path} — {preview}"
