"""
Co-Leadership API Views - Session 99

Simple, write-only API endpoints for human decisions and outcomes.

Endpoints:
- POST /api/coleadership/decisions/{id}/human_decision/ - Record human's final choice
- POST /api/coleadership/decisions/{id}/outcome/ - Record what actually happened
- GET /api/coleadership/stats/ - User's decision-making statistics

Philosophy: AI is advisory, human is ultimate decision-maker
"""

import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import CoLeadershipDecision, HumanDecision, DecisionOutcome
from .services import record_human_decision, record_outcome, get_user_decision_stats
from agents.models import UnifiedAgentTemplate

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_human_decision(request, decision_id):
    """
    Record the human's final decision.

    Session 99: Write-only endpoint for human decision commit.

    POST body:
    {
        "chosen_path_summary": "I'm going with option B because...",
        "justification": "Optional explanation",
        "is_override": false,
        "overridden_agent_id": null  // UUID of agent template if override
    }

    Returns:
    {
        "success": true,
        "message": "Decision recorded",
        "decision_id": "UUID",
        "frozen_at": "ISO timestamp"
    }
    """
    try:
        # Get decision (permission check via user ownership)
        decision = CoLeadershipDecision.objects.get(
            id=decision_id,
            initiated_by=request.user
        )

        # Check if already frozen
        if decision.is_frozen:
            return Response({
                'error': 'Decision already committed',
                'frozen_at': decision.frozen_at.isoformat()
            }, status=400)

        # Extract parameters
        chosen_path_summary = request.data.get('chosen_path_summary', '').strip()
        justification = request.data.get('justification', '').strip()
        is_override = request.data.get('is_override', False)
        overridden_agent_id = request.data.get('overridden_agent_id')

        # Validate required fields
        if not chosen_path_summary:
            return Response({
                'error': 'chosen_path_summary is required'
            }, status=400)

        # Get overridden agent if specified
        overridden_agent = None
        if is_override and overridden_agent_id:
            try:
                # Try UUID first
                overridden_agent = UnifiedAgentTemplate.objects.get(id=overridden_agent_id)
            except (UnifiedAgentTemplate.DoesNotExist, ValueError):
                # If UUID fails, try lookup by name (cto, coo, etc.)
                agent_name_map = {
                    'cto': 'CTOAgent',
                    'coo': 'COOAgent',
                }
                agent_name = agent_name_map.get(overridden_agent_id.lower())
                if agent_name:
                    try:
                        overridden_agent = UnifiedAgentTemplate.objects.get(name=agent_name)
                    except UnifiedAgentTemplate.DoesNotExist:
                        return Response({
                            'error': f'Agent template not found: {agent_name}'
                        }, status=404)
                else:
                    return Response({
                        'error': f'Invalid agent identifier: {overridden_agent_id}'
                    }, status=400)

        # Record human decision (this freezes the decision)
        human_decision = record_human_decision(
            decision=decision,
            chosen_path_summary=chosen_path_summary,
            justification=justification,
            is_override=is_override,
            overridden_agent=overridden_agent
        )

        logger.info(f"✅ Human decision recorded for {decision.title} by {request.user.username}")

        return Response({
            'success': True,
            'message': 'Decision recorded',
            'decision_id': str(decision.id),
            'frozen_at': decision.frozen_at.isoformat(),
            'is_override': is_override
        })

    except CoLeadershipDecision.DoesNotExist:
        return Response({
            'error': 'Decision not found or access denied'
        }, status=404)

    except Exception as e:
        logger.error(f"❌ Error saving human decision: {str(e)}")
        return Response({
            'error': 'Failed to save decision',
            'details': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_outcome(request, decision_id):
    """
    Record what actually happened after the decision.

    Session 99: Write-only endpoint for outcome logging.

    POST body:
    {
        "status": "success",  // "success" | "failure" | "mixed" | "pending"
        "outcome_summary": "What actually happened...",
        "attribution": "human",  // "ai" | "human" | "both" | "unknown"
        "metrics": {}  // Optional quantitative data
    }

    Returns:
    {
        "success": true,
        "message": "Outcome recorded",
        "decision_id": "UUID",
        "told_you_so_triggered": false,
        "told_you_so_message": ""
    }
    """
    try:
        # Get decision (permission check via user ownership)
        decision = CoLeadershipDecision.objects.get(
            id=decision_id,
            initiated_by=request.user
        )

        # Check if decision is frozen (must have human decision first)
        if not decision.is_frozen:
            return Response({
                'error': 'Cannot record outcome before human decision is committed'
            }, status=400)

        # Extract parameters
        status = request.data.get('status', 'pending')
        outcome_summary = request.data.get('outcome_summary', '').strip()
        attribution = request.data.get('attribution', 'unknown')
        metrics = request.data.get('metrics', {})

        # Validate status
        valid_statuses = ['pending', 'success', 'failure', 'mixed']
        if status not in valid_statuses:
            return Response({
                'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }, status=400)

        # Validate attribution
        valid_attributions = ['ai', 'human', 'both', 'unknown']
        if attribution not in valid_attributions:
            return Response({
                'error': f'Invalid attribution. Must be one of: {", ".join(valid_attributions)}'
            }, status=400)

        # Record outcome (this may trigger "I told you so" and reflection)
        outcome = record_outcome(
            decision=decision,
            status=status,
            outcome_summary=outcome_summary,
            metrics=metrics,
            attribution=attribution
        )

        logger.info(f"✅ Outcome recorded for {decision.title}: {status} (attribution: {attribution})")

        return Response({
            'success': True,
            'message': 'Outcome recorded',
            'decision_id': str(decision.id),
            'status': status,
            'attribution': attribution,
            'told_you_so_triggered': outcome.told_you_so_triggered,
            'told_you_so_message': outcome.told_you_so_message
        })

    except CoLeadershipDecision.DoesNotExist:
        return Response({
            'error': 'Decision not found or access denied'
        }, status=404)

    except Exception as e:
        logger.error(f"❌ Error saving outcome: {str(e)}")
        return Response({
            'error': 'Failed to save outcome',
            'details': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_stats(request):
    """
    Get user's decision-making statistics.

    Session 99: Simple stats endpoint.

    Returns:
    {
        "total_decisions": 14,
        "overrides": 6,
        "override_rate": 42.9,
        "ai_correct": 3,
        "human_correct": 5,
        "both_correct": 2,
        "pending": 4,
        "success_rate": 71.4,
        "avg_ai_confidence": 0.78
    }
    """
    try:
        stats = get_user_decision_stats(request.user)

        return Response({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        logger.error(f"❌ Error getting stats: {str(e)}")
        return Response({
            'error': 'Failed to get statistics',
            'details': str(e)
        }, status=500)
