"""
Session 1043: Backfill existing initiatives with sequential human-friendly IDs.

Orders by created_at ASC so older initiatives get lower numbers.
"""

from django.db import migrations


def backfill_human_ids(apps, schema_editor):
    Initiative = apps.get_model('core', 'Initiative')
    initiatives = Initiative.objects.filter(seq_id__isnull=True).order_by('created_at')
    for idx, init in enumerate(initiatives, start=1):
        init.seq_id = idx
        init.human_id = f"INIT-{idx:06d}"
        init.save(update_fields=['seq_id', 'human_id'])


def reverse_backfill(apps, schema_editor):
    Initiative = apps.get_model('core', 'Initiative')
    Initiative.objects.all().update(seq_id=None, human_id=None)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0250_initiative_sequential_human_id"),
    ]

    operations = [
        migrations.RunPython(backfill_human_ids, reverse_backfill),
    ]
