"""S2794 — Create TenantBoundaryHealthReport model (RUR-C1 substrate).

Scoped migration: TenantBoundaryHealthReport only. The full auto-detect
also picks up unrelated pre-existing Narrative model drift (tracked
separately under 'Model drift arc — 38 auto-migrations queued' per
S2793 open doc line 60); this migration deliberately excludes those
per PR scope discipline.
"""
import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0384_s2782_agentexecution_celery_task_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="TenantBoundaryHealthReport",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "env",
                    models.CharField(
                        help_text=(
                            "Execution environment: 'local' / 'ci' / 'prod'. "
                            "Populated from PLATFORM_ENV or best-effort autodetect."
                        ),
                        max_length=32,
                    ),
                ),
                (
                    "git_sha",
                    models.CharField(
                        help_text="git HEAD SHA at run time. Empty string if not resolvable.",
                        max_length=40,
                    ),
                ),
                (
                    "runner_identity",
                    models.CharField(
                        help_text="Who ran the suite: username / 'celery-beat' / 'ci' / etc.",
                        max_length=64,
                    ),
                ),
                (
                    "elapsed_secs",
                    models.FloatField(help_text="Wall-clock seconds for the full suite run."),
                ),
                (
                    "total_tests",
                    models.IntegerField(help_text="Total tests discovered + executed."),
                ),
                (
                    "passed",
                    models.IntegerField(help_text="Tests that passed cleanly."),
                ),
                (
                    "failed",
                    models.IntegerField(
                        help_text="Tests that asserted-false (contract violation)."
                    ),
                ),
                (
                    "errored",
                    models.IntegerField(
                        default=0,
                        help_text="Tests that raised an unexpected exception (infra issue).",
                    ),
                ),
                (
                    "skipped",
                    models.IntegerField(
                        default=0,
                        help_text="Tests explicitly skipped (e.g., DB-required in DB-free env).",
                    ),
                ),
                (
                    "failing_test_ids",
                    models.JSONField(
                        default=list,
                        help_text=(
                            "List of dotted test IDs that failed or errored, "
                            "e.g. ['tests.security.test_bucket_a_public_endpoints.TestX.test_y']."
                        ),
                    ),
                ),
                (
                    "coverage_metadata",
                    models.JSONField(
                        default=dict,
                        help_text=(
                            "Per-surface coverage: "
                            "{'sync_http_bucket_a': 'covered', ..., "
                            "'async_celery_task_boundary': 'not_yet_covered (I-0303 not opened)'}"
                        ),
                    ),
                ),
                (
                    "summary_json",
                    models.JSONField(
                        help_text=(
                            "Full serialized summary shape as emitted by the runner. "
                            "Fields above are denormalized for query efficiency; "
                            "this JSONB is the canonical record."
                        )
                    ),
                ),
            ],
            options={
                "verbose_name": "Tenant Boundary Health Report",
                "verbose_name_plural": "Tenant Boundary Health Reports",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="tenantboundaryhealthreport",
            index=models.Index(
                fields=["-created_at"], name="tbhr_created_desc_idx"
            ),
        ),
    ]
