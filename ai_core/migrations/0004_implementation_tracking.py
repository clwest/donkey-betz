# Generated migration for Implementation Tracking models
# Run with: python manage.py migrate backend

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ai_core', '0003_delete_agentknowledgebase_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImplementationSession',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('project_id', models.CharField(max_length=100)),
                ('agent_name', models.CharField(max_length=100)),
                ('agent_task', models.TextField()),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(
                    choices=[
                        ('running', 'Running'),
                        ('completed', 'Completed'),
                        ('failed', 'Failed'),
                        ('rollback', 'Rolled Back'),
                    ],
                    default='running',
                    max_length=20
                )),
                ('git_commit_before', models.CharField(blank=True, max_length=40)),
                ('database_snapshot_before', models.JSONField(blank=True, default=dict)),
                ('file_tree_before', models.JSONField(blank=True, default=list)),
                ('git_commit_after', models.CharField(blank=True, max_length=40)),
                ('database_snapshot_after', models.JSONField(blank=True, default=dict)),
                ('file_tree_after', models.JSONField(blank=True, default=list)),
                ('agent_claimed_changes', models.TextField(blank=True)),
                ('verified_changes', models.JSONField(blank=True, default=list)),
                ('implementation_evidence', models.JSONField(blank=True, default=dict)),
                ('files_modified', models.IntegerField(default=0)),
                ('lines_added', models.IntegerField(default=0)),
                ('lines_removed', models.IntegerField(default=0)),
                ('commands_executed', models.IntegerField(default=0)),
                ('database_changes', models.IntegerField(default=0)),
                ('rollback_script', models.TextField(blank=True)),
                ('can_rollback', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'implementation_sessions',
                'ordering': ['-started_at'],
            },
        ),
        migrations.CreateModel(
            name='FileModification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_path', models.CharField(max_length=500)),
                ('modification_type', models.CharField(
                    choices=[
                        ('created', 'Created'),
                        ('modified', 'Modified'),
                        ('deleted', 'Deleted'),
                        ('moved', 'Moved'),
                    ],
                    max_length=20
                )),
                ('content_before', models.TextField(blank=True)),
                ('content_after', models.TextField(blank=True)),
                ('diff_output', models.TextField(blank=True)),
                ('size_before', models.IntegerField(default=0)),
                ('size_after', models.IntegerField(default=0)),
                ('lines_changed', models.IntegerField(default=0)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('session', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='file_changes',
                    to='ai_core.implementationsession'
                )),
            ],
            options={
                'db_table': 'file_modifications',
            },
        ),
        migrations.CreateModel(
            name='CommandExecution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('command', models.TextField()),
                ('working_directory', models.CharField(max_length=500)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('exit_code', models.IntegerField(blank=True, null=True)),
                ('stdout_output', models.TextField(blank=True)),
                ('stderr_output', models.TextField(blank=True)),
                ('success', models.BooleanField(blank=True, null=True)),
                ('session', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='commands',
                    to='ai_core.implementationsession'
                )),
            ],
            options={
                'db_table': 'command_executions',
                'ordering': ['started_at'],
            },
        ),
        migrations.CreateModel(
            name='DatabaseChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_name', models.CharField(max_length=100)),
                ('change_type', models.CharField(
                    choices=[
                        ('create', 'Create'),
                        ('insert', 'Insert'),
                        ('update', 'Update'),
                        ('delete', 'Delete'),
                        ('alter', 'Alter'),
                    ],
                    max_length=20
                )),
                ('record_id', models.CharField(blank=True, max_length=100)),
                ('fields_changed', models.JSONField(blank=True, default=list)),
                ('values_before', models.JSONField(blank=True, default=dict)),
                ('values_after', models.JSONField(blank=True, default=dict)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('session', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='db_changes',
                    to='ai_core.implementationsession'
                )),
            ],
            options={
                'db_table': 'database_changes',
            },
        ),
        migrations.CreateModel(
            name='ImplementationEvidence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('evidence_type', models.CharField(
                    choices=[
                        ('git_commit', 'Git Commit'),
                        ('file_checksum', 'File Checksum'),
                        ('database_record', 'Database Record'),
                        ('command_output', 'Command Output'),
                        ('screenshot', 'Screenshot'),
                        ('test_result', 'Test Result'),
                        ('build_artifact', 'Build Artifact'),
                    ],
                    max_length=30
                )),
                ('evidence_data', models.JSONField()),
                ('description', models.TextField()),
                ('verified_at', models.DateTimeField(auto_now_add=True)),
                ('session', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='evidence',
                    to='ai_core.implementationsession'
                )),
            ],
            options={
                'db_table': 'implementation_evidence',
            },
        ),
    ]