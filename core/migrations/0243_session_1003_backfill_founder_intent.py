# Session 1003: Backfill founder_intent_set for stuck initiatives
#
# 596 initiatives stuck at Stage 1 because can_auto_progress() returns False
# when founder_intent_set=False. This bulk-fixes all ACTIVE/TRIAGE initiatives.

from django.db import migrations
from django.utils import timezone


def backfill_founder_intent(apps, schema_editor):
    """Set founder_intent on all ACTIVE/TRIAGE initiatives that lack it."""
    Initiative = apps.get_model('core', 'Initiative')

    stuck = Initiative.objects.filter(
        founder_intent_set=False,
        status__in=['ACTIVE', 'TRIAGE'],
    )
    count = stuck.count()

    if count > 0:
        stuck.update(
            founder_intent_set=True,
            founder_intent_set_at=timezone.now(),
            founder_intent_set_by='system_auto_backfill',
            execution_speed='fast',
            risk_tolerance='balanced',
        )
        print(f"\n  [Session 1003] Backfilled founder_intent on {count} stuck initiatives")
    else:
        print("\n  [Session 1003] No stuck initiatives found — nothing to backfill")


def reverse_backfill(apps, schema_editor):
    """Reverse: clear auto-backfilled founder intent."""
    Initiative = apps.get_model('core', 'Initiative')
    Initiative.objects.filter(
        founder_intent_set_by='system_auto_backfill',
    ).update(
        founder_intent_set=False,
        founder_intent_set_at=None,
        founder_intent_set_by='',
        execution_speed='',
        risk_tolerance='',
    )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0242_session_1003_desk_intelligence_briefs"),
    ]

    operations = [
        migrations.RunPython(backfill_founder_intent, reverse_backfill),
    ]
