"""
Session 862: Research Result Model

Tracks research conducted for Initiative Stage 1 (Research Brief).
Links spider data, search queries, and findings to initiatives.

This model bridges the gap between raw spider data and structured
research briefs that feed into the Initiative pipeline.
"""

import uuid
from django.db import models
from django.utils import timezone


class ResearchResult(models.Model):
    """
    Research conducted for an Initiative's Research Brief stage.

    Captures:
    - What was researched (topic, queries)
    - Sources used (spider data, web searches)
    - Findings and analysis
    - Link to resulting document

    Example flow:
        1. Dream is approved -> Initiative created
        2. ResearchAgent conducts research for Stage 1
        3. ResearchResult stores findings + spider sources
        4. create_research_brief() generates SelfBlog document
        5. Stage 1 links to the research brief document
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Initiative link
    # Session 905 fix: Allow null for blocked research that can't link to initiative yet
    initiative = models.ForeignKey(
        'core.Initiative',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='research_results',
        help_text='Initiative this research supports'
    )

    initiative_stage = models.ForeignKey(
        'core.InitiativeStage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='research_results',
        help_text='Stage 1 (Research Brief) this research fulfills'
    )

    # Research metadata
    topic = models.CharField(
        max_length=500,
        help_text='Research topic/question'
    )

    RESEARCH_TYPE_CHOICES = [
        ('market_analysis', 'Market Analysis'),
        ('competitor_research', 'Competitor Research'),
        ('technical_research', 'Technical Research'),
        ('user_research', 'User Research'),
        ('trend_analysis', 'Trend Analysis'),
        ('feasibility_study', 'Feasibility Study'),
        ('literature_review', 'Literature Review'),
        ('data_analysis', 'Data Analysis'),
    ]
    research_type = models.CharField(
        max_length=50,
        choices=RESEARCH_TYPE_CHOICES,
        default='market_analysis'
    )

    # Research inputs
    queries = models.JSONField(
        default=list,
        help_text='Search queries used during research'
    )

    spider_sources = models.ManyToManyField(
        'core.SpiderData',
        blank=True,
        related_name='research_results',
        help_text='Spider data used in this research'
    )

    external_sources = models.JSONField(
        default=list,
        help_text='External URLs and sources consulted: [{url, title, snippet}]'
    )

    # Research outputs
    findings = models.JSONField(
        default=dict,
        help_text='Structured research findings: {category: findings_text}'
    )

    summary = models.TextField(
        blank=True,
        help_text='Executive summary of research'
    )

    recommendations = models.JSONField(
        default=list,
        help_text='Recommendations based on research'
    )

    confidence_score = models.FloatField(
        default=0.0,
        help_text='Confidence in research findings (0-1)'
    )

    # Resulting document
    self_blog = models.ForeignKey(
        'core.SelfBlog',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='research_results',
        help_text='Research Brief document created from this research'
    )

    # Agent tracking
    conducted_by = models.CharField(
        max_length=100,
        default='ResearchAgent',
        help_text='Agent that conducted the research'
    )

    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('complete', 'Complete'),
        ('failed', 'Failed'),
        ('blocked', 'Blocked - Awaiting Data'),  # Session 905: Insufficient data
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Session 905: Data sufficiency tracking for self-unblock loop
    data_sufficient = models.BooleanField(
        default=True,
        help_text='Whether research has sufficient data to proceed'
    )
    blocked_reason = models.TextField(
        blank=True,
        help_text='Reason research is blocked (e.g., "Insufficient spider data")'
    )
    retry_count = models.IntegerField(
        default=0,
        help_text='Number of times research has been retried'
    )
    max_retries = models.IntegerField(
        default=3,
        help_text='Maximum retry attempts before escalation'
    )
    retry_after = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When to retry blocked research'
    )
    unblock_trigger = models.CharField(
        max_length=100,
        blank=True,
        help_text='What should trigger unblocking (e.g., "spider_data_arrival")'
    )

    # Timestamps
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        db_table = 'core_research_result'
        ordering = ['-created_at']
        verbose_name = 'Research Result'
        verbose_name_plural = 'Research Results'
        indexes = [
            models.Index(fields=['initiative', 'research_type']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['completed_at']),
        ]

    def __str__(self):
        return f"Research: {self.topic[:50]} for {self.initiative.name}"

    def mark_in_progress(self):
        """Mark research as in progress."""
        self.status = 'in_progress'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])

    def mark_complete(self, findings=None, summary=None, confidence=None):
        """Mark research as complete with findings."""
        if findings:
            self.findings = findings
        if summary:
            self.summary = summary
        if confidence is not None:
            self.confidence_score = confidence
        self.status = 'complete'
        self.completed_at = timezone.now()
        self.save()

    def mark_failed(self, error_message=''):
        """Mark research as failed."""
        self.status = 'failed'
        self.findings = {'error': error_message}
        self.save(update_fields=['status', 'findings'])

    def mark_blocked(self, reason='Insufficient data', retry_minutes=30):
        """
        Session 905: Mark research as blocked awaiting data.

        Args:
            reason: Why research is blocked
            retry_minutes: How long to wait before retry (default 30)
        """
        from datetime import timedelta

        self.status = 'blocked'
        self.data_sufficient = False
        self.blocked_reason = reason
        self.retry_after = timezone.now() + timedelta(minutes=retry_minutes)
        self.unblock_trigger = 'spider_data_arrival'
        self.save(update_fields=[
            'status', 'data_sufficient', 'blocked_reason',
            'retry_after', 'unblock_trigger', 'updated_at'
        ])

        # Update the associated InitiativeStage to BLOCKED
        if self.initiative_stage:
            self.initiative_stage.status = 'BLOCKED'
            self.initiative_stage.notes = f"Blocked: {reason}. Retry scheduled."
            self.initiative_stage.save(update_fields=['status', 'notes', 'updated_at'])

    def can_retry(self):
        """Check if research can be retried."""
        if self.status != 'blocked':
            return False
        if self.retry_count >= self.max_retries:
            return False
        if self.retry_after and timezone.now() < self.retry_after:
            return False
        return True

    def schedule_retry(self):
        """
        Session 905: Schedule a Celery task to retry this blocked research.

        Returns:
            task_id or None
        """
        if not self.can_retry():
            return None

        from core.tasks import retry_blocked_research
        from django.conf import settings

        # Calculate eta for retry
        eta = self.retry_after or timezone.now()

        # Schedule the retry task
        task = retry_blocked_research.apply_async(
            args=[str(self.id)],
            eta=eta
        )

        return task.id if task else None

    def create_research_brief(self):
        """
        Create a SelfBlog (Research Brief) from this research.
        Links it to the Initiative Stage 1.

        Returns:
            SelfBlog: The created research brief document
        """
        from core.models_unified_system import SelfBlog

        # Create the research brief document
        blog = SelfBlog.objects.create(
            title=f"Research Brief: {self.topic}",
            intro=self.summary or f"Research findings for {self.initiative.name}",
            full_text=self._format_findings_as_markdown(),
            category='research_brief',
            status='draft',
            initiative=self.initiative,
            initiative_stage=self.initiative_stage,
            tags=['research', 'brief', self.research_type],
        )

        # Link to this research
        self.self_blog = blog
        self.save(update_fields=['self_blog'])

        # Link to initiative stage document
        if self.initiative_stage:
            self.initiative_stage.document = blog
            self.initiative_stage.status = 'DRAFT'
            self.initiative_stage.save(update_fields=['document', 'status'])

        return blog

    def _format_findings_as_markdown(self):
        """Format findings as markdown document."""
        md = f"# Research Brief: {self.topic}\n\n"
        md += f"## Executive Summary\n\n{self.summary}\n\n"

        md += "## Research Methodology\n\n"
        md += f"- **Type:** {self.get_research_type_display()}\n"
        md += f"- **Conducted by:** {self.conducted_by}\n"
        md += f"- **Confidence Score:** {self.confidence_score:.0%}\n\n"

        if self.queries:
            md += "### Search Queries\n\n"
            for q in self.queries:
                md += f"- {q}\n"
            md += "\n"

        if self.external_sources:
            md += "### Sources Consulted\n\n"
            for source in self.external_sources:
                if isinstance(source, dict):
                    md += f"- [{source.get('title', 'Source')}]({source.get('url', '#')})\n"
                else:
                    md += f"- {source}\n"
            md += "\n"

        md += "## Findings\n\n"
        if isinstance(self.findings, dict) and 'error' not in self.findings:
            for key, value in self.findings.items():
                md += f"### {key}\n\n{value}\n\n"
        elif isinstance(self.findings, dict) and 'error' in self.findings:
            md += f"*Research failed: {self.findings['error']}*\n\n"
        else:
            md += str(self.findings) + "\n\n"

        if self.recommendations:
            md += "## Recommendations\n\n"
            for i, rec in enumerate(self.recommendations, 1):
                md += f"{i}. {rec}\n"
            md += "\n"

        md += "---\n\n"
        md += f"*Generated from Initiative: {self.initiative.name}*\n"

        return md

    @classmethod
    def create_for_initiative(cls, initiative, topic=None, research_type='market_analysis'):
        """
        Factory method to create research for an initiative's Stage 1.

        Args:
            initiative: The Initiative this research supports
            topic: Research topic (defaults to initiative name)
            research_type: Type of research to conduct

        Returns:
            ResearchResult: New research result instance
        """
        from core.models_document_registry import InitiativeStage

        # Get or create Stage 1
        stage, _ = InitiativeStage.objects.get_or_create(
            initiative=initiative,
            stage=1,
            defaults={'status': 'PENDING'}
        )

        return cls.objects.create(
            initiative=initiative,
            initiative_stage=stage,
            topic=topic or initiative.name,
            research_type=research_type,
            status='pending'
        )
