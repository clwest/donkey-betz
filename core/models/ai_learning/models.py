"""
AI Learning and agent collaboration models
"""

from django.db import models
from ..system.models import ErrorPattern


class AgentLearningSession(models.Model):
    """Track agent learning sessions and improvements over time"""

    session_id = models.CharField(max_length=100, unique=True)
    agent_type = models.CharField(max_length=50)  # 'AgentErrorHandler', 'GPT4oMini', etc.

    # Session statistics
    total_errors_encountered = models.IntegerField(default=0)
    total_errors_fixed = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0.0)
    average_resolution_time = models.FloatField(default=0.0)

    # Learning metrics
    new_patterns_learned = models.IntegerField(default=0)
    patterns_improved = models.IntegerField(default=0)
    knowledge_base_size_before = models.IntegerField(default=0)
    knowledge_base_size_after = models.IntegerField(default=0)

    # Session metadata
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    session_duration_minutes = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-started_at']
        verbose_name = "Agent Learning Session"
        verbose_name_plural = "Agent Learning Sessions"

    def __str__(self):
        return f"{self.agent_type} - {self.session_id} ({self.success_rate:.1%})"


class AgentCollaboration(models.Model):
    """Track how different agents collaborate and learn from each other"""

    primary_agent = models.CharField(max_length=50)
    assisting_agent = models.CharField(max_length=50)
    collaboration_type = models.CharField(max_length=50)  # 'fallback', 'consultation', 'parallel'

    # Problem context
    problem_domain = models.CharField(max_length=100)  # 'code_generation', 'error_fixing', 'optimization'
    problem_complexity = models.CharField(max_length=20)  # 'simple', 'moderate', 'complex'

    # Outcome
    collaboration_successful = models.BooleanField(default=False)
    primary_agent_contribution = models.TextField(blank=True)
    assisting_agent_contribution = models.TextField(blank=True)
    final_solution = models.TextField()

    # Learning transfer
    knowledge_transferred = models.TextField(blank=True)  # What the primary agent learned
    pattern_reinforced = models.ForeignKey(ErrorPattern, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Agent Collaboration"
        verbose_name_plural = "Agent Collaborations"

    def __str__(self):
        return f"{self.primary_agent} + {self.assisting_agent}: {self.problem_domain}"


class LearningInsight(models.Model):
    """Store insights and patterns discovered by the AI system"""

    insight_type = models.CharField(max_length=50)  # 'error_pattern', 'code_pattern', 'project_pattern'
    insight_category = models.CharField(max_length=100)  # 'common_mistakes', 'best_practices', 'optimization'

    # Insight content
    title = models.CharField(max_length=200)
    description = models.TextField()
    code_example = models.TextField(blank=True)
    solution_approach = models.TextField()

    # Evidence and confidence
    supporting_instances = models.IntegerField(default=1)  # How many times this was observed
    confidence_level = models.FloatField(default=0.5)
    applicability_scope = models.JSONField(default=dict)  # Where this insight applies

    # Impact tracking
    times_applied = models.IntegerField(default=0)
    success_when_applied = models.IntegerField(default=0)
    impact_score = models.FloatField(default=0.0)

    discovered_at = models.DateTimeField(auto_now_add=True)
    last_validated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-confidence_level', '-impact_score']
        verbose_name = "Learning Insight"
        verbose_name_plural = "Learning Insights"

    def __str__(self):
        return f"{self.insight_category}: {self.title} ({self.confidence_level:.1%})"