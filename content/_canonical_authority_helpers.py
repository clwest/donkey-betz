"""Cycle 1A KFI-2 (ADR-0120) — canonical_authority derivation + backfill.

Contract from 0120 (load-bearing):
1. Every Document row receives a canonical_authority value.
2. Derivation implements the 4-branch decision tree below (order matters).
3. Backfill is idempotent — a second pass writes zero rows.
4. Existing runtime behavior remains safe (no signal-triggered side-effects
   during backfill).
5. KFI-1 (0110 mirror) and KFI-3 (0130 retrieval) receive a stable schema.

The migration op (0049) delegates here so the derivation is testable via
direct import. Pattern mirrors ``content/_backfill_helpers.py``.

Signal-safety note (SIGN-1 F3 disposition, Chris Option D 2026-07-07):
0120 §2.1's illustrative ``doc.save(update_fields=…)`` per-row loop
triggers ``update_knowledge_base_stats`` (content/signals.py:21) on every
row where ``instance.collection and instance.is_active``, cascading into
``KnowledgeBase.update_statistics()`` — a full recompute + save on every
update. At 2989 rows that is ~12k extra queries during the migration.
The ADR's code block is illustrative implementation-mechanics; the
authoritative contract is the 5 elements above. This module implements
the contract with ``QuerySet.update()`` to bypass ``post_save`` signals,
preserving derivation semantics while eliminating the signal-cascade
cost. Both HEAD Document post_save handlers (line 21 KB stats, line 60
analytics on create-only) are safely bypassed for the update-only path.
"""

from typing import Any

from django.utils import timezone


def _derive_canonical_authority(document) -> str:
    """Return the canonical_authority classification for a Document.

    Evaluation order (load-bearing):
      B1. source == 'workspace'                           -> workspace_canonical
      B2. extracted_metadata['workspace_source_uuid']     -> derived
          (exported-mirror edge case per 0120 §2.5)
      B3. source == 'imported' AND dual-signal docs match -> repo_canonical
          Dual signal: file_path startswith 'docs/' OR
          extracted_metadata.scope == 'docs_index'.
      B4. else                                            -> derived
          Safe under-classification; explicit upgrade required to
          workspace_canonical via B1 or 0110 mirror pipeline.
    """
    source = getattr(document, 'source', '') or ''
    file_path = getattr(document, 'file_path', '') or ''
    meta = getattr(document, 'extracted_metadata', None) or {}

    if source == 'workspace':
        return 'workspace_canonical'
    if meta.get('workspace_source_uuid'):
        return 'derived'
    if source == 'imported' and (
        file_path.startswith('docs/')
        or meta.get('scope') == 'docs_index'
    ):
        return 'repo_canonical'
    return 'derived'


def run_backfill(Document: Any) -> dict:
    """Signal-safe backfill: assign canonical_authority to every Document.

    Uses ``QuerySet.update()`` per-row (bypasses ``post_save``) instead of
    per-row ``instance.save()`` — see module docstring.

    Idempotent: rows whose stored value already matches derivation are
    skipped, so a second run writes zero rows and returns all-zero
    counters.

    Args:
        Document: The Document model class (resolved by the migration
            via ``apps.get_model('content', 'Document')`` for
            migration-safe access; direct import in tests).

    Returns:
        Dict[str, int] of per-tier update counts.
    """
    updated = {
        'workspace_canonical': 0,
        'repo_canonical': 0,
        'derived': 0,
    }
    now = timezone.now()
    for doc in Document.objects.all().only(
        'id',
        'source',
        'file_path',
        'extracted_metadata',
        'canonical_authority',
    ).iterator():
        authority = _derive_canonical_authority(doc)
        if doc.canonical_authority == authority:
            continue
        Document.objects.filter(pk=doc.pk).update(
            canonical_authority=authority,
            updated_at=now,
        )
        updated[authority] += 1
    return updated
