"""Models for AI Opportunities.

GeneratedProject / ProjectFile / ProjectDeployment removed in Session 1244
(Cat 2 dormant cleanup batch). Reason: 0 rows + 0 importers across the
entire codebase; the canonical `core.GeneratedProject` model (registered
at `core.models.projects.models`, used by 13+ files) is the actual
generated-project model. The ai_opportunities variants were never
exercised. Audit deliverable `86870fdd-…` Finding 2.3.
"""
from django.db import models


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


# GeneratedProject / ProjectFile / ProjectDeployment removed in S1244 — see module docstring.