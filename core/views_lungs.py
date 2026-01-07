"""
Session 702: LUNGS Service API Views

API endpoints for the LUNGS (Limits, Usage, Notifications, Governance, Spending) service.

Endpoints:
- GET /api/lungs/breathe/     - Run full breathing check
- GET /api/lungs/status/      - Get cached respiratory status
- GET /api/lungs/oxygen/      - Get remaining budget %
- GET /api/lungs/budgets/     - List all budgets
- POST /api/lungs/budgets/    - Create new budget
- PUT /api/lungs/budgets/<id>/ - Update budget
- GET /api/lungs/forecast/    - Get spending forecast
- GET /api/lungs/history/     - Get breath cycle history
- GET /api/lungs/can-breathe/ - Check if LLM call allowed
"""

import logging
from decimal import Decimal

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def lungs_breathe(request):
    """
    Run full breathing check - aggregate consumption and update statuses.

    GET /api/lungs/breathe/

    Returns comprehensive breathing status including all budgets,
    oxygen levels, alerts, and forecasts.
    """
    try:
        from core.services.lungs import get_lungs_monitor

        lungs = get_lungs_monitor()
        result = lungs.breathe()

        return Response({
            'success': True,
            **result
        })

    except Exception as e:
        logger.exception(f"LUNGS breathe error: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def lungs_status(request):
    """
    Get cached respiratory status (fast endpoint).

    GET /api/lungs/status/

    Returns current breathing vitals from cache without running
    a full aggregation.
    """
    try:
        from core.services.lungs import get_lungs_monitor

        lungs = get_lungs_monitor()
        vitals = lungs.get_vitals()

        return Response({
            'success': True,
            **vitals
        })

    except Exception as e:
        logger.exception(f"LUNGS status error: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def lungs_oxygen(request):
    """
    Get remaining budget percentage.

    GET /api/lungs/oxygen/
    GET /api/lungs/oxygen/?scope=provider&identifier=openai

    Query params:
    - scope: 'system' (default), 'provider', or 'agent'
    - identifier: Provider or agent name (required for non-system scope)
    """
    try:
        from core.services.lungs import get_lungs_monitor

        scope = request.query_params.get('scope', 'system')
        identifier = request.query_params.get('identifier', None)

        lungs = get_lungs_monitor()
        oxygen_level = lungs.check_oxygen_level(scope, identifier)

        # Determine status from oxygen level
        if oxygen_level >= 80:
            status_str = 'normal'
        elif oxygen_level >= 50:
            status_str = 'elevated'
        elif oxygen_level >= 20:
            status_str = 'hyperventilating'
        else:
            status_str = 'holding'

        return Response({
            'success': True,
            'scope': scope,
            'identifier': identifier,
            'oxygen_level': oxygen_level,
            'status': status_str,
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.exception(f"LUNGS oxygen error: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def lungs_budgets(request):
    """
    List all budgets or create a new one.

    GET /api/lungs/budgets/
    POST /api/lungs/budgets/
    """
    if request.method == 'GET':
        return _list_budgets(request)
    else:
        return _create_budget(request)


def _list_budgets(request):
    """List all budgets."""
    try:
        from core.models_lungs import Budget

        active_only = request.query_params.get('active_only', 'true').lower() == 'true'

        budgets = Budget.objects.all()
        if active_only:
            budgets = budgets.filter(is_active=True)

        budget_list = [
            {
                'id': str(budget.id),
                'name': budget.name,
                'scope': budget.scope,
                'scope_identifier': budget.scope_identifier,
                'period': budget.period,
                'token_limit': budget.token_limit,
                'cost_limit': float(budget.cost_limit) if budget.cost_limit else None,
                'warning_threshold': budget.warning_threshold,
                'critical_threshold': budget.critical_threshold,
                'is_active': budget.is_active,
                'enforce_hard_limit': budget.enforce_hard_limit,
                'created_at': budget.created_at.isoformat(),
                'updated_at': budget.updated_at.isoformat(),
            }
            for budget in budgets
        ]

        return Response({
            'success': True,
            'count': len(budget_list),
            'budgets': budget_list,
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.exception(f"LUNGS list budgets error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _create_budget(request):
    """Create a new budget."""
    try:
        from core.models_lungs import Budget

        data = request.data

        # Validate required fields
        required = ['name', 'scope', 'period']
        missing = [f for f in required if f not in data]
        if missing:
            return Response({
                'success': False,
                'error': f"Missing required fields: {missing}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create budget
        budget = Budget.objects.create(
            name=data['name'],
            scope=data['scope'],
            scope_identifier=data.get('scope_identifier', ''),
            period=data['period'],
            token_limit=data.get('token_limit'),
            cost_limit=Decimal(str(data['cost_limit'])) if data.get('cost_limit') else None,
            warning_threshold=data.get('warning_threshold', 0.8),
            critical_threshold=data.get('critical_threshold', 0.95),
            is_active=data.get('is_active', True),
            enforce_hard_limit=data.get('enforce_hard_limit', False),
        )

        return Response({
            'success': True,
            'budget': {
                'id': str(budget.id),
                'name': budget.name,
                'scope': budget.scope,
            },
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.exception(f"LUNGS create budget error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def lungs_budget_detail(request, budget_id):
    """
    Get, update, or delete a specific budget.

    GET /api/lungs/budgets/<id>/
    PUT /api/lungs/budgets/<id>/
    DELETE /api/lungs/budgets/<id>/
    """
    from core.models_lungs import Budget

    try:
        budget = Budget.objects.get(id=budget_id)
    except Budget.DoesNotExist:
        return Response({
            'success': False,
            'error': f"Budget {budget_id} not found"
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response({
            'success': True,
            'budget': {
                'id': str(budget.id),
                'name': budget.name,
                'scope': budget.scope,
                'scope_identifier': budget.scope_identifier,
                'period': budget.period,
                'token_limit': budget.token_limit,
                'cost_limit': float(budget.cost_limit) if budget.cost_limit else None,
                'warning_threshold': budget.warning_threshold,
                'critical_threshold': budget.critical_threshold,
                'is_active': budget.is_active,
                'enforce_hard_limit': budget.enforce_hard_limit,
                'created_at': budget.created_at.isoformat(),
                'updated_at': budget.updated_at.isoformat(),
            }
        })

    elif request.method == 'PUT':
        try:
            data = request.data

            # Update fields if provided
            if 'name' in data:
                budget.name = data['name']
            if 'cost_limit' in data:
                budget.cost_limit = Decimal(str(data['cost_limit'])) if data['cost_limit'] else None
            if 'token_limit' in data:
                budget.token_limit = data['token_limit']
            if 'warning_threshold' in data:
                budget.warning_threshold = data['warning_threshold']
            if 'critical_threshold' in data:
                budget.critical_threshold = data['critical_threshold']
            if 'is_active' in data:
                budget.is_active = data['is_active']
            if 'enforce_hard_limit' in data:
                budget.enforce_hard_limit = data['enforce_hard_limit']

            budget.save()

            return Response({
                'success': True,
                'message': f"Budget {budget.name} updated",
                'timestamp': timezone.now().isoformat()
            })

        except Exception as e:
            logger.exception(f"LUNGS update budget error: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'DELETE':
        try:
            budget_name = budget.name
            budget.delete()
            return Response({
                'success': True,
                'message': f"Budget {budget_name} deleted",
                'timestamp': timezone.now().isoformat()
            })
        except Exception as e:
            logger.exception(f"LUNGS delete budget error: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def lungs_forecast(request):
    """
    Get spending forecast for all active budgets.

    GET /api/lungs/forecast/
    GET /api/lungs/forecast/?scope=provider&identifier=openai

    Returns projected end-of-period usage and whether on pace to exceed.
    """
    try:
        from core.models_lungs import Budget
        from core.services.lungs import get_lungs_monitor

        scope = request.query_params.get('scope', None)
        identifier = request.query_params.get('identifier', None)

        lungs = get_lungs_monitor()

        # Filter budgets
        budgets = Budget.objects.filter(is_active=True)
        if scope:
            budgets = budgets.filter(scope=scope)
            if identifier:
                budgets = budgets.filter(scope_identifier=identifier)

        forecasts = []
        for budget in budgets:
            forecast = lungs.forecast_end_of_period(budget)
            forecasts.append({
                'budget_name': budget.name,
                'scope': budget.get_scope_key(),
                'period': budget.period,
                'limit': float(budget.cost_limit) if budget.cost_limit else budget.token_limit,
                **forecast
            })

        # Also get spending velocity
        velocity = lungs.get_spending_velocity(hours=24)

        return Response({
            'success': True,
            'forecasts': forecasts,
            'spending_velocity': velocity,
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.exception(f"LUNGS forecast error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def lungs_history(request):
    """
    Get breath cycle history.

    GET /api/lungs/history/
    GET /api/lungs/history/?hours=48&limit=50

    Query params:
    - hours: Hours to look back (default: 24)
    - limit: Max records to return (default: 100)
    """
    try:
        from core.services.lungs import get_lungs_monitor

        hours = int(request.query_params.get('hours', 24))
        limit = int(request.query_params.get('limit', 100))

        # Clamp values
        hours = max(1, min(168, hours))  # 1 hour to 1 week
        limit = max(1, min(500, limit))

        lungs = get_lungs_monitor()
        history = lungs.get_history(hours=hours, limit=limit)

        return Response({
            'success': True,
            'hours': hours,
            'count': len(history),
            'history': history,
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.exception(f"LUNGS history error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def lungs_can_breathe(request):
    """
    Check if an LLM call is allowed within budget.

    GET /api/lungs/can-breathe/
    GET /api/lungs/can-breathe/?provider=openai&agent=ResearchAgent

    Query params:
    - provider: LLM provider name
    - agent: Agent name
    - estimated_tokens: Estimated tokens for the call
    """
    try:
        from core.services.lungs import get_lungs_monitor

        provider = request.query_params.get('provider', None)
        agent = request.query_params.get('agent', None)
        estimated_tokens = int(request.query_params.get('estimated_tokens', 0))

        lungs = get_lungs_monitor()
        allowed, reason = lungs.can_breathe(
            provider=provider,
            agent=agent,
            estimated_tokens=estimated_tokens
        )

        return Response({
            'success': True,
            'can_breathe': allowed,
            'reason': reason,
            'provider': provider,
            'agent': agent,
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.exception(f"LUNGS can-breathe error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def lungs_is_breathing(request):
    """
    Quick alive check - are we within system budget?

    GET /api/lungs/alive/

    Lightweight endpoint for load balancer health checks.
    """
    try:
        from core.services.lungs import get_lungs_monitor

        lungs = get_lungs_monitor()
        is_breathing = lungs.is_breathing()
        oxygen = lungs.check_oxygen_level('system')

        return Response({
            'alive': is_breathing,
            'oxygen_level': oxygen,
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.exception(f"LUNGS alive check error: {e}")
        return Response({
            'alive': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
