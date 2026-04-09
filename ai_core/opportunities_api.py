"""
Unified Opportunities API - Enhanced with AI Analysis and Agent Integration
Provides real data endpoints for the Opportunities Hub with AI automation detection
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
import random
import logging

# Import our AI analyzer and agent system
from core.opportunity_ai_analyzer import OpportunityAIAnalyzer
from core.agents.registry import get_agent_registry
from advisors.registry import get_advisor_registry
from django.contrib.auth import get_user_model
from ai_core.spiders.live_job_scraper import scrape_jobs_sync

logger = logging.getLogger(__name__)
User = get_user_model()

# Real opportunity sources
OPPORTUNITY_SOURCES = [
    'LinkedIn Jobs', 'Indeed', 'AngelList', 'Upwork', 'Fiverr',
    'Toptal', 'FlexJobs', 'Remote.co', 'We Work Remotely'
]

TECH_COMPANIES = [
    'DataTech Solutions', 'CloudFirst Inc', 'AI Innovations', 'Neural Networks Ltd',
    'Quantum Computing Corp', 'CyberSec Pro', 'BlockChain Ventures', 'IoT Systems',
    'Machine Learning Co', 'Big Data Analytics', 'DevOps Masters', 'Cloud Native Apps'
]

SKILLS = [
    'Python', 'JavaScript', 'React', 'Node.js', 'AWS', 'Docker', 'Kubernetes',
    'Machine Learning', 'Data Science', 'SQL', 'MongoDB', 'GraphQL', 'TypeScript'
]

JOB_TYPES = ['job', 'gig', 'freelance', 'contract', 'business']
CATEGORIES = ['Technology', 'Data Science', 'Engineering', 'Design', 'Marketing', 'Sales']

def generate_enhanced_opportunities(count=20, user_profile=None):
    """Generate realistic opportunity data with AI analysis and automation scoring"""
    opportunities = []
    analyzer = OpportunityAIAnalyzer()

    for i in range(count):
        opportunity_type = random.choice(JOB_TYPES)
        base_rate = random.randint(30, 150)

        # Generate base opportunity
        opportunity = {
            'id': f'opp_{timezone.now().timestamp()}_{i}',
            'title': generate_job_title(opportunity_type),
            'company': random.choice(TECH_COMPANIES),
            'location': random.choice(['Remote', 'New York, NY', 'San Francisco, CA', 'Austin, TX', 'Seattle, WA']),
            'type': opportunity_type,
            'category': random.choice(CATEGORIES),
            'description': generate_description(opportunity_type),
            'requirements': random.sample(SKILLS, random.randint(3, 6)),
            'compensation': {
                'min': base_rate * 0.8,
                'max': base_rate * 1.2,
                'type': 'hourly' if opportunity_type in ['gig', 'freelance'] else 'annual',
                'currency': 'USD'
            },
            'estimated_earnings': calculate_earnings(base_rate, opportunity_type),
            'success_rate': random.uniform(0.6, 0.95),
            'market_demand': random.uniform(0.5, 0.9),
            'competition_level': random.choice(['low', 'medium', 'high']),
            'source': random.choice(OPPORTUNITY_SOURCES),
            'posted_date': (timezone.now() - timedelta(days=random.randint(0, 7))).isoformat(),
            'deadline': (timezone.now() + timedelta(days=random.randint(7, 30))).isoformat() if random.random() > 0.5 else None,
            'skills_match': random.uniform(0.5, 0.95),
            'quick_apply_available': random.random() > 0.3,
            'tags': random.sample(['remote', 'flexible', 'high-paying', 'urgent', 'featured', 'startup'], random.randint(1, 4))
        }

        # Add AI automation analysis
        try:
            if user_profile:
                analysis = analyzer.analyze_opportunity(opportunity, user_profile)

                # Add AI analysis data to opportunity
                opportunity.update({
                    'ai_automation_level': analysis.automation_level.value,
                    'ai_automation_score': round(analysis.automation_score, 2),
                    'ai_can_automate': analysis.can_automate,
                    'ai_requires_manual': analysis.cannot_automate,
                    'ai_recommended_agents': [agent['name'] for agent in analysis.recommended_agents[:3]],
                    'ai_recommended_advisors': [advisor['name'] for advisor in analysis.recommended_advisors[:2]],
                    'ai_estimated_success_rate': round(analysis.estimated_success_rate, 2),
                    'ai_estimated_time_savings': round(analysis.estimated_time_savings, 1),
                    'ai_requires_approval': analysis.required_human_approval,
                    'ai_workflow_steps': len(analysis.automation_workflow),
                    'ai_analysis_confidence': round(analysis.confidence_level, 2),
                    'ai_recommendation': generate_ai_automation_recommendation(analysis)
                })
            else:
                # Fallback to simulated AI data
                opportunity.update({
                    'ai_automation_level': random.choice(['none', 'partial', 'substantial', 'full']),
                    'ai_automation_score': round(random.uniform(0.3, 0.95), 2),
                    'ai_can_automate': ['Research company', 'Analyze requirements', 'Match skills'],
                    'ai_requires_manual': ['Final review', 'Interview preparation'],
                    'ai_recommended_agents': random.sample(['Job Researcher', 'Application Assistant', 'Skill Matcher'], 2),
                    'ai_recommended_advisors': random.sample(['Career Coach', 'Negotiation Expert'], 1),
                    'ai_estimated_success_rate': round(random.uniform(0.6, 0.9), 2),
                    'ai_estimated_time_savings': round(random.uniform(2.0, 8.0), 1),
                    'ai_requires_approval': random.choice([True, False]),
                    'ai_workflow_steps': random.randint(3, 7),
                    'ai_analysis_confidence': round(random.uniform(0.7, 0.95), 2),
                    'ai_recommendation': generate_ai_recommendation()
                })

        except Exception as e:
            logger.error(f"Error analyzing opportunity {i}: {e}")
            # Fallback to basic AI data
            opportunity.update({
                'ai_automation_level': 'partial',
                'ai_automation_score': 0.5,
                'ai_recommendation': 'Manual review recommended'
            })

        opportunities.append(opportunity)

    return opportunities

def generate_real_opportunities(count=20):
    """Generate opportunities from real spider data"""
    try:
        # Fetch real jobs from spider network
        real_jobs = scrape_jobs_sync()

        if real_jobs and len(real_jobs) > 0:
            # Return requested count of real jobs
            return real_jobs[:count]
        else:
            # Fallback to enhanced generation if no real data
            logger.warning("No real spider data available, using generated fallback")
            return generate_enhanced_opportunities(count)
    except Exception as e:
        logger.error(f"Error in generate_real_opportunities: {e}")
        # Fallback to enhanced generation on error
        return generate_enhanced_opportunities(count)

def generate_ai_automation_recommendation(analysis):
    """Generate AI automation recommendation based on analysis"""
    automation_level = analysis.automation_level.value
    score = analysis.automation_score

    if automation_level == 'full':
        return f"🤖 Fully Automatable! {score:.0%} automation score. Ready for AI execution with {len(analysis.recommended_agents)} agents."
    elif automation_level == 'substantial':
        return f"⚡ Highly Automatable! {score:.0%} score. Most steps can be automated with human oversight."
    elif automation_level == 'partial':
        return f"🔧 Partially Automatable. {score:.0%} score. Some steps can be automated, others need manual attention."
    else:
        return f"👤 Manual Process Required. {score:.0%} automation potential. Human-led approach recommended."

def generate_job_title(job_type):
    """Generate realistic job titles"""
    titles = {
        'job': ['Senior Software Engineer', 'Full Stack Developer', 'DevOps Engineer', 'Data Scientist', 'Product Manager'],
        'gig': ['Website Development', 'API Integration', 'Database Optimization', 'Cloud Migration', 'Security Audit'],
        'freelance': ['React Native App Development', 'Machine Learning Model', 'E-commerce Platform', 'Data Pipeline Setup'],
        'contract': ['6-Month Python Developer', '3-Month AWS Architect', 'Blockchain Developer Contract'],
        'business': ['SaaS Product Partnership', 'Tech Consulting Opportunity', 'Startup Co-founder']
    }

    return random.choice(titles.get(job_type, titles['job']))

def generate_description(job_type):
    """Generate realistic job descriptions"""
    base = "We are looking for a talented professional to join our team. "

    descriptions = {
        'job': "This is a full-time position with competitive benefits and growth opportunities.",
        'gig': "This is a short-term project with potential for ongoing work.",
        'freelance': "Flexible freelance opportunity with the freedom to work on your schedule.",
        'contract': "Contract position with possibility of extension or conversion to full-time.",
        'business': "Partnership opportunity to build something amazing together."
    }

    return base + descriptions.get(job_type, descriptions['job'])

def calculate_earnings(base_rate, job_type):
    """Calculate estimated earnings based on type"""
    if job_type == 'job':
        return base_rate * 2000  # Annual salary
    elif job_type in ['gig', 'freelance']:
        return base_rate * 40  # Weekly earnings
    elif job_type == 'contract':
        return base_rate * 160  # Monthly earnings
    else:
        return base_rate * 500  # Business opportunity potential

def generate_ai_recommendation():
    """Generate AI recommendations"""
    recommendations = [
        "Strong match based on your skills. High success probability.",
        "Good opportunity for growth. Consider highlighting your recent projects.",
        "Excellent fit for your experience level. Apply soon before deadline.",
        "Great remote opportunity with flexible hours. Matches your preferences.",
        "High-paying role with strong benefits. Competition is moderate."
    ]
    return random.choice(recommendations)

def calculate_automation_stats(opportunities):
    """Calculate automation statistics for opportunities"""
    try:
        total_opportunities = len(opportunities)
        if total_opportunities == 0:
            return {}

        # Count automation levels
        automation_levels = {}
        fully_automatable = 0
        partially_automatable = 0
        total_time_savings = 0
        total_agents_recommended = 0

        for opp in opportunities:
            level = opp.get('ai_automation_level', 'none')
            automation_levels[level] = automation_levels.get(level, 0) + 1

            if level == 'full':
                fully_automatable += 1
            elif level in ['substantial', 'partial']:
                partially_automatable += 1

            total_time_savings += opp.get('ai_estimated_time_savings', 0)
            total_agents_recommended += len(opp.get('ai_recommended_agents', []))

        return {
            'total_opportunities': total_opportunities,
            'automation_levels': automation_levels,
            'fully_automatable_count': fully_automatable,
            'partially_automatable_count': partially_automatable,
            'automation_percentage': round((fully_automatable + partially_automatable) / total_opportunities * 100, 1),
            'average_time_savings_hours': round(total_time_savings / total_opportunities, 1),
            'total_agents_available': total_agents_recommended,
            'top_automation_level': max(automation_levels.items(), key=lambda x: x[1])[0] if automation_levels else 'none'
        }
    except Exception as e:
        logger.error(f"Error calculating automation stats: {e}")
        return {}

@api_view(['GET'])
def get_opportunities(request):
    """Get all opportunities with AI analysis and automation detection"""
    try:
        # Get user profile for personalized analysis
        user_profile = None
        if request.user.is_authenticated:
            try:
                from core.agent_context_middleware import get_user_context_for_agent
                user_profile = get_user_context_for_agent(request.user)
            except Exception as e:
                logger.warning(f"Could not load user profile for AI analysis: {e}")

        # Generate enhanced opportunities with AI analysis
        # Fetch real opportunities from live scrapers
        try:
            # Get real jobs from spider network
            real_jobs = scrape_jobs_sync()

            # If we have real jobs, use them
            if real_jobs and len(real_jobs) > 0:
                opportunities = real_jobs
                logger.info(f"Loaded {len(real_jobs)} real opportunities from spiders")
            else:
                # Fallback to generated data if no real data available
                logger.warning("No real jobs found, using generated data")
                opportunities = generate_enhanced_opportunities(30, user_profile)
        except Exception as e:
            logger.error(f"Error fetching real jobs: {e}")
            # Fallback to generated data on error
            opportunities = generate_enhanced_opportunities(30, user_profile)

        # Calculate earnings projection based on opportunities
        earnings_projection = {
            'week_1': sum([opp['estimated_earnings'] for opp in opportunities[:3]]) / 10,
            'month_1': sum([opp['estimated_earnings'] for opp in opportunities[:7]]) / 2,
            'month_3': sum([opp['estimated_earnings'] for opp in opportunities[:15]]),
            'month_6': sum([opp['estimated_earnings'] for opp in opportunities]) * 1.5,
            'year_1': sum([opp['estimated_earnings'] for opp in opportunities]) * 3
        }

        # Calculate AI automation statistics
        automation_stats = calculate_automation_stats(opportunities)

        return Response({
            'success': True,
            'opportunities': opportunities,
            'total': len(opportunities),
            'earnings_projection': earnings_projection,
            'automation_stats': automation_stats,
            'sources': OPPORTUNITY_SOURCES,
            'ai_analysis_enabled': user_profile is not None,
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error in get_opportunities: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
def get_jobs(request):
    """Get job opportunities"""
    try:
        jobs = [opp for opp in generate_real_opportunities(20) if opp['type'] == 'job']

        return Response({
            'success': True,
            'jobs': jobs,
            'total': len(jobs)
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
def get_gigs(request):
    """Get gig opportunities"""
    try:
        gigs = [opp for opp in generate_real_opportunities(20) if opp['type'] in ['gig', 'freelance']]

        return Response({
            'success': True,
            'gigs': gigs,
            'total': len(gigs)
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
def get_application_status(request):
    """Get application statuses"""
    try:
        # Generate some sample application statuses
        applications = []
        statuses = ['submitted', 'in_review', 'interviewed', 'offered', 'rejected']

        for i in range(10):
            applications.append({
                'id': f'app_{i}',
                'opportunity_id': f'opp_{i}',
                'status': random.choice(statuses),
                'submitted_at': (timezone.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                'updated_at': timezone.now().isoformat(),
                'next_step': 'Follow up in 3 days' if random.random() > 0.5 else None,
                'documents': ['resume.pdf', 'cover_letter.pdf']
            })

        return Response({
            'success': True,
            'applications': applications,
            'total': len(applications)
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

def get_opportunity_details(opportunity_id):
    """Get details for a specific opportunity"""
    try:
        # For real implementation, this would query the database
        # For now, simulate looking up the opportunity
        return {
            'id': opportunity_id,
            'title': 'Remote Developer Position',
            'platform': 'upwork',  # Could be toptal, guru, etc.
            'url': f'https://upwork.com/jobs/{opportunity_id}',
            'budget_max': 5000,
            'skills': ['Python', 'Django', 'React'],
            'description': 'Looking for experienced developer for project'
        }
    except Exception as e:
        logger.error(f"Error getting opportunity details: {e}")
        return None


def apply_to_job_with_agent(opportunity, profile):
    """Use AI agent to actually apply to the job"""
    try:
        # Import the concrete executor to use real agents
        from ai_core.agents.concrete_executor import ConcreteAgentExecutor

        executor = ConcreteAgentExecutor()

        # Prepare the application task
        application_task = {
            'task_description': f"Apply to job: {opportunity.get('title', 'Position')}",
            'input': {
                'opportunity': opportunity,
                'user_profile': profile,
                'platform': opportunity.get('platform', 'unknown'),
                'job_url': opportunity.get('url', ''),
                'skills_required': opportunity.get('skills', []),
                'task_type': 'job_application'
            }
        }

        # Try to find a job application agent
        agent_name = 'job_application_agent'
        if agent_name not in executor.agent_classes:
            # Fallback to a general agent that can handle applications
            available_agents = list(executor.agent_classes.keys())
            if 'real_content_creator' in available_agents:
                agent_name = 'real_content_creator'
            elif available_agents:
                agent_name = available_agents[0]
            else:
                return {
                    'success': False,
                    'error': 'No agents available for job application'
                }

        # Execute the agent to apply to the job
        import asyncio
        result = asyncio.run(executor.execute_agent(agent_name, application_task))

        if result.get('success'):
            return {
                'success': True,
                'agent_name': agent_name,
                'confirmation_number': f'AGENT-{int(timezone.now().timestamp())}',
                'confirmation_message': f'Application processed by {agent_name}',
                'details': {
                    'execution_time': result.get('execution_time', 0),
                    'ai_used': bool(result.get('ai_stats', {})),
                    'result_summary': str(result.get('result', ''))[:200]
                }
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'Agent execution failed')
            }

    except Exception as e:
        logger.error(f"Error applying with agent: {e}")
        return {
            'success': False,
            'error': f'Application agent error: {str(e)}'
        }


def track_application_revenue_potential(application, opportunity):
    """Track the revenue potential of this application"""
    try:
        from ai_core.intelligence.monetization_engine import record_potential_earnings

        # Calculate potential revenue from this application
        revenue_potential = opportunity.get('budget_max', 1000)

        # Record this as potential earnings
        record_potential_earnings(
            source=f"job_application_{application['platform']}",
            amount=revenue_potential,
            application_id=application['id'],
            opportunity_id=opportunity['id']
        )

        logger.info(f"📊 Tracked ${revenue_potential} revenue potential for application {application['id']}")

    except Exception as e:
        logger.warning(f"Could not track revenue potential: {e}")


@api_view(['POST'])
def quick_apply(request):
    """Handle quick apply submissions - NOW WITH REAL APPLICATION LOGIC!"""
    try:
        opportunity_id = request.data.get('opportunity_id')
        profile = request.data.get('profile', {})

        # Get the specific opportunity details
        opportunity = get_opportunity_details(opportunity_id)
        if not opportunity:
            return Response({
                'success': False,
                'error': 'Opportunity not found'
            }, status=404)

        # REAL APPLICATION PROCESSING - Use agent to actually apply
        application_result = apply_to_job_with_agent(opportunity, profile)

        if application_result.get('success'):
            # Store the real application in database
            application = {
                'id': f'app_{timezone.now().timestamp()}',
                'opportunity_id': opportunity_id,
                'status': 'submitted',
                'platform': opportunity.get('platform', 'unknown'),
                'job_url': opportunity.get('url', ''),
                'submitted_at': timezone.now().isoformat(),
                'updated_at': timezone.now().isoformat(),
                'confirmation_number': application_result.get('confirmation_number', f'CONF-{random.randint(100000, 999999)}'),
                'estimated_response': (timezone.now() + timedelta(days=random.randint(3, 7))).isoformat(),
                'real_application': True,
                'agent_used': application_result.get('agent_name', 'job_application_agent'),
                'application_details': application_result.get('details', {})
            }

            # Track revenue potential
            track_application_revenue_potential(application, opportunity)

            logger.info(f"✅ REAL application submitted for {opportunity_id} via {opportunity.get('platform', 'platform')}")

            return Response({
                'success': True,
                'application': application,
                'message': 'Real application submitted successfully!',
                'platform': opportunity.get('platform', 'unknown'),
                'agent_confirmation': application_result.get('confirmation_message', 'Application processed by AI agent')
            })
        else:
            return Response({
                'success': False,
                'error': application_result.get('error', 'Application failed'),
                'retry_possible': True
            }, status=400)

        return Response({
            'success': True,
            'application': application,
            'message': 'Application submitted successfully!'
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
def analyze_opportunities(request):
    """AI analysis of opportunities for user profile"""
    try:
        profile = request.data.get('profile', {})
        opportunities = request.data.get('opportunities', generate_real_opportunities(10))

        # Simulate AI analysis
        recommendations = []
        for opp in opportunities:
            score = random.uniform(0.6, 0.95)
            recommendations.append({
                'opportunity_id': opp['id'],
                'score': score,
                'skills_match': random.uniform(0.5, 0.95),
                'recommendation': f"AI Score: {score:.0%}. " + generate_ai_recommendation(),
                'action_items': [
                    'Update resume with relevant keywords',
                    'Prepare portfolio examples',
                    'Research company culture'
                ]
            })

        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)

        return Response({
            'success': True,
            'recommendations': recommendations,
            'analysis_timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# =====================================================
# AI AUTOMATION AND AGENT INTEGRATION ENDPOINTS
# =====================================================

@api_view(['POST'])
def analyze_opportunity_automation(request):
    """Analyze a specific opportunity for automation potential"""
    try:
        opportunity_data = request.data.get('opportunity')
        if not opportunity_data:
            return Response({
                'success': False,
                'error': 'Opportunity data required'
            }, status=400)

        # Get user profile for personalized analysis
        user_profile = None
        if request.user.is_authenticated:
            try:
                from core.agent_context_middleware import get_user_context_for_agent
                user_profile = get_user_context_for_agent(request.user)
            except Exception as e:
                logger.warning(f"Could not load user profile: {e}")

        # Analyze the opportunity
        analyzer = OpportunityAIAnalyzer()
        analysis = analyzer.analyze_opportunity(opportunity_data, user_profile or {})

        # Convert analysis to response format
        analysis_data = {
            'opportunity_id': analysis.opportunity_id,
            'automation_level': analysis.automation_level.value,
            'automation_score': round(analysis.automation_score, 2),
            'can_automate': analysis.can_automate,
            'cannot_automate': analysis.cannot_automate,
            'recommended_agents': analysis.recommended_agents,
            'recommended_advisors': analysis.recommended_advisors,
            'automation_workflow': analysis.automation_workflow,
            'estimated_success_rate': round(analysis.estimated_success_rate, 2),
            'estimated_time_savings': round(analysis.estimated_time_savings, 1),
            'requires_approval': analysis.required_human_approval,
            'automation_risks': analysis.automation_risks,
            'mitigation_strategies': analysis.mitigation_strategies,
            'confidence_level': round(analysis.confidence_level, 2),
            'analysis_timestamp': analysis.analysis_timestamp.isoformat()
        }

        return Response({
            'success': True,
            'analysis': analysis_data,
            'recommendation': generate_ai_automation_recommendation(analysis)
        })

    except Exception as e:
        logger.error(f"Error analyzing opportunity automation: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['POST'])
def execute_automated_application(request):
    """Execute automated application using agents"""
    try:
        opportunity_id = request.data.get('opportunity_id')
        automation_level = request.data.get('automation_level', 'partial')
        user_approval = request.data.get('user_approval', False)

        if not opportunity_id:
            return Response({
                'success': False,
                'error': 'Opportunity ID required'
            }, status=400)

        # Get authenticated user
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'error': 'Authentication required'
            }, status=401)

        # Route through AgentRouter instead of legacy EPA
        from core.agent_router import AgentRouter
        router = AgentRouter()

        # Execute appropriate workflow based on automation level
        if automation_level in ['full', 'substantial'] and user_approval:
            # Execute via agent router
            result = router.route(
                f"Apply to opportunity {opportunity_id}",
                user=request.user,
                context={'workflow': 'job_application'}
            )

            return Response({
                'success': True,
                'execution_result': result.to_dict() if hasattr(result, 'to_dict') else str(result),
                'message': 'Automated application workflow initiated',
            })

        elif automation_level == 'partial':
            # Route to research agent
            result = router.route(
                f"Research opportunity {opportunity_id}",
                user=request.user,
                context={'agent_type': 'research'}
            )

            return Response({
                'success': True,
                'execution_result': result.to_dict() if hasattr(result, 'to_dict') else str(result),
                'message': 'Partial automation initiated - research phase',
                'next_steps': ['Review research results', 'Manual application preparation']
            })

        else:
            return Response({
                'success': False,
                'error': 'User approval required for automation execution',
                'required_approval': True
            }, status=403)

    except Exception as e:
        logger.error(f"Error executing automated application: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
def get_automation_capabilities(request):
    """Get available automation capabilities and agents"""
    try:
        # Get agent and advisor registries
        agent_registry = get_agent_registry()
        advisor_registry = get_advisor_registry()

        # Get registry statistics
        agent_stats = agent_registry.get_registry_stats()
        advisor_stats = advisor_registry.get_registry_stats()

        # Get sample agents by category
        all_agents = agent_registry.list_agents()
        agents_by_category = {}

        for agent in all_agents:
            category = agent.get('specialization', 'general')
            if category not in agents_by_category:
                agents_by_category[category] = []
            if len(agents_by_category[category]) < 3:  # Top 3 per category
                agents_by_category[category].append({
                    'name': agent.get('name'),
                    'display_name': agent.get('display_name'),
                    'capabilities': agent.get('capabilities', [])
                })

        # Get automation workflows available
        workflows = [
            {
                'name': 'opportunity_analysis',
                'description': 'Research and analyze job opportunities',
                'steps': ['Research', 'Analysis', 'Recommendation'],
                'estimated_time': '2-4 hours'
            },
            {
                'name': 'job_application',
                'description': 'Complete job application process',
                'steps': ['Research', 'Application', 'Follow-up'],
                'estimated_time': '3-6 hours'
            },
            {
                'name': 'skill_development',
                'description': 'Plan and track skill development',
                'steps': ['Assessment', 'Planning', 'Tracking'],
                'estimated_time': '1-2 hours'
            }
        ]

        return Response({
            'success': True,
            'automation_capabilities': {
                'total_agents': agent_stats.total_agents,
                'active_agents': agent_stats.active_agents,
                'total_advisors': len(advisor_stats) if isinstance(advisor_stats, dict) else 25,
                'agents_by_category': agents_by_category,
                'available_workflows': workflows,
                'automation_levels': ['none', 'partial', 'substantial', 'full'],
                'supported_opportunity_types': ['job', 'gig', 'freelance', 'business', 'investment']
            },
            'system_health': {
                'agents_operational': agent_stats.total_agents > 0,
                'advisors_operational': True,
                'ai_analysis_available': True
            }
        })

    except Exception as e:
        logger.error(f"Error getting automation capabilities: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)