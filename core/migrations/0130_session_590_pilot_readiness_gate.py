# Generated manually for Session 590 - Pilot Readiness Gate

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0129_delete_gamelinehistory_delete_oddssnapshot_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PilotReadinessGate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('not_started', 'Not Started'), ('in_progress', 'In Progress'), ('ready', 'Ready for Review'), ('approved', 'Approved for Pilot'), ('blocked', 'Blocked'), ('waived', 'Waived (Low Risk)')], default='not_started', max_length=20)),
                ('risk_level', models.CharField(choices=[('low', 'Low - Auto-waivable'), ('medium', 'Medium - Requires basic checklist'), ('high', 'High - Full safety review'), ('critical', 'Critical - Executive approval required')], default='medium', max_length=20)),
                ('risk_factors', models.JSONField(default=list, help_text='List of factors that determined risk level')),
                ('summary', models.TextField(blank=True, help_text='Human-readable summary of what this pilot will test')),
                ('success_criteria', models.TextField(blank=True, help_text='What would make this pilot successful?')),
                ('failure_criteria', models.TextField(blank=True, help_text='What would cause us to stop the pilot?')),
                ('approved_by', models.CharField(blank=True, max_length=100)),
                ('approval_notes', models.TextField(blank=True)),
                ('decision_made_at', models.DateTimeField(blank=True, help_text='When the Boardroom decision was made', null=True)),
                ('gate_started_at', models.DateTimeField(blank=True, help_text='When readiness work began', null=True)),
                ('gate_ready_at', models.DateTimeField(blank=True, help_text='When all checklist items were completed', null=True)),
                ('gate_approved_at', models.DateTimeField(blank=True, help_text='When the gate was approved for pilot', null=True)),
                ('pilot_started_at', models.DateTimeField(blank=True, help_text='When the pilot actually began', null=True)),
                ('pilot_completed_at', models.DateTimeField(blank=True, help_text='When the pilot concluded', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('decision', models.OneToOneField(help_text='The Boardroom decision this gate controls', on_delete=django.db.models.deletion.CASCADE, related_name='readiness_gate', to='core.agentdecisionsummary')),
            ],
            options={
                'verbose_name': 'Pilot Readiness Gate',
                'verbose_name_plural': 'Pilot Readiness Gates',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ReadinessChecklistItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('item_type', models.CharField(choices=[('threat_model', 'Threat Model'), ('consent_lifecycle', 'Consent Lifecycle'), ('encryption_choice', 'Encryption/KMS Choice'), ('adversarial_test', 'Adversarial Test Plan'), ('kill_switch', 'Kill Switch Criteria'), ('rollback_procedure', 'Rollback Procedure'), ('success_metrics', 'Success Metrics'), ('basic_review', 'Basic Review'), ('executive_approval', 'Executive Approval'), ('legal_review', 'Legal Review'), ('security_review', 'Security Review'), ('custom', 'Custom Item')], max_length=30)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('waived', 'Waived'), ('blocked', 'Blocked')], default='pending', max_length=20)),
                ('is_required', models.BooleanField(default=True)),
                ('documentation_url', models.URLField(blank=True, help_text='Link to artifact document')),
                ('documentation_notes', models.TextField(blank=True, help_text='Notes about the artifact')),
                ('assigned_to', models.CharField(blank=True, help_text='Person/agent responsible', max_length=100)),
                ('completed_by', models.CharField(blank=True, max_length=100)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('completion_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('gate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checklist_items', to='core.pilotreadinessgate')),
            ],
            options={
                'verbose_name': 'Readiness Checklist Item',
                'verbose_name_plural': 'Readiness Checklist Items',
                'ordering': ['gate', 'item_type'],
            },
        ),
        migrations.CreateModel(
            name='PilotExecution',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('planned', 'Planned'), ('running', 'Running'), ('paused', 'Paused'), ('completed', 'Completed'), ('stopped', 'Stopped Early'), ('failed', 'Failed')], default='planned', max_length=20)),
                ('scope', models.TextField(blank=True, help_text='What is being tested')),
                ('constraints', models.JSONField(default=list, help_text='Limits on the pilot')),
                ('outcome', models.CharField(choices=[('pending', 'Pending'), ('success', 'Success - Proceed'), ('partial', 'Partial - Iterate'), ('failure', 'Failure - Do Not Proceed'), ('inconclusive', 'Inconclusive - Need More Data')], default='pending', max_length=20)),
                ('outcome_summary', models.TextField(blank=True)),
                ('metrics', models.JSONField(default=dict, help_text='Quantitative results')),
                ('learnings', models.JSONField(default=list, help_text='What we learned')),
                ('kill_switch_triggered', models.BooleanField(default=False)),
                ('kill_switch_reason', models.TextField(blank=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('gate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pilot_executions', to='core.pilotreadinessgate')),
            ],
            options={
                'verbose_name': 'Pilot Execution',
                'verbose_name_plural': 'Pilot Executions',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='pilotreadinessgate',
            index=models.Index(fields=['status'], name='core_pilotr_status_a4e8f0_idx'),
        ),
        migrations.AddIndex(
            model_name='pilotreadinessgate',
            index=models.Index(fields=['risk_level'], name='core_pilotr_risk_le_7c5e82_idx'),
        ),
        migrations.AddIndex(
            model_name='pilotreadinessgate',
            index=models.Index(fields=['-created_at'], name='core_pilotr_created_6f8d12_idx'),
        ),
    ]
