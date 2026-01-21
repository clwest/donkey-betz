"""
Project and code generation models
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from ..base.models import UnifiedBaseModel


class GeneratedProject(UnifiedBaseModel):
    """
    Stores information about AI-generated projects
    """
    name = models.CharField(max_length=255, help_text="Project name")
    project_type = models.CharField(max_length=100, help_text="Type of project (e.g., ecommerce, content_factory)")
    description = models.TextField(blank=True, help_text="Project description")
    agents_used = ArrayField(
        models.CharField(max_length=100),
        default=list,
        help_text="List of agent names that worked on this project"
    )
    advisors_consulted = ArrayField(
        models.CharField(max_length=100),
        default=list,
        help_text="List of advisors consulted for this project"
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ('generating', 'Generating'),
            ('completed', 'Completed'),
            ('error', 'Error'),
            ('cancelled', 'Cancelled')
        ],
        default='generating'
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='generated_projects',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'core_generated_projects'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.project_type})"


class GeneratedCode(UnifiedBaseModel):
    """
    Stores AI-generated code files with full persistence
    """
    project = models.ForeignKey(
        GeneratedProject,
        on_delete=models.CASCADE,
        related_name='code_files'
    )
    filename = models.CharField(max_length=255, help_text="Name of the file")
    file_path = models.CharField(max_length=500, help_text="Relative path from project root")
    content = models.TextField(help_text="The actual code content")
    language = models.CharField(
        max_length=50,
        choices=[
            ('python', 'Python'),
            ('javascript', 'JavaScript'),
            ('html', 'HTML'),
            ('css', 'CSS'),
            ('sql', 'SQL'),
            ('json', 'JSON'),
            ('yaml', 'YAML'),
            ('other', 'Other')
        ],
        default='python'
    )
    agent_creator = models.CharField(
        max_length=100,
        help_text="Name of the agent that created this code"
    )
    task_description = models.TextField(
        blank=True,
        help_text="Description of the task this code was created for"
    )
    is_latest = models.BooleanField(
        default=True,
        help_text="Whether this is the latest version of this file"
    )
    execution_status = models.CharField(
        max_length=50,
        choices=[
            ('untested', 'Untested'),
            ('success', 'Executed Successfully'),
            ('error', 'Execution Error'),
            ('timeout', 'Execution Timeout'),
            ('fixed', 'Auto-Fixed and Working')
        ],
        default='untested'
    )
    execution_output = models.TextField(
        blank=True,
        help_text="Output from code execution or error messages"
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='generated_code',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'core_generated_code'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'filename']),
            models.Index(fields=['project', 'is_latest']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.filename} - {self.project.name}"

    def save(self, *args, **kwargs):
        # When saving a new version, mark others as not latest
        if self.is_latest:
            GeneratedCode.objects.filter(
                project=self.project,
                filename=self.filename
            ).exclude(id=self.id).update(is_latest=False)
        super().save(*args, **kwargs)