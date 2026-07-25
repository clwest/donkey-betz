# Generated for Session 2965: Golden Evals validator harness PR-2a.
#
# Extends GoldenEvalRun with two new fields surfaced by S2965 T1 SIGN
# raw-ORM verification (Rigby A2 REVISE + Chris D-verdict 2026-07-25):
#
#   - ``evidence_source`` — records where the adapter drew tool-call evidence
#     from (``toolcallrecord_ledger`` / ``metadata_cache`` /
#     ``agent_execution_native``). Introduced after raw-ORM discovery that
#     ``ToolCallRecord`` PA writes silently regressed 2026-06-19 (35d) and
#     ``trace_id=NULL`` on 100% of 5,430 rows.
#
#   - ``ledger_health`` — signal to downstream predicates about
#     ledger-evidence trustworthiness (``ok`` / ``stale`` / ``unavailable``).
#     Rigby-specific ``no_fabricated_*`` predicates gate on ``ledger_health=ok``
#     and return ``INCONCLUSIVE_SUBSTRATE_BROKEN`` on non-ok health rather
#     than pass/fail against a broken audit trail.
#
# Bounded to GoldenEvalRun only — unrelated model drift (Narrative*,
# HAIDispatchLog AlterField pile) still deferred to its own remediation PR,
# mirroring the S2964 0395 scoping pattern.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0395_s2964_golden_eval_run"),
    ]

    operations = [
        migrations.AddField(
            model_name="goldenevalrun",
            name="evidence_source",
            field=models.CharField(
                max_length=32,
                default="agent_execution_native",
                db_index=True,
                help_text=(
                    "Where the adapter drew tool-call evidence from — one of "
                    "``core.services.golden_evals.context.KNOWN_EVIDENCE_SOURCES`` "
                    "('toolcallrecord_ledger' / 'metadata_cache' / "
                    "'agent_execution_native'). Introduced S2965 PR-2 after "
                    "raw-ORM discovery that ToolCallRecord PA writes silently "
                    "regressed 2026-06-19 (35d). Rigby-specific fabrication "
                    "predicates gate on this + ledger_health before pass/fail."
                ),
            ),
        ),
        migrations.AddField(
            model_name="goldenevalrun",
            name="ledger_health",
            field=models.CharField(
                max_length=16,
                default="ok",
                db_index=True,
                help_text=(
                    "Signal to downstream predicates about ledger-evidence "
                    "trustworthiness for the observation window. One of "
                    "``core.services.golden_evals.context.KNOWN_LEDGER_HEALTH`` "
                    "('ok' / 'stale' / 'unavailable'). Rigby fabrication "
                    "predicates return INCONCLUSIVE_SUBSTRATE_BROKEN on "
                    "non-'ok' health rather than pass/fail against sand."
                ),
            ),
        ),
    ]
