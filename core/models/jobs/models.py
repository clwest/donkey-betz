"""
Job and career-related models
"""

from django.db import models
from django.contrib.auth import get_user_model
from ..base.models import UnifiedBaseModel


class JobApplication(UnifiedBaseModel):
    """
    Track all job applications made through the platform.

    This model stores comprehensive information about each job application,
    including status tracking, employer responses, and success metrics.
    """
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('viewed', 'Application Viewed'),
        ('screening', 'Initial Screening'),
        ('phone_interview', 'Phone Interview'),
        ('technical_interview', 'Technical Interview'),
        ('final_interview', 'Final Interview'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('offer_declined', 'Offer Declined'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]

    APPLICATION_METHODS = [
        ('quick_apply', 'Quick Apply (AI-Generated)'),
        ('manual', 'Manual Application'),
        ('agent_automated', 'Agent Automated'),
        ('bulk_apply', 'Bulk Application'),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    # Job Information
    job_id = models.CharField(max_length=200, help_text="External job posting ID")
    platform = models.CharField(max_length=50, help_text="Job platform (LinkedIn, Indeed, etc.)")
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    job_url = models.URLField(blank=True)

    # Application Details
    applied_date = models.DateTimeField(auto_now_add=True)
    application_method = models.CharField(
        max_length=20,
        choices=APPLICATION_METHODS,
        default='quick_apply'
    )
    resume_version = models.CharField(
        max_length=100,
        blank=True,
        help_text="Which resume version was used"
    )
    cover_letter_used = models.TextField(blank=True)

    # Status Tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='applied'
    )
    last_status_update = models.DateTimeField(auto_now=True)

    # Response Tracking
    employer_response = models.TextField(blank=True)
    interview_dates = models.JSONField(
        default=list,
        help_text="List of interview dates and types"
    )
    notes = models.TextField(blank=True)

    # Success Metrics
    response_time_days = models.IntegerField(
        null=True,
        blank=True,
        help_text="Days from application to first response"
    )
    match_score = models.FloatField(
        default=0.0,
        help_text="AI-calculated fit score (0-100)"
    )

    # Salary Information
    salary_offered = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    salary_negotiated = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    def calculate_response_time(self):
        """Calculate response time if we have employer response."""
        if self.employer_response and self.status != 'applied':
            delta = self.last_status_update - self.applied_date
            self.response_time_days = delta.days
            return self.response_time_days
        return None

    def update_status(self, new_status, **kwargs):
        """
        Update application status and trigger learning loops.

        LEARNING LOOP: When job application outcomes are determined,
        update agent learning for better future matching.
        """
        old_status = self.status
        self.status = new_status
        self.save()

        # Trigger learning on outcome determination
        if new_status in ['offer_received', 'offer_accepted']:
            self._create_success_learning()
        elif new_status == 'rejected':
            self._create_failure_learning()

    def _create_success_learning(self):
        """Create learning entries for successful applications"""
        from ..ai_learning.models import UserAgentLearning, UserEmbedding

        try:
            # Update agent learning
            learning, created = UserAgentLearning.objects.get_or_create(
                user=self.user,
                agent_name='JobMatcherAgent',
                learning_domain='opportunity_matching',
                defaults={
                    'learning_content': {},
                    'confidence_score': 0.5
                }
            )

            # Track successful companies
            if 'successful_companies' not in learning.learning_content:
                learning.learning_content['successful_companies'] = []
            learning.learning_content['successful_companies'].append(self.company)

            # Track successful industries/roles
            if 'successful_positions' not in learning.learning_content:
                learning.learning_content['successful_positions'] = []
            learning.learning_content['successful_positions'].append({
                'position': self.position,
                'company': self.company,
                'match_score': self.match_score,
                'platform': self.platform
            })

            # Record success
            learning.record_success()
            learning.save()

            # Create embedding for similarity search
            try:
                UserEmbedding.objects.create(
                    user=self.user,
                    content_type='successful_application',
                    content=f"{self.position} at {self.company}",
                    embedding_vector=[],  # Will be populated by embedding service
                    confidence_score=self.match_score,
                    metadata={
                        'job_id': self.job_id,
                        'platform': self.platform,
                        'status': self.status,
                        'application_date': self.applied_date.isoformat()
                    }
                )
            except Exception as e:
                import logging
                logging.warning(f"Failed to create embedding for successful application: {e}")

        except Exception as e:
            import logging
            logging.error(f"Failed to create success learning for job application: {e}")

    def _create_failure_learning(self):
        """Create learning entries for rejected applications"""
        from ..ai_learning.models import UserAgentLearning

        try:
            learning, created = UserAgentLearning.objects.get_or_create(
                user=self.user,
                agent_name='JobMatcherAgent',
                learning_domain='opportunity_matching',
                defaults={
                    'learning_content': {},
                    'confidence_score': 0.5
                }
            )

            # Track rejections to avoid similar opportunities
            if 'rejected_patterns' not in learning.learning_content:
                learning.learning_content['rejected_patterns'] = []

            learning.learning_content['rejected_patterns'].append({
                'position': self.position,
                'company': self.company,
                'match_score': self.match_score,
                'platform': self.platform
            })

            # Record failure (decreases confidence slightly)
            learning.record_failure()
            learning.save()

        except Exception as e:
            import logging
            logging.error(f"Failed to create failure learning for job application: {e}")

    def is_successful(self):
        """Check if application was successful."""
        return self.status in ['offer_received', 'offer_accepted']

    def is_in_progress(self):
        """Check if application is still in progress."""
        return self.status in [
            'applied', 'viewed', 'screening',
            'phone_interview', 'technical_interview', 'final_interview'
        ]

    class Meta:
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"
        ordering = ['-applied_date']
        indexes = [
            models.Index(fields=['user', '-applied_date']),
            models.Index(fields=['status', '-applied_date']),
            models.Index(fields=['platform', '-applied_date']),
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.position} at {self.company} ({self.status})"


class ResumeVersion(UnifiedBaseModel):
    """
    Store different versions of user resumes for different job types.

    Users can have multiple resume versions optimized for different industries,
    roles, or application strategies.
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    # Version Information
    version_name = models.CharField(
        max_length=100,
        help_text="Name for this resume version (e.g., 'Software Engineer', 'Data Scientist')"
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Whether this is the primary/default resume"
    )

    # File and Content
    resume_file = models.FileField(upload_to='resumes/versions/')
    resume_text = models.TextField(
        blank=True,
        help_text="Extracted text content of the resume"
    )

    # Optimization Data
    target_industries = models.JSONField(
        default=list,
        help_text="Industries this resume is optimized for"
    )
    target_roles = models.JSONField(
        default=list,
        help_text="Role types this resume is optimized for"
    )
    keywords = models.JSONField(
        default=list,
        help_text="Keywords included in this resume version"
    )

    # Usage Statistics
    times_used = models.IntegerField(default=0)
    success_rate = models.FloatField(
        default=0.0,
        help_text="Success rate when using this resume (0-100)"
    )

    def calculate_success_rate(self):
        """Calculate success rate based on applications using this resume."""
        applications = JobApplication.objects.filter(
            user=self.user,
            resume_version=self.version_name
        )

        if applications.count() == 0:
            return 0.0

        successful = applications.filter(
            status__in=['offer_received', 'offer_accepted']
        ).count()

        self.success_rate = (successful / applications.count()) * 100
        return self.success_rate

    def increment_usage(self):
        """Increment usage counter."""
        self.times_used += 1
        self.save(update_fields=['times_used'])

    class Meta:
        verbose_name = "Resume Version"
        verbose_name_plural = "Resume Versions"
        unique_together = ['user', 'version_name']
        ordering = ['-is_primary', '-updated_at']

    def __str__(self):
        primary = " (Primary)" if self.is_primary else ""
        return f"{self.user.username}: {self.version_name}{primary}"