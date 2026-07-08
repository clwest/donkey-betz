"""Cycle 1A KFI-1 (ADR-0110) — target Deliverable UUID extraction.

Extracts the target deliverable UUID from a ratification_record.content
body. Ordered 3-path cascade (Chris F1 Option C 2026-07-08):

  Path 1 (canonical, prospective + historical Rigby-authored):
      ``- **Deliverable ID:** <uuid>`` MULTILINE
  Path 2 (historical compat only — mislabeled field on System-authored
  ratification records; NOT the canonical template going forward):
      ``- **Workspace UUID:** `<uuid>` `` MULTILINE
  Path 3 (defensive title fallback):
      ``- **ADR:** <TITLE>`` → lookup Deliverable by title in the same
      workspace, excluding ratification_record-typed rows. Ambiguous
      matches fail closed with TARGET_EXTRACTION_AMBIGUOUS.

Fail-closed terminals: TARGET_EXTRACTION_AMBIGUOUS (multiple title
hits) or TARGET_EXTRACTION_FAILED (no path matched).

Multi-pattern extraction exists ONLY for historical compatibility with
the 11 pre-KFI-1 ratification records observed in the workspace as of
HEAD ``5a878768``. The canonical template going forward is Path 1.
"""

from __future__ import annotations

import logging
import re
from uuid import UUID

logger = logging.getLogger(__name__)


_PATH1_RE = re.compile(
    r'^-\s+\*\*Deliverable ID:\*\*\s+([0-9a-f-]{36})\s*$',
    re.MULTILINE,
)
_PATH2_RE = re.compile(
    r'^-\s+\*\*Workspace UUID:\*\*\s+`([0-9a-f-]{36})`\s*$',
    re.MULTILINE,
)
_PATH3_RE = re.compile(
    r'^-\s+\*\*ADR:\*\*\s+(\S.*?)\s*$',
    re.MULTILINE,
)


def extract_target_deliverable_id(ratification_record, DeliverableModel):
    """Return the target Deliverable UUID for a ratification_record.

    Args:
        ratification_record: a Deliverable row (must have ``content`` and
            ``workspace_id`` attributes).
        DeliverableModel: the Deliverable model class (accepted as a
            parameter so callers can pass ``apps.get_model('core',
            'Deliverable')`` from a migration or historical context).

    Returns:
        A ``uuid.UUID`` on success or ``None`` on fail-closed terminal.
    """
    content = getattr(ratification_record, 'content', '') or ''
    rr_id = getattr(ratification_record, 'id', None)

    m = _PATH1_RE.search(content)
    if m:
        return UUID(m.group(1))

    m = _PATH2_RE.search(content)
    if m:
        return UUID(m.group(1))

    m = _PATH3_RE.search(content)
    if m:
        title = m.group(1).strip()
        hits = list(
            DeliverableModel.objects.filter(
                workspace_id=ratification_record.workspace_id,
                title=title,
            )
            .exclude(deliverable_type='ratification_record')
            .values_list('id', flat=True)
        )
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            logger.error(
                'TARGET_EXTRACTION_AMBIGUOUS rr=%s title=%s hits=%d',
                rr_id, title, len(hits),
            )
            return None

    logger.error('TARGET_EXTRACTION_FAILED rr=%s', rr_id)
    return None
