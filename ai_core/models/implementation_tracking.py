"""
Implementation Tracking Models

Tracks REAL changes made by agents to prove they actually implemented things,
not just provided advice.
"""

import subprocess
from django.db import models
from django.utils import timezone


import logging
logger = logging.getLogger(__name__)

class ImplementationSession(models.Model):
    """Tracks a complete agent implementation session"""

    id = models.AutoField(primary_key=True)
    project_id = models.CharField(max_length=100)
    agent_name = models.CharField(max_length=100)
    agent_task = models.TextField()

    # Session tracking
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('rollback', 'Rolled Back'),
    ], default='running')

    # Pre-implementation state
    git_commit_before = models.CharField(max_length=40, blank=True)  # Git commit hash
    database_snapshot_before = models.JSONField(default=dict, blank=True)
    file_tree_before = models.JSONField(default=list, blank=True)

    # Post-implementation state
    git_commit_after = models.CharField(max_length=40, blank=True)
    database_snapshot_after = models.JSONField(default=dict, blank=True)
    file_tree_after = models.JSONField(default=list, blank=True)

    # Agent output vs actual changes
    agent_claimed_changes = models.TextField(blank=True)  # What agent said it would do
    verified_changes = models.JSONField(default=list, blank=True)  # What it actually did
    implementation_evidence = models.JSONField(default=dict, blank=True)  # Proof of changes

    # Metrics
    files_modified = models.IntegerField(default=0)
    lines_added = models.IntegerField(default=0)
    lines_removed = models.IntegerField(default=0)
    commands_executed = models.IntegerField(default=0)
    database_changes = models.IntegerField(default=0)

    # Rollback capability
    rollback_script = models.TextField(blank=True)  # Script to undo changes
    can_rollback = models.BooleanField(default=False)

    class Meta:
        app_label = 'backend'
        db_table = 'implementation_sessions'
        ordering = ['-started_at']


class FileModification(models.Model):
    """Tracks individual file changes made during implementation"""

    session = models.ForeignKey(ImplementationSession, on_delete=models.CASCADE, related_name='file_changes')
    file_path = models.CharField(max_length=500)
    modification_type = models.CharField(max_length=20, choices=[
        ('created', 'Created'),
        ('modified', 'Modified'),
        ('deleted', 'Deleted'),
        ('moved', 'Moved'),
    ])

    # Content tracking
    content_before = models.TextField(blank=True)
    content_after = models.TextField(blank=True)
    diff_output = models.TextField(blank=True)  # Git diff output

    # File stats
    size_before = models.IntegerField(default=0)
    size_after = models.IntegerField(default=0)
    lines_changed = models.IntegerField(default=0)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'backend'
        db_table = 'file_modifications'


class CommandExecution(models.Model):
    """Tracks commands executed by agents during implementation"""

    session = models.ForeignKey(ImplementationSession, on_delete=models.CASCADE, related_name='commands')
    command = models.TextField()
    working_directory = models.CharField(max_length=500)

    # Execution details
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    exit_code = models.IntegerField(null=True, blank=True)

    # Output
    stdout_output = models.TextField(blank=True)
    stderr_output = models.TextField(blank=True)

    # Success tracking
    success = models.BooleanField(null=True, blank=True)

    class Meta:
        app_label = 'backend'
        db_table = 'command_executions'
        ordering = ['started_at']


class DatabaseChange(models.Model):
    """Tracks database changes made during implementation"""

    session = models.ForeignKey(ImplementationSession, on_delete=models.CASCADE, related_name='db_changes')
    table_name = models.CharField(max_length=100)
    change_type = models.CharField(max_length=20, choices=[
        ('create', 'Create'),
        ('insert', 'Insert'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('alter', 'Alter'),
    ])

    # Change details
    record_id = models.CharField(max_length=100, blank=True)  # Primary key of affected record
    fields_changed = models.JSONField(default=list, blank=True)  # List of changed field names
    values_before = models.JSONField(default=dict, blank=True)  # Old values
    values_after = models.JSONField(default=dict, blank=True)  # New values

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'backend'
        db_table = 'database_changes'


class ImplementationEvidence(models.Model):
    """Stores evidence that implementation actually occurred"""

    session = models.ForeignKey(ImplementationSession, on_delete=models.CASCADE, related_name='evidence')
    evidence_type = models.CharField(max_length=30, choices=[
        ('git_commit', 'Git Commit'),
        ('file_checksum', 'File Checksum'),
        ('database_record', 'Database Record'),
        ('command_output', 'Command Output'),
        ('screenshot', 'Screenshot'),
        ('test_result', 'Test Result'),
        ('build_artifact', 'Build Artifact'),
    ])

    evidence_data = models.JSONField()  # The actual evidence
    description = models.TextField()
    verified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'backend'
        db_table = 'implementation_evidence'


# Utility functions for implementation tracking

def start_implementation_session(project_id: str, agent_name: str, task_description: str) -> ImplementationSession:
    """Start tracking an implementation session"""
    session = ImplementationSession.objects.create(
        project_id=project_id,
        agent_name=agent_name,
        agent_task=task_description,
        status='running'
    )

    # Capture pre-implementation state
    session.git_commit_before = get_current_git_commit()
    session.file_tree_before = capture_file_tree()
    session.database_snapshot_before = capture_database_snapshot()
    session.save()

    return session


def complete_implementation_session(session: ImplementationSession, agent_output: str) -> dict:
    """Complete tracking and generate implementation report"""

    # Capture post-implementation state
    session.git_commit_after = get_current_git_commit()
    session.file_tree_after = capture_file_tree()
    session.database_snapshot_after = capture_database_snapshot()
    session.agent_claimed_changes = agent_output
    session.completed_at = timezone.now()

    # Analyze what actually changed
    changes = analyze_implementation_changes(session)
    session.verified_changes = changes['verified_changes']
    session.implementation_evidence = changes['evidence']
    session.files_modified = changes['stats']['files_modified']
    session.lines_added = changes['stats']['lines_added']
    session.lines_removed = changes['stats']['lines_removed']
    session.commands_executed = session.commands.count()
    session.database_changes = session.db_changes.count()

    # Generate rollback script
    session.rollback_script = generate_rollback_script(session)
    session.can_rollback = bool(session.rollback_script)

    # Determine final status
    if changes['stats']['total_changes'] > 0:
        session.status = 'completed'
    else:
        session.status = 'failed'  # Agent claimed to do work but made no changes

    session.save()

    return {
        'session': session,
        'changes': changes,
        'has_real_changes': changes['stats']['total_changes'] > 0,
        'evidence_count': len(changes['evidence']),
        'rollback_available': session.can_rollback
    }


def get_current_git_commit() -> str:
    """Get current git commit hash"""
    try:
        result = subprocess.run(['git', 'rev-parse', 'HEAD'],
                              capture_output=True, text=True,
                              cwd='/Users/donkeyking/development/unified-donkey-betz')
        return result.stdout.strip() if result.returncode == 0 else ''
    except Exception as _e:
        logger.warning(
            "implementation_tracking.get_current_git_commit: swallowed (%s: %s) — returning default",
            type(_e).__name__, _e,
        )
        return ''


def capture_file_tree() -> list:
    """Capture current file tree state"""
    try:
        result = subprocess.run(['find', '.', '-type', 'f', '-name', '*.py', '-o', '-name', '*.html', '-o', '-name', '*.js'],
                              capture_output=True, text=True,
                              cwd='/Users/donkeyking/development/unified-donkey-betz')
        return result.stdout.strip().split('\n') if result.returncode == 0 else []
    except Exception as _e:
        logger.warning(
            "implementation_tracking.capture_file_tree: swallowed (%s: %s) — returning default",
            type(_e).__name__, _e,
        )
        return []


def capture_database_snapshot() -> dict:
    """Capture relevant database state"""
    # For now, just return basic counts - could be expanded
    from core.models import GeneratedProject

    return {
        'generated_projects_count': GeneratedProject.objects.count(),
        'timestamp': timezone.now().isoformat()
    }


def analyze_implementation_changes(session: ImplementationSession) -> dict:
    """Analyze what actually changed during implementation"""
    changes = {
        'verified_changes': [],
        'evidence': {},
        'stats': {
            'files_modified': 0,
            'lines_added': 0,
            'lines_removed': 0,
            'total_changes': 0
        }
    }

    # Check for git changes
    if session.git_commit_before != session.git_commit_after:
        git_diff = get_git_diff(session.git_commit_before, session.git_commit_after)
        if git_diff:
            changes['verified_changes'].append({
                'type': 'git_changes',
                'description': f'Git commit changed from {session.git_commit_before[:8]} to {session.git_commit_after[:8]}',
                'diff': git_diff
            })
            changes['evidence']['git_diff'] = git_diff
            changes['stats']['total_changes'] += 1

    # Check file modifications from tracked changes
    file_mods = session.file_changes.all()
    changes['stats']['files_modified'] = file_mods.count()

    for mod in file_mods:
        changes['verified_changes'].append({
            'type': 'file_modification',
            'file': mod.file_path,
            'modification_type': mod.modification_type,
            'lines_changed': mod.lines_changed
        })
        changes['stats']['total_changes'] += 1

        if mod.lines_changed > 0:
            changes['stats']['lines_added'] += mod.lines_changed

    # Check command executions
    commands = session.commands.all()
    if commands.count() > 0:
        changes['verified_changes'].append({
            'type': 'command_executions',
            'count': commands.count(),
            'commands': [{'command': cmd.command, 'success': cmd.success} for cmd in commands]
        })
        changes['stats']['total_changes'] += commands.count()
        changes['evidence']['commands'] = list(commands.values())

    # Check database changes
    db_changes = session.db_changes.all()
    if db_changes.count() > 0:
        changes['verified_changes'].append({
            'type': 'database_changes',
            'count': db_changes.count(),
            'changes': list(db_changes.values())
        })
        changes['stats']['total_changes'] += db_changes.count()
        changes['evidence']['database'] = list(db_changes.values())

    return changes


def get_git_diff(commit_before: str, commit_after: str) -> str:
    """Get git diff between two commits"""
    try:
        result = subprocess.run(['git', 'diff', commit_before, commit_after],
                              capture_output=True, text=True,
                              cwd='/Users/donkeyking/development/unified-donkey-betz')
        return result.stdout if result.returncode == 0 else ''
    except Exception as _e:
        logger.warning(
            "implementation_tracking.get_git_diff: swallowed (%s: %s) — returning default",
            type(_e).__name__, _e,
        )
        return ''


def generate_rollback_script(session: ImplementationSession) -> str:
    """Generate script to rollback implementation changes"""
    script_lines = [
        "#!/bin/bash",
        "# Rollback script for implementation session {}".format(session.id),
        "# Generated at {}".format(timezone.now().isoformat()),
        ""
    ]

    # Add git rollback if commit changed
    if session.git_commit_before and session.git_commit_after and session.git_commit_before != session.git_commit_after:
        script_lines.extend([
            "# Rollback git changes",
            f"git reset --hard {session.git_commit_before}",
            ""
        ])

    # Add file rollbacks
    for file_mod in session.file_changes.all():
        if file_mod.modification_type == 'created':
            script_lines.append(f"rm -f '{file_mod.file_path}'")
        elif file_mod.modification_type == 'modified' and file_mod.content_before:
            script_lines.extend([
                f"# Restore {file_mod.file_path}",
                f"cat > '{file_mod.file_path}' << 'EOF'",
                file_mod.content_before,
                "EOF",
                ""
            ])

    return '\n'.join(script_lines)