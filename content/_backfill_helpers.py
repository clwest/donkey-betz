"""Session 1235 P5#1 — backfill helper for migration 0047.

Extracted from the migration so the same logic is testable via direct
import. The migration's RunPython forward function delegates here.

Module name uses ``session_1235_p5_1_`` prefix (not migration-numbered)
so the migration loader treats it as a non-migration file in the
``content/migrations/`` package.
"""

from typing import Any


def run_backfill(Document: Any) -> int:
    """Restore ``scope='docs_index'`` on docs corpus rows whose
    ``extracted_metadata`` was overwritten by TextProcessor's generic
    file-level dict.

    Targeted exactly: ``source='imported' AND processor='TextProcessor'
    AND scope key absent``. Other shapes left untouched. Merge preserves
    pre-existing processor/encoding/file_size keys.

    Args:
        Document: The Document model class (resolved by the migration via
            apps.get_model('content', 'Document') for migration safety,
            or directly imported in tests).

    Returns:
        Number of rows updated.
    """
    clobbered = Document.objects.filter(
        source='imported',
        extracted_metadata__processor='TextProcessor',
    ).exclude(
        extracted_metadata__has_key='scope',
    )

    count = 0
    for doc in clobbered:
        existing = doc.extracted_metadata or {}
        doc.extracted_metadata = {**existing, 'scope': 'docs_index'}
        doc.save(update_fields=['extracted_metadata', 'updated_at'])
        count += 1

    return count
