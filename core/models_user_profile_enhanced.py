"""
Enhanced User Profile Models for Memory and Personalization
============================================================

Structured user profile system for better memory retrieval and AI personalization.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from typing import Dict, List, Any
import json
from datetime import datetime

User = get_user_model()


class EnhancedUserProfile(models.Model):
    """
    Comprehensive user profile for deep personalization and memory retrieval.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='enhanced_profile')

    # ========== 1. KEY ROLES & LONG-TERM GOALS ==========
    primary_role = models.CharField(
        max_length=200,
        help_text="Primary professional role (e.g., CEO, Software Engineer, PhD Student)"
    )
    secondary_roles = models.JSONField(
        default=list,
        help_text="Additional roles and responsibilities"
    )
    long_term_goals = models.JSONField(
        default=list,
        help_text="Major life/career goals with target dates"
    )
    current_projects = models.JSONField(
        default=list,
        help_text="Active projects with priority levels and deadlines"
    )
    quarterly_objectives = models.JSONField(
        default=dict,
        help_text="OKRs or quarterly goals"
    )

    # ========== 2. COMMUNICATION & DECISION PREFERENCES ==========
    communication_style = models.CharField(
        max_length=50,
        choices=[
            ('concise', 'Concise - Brief and to the point'),
            ('detailed', 'Detailed - Comprehensive information'),
            ('balanced', 'Balanced - Mix based on context'),
            ('visual', 'Visual - Prefer charts and diagrams'),
            ('narrative', 'Narrative - Story-based explanations')
        ],
        default='balanced'
    )

    preferred_channels = models.JSONField(
        default=dict,
        help_text="Preferred communication channels by context (e.g., {urgent: 'phone', updates: 'email'})"
    )

    optimal_meeting_times = models.JSONField(
        default=list,
        help_text="Best times for meetings/calls (e.g., ['9-11am PST', '2-4pm PST'])"
    )

    decision_framework = models.CharField(
        max_length=50,
        choices=[
            ('data_driven', 'Data-Driven - Metrics and analytics focused'),
            ('intuitive', 'Intuitive - Gut feeling and experience'),
            ('collaborative', 'Collaborative - Team consensus'),
            ('analytical', 'Analytical - Pros/cons analysis'),
            ('rapid', 'Rapid - Quick decisions, iterate later')
        ],
        default='analytical'
    )

    delegation_preferences = models.JSONField(
        default=dict,
        help_text="What to delegate vs handle personally"
    )

    # ========== 3. PERSONAL PREFERENCES & ROUTINES ==========
    work_schedule = models.JSONField(
        default=dict,
        help_text="Typical work hours by day of week"
    )

    time_zone = models.CharField(
        max_length=50,
        default='America/Los_Angeles'
    )

    morning_routine = models.TextField(
        blank=True,
        help_text="Morning routine for optimal productivity"
    )

    energy_patterns = models.JSONField(
        default=dict,
        help_text="Energy levels throughout the day (e.g., {morning: 'high', afternoon: 'medium'})"
    )

    dietary_preferences = models.JSONField(
        default=dict,
        help_text="Dietary restrictions, allergies, preferences"
    )

    travel_preferences = models.JSONField(
        default=dict,
        help_text="Travel hubs, airline preferences, hotel chains, etc."
    )

    personal_values = models.JSONField(
        default=list,
        help_text="Core personal values that guide decisions"
    )

    stress_indicators = models.JSONField(
        default=list,
        help_text="Signs of stress and preferred interventions"
    )

    # ========== 4. SKILL LEVELS & LEARNING INTERESTS ==========
    core_competencies = models.JSONField(
        default=dict,
        help_text="Skills with proficiency levels (1-10)"
    )

    learning_style = models.CharField(
        max_length=50,
        choices=[
            ('visual', 'Visual - Images, diagrams, videos'),
            ('auditory', 'Auditory - Lectures, discussions'),
            ('reading', 'Reading/Writing - Text-based'),
            ('kinesthetic', 'Kinesthetic - Hands-on practice'),
            ('mixed', 'Mixed - Combination of styles')
        ],
        default='mixed'
    )

    current_learning_goals = models.JSONField(
        default=list,
        help_text="Skills or topics currently learning"
    )

    knowledge_gaps = models.JSONField(
        default=list,
        help_text="Identified areas for improvement"
    )

    preferred_learning_resources = models.JSONField(
        default=dict,
        help_text="Favorite learning platforms, authors, courses"
    )

    certifications = models.JSONField(
        default=list,
        help_text="Professional certifications with expiry dates"
    )

    # ========== 5. INTERVIEW-BASED PROFILE DATA ==========
    interview_completed = models.BooleanField(
        default=False,
        help_text="Whether the personal assistant interview has been completed"
    )

    interview_completion_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the interview was completed"
    )

    interview_type = models.CharField(
        max_length=20,
        choices=[
            ('quick', 'Quick Start - 2 minutes'),
            ('full', 'Full Interview - 10 minutes')
        ],
        null=True,
        blank=True
    )

    current_situation = models.CharField(
        max_length=100,
        choices=[
            ('employed_seeking_more', 'Employed - looking for more income'),
            ('unemployed_need_asap', 'Unemployed - need income ASAP'),
            ('student_part_time', 'Student - want part-time work'),
            ('entrepreneur_scaling', 'Entrepreneur - scaling my business'),
            ('retired_exploring', 'Retired - exploring opportunities'),
            ('other', 'Other')
        ],
        null=True,
        blank=True,
        help_text="Current life/work situation"
    )

    available_hours_per_week = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(168)],
        help_text="Hours available per week for income activities"
    )

    monthly_income_goal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Target monthly income from new opportunities"
    )

    strongest_skill = models.TextField(
        blank=True,
        help_text="User's description of their strongest skill"
    )

    skill_example = models.TextField(
        blank=True,
        help_text="Specific example of how they've used their strongest skill"
    )

    professional_background = models.TextField(
        blank=True,
        help_text="Professional background and work experience"
    )

    career_motivation = models.TextField(
        blank=True,
        help_text="What motivates career changes or professional drive"
    )

    professional_achievements = models.TextField(
        blank=True,
        help_text="Biggest professional achievement or recent project"
    )

    recent_learning = models.TextField(
        blank=True,
        help_text="Recent courses, certifications, or self-directed learning"
    )

    work_type_preferences = models.JSONField(
        default=list,
        help_text="Preferred work types (project-based, ongoing clients, etc.)"
    )

    things_to_avoid = models.TextField(
        blank=True,
        help_text="Work types or situations they absolutely want to avoid"
    )

    other_work_preferences = models.TextField(
        blank=True,
        help_text="Additional work preferences (remote only, industries, schedule)"
    )

    hidden_talents = models.JSONField(
        default=list,
        help_text="Hobbies, natural strengths, and passion areas that could be monetized"
    )

    available_assets = models.JSONField(
        default=list,
        help_text="Professional assets available (portfolio, LinkedIn, resume, etc.)"
    )

    commitment_level = models.CharField(
        max_length=20,
        choices=[
            ('very_serious', 'Very serious - Will work on this daily'),
            ('serious', 'Serious - Will dedicate real time'),
            ('exploring', 'Exploring - Want to see what\'s possible'),
            ('just_browsing', 'Just browsing')
        ],
        null=True,
        blank=True,
        help_text="Level of commitment to income generation"
    )

    auto_apply_preference = models.CharField(
        max_length=50,
        choices=[
            ('auto_yes', 'Yes - Apply automatically to good matches'),
            ('ask_first', 'Yes - But ask me first'),
            ('no_auto', 'No - Just show me opportunities')
        ],
        null=True,
        blank=True,
        help_text="Preference for automated job applications"
    )

    interview_insights = models.JSONField(
        default=list,
        help_text="AI-generated insights from interview responses"
    )

    profile_strength_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Overall profile strength score based on completeness and quality"
    )

    personalized_recommendations = models.JSONField(
        default=list,
        help_text="Personalized recommendations generated from interview"
    )

    # ========== 6. PRIVACY & UPDATE SETTINGS ==========
    privacy_level = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public - Share with all agents'),
            ('professional', 'Professional - Work-related only'),
            ('personal', 'Personal - Close assistants only'),
            ('private', 'Private - Encrypted, user only')
        ],
        default='professional'
    )

    sensitive_topics = models.JSONField(
        default=list,
        help_text="Topics to handle with extra care"
    )

    data_retention_days = models.IntegerField(
        default=90,
        validators=[MinValueValidator(7), MaxValueValidator(365)],
        help_text="How long to retain interaction history"
    )

    update_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily - High-frequency updates'),
            ('weekly', 'Weekly - Regular check-ins'),
            ('biweekly', 'Bi-weekly - Every two weeks'),
            ('monthly', 'Monthly - Monthly review'),
            ('quarterly', 'Quarterly - Seasonal updates')
        ],
        default='weekly'
    )

    last_profile_review = models.DateTimeField(
        auto_now_add=True,
        help_text="Last time profile was reviewed/updated"
    )

    # ========== ORGANIZATION: STABLE VS DYNAMIC FIELDS ==========
    stable_attributes = models.JSONField(
        default=dict,
        help_text="Rarely changing attributes (personality, core values)"
    )

    dynamic_attributes = models.JSONField(
        default=dict,
        help_text="Frequently changing attributes (current mood, energy)"
    )

    # ========== METADATA & ANALYTICS ==========
    profile_completeness = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )

    interaction_count = models.IntegerField(default=0)

    memory_retrieval_stats = models.JSONField(
        default=dict,
        help_text="Statistics on which profile fields are most accessed"
    )

    ai_insights = models.JSONField(
        default=dict,
        help_text="AI-generated insights about user patterns"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Enhanced User Profile"
        verbose_name_plural = "Enhanced User Profiles"

    def calculate_completeness(self) -> float:
        """Calculate profile completeness percentage including interview data."""
        # Core required fields
        required_fields = [
            'primary_role', 'long_term_goals', 'communication_style',
            'work_schedule', 'core_competencies', 'learning_style'
        ]

        completed = 0
        for field in required_fields:
            value = getattr(self, field, None)
            if value and (not isinstance(value, (list, dict)) or len(value) > 0):
                completed += 1

        # Optional profile fields
        optional_fields = [
            'secondary_roles', 'current_projects', 'quarterly_objectives',
            'dietary_preferences', 'travel_preferences', 'certifications'
        ]

        for field in optional_fields:
            value = getattr(self, field, None)
            if value and (not isinstance(value, (list, dict)) or len(value) > 0):
                completed += 0.5

        # Interview-specific fields (high value for income generation)
        interview_fields = [
            'current_situation', 'available_hours_per_week', 'monthly_income_goal',
            'strongest_skill', 'professional_background', 'commitment_level'
        ]

        for field in interview_fields:
            value = getattr(self, field, None)
            if value and (not isinstance(value, (list, dict)) or len(value) > 0):
                completed += 1.5  # Higher weight for interview data

        # Bonus points for interview completion
        if self.interview_completed:
            completed += 2

        total_possible = len(required_fields) + (len(optional_fields) * 0.5) + (len(interview_fields) * 1.5) + 2
        self.profile_completeness = (completed / total_possible) * 100
        return self.profile_completeness

    def get_context_for_ai(self, context_type: str = 'general') -> Dict[str, Any]:
        """
        Get relevant profile context for AI assistants based on context type.

        Args:
            context_type: Type of context needed ('general', 'work', 'personal', 'learning')

        Returns:
            Dictionary with relevant profile information
        """
        base_context = {
            'user_id': self.user_id,
            'primary_role': self.primary_role,
            'communication_style': self.communication_style,
            'decision_framework': self.decision_framework,
            'timezone': self.time_zone
        }

        if context_type == 'work':
            base_context.update({
                'current_projects': self.current_projects,
                'quarterly_objectives': self.quarterly_objectives,
                'work_schedule': self.work_schedule,
                'delegation_preferences': self.delegation_preferences,
                'optimal_meeting_times': self.optimal_meeting_times
            })

        elif context_type == 'personal':
            if self.privacy_level in ['personal', 'public']:
                base_context.update({
                    'personal_values': self.personal_values,
                    'dietary_preferences': self.dietary_preferences,
                    'travel_preferences': self.travel_preferences,
                    'energy_patterns': self.energy_patterns,
                    'stress_indicators': self.stress_indicators
                })

        elif context_type == 'learning':
            base_context.update({
                'learning_style': self.learning_style,
                'current_learning_goals': self.current_learning_goals,
                'knowledge_gaps': self.knowledge_gaps,
                'core_competencies': self.core_competencies,
                'preferred_learning_resources': self.preferred_learning_resources
            })

        elif context_type == 'income_opportunities':
            # Special context for income generation and job matching
            base_context.update({
                'current_situation': self.current_situation,
                'available_hours_per_week': self.available_hours_per_week,
                'monthly_income_goal': float(self.monthly_income_goal) if self.monthly_income_goal else None,
                'strongest_skill': self.strongest_skill,
                'skill_example': self.skill_example,
                'professional_background': self.professional_background,
                'career_motivation': self.career_motivation,
                'work_type_preferences': self.work_type_preferences,
                'things_to_avoid': self.things_to_avoid,
                'hidden_talents': self.hidden_talents,
                'commitment_level': self.commitment_level,
                'core_competencies': self.core_competencies,
                'available_assets': self.available_assets,
                'personalized_recommendations': self.personalized_recommendations,
                'profile_strength_score': self.profile_strength_score,
                'interview_completed': self.interview_completed
            })

        else:  # general
            base_context.update({
                'long_term_goals': self.long_term_goals[:3] if self.long_term_goals else [],
                'current_projects': self.current_projects[:2] if self.current_projects else [],
                'core_competencies': list(self.core_competencies.keys())[:5] if self.core_competencies else []
            })

        return base_context

    def track_memory_access(self, field_name: str):
        """Track which fields are accessed for memory optimization."""
        if not self.memory_retrieval_stats:
            self.memory_retrieval_stats = {}

        if field_name not in self.memory_retrieval_stats:
            self.memory_retrieval_stats[field_name] = 0

        self.memory_retrieval_stats[field_name] += 1
        self.save(update_fields=['memory_retrieval_stats'])

    def should_update_profile(self) -> bool:
        """Check if profile needs updating based on frequency setting."""
        if not self.last_profile_review:
            return True

        days_since_update = (datetime.now().date() - self.last_profile_review.date()).days

        update_intervals = {
            'daily': 1,
            'weekly': 7,
            'biweekly': 14,
            'monthly': 30,
            'quarterly': 90
        }

        return days_since_update >= update_intervals.get(self.update_frequency, 7)

    def __str__(self):
        return f"{self.user.username} - {self.primary_role} ({self.profile_completeness:.0f}% complete)"


class UserMemoryContext(models.Model):
    """
    Contextual memory storage for user interactions.
    Links profile data with specific memories for better retrieval.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memory_contexts')
    profile = models.ForeignKey(EnhancedUserProfile, on_delete=models.CASCADE)

    memory_type = models.CharField(
        max_length=50,
        choices=[
            ('decision', 'Decision Made'),
            ('preference', 'Preference Stated'),
            ('feedback', 'Feedback Given'),
            ('instruction', 'Instruction Provided'),
            ('context', 'Context Shared'),
            ('goal', 'Goal Mentioned'),
            ('constraint', 'Constraint Identified')
        ]
    )

    content = models.TextField()

    related_project = models.CharField(max_length=200, blank=True)
    related_goal = models.CharField(max_length=200, blank=True)

    importance = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    tags = models.JSONField(default=list)

    context_metadata = models.JSONField(
        default=dict,
        help_text="Additional context like mood, energy level, time of day"
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this memory becomes less relevant"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    accessed_count = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-importance', '-created_at']
        indexes = [
            models.Index(fields=['user', 'memory_type', '-created_at']),
            models.Index(fields=['user', '-importance']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.memory_type}: {self.content[:50]}..."