# Session 1098 Fix B-full: DeliverableAppend table.
#
# Purely additive migration. No data changes, no schema rewrites. The
# table stays empty until DELIVERABLE_APPEND_ENABLED flips to True and
# a caller invokes append_to_deliverable(). Rollback = drop table.
#
# See core/models_deliverable_appends.py and
# docs/plans/SESSION_1098_FIX_B_FULL_TICKET.md.

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0336_agentexecution_parent_root_lineage'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliverableAppend',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True,
                        serialize=False, verbose_name='ID',
                    ),
                ),
                (
                    'call_id',
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        help_text=(
                            'Callers pass the LLMCallEvent.call_id here so '
                            'retries with the same (deliverable, call_id, '
                            'chunk_index) dedupe automatically via the '
                            'unique constraint.'
                        ),
                    ),
                ),
                (
                    'expected_initiative_id',
                    models.UUIDField(
                        blank=True,
                        help_text=(
                            'Optional. The initiative_id the caller *expected* '
                            'the Deliverable to still be linked to at commit '
                            'time. If set and it does not match '
                            'Deliverable.initiative_id inside the SELECT FOR '
                            'UPDATE transaction, the append is recorded as '
                            'status=superseded and routed to a fallback. See '
                            'core/services/deliverable_append_service.'
                            'append_to_deliverable.'
                        ),
                        null=True,
                    ),
                ),
                (
                    'execution_id',
                    models.UUIDField(
                        blank=True,
                        db_index=True,
                        help_text=(
                            'Owning AgentExecution.id — matches '
                            'LLMCallEvent.execution_id.'
                        ),
                        null=True,
                    ),
                ),
                (
                    'agent_name',
                    models.CharField(db_index=True, max_length=120),
                ),
                ('content', models.TextField()),
                (
                    'append_offset',
                    models.IntegerField(
                        blank=True,
                        help_text=(
                            'Byte offset into Deliverable.content where this '
                            'append starts. Set when status transitions '
                            'pending -> committed.'
                        ),
                        null=True,
                    ),
                ),
                (
                    'chunk_index',
                    models.IntegerField(
                        default=0,
                        help_text=(
                            'For streaming: 0-based index within a single '
                            'call. Unique per (deliverable, call_id). Non-'
                            'streaming callers leave this at 0.'
                        ),
                    ),
                ),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('pending', 'Pending'),
                            ('committed', 'Committed'),
                            ('failed', 'Failed'),
                            ('superseded', 'Superseded'),
                        ],
                        db_index=True,
                        default='pending',
                        max_length=16,
                    ),
                ),
                (
                    'failure_reason',
                    models.CharField(blank=True, default='', max_length=500),
                ),
                (
                    'routing_metadata',
                    models.JSONField(blank=True, default=dict),
                ),
                (
                    'created_at',
                    models.DateTimeField(auto_now_add=True, db_index=True),
                ),
                (
                    'committed_at',
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    'deliverable',
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name='appends',
                        to='core.deliverable',
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name='deliverableappend',
            index=models.Index(
                fields=['deliverable', 'status'],
                name='deliv_append_deliv_status',
            ),
        ),
        migrations.AddIndex(
            model_name='deliverableappend',
            index=models.Index(
                fields=['execution_id', '-created_at'],
                name='deliv_append_exec_time',
            ),
        ),
        migrations.AddIndex(
            model_name='deliverableappend',
            index=models.Index(
                fields=['-created_at', 'status'],
                name='deliv_append_time_status',
            ),
        ),
        migrations.AddConstraint(
            model_name='deliverableappend',
            constraint=models.UniqueConstraint(
                fields=('deliverable', 'call_id', 'chunk_index'),
                name='deliverable_append_idempotent',
            ),
        ),
    ]
