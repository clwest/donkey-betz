"""
Extended User Profile Model for AI Income Platform
Stores user skills, preferences, and goals for personalization
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class ExtendedUserProfile(models.Model):
    """
    Extended profile to store user's professional information,
    skills, and preferences for AI-driven income opportunities
    """

    # Link to Django User
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='extended_profile'
    )

    # Professional Information
    full_name = models.CharField(max_length=255, blank=True)
    professional_title = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True, help_text="Professional biography")

    # Skills and Experience
    skills = models.JSONField(
        default=list,
        help_text="List of professional skills"
    )
    experience_years = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(50)]
    )
    education_level = models.CharField(
        max_length=50,
        choices=[
            ('high_school', 'High School'),
            ('associate', 'Associate Degree'),
            ('bachelor', 'Bachelor\'s Degree'),
            ('master', 'Master\'s Degree'),
            ('phd', 'PhD/Doctorate'),
            ('other', 'Other'),
        ],
        blank=True
    )
    certifications = models.JSONField(
        default=list,
        help_text="Professional certifications"
    )

    # Income Goals
    target_income = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Monthly income goal in USD"
    )
    minimum_hourly_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum acceptable hourly rate"
    )

    # Work Preferences
    AVAILABILITY_CHOICES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('freelance', 'Freelance'),
        ('contract', 'Contract'),
        ('flexible', 'Flexible'),
    ]
    availability = models.CharField(
        max_length=50,
        choices=AVAILABILITY_CHOICES,
        default='flexible'
    )

    hours_per_week = models.IntegerField(
        default=40,
        validators=[MinValueValidator(1), MaxValueValidator(168)]
    )

    # Location
    location = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(max_length=50, blank=True)
    remote_only = models.BooleanField(default=False)

    # Job Categories
    preferred_categories = models.JSONField(
        default=list,
        help_text="Preferred job categories"
    )
    avoided_categories = models.JSONField(
        default=list,
        help_text="Categories to avoid"
    )

    # Industry Preferences
    preferred_industries = models.JSONField(
        default=list,
        help_text="Preferred industries"
    )

    # AI Personalization
    ai_suggestions_enabled = models.BooleanField(default=True)
    auto_apply_enabled = models.BooleanField(default=False)
    risk_tolerance = models.CharField(
        max_length=20,
        choices=[
            ('conservative', 'Conservative'),
            ('moderate', 'Moderate'),
            ('aggressive', 'Aggressive'),
        ],
        default='moderate'
    )

    # Resume and Portfolio
    resume_text = models.TextField(blank=True)
    portfolio_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)

    # Application History
    total_applications = models.IntegerField(default=0)
    successful_applications = models.IntegerField(default=0)
    total_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    # Sports Betting Preferences (for Sports AI)
    sports_betting_enabled = models.BooleanField(default=False)
    betting_bankroll = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    favorite_sports = models.JSONField(
        default=list,
        help_text="Preferred sports for betting"
    )
    betting_risk_level = models.CharField(
        max_length=20,
        choices=[
            ('conservative', 'Conservative'),
            ('moderate', 'Moderate'),
            ('aggressive', 'Aggressive'),
        ],
        default='conservative'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_completed = models.BooleanField(default=False)
    onboarding_completed = models.BooleanField(default=False)

    # Interview Data (from Personal Assistant)
    interview_data = models.JSONField(
        default=dict,
        help_text="Data collected from AI interview"
    )
    interview_completed = models.BooleanField(default=False)
    interview_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Extended User Profile"
        verbose_name_plural = "Extended User Profiles"
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
            models.Index(fields=['profile_completed']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.professional_title or 'Profile'}"

    def get_skills_list(self):
        """Return skills as a list"""
        if isinstance(self.skills, list):
            return self.skills
        return []

    def add_skill(self, skill):
        """Add a skill to the profile"""
        if skill and skill not in self.skills:
            self.skills.append(skill)
            self.save()

    def remove_skill(self, skill):
        """Remove a skill from the profile"""
        if skill in self.skills:
            self.skills.remove(skill)
            self.save()

    def calculate_success_rate(self):
        """Calculate application success rate"""
        if self.total_applications == 0:
            return 0
        return (self.successful_applications / self.total_applications) * 100

    def update_earnings(self, amount):
        """Update total earnings"""
        self.total_earnings += amount
        self.save()

    def is_profile_complete(self):
        """Check if profile has minimum required information"""
        required_fields = [
            self.full_name,
            self.professional_title,
            self.skills,
            self.location,
            self.target_income
        ]

        self.profile_completed = all(required_fields)
        self.save()
        return self.profile_completed

    def get_ai_context(self):
        """
        Return profile data formatted for AI agents
        """
        return {
            'user_id': self.user.id,
            'username': self.user.username,
            'full_name': self.full_name,
            'title': self.professional_title,
            'skills': self.skills,
            'experience_years': self.experience_years,
            'target_income': float(self.target_income) if self.target_income else None,
            'availability': self.availability,
            'hours_per_week': self.hours_per_week,
            'location': self.location,
            'remote_only': self.remote_only,
            'preferred_categories': self.preferred_categories,
            'risk_tolerance': self.risk_tolerance,
            'success_rate': self.calculate_success_rate(),
            'total_earnings': float(self.total_earnings),
            'interview_completed': self.interview_completed,
            'sports_betting_enabled': self.sports_betting_enabled,
            'betting_bankroll': float(self.betting_bankroll) if self.betting_bankroll else None,
            'favorite_sports': self.favorite_sports,
        }

    def save_interview_response(self, question, answer):
        """Save individual interview responses"""
        if not self.interview_data:
            self.interview_data = {}

        self.interview_data[question] = {
            'answer': answer,
            'timestamp': timezone.now().isoformat()
        }
        self.save()

    def extract_skills_from_interview(self):
        """
        Extract skills from interview data using AI analysis
        """
        # This would be enhanced with actual AI processing
        extracted_skills = []

        if self.interview_data:
            for question, response in self.interview_data.items():
                answer = response.get('answer', '').lower()

                # Simple skill extraction (would be AI-enhanced)
                skill_keywords = [
                    'python', 'javascript', 'react', 'django',
                    'machine learning', 'ai', 'data analysis',
                    'writing', 'design', 'marketing', 'sales',
                    'project management', 'leadership'
                ]

                for skill in skill_keywords:
                    if skill in answer and skill not in extracted_skills:
                        extracted_skills.append(skill)

        # Update skills if new ones found
        for skill in extracted_skills:
            self.add_skill(skill)

        return extracted_skills


# Signal handlers to create profile automatically
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_extended_profile(sender, instance, created, **kwargs):
    """Create extended profile when user is created"""
    if created:
        ExtendedUserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_extended_profile(sender, instance, **kwargs):
    """Save extended profile when user is saved"""
    if hasattr(instance, 'extended_profile'):
        instance.extended_profile.save()