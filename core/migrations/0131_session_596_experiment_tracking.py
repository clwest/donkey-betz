# Generated for Session 596 - Creates Experiment model
# Replaces the delete migration that was causing issues

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0130_session_590_pilot_readiness_gate'),
    ]

    operations = [
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('hypothesis', models.TextField(blank=True)),
                ('kpi_owner', models.CharField(blank=True, max_length=100)),
                ('primary_kpi', models.CharField(blank=True, max_length=255)),
                ('target_value', models.CharField(blank=True, max_length=100)),
                ('current_value', models.CharField(blank=True, max_length=100, null=True)),
                ('secondary_kpis', models.JSONField(blank=True, default=list)),
                ('status', models.CharField(choices=[('running', 'Running'), ('success', 'Success'), ('failure', 'Failure'), ('inconclusive', 'Inconclusive')], default='running', max_length=20)),
                ('extracted_metrics', models.JSONField(blank=True, default=dict)),
                ('result_summary', models.TextField(blank=True, null=True)),
                ('learnings', models.TextField(blank=True, null=True)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('pilot', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='experiment', to='core.pilotexecution')),
            ],
            options={
                'verbose_name': 'Experiment',
                'verbose_name_plural': 'Experiments',
                'ordering': ['-started_at'],
            },
        ),
    ]
