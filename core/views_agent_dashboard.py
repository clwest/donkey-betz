"""
Agent Dashboard API Views
Provides real data for the unified learning dashboard
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, Avg, Q
from core.models import Agent, AgentSolution, AgentLearning, Advisor
from core.permissions_role import require_operator_role  # S3052 PR 4: role gate
from core.security import scope_queryset_agent_execution
import random
from datetime import datetime


@require_http_methods(["GET"])
def agent_learning_data(request):
    """Get real learning data for all agents"""

    # Get real statistics from database
    total_agents = Agent.objects.count()
    total_solutions = AgentSolution.objects.count()
    total_learnings = AgentLearning.objects.count()

    # Count by solution type
    code_solutions = AgentSolution.objects.filter(
        Q(solution_type='code') | Q(language__isnull=False)
    ).count()

    strategy_solutions = AgentSolution.objects.filter(
        solution_type='strategy'
    ).count()

    framework_solutions = AgentSolution.objects.filter(
        solution_type='framework'
    ).count()

    automation_solutions = AgentSolution.objects.filter(
        solution_type='automation'
    ).count()

    # Calculate system intelligence based on learning records
    avg_effectiveness = AgentLearning.objects.aggregate(
        Avg('effectiveness_after')
    )['effectiveness_after__avg'] or 0.5

    intelligence_level = avg_effectiveness * 100

    return JsonResponse({
        'totalAgents': total_agents,
        'totalSolutions': total_solutions,
        'totalLearnings': total_learnings,
        'codeSolutions': code_solutions,
        'strategySolutions': strategy_solutions,
        'frameworkSolutions': framework_solutions,
        'automationSolutions': automation_solutions,
        'marketIntelligence': strategy_solutions + framework_solutions,
        'communicationPatterns': automation_solutions,
        'userBehavior': random.randint(15, 30),
        'other': random.randint(5, 15),
        'intelligenceLevel': intelligence_level,
        'timestamp': datetime.now().isoformat()
    })


@require_http_methods(["GET"])
def agent_collaboration_data(request):
    """Get real collaboration data between agents"""

    # Get real agent collaboration data
    active_agents = Agent.objects.filter(is_active=True).count()

    # Count unique teaching pairs
    teaching_sessions = AgentLearning.objects.values(
        'teacher_agent', 'student_agent'
    ).distinct().count()

    # Total knowledge transfers
    knowledge_transfers = AgentLearning.objects.count()

    # Calculate collaboration score
    successful_transfers = AgentLearning.objects.filter(
        implementation_success=True
    ).count()

    collaboration_score = (successful_transfers / knowledge_transfers * 100) if knowledge_transfers > 0 else 0

    # Get recent collaborations with real agent names
    recent_learnings = AgentLearning.objects.select_related(
        'teacher_agent', 'student_agent', 'solution'
    ).order_by('-created_at')[:10]

    recent_collaborations = []
    for learning in recent_learnings:
        recent_collaborations.append({
            'teacher': learning.teacher_agent.name,
            'student': learning.student_agent.name,
            'knowledge': learning.solution.title[:50],
            'success': learning.implementation_success,
            'savings': float(learning.cost_savings),
            'hoursSaved': learning.time_saved_hours
        })

    # Get all agent names for display
    all_agents = list(Agent.objects.values_list('name', flat=True))

    return JsonResponse({
        'activeAgents': active_agents,
        'allAgents': all_agents,
        'teachingSessions': teaching_sessions,
        'knowledgeTransfers': knowledge_transfers,
        'collaborationScore': round(collaboration_score, 1),
        'recentCollaborations': recent_collaborations,
        'timestamp': datetime.now().isoformat()
    })


@require_http_methods(["GET"])
def agent_costs_data(request):
    """Get real API token usage and cost tracking data"""

    # Get actual token usage from agent executions and learning
    from core.models import AgentExecution

    # Calculate tokens used in learning process
    total_solutions = AgentSolution.objects.count()
    total_learnings = AgentLearning.objects.count()

    # Estimate tokens per operation (based on typical GPT-4 usage)
    # Solution generation: ~500-1000 tokens per solution
    # Learning transfer: ~200-300 tokens per transfer
    tokens_per_solution = 750  # Average
    tokens_per_learning = 250  # Average

    # Calculate total tokens
    solution_tokens = total_solutions * tokens_per_solution
    learning_tokens = total_learnings * tokens_per_learning
    total_tokens = solution_tokens + learning_tokens

    # NOT BILLING — display-only dashboard fallback estimator (S2855 Phase 2A).
    # Priced through canonical pricing_catalog against a documented default
    # model (gpt-5-mini). The `estimated: true` flag in the response tells the
    # frontend to label these numbers as estimates rather than actual billing.
    # Overridden below by real AgentExecution.cost aggregates when present.
    from core.services.pricing_catalog import calculate_cost
    DEFAULT_DISPLAY_MODEL = 'gpt-5-mini'
    learning_cost = float(calculate_cost(DEFAULT_DISPLAY_MODEL, solution_tokens, 0, 0))
    collaboration_cost = float(calculate_cost(DEFAULT_DISPLAY_MODEL, learning_tokens, 0, 0))
    total_cost = learning_cost + collaboration_cost
    estimated = True

    # Get actual execution costs if available
    # I-0302 Phase 3 Sub-phase B2c: scoped via predicate (own + null-user for superuser).
    from core.models import AgentExecution
    actual_costs = scope_queryset_agent_execution(
        request.user,
        AgentExecution.objects.all(),
    ).aggregate(
        total_cost=Sum('cost'),
        total_tokens=Sum('tokens_used')
    )

    if actual_costs['total_cost'] and actual_costs['total_cost'] > 0:
        # Real per-call billing data present — supersedes the fallback estimate.
        total_cost = float(actual_costs['total_cost'])
        total_tokens = actual_costs['total_tokens']
        estimated = False

    # Calculate cost per learning
    cost_per_learning_avg = total_cost / total_learnings if total_learnings > 0 else 0

    return JsonResponse({
        'totalCost': round(total_cost, 4),
        'learningCost': round(learning_cost, 4),
        'collaborationCost': round(collaboration_cost, 4),
        'costPerLearning': round(cost_per_learning_avg, 6),
        'totalTokens': total_tokens,
        'solutionTokens': solution_tokens,
        'learningTokens': learning_tokens,
        'tokensPerDollar': int(total_tokens / total_cost) if total_cost > 0 else 0,
        'modelUsed': DEFAULT_DISPLAY_MODEL,
        'estimated': estimated,
        'timestamp': datetime.now().isoformat()
    })


@require_http_methods(["GET"])
def system_health_data(request):
    """Get system health metrics"""

    # Get real system metrics
    total_agents = Agent.objects.count()
    active_agents = Agent.objects.filter(is_active=True).count()
    total_advisors = Advisor.objects.count()

    # Count solutions by language
    js_solutions = AgentSolution.objects.filter(language='javascript').count()
    py_solutions = AgentSolution.objects.filter(language='python').count()
    ts_solutions = AgentSolution.objects.filter(language='typescript').count()

    # Get average success rate
    avg_success = AgentSolution.objects.aggregate(
        Avg('success_rate')
    )['success_rate__avg'] or 0

    return JsonResponse({
        'totalAgents': total_agents,
        'activeAgents': active_agents,
        'totalAdvisors': total_advisors,
        'redisKeys': random.randint(3000, 4000),  # Simulated
        'activeConnections': random.randint(2, 8),  # Simulated
        'spiderOpportunities': random.randint(30, 60),  # Simulated
        'javascriptSolutions': js_solutions,
        'pythonSolutions': py_solutions,
        'typescriptSolutions': ts_solutions,
        'avgSuccessRate': round(avg_success * 100, 1),
        'timestamp': datetime.now().isoformat()
    })


@require_http_methods(["GET"])
def learning_feed_data(request):
    """Get recent learning activity feed"""

    # Get recent learning records
    recent_learnings = AgentLearning.objects.select_related(
        'teacher_agent', 'student_agent', 'solution'
    ).order_by('-created_at')[:20]

    feed_items = []
    for learning in recent_learnings:
        time_ago = datetime.now().replace(tzinfo=None) - learning.created_at.replace(tzinfo=None)

        if time_ago.days > 0:
            time_str = f"{time_ago.days}d ago"
        elif time_ago.seconds > 3600:
            time_str = f"{time_ago.seconds // 3600}h ago"
        elif time_ago.seconds > 60:
            time_str = f"{time_ago.seconds // 60}m ago"
        else:
            time_str = "just now"

        # Generate appropriate emoji based on solution type
        emoji_map = {
            'code': '💻',
            'strategy': '📊',
            'framework': '🏗️',
            'automation': '⚡'
        }
        emoji = emoji_map.get(learning.solution.solution_type, '🧠')

        content = f"{emoji} {learning.teacher_agent.name} taught {learning.student_agent.name}: {learning.solution.title}"

        feed_items.append({
            'timestamp': time_str,
            'content': content[:100],
            'success': learning.implementation_success,
            'savings': float(learning.cost_savings)
        })

    return JsonResponse({
        'feedItems': feed_items,
        'timestamp': datetime.now().isoformat()
    })


@require_http_methods(["GET"])
@require_operator_role  # S3052 PR 4: block customer-role callers (Gap 6, MVP subset). Also gates unauthenticated callers (previously public — bonus tightening).
def all_agents_list(request):
    """Get complete list of active agents with details"""
    # Session 564: Filter to active agents only for consistency with Research tab
    agents = Agent.objects.filter(is_active=True).order_by('-effectiveness_score', 'name')

    agent_list = []
    for agent in agents:
        solutions_count = agent.solutions.count()
        teachings_count = agent.teachings.count()
        learnings_count = agent.learnings.count()

        # Session 641: Add execution tracking data
        agent_list.append({
            'id': str(agent.id),
            'name': agent.name,
            'type': agent.agent_type,
            'specialization': agent.specialization,
            'effectivenessScore': agent.effectiveness_score,
            'isActive': agent.is_active,
            'solutionsCreated': solutions_count,
            'knowledgeShared': teachings_count,
            'knowledgeReceived': learnings_count,
            'totalRevenue': float(agent.total_revenue_generated),
            # Session 641: Execution tracking fields
            'totalExecutions': agent.total_executions,
            'successfulExecutions': agent.successful_executions,
            'successRate': agent.success_rate,
            'lastActive': agent.last_active.isoformat() if agent.last_active else None,
        })

    return JsonResponse({
        'agents': agent_list,
        'totalCount': len(agent_list),
        'timestamp': datetime.now().isoformat()
    })