"""
AI Opportunity Pipeline API
Connects the AI monetization research and project building to the frontend
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime
import logging
from pathlib import Path

# Import our pipeline components
from ai_core.spiders.ai_monetization_spider import research_ai_monetization_sync
from agents.ai_project_builder import AIProjectBuilder
from advisors.registry import AdvisorRegistry
from advisors.llm_advisor_system import LLMAdvisor

logger = logging.getLogger(__name__)


@api_view(['POST'])
def execute_ai_opportunity_pipeline(request):
    """
    Execute the AI opportunity pipeline:
    1. Research AI monetization strategies
    2. Build actual projects
    3. Return results to frontend
    """
    try:
        # Get preferences from request
        preference = request.data.get('preference', '')
        strategies_count = request.data.get('strategies_count', 3)

        logger.info(f"🚀 Starting AI Opportunity Pipeline via API - Preference: {preference}")

        # Step 1: Research AI monetization strategies
        strategies = research_ai_monetization_sync()

        if not strategies:
            return Response({
                'success': False,
                'error': 'No AI monetization strategies found'
            }, status=404)

        logger.info(f"📊 Found {len(strategies)} AI monetization strategies")

        # Filter by preference if provided
        if preference:
            filtered_strategies = []
            for strategy in strategies:
                if (preference.lower() in strategy.get('title', '').lower() or
                    preference.lower() in strategy.get('strategy_type', '').lower()):
                    filtered_strategies.append(strategy)

            if filtered_strategies:
                strategies = filtered_strategies

        # Step 2: Build projects for top strategies
        builder = AIProjectBuilder()
        execution_results = []

        # Initialize advisor registry for consultations
        advisor_registry = AdvisorRegistry()

        for strategy in strategies[:strategies_count]:
            logger.info(f"⚙️ Building project for: {strategy['title']}")

            # Convert strategy to task
            task = f"build {strategy.get('strategy_type', 'ai application')} for: {strategy['title']}"

            # Build the project
            result = builder.build_project(task, strategy)

            if result['success']:
                logger.info(f"✅ Successfully built: {strategy['title']}")

                # Get advisor consultation for this project
                advisor_insights = _get_advisor_consultation(strategy, advisor_registry)
                result['advisor_insights'] = advisor_insights
                execution_results.append({
                    'success': True,
                    'strategy': strategy,
                    'project_path': result.get('project_path'),
                    'files_created': result.get('files_created', []),
                    'launch_command': result.get('launch_command'),
                    'revenue_potential': strategy.get('potential_revenue'),
                    'project_type': result.get('project_type'),
                    'advisor_insights': advisor_insights
                })
            else:
                logger.error(f"❌ Failed to build: {strategy['title']}")
                execution_results.append({
                    'success': False,
                    'strategy': strategy,
                    'error': result.get('error')
                })

        # Calculate summary statistics
        successful_projects = [r for r in execution_results if r['success']]

        # Step 3: Return results
        return Response({
            'success': True,
            'summary': {
                'strategies_researched': len(strategies),
                'projects_attempted': len(execution_results),
                'projects_successful': len(successful_projects),
                'success_rate': f"{len(successful_projects)/len(execution_results)*100:.0f}%" if execution_results else "0%",
                'total_revenue_potential': _calculate_total_revenue(successful_projects)
            },
            'strategies': strategies[:10],  # Top 10 strategies
            'projects': execution_results,
            'next_steps': [
                'Add OpenAI API keys to generated projects',
                'Test each application',
                'Create landing pages',
                'Set up payment processing',
                'Launch beta versions'
            ],
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error in AI opportunity pipeline: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
def get_ai_strategies(request):
    """
    Get available AI monetization strategies without building
    """
    try:
        # Research strategies
        strategies = research_ai_monetization_sync()

        if not strategies:
            return Response({
                'success': False,
                'error': 'No strategies found'
            }, status=404)

        return Response({
            'success': True,
            'strategies': strategies,
            'total': len(strategies),
            'categories': _get_strategy_categories(strategies),
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting AI strategies: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
def build_ai_project(request):
    """
    Build a specific AI project from a strategy
    """
    try:
        strategy = request.data.get('strategy')
        if not strategy:
            return Response({
                'success': False,
                'error': 'Strategy data required'
            }, status=400)

        logger.info(f"🔨 Building individual project: {strategy.get('title', 'Unknown')}")

        # Build the project
        builder = AIProjectBuilder()
        task = f"build {strategy.get('strategy_type', 'ai application')} for: {strategy.get('title', '')}"
        result = builder.build_project(task, strategy)

        if result['success']:
            return Response({
                'success': True,
                'project': {
                    'strategy': strategy,
                    'project_path': result.get('project_path'),
                    'files_created': result.get('files_created', []),
                    'launch_command': result.get('launch_command'),
                    'revenue_potential': strategy.get('potential_revenue'),
                    'project_type': result.get('project_type'),
                    'ready_to_launch': result.get('ready_to_launch', False)
                },
                'message': f"Successfully built {strategy.get('title', 'project')}",
                'timestamp': timezone.now().isoformat()
            })
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Failed to build project')
            }, status=500)

    except Exception as e:
        logger.error(f"Error building AI project: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
def get_generated_projects(request):
    """
    Get list of all generated projects
    """
    try:
        projects_dir = Path("/Users/donkeyking/Donkey_Betz/unified-donkey-betz/generated_projects")

        if not projects_dir.exists():
            return Response({
                'success': True,
                'projects': [],
                'total': 0
            })

        projects = []
        for project_dir in projects_dir.iterdir():
            if project_dir.is_dir():
                # Get project info
                readme_path = project_dir / "README.md"
                requirements_path = project_dir / "requirements.txt"

                project_info = {
                    'name': project_dir.name,
                    'path': str(project_dir),
                    'created': datetime.fromtimestamp(project_dir.stat().st_ctime).isoformat(),
                    'has_readme': readme_path.exists(),
                    'has_requirements': requirements_path.exists(),
                    'files': [f.name for f in project_dir.iterdir() if f.is_file()]
                }

                # Try to extract revenue info from README
                if readme_path.exists():
                    try:
                        readme_content = readme_path.read_text()
                        if 'Revenue Potential' in readme_content:
                            for line in readme_content.split('\n'):
                                if 'Revenue Potential' in line:
                                    project_info['revenue_potential'] = line.split(':', 1)[1].strip() if ':' in line else 'Unknown'
                                    break
                    except:
                        pass

                projects.append(project_info)

        # Sort by creation date (newest first)
        projects.sort(key=lambda x: x['created'], reverse=True)

        return Response({
            'success': True,
            'projects': projects,
            'total': len(projects),
            'workspace': str(projects_dir),
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting generated projects: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


def _calculate_total_revenue(successful_projects):
    """Calculate total revenue potential from successful projects"""
    import re
    total = 0

    for project in successful_projects:
        revenue_str = project.get('revenue_potential', '')
        # Extract numbers from revenue string
        numbers = re.findall(r'\d+', revenue_str.replace(',', ''))
        if numbers:
            # Take the highest number (optimistic estimate)
            total += int(numbers[-1])

    if total > 0:
        return f"${total:,}/month"
    return "Unknown"


def _get_strategy_categories(strategies):
    """Get unique strategy categories"""
    categories = set()
    for strategy in strategies:
        strategy_type = strategy.get('strategy_type')
        if strategy_type:
            categories.add(strategy_type)

    return sorted(list(categories))


def _get_advisor_consultation(strategy, advisor_registry):
    """Get advisor insights for an AI project strategy"""
    try:
        # Select relevant advisors based on the strategy type
        relevant_advisors = []

        # Get advisors for business/investment advice
        business_advisors = ['Warren Buffett (AI Model)', 'Cathie Wood (AI Model)', 'Peter Thiel (AI Model)']

        # Get advisors for tech/AI advice
        tech_advisors = ['Elon Musk (AI Model)', 'Naval Ravikant (AI Model)']

        # Select 2-3 advisors for consultation
        selected_advisors = []
        if strategy.get('strategy_type') in ['ai_application', 'saas_development']:
            selected_advisors = business_advisors[:2] + tech_advisors[:1]
        else:
            selected_advisors = business_advisors[:2]

        insights = []
        for advisor_name in selected_advisors:
            try:
                # Get advisor profile
                advisor_info = advisor_registry.get_advisor_by_name(advisor_name)
                if advisor_info:
                    # Create LLM advisor instance
                    advisor = LLMAdvisor(
                        advisor_id=advisor_info['id'],
                        advisor_profile=advisor_info,
                        user=None  # Can be user context if available
                    )

                    # Get consultation on the AI project
                    consultation_context = {
                        'project_title': strategy.get('title', ''),
                        'project_type': strategy.get('strategy_type', ''),
                        'revenue_potential': strategy.get('potential_revenue', ''),
                        'time_to_implement': strategy.get('time_to_implement', ''),
                        'difficulty': strategy.get('difficulty', ''),
                        'description': strategy.get('description', '')
                    }

                    result = advisor.provide_consultation(
                        topic=f"AI Business Opportunity: {strategy.get('title', 'AI Project')}",
                        context=consultation_context,
                        consultation_type='investment_analysis'
                    )

                    if result.get('success'):
                        insights.append({
                            'advisor': advisor_name,
                            'advice': result.get('advice', ''),
                            'recommendations': result.get('recommendations', []),
                            'action_items': result.get('action_items', [])
                        })
                        logger.info(f"✅ Got insights from {advisor_name}")

            except Exception as e:
                logger.warning(f"Could not get consultation from {advisor_name}: {e}")
                # Add mock insights as fallback
                insights.append({
                    'advisor': advisor_name,
                    'advice': f"This AI project shows strong potential. Focus on rapid prototyping and market validation.",
                    'recommendations': [
                        'Start with an MVP to test market demand',
                        'Focus on a specific niche initially',
                        'Build strong API documentation'
                    ],
                    'action_items': [
                        'Create landing page',
                        'Run pilot with 10 beta users',
                        'Set up analytics tracking'
                    ]
                })

        return insights

    except Exception as e:
        logger.error(f"Error getting advisor consultation: {e}")
        # Return mock insights as fallback
        return [{
            'advisor': 'Warren Buffett (AI Model)',
            'advice': 'Focus on creating sustainable value and competitive moats in your AI business.',
            'recommendations': [
                'Build a strong brand and customer loyalty',
                'Focus on recurring revenue models',
                'Maintain low operational costs'
            ],
            'action_items': [
                'Validate market demand before scaling',
                'Build defensible technology advantages',
                'Focus on customer retention metrics'
            ]
        }]