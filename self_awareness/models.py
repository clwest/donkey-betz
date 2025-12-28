"""
Self-Awareness Models for Unified Donkey Betz Platform

These models track system introspection, performance metrics, 
code analysis, and autonomous evolution capabilities.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class SystemMetrics(models.Model):
    """Track real-time system performance and health metrics"""
    
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    
    # Performance Metrics
    cpu_usage = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    memory_usage = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    disk_usage = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Application Metrics
    active_agents = models.IntegerField(default=0)
    pending_tasks = models.IntegerField(default=0)
    completed_tasks = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    
    # Database Metrics
    db_query_count = models.IntegerField(default=0)
    db_avg_response_time = models.FloatField(default=0.0)
    
    # Network Metrics
    request_count = models.IntegerField(default=0)
    avg_response_time = models.FloatField(default=0.0)
    
    # Self-Awareness Metrics
    self_analysis_score = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    optimization_opportunities = models.IntegerField(default=0)
    
    class Meta:
        app_label = 'self_awareness'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['cpu_usage']),
            models.Index(fields=['memory_usage']),
        ]

    def __str__(self):
        return f"SystemMetrics({self.timestamp})"


class CodebaseSnapshot(models.Model):
    """Track codebase state and changes for self-analysis"""

    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    # Codebase Statistics
    total_files = models.IntegerField(default=0)
    total_lines = models.IntegerField(default=0)
    python_files = models.IntegerField(default=0)
    javascript_files = models.IntegerField(default=0)

    # Code Quality Metrics
    complexity_score = models.FloatField(default=0.0)
    test_coverage = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    code_duplication = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    # Architecture Analysis
    total_models = models.IntegerField(default=0)
    total_views = models.IntegerField(default=0)
    total_apis = models.IntegerField(default=0)
    total_agents = models.IntegerField(default=0)

    # Dependencies
    third_party_packages = models.JSONField(default=list)
    api_integrations = models.JSONField(default=list)

    # Change Tracking
    files_changed = models.IntegerField(default=0)
    lines_added = models.IntegerField(default=0)
    lines_removed = models.IntegerField(default=0)

    class Meta:
        app_label = 'self_awareness'
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"CodebaseSnapshot({self.timestamp})"


class SelfAnalysisReport(models.Model):
    """Store results of automated self-analysis"""
    
    ANALYSIS_TYPES = [
        ('performance', 'Performance Analysis'),
        ('architecture', 'Architecture Analysis'),
        ('security', 'Security Analysis'),
        ('optimization', 'Optimization Analysis'),
        ('code_quality', 'Code Quality Analysis'),
        ('dependency', 'Dependency Analysis'),
    ]
    
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    analysis_type = models.CharField(max_length=50, choices=ANALYSIS_TYPES, db_index=True)
    
    # Analysis Results
    score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    findings = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    
    # Metadata
    execution_time = models.FloatField(default=0.0)  # seconds
    confidence = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    # Action Items
    critical_issues = models.IntegerField(default=0)
    warning_issues = models.IntegerField(default=0)
    info_issues = models.IntegerField(default=0)
    
    # Context
    codebase_snapshot = models.ForeignKey(CodebaseSnapshot, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        app_label = 'self_awareness'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['analysis_type', 'timestamp']),
            models.Index(fields=['score']),
        ]
        
    def __str__(self):
        return f"SelfAnalysisReport({self.analysis_type} - {self.score:.2f})"


class SystemEvolution(models.Model):
    """Track autonomous system improvements and evolution"""
    
    EVOLUTION_TYPES = [
        ('optimization', 'Performance Optimization'),
        ('feature', 'New Feature'),
        ('bugfix', 'Bug Fix'),
        ('refactor', 'Code Refactoring'),
        ('security', 'Security Enhancement'),
        ('dependency', 'Dependency Update'),
    ]
    
    STATUS_CHOICES = [
        ('proposed', 'Proposed'),
        ('analyzing', 'Analyzing'),
        ('testing', 'Testing'),
        ('implementing', 'Implementing'),
        ('deployed', 'Deployed'),
        ('monitoring', 'Monitoring'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('reverted', 'Reverted'),
    ]
    
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    evolution_type = models.CharField(max_length=50, choices=EVOLUTION_TYPES, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='proposed', db_index=True)
    
    # Evolution Details
    title = models.CharField(max_length=200)
    description = models.TextField()
    rationale = models.TextField()
    
    # Technical Details
    affected_files = models.JSONField(default=list)
    code_changes = models.JSONField(default=dict)
    test_results = models.JSONField(default=dict)
    
    # Impact Assessment
    expected_benefit = models.TextField()
    risk_assessment = models.TextField()
    rollback_plan = models.TextField()
    
    # Metrics
    confidence_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    priority = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    # Execution
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    execution_logs = models.JSONField(default=list)
    
    # Results
    success_metrics = models.JSONField(default=dict)
    performance_impact = models.JSONField(default=dict)
    
    class Meta:
        app_label = 'self_awareness'
        ordering = ['-priority', '-timestamp']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['evolution_type', 'timestamp']),
        ]
        
    def __str__(self):
        return f"SystemEvolution({self.title} - {self.status})"


class CodeEmbedding(models.Model):
    """Store vector embeddings of code for semantic search and analysis"""
    
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    
    # File Information
    file_path = models.CharField(max_length=500, db_index=True)
    file_type = models.CharField(max_length=20)
    function_name = models.CharField(max_length=200, blank=True)
    class_name = models.CharField(max_length=200, blank=True)
    
    # Code Content
    code_snippet = models.TextField()
    code_hash = models.CharField(max_length=64, db_index=True)  # SHA-256
    
    # Embedding Data
    embedding_vector = models.JSONField()  # Store as JSON array
    embedding_model = models.CharField(max_length=100, default='text-embedding-3-small')
    
    # Metadata
    tokens = models.IntegerField(default=0)
    complexity_score = models.FloatField(default=0.0)
    importance_score = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    # Relationships
    dependencies = models.JSONField(default=list)
    imports = models.JSONField(default=list)
    
    class Meta:
        app_label = 'self_awareness'
        unique_together = ['file_path', 'code_hash']
        ordering = ['-importance_score', '-timestamp']
        indexes = [
            models.Index(fields=['file_path']),
            models.Index(fields=['code_hash']),
            models.Index(fields=['importance_score']),
        ]
        
    def __str__(self):
        return f"CodeEmbedding({self.file_path}:{self.function_name or self.class_name or 'module'})"


class SelfHealingAction(models.Model):
    """Track self-healing actions and their effectiveness"""
    
    ACTION_TYPES = [
        ('restart_service', 'Restart Service'),
        ('clear_cache', 'Clear Cache'),
        ('optimize_database', 'Optimize Database'),
        ('fix_memory_leak', 'Fix Memory Leak'),
        ('update_config', 'Update Configuration'),
        ('rollback_change', 'Rollback Change'),
        ('scale_resources', 'Scale Resources'),
    ]
    
    STATUS_CHOICES = [
        ('detected', 'Issue Detected'),
        ('analyzing', 'Analyzing Issue'),
        ('planning', 'Planning Action'),
        ('executing', 'Executing Action'),
        ('verifying', 'Verifying Fix'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='detected', db_index=True)
    
    # Issue Information
    issue_description = models.TextField()
    issue_severity = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], default='medium')
    
    # Detection
    detected_by = models.CharField(max_length=100)  # Monitor, user report, etc.
    detection_confidence = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    # Action Details
    action_plan = models.JSONField(default=dict)
    action_logs = models.JSONField(default=list)
    
    # Results
    success = models.BooleanField(null=True)
    effectiveness_score = models.FloatField(null=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    resolution_time = models.FloatField(null=True)  # seconds
    
    # Metrics Before/After
    metrics_before = models.JSONField(default=dict)
    metrics_after = models.JSONField(default=dict)
    
    class Meta:
        app_label = 'self_awareness'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['status', 'issue_severity']),
            models.Index(fields=['action_type', 'success']),
        ]
        
    def __str__(self):
        return f"SelfHealingAction({self.action_type} - {self.status})"
