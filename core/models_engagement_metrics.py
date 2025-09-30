"""
Engagement Metrics and A/B Testing Models
==========================================
Track user engagement and measure personalization impact
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid


class EngagementMetrics(models.Model):
    """
    Track user engagement metrics for measuring personalization effectiveness
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='engagement_metrics')

    # Session info
    session_id = models.CharField(max_length=100, db_index=True)
    session_start = models.DateTimeField(auto_now_add=True)
    session_end = models.DateTimeField(null=True, blank=True)

    # Page metrics
    page_views = models.IntegerField(default=0)
    time_on_page = models.IntegerField(default=0, help_text='Time in seconds')

    # Opportunity interaction metrics
    opportunities_shown = models.IntegerField(default=0)
    opportunities_clicked = models.IntegerField(default=0)
    opportunities_applied = models.IntegerField(default=0)

    # Click-through rate (CTR) - calculated
    ctr = models.FloatField(default=0.0, help_text='Click-through rate')
    application_rate = models.FloatField(default=0.0, help_text='Application rate from clicks')

    # Personalization metrics
    personalized_results = models.BooleanField(default=False)
    personalization_boost_applied = models.FloatField(default=0.0)

    # A/B Testing
    ab_test_group = models.CharField(
        max_length=20,
        choices=[
            ('control', 'Control (No Personalization)'),
            ('treatment', 'Treatment (With Personalization)'),
        ],
        null=True,
        blank=True
    )

    # Revenue tracking
    potential_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['ab_test_group', '-created_at']),
            models.Index(fields=['personalized_results', '-created_at']),
        ]

    def calculate_metrics(self):
        """Calculate CTR and application rate"""
        if self.opportunities_shown > 0:
            self.ctr = self.opportunities_clicked / self.opportunities_shown
        else:
            self.ctr = 0.0

        if self.opportunities_clicked > 0:
            self.application_rate = self.opportunities_applied / self.opportunities_clicked
        else:
            self.application_rate = 0.0

        self.save()

    def end_session(self):
        """Mark session as ended"""
        self.session_end = timezone.now()
        self.calculate_metrics()

    @classmethod
    def get_user_engagement_summary(cls, user, days=30):
        """Get engagement summary for user over specified period"""
        start_date = timezone.now() - timedelta(days=days)

        metrics = cls.objects.filter(
            user=user,
            created_at__gte=start_date
        )

        if not metrics.exists():
            return None

        from django.db.models import Sum, Avg, Count

        summary = metrics.aggregate(
            total_sessions=Count('id'),
            total_opportunities_shown=Sum('opportunities_shown'),
            total_clicks=Sum('opportunities_clicked'),
            total_applications=Sum('opportunities_applied'),
            avg_ctr=Avg('ctr'),
            avg_application_rate=Avg('application_rate'),
            total_potential_revenue=Sum('potential_revenue')
        )

        return summary

    @classmethod
    def compare_ab_groups(cls, days=30):
        """Compare control vs treatment groups"""
        start_date = timezone.now() - timedelta(days=days)

        from django.db.models import Avg, Sum, Count

        control = cls.objects.filter(
            ab_test_group='control',
            created_at__gte=start_date
        ).aggregate(
            users=Count('user', distinct=True),
            avg_ctr=Avg('ctr'),
            avg_app_rate=Avg('application_rate'),
            total_revenue=Sum('potential_revenue')
        )

        treatment = cls.objects.filter(
            ab_test_group='treatment',
            created_at__gte=start_date
        ).aggregate(
            users=Count('user', distinct=True),
            avg_ctr=Avg('ctr'),
            avg_app_rate=Avg('application_rate'),
            total_revenue=Sum('potential_revenue')
        )

        # Calculate improvement
        improvement = {}
        if control['avg_ctr'] and treatment['avg_ctr']:
            improvement['ctr'] = ((treatment['avg_ctr'] - control['avg_ctr']) / control['avg_ctr']) * 100

        if control['avg_app_rate'] and treatment['avg_app_rate']:
            improvement['app_rate'] = ((treatment['avg_app_rate'] - control['avg_app_rate']) / control['avg_app_rate']) * 100

        if control['total_revenue'] and treatment['total_revenue']:
            improvement['revenue'] = ((treatment['total_revenue'] - control['total_revenue']) / control['total_revenue']) * 100

        return {
            'control': control,
            'treatment': treatment,
            'improvement': improvement
        }

    def __str__(self):
        return f"{self.user.username} - {self.session_id} - CTR: {self.ctr:.2%}"


class OpportunityInteraction(models.Model):
    """
    Track individual opportunity interactions for detailed analytics
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='opportunity_interactions')
    engagement_session = models.ForeignKey(EngagementMetrics, on_delete=models.CASCADE, related_name='interactions', null=True)

    # Opportunity details
    opportunity_id = models.CharField(max_length=200)
    opportunity_title = models.CharField(max_length=500)
    opportunity_platform = models.CharField(max_length=100)
    opportunity_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    # Interaction type
    interaction_type = models.CharField(
        max_length=20,
        choices=[
            ('view', 'Viewed'),
            ('click', 'Clicked'),
            ('apply', 'Applied'),
            ('reject', 'Rejected'),
        ]
    )

    # Personalization context
    was_personalized = models.BooleanField(default=False)
    personalization_boost = models.FloatField(default=0.0)
    match_score = models.IntegerField(default=0)

    # Timing
    interaction_timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    time_to_interact = models.IntegerField(default=0, help_text='Seconds from view to interaction')

    # Outcome
    resulted_in_application = models.BooleanField(default=False)
    application_success = models.BooleanField(null=True, blank=True)

    class Meta:
        ordering = ['-interaction_timestamp']
        indexes = [
            models.Index(fields=['user', '-interaction_timestamp']),
            models.Index(fields=['opportunity_platform', '-interaction_timestamp']),
            models.Index(fields=['interaction_type', '-interaction_timestamp']),
        ]

    @classmethod
    def get_platform_performance(cls, user, days=30):
        """Analyze which platforms user engages with most"""
        start_date = timezone.now() - timedelta(days=days)

        from django.db.models import Count, Avg

        platform_stats = cls.objects.filter(
            user=user,
            interaction_timestamp__gte=start_date
        ).values('opportunity_platform').annotate(
            total_interactions=Count('id'),
            clicks=Count('id', filter=models.Q(interaction_type='click')),
            applications=Count('id', filter=models.Q(interaction_type='apply')),
            avg_match_score=Avg('match_score')
        ).order_by('-total_interactions')

        return list(platform_stats)

    def __str__(self):
        return f"{self.user.username} - {self.interaction_type} - {self.opportunity_title[:50]}"
