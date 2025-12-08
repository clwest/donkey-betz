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
from core.models.agents_registry import UnifiedAgentTemplate

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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_boardroom_meeting(request):
    """
    Start an executive boardroom meeting via REST API.

    Session 100: Part 13 - Standalone boardroom meeting endpoint for Flutter client.

    POST body:
    {
        "topic": "Q4 Product Launch Strategy",
        "project_id": "uuid-optional",
        "participants": ["CTOAgent", "CFOAgent", "MarketingAgent"]
    }

    Returns complete meeting data including:
    - Agent perspectives
    - Meeting summary
    - Decisions made
    - Action items with ownership
    - session_id and decision_id for follow-up actions
    """
    try:
        from agents.meeting_coordinator_agent import MeetingCoordinatorAgent
        from content.models import AISession, CreativeProject
        from core.models.agents_registry import UnifiedAgentTemplate
        from .services import start_decision, log_agent_recommendation
        import uuid as uuid_module

        # Extract parameters
        topic = request.data.get('topic', '').strip()
        project_id = request.data.get('project_id')
        participants = request.data.get('participants', ['CTOAgent', 'COOAgent'])

        # Validate required fields
        if not topic:
            return Response({
                'error': 'topic is required'
            }, status=400)

        if not participants or not isinstance(participants, list):
            return Response({
                'error': 'participants must be a non-empty list of agent names'
            }, status=400)

        # Get project if provided
        project = None
        if project_id:
            try:
                # Validate UUID format
                project_uuid = uuid_module.UUID(project_id)
                # Session 173: CreativeProject uses 'id' not 'project_id'
                project = CreativeProject.objects.get(
                    id=project_uuid,
                    user=request.user
                )
            except (CreativeProject.DoesNotExist, ValueError, TypeError):
                # If UUID is invalid or project doesn't exist, just skip project linkage
                logger.warning(f"Invalid or non-existent project_id: {project_id}")
                pass

        # Start the meeting
        coordinator = MeetingCoordinatorAgent(user=request.user)
        meeting_result = coordinator.start_meeting(
            topic=topic,
            project_id=project_id,
            participants=participants
        )

        # Check if meeting was successful
        if meeting_result.get('status') != 'complete':
            return Response({
                'error': 'Meeting failed to complete',
                'details': meeting_result.get('message', 'Unknown error')
            }, status=500)

        # Create a boardroom AISession to store results
        session = AISession.objects.create(
            user=request.user,
            title=f"Boardroom: {topic[:100]}",
            session_type='boardroom',
            meeting_topic=topic,
            project=project,
            participants=meeting_result.get('participants', []),
            meeting_summary=meeting_result.get('summary', ''),
            decisions=meeting_result.get('decisions', []),
            action_items=meeting_result.get('action_items', []),
            agent_responses=meeting_result.get('agent_responses', {}),
            is_active=False,  # Meetings are one-shot
            conversation_transcript=[{
                'role': 'system',
                'content': f"Executive meeting conducted: {topic}"
            }]
        )

        logger.info(f"✅ Created boardroom session: {session.session_id}")

        # Create co-leadership decision + log agent recommendations
        decision = start_decision(
            project=project,
            session=session,
            user=request.user,
            title=topic,
            description=meeting_result.get('summary', '')
        )

        # Log each agent's recommendation
        agent_responses = meeting_result.get('agent_responses', {})
        for agent_name, response_text in agent_responses.items():
            try:
                # Find agent template
                agent_template = UnifiedAgentTemplate.objects.get(name=agent_name)

                # Simple stance inference (can enhance later)
                stance = 'neutral'  # Default
                if 'recommend' in response_text.lower() or 'support' in response_text.lower():
                    stance = 'support'
                elif 'concern' in response_text.lower() or 'risk' in response_text.lower():
                    stance = 'concern'
                elif 'alternative' in response_text.lower():
                    stance = 'alternative'

                # Log recommendation
                log_agent_recommendation(
                    decision=decision,
                    agent_template=agent_template,
                    payload_dict={
                        'stance': stance,
                        'summary': response_text[:200],  # First 200 chars
                        'recommendation': response_text,
                        'risks': '',  # Can extract later
                        'alternative_paths': [],
                        'confidence': None,  # Can add later
                        'time_horizon': ''
                    }
                )
            except UnifiedAgentTemplate.DoesNotExist:
                logger.warning(f"Agent template not found: {agent_name}")
                continue

        logger.info(f"✅ Boardroom meeting complete: {topic}")

        # Return complete meeting data (matching existing format)
        return Response({
            'success': True,
            'topic': topic,
            'project_id': str(project.id) if project else None,
            'participants': meeting_result.get('participants', []),
            'agent_responses': meeting_result.get('agent_responses', {}),
            'summary': meeting_result.get('summary', ''),
            'decisions': meeting_result.get('decisions', []),
            'action_items': meeting_result.get('action_items', []),
            'met_at': meeting_result.get('met_at'),
            'session_id': str(session.session_id),
            'decision_id': str(decision.id)
        })

    except Exception as e:
        logger.error(f"❌ Error starting boardroom meeting: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'error': 'Failed to start boardroom meeting',
            'details': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_decisions(request):
    """
    Get all co-leadership decisions for the authenticated user.

    Session 108: General decision list endpoint for mobile UI.

    Query params:
    - limit: Number of results (default: 20, max: 100)
    - offset: Skip first N results (default: 0)

    Returns list of decisions with summary info (not full detail).
    """
    try:
        # Get query params
        limit = min(int(request.GET.get('limit', 20)), 100)
        offset = int(request.GET.get('offset', 0))

        # Get all user's decisions
        decisions = CoLeadershipDecision.objects.filter(
            initiated_by=request.user
        ).select_related(
            'human_decision',
            'outcome',
            'project',
            'session'
        ).order_by('-created_at')[offset:offset + limit]

        # Build response
        decisions_list = []
        for decision in decisions:
            # Determine status
            if not decision.is_frozen:
                status = 'pending_decision'
            elif not decision.has_outcome:
                status = 'pending_outcome'
            else:
                status = 'complete'

            # Get outcome attribution if exists
            outcome_attribution = None
            if hasattr(decision, 'outcome'):
                outcome_attribution = decision.outcome.attribution

            decision_data = {
                'id': str(decision.id),
                'title': decision.title,
                'meeting_topic': decision.title,  # Alias for consistency
                'created_at': decision.created_at.isoformat(),
                'frozen_at': decision.frozen_at.isoformat() if decision.frozen_at else None,
                'has_human_decision': decision.is_frozen,
                'has_outcome': decision.has_outcome,
                'status': status,
                'outcome_attribution': outcome_attribution,
                'project_id': str(decision.project.id) if decision.project else None,
                'project_name': decision.project.name if decision.project else None
            }

            decisions_list.append(decision_data)

        return Response({
            'success': True,
            'decisions': decisions_list,
            'total': len(decisions_list),
            'limit': limit,
            'offset': offset
        })

    except Exception as e:
        logger.error(f"❌ Error listing decisions: {str(e)}")
        return Response({
            'error': 'Failed to list decisions',
            'details': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_decision_detail(request, decision_id):
    """
    Get complete details for a single co-leadership decision.

    Session 108: Decision detail endpoint for mobile UI.

    Returns:
    - Decision metadata
    - All agent recommendations
    - Human decision (if exists)
    - Outcome (if exists)
    - "I told you so" message (if exists)
    """
    try:
        # Get decision (permission check via user ownership)
        decision = CoLeadershipDecision.objects.select_related(
            'human_decision',
            'outcome',
            'project',
            'session'
        ).prefetch_related(
            'recommendations__agent_template'
        ).get(
            id=decision_id,
            initiated_by=request.user
        )

        # Build decision data
        decision_data = {
            'id': str(decision.id),
            'title': decision.title,
            'description': decision.description,
            'created_at': decision.created_at.isoformat(),
            'frozen_at': decision.frozen_at.isoformat() if decision.frozen_at else None,
            'is_frozen': decision.is_frozen,
            'has_outcome': decision.has_outcome,
            'project': None,
            'session_id': str(decision.session.session_id) if decision.session else None
        }

        # Add project info if exists
        if decision.project:
            decision_data['project'] = {
                'id': str(decision.project.id),
                'name': decision.project.name
            }

        # Add agent recommendations
        recommendations_list = []
        for rec in decision.recommendations.all():
            recommendations_list.append({
                'id': rec.id,
                'agent_name': rec.agent_template.display_name,
                'agent_id': rec.agent_template.name,
                'stance': rec.stance,
                'stance_display': rec.get_stance_display(),
                'summary': rec.summary,
                'recommendation_text': rec.recommendation_text,
                'risk_analysis': rec.risk_analysis,
                'alternative_paths': rec.alternative_paths,
                'confidence': rec.confidence,
                'time_horizon': rec.time_horizon,
                'created_at': rec.created_at.isoformat()
            })

        decision_data['agent_recommendations'] = recommendations_list

        # Add human decision if exists
        if hasattr(decision, 'human_decision'):
            hd = decision.human_decision
            decision_data['human_decision'] = {
                'chosen_path_summary': hd.chosen_path_summary,
                'justification': hd.justification,
                'is_override': hd.is_override,
                'overridden_agent': hd.overridden_agent.display_name if hd.overridden_agent else None,
                'overridden_agent_id': hd.overridden_agent.name if hd.overridden_agent else None,
                'created_at': hd.created_at.isoformat()
            }
        else:
            decision_data['human_decision'] = None

        # Add outcome if exists
        if hasattr(decision, 'outcome'):
            outcome = decision.outcome
            decision_data['outcome'] = {
                'status': outcome.status,
                'status_display': outcome.get_status_display(),
                'attribution': outcome.attribution,
                'attribution_display': outcome.get_attribution_display(),
                'outcome_summary': outcome.outcome_summary,
                'metrics': outcome.metrics,
                'told_you_so_triggered': outcome.told_you_so_triggered,
                'told_you_so_message': outcome.told_you_so_message if outcome.told_you_so_triggered else None,
                'created_at': outcome.created_at.isoformat()
            }
        else:
            decision_data['outcome'] = None

        return Response({
            'success': True,
            'decision': decision_data
        })

    except CoLeadershipDecision.DoesNotExist:
        return Response({
            'error': 'Decision not found or access denied'
        }, status=404)

    except Exception as e:
        logger.error(f"❌ Error getting decision detail: {str(e)}")
        return Response({
            'error': 'Failed to get decision detail',
            'details': str(e)
        }, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_decision(request, decision_id):
    """
    Delete a co-leadership decision.

    Session 180: Delete endpoint for cleaning up decision timeline.

    Only the user who initiated the decision can delete it.
    Cascades to delete related recommendations, human_decision, and outcome.
    """
    try:
        # Get decision (permission check via user ownership)
        decision = CoLeadershipDecision.objects.get(
            id=decision_id,
            initiated_by=request.user
        )

        title = decision.title
        decision.delete()

        logger.info(f"🗑️ Deleted decision: {title} (user: {request.user.username})")

        return Response({
            'success': True,
            'message': f'Decision "{title}" deleted successfully'
        })

    except CoLeadershipDecision.DoesNotExist:
        return Response({
            'error': 'Decision not found or access denied'
        }, status=404)

    except Exception as e:
        logger.error(f"❌ Error deleting decision: {str(e)}")
        return Response({
            'error': 'Failed to delete decision',
            'details': str(e)
        }, status=500)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_preferences(request):
    """
    Get or update user's co-leadership preferences.

    Session 108: Preferences endpoint for mobile settings.

    GET: Returns current preferences
    POST: Updates preferences

    POST body:
    {
        "allow_told_you_so": true,
        "tone": "playful"  // "serious" or "playful"
    }
    """
    try:
        from .models import CoLeadershipPreferences

        # Get or create preferences
        prefs, created = CoLeadershipPreferences.objects.get_or_create(
            user=request.user,
            defaults={'allow_told_you_so': False, 'tone': 'serious'}
        )

        if request.method == 'GET':
            return Response({
                'success': True,
                'preferences': {
                    'allow_told_you_so': prefs.allow_told_you_so,
                    'tone': prefs.tone,
                    'tone_choices': [
                        {'value': 'serious', 'label': 'Serious - Professional and straightforward'},
                        {'value': 'playful', 'label': 'Playful - Lighthearted and engaging'}
                    ]
                }
            })

        elif request.method == 'POST':
            # Update preferences
            if 'allow_told_you_so' in request.data:
                prefs.allow_told_you_so = bool(request.data['allow_told_you_so'])

            if 'tone' in request.data:
                tone = request.data['tone']
                if tone in ['serious', 'playful']:
                    prefs.tone = tone
                else:
                    return Response({
                        'error': 'Invalid tone. Must be "serious" or "playful"'
                    }, status=400)

            prefs.save()

            logger.info(f"✅ Updated co-leadership preferences for {request.user.username}")

            return Response({
                'success': True,
                'message': 'Preferences updated',
                'preferences': {
                    'allow_told_you_so': prefs.allow_told_you_so,
                    'tone': prefs.tone
                }
            })

    except Exception as e:
        logger.error(f"❌ Error managing preferences: {str(e)}")
        return Response({
            'error': 'Failed to manage preferences',
            'details': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_project_decisions(request, project_id):
    """
    Get all co-leadership decisions for a specific project.

    Session 100: Part 2 - Decisions timeline for projects.

    Returns list of decisions with their recommendations, human choices, and outcomes.
    """
    try:
        # Get project (verify ownership)
        from content.models import CreativeProject
        project = CreativeProject.objects.get(
            id=project_id,  # Session 119: Fixed - use 'id' not 'project_id'
            user=request.user
        )

        # Get all decisions for this project
        decisions = CoLeadershipDecision.objects.filter(
            project=project
        ).select_related(
            'human_decision',
            'outcome'
        ).prefetch_related(
            'recommendations__agent_template'
        ).order_by('-created_at')

        # Build response
        decisions_list = []
        for decision in decisions:
            decision_data = {
                'id': str(decision.id),
                'title': decision.title,
                'description': decision.description,
                'created_at': decision.created_at.isoformat(),
                'frozen_at': decision.frozen_at.isoformat() if decision.frozen_at else None,
                'is_frozen': decision.is_frozen,
                'has_outcome': decision.has_outcome,
                'recommendations': [],
                'human_decision': None,
                'outcome': None
            }

            # Add agent recommendations
            for rec in decision.recommendations.all():
                decision_data['recommendations'].append({
                    'agent': rec.agent_template.display_name,
                    'stance': rec.get_stance_display(),
                    'summary': rec.summary,
                    'confidence': rec.confidence
                })

            # Add human decision if exists
            if hasattr(decision, 'human_decision'):
                hd = decision.human_decision
                decision_data['human_decision'] = {
                    'chosen_path': hd.chosen_path_summary,
                    'justification': hd.justification,
                    'is_override': hd.is_override,
                    'overridden_agent': hd.overridden_agent.display_name if hd.overridden_agent else None
                }

            # Add outcome if exists
            if hasattr(decision, 'outcome'):
                outcome = decision.outcome
                decision_data['outcome'] = {
                    'status': outcome.get_status_display(),
                    'attribution': outcome.get_attribution_display(),
                    'summary': outcome.outcome_summary,
                    'told_you_so_message': outcome.told_you_so_message if outcome.told_you_so_triggered else None
                }

            decisions_list.append(decision_data)

        return Response({
            'success': True,
            'project': {
                'id': str(project.id),  # Session 119: Fixed - use 'id' not 'project_id'
                'name': project.name
            },
            'decisions': decisions_list,
            'total': len(decisions_list)
        })

    except CreativeProject.DoesNotExist:
        return Response({
            'error': 'Project not found or access denied'
        }, status=404)

    except Exception as e:
        logger.error(f"❌ Error getting project decisions: {str(e)}")
        return Response({
            'error': 'Failed to get project decisions',
            'details': str(e)
        }, status=500)
