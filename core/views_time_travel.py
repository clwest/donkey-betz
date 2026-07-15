"""
Time Travel Debugging API Views - Session 255

Replay agent decisions and see what they were "thinking."
Like a debugger for AI agents!
"""

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count, Avg

from .auth_middleware import token_auth_required
from .models_unified_system import (
    AgentSession, DecisionPoint, ThoughtBubble, ReplayBookmark, DebugAnnotation, Agent
)


# =============================================================================
# TIME TRAVEL OVERVIEW
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_time_travel_overview(request):
    """Get overview of all debug sessions for time travel."""
    try:
        # Recent sessions
        sessions = AgentSession.objects.select_related('agent').order_by('-started_at')[:50]

        # Stats
        total_sessions = AgentSession.objects.count()
        completed_sessions = AgentSession.objects.filter(status='completed').count()
        failed_sessions = AgentSession.objects.filter(status='failed').count()
        bookmarked_sessions = AgentSession.objects.filter(is_bookmarked=True).count()

        # Decision stats
        total_decisions = DecisionPoint.objects.count()
        flagged_decisions = DecisionPoint.objects.filter(is_flagged=True).count()

        # Average decisions per session
        avg_decisions = AgentSession.objects.aggregate(
            avg=Avg('total_decisions')
        )['avg'] or 0

        # Sessions by agent
        sessions_by_agent = AgentSession.objects.values(
            'agent__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        # Decision type distribution
        decision_types = DecisionPoint.objects.values('decision_type').annotate(
            count=Count('id')
        ).order_by('-count')

        # Recent sessions list
        recent_sessions = []
        for session in sessions:
            recent_sessions.append({
                'id': str(session.id),
                'agent_name': session.agent.name,
                'agent_id': str(session.agent.id),
                'task_type': session.task_type,
                'task_description': session.task_description[:100] + '...' if len(session.task_description) > 100 else session.task_description,
                'status': session.status,
                'total_decisions': session.total_decisions,
                'duration': session.get_duration_formatted(),
                'is_bookmarked': session.is_bookmarked,
                'started_at': session.started_at.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'overview': {
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions,
                'failed_sessions': failed_sessions,
                'bookmarked_sessions': bookmarked_sessions,
                'total_decisions': total_decisions,
                'flagged_decisions': flagged_decisions,
                'avg_decisions_per_session': round(avg_decisions, 1),
            },
            'sessions_by_agent': list(sessions_by_agent),
            'decision_types': list(decision_types),
            'recent_sessions': recent_sessions
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# SESSION DETAIL (for replay)
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_session_detail(request, session_id):
    """Get full session details for replay."""
    try:
        session = AgentSession.objects.select_related('agent').get(id=session_id)

        # Get all decisions with thoughts
        decisions = []
        for decision in session.decisions.order_by('sequence_number'):
            thoughts = []
            for thought in decision.thoughts.order_by('sequence_number'):
                thoughts.append({
                    'id': str(thought.id),
                    'sequence': thought.sequence_number,
                    'type': thought.thought_type,
                    'content': thought.content,
                    'importance': thought.importance,
                    'influences_decision': thought.influences_decision,
                })

            annotations = []
            for annotation in decision.annotations.all():
                annotations.append({
                    'id': str(annotation.id),
                    'content': annotation.content,
                    'type': annotation.annotation_type,
                    'created_at': annotation.created_at.isoformat(),
                })

            decisions.append({
                'id': str(decision.id),
                'sequence': decision.sequence_number,
                'type': decision.decision_type,
                'context': decision.context,
                'reasoning': decision.reasoning,
                'alternatives': decision.alternatives,
                'action_taken': decision.action_taken,
                'action_params': decision.action_params,
                'confidence': decision.confidence_score,
                'was_successful': decision.was_successful,
                'outcome_notes': decision.outcome_notes,
                'duration_ms': decision.duration_ms,
                'is_flagged': decision.is_flagged,
                'flag_reason': decision.flag_reason,
                'timestamp': decision.timestamp.isoformat(),
                'thoughts': thoughts,
                'annotations': annotations,
            })

        # Get bookmarks
        bookmarks = []
        for bookmark in session.bookmarks.all():
            bookmarks.append({
                'id': str(bookmark.id),
                'decision_id': str(bookmark.decision.id) if bookmark.decision else None,
                'title': bookmark.title,
                'description': bookmark.description,
                'type': bookmark.bookmark_type,
                'created_at': bookmark.created_at.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'session': {
                'id': str(session.id),
                'agent_id': str(session.agent.id),
                'agent_name': session.agent.name,
                'task_type': session.task_type,
                'task_description': session.task_description,
                'input_data': session.input_data,
                'output_data': session.output_data,
                'status': session.status,
                'error_message': session.error_message,
                'total_decisions': session.total_decisions,
                'token_usage': session.token_usage,
                'api_calls': session.api_calls,
                'duration_ms': session.duration_ms,
                'duration_formatted': session.get_duration_formatted(),
                'is_bookmarked': session.is_bookmarked,
                'bookmark_note': session.bookmark_note,
                'started_at': session.started_at.isoformat(),
                'ended_at': session.ended_at.isoformat() if session.ended_at else None,
            },
            'decisions': decisions,
            'bookmarks': bookmarks,
        })

    except AgentSession.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Session not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# SESSION MANAGEMENT
# =============================================================================

@require_http_methods(["POST"])
@token_auth_required
def start_session(request):
    """Start a new debug session for an agent.
    Session 750: Fixed to accept agent_id from request body instead of URL param.
    """
    try:
        data = json.loads(request.body) if request.body else {}

        agent_id = data.get('agent_id')
        if not agent_id:
            return JsonResponse({'success': False, 'error': 'agent_id is required'}, status=400)

        agent = Agent.objects.get(id=agent_id)

        session = AgentSession.objects.create(
            agent=agent,
            task_type=data.get('task_type', 'unknown'),
            task_description=data.get('task_description', ''),
            input_data=data.get('input_data', {}),
            status='running'
        )

        return JsonResponse({
            'success': True,
            'session_id': str(session.id),
            'message': f'Debug session started for {agent.name}'
        })

    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@token_auth_required
def end_session(request, session_id):
    """End a debug session."""
    try:
        data = json.loads(request.body) if request.body else {}

        session = AgentSession.objects.get(id=session_id)

        session.status = data.get('status', 'completed')
        session.output_data = data.get('output_data', {})
        session.error_message = data.get('error_message')
        session.ended_at = timezone.now()
        session.duration_ms = int((session.ended_at - session.started_at).total_seconds() * 1000)
        session.token_usage = data.get('token_usage', 0)
        session.api_calls = data.get('api_calls', 0)
        session.save()

        return JsonResponse({
            'success': True,
            'session_id': str(session.id),
            'status': session.status,
            'duration': session.get_duration_formatted()
        })

    except AgentSession.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Session not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@token_auth_required
def toggle_bookmark_session(request, session_id):
    """Toggle bookmark on a session."""
    try:
        data = json.loads(request.body) if request.body else {}

        session = AgentSession.objects.get(id=session_id)
        session.is_bookmarked = not session.is_bookmarked
        session.bookmark_note = data.get('note', session.bookmark_note)
        session.save()

        return JsonResponse({
            'success': True,
            'is_bookmarked': session.is_bookmarked,
            'message': 'Session bookmarked' if session.is_bookmarked else 'Bookmark removed'
        })

    except AgentSession.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Session not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# DECISION POINT MANAGEMENT
# =============================================================================

@require_http_methods(["POST"])
@token_auth_required
def record_decision(request):
    """Record a decision point during agent execution.
    Session 750: Fixed to accept session_id from request body instead of URL param.
    """
    try:
        data = json.loads(request.body) if request.body else {}

        session_id = data.get('session_id')
        if not session_id:
            return JsonResponse({'success': False, 'error': 'session_id is required'}, status=400)

        session = AgentSession.objects.get(id=session_id)

        # Get next sequence number
        last_decision = session.decisions.order_by('-sequence_number').first()
        sequence_number = (last_decision.sequence_number + 1) if last_decision else 1

        decision = DecisionPoint.objects.create(
            session=session,
            sequence_number=sequence_number,
            decision_type=data.get('decision_type', 'other'),
            context=data.get('context', {}),
            reasoning=data.get('reasoning', ''),
            alternatives=data.get('alternatives', []),
            action_taken=data.get('action_taken', ''),
            action_params=data.get('action_params', {}),
            confidence_score=data.get('confidence', 0.8),
            duration_ms=data.get('duration_ms', 0),
        )

        # Update session decision count
        session.total_decisions = sequence_number
        session.save()

        # Record any thoughts
        thoughts = data.get('thoughts', [])
        for i, thought in enumerate(thoughts):
            ThoughtBubble.objects.create(
                decision=decision,
                sequence_number=i + 1,
                thought_type=thought.get('type', 'observation'),
                content=thought.get('content', ''),
                importance=thought.get('importance', 0.5),
                influences_decision=thought.get('influences_decision', True),
            )

        return JsonResponse({
            'success': True,
            'decision_id': str(decision.id),
            'sequence_number': sequence_number
        })

    except AgentSession.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Session not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@token_auth_required
def update_decision_outcome(request, decision_id):
    """Update the outcome of a decision after execution."""
    try:
        data = json.loads(request.body) if request.body else {}

        decision = DecisionPoint.objects.get(id=decision_id)
        decision.was_successful = data.get('was_successful')
        decision.outcome_notes = data.get('outcome_notes', '')
        decision.save()

        return JsonResponse({
            'success': True,
            'decision_id': str(decision.id),
            'was_successful': decision.was_successful
        })

    except DecisionPoint.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Decision not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@token_auth_required
def flag_decision(request, decision_id):
    """Flag a decision for review."""
    try:
        data = json.loads(request.body) if request.body else {}

        decision = DecisionPoint.objects.get(id=decision_id)
        decision.is_flagged = not decision.is_flagged
        decision.flag_reason = data.get('reason', '')
        decision.save()

        return JsonResponse({
            'success': True,
            'is_flagged': decision.is_flagged,
            'message': 'Decision flagged' if decision.is_flagged else 'Flag removed'
        })

    except DecisionPoint.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Decision not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# BOOKMARKS & ANNOTATIONS
# =============================================================================

@require_http_methods(["POST"])
@token_auth_required
def create_bookmark(request):
    """Create a bookmark at a specific decision point.
    Session 750: Fixed to accept session_id from request body instead of URL param.
    """
    try:
        data = json.loads(request.body) if request.body else {}

        session_id = data.get('session_id')
        if not session_id:
            return JsonResponse({'success': False, 'error': 'session_id is required'}, status=400)

        session = AgentSession.objects.get(id=session_id)

        decision_id = data.get('decision_id')
        decision = None
        if decision_id:
            decision = DecisionPoint.objects.get(id=decision_id)

        bookmark = ReplayBookmark.objects.create(
            session=session,
            decision=decision,
            title=data.get('title', 'Bookmark'),
            description=data.get('description', ''),
            bookmark_type=data.get('bookmark_type', 'interesting'),
        )

        return JsonResponse({
            'success': True,
            'bookmark_id': str(bookmark.id),
            'message': 'Bookmark created'
        })

    except AgentSession.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Session not found'}, status=404)
    except DecisionPoint.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Decision not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["DELETE"])
@token_auth_required
def delete_bookmark(request, bookmark_id):
    """Delete a bookmark."""
    try:
        bookmark = ReplayBookmark.objects.get(id=bookmark_id)
        bookmark.delete()

        return JsonResponse({
            'success': True,
            'message': 'Bookmark deleted'
        })

    except ReplayBookmark.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Bookmark not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@token_auth_required
def add_annotation(request):
    """Add an annotation to a decision point.
    Session 750: Fixed to accept decision_id from request body instead of URL param.
    """
    try:
        data = json.loads(request.body) if request.body else {}

        decision_id = data.get('decision_id')
        if not decision_id:
            return JsonResponse({'success': False, 'error': 'decision_id is required'}, status=400)

        decision = DecisionPoint.objects.get(id=decision_id)

        annotation = DebugAnnotation.objects.create(
            decision=decision,
            content=data.get('content', ''),
            annotation_type=data.get('annotation_type', 'note'),
        )

        return JsonResponse({
            'success': True,
            'annotation_id': str(annotation.id),
            'message': 'Annotation added'
        })

    except DecisionPoint.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Decision not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["DELETE"])
@token_auth_required
def delete_annotation(request, annotation_id):
    """Delete an annotation."""
    try:
        annotation = DebugAnnotation.objects.get(id=annotation_id)
        annotation.delete()

        return JsonResponse({
            'success': True,
            'message': 'Annotation deleted'
        })

    except DebugAnnotation.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Annotation not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# SEARCH & FILTER
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def search_sessions(request):
    """Search sessions with filters."""
    try:
        # Filters
        agent_id = request.GET.get('agent_id')
        status = request.GET.get('status')
        task_type = request.GET.get('task_type')
        bookmarked = request.GET.get('bookmarked')
        limit = int(request.GET.get('limit', 50))

        sessions = AgentSession.objects.select_related('agent').order_by('-started_at')

        if agent_id:
            sessions = sessions.filter(agent_id=agent_id)
        if status:
            sessions = sessions.filter(status=status)
        if task_type:
            sessions = sessions.filter(task_type__icontains=task_type)
        if bookmarked == 'true':
            sessions = sessions.filter(is_bookmarked=True)

        sessions = sessions[:limit]

        results = []
        for session in sessions:
            results.append({
                'id': str(session.id),
                'agent_name': session.agent.name,
                'task_type': session.task_type,
                'status': session.status,
                'total_decisions': session.total_decisions,
                'is_bookmarked': session.is_bookmarked,
                'started_at': session.started_at.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'sessions': results,
            'count': len(results)
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_flagged_decisions(request):
    """Get all flagged decisions for review."""
    try:
        limit = int(request.GET.get('limit', 50))

        decisions = DecisionPoint.objects.select_related(
            'session', 'session__agent'
        ).filter(is_flagged=True).order_by('-timestamp')[:limit]

        results = []
        for decision in decisions:
            results.append({
                'id': str(decision.id),
                'session_id': str(decision.session.id),
                'agent_name': decision.session.agent.name,
                'sequence': decision.sequence_number,
                'decision_type': decision.decision_type,
                'action_taken': decision.action_taken,
                'flag_reason': decision.flag_reason,
                'was_successful': decision.was_successful,
                'timestamp': decision.timestamp.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'flagged_decisions': results,
            'count': len(results)
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# AGENT SESSION HISTORY
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_agent_sessions(request, agent_id):
    """Get session history for a specific agent."""
    try:
        limit = int(request.GET.get('limit', 30))

        agent = Agent.objects.get(id=agent_id)
        sessions = AgentSession.objects.filter(agent=agent).order_by('-started_at')[:limit]

        # Stats for this agent
        total_sessions = AgentSession.objects.filter(agent=agent).count()
        successful_sessions = AgentSession.objects.filter(agent=agent, status='completed').count()
        total_decisions = DecisionPoint.objects.filter(session__agent=agent).count()
        flagged_decisions = DecisionPoint.objects.filter(session__agent=agent, is_flagged=True).count()

        session_list = []
        for session in sessions:
            session_list.append({
                'id': str(session.id),
                'task_type': session.task_type,
                'task_description': session.task_description[:100] + '...' if len(session.task_description) > 100 else session.task_description,
                'status': session.status,
                'total_decisions': session.total_decisions,
                'duration': session.get_duration_formatted(),
                'is_bookmarked': session.is_bookmarked,
                'started_at': session.started_at.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'agent_name': agent.name,
            'stats': {
                'total_sessions': total_sessions,
                'successful_sessions': successful_sessions,
                'success_rate': round(successful_sessions / max(total_sessions, 1) * 100, 1),
                'total_decisions': total_decisions,
                'flagged_decisions': flagged_decisions,
            },
            'sessions': session_list
        })

    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# SIMULATE DEBUG SESSION (for demo/testing)
# =============================================================================

@require_http_methods(["POST"])
@token_auth_required
def simulate_session(request, agent_id):
    """Create a simulated debug session for testing the UI.
    Session 750: Enhanced with realistic data instead of placeholders.
    """
    try:
        import random

        agent = Agent.objects.get(id=agent_id)

        # Task configurations with realistic data
        task_configs = {
            'image_generation': {
                'description': f'Generate professional marketing image for {agent.name} campaign',
                'input': {'prompt': 'Create a modern tech startup banner', 'style': 'minimalist', 'dimensions': '1920x1080'},
                'decisions': [
                    {
                        'type': 'analysis',
                        'action': 'Analyzing visual requirements',
                        'reasoning': 'Examined the prompt for key visual elements: modern aesthetic, tech industry focus, minimalist design. Identified need for clean lines, tech-forward color palette, and professional composition.',
                        'alternatives': ['Use vibrant gradient background', 'Apply flat design with icons', 'Create 3D rendered scene'],
                        'thoughts': [
                            ('observation', 'The prompt emphasizes professionalism and modern tech aesthetics'),
                            ('hypothesis', 'A minimalist approach with strategic color accents would best convey tech sophistication'),
                            ('evaluation', 'Comparing reference images shows clean designs perform better for B2B'),
                        ],
                    },
                    {
                        'type': 'planning',
                        'action': 'Planning composition layout',
                        'reasoning': 'Determined optimal layout using rule of thirds. Central focal point with asymmetric balance will create visual interest while maintaining professional appearance.',
                        'alternatives': ['Centered symmetric layout', 'Golden ratio spiral composition', 'Grid-based modular design'],
                        'thoughts': [
                            ('insight', 'Asymmetric layouts create more dynamic visual flow'),
                            ('evaluation', 'Rule of thirds provides good balance between creativity and professionalism'),
                        ],
                    },
                    {
                        'type': 'tool_selection',
                        'action': 'Selected DALL-E 3 for generation',
                        'reasoning': 'DALL-E 3 chosen for superior text rendering and photorealistic output. Stable Diffusion considered but text accuracy is critical for marketing materials.',
                        'alternatives': ['Stable Diffusion XL for artistic style', 'Midjourney for creative interpretation', 'Firefly for commercial licensing'],
                        'thoughts': [
                            ('observation', 'Marketing images often contain text elements requiring high fidelity'),
                            ('evaluation', 'DALL-E 3 text rendering accuracy is ~95% vs ~60% for alternatives'),
                        ],
                    },
                    {
                        'type': 'parameter_choice',
                        'action': 'Configured generation parameters',
                        'reasoning': 'Set quality to HD, natural style selected over vivid to maintain professional tone. Added negative prompts to avoid common artifacts.',
                        'alternatives': ['Vivid style for more impact', 'Standard quality for faster generation', 'Multiple variations for A/B testing'],
                        'thoughts': [
                            ('hypothesis', 'Natural style will better align with B2B expectations'),
                            ('insight', 'HD quality reduces need for post-processing touch-ups'),
                        ],
                    },
                    {
                        'type': 'quality_check',
                        'action': 'Validated output against requirements',
                        'reasoning': 'Checked generated image for: composition alignment, color consistency, text legibility, brand appropriateness. All criteria met with minor adjustments recommended for contrast.',
                        'alternatives': ['Request regeneration with modified prompt', 'Apply post-processing filters', 'Accept as-is without modifications'],
                        'thoughts': [
                            ('observation', 'Image meets 4/5 quality criteria, minor contrast adjustment needed'),
                            ('evaluation', 'Post-processing is more efficient than regeneration for minor issues'),
                            ('insight', 'Adding 10% contrast boost will improve text readability'),
                        ],
                    },
                ],
            },
            'research': {
                'description': f'Research market trends for {agent.name} strategic analysis',
                'input': {'topic': 'AI industry trends 2026', 'depth': 'comprehensive', 'sources': ['news', 'reports', 'social']},
                'decisions': [
                    {
                        'type': 'analysis',
                        'action': 'Analyzing research scope',
                        'reasoning': 'Defined research boundaries: focus on enterprise AI adoption, exclude consumer applications. Timeframe: last 6 months with forward projections.',
                        'alternatives': ['Broader scope including consumer AI', 'Narrow focus on single vertical', 'Historical analysis over 5 years'],
                        'thoughts': [
                            ('observation', 'Enterprise AI market showing 40% YoY growth'),
                            ('hypothesis', 'Focusing on enterprise will yield more actionable insights'),
                        ],
                    },
                    {
                        'type': 'planning',
                        'action': 'Structured research methodology',
                        'reasoning': 'Adopted mixed-methods approach: quantitative market data from reports, qualitative insights from expert interviews and social sentiment.',
                        'alternatives': ['Pure quantitative analysis', 'Survey-based primary research', 'Competitive intelligence focus'],
                        'thoughts': [
                            ('insight', 'Mixed methods provide both breadth and depth'),
                            ('evaluation', 'Social sentiment adds real-time market pulse data'),
                        ],
                    },
                    {
                        'type': 'tool_selection',
                        'action': 'Selected data aggregation spiders',
                        'reasoning': 'Deployed TechCrunch, Reuters, and HackerNews spiders for news. Added Crunchbase spider for funding data. Twitter/X excluded due to API limitations.',
                        'alternatives': ['Include Twitter/X with rate limiting', 'Add LinkedIn for professional insights', 'Use only premium data sources'],
                        'thoughts': [
                            ('observation', 'News spiders provide 500+ relevant articles per week'),
                            ('evaluation', 'Crunchbase funding data correlates with market confidence'),
                        ],
                    },
                    {
                        'type': 'parameter_choice',
                        'action': 'Configured data filters',
                        'reasoning': 'Set relevance threshold to 0.75, date range to 6 months, excluded duplicate sources. Entity extraction enabled for trend identification.',
                        'alternatives': ['Lower threshold for broader coverage', 'Shorter timeframe for recency', 'Manual curation over automated filtering'],
                        'thoughts': [
                            ('hypothesis', '0.75 threshold balances signal-to-noise ratio'),
                            ('insight', 'Entity extraction reveals hidden connections between trends'),
                        ],
                    },
                    {
                        'type': 'quality_check',
                        'action': 'Validated research completeness',
                        'reasoning': 'Cross-referenced findings against 3 analyst reports. 87% alignment achieved. Identified 2 emerging trends not in mainstream reports.',
                        'alternatives': ['Seek additional validation sources', 'Focus only on consensus findings', 'Flag novel findings for review'],
                        'thoughts': [
                            ('observation', 'Novel trends may indicate early signals or noise'),
                            ('evaluation', 'Historical accuracy of spider-detected trends is 73%'),
                            ('insight', 'Flagging for human review adds appropriate caution'),
                        ],
                    },
                ],
            },
            'content_creation': {
                'description': f'Create engaging content piece via {agent.name}',
                'input': {'type': 'blog_post', 'topic': 'Future of AI assistants', 'tone': 'authoritative', 'length': '1500 words'},
                'decisions': [
                    {
                        'type': 'analysis',
                        'action': 'Analyzing content requirements',
                        'reasoning': 'Target audience: tech-savvy professionals. Key angles: productivity gains, integration challenges, ethical considerations. SEO keywords identified.',
                        'alternatives': ['Consumer-focused angle', 'Technical deep-dive approach', 'Opinion/editorial style'],
                        'thoughts': [
                            ('observation', 'B2B content performs best with data-backed claims'),
                            ('hypothesis', 'Balancing technical depth with accessibility will maximize engagement'),
                        ],
                    },
                    {
                        'type': 'planning',
                        'action': 'Outlined content structure',
                        'reasoning': 'Adopted inverted pyramid with hook, 3 main sections, and actionable conclusion. Each section targets specific reader intent stage.',
                        'alternatives': ['Listicle format for scannability', 'Narrative storytelling approach', 'Q&A format for direct answers'],
                        'thoughts': [
                            ('insight', 'Inverted pyramid improves time-on-page for skimmers'),
                            ('evaluation', 'Section headers enable both deep readers and scanners'),
                        ],
                    },
                    {
                        'type': 'tool_selection',
                        'action': 'Selected GPT-5 for drafting',
                        'reasoning': 'GPT-5 chosen for nuanced understanding and consistent voice. Claude considered for longer context but topic fits within GPT-5 capabilities.',
                        'alternatives': ['Claude for nuanced reasoning', 'GPT-5-mini for speed', 'Human writer for authenticity'],
                        'thoughts': [
                            ('observation', 'GPT-5 maintains consistent authoritative tone'),
                            ('evaluation', 'Token efficiency is 20% better than alternatives for this length'),
                        ],
                    },
                    {
                        'type': 'parameter_choice',
                        'action': 'Configured generation settings',
                        'reasoning': 'Temperature 0.7 for creativity while maintaining factual accuracy. Max tokens set for 1800 to allow editing buffer. System prompt includes brand voice guidelines.',
                        'alternatives': ['Lower temperature for more conservative output', 'Higher temperature for unique angles', 'Zero-shot without brand guidelines'],
                        'thoughts': [
                            ('hypothesis', '0.7 temperature provides optimal creativity-accuracy balance'),
                            ('insight', 'Brand voice system prompts improve consistency by 40%'),
                        ],
                    },
                    {
                        'type': 'quality_check',
                        'action': 'Evaluated content quality',
                        'reasoning': 'Checked readability (Grade 10 level achieved), factual accuracy (3 claims verified), originality (94% unique), and brand voice alignment (strong match).',
                        'alternatives': ['Request revision for specific sections', 'Add more data citations', 'Simplify for broader audience'],
                        'thoughts': [
                            ('observation', 'Readability score optimal for target audience'),
                            ('evaluation', 'Originality score exceeds 90% threshold'),
                            ('insight', 'Minor citation additions would strengthen authority'),
                        ],
                    },
                ],
            },
        }

        # Select task type
        task_type = random.choice(list(task_configs.keys()))
        config = task_configs[task_type]

        session = AgentSession.objects.create(
            agent=agent,
            task_type=task_type,
            task_description=config['description'],
            input_data=config['input'],
            status='completed',
            token_usage=random.randint(500, 2000),
            api_calls=random.randint(2, 8),
        )

        # Create decisions with realistic data
        failure_reasons = [
            'API rate limit exceeded, retrying with exponential backoff',
            'Generated output did not meet quality threshold (scored 0.68, required 0.75)',
            'Timeout occurred during external data fetch, using cached fallback',
            'Validation failed: missing required field in structured output',
        ]

        for seq, decision_config in enumerate(config['decisions'], 1):
            was_successful = random.random() > 0.2
            outcome_notes = None if was_successful else random.choice(failure_reasons)

            decision = DecisionPoint.objects.create(
                session=session,
                sequence_number=seq,
                decision_type=decision_config['type'],
                context={'step': seq, 'task_type': task_type, 'agent': agent.name},
                reasoning=decision_config['reasoning'],
                alternatives=decision_config['alternatives'],
                action_taken=decision_config['action'],
                action_params={'confidence': round(random.uniform(0.75, 0.95), 2)},
                confidence_score=random.uniform(0.7, 0.95),
                was_successful=was_successful,
                outcome_notes=outcome_notes,
                duration_ms=random.randint(100, 1500),
            )

            # Add thoughts
            for t_seq, (thought_type, content) in enumerate(decision_config['thoughts'], 1):
                ThoughtBubble.objects.create(
                    decision=decision,
                    sequence_number=t_seq,
                    thought_type=thought_type,
                    content=content,
                    importance=random.uniform(0.5, 0.9),
                    influences_decision=random.random() > 0.3,
                )

        # Finalize session
        session.total_decisions = len(config['decisions'])
        session.ended_at = timezone.now()
        session.duration_ms = random.randint(5000, 30000)
        session.save()

        return JsonResponse({
            'success': True,
            'session_id': str(session.id),
            'decisions_created': session.total_decisions,
            'message': f'Simulated session created with {session.total_decisions} decisions'
        })

    except Agent.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agent not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
