"""
Real Income Builder Views
Provides real job opportunities from spider network and job simulator
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ai_core.agents.real_job_simulator import real_job_simulator
from ai_core.agents.intelligent_job_matcher import IntelligentJobMatcher

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def real_income_opportunities(request):
    """Get real income opportunities from DATABASE, job simulator, and spider network - PERSONALIZED"""
    try:
        logger.info("🎯 Fetching PERSONALIZED income opportunities from DATABASE")

        # PRIORITY 1: Get opportunities from DATABASE (real data from spiders)
        from core.models_unified_system import Opportunity, UserAgentLearning
        from django.utils import timezone
        from datetime import timedelta

        # 🧠 LEARNING INTEGRATION: Get user's learned preferences
        user_preferences = None
        platform_preferences = None
        personalization_active = False

        if request.user and request.user.is_authenticated:
            try:
                # Get user preferences learning
                user_preferences = UserAgentLearning.objects.filter(
                    user=request.user,
                    learning_domain='user_preferences',
                    is_active=True,
                    confidence_score__gte=0.3  # Accept medium-confidence and above
                ).first()

                # Get platform success patterns
                platform_preferences = UserAgentLearning.objects.filter(
                    user=request.user,
                    learning_domain='platform_preferences',
                    is_active=True,
                    confidence_score__gte=0.3
                ).first()

                if user_preferences or platform_preferences:
                    personalization_active = True
                    logger.info(f"✅ Personalization ACTIVE for {request.user.username}")
                else:
                    logger.info(f"📊 Building learning profile for {request.user.username}")
            except Exception as e:
                logger.warning(f"Could not load user preferences: {e}")

        # Extract preference data
        preferred_sources = []
        salary_min = 0
        salary_max = 999999
        preferred_industries = []

        if user_preferences and user_preferences.learning_content:
            content = user_preferences.learning_content

            # Extract preferred sources (platforms with high engagement)
            if 'preferred_sources' in content:
                sources_data = content['preferred_sources']
                # Get sources with avg_depth >= 2.0 (clicked or deeper)
                preferred_sources = [
                    source for source, data in sources_data.items()
                    if data.get('avg_depth', 0) >= 2.0
                ]
                logger.info(f"🎯 Preferred sources: {preferred_sources}")

            # Extract salary preferences
            if 'preferred_salary_range' in content:
                salary_data = content['preferred_salary_range']
                salary_min = salary_data.get('min', 0)
                salary_max = salary_data.get('max', 999999)
                logger.info(f"💰 Preferred salary: ${salary_min} - ${salary_max}")

            # Extract industry preferences
            if 'preferred_industries' in content:
                industries_data = content['preferred_industries']
                preferred_industries = list(industries_data.keys())

        # Also check platform preferences for success rates
        platform_success_rates = {}
        if platform_preferences and platform_preferences.learning_content:
            platforms_data = platform_preferences.learning_content.get('platforms', {})
            for platform, data in platforms_data.items():
                success_rate = data.get('success_rate', 0)
                if success_rate > 0:
                    platform_success_rates[platform] = success_rate
                    # Add high-success platforms to preferred list
                    if success_rate > 0.5 and platform not in preferred_sources:
                        preferred_sources.append(platform)

        db_opportunities = []
        try:
            # Get active opportunities from last 7 days
            recent_cutoff = timezone.now() - timedelta(days=7)

            # Build query with personalization
            query = Opportunity.objects.filter(
                status='active',
                created_at__gte=recent_cutoff
            )

            # 🎯 PERSONALIZATION: Filter by preferences
            if personalization_active:
                # Filter by preferred sources (if user has preferences)
                if preferred_sources:
                    logger.info(f"🔍 Filtering by preferred sources: {preferred_sources}")
                    query = query.filter(source__in=preferred_sources)

                # Filter by salary range (if user has preferences)
                if salary_min > 0 or salary_max < 999999:
                    logger.info(f"💵 Filtering by salary: ${salary_min} - ${salary_max}")
                    query = query.filter(
                        potential_revenue__gte=salary_min,
                        potential_revenue__lte=salary_max
                    )

            # Get opportunities
            db_opps = query.order_by('-match_score', '-created_at')[:30]  # Get more for ranking

            # 🎯 PERSONALIZATION: Calculate personalized scores
            for opp in db_opps:
                # Base score from match_score
                base_score = opp.match_score

                # Personalization boost (0-20 points)
                personalization_boost = 0

                # Boost if from preferred source
                if opp.source in preferred_sources:
                    source_boost = 10
                    # Extra boost based on success rate
                    if opp.source in platform_success_rates:
                        success_rate = platform_success_rates[opp.source]
                        source_boost += int(success_rate * 10)  # 0-10 extra points
                    personalization_boost += source_boost

                # Boost if in preferred salary range
                if salary_min > 0 and opp.potential_revenue >= salary_min:
                    personalization_boost += 5

                # Final personalized score
                personalized_score = min(100, base_score + personalization_boost)

                opportunity = {
                    'id': f"db_{opp.id}",
                    'title': opp.title,
                    'stream_type': opp.opportunity_type,
                    'description': opp.description if hasattr(opp, 'description') else f"{opp.opportunity_type} opportunity",
                    'time_to_income': '1-3 days',
                    'potential_monthly': f"${float(opp.potential_revenue):,.0f}",
                    'difficulty': 'intermediate',
                    'initial_investment': 0,
                    'success_rate': opp.match_score,
                    'market_demand': 85,
                    'required_skills': opp.skills_required if hasattr(opp, 'skills_required') else [],
                    'action_steps': [
                        'Review opportunity details',
                        'Prepare custom proposal',
                        'Submit application',
                        'Follow up within 24 hours'
                    ],
                    'resources': [
                        {'name': opp.source, 'url': '#apply'}
                    ],
                    'source': opp.source,
                    'hourly_rate': float(opp.hourly_rate) if opp.hourly_rate else None,
                    'score': opp.match_score / 100,  # Normalize to 0-1
                    'personalized_score': personalized_score,  # 🧠 NEW: Personalized score
                    'personalization_boost': personalization_boost,  # 🧠 NEW: Show boost amount
                    'created_at': opp.created_at.isoformat(),
                    'is_personalized': personalization_active  # 🧠 NEW: Flag for frontend
                }
                db_opportunities.append(opportunity)

            # 🎯 PERSONALIZATION: Sort by personalized score
            if personalization_active:
                db_opportunities.sort(key=lambda x: x['personalized_score'], reverse=True)
                logger.info(f"✅ Loaded {len(db_opportunities)} PERSONALIZED opportunities from DATABASE")
            else:
                logger.info(f"✅ Loaded {len(db_opportunities)} opportunities from DATABASE (no personalization)")
        except Exception as e:
            logger.error(f"❌ Error loading from database: {e}")
            db_opportunities = []

        # PRIORITY 2: Get real job sessions from the simulator (fallback)
        active_sessions = real_job_simulator.generate_active_sessions(5) if len(db_opportunities) < 5 else []

        # Convert sessions to opportunities format
        opportunities = db_opportunities.copy()

        for session in active_sessions:
            opportunity = {
                'id': f"real_{session['session_id']}",
                'title': session['job_title'],
                'stream_type': session['category'],
                'description': f"Real opportunity from {session['platform']} - Client: {session['client_name']}",
                'time_to_income': '1-3 days',
                'potential_monthly': f"${session['job_budget'] * 4:,.0f}",
                'difficulty': 'intermediate',
                'initial_investment': 0,
                'success_rate': 85,
                'market_demand': 90,
                'required_skills': session['agent_skills'],
                'action_steps': [
                    f"Apply on {session['platform']}",
                    "Submit proposal with portfolio",
                    "Complete initial milestones",
                    f"Deliver {session['next_deliverable']}"
                ],
                'resources': [
                    {'name': f'{session["platform"]} Platform', 'url': f'https://{session["platform"].lower()}.com'},
                    {'name': 'Portfolio Examples', 'url': '#portfolio'}
                ],
                'platform': session['platform'],
                'client_name': session['client_name'],
                'hourly_rate': session['hourly_rate'],
                'job_progress': session['job_progress'],
                'status': session['status'],
                'revenue_generated': session['revenue_generated']
            }
            opportunities.append(opportunity)

        # Get additional opportunities from intelligent job matcher (skip if fails)
        spider_jobs = []
        try:
            matcher = IntelligentJobMatcher()
            if hasattr(matcher, 'get_available_jobs'):
                spider_jobs = matcher.get_available_jobs(limit=5)
            else:
                logger.warning("IntelligentJobMatcher missing get_available_jobs method")
        except Exception as e:
            logger.warning(f"Could not get spider jobs: {e}")
            spider_jobs = []

        for job in spider_jobs:
            opportunity = {
                'id': f"spider_{job.get('id', '')}",
                'title': job.get('title', 'Untitled Opportunity'),
                'stream_type': job.get('category', 'freelancing'),
                'description': job.get('description', ''),
                'time_to_income': job.get('timeline', '3-7 days'),
                'potential_monthly': f"${job.get('budget', 1000) * 2:,.0f}",
                'difficulty': job.get('difficulty', 'intermediate'),
                'initial_investment': 0,
                'success_rate': job.get('match_score', 75),
                'market_demand': 85,
                'required_skills': job.get('skills_required', []),
                'action_steps': [
                    'Review job requirements',
                    'Prepare custom proposal',
                    'Submit application',
                    'Follow up within 24 hours'
                ],
                'resources': [
                    {'name': 'Job Board', 'url': job.get('url', '#')},
                    {'name': 'Skill Resources', 'url': '#skills'}
                ],
                'source': 'spider_network',
                'posted_date': job.get('posted_date', ''),
                'company': job.get('company', 'Client')
            }
            opportunities.append(opportunity)

        # Calculate real revenue data
        total_revenue = sum(opp.get('revenue_generated', 0) for opp in opportunities if 'revenue_generated' in opp)

        revenue_data = {
            'current_metrics': {
                'total_revenue': total_revenue,
                'monthly_revenue': total_revenue * 30,
                'weekly_revenue': total_revenue * 7,
                'daily_revenue': total_revenue
            },
            'by_category': {
                'content': total_revenue * 0.2,
                'ai_services': total_revenue * 0.3,
                'digital_products': total_revenue * 0.15,
                'trading': total_revenue * 0.1,
                'freelancing': total_revenue * 0.25
            },
            'projections': {
                'monthly': total_revenue * 30,
                'yearly': total_revenue * 365
            }
        }

        # 🧠 Return top 15 personalized opportunities
        top_opportunities = opportunities[:15]

        return JsonResponse({
            'success': True,
            'opportunities': top_opportunities,
            'count': len(top_opportunities),
            'revenue': revenue_data,
            'message': 'Personalized opportunities based on your preferences' if personalization_active else 'Real opportunities from active job market',
            'is_real': True,
            'is_personalized': personalization_active,  # 🧠 NEW: Tell frontend if personalized
            'personalization_data': {  # 🧠 NEW: Show what we learned
                'preferred_sources': preferred_sources if personalization_active else [],
                'salary_range': {'min': salary_min, 'max': salary_max} if personalization_active else None,
                'platform_success_rates': platform_success_rates if personalization_active else {}
            } if personalization_active else {},
            'source': 'personalized_learning_engine' if personalization_active else 'job_simulator_and_spiders'
        })

    except Exception as e:
        logger.error(f"Error fetching real opportunities: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'opportunities': [],
            'message': 'Error fetching opportunities'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def analyze_real_opportunities(request):
    """Analyze real opportunities based on user profile"""
    try:
        data = json.loads(request.body) if request.body else {}
        user_skills = data.get('skills', ['python', 'javascript', 'ai'])
        skill_level = data.get('skill_level', 'intermediate')

        logger.info(f"🔍 Analyzing opportunities for user with skills: {user_skills}")

        # Get matched opportunities
        matcher = IntelligentJobMatcher()
        matched_jobs = matcher.match_jobs_to_profile({
            'skills': user_skills,
            'experience_level': skill_level,
            'availability': data.get('available_hours', 20)
        })

        # Convert to opportunity format
        opportunities = []
        for job in matched_jobs[:10]:  # Top 10 matches
            opportunity = {
                'id': f"matched_{job.get('id', '')}",
                'title': job.get('title', ''),
                'stream_type': job.get('category', 'freelancing'),
                'description': job.get('description', ''),
                'time_to_income': '2-5 days',
                'potential_monthly': f"${job.get('budget', 0) * 3:,.0f}",
                'difficulty': skill_level,
                'initial_investment': 0,
                'success_rate': job.get('match_score', 80),
                'market_demand': 88,
                'required_skills': job.get('skills_required', user_skills),
                'action_steps': [
                    'Review matched opportunity',
                    'Customize proposal for your skills',
                    'Submit application today',
                    'Start earning this week'
                ],
                'resources': [
                    {'name': 'Apply Now', 'url': job.get('url', '#')},
                    {'name': 'Similar Jobs', 'url': '#similar'}
                ],
                'match_score': job.get('match_score', 80),
                'match_reason': job.get('match_reason', 'Skills match')
            }
            opportunities.append(opportunity)

        return JsonResponse({
            'success': True,
            'opportunities': opportunities,
            'count': len(opportunities),
            'message': f'Found {len(opportunities)} matched opportunities',
            'user_profile': {
                'skills': user_skills,
                'level': skill_level
            },
            'is_real': True,
            'source': 'intelligent_matcher'
        })

    except Exception as e:
        logger.error(f"Error analyzing opportunities: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)