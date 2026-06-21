"""Session 1180 — make AgentFollowupSubscription.expires_at nullable so auto-wake
subscriptions can be execution-lifecycle-bound (NULL expiry = fire on terminal,
regardless of wall-clock runtime). Session 1178 ratified TTL bumps (30s→60s) kept
racing slow agents (ThinkingAgent at 67s blew the 60s TTL in Session 1180 Pass B
Cell 5 attempt); decoupling expiry from runtime closes the race structurally.

Explicit schedule_followup(after_seconds=N) keeps its delayed-reminder semantic
(non-NULL expires_at, time-bounded). Only the implicit auto-wake path writes NULL.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0358_session_1174_agentfollowupsubscription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agentfollowupsubscription',
            name='expires_at',
            field=models.DateTimeField(
                null=True,
                blank=True,
                db_index=True,
                help_text=(
                    "When the subscription expires and becomes ineligible to fire. "
                    "NULL = execution-lifecycle-bound (auto-wake default — fires on terminal "
                    "regardless of runtime). Non-NULL = explicit schedule_followup delayed-wake "
                    "(now() + after_seconds at creation; beat-scheduled cleanup expires non-NULL "
                    "rows whose state='armed' and now() > expires_at)."
                ),
            ),
        ),
    ]
