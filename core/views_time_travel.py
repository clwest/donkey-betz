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
from django.db.models import Count, Avg, Q

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

@csrf_exempt
@require_http_methods(["POST"])
def start_session(request, agent_id):
    """Start a new debug session for an agent."""
    try:
        data = json.loads(request.body) if request.body else {}

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


@csrf_exempt
@require_http_methods(["POST"])
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


@csrf_exempt
@require_http_methods(["POST"])
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

@csrf_exempt
@require_http_methods(["POST"])
def record_decision(request, session_id):
    """Record a decision point during agent execution."""
    try:
        data = json.loads(request.body) if request.body else {}

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


@csrf_exempt
@require_http_methods(["POST"])
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


@csrf_exempt
@require_http_methods(["POST"])
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

@csrf_exempt
@require_http_methods(["POST"])
def create_bookmark(request, session_id):
    """Create a bookmark at a specific decision point."""
    try:
        data = json.loads(request.body) if request.body else {}

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


@csrf_exempt
@require_http_methods(["DELETE"])
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


@csrf_exempt
@require_http_methods(["POST"])
def add_annotation(request, decision_id):
    """Add an annotation to a decision point."""
    try:
        data = json.loads(request.body) if request.body else {}

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


@csrf_exempt
@require_http_methods(["DELETE"])
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

@csrf_exempt
@require_http_methods(["POST"])
def simulate_session(request, agent_id):
    """Create a simulated debug session for testing the UI."""
    try:
        import random

        agent = Agent.objects.get(id=agent_id)

        # Create session
        task_types = ['image_generation', 'research', 'analysis', 'content_creation', 'workflow']
        task_type = random.choice(task_types)

        session = AgentSession.objects.create(
            agent=agent,
            task_type=task_type,
            task_description=f"Simulated {task_type} task for testing time travel debugging",
            input_data={'prompt': 'Test prompt', 'style': 'professional'},
            status='completed',
            token_usage=random.randint(500, 2000),
            api_calls=random.randint(2, 8),
        )

        # Create decisions
        decision_types = [
            ('analysis', 'Analyzing input requirements'),
            ('planning', 'Planning execution approach'),
            ('tool_selection', 'Selecting appropriate tool'),
            ('parameter_choice', 'Choosing parameters'),
            ('quality_check', 'Checking output quality'),
        ]

        for seq, (dtype, action) in enumerate(decision_types, 1):
            decision = DecisionPoint.objects.create(
                session=session,
                sequence_number=seq,
                decision_type=dtype,
                context={'step': seq, 'input': 'test'},
                reasoning=f"At step {seq}, I considered multiple approaches and decided this was the best path forward based on the requirements.",
                alternatives=[f'Alternative {i}' for i in range(1, 4)],
                action_taken=action,
                action_params={'confidence': 0.85},
                confidence_score=random.uniform(0.7, 0.95),
                was_successful=random.random() > 0.2,
                duration_ms=random.randint(100, 1500),
            )

            # Add thoughts
            thought_types = ['observation', 'hypothesis', 'evaluation', 'insight']
            for t_seq in range(1, random.randint(2, 4)):
                ThoughtBubble.objects.create(
                    decision=decision,
                    sequence_number=t_seq,
                    thought_type=random.choice(thought_types),
                    content=f"Thought {t_seq}: Considering the context and requirements...",
                    importance=random.uniform(0.3, 0.9),
                    influences_decision=random.random() > 0.3,
                )

        # Finalize session
        session.total_decisions = len(decision_types)
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
