"""
Job Application System - Complete job search and application automation

This system provides comprehensive job application management including:
- Job opportunity discovery and scoring
- AI-powered quick apply functionality
- Application tracking and status management
- Success pattern analysis and learning
"""

import logging
import json
from typing import Dict, Any, List
from decimal import Decimal
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Q, Count, Avg
from django.utils import timezone

from .models import ExtendedUserProfile, JobApplication, ResumeVersion, UserEmbedding
from .agent_context_middleware import (
    get_user_context_for_agent,
    calculate_opportunity_fit_score
)
from ai_core.agents.ai_enforced_base import AIEnforcedApplicationAgent

logger = logging.getLogger(__name__)

User = get_user_model()


@method_decorator([csrf_exempt, login_required], name='dispatch')
class JobOpportunityView(View):
    """
    API for job opportunity discovery and analysis.

    This view provides job matching, scoring, and recommendation
    functionality based on user profiles and preferences.
    """

    def get(self, request):
        """Get personalized job opportunities with fit scores"""
        try:
            # Get user context for personalization
            user_context = get_user_context_for_agent(request.user)

            # Get query parameters
            location = request.GET.get('location', '')
            remote_only = request.GET.get('remote', '').lower() == 'true'
            salary_min = request.GET.get('salary_min', '')
            keywords = request.GET.get('keywords', '').split(',') if request.GET.get('keywords') else []
            page = int(request.GET.get('page', 1))
            per_page = int(request.GET.get('per_page', 20))

            # Simulate job opportunities (in real implementation, this would call external APIs)
            opportunities = self._get_job_opportunities(
                user_context, location, remote_only, salary_min, keywords, page, per_page
            )

            # Score each opportunity for this user
            scored_opportunities = []
            for opportunity in opportunities:
                fit_score = calculate_opportunity_fit_score(request.user, opportunity)
                opportunity['fit_score'] = fit_score
                opportunity['recommended'] = fit_score >= 70

                # Add application status if user has applied
                existing_app = JobApplication.objects.filter(
                    user=request.user,
                    job_id=opportunity['id']
                ).first()

                opportunity['application_status'] = {
                    'applied': existing_app is not None,
                    'status': existing_app.status if existing_app else None,
                    'applied_date': existing_app.applied_date.isoformat() if existing_app else None
                }

                scored_opportunities.append(opportunity)

            # Sort by fit score
            scored_opportunities.sort(key=lambda x: x['fit_score'], reverse=True)

            return JsonResponse({
                'success': True,
                'opportunities': scored_opportunities,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': len(scored_opportunities),
                    'has_next': len(scored_opportunities) == per_page
                },
                'user_preferences': {
                    'location': user_context.get('professional_profile', {}).get('location', ''),
                    'remote_preference': user_context.get('professional_profile', {}).get('remote_preference', ''),
                    'salary_range': user_context.get('professional_profile', {}).get('salary_range', {}),
                    'top_skills': [skill.get('name', '') for skill in user_context.get('skills', {}).get('top_skills', [])]
                }
            })

        except Exception as e:
            logger.error(f"Error fetching opportunities for {request.user.username}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    def _get_job_opportunities(self, user_context: Dict, location: str, remote_only: bool,
                             salary_min: str, keywords: List[str], page: int, per_page: int) -> List[Dict]:
        """
        Get job opportunities from various sources.

        In a real implementation, this would integrate with:
        - LinkedIn Jobs API
        - Indeed API
        - Glassdoor API
        - Company career pages
        - Job board APIs
        """

        # Get user skills for better matching
        user_skills = user_context.get('skills', {}).get('skills_list', [])
        user_location = user_context.get('professional_profile', {}).get('location', '')
        salary_range = user_context.get('professional_profile', {}).get('salary_range', {})

        # Simulate realistic job opportunities based on user profile
        sample_opportunities = [
            {
                'id': 'job_001',
                'title': 'Senior Software Engineer',
                'company': 'TechCorp Inc.',
                'location': 'San Francisco, CA',
                'remote': True,
                'salary_min': 120000,
                'salary_max': 160000,
                'description': 'We are looking for a Senior Software Engineer to join our growing team. You will work on scalable web applications using modern technologies.',
                'required_skills': ['Python', 'JavaScript', 'React', 'SQL'],
                'preferred_skills': ['AWS', 'Docker', 'Kubernetes'],
                'min_experience': 5,
                'max_experience': 10,
                'company_size': 'Medium (100-500)',
                'industry': 'Technology',
                'posted_date': '2025-01-10',
                'apply_url': 'https://techcorp.com/careers/senior-engineer',
                'platform': 'linkedin'
            },
            {
                'id': 'job_002',
                'title': 'Data Scientist',
                'company': 'DataFlow Analytics',
                'location': 'Remote',
                'remote': True,
                'salary_min': 100000,
                'salary_max': 140000,
                'description': 'Join our data science team to build machine learning models and analytics solutions.',
                'required_skills': ['Python', 'Machine Learning', 'SQL', 'Statistics'],
                'preferred_skills': ['TensorFlow', 'PyTorch', 'Pandas', 'Jupyter'],
                'min_experience': 3,
                'max_experience': 7,
                'company_size': 'Startup (10-50)',
                'industry': 'Data Analytics',
                'posted_date': '2025-01-09',
                'apply_url': 'https://dataflow.com/jobs/data-scientist',
                'platform': 'indeed'
            },
            {
                'id': 'job_003',
                'title': 'Frontend Developer',
                'company': 'Design Studios LLC',
                'location': 'New York, NY',
                'remote': False,
                'salary_min': 80000,
                'salary_max': 110000,
                'description': 'Create beautiful and responsive user interfaces for our client projects.',
                'required_skills': ['JavaScript', 'React', 'HTML', 'CSS'],
                'preferred_skills': ['TypeScript', 'Vue.js', 'Figma'],
                'min_experience': 2,
                'max_experience': 5,
                'company_size': 'Small (10-50)',
                'industry': 'Design',
                'posted_date': '2025-01-08',
                'apply_url': 'https://designstudios.com/careers',
                'platform': 'company_website'
            },
            {
                'id': 'job_004',
                'title': 'DevOps Engineer',
                'company': 'CloudTech Solutions',
                'location': 'Austin, TX',
                'remote': True,
                'salary_min': 110000,
                'salary_max': 150000,
                'description': 'Manage cloud infrastructure and CI/CD pipelines for our SaaS platform.',
                'required_skills': ['AWS', 'Docker', 'Kubernetes', 'Linux'],
                'preferred_skills': ['Terraform', 'Jenkins', 'Monitoring'],
                'min_experience': 4,
                'max_experience': 8,
                'company_size': 'Medium (100-500)',
                'industry': 'Cloud Services',
                'posted_date': '2025-01-07',
                'apply_url': 'https://cloudtech.com/jobs/devops',
                'platform': 'glassdoor'
            },
            {
                'id': 'job_005',
                'title': 'Product Manager',
                'company': 'InnovateCorp',
                'location': 'Seattle, WA',
                'remote': False,
                'salary_min': 130000,
                'salary_max': 170000,
                'description': 'Lead product strategy and development for our flagship products.',
                'required_skills': ['Product Management', 'Strategy', 'Analytics', 'Leadership'],
                'preferred_skills': ['Agile', 'User Research', 'A/B Testing'],
                'min_experience': 6,
                'max_experience': 12,
                'company_size': 'Large (1000+)',
                'industry': 'Technology',
                'posted_date': '2025-01-06',
                'apply_url': 'https://innovate.com/careers/pm',
                'platform': 'linkedin'
            }
        ]

        # Filter opportunities based on search criteria
        filtered_opportunities = []
        for opp in sample_opportunities:
            # Location filter
            if location and location.lower() not in opp['location'].lower() and not opp['remote']:
                continue

            # Remote filter
            if remote_only and not opp['remote']:
                continue

            # Salary filter
            if salary_min and opp['salary_max'] < int(salary_min):
                continue

            # Keywords filter
            if keywords:
                opp_text = f"{opp['title']} {opp['description']} {' '.join(opp['required_skills'])}".lower()
                if not any(keyword.lower() in opp_text for keyword in keywords if keyword.strip()):
                    continue

            filtered_opportunities.append(opp)

        # Pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page

        return filtered_opportunities[start_idx:end_idx]


@method_decorator([csrf_exempt, login_required], name='dispatch')
class QuickApplyView(View):
    """
    API for AI-powered quick job applications.

    This view handles the complete application process:
    - Generates personalized cover letters
    - Selects appropriate resume version
    - Submits applications through platform APIs
    - Tracks application status
    """

    def post(self, request):
        """Submit a quick application to a job opportunity"""
        try:
            data = json.loads(request.body)
            job_data = data.get('job_data', {})

            if not job_data.get('id'):
                return JsonResponse({
                    'success': False,
                    'error': 'Job ID is required'
                }, status=400)

            # Check if user has already applied
            existing_app = JobApplication.objects.filter(
                user=request.user,
                job_id=job_data['id']
            ).first()

            if existing_app:
                return JsonResponse({
                    'success': False,
                    'error': 'You have already applied to this position',
                    'application_id': str(existing_app.id),
                    'applied_date': existing_app.applied_date.isoformat()
                }, status=400)

            # Get user profile for application
            try:
                extended_profile = ExtendedUserProfile.objects.get(user=request.user)
            except ExtendedUserProfile.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Please complete your profile before applying to jobs'
                }, status=400)

            # Check profile completeness
            completeness = extended_profile.calculate_profile_completeness()
            if completeness < 60:
                return JsonResponse({
                    'success': False,
                    'error': f'Profile is only {completeness:.1f}% complete. Please add more information.',
                    'required_fields': ['full_name', 'phone', 'current_title', 'skills', 'resume']
                }, status=400)

            # Initialize AI application agent with user context
            application_agent = AIEnforcedApplicationAgent(
                agent_name="QuickApplyAgent",
                user=request.user
            )

            # Analyze job fit
            job_analysis = application_agent.analyze_job_fit(job_data)

            # Generate personalized cover letter
            cover_letter = application_agent.generate_cover_letter(job_data)

            # Select best resume version
            resume_version = self._select_best_resume(request.user, job_data)

            # Calculate match score
            match_score = calculate_opportunity_fit_score(request.user, job_data)

            # Create application record
            application = JobApplication.objects.create(
                user=request.user,
                job_id=job_data['id'],
                platform=job_data.get('platform', 'unknown'),
                company=job_data.get('company', ''),
                position=job_data.get('title', ''),
                job_url=job_data.get('apply_url', ''),
                application_method='quick_apply',
                resume_version=resume_version.version_name if resume_version else 'Primary',
                cover_letter_used=cover_letter,
                match_score=match_score
            )

            # Simulate application submission (in real implementation, integrate with platform APIs)
            submission_result = self._submit_application_to_platform(
                job_data, extended_profile, cover_letter, resume_version
            )

            # Update application status based on submission result
            if submission_result['success']:
                application.status = 'applied'
            else:
                application.status = 'failed'
                application.notes = f"Submission failed: {submission_result.get('error', 'Unknown error')}"

            application.save()

            # Create user embedding for learning
            self._create_application_embedding(request.user, application, job_analysis)

            # Update resume usage statistics
            if resume_version:
                resume_version.increment_usage()

            logger.info(f"Quick apply completed for {request.user.username}: {job_data.get('title')} at {job_data.get('company')}")

            return JsonResponse({
                'success': True,
                'application': {
                    'id': str(application.id),
                    'job_id': application.job_id,
                    'company': application.company,
                    'position': application.position,
                    'status': application.status,
                    'applied_date': application.applied_date.isoformat(),
                    'match_score': application.match_score,
                    'cover_letter_preview': cover_letter[:200] + "..." if len(cover_letter) > 200 else cover_letter,
                    'resume_version': resume_version.version_name if resume_version else 'Primary'
                },
                'job_analysis': job_analysis,
                'submission_result': submission_result
            })

        except Exception as e:
            logger.error(f"Error in quick apply for {request.user.username}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    def _select_best_resume(self, user: User, job_data: Dict[str, Any]) -> ResumeVersion:
        """Select the best resume version for this job application"""
        resume_versions = ResumeVersion.objects.filter(user=user)

        if not resume_versions.exists():
            return None

        # If only one version, use it
        if resume_versions.count() == 1:
            return resume_versions.first()

        # Try to match by target industries/roles
        job_industry = job_data.get('industry', '').lower()
        job_title = job_data.get('title', '').lower()

        best_match = None
        best_score = 0

        for version in resume_versions:
            score = 0

            # Check industry match
            if job_industry:
                for target_industry in version.target_industries:
                    if job_industry in target_industry.lower():
                        score += 3

            # Check role match
            if job_title:
                for target_role in version.target_roles:
                    if any(word in job_title for word in target_role.lower().split()):
                        score += 2

            # Prefer primary resume as fallback
            if version.is_primary:
                score += 1

            # Consider success rate
            score += version.success_rate / 20  # Convert percentage to small bonus

            if score > best_score:
                best_score = score
                best_match = version

        return best_match or resume_versions.filter(is_primary=True).first() or resume_versions.first()

    def _submit_application_to_platform(self, job_data: Dict, profile: ExtendedUserProfile,
                                      cover_letter: str, resume_version: ResumeVersion) -> Dict[str, Any]:
        """
        Submit application to the job platform.

        In a real implementation, this would integrate with:
        - LinkedIn Easy Apply API
        - Indeed Apply API
        - Company ATS systems
        - Email applications
        """

        platform = job_data.get('platform', 'unknown')

        # Simulate different platform submissions
        if platform == 'linkedin':
            return self._submit_to_linkedin(job_data, profile, cover_letter, resume_version)
        elif platform == 'indeed':
            return self._submit_to_indeed(job_data, profile, cover_letter, resume_version)
        elif platform == 'company_website':
            return self._submit_to_company_website(job_data, profile, cover_letter, resume_version)
        else:
            # Generic application simulation
            return {
                'success': True,
                'method': 'email',
                'message': f'Application sent via email to {job_data.get("company", "company")}',
                'confirmation_id': f'APP_{timezone.now().strftime("%Y%m%d_%H%M%S")}'
            }

    def _submit_to_linkedin(self, job_data: Dict, profile: ExtendedUserProfile,
                           cover_letter: str, resume_version: ResumeVersion) -> Dict[str, Any]:
        """Simulate LinkedIn Easy Apply submission"""
        # In real implementation, use LinkedIn API
        return {
            'success': True,
            'method': 'linkedin_easy_apply',
            'message': 'Successfully submitted via LinkedIn Easy Apply',
            'confirmation_id': f'LI_{job_data["id"]}'
        }

    def _submit_to_indeed(self, job_data: Dict, profile: ExtendedUserProfile,
                         cover_letter: str, resume_version: ResumeVersion) -> Dict[str, Any]:
        """Simulate Indeed application submission"""
        # In real implementation, use Indeed API
        return {
            'success': True,
            'method': 'indeed_apply',
            'message': 'Successfully submitted via Indeed',
            'confirmation_id': f'IND_{job_data["id"]}'
        }

    def _submit_to_company_website(self, job_data: Dict, profile: ExtendedUserProfile,
                                  cover_letter: str, resume_version: ResumeVersion) -> Dict[str, Any]:
        """Simulate company website application submission"""
        # In real implementation, integrate with company ATS systems
        return {
            'success': True,
            'method': 'company_ats',
            'message': f'Successfully submitted to {job_data.get("company", "company")} careers page',
            'confirmation_id': f'CMP_{job_data["id"]}'
        }

    def _create_application_embedding(self, user: User, application: JobApplication,
                                    job_analysis: Dict[str, Any]):
        """Create user embedding for learning from this application"""
        try:
            # Create embedding content
            embedding_content = f"""
Application: {application.position} at {application.company}
Match Score: {application.match_score}
Skills Match: {job_analysis.get('skills_match', {}).get('match_percentage', 0)}%
Salary Compatible: {job_analysis.get('salary_match', {}).get('compatible', False)}
Application Method: {application.application_method}
Resume Used: {application.resume_version}
"""

            # In a real implementation, generate actual embeddings using an embedding model
            mock_embedding = [0.1] * 384  # Simulate 384-dimensional embedding

            UserEmbedding.objects.create(
                user=user,
                embedding_vector=mock_embedding,
                content=embedding_content,
                content_type='successful_application' if application.match_score >= 70 else 'application_attempt',
                confidence_score=min(application.match_score / 100, 1.0),
                source_application=application,
                source_metadata={
                    'job_analysis': job_analysis,
                    'application_date': application.applied_date.isoformat()
                }
            )

        except Exception as e:
            logger.warning(f"Failed to create application embedding for {user.username}: {str(e)}")


@method_decorator([csrf_exempt, login_required], name='dispatch')
class ApplicationStatusView(View):
    """API for updating and tracking job application statuses"""

    def post(self, request, application_id):
        """Update application status"""
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            notes = data.get('notes', '')
            employer_response = data.get('employer_response', '')

            if not new_status:
                return JsonResponse({
                    'success': False,
                    'error': 'Status is required'
                }, status=400)

            # Get application
            try:
                application = JobApplication.objects.get(
                    id=application_id,
                    user=request.user
                )
            except JobApplication.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Application not found'
                }, status=404)

            # Update application
            old_status = application.status
            application.status = new_status
            if notes:
                application.notes = notes
            if employer_response:
                application.employer_response = employer_response

            # Calculate response time if moving from 'applied' to any response
            if old_status == 'applied' and new_status != 'applied':
                application.calculate_response_time()

            application.save()

            # Create learning embedding if status indicates success or failure
            if new_status in ['offer_received', 'offer_accepted', 'rejected']:
                self._create_outcome_embedding(request.user, application)

            logger.info(f"Updated application status for {request.user.username}: {application.position} at {application.company} -> {new_status}")

            return JsonResponse({
                'success': True,
                'application': {
                    'id': str(application.id),
                    'status': application.status,
                    'last_update': application.last_status_update.isoformat(),
                    'response_time_days': application.response_time_days,
                    'is_successful': application.is_successful(),
                    'is_in_progress': application.is_in_progress()
                }
            })

        except Exception as e:
            logger.error(f"Error updating application status for {request.user.username}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    def _create_outcome_embedding(self, user: User, application: JobApplication):
        """Create embedding for learning from application outcome"""
        try:
            outcome_type = 'successful_application' if application.is_successful() else 'rejected_application'

            embedding_content = f"""
Outcome: {application.status}
Position: {application.position} at {application.company}
Match Score: {application.match_score}
Response Time: {application.response_time_days} days
Application Method: {application.application_method}
Resume Version: {application.resume_version}
Employer Response: {application.employer_response[:200] if application.employer_response else 'None'}
Notes: {application.notes[:200] if application.notes else 'None'}
"""

            # Generate mock embedding (in real implementation, use actual embedding model)
            mock_embedding = [0.1] * 384

            UserEmbedding.objects.create(
                user=user,
                embedding_vector=mock_embedding,
                content=embedding_content,
                content_type=outcome_type,
                confidence_score=0.9 if application.is_successful() else 0.7,
                source_application=application,
                source_metadata={
                    'outcome': application.status,
                    'response_time': application.response_time_days,
                    'final_update': application.last_status_update.isoformat()
                }
            )

        except Exception as e:
            logger.warning(f"Failed to create outcome embedding for {user.username}: {str(e)}")


# URL patterns helper
def get_job_application_urls():
    """Return URL patterns for job application system"""
    from django.urls import path

    return [
        path('api/jobs/opportunities/', JobOpportunityView.as_view(), name='job_opportunities'),
        path('api/jobs/quick-apply/', QuickApplyView.as_view(), name='quick_apply'),
        path('api/jobs/applications/<uuid:application_id>/status/', ApplicationStatusView.as_view(), name='application_status'),
    ]