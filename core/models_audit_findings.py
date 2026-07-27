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

    CONFIDENCE_HIGH = "high"
    CONFIDENCE_MEDIUM = "medium"
    CONFIDENCE_LOW = "low"
    CONFIDENCE_CHOICES = [
        (CONFIDENCE_HIGH, "High"),
        (CONFIDENCE_MEDIUM, "Medium"),
        (CONFIDENCE_LOW, "Low"),
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
