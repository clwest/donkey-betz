# Generated manually for Session 609
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0133_session_599_experiment_halt_and_outcome'),
    ]

    operations = [
        migrations.CreateModel(
            name='KPISnapshot',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('kpi_name', models.CharField(max_length=255)),
                ('value', models.CharField(max_length=100)),
                ('numeric_value', models.FloatField(blank=True, help_text='Parsed numeric value for charting', null=True)),
                ('target_value', models.CharField(blank=True, max_length=100)),
                ('progress_percent', models.FloatField(blank=True, null=True)),
                ('data_source', models.CharField(blank=True, help_text='e.g., spider:mit_tech_review, agent:research', max_length=100)),
                ('source_query', models.TextField(blank=True, help_text='Query or filter used to calculate value')),
                ('snapshot_type', models.CharField(choices=[('auto', 'Automatic'), ('manual', 'Manual'), ('scheduled', 'Scheduled')], default='auto', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('captured_at', models.DateTimeField(auto_now_add=True)),
                ('experiment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kpi_snapshots', to='core.experiment')),
            ],
            options={
                'ordering': ['-captured_at'],
            },
        ),
        migrations.AddIndex(
            model_name='kpisnapshot',
            index=models.Index(fields=['experiment', '-captured_at'], name='core_kpisna_experim_idx'),
        ),
    ]
