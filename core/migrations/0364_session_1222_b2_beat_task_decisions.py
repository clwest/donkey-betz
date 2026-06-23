"""Session 1222 P6 (audit B2): annotate 4 keep-disabled beat tasks + re-enable
the Operator Edge newsletter with dry_run safeguards.

Chris's per-task decisions on the 5 disabled PeriodicTask rows (deliverable
116bb6bd-2935-440b-bf69-1bcd7ee1ac9d):

| Name                                   | Decision | Reason                                 |
|----------------------------------------|----------|----------------------------------------|
| backfill-spider-embeddings             | Keep off | Backfill complete; resume on demand    |
| scan-income-spider-orchestrator        | Keep off | Superseded by scan-spider-opportunities|
| scan-spider-opportunities              | Keep off | Mode B (curate now) — see audit C1.    |
|                                        |          | Pool stays at ~2,584 while UI/metrics  |
|                                        |          | catch up. Re-enable via manual trigger |
|                                        |          | when ready to grow.                    |
| warm-up-spiders                        | Keep off | Spiders stay warm through normal use   |
| generate-operator-edge-newsletter      | ENABLE   | Operator Edge is active; ship with     |
|                                        |          | dry_run=True for 2-Friday burn-in,     |
|                                        |          | then flip dry_run=False once verified  |

The 4 keep-disabled rows get a 'description' field annotation so future
operators know WHY each is disabled and what the resume path is. Annotation
is data-only — no schedule or kwargs changes for those rows.

The newsletter gets:
- enabled=True
- kwargs updated to {'dry_run': True} so the first burn-in Fridays generate
  the newsletter but route output to "ready" / preview state instead of
  publishing. See core/tasks.py:5765 for the task signature.
- description updated to reflect the burn-in plan

Companion change in `core/celery.py`: the static beat_schedule entry for
`generate-operator-edge-newsletter` gains `'kwargs': {'dry_run': True}` so
that if a fresh environment runs `add_critical_celery_tasks --force`, it
materializes the same safe-by-default state.

To promote off dry_run after the burn-in: update kwargs to {} or
{'dry_run': False} via a follow-up migration or the django-celery-beat
admin UI.

See:
- docs/handoffs/SESSION_1222_*.md (this session's close)
- deliverable 116bb6bd-… (audit B2 classification + decision card)
- audit deliverable bec077ed-… (Session 1217 self-directed audit, finding B2)
"""

from django.db import migrations


_KEEP_DISABLED_ANNOTATIONS = {
    "backfill-spider-embeddings": (
        "Disabled Session 1222 P6 (audit B2). Backfill is complete (644 "
        "historical runs). Re-enable on demand if a new embedding model "
        "warrants a fresh backfill — leave it off otherwise to keep the "
        "ml queue clear. See deliverable 116bb6bd-…."
    ),
    "scan-income-spider-orchestrator": (
        "Disabled Session 1222 P6 (audit B2). Superseded by "
        "scan-spider-opportunities (which itself is keep-disabled per "
        "audit C1 Mode B). Resume path: re-enable both together if the "
        "income-spider intake path is revived."
    ),
    "scan-spider-opportunities": (
        "Disabled Session 1222 P6 (audit B2). Mode B (curate now, "
        "Rigby-ratified) — keep disabled until the platform's "
        "Opportunity-curation UX catches up to the existing ~2,584-row "
        "system pool surfaced by audit C1. Re-enable + add rate-limit "
        "guardrails (max-N new opps/day) once curation is ready, OR "
        "trigger manually via the Django shell. See deliverable "
        "116bb6bd-…."
    ),
    "warm-up-spiders": (
        "Disabled Session 1222 P6 (audit B2). Spiders stay warm via "
        "normal use; no need to fire a dedicated warmup tick every "
        "6 hours. Re-enable if connection-cold-start latency starts "
        "showing in ops telemetry."
    ),
}

_NEWSLETTER_NAME = "generate-operator-edge-newsletter"
_NEWSLETTER_DESCRIPTION = (
    "Operator Edge weekly newsletter (Session 1222 P6 / audit B2 ENABLE). "
    "Ships with dry_run=True for 2-Friday burn-in so the newsletter "
    "generates + lands in ready/preview state without auto-publishing. "
    "Flip kwargs to {'dry_run': False} after verifying 2 successful runs."
)


def apply_b2_decisions(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")

    # 1) Annotate keep-disabled rows with the reason text. No schedule or
    # enabled flip — they stay disabled.
    for name, description in _KEEP_DISABLED_ANNOTATIONS.items():
        PeriodicTask.objects.filter(name=name).update(description=description)

    # 2) Re-enable the Operator Edge newsletter with dry_run safeguards.
    PeriodicTask.objects.filter(name=_NEWSLETTER_NAME).update(
        enabled=True,
        kwargs='{"dry_run": true}',
        description=_NEWSLETTER_DESCRIPTION,
    )


def revert_b2_decisions(apps, schema_editor):
    """Reverse — clear the descriptions and disable the newsletter again.

    Keeps the keep-disabled rows in their disabled state (their original
    state) and just strips the description annotation. The newsletter goes
    back to enabled=False + cleared kwargs.
    """
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")

    for name in _KEEP_DISABLED_ANNOTATIONS:
        PeriodicTask.objects.filter(name=name).update(description="")

    PeriodicTask.objects.filter(name=_NEWSLETTER_NAME).update(
        enabled=False,
        kwargs="{}",
        description="",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0363_session_1198_agent_initiative_affinity"),
        ("django_celery_beat", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(apply_b2_decisions, revert_b2_decisions),
    ]
