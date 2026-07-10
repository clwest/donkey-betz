"""
Session Handoff API - Session 455

Cross-platform conversation session management for web ↔ Discord continuity.

Endpoints:
- GET /api/sessions/active/ - Get user's active sessions across all platforms
- GET /api/sessions/<conversation_id>/ - Get session details and history
- POST /api/sessions/resume/ - Resume a session from another platform
- POST /api/sessions/end/ - End a session (mark inactive)

Usage:
    # Get active sessions
    GET /api/sessions/active/

    # Resume a Discord session on web
    POST /api/sessions/resume/
    {"conversation_id": "uuid-here"}

    # End a session
    POST /api/sessions/end/
    {"conversation_id": "uuid-here"}
"""

import logging
from datetime import timedelta
from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

from core.security import scope_queryset_chat_conversation

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def get_active_sessions(request):
    """
    Get all active conversation sessions for the current user.
    Returns sessions from both web and Discord.
    """
    from core.models import ChatConversation

    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Authentication required'
        }, status=401)

    try:
        user = request.user

        # Session expiry window (24 hours)
        cutoff = timezone.now() - timedelta(hours=24)

        # Get sessions by user OR by linked Discord ID.
        # I-0302 Phase 3 Sub-phase C1 (2026-07-10): predicate handles the
        # workspace-scoped + user-owned branch; the Discord fallback is
        # OR'd on top because the Discord platform doesn't participate in
        # workspaces (predicate wouldn't include it). Both filters are
        # keyed on the authenticated user (`request.user`), preserving
        # Rigby SIGN Q7 "auth mapping, not any row" invariant.
        base_query = scope_queryset_chat_conversation(
            user,
            ChatConversation.objects.filter(
                session_active=True,
                created_at__gte=cutoff,
            ),
        )
        if user.discord_id:
            # Union in Discord-mapped rows for the authenticated user.
            discord_query = ChatConversation.objects.filter(
                session_active=True,
                created_at__gte=cutoff,
                discord_user_id=user.discord_id,
            )
            sessions_query = (base_query | discord_query).distinct()
        else:
            sessions_query = base_query

        # Group by conversation_id to get unique sessions
        from django.db.models import Max, Min, Count
        session_data = sessions_query.values('conversation_id', 'platform').annotate(
            first_message=Min('created_at'),
            last_activity=Max('created_at'),
            message_count=Count('id')
        ).order_by('-last_activity')

        sessions = []
        seen_conversations = set()

        for session in session_data:
            conv_id = session['conversation_id']
            if conv_id in seen_conversations:
                continue
            seen_conversations.add(conv_id)

            # Get the first message for title.
            # I-0302 Phase 3 Sub-phase C1: scope at point-of-use even though
            # conv_id was sourced from an already-scoped queryset above.
            first_msg = scope_queryset_chat_conversation(
                user,
                ChatConversation.objects.filter(conversation_id=conv_id),
            ).order_by('created_at').first()

            title = first_msg.session_title if first_msg and first_msg.session_title else None
            if not title and first_msg:
                title = first_msg.user_message[:50] + ('...' if len(first_msg.user_message) > 50 else '')

            sessions.append({
                'conversation_id': conv_id,
                'title': title,
                'platform': session['platform'],
                'started_at': session['first_message'].isoformat() if session['first_message'] else None,
                'last_activity': session['last_activity'].isoformat() if session['last_activity'] else None,
                'message_count': session['message_count'] * 2,  # user + assistant per record
                'can_resume': True,
            })

        return JsonResponse({
            'success': True,
            'sessions': sessions,
            'total': len(sessions)
        })

    except Exception as e:
        logger.error(f"Error getting active sessions: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_session_details(request, conversation_id):
    """
    Get details and history for a specific session.
    """
    from core.models import ChatConversation

    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Authentication required'
        }, status=401)

    try:
        user = request.user

        # Verify user has access to this session.
        # I-0302 Phase 3 Sub-phase C1 (2026-07-10): predicate for
        # workspace-scoped + user-owned branch; Discord fallback OR'd
        # on top (Discord platform is orthogonal to workspaces).
        base_scope = scope_queryset_chat_conversation(
            user,
            ChatConversation.objects.filter(conversation_id=conversation_id),
        )
        if user.discord_id:
            discord_scope = ChatConversation.objects.filter(
                conversation_id=conversation_id,
                discord_user_id=user.discord_id,
            )
            session_msgs = (base_scope | discord_scope).distinct()
        else:
            session_msgs = base_scope

        if not session_msgs.exists():
            return JsonResponse({
                'success': False,
                'error': 'Session not found or access denied'
            }, status=404)

        # Get session info
        first_msg = session_msgs.order_by('created_at').first()
        last_msg = session_msgs.order_by('-created_at').first()

        # Build history
        history = []
        for msg in session_msgs.order_by('created_at')[:50]:  # Limit to 50 messages
            if msg.user_message:
                history.append({
                    'role': 'user',
                    'content': msg.user_message,
                    'timestamp': msg.created_at.isoformat(),
                    'platform': msg.platform,
                })
            if msg.assistant_response:
                history.append({
                    'role': 'assistant',
                    'content': msg.assistant_response,
                    'timestamp': msg.created_at.isoformat(),
                    'agents_used': msg.agents_used,
                })

        title = first_msg.session_title if first_msg.session_title else first_msg.user_message[:50]

        return JsonResponse({
            'success': True,
            'session': {
                'conversation_id': conversation_id,
                'title': title,
                'platform': first_msg.platform,
                'started_at': first_msg.created_at.isoformat(),
                'last_activity': last_msg.created_at.isoformat() if last_msg else None,
                'is_active': first_msg.session_active,
                'message_count': len(history),
            },
            'history': history
        })

    except Exception as e:
        logger.error(f"Error getting session details: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def resume_session(request):
    """
    Resume a session from another platform.
    Marks the session as active and returns the conversation_id for use.
    """
    from core.models import ChatConversation

    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Authentication required'
        }, status=401)

    try:
        data = json.loads(request.body) if request.body else {}
        conversation_id = data.get('conversation_id')

        if not conversation_id:
            return JsonResponse({
                'success': False,
                'error': 'conversation_id required'
            }, status=400)

        user = request.user

        # Verify user has access to this session.
        # I-0302 Phase 3 Sub-phase C1 (2026-07-10): predicate + Discord union.
        base_scope = scope_queryset_chat_conversation(
            user,
            ChatConversation.objects.filter(conversation_id=conversation_id),
        )
        if user.discord_id:
            discord_scope = ChatConversation.objects.filter(
                conversation_id=conversation_id,
                discord_user_id=user.discord_id,
            )
            session_msgs = (base_scope | discord_scope).distinct()
        else:
            session_msgs = base_scope

        if not session_msgs.exists():
            return JsonResponse({
                'success': False,
                'error': 'Session not found or access denied'
            }, status=404)

        # Mark session as active and link to user if not already
        session_msgs.update(session_active=True)

        # Link unlinked Discord messages to user
        if user.discord_id:
            session_msgs.filter(
                discord_user_id=user.discord_id,
                user__isnull=True
            ).update(user=user)

        # Get session summary
        first_msg = session_msgs.order_by('created_at').first()
        history_count = session_msgs.count() * 2

        return JsonResponse({
            'success': True,
            'message': f'Session resumed successfully with {history_count} messages',
            'session': {
                'conversation_id': conversation_id,
                'title': first_msg.session_title or first_msg.user_message[:50],
                'message_count': history_count,
                'original_platform': first_msg.platform,
            }
        })

    except Exception as e:
        logger.error(f"Error resuming session: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def end_session(request):
    """
    End a session (mark as inactive).
    The session history is preserved but won't appear in active sessions.
    """
    from core.models import ChatConversation

    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Authentication required'
        }, status=401)

    try:
        data = json.loads(request.body) if request.body else {}
        conversation_id = data.get('conversation_id')

        if not conversation_id:
            return JsonResponse({
                'success': False,
                'error': 'conversation_id required'
            }, status=400)

        user = request.user

        # Verify user has access to this session.
        # I-0302 Phase 3 Sub-phase C1 (2026-07-10): predicate + Discord union.
        base_scope = scope_queryset_chat_conversation(
            user,
            ChatConversation.objects.filter(conversation_id=conversation_id),
        )
        if user.discord_id:
            discord_scope = ChatConversation.objects.filter(
                conversation_id=conversation_id,
                discord_user_id=user.discord_id,
            )
            session_msgs = (base_scope | discord_scope).distinct()
        else:
            session_msgs = base_scope

        if not session_msgs.exists():
            return JsonResponse({
                'success': False,
                'error': 'Session not found or access denied'
            }, status=404)

        # Mark session as inactive
        updated = session_msgs.update(session_active=False)

        return JsonResponse({
            'success': True,
            'message': f'Session ended. {updated} messages marked as inactive.',
            'conversation_id': conversation_id
        })

    except Exception as e:
        logger.error(f"Error ending session: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_cross_platform_status(request):
    """
    Get cross-platform session status for the current user.
    Shows Discord link status and active sessions per platform.
    """
    from core.models import ChatConversation

    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Authentication required'
        }, status=401)

    try:
        user = request.user
        cutoff = timezone.now() - timedelta(hours=24)

        # Base query.
        # I-0302 Phase 3 Sub-phase C1 (2026-07-10): predicate + Discord union.
        base_scope = scope_queryset_chat_conversation(
            user,
            ChatConversation.objects.filter(
                session_active=True, created_at__gte=cutoff,
            ),
        )
        if user.discord_id:
            discord_scope = ChatConversation.objects.filter(
                session_active=True,
                created_at__gte=cutoff,
                discord_user_id=user.discord_id,
            )
            base_query = (base_scope | discord_scope).distinct()
        else:
            base_query = base_scope

        # Count by platform
        web_sessions = base_query.filter(platform='web').values('conversation_id').distinct().count()
        discord_sessions = base_query.filter(platform='discord').values('conversation_id').distinct().count()

        return JsonResponse({
            'success': True,
            'status': {
                'discord_linked': bool(user.discord_id),
                'discord_username': user.discord_username if hasattr(user, 'discord_username') else None,
                'active_sessions': {
                    'web': web_sessions,
                    'discord': discord_sessions,
                    'total': web_sessions + discord_sessions,
                },
                'can_sync': bool(user.discord_id),
            }
        })

    except Exception as e:
        logger.error(f"Error getting cross-platform status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# Import models at module level for Q objects
from django.db import models
