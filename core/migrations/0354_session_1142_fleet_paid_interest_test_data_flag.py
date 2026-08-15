"""Session 1142 — FleetPaidInterest test-data flag.

Adds ``is_test_data`` boolean to FleetPaidInterest so the Decision 13
trigger evaluator can exclude smoke/test rows from real-demand counts.

Backfill flags any row whose email lives in an RFC 2606 reserved
domain (``example.com``, ``example.org``, ``example.net``,
``example``) or in the test-only TLDs (``.test``, ``.invalid``,
``.localhost``). Those domains are reserved by IANA precisely so they
never collide with real production addresses — a perfect fit for
"this is test data" detection.

Background: at Session 1141 review, Rigby surfaced that the Decision 13
paid-interest gate was flipped to ``ready`` by Session 1138's E2E smoke
row (`smoke-test@example.com`, ``willing_pay=49``) and three sibling
test rows from later smoke runs. The gate is supposed to represent
real customer demand; flipping on test data undermines the entire
launch-trigger ritual.
"""
from django.db import migrations, models


RFC_2606_RESERVED_SUFFIXES = (
    "@example.com",
    "@example.org",
    "@example.net",
    "@example",
)
TEST_TLD_SUFFIXES = (
    ".test",
    ".invalid",
    ".localhost",
)


def _is_test_email(email: str) -> bool:
    """Return True when ``email`` is in an RFC 2606 reserved test domain."""
    if not email:
        return False
    lower = email.lower()
    if lower.endswith(RFC_2606_RESERVED_SUFFIXES):
        return True
    return any(lower.endswith(tld) for tld in TEST_TLD_SUFFIXES)


def backfill_test_data_flag(apps, schema_editor):
    """Mark existing FleetPaidInterest rows with test-domain emails as test data."""
    FleetPaidInterest = apps.get_model("core", "FleetPaidInterest")
    count = 0
    for row in FleetPaidInterest.objects.all().only("id", "email"):
        if _is_test_email(row.email):
            row.is_test_data = True
            row.save(update_fields=["is_test_data"])
            count += 1
    if count:
        print(f"  Backfilled is_test_data=True on {count} FleetPaidInterest rows")


def reverse_backfill(apps, schema_editor):
    """No-op reverse — the column itself is dropped by AddField reversal."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0353_session_1140_action_status_needs_regen"),
    ]

    operations = [
        migrations.AddField(
            model_name="fleetpaidinterest",
            name="is_test_data",
            field=models.BooleanField(
                default=False,
                db_index=True,
                help_text=(
                    "True for smoke / E2E / CORS-check submissions whose "
                    "email lives in an RFC 2606 reserved domain "
                    "(example.com / example.org / example.net / .test / "
                    ".invalid / .localhost). evaluate_trigger_state "
                    "excludes these rows from the production demand-gate "
                    "count but still reports them under test_signals."
                ),
            ),
        ),
        migrations.RunPython(backfill_test_data_flag, reverse_backfill),
    ]
