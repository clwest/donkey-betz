"""Session 1235 P5#1 — backfill extracted_metadata for clobbered docs corpus rows.

Restores ``scope='docs_index'`` (and adjacent retrieval keys derivable from
the existing Document row) on Documents where the upload `/process` endpoint
or async `process_document_async` task had overwritten the rich
sync_docs_index_to_documents-written metadata with TextProcessor's generic
file-level metadata (``{processor, encoding, file_size}``).

Companion to the merge-not-overwrite fixes at the four clobber sites in
the same PR (content/views.py:319, core/tasks_misc.py:1678,
core/tasks_media.py:649 + :836) and to the new sync update-path refresh
in core/management/commands/sync_docs_index_to_documents.py.

Victims at LOCAL verification time (2026-06-25 UTC):
  source='imported' AND extracted_metadata->>'processor' = 'TextProcessor'
  AND NOT extracted_metadata ? 'scope' → 3 rows.

Strategy: for any matching row, MERGE ``{'scope': 'docs_index'}`` into
the existing dict (preserves the processor keys; restores the curated
classification consumed by `scoped_retrieval`).

Subsystems / outbound_links / inbound_links_count / etc. require re-running
sync_docs_index_to_documents to repopulate. The new update-path refresh
shipped in the same PR will heal those on the next content-change pass.
"""

from django.db import migrations

from content._backfill_helpers import run_backfill


def backfill_scope_on_clobbered_docs(apps, schema_editor):
    Document = apps.get_model('content', 'Document')
    count = run_backfill(Document)

    # Telemetry for the migration run logs / production observability.
    # Migrations don't have a logger by convention; printing is fine and
    # surfaces in Railway deploy logs + local migrate output.
    if count:
        print(
            f"[SESSION_1235_P5_1_BACKFILL] restored scope='docs_index' "
            f"on {count} clobbered docs corpus Document rows"
        )


def reverse_noop(apps, schema_editor):
    """No reverse: removing scope='docs_index' would re-clobber the docs.

    If a real rollback is ever needed, run a custom SQL query — but the
    forward operation is purely additive (sets one key), so reversing
    is rarely the right move.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0046_add_workspace_to_media_models'),
    ]

    operations = [
        migrations.RunPython(
            backfill_scope_on_clobbered_docs,
            reverse_code=reverse_noop,
        ),
    ]
