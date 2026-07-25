# Generated for Session 2964: Golden Evals validator harness (canon_v2 ratified S2963).
#
# Bounded to GoldenEvalRun only — unrelated model drift observed at
# ``makemigrations`` time (Narrative*, HAIDispatchLog AlterField churn, etc.)
# is intentionally NOT bundled here; that drift belongs to its own remediation
# PR so PR-1 stays reviewable + Rigby's post-merge dogfood targets a
# well-scoped schema delta.

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0394_s2933_signal_dispatch"),
    ]

    operations = [
        migrations.CreateModel(
            name="GoldenEvalRun",
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
                (
                    "run_id",
                    models.UUIDField(
                        db_index=True,
                        help_text=(
                            "Groups all rows produced by one ``run_golden_evals`` "
                            "invocation. Drift dashboards cohort-query on this."
                        ),
                    ),
                ),
                (
                    "yaml_path",
                    models.CharField(
                        db_index=True,
                        help_text="Relative path to the evals/tier1/*.yaml file that produced this row.",
                        max_length=255,
                    ),
                ),
                (
                    "prompt_id",
                    models.CharField(
                        db_index=True,
                        help_text=(
                            "``prompts[*].id`` from the YAML (e.g., "
                            "'rigby_happy_01_constitution_authoring_initiatives_intent')."
                        ),
                        max_length=255,
                    ),
                ),
                (
                    "substrate_type",
                    models.CharField(
                        db_index=True,
                        help_text=(
                            "One of ``core.services.golden_evals.context.KNOWN_SUBSTRATES`` "
                            "(currently 'agent_execution' or 'chat_conversation'). "
                            "Validated at write-time by the harness."
                        ),
                        max_length=64,
                    ),
                ),
                (
                    "primary_row_id",
                    models.CharField(
                        blank=True,
                        help_text=(
                            "Substrate-native PK for the row the adapter observed. "
                            "Blank when the harness ran in ``--dry-run`` mode and no "
                            "substrate row was produced (skeleton dispatch)."
                        ),
                        max_length=64,
                    ),
                ),
                (
                    "evidence_ledger_refs",
                    models.JSONField(
                        blank=True,
                        default=list,
                        help_text=(
                            "List of substrate refs the adapter identified as evidence "
                            "(ToolCallRecord IDs, LLMCallLog IDs, related "
                            "deliverable_factory rows, etc). Shape: "
                            "[{'kind': 'tool_call_record', 'id': '...'}, ...]."
                        ),
                    ),
                ),
                (
                    "passed",
                    models.BooleanField(
                        blank=True,
                        db_index=True,
                        help_text=(
                            "True/False after acceptance-criteria runners execute; "
                            "NULL when the row was produced in ``--dry-run`` mode "
                            "(skeleton dispatch, no validation yet)."
                        ),
                        null=True,
                    ),
                ),
                (
                    "failure_reasons",
                    models.JSONField(
                        blank=True,
                        default=list,
                        help_text=(
                            "List of {predicate, detail} dicts for each acceptance-criteria "
                            "predicate that failed. Empty when ``passed=True`` or "
                            "``passed=NULL``."
                        ),
                    ),
                ),
                (
                    "finalized_at",
                    models.DateTimeField(
                        blank=True,
                        help_text=(
                            "Substrate finalization timestamp (per canon_v2 Item 6). "
                            "NULL when the substrate row is still in a mutable phase "
                            "(e.g., ChatConversation pre-response) — the adapter "
                            "surfaces this so validators can defer or skip mid-flight rows."
                        ),
                        null=True,
                    ),
                ),
                (
                    "latency_ms",
                    models.IntegerField(
                        blank=True,
                        help_text=(
                            "Opt-in latency evidence per canon_v2 Item 3. Only populated "
                            "when the slice YAML declares latency as an evidence dimension."
                        ),
                        null=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={
                "db_table": "core_golden_eval_run",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="goldenevalrun",
            index=models.Index(
                fields=["run_id", "yaml_path"],
                name="core_golden_run_id_cbf512_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="goldenevalrun",
            index=models.Index(
                fields=["yaml_path", "prompt_id"],
                name="core_golden_yaml_pa_780165_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="goldenevalrun",
            index=models.Index(
                fields=["substrate_type", "passed"],
                name="core_golden_substra_fe8d1b_idx",
            ),
        ),
    ]
