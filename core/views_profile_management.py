"""
Profile Management Views - API endpoints for user profile completion

These views provide the API layer for managing extended user profiles,
including profile setup, skills management, and completion tracking.
"""

import logging
from decimal import Decimal
from typing import Dict, Any

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json

from .models import ExtendedUserProfile, JobApplication, ResumeVersion, UserEmbedding
from .agent_context_middleware import get_user_context_for_agent

logger = logging.getLogger(__name__)

User = get_user_model()


@method_decorator([csrf_exempt, login_required], name='dispatch')
class ExtendedProfileView(View):
    """
    API for managing extended user profiles.

    Provides CRUD operations for the extended profile system
    that powers personalized AI agent interactions.
    """

    def get(self, request):
        """Get current user's extended profile"""
        try:
            profile, created = ExtendedUserProfile.objects.get_or_create(user=request.user)

            if created:
                logger.info(f"Created new extended profile for {request.user.username}")

            # Calculate profile completeness
            completeness = profile.calculate_profile_completeness()
            profile.save(update_fields=['profile_completeness'])

            return JsonResponse({
                'success': True,
                'profile': {
                    'id': str(profile.id),
                    'full_name': profile.full_name,
                    'phone': profile.phone,
                    'location': profile.location,
                    'timezone': profile.timezone,
                    'current_title': profile.current_title,
                    'years_experience': profile.years_experience,
                    'experience_level': profile.experience_level,
                    'desired_salary_min': float(profile.desired_salary_min) if profile.desired_salary_min else None,
                    'desired_salary_max': float(profile.desired_salary_max) if profile.desired_salary_max else None,
                    'skills': profile.skills,
                    'certifications': profile.certifications,
                    'work_history': profile.work_history,
                    'education': profile.education,
                    'resume_url': profile.resume.url if profile.resume else None,
                    'portfolio_url': profile.portfolio_url,
                    'cover_letters': profile.cover_letters,
                    'linkedin_url': profile.linkedin_url,
                    'indeed_profile': profile.indeed_profile,
                    'github_username': profile.github_username,
                    'job_preferences': profile.job_preferences,
                    'remote_preference': profile.remote_preference,
                    'willing_to_relocate': profile.willing_to_relocate,
                    'profile_completeness': completeness,
                    'created_at': profile.created_at.isoformat(),
                    'updated_at': profile.updated_at.isoformat()
                }
            })

        except Exception as e:
            logger.error(f"Error fetching profile for {request.user.username}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    def post(self, request):
        """Update user's extended profile"""
        try:
            data = json.loads(request.body or b"{}")
            profile, created = ExtendedUserProfile.objects.get_or_create(user=request.user)

            # Update basic information
            if 'full_name' in data:
                profile.full_name = data['full_name']
            if 'phone' in data:
                profile.phone = data['phone']
            if 'location' in data:
                profile.location = data['location']
            if 'timezone' in data:
                profile.timezone = data['timezone']

            # Update professional information
            if 'current_title' in data:
                profile.current_title = data['current_title']
            if 'years_experience' in data:
                profile.years_experience = int(data['years_experience'])
            if 'experience_level' in data:
                profile.experience_level = data['experience_level']
            if 'desired_salary_min' in data and data['desired_salary_min']:
                profile.desired_salary_min = Decimal(str(data['desired_salary_min']))
            if 'desired_salary_max' in data and data['desired_salary_max']:
                profile.desired_salary_max = Decimal(str(data['desired_salary_max']))

            # Update skills and certifications
            if 'skills' in data:
                profile.skills = data['skills']
            if 'certifications' in data:
                profile.certifications = data['certifications']

            # Update background
            if 'work_history' in data:
                profile.work_history = data['work_history']
            if 'education' in data:
                profile.education = data['education']

            # Update URLs and profiles
            if 'portfolio_url' in data:
                profile.portfolio_url = data['portfolio_url']
            if 'linkedin_url' in data:
                profile.linkedin_url = data['linkedin_url']
            if 'indeed_profile' in data:
                profile.indeed_profile = data['indeed_profile']
            if 'github_username' in data:
                profile.github_username = data['github_username']

            # Update preferences
            if 'job_preferences' in data:
                profile.job_preferences = data['job_preferences']
            if 'remote_preference' in data:
                profile.remote_preference = data['remote_preference']
            if 'willing_to_relocate' in data:
                profile.willing_to_relocate = data['willing_to_relocate']

            # Update cover letters
            if 'cover_letters' in data:
                profile.cover_letters = data['cover_letters']

            # Calculate and save completeness
            completeness = profile.calculate_profile_completeness()
            profile.save()

            logger.info(f"Updated profile for {request.user.username} (completeness: {completeness:.1f}%)")

            return JsonResponse({
                'success': True,
                'profile_completeness': completeness,
                'message': f'Profile updated successfully ({completeness:.1f}% complete)'
            })

        except Exception as e:
            logger.error(f"Error updating profile for {request.user.username}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([csrf_exempt, login_required], name='dispatch')
class ProfileCompletionView(View):
    """API for tracking profile completion progress"""

    def get(self, request):
        """Get profile completion status and suggestions"""
        try:
            profile, created = ExtendedUserProfile.objects.get_or_create(user=request.user)
            completeness = profile.calculate_profile_completeness()

            # Identify missing fields
            missing_fields = []
            required_fields = {
                'full_name': 'Full Name',
                'phone': 'Phone Number',
                'location': 'Location',
                'current_title': 'Current Job Title',
                'years_experience': 'Years of Experience',
                'skills': 'Skills',
                'work_history': 'Work History',
                'resume': 'Resume Upload'
            }

            for field_name, display_name in required_fields.items():
                value = getattr(profile, field_name)
                if not value or (isinstance(value, list) and len(value) == 0):
                    missing_fields.append({
                        'field': field_name,
                        'display_name': display_name,
                        'priority': 'high' if field_name in ['full_name', 'current_title', 'skills', 'resume'] else 'medium'
                    })

            # Generate completion suggestions
            suggestions = []
            if completeness < 50:
                suggestions.append("Complete your basic information to unlock AI-powered job matching")
            if not profile.skills:
                suggestions.append("Add your skills to get personalized job recommendations")
            if not profile.work_history:
                suggestions.append("Add work history for better cover letter generation")
            if not profile.resume:
                suggestions.append("Upload your resume to enable quick job applications")

            return JsonResponse({
                'success': True,
                'completion': {
                    'percentage': completeness,
                    'missing_fields': missing_fields,
                    'suggestions': suggestions,
                    'next_priority': missing_fields[0] if missing_fields else None
                }
            })

        except Exception as e:
            logger.error(f"Error getting completion status for {request.user.username}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([csrf_exempt, login_required], name='dispatch')
class ResumeUploadView(View):
    """API for uploading and managing resume files"""

    def post(self, request):
        """Upload a new resume file"""
        try:
            if 'resume' not in request.FILES:
                return JsonResponse({
                    'success': False,
                    'error': 'No resume file provided'
                }, status=400)

            resume_file = request.FILES['resume']
            version_name = request.POST.get('version_name', 'Primary Resume')
            is_primary = request.POST.get('is_primary', 'true').lower() == 'true'

            # Validate file type
            allowed_extensions = ['.pdf', '.doc', '.docx']
            file_extension = resume_file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
                }, status=400)

            # Update extended profile with resume
            profile, created = ExtendedUserProfile.objects.get_or_create(user=request.user)
            profile.resume = resume_file
            profile.save()

            # Create or update resume version
            resume_version, created = ResumeVersion.objects.update_or_create(
                user=request.user,
                version_name=version_name,
                defaults={
                    'resume_file': resume_file,
                    'is_primary': is_primary
                }
            )

            # If this is marked as primary, unmark others
            if is_primary:
                ResumeVersion.objects.filter(
                    user=request.user
                ).exclude(
                    id=resume_version.id
                ).update(is_primary=False)

            # Update profile completeness
            completeness = profile.calculate_profile_completeness()
            profile.save(update_fields=['profile_completeness'])

            logger.info(f"Resume uploaded for {request.user.username}: {version_name}")

            return JsonResponse({
                'success': True,
                'resume_version': {
                    'id': str(resume_version.id),
                    'version_name': resume_version.version_name,
                    'is_primary': resume_version.is_primary,
                    'file_url': resume_version.resume_file.url,
                    'created_at': resume_version.created_at.isoformat()
                },
                'profile_completeness': completeness
            })

        except Exception as e:
            logger.error(f"Error uploading resume for {request.user.username}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    def get(self, request):
        """Get all resume versions for the user"""
        try:
            resume_versions = ResumeVersion.objects.filter(user=request.user)

            versions_data = []
            for version in resume_versions:
                version.calculate_success_rate()  # Update success rate
                versions_data.append({
                    'id': str(version.id),
                    'version_name': version.version_name,
                    'is_primary': version.is_primary,
                    'file_url': version.resume_file.url if version.resume_file else None,
                    'target_industries': version.target_industries,
                    'target_roles': version.target_roles,
                    'times_used': version.times_used,
                    'success_rate': version.success_rate,
                    'created_at': version.created_at.isoformat(),
                    'updated_at': version.updated_at.isoformat()
                })

            return JsonResponse({
                'success': True,
                'resume_versions': versions_data
            })

        except Exception as e:
            logger.error(f"Error fetching resume versions for {request.user.username}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([csrf_exempt, login_required], name='dispatch')
class UserContextView(View):
    """API for getting user context for agent personalization"""

    def get(self, request):
        """Get comprehensive user context for AI agents"""
        try:
            # Get full user context using the middleware
            context = get_user_context_for_agent(request.user)

            return JsonResponse({
                'success': True,
                'user_context': context
            })

        except Exception as e:
            logger.error(f"Error getting user context for {request.user.username}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([csrf_exempt, login_required], name='dispatch')
class JobApplicationsView(View):
    """API for managing job applications"""

    def get(self, request):
        """Get user's job applications with analytics"""
        try:
            applications = JobApplication.objects.filter(user=request.user).order_by('-applied_date')

            applications_data = []
            for app in applications:
                app.calculate_response_time()  # Update response time
                applications_data.append({
                    'id': str(app.id),
                    'job_id': app.job_id,
                    'platform': app.platform,
                    'company': app.company,
                    'position': app.position,
                    'job_url': app.job_url,
                    'applied_date': app.applied_date.isoformat(),
                    'application_method': app.application_method,
                    'status': app.status,
                    'last_status_update': app.last_status_update.isoformat(),
                    'response_time_days': app.response_time_days,
                    'match_score': app.match_score,
                    'is_successful': app.is_successful(),
                    'is_in_progress': app.is_in_progress(),
                    'employer_response': app.employer_response,
                    'notes': app.notes
                })

            # Calculate analytics
            total_apps = applications.count()
            successful_apps = applications.filter(status__in=['offer_received', 'offer_accepted']).count()
            success_rate = (successful_apps / total_apps * 100) if total_apps > 0 else 0

            # Response time analytics
            responded_apps = applications.exclude(response_time_days__isnull=True)
            avg_response_time = None
            if responded_apps.exists():
                from django.db.models import Avg
                avg_response_time = responded_apps.aggregate(avg=Avg('response_time_days'))['avg']

            return JsonResponse({
                'success': True,
                'applications': applications_data,
                'analytics': {
                    'total_applications': total_apps,
                    'successful_applications': successful_apps,
                    'success_rate': round(success_rate, 2),
                    'average_response_time_days': round(avg_response_time, 1) if avg_response_time else None,
                    'applications_this_month': applications.filter(
                        applied_date__month=request.GET.get('month', ''),
                        applied_date__year=request.GET.get('year', '')
                    ).count() if request.GET.get('month') and request.GET.get('year') else None
                }
            })

        except Exception as e:
            logger.error(f"Error fetching applications for {request.user.username}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    def post(self, request):
        """Create a new job application record"""
        try:
            data = json.loads(request.body or b"{}")

            application = JobApplication.objects.create(
                user=request.user,
                job_id=data.get('job_id', ''),
                platform=data.get('platform', ''),
                company=data.get('company', ''),
                position=data.get('position', ''),
                job_url=data.get('job_url', ''),
                application_method=data.get('application_method', 'quick_apply'),
                resume_version=data.get('resume_version', ''),
                cover_letter_used=data.get('cover_letter_used', ''),
                match_score=float(data.get('match_score', 0))
            )

            logger.info(f"Created job application for {request.user.username}: {application.position} at {application.company}")

            return JsonResponse({
                'success': True,
                'application': {
                    'id': str(application.id),
                    'company': application.company,
                    'position': application.position,
                    'status': application.status,
                    'applied_date': application.applied_date.isoformat(),
                    'match_score': application.match_score
                }
            })

        except Exception as e:
            logger.error(f"Error creating application for {request.user.username}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


# URL patterns helper
def get_profile_urls():
    """Return URL patterns for profile management"""
    from django.urls import path

    return [
        path('api/profile/extended/', ExtendedProfileView.as_view(), name='extended_profile'),
        path('api/profile/completion/', ProfileCompletionView.as_view(), name='profile_completion'),
        path('api/profile/resume/', ResumeUploadView.as_view(), name='resume_upload'),
        path('api/profile/context/', UserContextView.as_view(), name='user_context'),
        path('api/profile/applications/', JobApplicationsView.as_view(), name='job_applications'),
    ]