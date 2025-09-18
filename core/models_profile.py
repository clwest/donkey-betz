from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class UserProfile(models.Model):
    """Extended user profile for AI job applications"""

    # Link to Django User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ai_profile')

    # Basic Information
    full_name = models.CharField(max_length=200)
    professional_title = models.CharField(max_length=200, help_text="e.g. Full Stack Developer, Data Scientist")
    location = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)

    # Professional Summary
    professional_summary = models.TextField(
        help_text="A brief overview of your experience and expertise (2-3 paragraphs)"
    )
    years_of_experience = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        default=0
    )

    # Skills (stored as JSON)
    technical_skills = models.JSONField(
        default=list,
        help_text="List of technical skills (e.g., Python, React, AWS)"
    )
    soft_skills = models.JSONField(
        default=list,
        help_text="List of soft skills (e.g., Leadership, Communication)"
    )
    industries = models.JSONField(
        default=list,
        help_text="Industries you have experience in"
    )

    # Work Experience (stored as JSON array)
    work_experience = models.JSONField(
        default=list,
        help_text="""List of work experiences, each containing:
        - company, title, start_date, end_date, current, description, achievements"""
    )

    # Education (stored as JSON array)
    education = models.JSONField(
        default=list,
        help_text="""List of education entries, each containing:
        - institution, degree, field_of_study, start_year, end_year, gpa (optional)"""
    )

    # Certifications (stored as JSON array)
    certifications = models.JSONField(
        default=list,
        help_text="List of certifications with name, issuer, date"
    )

    # Projects (stored as JSON array)
    projects = models.JSONField(
        default=list,
        help_text="""Notable projects, each containing:
        - name, description, technologies, url (optional), role"""
    )

    # Job Preferences
    desired_job_titles = models.JSONField(
        default=list,
        help_text="Job titles you're interested in"
    )
    job_type_preferences = models.JSONField(
        default=list,
        help_text="remote, hybrid, onsite, contract, full-time, part-time"
    )
    minimum_salary = models.IntegerField(
        null=True, blank=True,
        help_text="Minimum acceptable salary (annual USD)"
    )
    preferred_salary = models.IntegerField(
        null=True, blank=True,
        help_text="Preferred salary (annual USD)"
    )
    willing_to_relocate = models.BooleanField(default=False)
    preferred_locations = models.JSONField(
        default=list,
        help_text="List of preferred work locations"
    )

    # AI Application Settings
    auto_apply = models.BooleanField(
        default=False,
        help_text="Automatically apply to matched jobs"
    )
    min_match_score = models.FloatField(
        default=0.7,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Minimum AI match score to consider a job (0-1)"
    )
    application_tone = models.CharField(
        max_length=50,
        choices=[
            ('professional', 'Professional'),
            ('friendly', 'Friendly'),
            ('enthusiastic', 'Enthusiastic'),
            ('formal', 'Formal'),
        ],
        default='professional'
    )

    # Additional Information
    languages = models.JSONField(
        default=list,
        help_text="Languages spoken with proficiency level"
    )
    achievements = models.JSONField(
        default=list,
        help_text="Notable achievements and awards"
    )
    references_available = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_complete = models.BooleanField(default=False)

    class Meta:
        db_table = 'user_ai_profiles'
        verbose_name = 'User AI Profile'
        verbose_name_plural = 'User AI Profiles'

    def __str__(self):
        return f"{self.full_name} - {self.professional_title}"

    def calculate_profile_completeness(self):
        """Calculate how complete the profile is (0-100%)"""
        required_fields = [
            'full_name', 'professional_title', 'professional_summary',
            'technical_skills', 'work_experience', 'education'
        ]

        completed = 0
        for field in required_fields:
            value = getattr(self, field)
            if value and (not isinstance(value, list) or len(value) > 0):
                completed += 1

        return int((completed / len(required_fields)) * 100)

    def get_skills_for_matching(self):
        """Get all skills for job matching"""
        return {
            'technical': self.technical_skills,
            'soft': self.soft_skills,
            'total_count': len(self.technical_skills) + len(self.soft_skills)
        }

    def get_experience_summary(self):
        """Get a summary of work experience"""
        if not self.work_experience:
            return "No experience listed"

        current_job = next((job for job in self.work_experience if job.get('current')), None)
        if current_job:
            return f"{current_job['title']} at {current_job['company']}"
        elif self.work_experience:
            latest = self.work_experience[0]
            return f"Former {latest['title']} at {latest['company']}"

        return "Multiple experiences"