"""
Models for AI Opportunities and Generated Projects
"""
from django.db import models
from django.conf import settings
import json


class AIStrategy(models.Model):
    """Stores discovered AI monetization strategies"""
    strategy_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=300)
    source = models.CharField(max_length=100)
    url = models.URLField(max_length=500, blank=True)
    strategy_type = models.CharField(max_length=100)
    description = models.TextField()
    potential_revenue = models.CharField(max_length=100)
    time_to_implement = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=50)
    final_score = models.FloatField()
    discovered_date = models.DateTimeField(auto_now_add=True)
    actionable_steps = models.JSONField(default=list)

    class Meta:
        app_label = 'ai_opportunities'
        ordering = ['-final_score', '-discovered_date']

    def __str__(self):
        return f"{self.title} ({self.potential_revenue})"


class GeneratedProject(models.Model):
    """Stores AI-generated projects with their code and files"""
    STATUS_CHOICES = [
        ('generated', 'Generated'),
        ('testing', 'Testing'),
        ('deployed', 'Deployed'),
        ('archived', 'Archived'),
    ]

    # Basic info
    project_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    project_type = models.CharField(max_length=100)

    # Relationship to strategy and user
    strategy = models.ForeignKey(AIStrategy, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_projects')

    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='generated')
    revenue_potential = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Advisor insights
    advisor_insights = models.JSONField(default=list, blank=True)

    # Success metrics
    ready_to_launch = models.BooleanField(default=False)
    launch_command = models.CharField(max_length=200, blank=True)

    class Meta:
        app_label = 'ai_opportunities'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.project_type})"


class ProjectFile(models.Model):
    """Stores individual files for each generated project"""
    FILE_TYPE_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('html', 'HTML'),
        ('css', 'CSS'),
        ('markdown', 'Markdown'),
        ('json', 'JSON'),
        ('yaml', 'YAML'),
        ('txt', 'Text'),
        ('requirements', 'Requirements'),
        ('env', 'Environment'),
    ]

    project = models.ForeignKey(GeneratedProject, on_delete=models.CASCADE, related_name='files')
    filename = models.CharField(max_length=200)
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    content = models.TextField()
    file_size = models.IntegerField(default=0)  # in bytes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'ai_opportunities'
        ordering = ['filename']
        unique_together = [['project', 'filename']]

    def save(self, *args, **kwargs):
        # Calculate file size
        self.file_size = len(self.content.encode('utf-8'))

        # Auto-detect file type if not set
        if not self.file_type:
            ext_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.html': 'html',
                '.css': 'css',
                '.md': 'markdown',
                '.json': 'json',
                '.yml': 'yaml',
                '.yaml': 'yaml',
                '.txt': 'txt',
                'requirements.txt': 'requirements',
                '.env': 'env',
            }
            for ext, ftype in ext_map.items():
                if self.filename.endswith(ext) or self.filename == ext:
                    self.file_type = ftype
                    break
            else:
                self.file_type = 'txt'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project.name}/{self.filename}"


class ProjectDeployment(models.Model):
    """Tracks deployment status and URLs for projects"""
    project = models.OneToOneField(GeneratedProject, on_delete=models.CASCADE, related_name='deployment')

    # Deployment status
    is_deployed = models.BooleanField(default=False)
    deployment_url = models.URLField(max_length=500, blank=True)
    deployment_platform = models.CharField(max_length=100, blank=True)  # e.g., 'heroku', 'vercel', 'aws'

    # API keys status (don't store actual keys)
    has_openai_key = models.BooleanField(default=False)
    has_other_keys = models.BooleanField(default=False)

    # Metrics
    total_runs = models.IntegerField(default=0)
    successful_runs = models.IntegerField(default=0)
    last_run = models.DateTimeField(null=True, blank=True)

    # Revenue tracking
    actual_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')

    deployed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Deployment: {self.project.name}"