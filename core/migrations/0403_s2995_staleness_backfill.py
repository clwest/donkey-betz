# S2995 v2 item #4 — PR (b): backfill staleness on existing rows.
#
# Migration 0402 added the staleness column with default 'fresh'.
# Local dry-run of `--recheck-staleness` verified distribution:
# 896 fresh / 4 suspected = 99.6% / 0.4% over 900 rows (4 flips).
# All 4 flips are real staleness signals — refs to paths that no
# longer exist in the repo layout (`models/conversations/models.py`,
# `executor/models.py`, `assistant/base.py`) or lines out of range
# (`base_agent.py:4723`). Zero false positives from the git-ls-files
# basename normalization.
#
# This migration persists the recheck by running the same
# `_check_staleness_at_head` helper over every row. Failed refs land
# in `metadata['staleness_failed_refs']` so v2 item #8 (wire-through
# smoke check) can consume without a second schema field.
#
# Reverse migration is pragmatic: rolling back would need per-row
# prior staleness state, which was uniformly 'fresh' at migration
# 0402 time. We reset all rows to 'fresh' + drop the failed_refs
# metadata key on reverse.
#
# Idempotent: safe to re-run. For future rechecks after code churn,
# use `python manage.py index_doc_research_findings
# --recheck-staleness --apply` instead of writing a new migration.

from pathlib import Path

from django.conf import settings
from django.db import migrations

from core.management.commands.index_doc_research_findings import (
    _build_repo_file_index,
    _check_staleness_at_head,
)


def backfill_staleness(apps, schema_editor):
    Finding = apps.get_model("core", "DocResearchFinding")
    base_dir = Path(settings.BASE_DIR)
    file_index = _build_repo_file_index(base_dir)

    qs = Finding.objects.all().only("id", "text", "staleness", "metadata")
    for row in qs.iterator(chunk_size=500):
        new_val, failed_refs = _check_staleness_at_head(
            row.text, base_dir, file_index
        )
        if new_val == row.staleness:
            # No flip needed — but also ensure metadata is clean
            # (idempotency: if metadata got polluted somehow, wipe it).
            existing_failed = (row.metadata or {}).get("staleness_failed_refs")
            if new_val == "fresh" and existing_failed:
                merged = dict(row.metadata or {})
                merged.pop("staleness_failed_refs", None)
                Finding.objects.filter(id=row.id).update(metadata=merged)
            continue
        merged = dict(row.metadata or {})
        if failed_refs:
            merged["staleness_failed_refs"] = failed_refs
        else:
            merged.pop("staleness_failed_refs", None)
        Finding.objects.filter(id=row.id).update(
            staleness=new_val,
            metadata=merged,
        )


def reset_staleness_to_fresh(apps, schema_editor):
    Finding = apps.get_model("core", "DocResearchFinding")
    # Pragmatic reverse: reset non-fresh rows and drop failed_refs key.
    for row in Finding.objects.exclude(staleness="fresh").iterator(chunk_size=500):
        merged = dict(row.metadata or {})
        merged.pop("staleness_failed_refs", None)
        Finding.objects.filter(id=row.id).update(
            staleness="fresh",
            metadata=merged,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0402_s2995_doc_research_finding_staleness"),
    ]

    operations = [
        migrations.RunPython(backfill_staleness, reset_staleness_to_fresh),
    ]
