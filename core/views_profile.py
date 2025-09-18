from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime

# This will use the existing User model and extend it
from django.contrib.auth.models import User

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class ExtendedProfileView(View):
    """Handle extended user profile for AI job applications"""

    def get(self, request):
        """Get the user's extended profile"""
        try:
            user = request.user

            # Get or create profile data (stored in session or cache for now)
            # In production, this would come from the database
            profile_data = request.session.get(f'extended_profile_{user.id}', {})

            # Merge with user basic data
            profile = {
                'id': str(user.id),
                'user': user.username,
                'email': user.email,
                'full_name': profile_data.get('full_name', f'{user.first_name} {user.last_name}'.strip()),
                'current_title': profile_data.get('current_title', ''),
                'years_experience': profile_data.get('years_experience', 0),
                'location': profile_data.get('location', ''),
                'remote_preference': profile_data.get('remote_preference', 'no_preference'),
                'skills': profile_data.get('skills', []),
                'work_history': profile_data.get('work_history', []),
                'education': profile_data.get('education', []),
                'desired_salary_min': profile_data.get('desired_salary_min'),
                'desired_salary_max': profile_data.get('desired_salary_max'),
                'linkedin_url': profile_data.get('linkedin_url', ''),
                'github_username': profile_data.get('github_username', ''),
                'portfolio_url': profile_data.get('portfolio_url', ''),
                'professional_summary': profile_data.get('professional_summary', ''),
                'job_preferences': profile_data.get('job_preferences', {
                    'industries': [],
                    'job_types': [],
                    'company_sizes': [],
                    'cultures': [],
                    'auto_apply': False,
                    'min_match_score': 0.7,
                    'application_tone': 'professional',
                    'max_applications_per_day': 10
                }),
                'profile_completeness': self.calculate_completeness(profile_data),
                'created_at': profile_data.get('created_at', datetime.now().isoformat()),
                'updated_at': profile_data.get('updated_at', datetime.now().isoformat())
            }

            return JsonResponse({
                'success': True,
                'profile': profile
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    def post(self, request):
        """Update the user's extended profile"""
        try:
            user = request.user
            data = json.loads(request.body)

            # Get existing profile
            profile_data = request.session.get(f'extended_profile_{user.id}', {})

            # Update fields
            updateable_fields = [
                'full_name', 'current_title', 'years_experience', 'location',
                'remote_preference', 'skills', 'work_history', 'education',
                'desired_salary_min', 'desired_salary_max', 'linkedin_url',
                'github_username', 'portfolio_url', 'professional_summary',
                'job_preferences', 'languages', 'availability', 'contract_preference',
                'key_achievements', 'certifications'
            ]

            for field in updateable_fields:
                if field in data:
                    profile_data[field] = data[field]

            # Update timestamps
            if 'created_at' not in profile_data:
                profile_data['created_at'] = datetime.now().isoformat()
            profile_data['updated_at'] = datetime.now().isoformat()

            # Save to session (in production, save to database)
            request.session[f'extended_profile_{user.id}'] = profile_data
            request.session.modified = True

            # Return updated profile
            profile = {
                'id': str(user.id),
                'user': user.username,
                'email': user.email,
                **profile_data,
                'profile_completeness': self.calculate_completeness(profile_data)
            }

            return JsonResponse({
                'success': True,
                'profile': profile,
                'message': 'Profile updated successfully'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    def calculate_completeness(self, profile_data):
        """Calculate profile completeness percentage"""
        required_fields = [
            'full_name', 'current_title', 'professional_summary',
            'skills', 'work_history', 'education'
        ]

        completed = 0
        for field in required_fields:
            value = profile_data.get(field)
            if value:
                if isinstance(value, list) and len(value) > 0:
                    completed += 1
                elif isinstance(value, str) and value.strip():
                    completed += 1
                elif not isinstance(value, (list, str)):
                    completed += 1

        return int((completed / len(required_fields)) * 100)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class ProfileSkillsView(View):
    """Manage user skills"""

    def post(self, request):
        """Add or update skills"""
        try:
            user = request.user
            data = json.loads(request.body)
            skills = data.get('skills', [])

            # Get profile
            profile_data = request.session.get(f'extended_profile_{user.id}', {})
            profile_data['skills'] = skills
            profile_data['updated_at'] = datetime.now().isoformat()

            # Save
            request.session[f'extended_profile_{user.id}'] = profile_data
            request.session.modified = True

            return JsonResponse({
                'success': True,
                'skills': skills,
                'message': 'Skills updated successfully'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    def delete(self, request):
        """Remove a skill"""
        try:
            user = request.user
            data = json.loads(request.body)
            skill_to_remove = data.get('skill')

            # Get profile
            profile_data = request.session.get(f'extended_profile_{user.id}', {})
            skills = profile_data.get('skills', [])

            if skill_to_remove in skills:
                skills.remove(skill_to_remove)
                profile_data['skills'] = skills
                profile_data['updated_at'] = datetime.now().isoformat()

                # Save
                request.session[f'extended_profile_{user.id}'] = profile_data
                request.session.modified = True

                return JsonResponse({
                    'success': True,
                    'skills': skills,
                    'message': f'Removed skill: {skill_to_remove}'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Skill not found'
                }, status=404)

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class ProfileForApplicationView(View):
    """Get profile data formatted for job applications"""

    def get(self, request):
        """Get profile data optimized for AI job applications"""
        try:
            user = request.user
            profile_data = request.session.get(f'extended_profile_{user.id}', {})

            # Format for job application
            application_profile = {
                'full_name': profile_data.get('full_name', f'{user.first_name} {user.last_name}'.strip()),
                'email': user.email,
                'current_title': profile_data.get('current_title', ''),
                'professional_summary': profile_data.get('professional_summary', ''),
                'years_experience': profile_data.get('years_experience', 0),
                'skills': profile_data.get('skills', []),
                'work_history': profile_data.get('work_history', []),
                'education': profile_data.get('education', []),
                'linkedin_url': profile_data.get('linkedin_url', ''),
                'github_username': profile_data.get('github_username', ''),
                'portfolio_url': profile_data.get('portfolio_url', ''),
                'location': profile_data.get('location', ''),
                'remote_preference': profile_data.get('remote_preference', 'no_preference'),
                'languages': profile_data.get('languages', []),
                'certifications': profile_data.get('certifications', []),
                'key_achievements': profile_data.get('key_achievements', []),
                'availability': profile_data.get('availability', 'immediate'),
                'application_settings': {
                    'tone': profile_data.get('job_preferences', {}).get('application_tone', 'professional'),
                    'auto_apply': profile_data.get('job_preferences', {}).get('auto_apply', False),
                    'min_match_score': profile_data.get('job_preferences', {}).get('min_match_score', 0.7)
                }
            }

            # Check if profile is complete enough for applications
            completeness = self.calculate_application_readiness(application_profile)

            return JsonResponse({
                'success': True,
                'profile': application_profile,
                'ready_for_applications': completeness['is_ready'],
                'completeness': completeness,
                'missing_fields': completeness['missing']
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    def calculate_application_readiness(self, profile):
        """Check if profile is ready for job applications"""
        required = ['full_name', 'email', 'professional_summary', 'skills', 'work_history']
        missing = []

        for field in required:
            value = profile.get(field)
            if not value or (isinstance(value, list) and len(value) == 0):
                missing.append(field)

        score = (len(required) - len(missing)) / len(required) * 100

        return {
            'is_ready': len(missing) == 0,
            'score': score,
            'missing': missing,
            'required': required
        }