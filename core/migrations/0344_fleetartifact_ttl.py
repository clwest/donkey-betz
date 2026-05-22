# Session 1129 — Move 2 Round 2: Fleet artifact TTL + soft-delete columns.
# Hand-edited from `makemigrations core` output to drop unrelated pending
# drift (agentexecution AlterField, Narrative* model creates). Only the
# Round 2 FleetArtifact changes from `core/models/fleet.py` land here.

from datetime import timedelta

from django.conf import settings
from django.db import migrations, models


def backfill_expires_at(apps, schema_editor):
    """Set expires_at = created_at + DEFAULT_TTL_DAYS for any pre-Round-2 rows.

    Round 1 artifacts had no TTL concept; we apply the same default so
    they participate in the cleanup lifecycle going forward instead of
    living forever. Run in batches to avoid locking large tables.
    """
    FleetArtifact = apps.get_model("core", "FleetArtifact")
    ttl_days = int(getattr(settings, "FLEET_ARTIFACT_DEFAULT_TTL_DAYS", 30))
    batch_size = 1000
    qs = FleetArtifact.objects.filter(expires_at__isnull=True).only(
        "id", "created_at"
    )
    while True:
        chunk = list(qs[:batch_size])
        if not chunk:
            break
        for row in chunk:
            row.expires_at = row.created_at + timedelta(days=ttl_days)
        FleetArtifact.objects.bulk_update(chunk, ["expires_at"], batch_size=200)


def reverse_backfill(apps, schema_editor):
    # No-op on reverse — once columns drop, data goes with them.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0343_fleetartifact"),
    ]

    operations = [
        migrations.AddField(
            model_name="fleetartifact",
            name="expires_at",
            field=models.DateTimeField(
                blank=True,
                db_index=True,
                help_text=(
                    "Server-set at create time: created_at + DEFAULT_TTL_DAYS. "
                    "Past expires_at + deleted_at IS NULL = candidate for cleanup."
                ),
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="fleetartifact",
            name="deleted_at",
            field=models.DateTimeField(
                blank=True,
                db_index=True,
                help_text=(
                    "Soft-delete marker. Set by cleanup job on expiry OR "
                    "by manual operator action. Hard delete is Round 3+."
                ),
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="fleetartifact",
            name="delete_reason",
            field=models.CharField(
                blank=True,
                default="",
                help_text=(
                    "Why this artifact was soft-deleted. Values: 'expired' "
                    "(cleanup), 'manual', 'admin', '' (not deleted)."
                ),
                max_length=32,
            ),
        ),
        migrations.AddIndex(
            model_name="fleetartifact",
            index=models.Index(
                fields=["created_by_identity", "-created_at", "-id"],
                name="core_fleeta_list_stable_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="fleetartifact",
            index=models.Index(
                fields=["expires_at", "deleted_at"],
                name="core_fleeta_cleanup_scan_idx",
            ),
        ),
        migrations.RunPython(backfill_expires_at, reverse_backfill),
    ]
