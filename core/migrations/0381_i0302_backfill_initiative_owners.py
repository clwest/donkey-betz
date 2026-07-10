"""
I-0302 Phase 3 Sub-phase A1 — data migration: backfill null-owner Initiative
rows to the canonical primary user.

Ratified 2026-07-10 via I-0302 Phase 2 predicate module ratification (§8
Phase 3 opening moves) + Chris D-verdict 2026-07-10 (Option C on the
Initiative null-owner transitional policy — backfill + NOT NULL, no
transitional predicate).

Provenance: pre-prod single-user normalization step. Revisit when Phase 0
multi-tenant lands. Canonical primary user is resolved dynamically via
``User.objects.filter(is_superuser=True).order_by('pk').first()`` — NOT
a hardcoded string. Preserves Phase 1 §7 Rigby SIGN F3 guardrail.

Pre-flight expectations (local DB, 2026-07-10, HEAD 0f233567):
- ``Initiative.objects.count()``                       = 62
- ``Initiative.objects.filter(owner__isnull=True).count()`` = 62
- Canonical superuser: ``chris`` (only superuser on local)

Guardrails (per Rigby SIGN Q5 2026-07-10):
1. Hard-fail if no superuser exists AND there is work to do (deny silent
   fallback). Empty-null-owner-set case (fresh test DB, already-backfilled
   local) short-circuits before the superuser lookup so the migration is a
   pure no-op — never denies test-DB setup.
2. Log superuser count — surface unexpected multi-superuser state without
   changing behavior (earliest-pk selection is the ratified rule).
3. Idempotent — only updates rows where ``owner__isnull=True``.
4. Post-step gate — asserts ``null-owner count == 0`` before returning.
5. Provenance — logs backfilled row count + target user pk.

Reversibility: one-way normalization. Reverse is a noop that logs a loud
warning; do NOT rely on reverse for data restoration. Restore from
backup if the schema flip in 0382 needs to be undone in production.

Validated on local only; staging/prod must re-run the preflight ORM
counts (total / null_owner / non_null_owner / superuser existence)
before this migration is applied.
"""

from django.db import migrations


def backfill_initiative_owners(apps, schema_editor):
    Initiative = apps.get_model('core', 'Initiative')
    User = apps.get_model('core', 'UnifiedUser')

    null_owner_qs = Initiative.objects.filter(owner__isnull=True)
    to_backfill = null_owner_qs.count()

    # Empty-set fast path — supports test DB setup (fresh DB has 0 Initiative
    # rows AND 0 User rows) and idempotent re-apply on already-backfilled DBs.
    # Superuser lookup only runs when there's actual work to do.
    if to_backfill == 0:
        print("[I-0302 A1] null-owner Initiative rows: 0 — nothing to backfill.")
        return

    primary_user = User.objects.filter(is_superuser=True).order_by('pk').first()
    if primary_user is None:
        raise RuntimeError(
            "I-0302 Phase 3 Sub-phase A1: no superuser found — cannot resolve "
            "canonical primary user for null-owner backfill. Aborting migration."
        )

    superuser_count = User.objects.filter(is_superuser=True).count()
    print(
        f"[I-0302 A1] canonical superuser resolved: pk={primary_user.pk} "
        f"username={primary_user.username!r} "
        f"(total superusers on this DB: {superuser_count})"
    )
    print(f"[I-0302 A1] backfilling {to_backfill} null-owner Initiative rows...")

    updated = null_owner_qs.update(owner=primary_user)

    remaining_null = Initiative.objects.filter(owner__isnull=True).count()
    if remaining_null != 0:
        raise RuntimeError(
            f"I-0302 Phase 3 Sub-phase A1: post-backfill gate failed — "
            f"{remaining_null} rows still have null owner after update. "
            f"Aborting before schema flip."
        )

    print(
        f"[I-0302 A1] backfill complete: {updated} rows updated to owner pk="
        f"{primary_user.pk}; null-owner remaining: 0"
    )


def reverse_backfill(apps, schema_editor):
    print(
        "[I-0302 A1] reverse: NOOP — this is a one-way pre-prod single-user "
        "normalization step. Restore from backup if data restoration is needed. "
        "Schema reverse (0382) will still restore the nullable/SET_NULL column."
    )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0380_session_2737_hai_dispatch_log'),
    ]

    operations = [
        migrations.RunPython(backfill_initiative_owners, reverse_backfill),
    ]
