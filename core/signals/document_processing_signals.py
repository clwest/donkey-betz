"""
Document + Narrative Shift Signal Handlers — Session 1115 batch-7

Closes two "truly forgotten" Celery task orphans by wiring them to the
Django signal that should have triggered them all along:

1. `Document.post_save` (created=True, status=pending, file_path set)
   → dispatches `core.tasks.process_document_async`
   The task extracts text/metadata via DocumentProcessingPipeline and,
   if `generate_embeddings=True` (the default), chains into
   `generate_document_embeddings` for RAG search support.

2. `NarrativeShift.post_save` (created=True)
   → dispatches `narrative_drift.trigger_content_from_shift`
   The task creates a `ChannelEpisode` summarizing the shift using
   fields that are already populated when the shift is saved
   (shift_summary, historian_analysis, etc.). It self-gates on
   confidence >= 0.6 and importance >= 0.5, so low-quality shifts
   short-circuit cheaply.

Both handlers:
- Use `transaction.on_commit` so the dispatch waits for the row's
  transaction to commit (mirrors `trigger_signals.on_spider_data_created`).
- Use `try/except` to swallow dispatch errors — a signal handler raising
  would block the originating save.
- Only fire on `created=True` to avoid loops where the task `.save()`s
  the row again.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

logger = logging.getLogger(__name__)


def _document_sender():
    """Resolve content.Document at signal-bind time. Lazy to avoid AppRegistry
    not-ready issues during apps.py import."""
    from content.models import Document
    return Document


def _narrative_shift_sender():
    """Resolve core.NarrativeShift at signal-bind time. The model lives in
    `core/models_narrative_drift.py` which isn't auto-imported during Django
    startup (the `core.models` package directory shadows `core/models.py`'s
    catch-all import), so we import it here to force registration."""
    from core.models_narrative_drift import NarrativeShift
    return NarrativeShift


@receiver(post_save, sender='content.Document')
def on_document_created(sender, instance, created, **kwargs):
    """Dispatch process_document_async on new Document with file_path set."""
    if not created:
        return
    if not getattr(instance, 'file_path', None):
        return
    # Only fire when document is in the initial pending state — avoids
    # accidentally re-processing manually-created or already-processed rows.
    status = getattr(instance, 'status', None)
    if status not in ('pending', 'PENDING', None, ''):
        return

    def _dispatch():
        try:
            from core.tasks import process_document_async
            process_document_async.delay(instance.id)
            logger.info(
                "[doc-signal] dispatched process_document_async for Document %s",
                instance.id,
            )
        except Exception as e:
            logger.error(
                "[doc-signal] failed to dispatch process_document_async for %s: %s",
                instance.id, e,
            )

    try:
        transaction.on_commit(_dispatch)
    except Exception as e:
        logger.error("[doc-signal] on_commit scheduling failed: %s", e)


def on_narrative_shift_created(sender, instance, created, **kwargs):
    """Dispatch trigger_content_from_narrative_shift on new NarrativeShift.

    The task self-gates on confidence/importance thresholds, so we
    dispatch on every creation and let it short-circuit cheaply.
    """
    if not created:
        return

    def _dispatch():
        try:
            # Use send_task with the registered task name (note: the function
            # is `trigger_content_from_narrative_shift` but the @shared_task
            # decorator registers it as `narrative_drift.trigger_content_from_shift`).
            # Using send_task with the canonical name also lets the audit's
            # send_task-scan attribute this call as a real caller.
            from celery import current_app
            current_app.send_task(
                'narrative_drift.trigger_content_from_shift',
                args=[str(instance.id)],
            )
            logger.info(
                "[narrative-signal] dispatched trigger_content_from_shift for NarrativeShift %s",
                instance.id,
            )
        except Exception as e:
            logger.error(
                "[narrative-signal] failed to dispatch trigger_content_from_shift for %s: %s",
                instance.id, e,
            )

    try:
        transaction.on_commit(_dispatch)
    except Exception as e:
        logger.error("[narrative-signal] on_commit scheduling failed: %s", e)


def connect_document_processing_signals():
    """Explicit connector called from apps.py.ready().

    Connects on_narrative_shift_created via post_save.connect rather than
    @receiver — the NarrativeShift model isn't auto-registered during
    Django startup (it lives in `core/models_narrative_drift.py` which is
    only imported by `core/models.py`, but the `core/models/` package
    directory shadows that file). Importing it here forces registration
    before the signal connection runs.

    on_document_created is bound via @receiver with a string-lazy sender
    'content.Document' since content.Document IS in the package's
    canonical models module.
    """
    NarrativeShift = _narrative_shift_sender()
    post_save.connect(
        on_narrative_shift_created,
        sender=NarrativeShift,
        dispatch_uid='document_processing_signals.on_narrative_shift_created',
    )
    logger.info("Document + NarrativeShift processing signals connected")
