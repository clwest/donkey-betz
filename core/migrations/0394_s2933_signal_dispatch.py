"""Session 2933 A3 v1 — SignalDispatch audit table.

Adds the ``core_signaldispatch`` audit table for signal-triggered agent
dispatches. Mapping rules live in Python
(``core.services.signal_dispatch_service.SIGNAL_DISPATCH_RULES``, Path B
per S2933 Rigby zoom-out) — this migration only creates the audit
surface.

Isolated to a single CreateModel + its indexes to avoid entangling with
the pre-existing model drift (haidispatchlog / narrative / audit
tables) surfaced by `makemigrations` — that drift is tracked in the
bundled dev-env drift slate.
"""
import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0393_s2856_llmcalllog_was_downgraded'),
    ]

    operations = [
        migrations.CreateModel(
            name='SignalDispatch',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    'rule_key',
                    models.CharField(
                        db_index=True,
                        help_text=(
                            "Stable identifier of the (pattern_type, agent) rule that "
                            "produced this dispatch. Sourced from "
                            "``core.services.signal_dispatch_service.SIGNAL_DISPATCH_RULES``."
                        ),
                        max_length=100,
                    ),
                ),
                (
                    'pattern_type',
                    models.CharField(
                        db_index=True,
                        help_text=(
                            "Copied from the triggering SignalCluster for post-hoc queries."
                        ),
                        max_length=30,
                    ),
                ),
                (
                    'agent_name',
                    models.CharField(
                        db_index=True,
                        help_text="AGENT_MAP key that was dispatched (or would have been).",
                        max_length=100,
                    ),
                ),
                (
                    'outcome',
                    models.CharField(
                        choices=[
                            ('queued', 'Queued'),
                            ('dispatched', 'Dispatched'),
                            ('succeeded', 'Succeeded'),
                            ('failed', 'Failed'),
                            ('skipped_cap', 'Skipped — cap reached'),
                            ('skipped_not_actionable', 'Skipped — cluster not actionable'),
                            ('rejected_agent_missing', 'Rejected — agent not in registry'),
                            ('rejected_unknown_rule', 'Rejected — rule key not registered'),
                        ],
                        db_index=True,
                        default='queued',
                        max_length=30,
                    ),
                ),
                (
                    'error_summary',
                    models.TextField(
                        blank=True,
                        default='',
                        help_text=(
                            "Short human-readable failure reason when outcome != succeeded. "
                            "Populated for failed / rejected_* outcomes."
                        ),
                    ),
                ),
                (
                    'input_payload',
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text=(
                            "Frozen context handed to AgentRouter.route (cluster snapshot: "
                            "keywords / strength / confidence / summary / rule_key)."
                        ),
                    ),
                ),
                (
                    'agent_execution_id',
                    models.UUIDField(
                        blank=True,
                        db_index=True,
                        help_text=(
                            "AgentExecution.id captured from AgentResult.execution_id when "
                            "the dispatch produced one. Raw UUID (not FK) so the audit row "
                            "survives execution-row cleanup."
                        ),
                        null=True,
                    ),
                ),
                (
                    'scan_run_id',
                    models.CharField(
                        blank=True,
                        db_index=True,
                        default='',
                        help_text=(
                            "Correlation id shared by all dispatches enqueued in one scan tick. "
                            "Blank for manual dispatches via ``resend_signal_dispatch``."
                        ),
                        max_length=64,
                    ),
                ),
                (
                    'dispatched_at',
                    models.DateTimeField(auto_now_add=True, db_index=True),
                ),
                (
                    'completed_at',
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    'signal_cluster',
                    models.ForeignKey(
                        help_text='The cluster whose threshold crossing triggered this dispatch.',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='dispatches',
                        to='core.signalcluster',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Signal Dispatch',
                'verbose_name_plural': 'Signal Dispatches',
                'ordering': ['-dispatched_at'],
            },
        ),
        migrations.AddIndex(
            model_name='signaldispatch',
            index=models.Index(
                fields=['rule_key', '-dispatched_at'],
                name='core_signal_rule_ke_dd62ae_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='signaldispatch',
            index=models.Index(
                fields=['signal_cluster', 'rule_key'],
                name='core_signal_signal__a9cf01_idx',
            ),
        ),
    ]
