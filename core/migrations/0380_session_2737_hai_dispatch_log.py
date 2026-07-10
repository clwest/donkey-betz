"""
Session 2737 — §16 Notification Fanout Wrap-Up Bundle Gap 2 —
HAIDispatchLog cross-channel dispatch audit table.

Hand-authored to scope this migration to ONLY the HAIDispatchLog model.
Django's ``makemigrations`` at HEAD picks up unrelated pending drift on
Narrative* models that is out-of-scope for the §16 wrap-up bundle; that
drift belongs in a separate migration owned by the Narrative subsystem
maintainer, not this bundle.

Ratified rules governing this migration:
- PLAYBOOK-2.2.2 (CDR discipline) — CDR-001 §7 Gap 2 covers scope
- PLAYBOOK-3.2.2 (acceptance-tests-first) — AT16-2 pre-drafted
"""
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0379_toolcallrecord_truncation_signals'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HAIDispatchLog',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'source_type',
                    models.CharField(
                        help_text='HAI source_type — matches HumanAttentionItem.source_type',
                        max_length=100,
                    ),
                ),
                (
                    'source_id',
                    models.CharField(
                        help_text='HAI source_id — matches HumanAttentionItem.source_id',
                        max_length=200,
                    ),
                ),
                (
                    'channel',
                    models.CharField(
                        help_text=(
                            "Channel identifier — 'discord' | 'webpush' | 'expo' "
                            "| 'inbox' as of v1. New channels MAY be added without "
                            'schema migration; the enum contract is on '
                            'ChannelDispatchState, not on this field.'
                        ),
                        max_length=32,
                    ),
                ),
                ('dispatched_at', models.DateTimeField(auto_now_add=True)),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('not_attempted', 'NOT_ATTEMPTED'),
                            ('succeeded', 'SUCCEEDED'),
                            ('failed', 'FAILED'),
                            ('suppressed_by_producer', 'SUPPRESSED_BY_PRODUCER'),
                            ('kill_switch', 'KILL_SWITCH'),
                            ('gated_out', 'GATED_OUT'),
                        ],
                        default='not_attempted',
                        max_length=32,
                    ),
                ),
                ('error_message', models.TextField(blank=True, default='')),
                ('executor_actor', models.CharField(blank=True, default='', max_length=200)),
                ('sponsor_actor', models.CharField(blank=True, default='', max_length=200)),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name='hai_dispatch_logs',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'principal_user',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name='hai_dispatch_logs_as_principal',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'db_table': 'hai_dispatch_logs',
                'ordering': ['-dispatched_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='haidispatchlog',
            constraint=models.UniqueConstraint(
                fields=('user', 'source_type', 'source_id', 'channel'),
                name='hai_dispatch_log_dedup_recipient_source_channel',
            ),
        ),
        migrations.AddIndex(
            model_name='haidispatchlog',
            index=models.Index(
                fields=['user', 'dispatched_at'],
                name='hai_dispatch__user_id_5c3e73_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='haidispatchlog',
            index=models.Index(
                fields=['source_type', 'source_id'],
                name='hai_dispatch__source__ac9d76_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='haidispatchlog',
            index=models.Index(
                fields=['channel', 'status', 'dispatched_at'],
                name='hai_dispatch__channel_a5e19b_idx',
            ),
        ),
    ]
