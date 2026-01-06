# Generated manually for Session 686: Human Interface Layer
# Run: python manage.py migrate core

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0142_session_677_agent_model_configs'),
    ]

    operations = [
        migrations.CreateModel(
            name='HumanAttentionItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('source_type', models.CharField(max_length=50)),
                ('source_id', models.CharField(blank=True, max_length=100)),
                ('source_agent', models.CharField(blank=True, max_length=100)),
                ('item_type', models.CharField(max_length=50)),
                ('title', models.CharField(max_length=200)),
                ('summary', models.TextField()),
                ('payload', models.JSONField(default=dict)),
                ('urgency', models.CharField(choices=[('critical', 'Critical'), ('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], default='medium', max_length=20)),
                ('priority_score', models.FloatField(default=0.0)),
                ('impact_estimate', models.CharField(blank=True, max_length=20)),
                ('ml_prediction', models.JSONField(blank=True, null=True)),
                ('ml_confidence', models.FloatField(blank=True, null=True)),
                ('ml_recommendation', models.CharField(blank=True, max_length=100)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('viewed', 'Viewed'), ('acted', 'Acted'), ('deferred', 'Deferred'), ('ignored', 'Ignored'), ('expired', 'Expired')], default='pending', max_length=20)),
                ('decision', models.CharField(blank=True, choices=[('approve', 'Approve'), ('reject', 'Reject'), ('modify', 'Modify'), ('defer', 'Defer'), ('delegate', 'Delegate'), ('ignore', 'Ignore'), ('escalate', 'Escalate')], max_length=20, null=True)),
                ('decision_feedback', models.TextField(blank=True)),
                ('decision_confidence', models.FloatField(blank=True, null=True)),
                ('decided_at', models.DateTimeField(blank=True, null=True)),
                ('time_to_decision_ms', models.IntegerField(blank=True, null=True)),
                ('human_overrode_ml', models.BooleanField(default=False)),
                ('override_reason', models.TextField(blank=True)),
                ('deferred_until', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('viewed_at', models.DateTimeField(blank=True, null=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attention_items', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-priority_score', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='HumanFeedbackRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('decision', models.CharField(max_length=20)),
                ('feedback_text', models.TextField(blank=True)),
                ('confidence', models.FloatField(blank=True, null=True)),
                ('ml_task_type', models.CharField(blank=True, max_length=50)),
                ('ml_models_used', models.JSONField(blank=True, null=True)),
                ('ml_prediction', models.JSONField(blank=True, null=True)),
                ('ml_confidence', models.FloatField(blank=True, null=True)),
                ('human_agreed_with_ml', models.BooleanField(null=True)),
                ('confidence_delta', models.FloatField(blank=True, null=True)),
                ('fed_to_ml', models.BooleanField(default=False)),
                ('fed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('attention_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedback_records', to='core.humanattentionitem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='HumanPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quiet_hours_start', models.TimeField(blank=True, null=True)),
                ('quiet_hours_end', models.TimeField(blank=True, null=True)),
                ('min_urgency_to_notify', models.CharField(choices=[('critical', 'Critical'), ('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], default='medium', max_length=20)),
                ('preferred_channel', models.CharField(choices=[('discord', 'Discord'), ('web', 'Web Dashboard'), ('email', 'Email')], default='discord', max_length=50)),
                ('review_depth', models.CharField(choices=[('quick', 'Quick (< 30s)'), ('standard', 'Standard (30s-2min)'), ('thorough', 'Thorough (> 2min)')], default='standard', max_length=20)),
                ('auto_approve_low_risk', models.BooleanField(default=False)),
                ('require_review_above_confidence', models.FloatField(default=0.95)),
                ('trusted_agents', models.JSONField(default=list)),
                ('blocked_sources', models.JSONField(default=list)),
                ('topic_weights', models.JSONField(default=dict)),
                ('source_weights', models.JSONField(default=dict)),
                ('avg_decision_time_ms', models.IntegerField(blank=True, null=True)),
                ('approval_rate', models.FloatField(blank=True, null=True)),
                ('total_decisions', models.IntegerField(default=0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='human_preferences', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HumanControlAction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action_type', models.CharField(choices=[('pause_agent', 'Pause Agent'), ('resume_agent', 'Resume Agent'), ('pause_all', 'Pause All'), ('resume_all', 'Resume All'), ('override_decision', 'Override Decision'), ('adjust_threshold', 'Adjust Threshold'), ('block_source', 'Block Source'), ('unblock_source', 'Unblock Source'), ('priority_boost', 'Priority Boost'), ('quiet_mode', 'Quiet Mode'), ('review_mode', 'Review Mode')], max_length=50)),
                ('target_type', models.CharField(choices=[('agent', 'Agent'), ('source', 'Source'), ('model', 'Model'), ('system', 'System')], max_length=50)),
                ('target_id', models.CharField(max_length=100)),
                ('old_value', models.JSONField(blank=True, null=True)),
                ('new_value', models.JSONField(blank=True, null=True)),
                ('reason', models.TextField(blank=True)),
                ('auto_revert_at', models.DateTimeField(blank=True, null=True)),
                ('reverted', models.BooleanField(default=False)),
                ('reverted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='control_actions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='HumanSystemState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('system_paused', models.BooleanField(default=False)),
                ('review_mode', models.BooleanField(default=False)),
                ('quiet_mode', models.BooleanField(default=False)),
                ('quiet_mode_until', models.DateTimeField(blank=True, null=True)),
                ('paused_agents', models.JSONField(default=list)),
                ('ml_confidence_threshold', models.FloatField(default=0.6)),
                ('auto_approve_threshold', models.FloatField(default=0.95)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Human System State',
                'verbose_name_plural': 'Human System State',
            },
        ),
        migrations.AddIndex(
            model_name='humanattentionitem',
            index=models.Index(fields=['user', 'status'], name='core_humana_user_id_a1b2c3_idx'),
        ),
        migrations.AddIndex(
            model_name='humanattentionitem',
            index=models.Index(fields=['user', 'urgency'], name='core_humana_user_id_d4e5f6_idx'),
        ),
        migrations.AddIndex(
            model_name='humanattentionitem',
            index=models.Index(fields=['source_type'], name='core_humana_source__g7h8i9_idx'),
        ),
        migrations.AddIndex(
            model_name='humanattentionitem',
            index=models.Index(fields=['created_at'], name='core_humana_created_j0k1l2_idx'),
        ),
    ]
