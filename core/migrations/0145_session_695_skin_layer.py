"""
Migration: Session 695 - SKIN Layer Models

Creates the three core models for the SKIN (Project Execution System) layer:
- ProjectWorkspace: Target projects that agents work on
- WorkspaceOperation: Audit trail of all operations
- WorkspaceContext: Cached understanding of project structure

Human Body Metaphor:
    SKIN = The boundary where AI touches reality (file system, git, builds)
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.contrib.postgres.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0143_session_686_human_interface_layer'),  # Skip deleted 0144
    ]

    operations = [
        # ==================== ProjectWorkspace ====================
        migrations.CreateModel(
            name='ProjectWorkspace',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='Human-readable project name', max_length=200)),
                ('description', models.TextField(blank=True, help_text='Project description and notes')),
                ('workspace_type', models.CharField(
                    choices=[
                        ('local', 'Local Directory'),
                        ('git_remote', 'Git Remote Repository'),
                        ('sandbox', 'Isolated Sandbox'),
                        ('container', 'Docker Container')
                    ],
                    default='local',
                    max_length=50
                )),
                ('root_path', models.CharField(help_text='Absolute path to project root', max_length=500)),
                ('git_remote_url', models.CharField(blank=True, help_text='Git remote URL if applicable', max_length=500)),
                ('tech_stack', models.JSONField(default=dict, help_text='Detected or configured tech stack')),
                ('entry_points', models.JSONField(default=dict, help_text='Key directories in the project')),
                ('allow_file_write', models.BooleanField(default=True, help_text='Allow agents to create/modify files')),
                ('allow_file_delete', models.BooleanField(default=False, help_text='Allow agents to delete files')),
                ('allow_command_execution', models.BooleanField(default=True, help_text='Allow agents to run shell commands')),
                ('allow_git_operations', models.BooleanField(default=True, help_text='Allow agents to perform git operations')),
                ('protected_paths', django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=200),
                    blank=True,
                    default=list,
                    help_text='Paths that agents cannot modify',
                    size=None
                )),
                ('require_human_review', models.BooleanField(default=False, help_text='Require human approval before applying changes')),
                ('is_active', models.BooleanField(default=False, help_text='Is this the currently active workspace?')),
                ('last_operation_at', models.DateTimeField(blank=True, null=True, help_text='When was the last operation performed?')),
                ('current_branch', models.CharField(blank=True, help_text='Current git branch', max_length=100)),
                ('total_operations', models.IntegerField(default=0, help_text='Total operations performed')),
                ('total_files_written', models.IntegerField(default=0, help_text='Total files created/modified')),
                ('total_commits', models.IntegerField(default=0, help_text='Total git commits made by agents')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='project_workspaces',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Project Workspace',
                'verbose_name_plural': 'Project Workspaces',
                'db_table': 'core_project_workspaces',
                'ordering': ['-updated_at'],
            },
        ),

        # ProjectWorkspace indexes
        migrations.AddIndex(
            model_name='projectworkspace',
            index=models.Index(fields=['user', 'is_active'], name='core_projec_user_id_8f3a1c_idx'),
        ),
        migrations.AddIndex(
            model_name='projectworkspace',
            index=models.Index(fields=['user', '-updated_at'], name='core_projec_user_id_a2b4d5_idx'),
        ),

        # Unique constraint: only one active workspace per user
        migrations.AddConstraint(
            model_name='projectworkspace',
            constraint=models.UniqueConstraint(
                condition=models.Q(('is_active', True)),
                fields=('user',),
                name='unique_active_workspace_per_user'
            ),
        ),

        # ==================== WorkspaceOperation ====================
        migrations.CreateModel(
            name='WorkspaceOperation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('agent_name', models.CharField(help_text='Name of the agent that performed this operation', max_length=100)),
                ('agent_task', models.TextField(blank=True, help_text='The task description that led to this operation')),
                ('operation_type', models.CharField(
                    choices=[
                        ('file_create', 'Create File'),
                        ('file_modify', 'Modify File'),
                        ('file_delete', 'Delete File'),
                        ('file_rename', 'Rename File'),
                        ('command_exec', 'Execute Command'),
                        ('git_commit', 'Git Commit'),
                        ('git_branch', 'Git Branch'),
                        ('git_checkout', 'Git Checkout'),
                        ('git_merge', 'Git Merge'),
                        ('build_run', 'Run Build'),
                        ('test_run', 'Run Tests'),
                        ('lint_run', 'Run Linter'),
                        ('deploy', 'Deploy')
                    ],
                    max_length=50
                )),
                ('file_path', models.CharField(blank=True, help_text='Relative path to the file', max_length=500)),
                ('file_content_before', models.TextField(blank=True, help_text='File content before operation')),
                ('file_content_after', models.TextField(blank=True, help_text='File content after operation')),
                ('file_size_before', models.IntegerField(blank=True, null=True, help_text='File size in bytes before')),
                ('file_size_after', models.IntegerField(blank=True, null=True, help_text='File size in bytes after')),
                ('command', models.TextField(blank=True, help_text='Command that was executed')),
                ('command_output', models.TextField(blank=True, help_text='stdout from command execution')),
                ('command_error', models.TextField(blank=True, help_text='stderr from command execution')),
                ('exit_code', models.IntegerField(blank=True, null=True, help_text='Command exit code')),
                ('success', models.BooleanField(default=False, help_text='Did the operation succeed?')),
                ('error_message', models.TextField(blank=True, help_text='Error message if operation failed')),
                ('execution_time_ms', models.IntegerField(blank=True, null=True, help_text='How long the operation took')),
                ('requires_review', models.BooleanField(default=False, help_text='Does this operation require human review?')),
                ('reviewed_by_human', models.BooleanField(default=False, help_text='Has a human reviewed this operation?')),
                ('human_approved', models.BooleanField(blank=True, null=True, help_text='Did the human approve?')),
                ('human_feedback', models.TextField(blank=True, help_text='Human feedback on the operation')),
                ('reviewed_at', models.DateTimeField(blank=True, null=True, help_text='When was this reviewed?')),
                ('can_rollback', models.BooleanField(default=True, help_text='Can this operation be rolled back?')),
                ('rolled_back', models.BooleanField(default=False, help_text='Has this operation been rolled back?')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('rollback_operation', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='rollback_of',
                    to='core.workspaceoperation'
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='workspace_operations',
                    to=settings.AUTH_USER_MODEL
                )),
                ('workspace', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='operations',
                    to='core.projectworkspace'
                )),
            ],
            options={
                'verbose_name': 'Workspace Operation',
                'verbose_name_plural': 'Workspace Operations',
                'db_table': 'core_workspace_operations',
                'ordering': ['-created_at'],
            },
        ),

        # WorkspaceOperation indexes
        migrations.AddIndex(
            model_name='workspaceoperation',
            index=models.Index(fields=['workspace', '-created_at'], name='core_worksp_workspa_a1b2c3_idx'),
        ),
        migrations.AddIndex(
            model_name='workspaceoperation',
            index=models.Index(fields=['workspace', 'operation_type'], name='core_worksp_workspa_d4e5f6_idx'),
        ),
        migrations.AddIndex(
            model_name='workspaceoperation',
            index=models.Index(fields=['agent_name', '-created_at'], name='core_worksp_agent_n_g7h8i9_idx'),
        ),
        migrations.AddIndex(
            model_name='workspaceoperation',
            index=models.Index(fields=['workspace', 'file_path'], name='core_worksp_workspa_j0k1l2_idx'),
        ),
        migrations.AddIndex(
            model_name='workspaceoperation',
            index=models.Index(fields=['requires_review', 'reviewed_by_human'], name='core_worksp_require_m3n4o5_idx'),
        ),

        # ==================== WorkspaceContext ====================
        migrations.CreateModel(
            name='WorkspaceContext',
            fields=[
                ('workspace', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    primary_key=True,
                    related_name='context',
                    serialize=False,
                    to='core.projectworkspace'
                )),
                ('file_tree', models.JSONField(default=dict, help_text='Directory structure with files')),
                ('key_files', models.JSONField(default=dict, help_text='Important files that agents should know about')),
                ('coding_patterns', models.JSONField(default=dict, help_text='Recognized patterns in the codebase')),
                ('dependencies', models.JSONField(default=dict, help_text='Project dependencies')),
                ('import_aliases', models.JSONField(default=dict, help_text='Import aliases/paths configured in the project')),
                ('directory_purposes', models.JSONField(default=dict, help_text='What each directory is for')),
                ('total_files', models.IntegerField(default=0, help_text='Total files in workspace')),
                ('total_directories', models.IntegerField(default=0, help_text='Total directories in workspace')),
                ('total_lines_of_code', models.IntegerField(default=0, help_text='Approximate total lines of code')),
                ('file_type_counts', models.JSONField(default=dict, help_text='Count of files by extension')),
                ('last_scanned_at', models.DateTimeField(auto_now=True, help_text='When was this context last updated?')),
                ('scan_depth', models.IntegerField(default=5, help_text='How deep the directory scan went')),
                ('scan_duration_ms', models.IntegerField(blank=True, null=True, help_text='How long the scan took')),
                ('excluded_patterns', django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=100),
                    blank=True,
                    default=list,
                    help_text='Patterns excluded from scan',
                    size=None
                )),
            ],
            options={
                'verbose_name': 'Workspace Context',
                'verbose_name_plural': 'Workspace Contexts',
                'db_table': 'core_workspace_contexts',
            },
        ),
    ]
