"""Cycle 1A KFI-2 (ADR-0120) — canonical_authority field + backfill.

Adds ``Document.canonical_authority`` CharField and populates existing
rows via the derivation helper in ``content/_canonical_authority_helpers.py``.

Signal-safety (SIGN-1 F3 / Chris Option D 2026-07-07): the backfill uses
``QuerySet.update()`` to bypass ``post_save`` signals (specifically
``update_knowledge_base_stats`` in ``content/signals.py:21``) so the
migration does not trigger per-row ``KnowledgeBase.update_statistics()``
recomputes. This is an implementation-mechanics deviation from 0120
§2.1's illustrative ``doc.save(update_fields=…)`` block; the load-bearing
contract (4-branch derivation, all rows classified, idempotence,
runtime-safe, stable schema for 0110/0130) is preserved.
"""

from django.db import migrations, models


def run_backfill_op(apps, schema_editor):
    """Delegate to the testable helper via ``apps.get_model`` for
    migration-safe historical access."""
    from content._canonical_authority_helpers import run_backfill

    Document = apps.get_model('content', 'Document')
    run_backfill(Document)


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0048_session_1244_rename_workflowexecution'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='canonical_authority',
            field=models.CharField(
                choices=[
                    ('workspace_canonical', 'Workspace Canonical'),
                    ('repo_canonical', 'Repo Canonical'),
                    ('derived', 'Derived'),
                ],
                db_index=True,
                default='derived',
                help_text=(
                    "Source-tier classification for authority-aware "
                    "retrieval. 'workspace_canonical' = mirror of a "
                    "workspace Deliverable (canonical for research/"
                    "governance per 0005 §3). 'repo_canonical' = "
                    "ingested from git-canonical /docs/ file (canonical "
                    "for its own content in the repo). 'derived' = "
                    "downstream/derived surface (e.g., API-imported, "
                    "spider-scraped, or unclassified)."
                ),
                max_length=20,
            ),
        ),
        migrations.RunPython(run_backfill_op, migrations.RunPython.noop),
    ]
