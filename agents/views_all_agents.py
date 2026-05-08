"""
View to list all available agents from ConcreteAgentExecutor
"""

# PARTIAL — Session 1113 review (Session 1111 PR-B/PR-E queue).
# Classification: built but not URL-mounted.
# Why: imported by `agents/urls_deployment.py`, which is itself dark
# (never `include()`-d). No active runtime caller.
# Decision pending: same as `agents/urls_deployment.py`.
# See: docs/handoffs/SESSION_1111_DEEPER_REVIEW_MAP.md

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["GET"])
def list_all_concrete_agents(request):
    """
    List all 152 agents from ConcreteAgentExecutor
    """
    try:
        from ai_core.agents.concrete_executor import ConcreteAgentExecutor

        # Initialize the executor
        executor = ConcreteAgentExecutor()

        # Get all agent classes
        agent_list = []

        # Add all registered agent classes with proper metadata
        for agent_name, agent_class in executor.agent_classes.items():
            # Get agent metadata from the class docstring or attributes
            display_name = agent_name.replace('_', ' ').title()

            # Map internal names to user-friendly display names and descriptions
            agent_metadata = {
                'business_agent': {
                    'name': 'Business Agent',
                    'specialization': 'Business strategy and planning',
                    'description': 'Analyzes business requirements and creates strategic plans'
                },
                'market_research_specialist': {
                    'name': 'Market Research Specialist',
                    'specialization': 'Market analysis and insights',
                    'description': 'Conducts market research and competitive analysis'
                },
                'ml_pipeline': {
                    'name': 'ML Recommendation Engine',
                    'specialization': 'Machine learning architectures',
                    'description': 'Designs ML pipelines and recommendation systems'
                },
                'database_architect': {
                    'name': 'Database Architect',
                    'specialization': 'Database design and optimization',
                    'description': 'Designs optimal database schemas and query strategies'
                },
                'frontend_engineer': {
                    'name': 'Frontend Engineer',
                    'specialization': 'User interface development',
                    'description': 'Creates responsive and interactive user interfaces'
                },
                'api_gateway_architect': {
                    'name': 'API Developer',
                    'specialization': 'API design and integration',
                    'description': 'Designs RESTful APIs and microservice architectures'
                },
                'security_specialist': {
                    'name': 'Security Specialist',
                    'specialization': 'Application security',
                    'description': 'Implements security best practices and vulnerability assessments'
                },
                'devops_engineer': {
                    'name': 'DevOps Engineer',
                    'specialization': 'CI/CD and infrastructure',
                    'description': 'Sets up deployment pipelines and infrastructure automation'
                },
                'data_scientist': {
                    'name': 'Data Scientist',
                    'specialization': 'Data analysis and modeling',
                    'description': 'Performs data analysis and builds predictive models'
                },
                'ux_designer': {
                    'name': 'UX Designer',
                    'specialization': 'User experience design',
                    'description': 'Designs user workflows and interaction patterns'
                },
                'product_manager': {
                    'name': 'Product Manager',
                    'specialization': 'Product strategy',
                    'description': 'Defines product roadmap and feature prioritization'
                },
                'qa_engineer': {
                    'name': 'QA Engineer',
                    'specialization': 'Quality assurance',
                    'description': 'Designs test strategies and ensures quality standards'
                },
                'backend_engineer': {
                    'name': 'Backend Engineer',
                    'specialization': 'Server-side development',
                    'description': 'Builds scalable backend systems and services'
                },
                'blockchain_developer': {
                    'name': 'Blockchain Developer',
                    'specialization': 'Blockchain and smart contracts',
                    'description': 'Develops blockchain solutions and smart contracts'
                },
                'mobile_developer': {
                    'name': 'Mobile Developer',
                    'specialization': 'Mobile app development',
                    'description': 'Creates native and cross-platform mobile applications'
                },
                'cloud_architect': {
                    'name': 'Cloud Architect',
                    'specialization': 'Cloud infrastructure',
                    'description': 'Designs scalable cloud architectures and solutions'
                },
                'ai_ethicist': {
                    'name': 'AI Ethicist',
                    'specialization': 'Ethical AI practices',
                    'description': 'Ensures ethical considerations in AI implementations'
                },
                'performance_engineer': {
                    'name': 'Performance Engineer',
                    'specialization': 'Performance optimization',
                    'description': 'Optimizes application performance and scalability'
                },
                'content_strategist': {
                    'name': 'Content Strategist',
                    'specialization': 'Content planning',
                    'description': 'Develops content strategies and information architecture'
                },
                'seo_specialist': {
                    'name': 'SEO Specialist',
                    'specialization': 'Search engine optimization',
                    'description': 'Optimizes for search engine visibility and ranking'
                }
            }

            # Get metadata or use defaults
            metadata = agent_metadata.get(agent_name, {
                'name': display_name,
                'specialization': 'General AI capabilities',
                'description': f'Specialized agent for {display_name.lower()} tasks'
            })

            agent_list.append({
                'id': agent_name,
                'name': metadata['name'],
                'specialization': metadata['specialization'],
                'description': metadata['description'],
                'internal_name': agent_name
            })

        # Group by specialization
        categories = {}
        for agent in agent_list:
            spec = agent['specialization']
            if spec not in categories:
                categories[spec] = []
            categories[spec].append(agent)

        return JsonResponse({
            'success': True,
            'total_agents': len(agent_list),
            'agents': agent_list,
            'categories': categories,
            'specializations': list(categories.keys()),
            'message': f'Retrieved {len(agent_list)} agents from ConcreteAgentExecutor'
        })

    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)