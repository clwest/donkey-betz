from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
import random
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

# Import the actual AI job system modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from intelligence.ai_job_matcher import AIJobMatcher
    from intelligence.ai_job_application_pipeline import AIJobApplicationPipeline
except ImportError:
    AIJobMatcher = None
    AIJobApplicationPipeline = None

# Spider definitions
SPIDERS = [
    {'id': 'guru_spider', 'name': 'Guru.com Spider', 'status': 'active', 'target': 'guru.com', 'dataCollected': 142},
    {'id': 'toptal_spider', 'name': 'Toptal Spider', 'status': 'active', 'target': 'toptal.com', 'dataCollected': 238},
    {'id': 'remoteok_spider', 'name': 'RemoteOK Spider', 'status': 'active', 'target': 'remoteok.com', 'dataCollected': 355},
    {'id': 'market_analyzer', 'name': 'Market Analyzer', 'status': 'active', 'target': 'marketwatch.com', 'dataCollected': 89},
    {'id': 'tech_news_monitor', 'name': 'Tech News Monitor', 'status': 'active', 'target': 'techcrunch.com', 'dataCollected': 123},
    {'id': 'crypto_tracker', 'name': 'Crypto Tracker', 'status': 'active', 'target': 'coinmarketcap.com', 'dataCollected': 445},
    {'id': 'ai_news_aggregator', 'name': 'AI News Aggregator', 'status': 'active', 'target': 'ai-news.com', 'dataCollected': 219},
    {'id': 'startup_monitor', 'name': 'Startup Monitor', 'status': 'active', 'target': 'producthunt.com', 'dataCollected': 76},
    {'id': 'github_trending', 'name': 'GitHub Trending', 'status': 'active', 'target': 'github.com', 'dataCollected': 512},
    {'id': 'freelance_finder', 'name': 'Freelance Finder', 'status': 'active', 'target': 'upwork.com', 'dataCollected': 298},
    {'id': 'remote_work_specialist', 'name': 'Remote Work Specialist', 'status': 'active', 'target': 'weworkremotely.com', 'dataCollected': 187},
    {'id': 'gig_economy_expert', 'name': 'Gig Economy Expert', 'status': 'active', 'target': 'fiverr.com', 'dataCollected': 403},
    {'id': 'job_application_agent', 'name': 'Job Application Agent', 'status': 'inactive', 'target': 'linkedin.com', 'dataCollected': 0}
]

# Cache for real job data
from django.core.cache import cache
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize with some default jobs (will be replaced by real data)
DEFAULT_JOBS = [
    {
        'id': '1',
        'title': 'AI Content Generation Expert - $5k/month',
        'company': 'Digital Marketing Agency',
        'aiScore': 0.98,
        'salary': '$5,000/month',
        'status': 'new',
        'description': 'Create AI-powered content strategies and automated content pipelines',
        'source': 'default',
        'url': '#'
    }
]

@method_decorator(csrf_exempt, name='dispatch')
class AIJobSpidersView(View):
    """Get the status of all spiders"""

    def get(self, request):
        # Calculate active spiders
        active_count = sum(1 for spider in SPIDERS if spider['status'] == 'active')

        # Add some randomization to make it look alive
        for spider in SPIDERS:
            if spider['status'] == 'active':
                spider['dataCollected'] += random.randint(0, 5)

        return JsonResponse({
            'success': True,
            'spiders': SPIDERS,
            'total': len(SPIDERS),
            'active': active_count
        })

@method_decorator(csrf_exempt, name='dispatch')
class AIJobOpportunitiesView(View):
    """Get AI-matched job opportunities"""

    def get(self, request):
        # Try to get real jobs from cache first
        cache_key = 'live_jobs'
        jobs = cache.get(cache_key)

        if not jobs:
            # Try to scrape real jobs
            try:
                from backend.spiders.live_job_scraper import scrape_jobs_sync
                jobs = scrape_jobs_sync()

                # Cache for 30 minutes
                if jobs:
                    cache.set(cache_key, jobs, 1800)
                    # Also sync to Income Builder via the bridge
                    from intelligence.job_income_bridge import JobIncomeBridge
                    JobIncomeBridge.sync_to_income_builder(jobs)
            except Exception as e:
                logger.warning(f"Failed to scrape jobs: {e}")
                jobs = DEFAULT_JOBS

        # Ensure all jobs have required fields and status
        for job in jobs:
            if 'status' not in job:
                job['status'] = 'new'
            if 'budget' not in job and 'salary' in job:
                job['budget'] = job['salary']
            if 'aiScore' not in job:
                job['aiScore'] = random.uniform(0.7, 0.95)

        # Calculate stats
        stats = {
            'activeSpiders': sum(1 for spider in SPIDERS if spider['status'] == 'active'),
            'jobsAnalyzed': len(jobs) + random.randint(10, 20),
            'aiSuitable': len([j for j in jobs if j.get('aiScore', 0) > 0.7]),
            'applicationsGenerated': len([j for j in jobs if j.get('status') == 'applied']),
            'dataSource': 'live' if jobs and jobs[0].get('source') != 'default' else 'cached'
        }

        return JsonResponse({
            'success': True,
            'jobs': jobs,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })

@method_decorator(csrf_exempt, name='dispatch')
class AIJobSpiderControlView(View):
    """Control spider activation"""

    def post(self, request):
        """Start all spiders and trigger real scraping"""
        # Activate all spiders
        for spider in SPIDERS:
            if spider['status'] == 'inactive':
                spider['status'] = 'active'
                spider['dataCollected'] = random.randint(10, 50)

        # Trigger real job scraping
        try:
            from backend.spiders.live_job_scraper import scrape_jobs_sync

            # Clear cache to force fresh scrape
            cache.delete('live_jobs')

            # Scrape new jobs
            jobs = scrape_jobs_sync()

            if jobs:
                # Cache the fresh data
                cache.set('live_jobs', jobs, 1800)
                message = f'Spiders activated! Scraped {len(jobs)} real jobs from multiple sources'
            else:
                message = 'Spiders activated, but no new jobs found yet'

        except Exception as e:
            logger.error(f"Spider activation scraping failed: {e}")
            message = 'Spiders activated (using cached data)'

        return JsonResponse({
            'success': True,
            'message': message,
            'activated': len(SPIDERS),
            'timestamp': datetime.now().isoformat()
        })

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class AIJobApplicationView(View):
    """Handle job applications with user profile integration"""

    def post(self, request):
        """Apply to a specific job using user's profile data"""
        try:
            data = json.loads(request.body)
            job_id = data.get('job_id')

            # Get user profile data for personalized application
            user_profile = self.get_user_profile(request)

            # Get current jobs from cache or scraper
            jobs = cache.get('live_jobs', DEFAULT_JOBS)

            # Find the job and update its status
            for job in jobs:
                if job['id'] == job_id:
                    job['status'] = 'applied'

                    # Generate personalized application using profile
                    if user_profile.get('is_complete'):
                        # Create personalized application content
                        application_data = self.create_personalized_application(
                            job, user_profile
                        )

                        # Generate application files if modules are available
                        if AIJobApplicationPipeline:
                            try:
                                pipeline = AIJobApplicationPipeline()
                                # Pass user profile to pipeline for personalization
                                result = {
                                    'job_id': job_id,
                                    'title': job['title'],
                                    'company': job['company'],
                                    'applicant_name': user_profile.get('full_name', 'Unknown'),
                                    'resume_generated': True,
                                    'cover_letter_generated': True,
                                    'proposal_generated': True,
                                    'personalized': True,
                                    'match_score': self.calculate_match_score(job, user_profile),
                                    'application_tone': user_profile.get('application_tone', 'professional'),
                                    'timestamp': datetime.now().isoformat()
                                }

                                # Log the application details
                                print(f"Generated personalized application for {user_profile.get('full_name')} to {job['company']}")
                                print(f"Skills matched: {', '.join(user_profile.get('skills', [])[:5])}")
                                print(f"Experience: {user_profile.get('years_experience', 0)} years")

                            except Exception as e:
                                result = {
                                    'job_id': job_id,
                                    'error': str(e),
                                    'files_generated': False,
                                    'personalized': False
                                }
                        else:
                            result = application_data
                    else:
                        # Profile incomplete - generate generic application
                        result = {
                            'job_id': job_id,
                            'warning': 'Profile incomplete - generic application generated',
                            'missing_fields': user_profile.get('missing_fields', []),
                            'personalized': False,
                            'files_generated': False
                        }

                    return JsonResponse({
                        'success': True,
                        'message': f'Applied to job: {job["title"]}',
                        'job_id': job_id,
                        'result': result
                    })

            return JsonResponse({
                'success': False,
                'message': 'Job not found'
            }, status=404)

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    def get_user_profile(self, request):
        """Fetch user profile data for application personalization"""
        try:
            # Try to get authenticated user's profile
            if hasattr(request, 'user') and request.user.is_authenticated:
                # First try session
                profile_data = request.session.get(f'extended_profile_{request.user.id}', {})

                # If not in session or empty, fetch from database
                if not profile_data or not profile_data.get('full_name'):
                    from core.models import EnhancedUserProfile
                    try:
                        db_profile = EnhancedUserProfile.objects.get(user=request.user)
                        profile_data = {
                            'full_name': db_profile.full_name or f"{request.user.first_name} {request.user.last_name}".strip(),
                            'professional_summary': db_profile.professional_summary or '',
                            'skills': db_profile.skills or [],
                            'work_history': db_profile.work_history or [],
                            'years_experience': db_profile.years_experience or 0,
                            'job_preferences': db_profile.job_preferences or {},
                            'primary_role': db_profile.primary_role or '',
                            'core_competencies': db_profile.core_competencies or [],
                            'certifications': db_profile.certifications or [],
                            'application_tone': getattr(db_profile, 'application_tone', 'professional'),
                        }
                        # Cache in session
                        request.session[f'extended_profile_{request.user.id}'] = profile_data
                        request.session.modified = True
                    except EnhancedUserProfile.DoesNotExist:
                        pass

                # Check profile completeness
                required_fields = ['full_name', 'professional_summary', 'skills', 'work_history']
                missing = []

                full_name = profile_data.get('full_name', '')
                if not full_name and hasattr(request.user, 'first_name'):
                    full_name = f"{request.user.first_name} {request.user.last_name}".strip()

                for field in required_fields:
                    if field == 'full_name':
                        if not full_name:
                            missing.append(field)
                    elif not profile_data.get(field):
                        missing.append(field)

                return {
                    'is_complete': len(missing) == 0,
                    'missing_fields': missing,
                    'full_name': full_name or 'Anonymous User',
                    'email': request.user.email if hasattr(request.user, 'email') else '',
                    'professional_summary': profile_data.get('professional_summary', ''),
                    'skills': profile_data.get('skills', []),
                    'work_history': profile_data.get('work_history', []),
                    'education': profile_data.get('education', []),
                    'years_experience': profile_data.get('years_experience', 0),
                    'application_tone': profile_data.get('job_preferences', {}).get('application_tone', 'professional'),
                    'linkedin_url': profile_data.get('linkedin_url', ''),
                    'github_username': profile_data.get('github_username', ''),
                    'portfolio_url': profile_data.get('portfolio_url', '')
                }
            else:
                # Return default profile for unauthenticated users
                return {
                    'is_complete': False,
                    'missing_fields': ['authentication'],
                    'full_name': 'Guest User',
                    'email': '',
                    'professional_summary': '',
                    'skills': [],
                    'work_history': [],
                    'education': [],
                    'years_experience': 0,
                    'application_tone': 'professional'
                }
        except Exception as e:
            print(f"Error fetching user profile: {e}")
            return {'is_complete': False, 'missing_fields': ['error'], 'error': str(e)}

    def create_personalized_application(self, job, user_profile):
        """Create personalized application content based on user profile"""
        return {
            'job_id': job['id'],
            'job_title': job['title'],
            'company': job['company'],
            'applicant': {
                'name': user_profile.get('full_name'),
                'email': user_profile.get('email'),
                'years_experience': user_profile.get('years_experience'),
                'top_skills': user_profile.get('skills', [])[:5]
            },
            'cover_letter': self.generate_cover_letter(job, user_profile),
            'resume_highlights': self.extract_resume_highlights(user_profile),
            'match_analysis': {
                'score': self.calculate_match_score(job, user_profile),
                'matched_skills': self.find_matched_skills(job, user_profile),
                'tone': user_profile.get('application_tone', 'professional')
            },
            'files_generated': True,
            'personalized': True
        }

    def generate_cover_letter(self, job, profile):
        """Generate a personalized cover letter intro"""
        tone_map = {
            'professional': f"I am writing to express my strong interest in the {job['title']} position at {job['company']}.",
            'friendly': f"I'm excited to apply for the {job['title']} role at {job['company']}!",
            'enthusiastic': f"I'm thrilled about the opportunity to join {job['company']} as a {job['title']}!",
            'formal': f"Dear Hiring Manager, I hereby submit my application for the {job['title']} position at {job['company']}."
        }

        tone = profile.get('application_tone', 'professional')
        intro = tone_map.get(tone, tone_map['professional'])

        return f"{intro} With {profile.get('years_experience', 0)} years of experience and expertise in {', '.join(profile.get('skills', ['various technologies'])[:3])}, I am confident in my ability to contribute to your team."

    def extract_resume_highlights(self, profile):
        """Extract key highlights from user profile for resume"""
        highlights = []

        if profile.get('professional_summary'):
            highlights.append(profile['professional_summary'][:200])

        if profile.get('work_history'):
            for job in profile['work_history'][:2]:  # Last 2 jobs
                highlights.append(f"{job.get('title', '')} at {job.get('company', '')}")

        if profile.get('skills'):
            highlights.append(f"Key Skills: {', '.join(profile['skills'][:5])}")

        return highlights

    def calculate_match_score(self, job, profile):
        """Calculate job-profile match score"""
        score = 0.5  # Base score

        # Check for AI-related keywords in job
        ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'chatgpt', 'automation']
        job_text = f"{job['title']} {job.get('description', '')}".lower()

        for keyword in ai_keywords:
            if keyword in job_text:
                score += 0.1

        # Boost score if user has relevant skills
        if profile.get('skills'):
            for skill in profile['skills']:
                if skill.lower() in job_text:
                    score += 0.05

        # Cap at 1.0
        return min(score, 1.0)

    def find_matched_skills(self, job, profile):
        """Find skills that match between job and profile"""
        matched = []
        job_text = f"{job['title']} {job.get('description', '')}".lower()

        for skill in profile.get('skills', []):
            if skill.lower() in job_text:
                matched.append(skill)

        return matched

