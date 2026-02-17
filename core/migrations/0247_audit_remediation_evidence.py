"""
Session 1023: Add evidence gate fields to AuditRemediationTask.

Adds 'spec_complete' status and 4 evidence fields so tasks can't be marked
'completed' without proof of real code artifacts (commit, PR, diff, etc.).
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0246_code_artifact_model"),
    ]

    operations = [
        # Add spec_complete to STATUS_CHOICES (VARCHAR(20) already fits 13 chars)
        migrations.AlterField(
            model_name='auditremediationtask',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('assigned', 'Assigned'),
                    ('in_progress', 'In Progress'),
                    ('spec_complete', 'Spec Complete'),
                    ('completed', 'Completed'),
                    ('failed', 'Failed'),
                    ('cancelled', 'Cancelled'),
                ],
                default='pending',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='auditremediationtask',
            name='evidence_type',
            field=models.CharField(
                choices=[
                    ('none', 'No Evidence'),
                    ('commit', 'Git Commit'),
                    ('pr', 'Pull Request'),
                    ('diff', 'Diff/Patch'),
                    ('patch_artifact', 'Patch Artifact'),
                    ('manual_verify', 'Manually Verified'),
                ],
                default='none',
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name='auditremediationtask',
            name='evidence_ref',
            field=models.CharField(
                blank=True,
                help_text='Commit hash, PR URL, or CodeArtifact UUID',
                max_length=500,
            ),
        ),
        migrations.AddField(
            model_name='auditremediationtask',
            name='verified_by',
            field=models.CharField(
                blank=True,
                help_text='User or agent that verified the evidence',
                max_length=100,
            ),
        ),
        migrations.AddField(
            model_name='auditremediationtask',
            name='evidence_verified_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
