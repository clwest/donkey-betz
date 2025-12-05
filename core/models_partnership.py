"""
Human-AI Partnership Models (Unified Project Model)

Session 324: UNIFIED PROJECT MODEL
This is now THE SINGLE project model for the entire platform.
Previously there were two models (CreativeProject and PartnershipProject).
CreativeProject has been deprecated and merged into this model.

History:
- Session Pre-38: Partnership layer for human-AI collaboration
- Session 324: Unified with CreativeProject - now the single project model

Architecture:
- PartnershipProject: THE unified project model for all projects
- CollaborativeContent: Tracks content created together
- Integrates with Opportunity model (additive only)
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import uuid
from datetime import timedelta

from .models.base.models import UnifiedBaseModel


class PartnershipProject(UnifiedBaseModel):
    """
    Tracks an actual human-AI partnership project (contract, gig, content creation)

    This is PROOF that human-AI partnership works!
    Shows exactly who did what, time saved, money earned through collaboration.

    Separate from learning loop - this is about execution tracking.
    """

    # Link to opportunity (additive - doesn't change Opportunity model yet)
    opportunity = models.ForeignKey(
        'core.Opportunity',
        on_delete=models.CASCADE,
        related_name='partnership_projects',
        null=True,  # Can exist without opportunity
        blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='partnership_projects'
    )

    # Project basics
    project_name = models.CharField(max_length=200)
    project_type = models.CharField(max_length=50, choices=[
        ('content_creation', 'Content Creation'),
        ('data_analysis', 'Data Analysis'),
        ('research', 'Research Project'),
        ('development', 'Software Development'),
        ('design', 'Design Work'),
        ('consulting', 'Consulting/Advisory'),
        ('writing', 'Writing/Copywriting'),
        ('marketing', 'Marketing Content'),
        ('technical_writing', 'Technical Documentation'),
        ('other', 'Other Partnership'),
    ])

    description = models.TextField(
        help_text="What are we building together?"
    )

    # Partnership workflow
    workflow_steps = models.JSONField(
        default=list,
        help_text="List of steps in collaboration: [{step, ai_role, human_role, status}]"
    )
    current_step = models.IntegerField(default=0)

    # CONTRIBUTION TRACKING (This is the key!)
    ai_contributions = models.JSONField(
        default=list,
        help_text="What AI did: [{agent, task, time_saved, output, timestamp}]"
    )
    human_contributions = models.JSONField(
        default=list,
        help_text="What human did: [{task, time_spent, value_added, timestamp}]"
    )

    # Time metrics
    ai_time_equivalent = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Hours of work AI did (if human did it)"
    )
    human_time_actual = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Actual hours human spent"
    )

    # Contribution percentages
    ai_contribution_percent = models.IntegerField(
        default=0,
        help_text="AI's % of total work (0-100)"
    )
    human_contribution_percent = models.IntegerField(
        default=100,
        help_text="Human's % of total work (0-100)"
    )

    # Quality & outcome
    deliverable_description = models.TextField(
        blank=True,
        help_text="Description of what was delivered"
    )
    deliverable_url = models.URLField(
        blank=True,
        help_text="Link to deliverable if applicable"
    )

    quality_score = models.IntegerField(
        default=0,
        help_text="0-100: Quality of output (self-assessed)"
    )
    client_satisfaction = models.IntegerField(
        null=True,
        blank=True,
        help_text="0-100: Client rating if available"
    )

    # Financial (THE PROOF)
    contract_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total contract value"
    )
    payment_received = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Actual payment received"
    )
    ai_value_contribution = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="$ value AI contributed (based on time saved)"
    )

    # Status
    status = models.CharField(max_length=20, choices=[
        ('planning', 'Planning'),
        ('in_progress', 'In Progress'),
        ('review', 'Under Review'),
        ('submitted', 'Delivered'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
        ('cancelled', 'Cancelled'),
    ], default='planning')

    # ==========================================================================
    # Session 324: Fields merged from CreativeProject for unified model
    # ==========================================================================

    # Project goal (from CreativeProject)
    goal = models.TextField(
        blank=True,
        help_text="What's the objective of this project?"
    )

    # Timeline (from CreativeProject)
    deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Project deadline"
    )

    # Organization (from CreativeProject)
    category = models.CharField(
        max_length=50,
        blank=True,
        help_text="Project category (e.g., 'Branding', 'Marketing', 'Research')"
    )

    colors = models.CharField(
        max_length=200,
        blank=True,
        help_text="Color palette for this project (e.g., 'navy blue, gold, white')"
    )

    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Project tags for organization"
    )

    # Workflow tracking (from CreativeProject)
    total_workflows = models.PositiveIntegerField(
        default=0,
        help_text="Total number of workflows in this project"
    )

    completed_workflows = models.PositiveIntegerField(
        default=0,
        help_text="Number of completed workflows"
    )

    # Collaboration flags (from CreativeProject)
    is_shared = models.BooleanField(
        default=False,
        help_text="Whether project is shared with others"
    )

    is_quick_starts = models.BooleanField(
        default=False,
        help_text="Special project for ad-hoc/spontaneous work"
    )

    # Rich metadata (from CreativeProject Session 293)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Rich metadata: research_sources, executive_recommendations, creative_direction, suggested_next_steps"
    )

    # ==========================================================================
    # End Session 324 merged fields
    # ==========================================================================

    # Learning (separate from core learning loop)
    what_worked = models.TextField(
        blank=True,
        help_text="What worked well in this partnership?"
    )
    what_to_improve = models.TextField(
        blank=True,
        help_text="What could be improved next time?"
    )
    lessons_learned = models.JSONField(
        default=dict,
        help_text="Key lessons for future partnerships"
    )

    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['-started_at']),
            models.Index(fields=['deadline']),  # Session 324
        ]

    def __str__(self):
        return f"{self.project_name} ({self.status})"

    # Session 324: Properties from CreativeProject
    @property
    def progress_percentage(self):
        """
        Calculate project completion percentage

        Session 324: Merged from CreativeProject
        - Workflow-based: If total_workflows > 0, use completed/total ratio
        - AI contribution-based: Use ai_contribution_percent as fallback
        """
        # Workflow-based progress
        if self.total_workflows > 0:
            return int((self.completed_workflows / self.total_workflows) * 100)

        # Fallback to AI contribution percent
        return self.ai_contribution_percent

    @property
    def is_overdue(self):
        """Check if project is past deadline"""
        if not self.deadline:
            return False
        return timezone.now() > self.deadline and self.status not in ['completed', 'archived']

    @property
    def name(self):
        """Alias for project_name for compatibility with CreativeProject references"""
        return self.project_name

    @name.setter
    def name(self, value):
        """Setter for name alias"""
        self.project_name = value

    def get_sequential_number(self):
        """
        Get sequential number for this project (per user, chronological)

        Session 324: Merged from CreativeProject for unified model
        Returns 1-based sequential number for easy referencing
        Example: "Project #5" instead of "Project d4f7b3c2-8a9e-4d1f..."
        """
        # Count how many projects this user has created BEFORE this one
        earlier_projects = PartnershipProject.objects.filter(
            user=self.user,
            created_at__lt=self.created_at
        ).count()

        # Sequential number is count + 1 (1-based indexing)
        return earlier_projects + 1

    def update_workflow_counts(self):
        """
        Update workflow counts from related ProjectWorkflow entries

        Session 324: Merged from CreativeProject for unified model
        """
        # This is a placeholder - will be connected when ProjectWorkflow is migrated
        pass

    def calculate_partnership_roi(self):
        """
        Calculate ROI of AI partnership

        Returns dict with all key metrics proving partnership value
        """
        if float(self.human_time_actual) == 0:
            return {
                'error': 'No human time tracked yet',
                'time_saved_hours': 0,
                'efficiency_multiplier': 0,
                'effective_hourly_rate': 0,
            }

        # Without AI: would've taken ai_time_equivalent + human_time_actual
        solo_hours = float(self.ai_time_equivalent) + float(self.human_time_actual)

        # With AI: only took human_time_actual
        partnership_hours = float(self.human_time_actual)

        time_saved = solo_hours - partnership_hours
        efficiency_multiplier = solo_hours / partnership_hours if partnership_hours > 0 else 0

        # Effective hourly rate
        effective_rate = float(self.payment_received) / partnership_hours if partnership_hours > 0 else 0

        # AI's contribution to earnings
        if solo_hours > 0:
            ai_earnings_contribution = float(self.payment_received) * (float(self.ai_time_equivalent) / solo_hours)
        else:
            ai_earnings_contribution = 0

        return {
            'time_saved_hours': round(time_saved, 2),
            'efficiency_multiplier': round(efficiency_multiplier, 2),
            'effective_hourly_rate': round(effective_rate, 2),
            'ai_contribution': f"{self.ai_contribution_percent}%",
            'human_contribution': f"{self.human_contribution_percent}%",
            'ai_earnings_contribution': round(ai_earnings_contribution, 2),
            'solo_hours_estimate': round(solo_hours, 2),
            'actual_hours': round(partnership_hours, 2),
            'roi_summary': (
                f"${self.payment_received:.2f} earned in {partnership_hours:.1f}h "
                f"(would've taken {solo_hours:.1f}h solo) = {efficiency_multiplier:.1f}x faster"
            )
        }

    def add_ai_contribution(self, agent_name, task, time_saved_hours, output_summary):
        """
        Track an AI contribution to the project

        Args:
            agent_name: Which agent did this
            task: What was done
            time_saved_hours: How many hours this saved
            output_summary: Brief description of output
        """
        contribution = {
            'agent': agent_name,
            'task': task,
            'time_saved': float(time_saved_hours),
            'output': output_summary,
            'timestamp': timezone.now().isoformat()
        }

        self.ai_contributions.append(contribution)
        self.ai_time_equivalent += Decimal(str(time_saved_hours))
        self.save()

        return contribution

    def add_human_contribution(self, task, time_spent_hours, value_added):
        """
        Track a human contribution to the project

        Args:
            task: What did human do
            time_spent_hours: How long it took
            value_added: What value did human add
        """
        contribution = {
            'task': task,
            'time_spent': float(time_spent_hours),
            'value_added': value_added,
            'timestamp': timezone.now().isoformat()
        }

        self.human_contributions.append(contribution)
        self.human_time_actual += Decimal(str(time_spent_hours))
        self.save()

        return contribution

    def update_contribution_percentages(self):
        """Recalculate AI vs Human contribution percentages"""
        total_time = float(self.ai_time_equivalent) + float(self.human_time_actual)

        if total_time > 0:
            self.ai_contribution_percent = int((float(self.ai_time_equivalent) / total_time) * 100)
            self.human_contribution_percent = int((float(self.human_time_actual) / total_time) * 100)
        else:
            self.ai_contribution_percent = 0
            self.human_contribution_percent = 100

        self.save()

    # ==========================================================================
    # Session 350: Domain-Aware Spider Targeting
    # ==========================================================================

    def extract_and_save_domains(self, use_gpt: bool = True) -> dict:
        """
        Extract domain information from project description and save to metadata.

        Uses DomainExtractionService to analyze the project and extract:
        - Primary domain (e.g., 'fitness_health', 'saas_b2b')
        - Domain tags for targeted spider queries
        - Suggested search queries
        - Relevant subreddits

        Args:
            use_gpt: Whether to use GPT for enhanced extraction (default True)

        Returns:
            Dict with domain information
        """
        from core.services.domain_extraction_service import get_domain_extraction_service

        service = get_domain_extraction_service()

        # Use project name + description + goal for extraction
        business_idea = f"{self.project_name}"
        if self.description:
            business_idea += f": {self.description}"
        if self.goal:
            business_idea += f". Goal: {self.goal}"

        result = service.extract_domains(business_idea, use_gpt=use_gpt)

        # Save to metadata
        if self.metadata is None:
            self.metadata = {}

        self.metadata['domain_targeting'] = {
            'primary_domain': result.primary_domain,
            'domain_tags': result.domain_tags,
            'spider_queries': result.spider_queries,
            'spider_categories': result.spider_categories,
            'subreddits': result.subreddits,
            'confidence': result.confidence,
            'reasoning': result.reasoning,
            'extracted_at': timezone.now().isoformat()
        }

        self.save()

        return self.metadata['domain_targeting']

    def get_domain_targeting(self) -> dict:
        """
        Get domain targeting info, extracting if not already present.

        Returns:
            Dict with domain targeting information
        """
        if self.metadata and 'domain_targeting' in self.metadata:
            return self.metadata['domain_targeting']

        # Extract if not present
        return self.extract_and_save_domains()

    @property
    def primary_domain(self) -> str:
        """Get the primary business domain for this project."""
        targeting = self.get_domain_targeting()
        return targeting.get('primary_domain', 'general_startup')

    @property
    def domain_tags(self) -> list:
        """Get domain tags for spider targeting."""
        targeting = self.get_domain_targeting()
        return targeting.get('domain_tags', [])

    @property
    def spider_queries(self) -> list:
        """Get suggested spider queries for this project's domain."""
        targeting = self.get_domain_targeting()
        return targeting.get('spider_queries', [])

    @property
    def domain_subreddits(self) -> list:
        """Get relevant subreddits for this project's domain."""
        targeting = self.get_domain_targeting()
        return targeting.get('subreddits', [])

    # ==========================================================================
    # End Session 350 Domain Targeting
    # ==========================================================================

    # ==========================================================================
    # Session 354: Project Learning Loop
    # Enable projects to autonomously learn and track their domain over time
    # ==========================================================================

    learning_enabled = models.BooleanField(
        default=False,
        help_text="Enable continuous learning for this project"
    )

    learning_topics = models.JSONField(
        default=list,
        blank=True,
        help_text="Topics to track: ['coffee trends', 'specialty drinks']"
    )

    learning_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('biweekly', 'Every 2 Weeks'),
            ('monthly', 'Monthly'),
        ],
        default='weekly',
        help_text="How often to run learning cycles"
    )

    last_learning_run = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the last learning cycle ran"
    )

    next_learning_run = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the next learning cycle should run"
    )

    learning_history = models.JSONField(
        default=list,
        blank=True,
        help_text="History of learning runs: [{date, findings_count, deltas}]"
    )

    # ==========================================================================
    # End Session 354 Learning Loop
    # ==========================================================================

    def mark_completed(self, payment_received):
        """
        Mark project as completed and track payment

        Args:
            payment_received: Amount paid
        """
        self.status = 'completed'
        self.payment_received = Decimal(str(payment_received))
        self.completed_at = timezone.now()

        # Calculate AI's value contribution
        total_time = float(self.ai_time_equivalent) + float(self.human_time_actual)
        if total_time > 0:
            ai_percentage = float(self.ai_time_equivalent) / total_time
            self.ai_value_contribution = self.payment_received * Decimal(str(ai_percentage))

        self.save()

    def __str__(self):
        return f"{self.project_name} - {self.ai_contribution_percent}% AI / {self.human_contribution_percent}% Human"


class CollaborativeContent(UnifiedBaseModel):
    """
    Tracks content created through human-AI collaboration
    Shows WHO did WHAT in the creation process

    This is separate from learning loop - focused on execution tracking.
    """

    partnership_project = models.ForeignKey(
        PartnershipProject,
        on_delete=models.CASCADE,
        related_name='content_pieces'
    )

    # Content basics
    content_type = models.CharField(max_length=50, choices=[
        ('blog_post', 'Blog Post'),
        ('article', 'Article'),
        ('social_media', 'Social Media Post'),
        ('email', 'Email'),
        ('documentation', 'Documentation'),
        ('marketing_copy', 'Marketing Copy'),
        ('technical_writing', 'Technical Writing'),
        ('product_description', 'Product Description'),
        ('landing_page', 'Landing Page Copy'),
        ('video_script', 'Video Script'),
        ('other', 'Other Content'),
    ])
    title = models.CharField(max_length=300)

    # Collaboration trail (THIS IS THE PROOF!)
    ai_first_draft = models.TextField(
        help_text="What AI generated initially"
    )
    ai_agents_used = models.JSONField(
        default=list,
        help_text="Which agents contributed: ['ContentGenerator', 'SEOOptimizer']"
    )
    ai_generation_time = models.DurationField(
        default=timedelta(seconds=0),
        help_text="How long AI took"
    )

    human_edits = models.JSONField(
        default=list,
        help_text="What human changed: [{timestamp, section, change, reason}]"
    )
    human_additions = models.JSONField(
        default=list,
        help_text="What human added: [{section, content, value}]"
    )
    human_time_spent = models.DurationField(
        default=timedelta(seconds=0),
        help_text="Total time human spent"
    )

    final_content = models.TextField(
        blank=True,
        help_text="The delivered version"
    )

    # Quality metrics
    word_count = models.IntegerField(default=0)
    seo_score = models.IntegerField(
        null=True,
        blank=True,
        help_text="0-100 SEO quality score"
    )
    readability_score = models.IntegerField(
        null=True,
        blank=True,
        help_text="0-100 readability score"
    )

    # Contribution breakdown
    ai_generated_words = models.IntegerField(
        default=0,
        help_text="Words in AI draft"
    )
    human_written_words = models.IntegerField(
        default=0,
        help_text="Words human added"
    )
    ai_contribution_percent = models.IntegerField(
        default=0,
        help_text="% of final content from AI"
    )

    # Client feedback
    accepted = models.BooleanField(default=False)
    client_feedback = models.TextField(blank=True)
    revision_count = models.IntegerField(
        default=0,
        help_text="Number of revision rounds"
    )

    # Status
    status = models.CharField(max_length=20, choices=[
        ('drafting', 'AI Drafting'),
        ('editing', 'Human Editing'),
        ('review', 'Final Review'),
        ('delivered', 'Delivered'),
        ('accepted', 'Accepted by Client'),
        ('revision', 'Needs Revision'),
    ], default='drafting')

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']
        verbose_name_plural = 'Collaborative Content Pieces'

    def calculate_collaboration_metrics(self):
        """
        Analyze the human-AI collaboration

        Returns dict showing partnership breakdown
        """
        # Estimate what it would take solo
        words_per_hour = 500  # Average writing speed
        solo_hours_estimate = self.word_count / words_per_hour if self.word_count > 0 else 0

        actual_hours = self.human_time_spent.total_seconds() / 3600

        if actual_hours > 0:
            efficiency = solo_hours_estimate / actual_hours
            time_saved = solo_hours_estimate - actual_hours
        else:
            efficiency = 0
            time_saved = 0

        return {
            'ai_wrote': f"{self.ai_generated_words} words",
            'human_wrote': f"{self.human_written_words} words",
            'total_words': self.word_count,
            'ai_percent': f"{self.ai_contribution_percent}%",
            'human_percent': f"{100 - self.ai_contribution_percent}%",
            'time_saved': f"{time_saved:.1f} hours",
            'efficiency': f"{efficiency:.1f}x faster" if efficiency > 0 else "N/A",
            'solo_estimate': f"{solo_hours_estimate:.1f} hours",
            'actual_time': f"{actual_hours:.1f} hours",
            'partnership_summary': (
                f"AI drafted {self.ai_contribution_percent}%, "
                f"human refined {100 - self.ai_contribution_percent}%, "
                f"delivered in {actual_hours:.1f}h vs {solo_hours_estimate:.1f}h solo"
            )
        }

    def add_human_edit(self, section, change_description, reason):
        """Track a human edit to the content"""
        edit = {
            'timestamp': timezone.now().isoformat(),
            'section': section,
            'change': change_description,
            'reason': reason
        }
        self.human_edits.append(edit)
        self.save()
        return edit

    def add_human_addition(self, section, content, value_explanation):
        """Track content human added"""
        addition = {
            'timestamp': timezone.now().isoformat(),
            'section': section,
            'content': content[:200],  # Store preview
            'value': value_explanation,
            'word_count': len(content.split())
        }
        self.human_additions.append(addition)
        self.human_written_words += len(content.split())
        self.save()
        return addition

    def finalize_content(self, final_text):
        """
        Finalize the content and calculate contribution percentages

        Args:
            final_text: The final delivered content
        """
        self.final_content = final_text
        self.word_count = len(final_text.split())
        self.status = 'delivered'

        # Calculate contribution percentages
        total_words = self.ai_generated_words + self.human_written_words
        if total_words > 0:
            self.ai_contribution_percent = int((self.ai_generated_words / total_words) * 100)

        self.save()

    def __str__(self):
        return f"{self.title} ({self.content_type}) - {self.ai_contribution_percent}% AI"
