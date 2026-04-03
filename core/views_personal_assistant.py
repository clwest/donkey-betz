"""
Personal AI Assistant API Views
================================

Session 932: Updated to route through UnifiedPAEntrypoint for consistent behavior
between REST and WebSocket endpoints.
"""

import logging
import time
import uuid
import asyncio
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.db.models import Max, Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

# Legacy import for backward compatibility
try:
    from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant as PersonalAIAssistant
    logger.info("Using Enhanced Personal AI Assistant with database access")
except ImportError:
    from core.personal_ai_assistant import PersonalAIAssistant
    logger.info("Using standard Personal AI Assistant")


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_with_assistant(request):
    """
    Chat with the personal AI assistant.

    Session 932: Now routes through UnifiedPAEntrypoint for consistent behavior.

    Request body:
    {
        "message": "User's message",
        "context": {} // Optional additional context
        "generate_audio": false // Optional TTS
        "use_legacy": false // Force old implementation (for debugging)
    }

    Response:
    {
        "success": true,
        "data": {
            "content": "Response text...",
            "trace_id": "pa-123-abc",
            "tool_runs": [...],
            "audio_url": null,
            "intent": "...",
            "latency_ms": 1500
        }
    }
    """
    try:
        message = request.data.get('message', '').strip()
        context = request.data.get('context', {})
        generate_audio = request.data.get('generate_audio', False)
        use_legacy = request.data.get('use_legacy', False)

        if not message:
            return Response({'error': 'Message is required'}, status=400)

        if len(message) > 8000:
            message = message[:8000]

        # Session 932: Route through UnifiedPA unless legacy mode requested
        if not use_legacy:
            try:
                from core.services.unified_pa_entrypoint import get_unified_pa

                pa = get_unified_pa(request.user)

                # Run async method in sync context
                response = async_to_sync(pa.process_message)(
                    message=message,
                    context=context,
                    generate_audio=generate_audio
                )

                return Response({
                    'success': True,
                    'data': {
                        'content': response.content,
                        'trace_id': response.trace_id,
                        'tool_runs': response.tool_runs,
                        'audio_url': response.audio_url,
                        'intent': response.intent,
                        'routed_to': response.routed_to,
                        'profile_completeness': response.profile_completeness,
                        'latency_ms': response.latency_ms,
                        'error': response.error,
                    }
                })

            except Exception as e:
                logger.warning(
                    f"OLD_PA_FALLBACK_INVOKED: UnifiedPA failed for user={request.user.id}, "
                    f"falling back to legacy PA. Error: {e}"
                )
                # Fall through to legacy implementation

        # Legacy implementation (fallback or explicit)
        logger.info(f"OLD_PA_SERVING: user={request.user.id} use_legacy={use_legacy}")
        assistant = PersonalAIAssistant(request.user)
        response_data = assistant.process_message(message, context)

        return Response({
            'success': True,
            'data': response_data
        })

    except Exception as e:
        import traceback
        logger.error(f"Error in chat_with_assistant: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return Response({
            'error': 'Failed to process message',
            'detail': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_assistant_context(request):
    """Get the current personalized context for the user.

    Session 1078: Stale-first, async rebuild pattern.
    - Fresh hit → return immediately.
    - Fresh miss + stale exists → return stale, enqueue Celery rebuild.
    - Both miss → return minimal skeleton, enqueue Celery rebuild.
    Never blocks the request thread on a cold context build.

    Admin query params (staff only):
        force_rebuild=1  — bypass fresh cache (still reads stale)
        skip_cache=1     — bypass all cache reads AND writes (pure profiling)
        debug=1          — include timing breakdown in response
    """
    import hashlib
    from time import monotonic

    user_id = request.user.id
    user_hash = hashlib.md5(str(user_id).encode()).hexdigest()
    fresh_key = f"pa_ctx:fresh:{user_hash}"
    stale_key = f"pa_ctx:stale:{user_hash}"

    t0_total = monotonic()
    is_staff = getattr(request.user, 'is_staff', False)
    force_rebuild = is_staff and request.query_params.get('force_rebuild') == '1'
    skip_cache = is_staff and request.query_params.get('skip_cache') == '1'
    include_debug = is_staff and request.query_params.get('debug') == '1'

    def _enqueue_rebuild(reason):
        """Fire-and-forget Celery rebuild with stampede lock."""
        try:
            from core.tasks import rebuild_pa_context_task
            rebuild_pa_context_task.delay(user_id, reason=reason)
        except Exception as exc:
            logger.warning("PA_CONTEXT_METRICS enqueue_failed user_id=%s error=%s", user_id, str(exc))

    def _minimal_skeleton():
        """Safe default when no cache exists at all."""
        return {
            'user_id': str(user_id),
            'username': request.user.username,
            'personalization': {'profile_completeness': 0},
            '_skeleton': True,
        }

    # ── 1. Try fresh cache ──────────────────────────────────────────────
    if not skip_cache and not force_rebuild:
        t0_cache = monotonic()
        fresh = cache.get(fresh_key)
        cache_get_ms = int((monotonic() - t0_cache) * 1000)

        if fresh is not None:
            total_ms = int((monotonic() - t0_total) * 1000)
            logger.info(
                "PA_CONTEXT_METRICS status=fresh_hit user_id=%s cache_get_ms=%s total_ms=%s",
                user_id, cache_get_ms, total_ms,
            )
            resp = {'success': True, 'context': fresh}
            if include_debug:
                resp['_debug'] = {'cache': 'fresh_hit', 'cache_get_ms': cache_get_ms, 'total_ms': total_ms}
            return Response(resp)

    # ── 2. Fresh miss — try stale, enqueue rebuild ──────────────────────
    stale = None if skip_cache else cache.get(stale_key)

    if stale is not None:
        _enqueue_rebuild('fresh_miss')
        total_ms = int((monotonic() - t0_total) * 1000)
        logger.info(
            "PA_CONTEXT_METRICS status=stale_served user_id=%s total_ms=%s enqueue_rebuild=true",
            user_id, total_ms,
        )
        resp = {'success': True, 'context': stale}
        if include_debug:
            resp['_debug'] = {'cache': 'stale_served', 'total_ms': total_ms, 'rebuild_enqueued': True}
        return Response(resp)

    # ── 3. Both miss — return skeleton, enqueue rebuild ─────────────────
    _enqueue_rebuild('cold_start')
    skeleton = _minimal_skeleton()
    total_ms = int((monotonic() - t0_total) * 1000)
    logger.warning(
        "PA_CONTEXT_METRICS status=skeleton user_id=%s total_ms=%s enqueue_rebuild=true",
        user_id, total_ms,
    )
    resp = {'success': True, 'context': skeleton}
    if include_debug:
        resp['_debug'] = {'cache': 'skeleton', 'total_ms': total_ms, 'rebuild_enqueued': True}
    return Response(resp)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_learning_summary(request):
    """Get summary of what the assistant has learned about the user."""
    try:
        # Create assistant fresh each time (contains unpickleable objects like OpenAI client)
        assistant = PersonalAIAssistant(request.user)

        # Get learning summary
        summary = assistant.get_learning_summary()

        return Response({
            'success': True,
            'summary': summary
        })

    except Exception as e:
        logger.error(f"Error getting learning summary: {e}")
        return Response({
            'error': 'Failed to get summary',
            'detail': str(e)
        }, status=500)


# =============================================================================
# SESSION 932: UNIFIED PA ENDPOINTS (No Legacy Fallback)
# =============================================================================

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unified_pa_chat(request):
    """
    Session 932: Chat through UnifiedPAEntrypoint exclusively.
    Session 974b: Dispatches to Celery task for async processing to avoid
    Railway proxy timeouts. Returns task_id for polling via pa_chat_status.

    Request body:
    {
        "message": "User's message",
        "context": {} // Optional additional context
        "generate_audio": false // Optional TTS
        "conversation_id": "pa-xxxxx" // Optional conversation ID
    }

    Response:
    {
        "success": true,
        "task_id": "celery-task-uuid",
        "status": "processing"
    }
    """
    try:
        message = request.data.get('message', '').strip()
        context = request.data.get('context', {})
        generate_audio = request.data.get('generate_audio', False)
        conversation_id = request.data.get('conversation_id')
        source = request.data.get('source', 'web')
        platform = request.data.get('platform', 'web')

        if not message:
            return Response({'error': 'Message is required'}, status=400)

        if len(message) > 8000:
            message = message[:8000]

        # VIP scoping — inject workspace context and restrict PA behavior
        workspace_id = None
        try:
            from core.vip_scope import get_vip_scope
            vip_scope = get_vip_scope(request)
            if vip_scope.is_vip:
                context = context or {}
                if vip_scope.workspace_id:
                    workspace_id = vip_scope.workspace_id
                context['vip_mode'] = True
                context['vip_recipient_name'] = vip_scope.recipient_name or ''
                context['vip_system_directive'] = (
                    'CRITICAL: You are speaking with a VIP demo viewer in a SCOPED workspace. '
                    'This person was personally invited by Chris to preview specific deliverables. '
                    '\n\nRULES (MUST follow):'
                    '\n1. ONLY discuss the deliverables and content in their workspace. Use deliverable_tool to look up what is there.'
                    '\n2. Do NOT mention or describe platform features they cannot access (Creative Studio, Intelligence Desks, Sports betting, Advisors, Image/Video generation, etc).'
                    '\n3. Do NOT list navigation options, dashboards, or pages — they only have Home and Library.'
                    '\n4. Do NOT discuss internal operations, other users, costs, infrastructure, API keys, or system errors.'
                    '\n5. Do NOT use platform_awareness_tool — it returns global data not relevant to this VIP.'
                    '\n6. When asked "what can I do here", describe the DELIVERABLES in their workspace and offer to explain any of them in detail.'
                    '\n7. If asked about pricing, business terms, or partnerships, say "Chris will follow up with you directly on that."'
                    '\n8. Be warm, professional, and concise. You represent Chris and the Donkey Betz brand.'
                    '\n9. If they ask about the technology behind the platform, you can explain at a high level (AI agents, knowledge pipeline, etc) but do NOT expose specific agent names, counts, or internal architecture.'
                )
        except Exception:
            pass

        # Session 1077: Inject workspace context so PA knows which workspace is active
        workspace_id = request.data.get('workspace_id') or workspace_id
        if workspace_id:
            try:
                from core.models import ProjectWorkspace
                workspace = ProjectWorkspace.objects.get(id=workspace_id)
                context = context or {}
                context['workspace'] = {
                    'id': str(workspace.id),
                    'name': workspace.name,
                    'slug': getattr(workspace, 'slug', ''),
                }
            except Exception:
                logger.warning(f"PA chat received invalid workspace_id: {workspace_id}")

        from core.tasks import process_pa_chat_task

        task = process_pa_chat_task.delay(
            user_id=request.user.id,
            message=message,
            context=context,
            generate_audio=generate_audio,
            conversation_id=conversation_id,
            source=source,
            platform=platform,
        )

        # Dispatch autonomous Claude Code agent if message addresses it
        # This runs at the VIEW level (synchronous, before returning to client)
        # so it doesn't depend on the PA task completing first.
        try:
            from core.services.claude_code_agent import should_claude_code_respond
            if should_claude_code_respond(message, source):
                from core.tasks import claude_code_agent_respond
                claude_code_agent_respond.delay(conversation_id, message, source)
                logger.info(f"[ClaudeCodeAgent] Dispatched from view for conversation {conversation_id}")
        except Exception as e:
            logger.warning(f"[ClaudeCodeAgent] View dispatch failed: {e}")

        return Response({
            'success': True,
            'task_id': str(task.id),
            'status': 'processing',
        })

    except Exception as e:
        import traceback
        logger.error(f"Error in unified_pa_chat: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return Response({
            'success': False,
            'error': 'Failed to process message',
            'detail': str(e),
            'trace_id': None,
        }, status=500)


def _should_trigger_pa(message_text: str) -> bool:
    """Check if a message mentions Rigby and should trigger PA processing."""
    import re
    text = message_text.lower().strip()
    patterns = [
        r'\brigby\b',        # "rigby" as a word
        r'@rigby',           # explicit @mention
    ]
    return any(re.search(p, text) for p in patterns)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pa_conversation_post_message(request, conversation_id):
    """
    Store-only message endpoint for 3-way chat.

    Posts a message to the conversation without triggering PA processing,
    UNLESS the message mentions @rigby or 'Rigby'.

    Used by Claude Code to participate in conversations directly.
    """
    try:
        message = request.data.get('message', '').strip()
        source = request.data.get('source', 'web')
        trigger_pa = request.data.get('trigger_pa', None)  # Explicit override

        if not message:
            return Response({'error': 'Message is required'}, status=400)

        from core.models import ChatConversation

        # Security: verify user has access to this conversation (or is creating a new one)
        if not request.user.is_staff:
            existing = ChatConversation.objects.filter(conversation_id=conversation_id).first()
            if existing and existing.user_id and existing.user_id != request.user.id:
                return Response({'error': 'Conversation not found'}, status=404)

        # Auto-detect whether to trigger PA if not explicitly set
        if trigger_pa is None:
            trigger_pa = _should_trigger_pa(message)

        # Store the message
        chat_row = ChatConversation.objects.create(
            user=request.user,
            conversation_id=conversation_id,
            user_message=message,
            assistant_response='',  # No response yet (store-only)
            source=source,
            platform='cli' if source == 'claude-code' else 'web',
            metadata={'store_only': not trigger_pa, 'mentions_pa': trigger_pa},
        )

        # Broadcast to WebSocket for real-time delivery
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"pa_conversation_{conversation_id}",
                    {
                        "type": "message.created",
                        "message": {
                            "id": str(chat_row.id),
                            "role": "user",
                            "content": message,
                            "source": source,
                            "timestamp": chat_row.created_at.isoformat(),
                        }
                    }
                )
        except Exception:
            pass  # WebSocket broadcast is non-critical

        # Dispatch autonomous Claude Code agent if message is addressed to it
        try:
            from core.tasks import claude_code_agent_respond
            from core.services.claude_code_agent import should_claude_code_respond
            if should_claude_code_respond(message, source):
                claude_code_agent_respond.delay(conversation_id, message, source)
        except Exception:
            pass  # Non-critical

        # If @rigby mentioned, trigger PA processing
        task_id = None
        if trigger_pa:
            from core.tasks import process_pa_chat_task
            context = request.data.get('context', {})
            context['source'] = source
            context['already_stored'] = True  # Prevent duplicate user message broadcast
            task = process_pa_chat_task.delay(
                user_id=str(request.user.id),
                message=message,
                context=context,
                conversation_id=conversation_id,
                source=source,
                platform='cli' if source == 'claude-code' else 'web',
            )
            task_id = str(task.id)

        return Response({
            'success': True,
            'message_id': str(chat_row.id),
            'conversation_id': conversation_id,
            'trigger_pa': trigger_pa,
            'task_id': task_id,
            'source': source,
        })

    except Exception as e:
        logger.error(f"Error in pa_conversation_post_message: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pa_conversation_messages(request, conversation_id):
    """
    Get recent messages for a conversation (for CLI watch mode).
    Supports ?after=<message_id> for incremental polling.
    """
    from core.models import ChatConversation

    # Security: verify user has access to this conversation
    if not request.user.is_staff:
        has_access = ChatConversation.objects.filter(
            conversation_id=conversation_id, user=request.user
        ).exists()
        if not has_access:
            return Response({'error': 'Conversation not found'}, status=404)

    after_id = request.query_params.get('after')
    limit = min(int(request.query_params.get('limit', 50)), 100)

    qs = ChatConversation.objects.filter(conversation_id=conversation_id).order_by('created_at')

    if after_id:
        try:
            after_row = ChatConversation.objects.get(id=after_id)
            qs = qs.filter(created_at__gt=after_row.created_at)
        except ChatConversation.DoesNotExist:
            pass

    messages = []
    for row in qs.order_by('-created_at')[:limit]:
        if row.user_message:
            messages.append({
                'id': str(row.id),
                'role': 'user',
                'content': row.user_message,
                'source': row.source or 'web',
                'timestamp': row.created_at.isoformat(),
            })
        if row.assistant_response:
            messages.append({
                'id': f"{row.id}-response",
                'role': 'assistant',
                'content': row.assistant_response,
                'source': 'pa',
                'timestamp': row.created_at.isoformat(),
            })

    messages.reverse()  # Chronological order

    return Response({
        'success': True,
        'conversation_id': conversation_id,
        'messages': messages[-limit:],
        'count': len(messages),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pa_activity_feed(request):
    """
    Rigby's activity feed — shows actual tool calls with timestamps.
    Proves what Rigby is really doing vs what he says he's doing.

    Query params:
    - hours: lookback window (default 1)
    - limit: max results (default 50)
    - agent: filter by agent name (default: PersonalAssistant)
    """
    from core.models_tool_calls import ToolCallRecord
    from django.utils import timezone
    from datetime import timedelta

    hours = int(request.query_params.get('hours', 1))
    limit = min(int(request.query_params.get('limit', 50)), 200)
    agent_filter = request.query_params.get('agent', '')

    cutoff = timezone.now() - timedelta(hours=hours)
    qs = ToolCallRecord.objects.filter(created_at__gte=cutoff).order_by('-created_at')

    if agent_filter:
        qs = qs.filter(agent_name__icontains=agent_filter)

    records = []
    for r in qs[:limit]:
        records.append({
            'id': str(r.id),
            'agent': r.agent_name,
            'tool': r.tool_name,
            'success': r.success,
            'latency_ms': r.latency_ms,
            'timestamp': r.created_at.isoformat(),
            'parameters_preview': str(r.parameters)[:200] if r.parameters else '',
            'result_preview': str(r.result_summary)[:200] if r.result_summary else '',
        })

    # Summary stats
    total_calls = qs.count()
    tool_counts = {}
    for r in qs[:500]:
        tool_counts[r.tool_name] = tool_counts.get(r.tool_name, 0) + 1

    return Response({
        'success': True,
        'window_hours': hours,
        'total_calls': total_calls,
        'tool_breakdown': dict(sorted(tool_counts.items(), key=lambda x: -x[1])[:15]),
        'recent_calls': records,
        'message': f'Rigby made {total_calls} tool calls in the last {hours} hour(s)' if total_calls > 0
                   else f'Rigby has made NO tool calls in the last {hours} hour(s) — he may be idle',
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pa_chat_status(request, task_id):
    """
    Session 974b: Poll async PA chat task status.

    Returns processing/completed/failed with full response on completion.
    """
    try:
        from celery.result import AsyncResult
        from celery import current_app

        result = AsyncResult(task_id, app=current_app)

        if result.successful():
            task_result = result.result or {}
            return Response({
                'success': True,
                'status': 'completed',
                **task_result,
            })
        elif result.failed():
            return Response({
                'success': False,
                'status': 'failed',
                'error': str(result.result) if result.result else 'Processing failed',
            })
        elif result.state == 'PENDING':
            # Session 1076: PENDING means Celery has no record of this task —
            # either it was never dispatched, or the result expired from Redis.
            # Return failed instead of processing to stop infinite UI polling.
            return Response({
                'success': False,
                'status': 'failed',
                'error': 'Task not found or result expired. Please retry.',
            })
        else:
            return Response({
                'success': True,
                'status': 'processing',
            })

    except Exception as e:
        logger.error(f"Error checking PA chat status: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unified_pa_context(request):
    """
    Session 932: Get context from UnifiedPAEntrypoint.

    Returns the context that would be used for the next message.

    Response:
    {
        "success": true,
        "user": {"name": "...", "profile_completeness": 65},
        "system_stats": {"agents": 76, "spiders": 77, ...},
        "available_tools": ["image_generation", "web_search", ...]
    }
    """
    # First-login onboarding check — fires once per new user
    try:
        from core.services.user_onboarding_service import is_first_login, onboard_new_user
        if is_first_login(request.user):
            onboard_new_user(request.user)
            logger.info("Auto-onboarded new user: %s", request.user.username)
    except Exception as e:
        logger.debug("Onboarding check skipped: %s", e)

    try:
        from core.services.unified_pa_entrypoint import get_unified_pa

        pa = get_unified_pa(request.user)

        # Get profile completeness
        profile_completeness = None
        try:
            if pa.profile_service:
                score = pa.profile_service.get_completeness_score(request.user)
                profile_completeness = int(score * 100)
        except Exception:
            pass

        # Get system stats
        system_stats = {}
        try:
            from core.models_unified_system import Agent, Advisor
            from ai_core.spiders.spider_registry import spider_registry

            system_stats = {
                'agents': Agent.objects.count(),
                'advisors': Advisor.objects.count(),
                'spiders': len(spider_registry.list_spiders()),
            }
        except Exception:
            pass

        # Get available tools from dispatcher
        available_tools = []
        try:
            available_tools = list(pa.tool_dispatcher.tools.keys())
        except Exception:
            pass

        return Response({
            'success': True,
            'user': {
                'username': request.user.username,
                'first_name': request.user.first_name or request.user.username,
                'profile_completeness': profile_completeness,
            },
            'system_stats': system_stats,
            'available_tools': available_tools,
            'tool_count': len(available_tools),
        })

    except Exception as e:
        logger.error(f"Error in unified_pa_context: {e}")
        return Response({
            'success': False,
            'error': str(e),
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def provide_feedback(request):
    """
    Provide feedback on assistant's response.

    Request body:
    {
        "message_id": "ID of the message",
        "feedback": "positive" or "negative",
        "details": "Optional feedback details"
    }
    """
    try:
        feedback = request.data.get('feedback')
        details = request.data.get('details', '')

        if feedback not in ['positive', 'negative']:
            return Response({'error': 'Invalid feedback type'}, status=400)

        # Create assistant fresh each time (contains unpickleable objects like OpenAI client)
        assistant = PersonalAIAssistant(request.user)

        # Process feedback (enhance learning)
        if assistant.learning_history:
            last_interaction = assistant.learning_history[-1]
            last_interaction['feedback'] = feedback
            last_interaction['feedback_details'] = details

            # Adjust confidence based on feedback
            if feedback == 'positive':
                last_interaction['confidence'] = min(last_interaction.get('confidence', 0.5) * 1.1, 1.0)
            else:
                last_interaction['confidence'] = max(last_interaction.get('confidence', 0.5) * 0.9, 0.1)

            # Re-learn from the interaction
            assistant.learn_from_interaction(
                last_interaction['message'],
                last_interaction['response'],
                last_interaction
            )

        return Response({
            'success': True,
            'message': 'Feedback recorded'
        })

    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        return Response({
            'error': 'Failed to record feedback',
            'detail': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_assistant(request):
    """Reset the assistant's learning for the user."""
    try:
        cache_key = f'assistant_{request.user.id}'
        cache.delete(cache_key)

        # Clear user embeddings
        from core.models import UserEmbedding
        UserEmbedding.objects.filter(user=request.user).delete()

        # Clear behavior patterns from profile
        from core.models import ExtendedUserProfile
        try:
            profile = ExtendedUserProfile.objects.get(user=request.user)
            metadata = profile.metadata or {}
            metadata.pop('behavior_patterns', None)
            profile.metadata = metadata
            profile.save()
        except ExtendedUserProfile.DoesNotExist:
            pass

        return Response({
            'success': True,
            'message': 'Assistant reset successfully'
        })

    except Exception as e:
        logger.error(f"Error resetting assistant: {e}")
        return Response({
            'error': 'Failed to reset assistant',
            'detail': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def voice_to_assistant(request):
    """
    Voice input for Personal Assistant.
    Session 113: Voice Input MVP

    Combines audio transcription + assistant chat in one endpoint.

    Request:
    - multipart/form-data with 'audio' file (webm/m4a/wav)
    - Optional 'session_id' for conversation threading

    Response:
    {
        "success": true,
        "user_text": "transcribed text...",
        "assistant_message": {
            "response": "...",
            "suggestions": [...],
            "actions": [...],
            "confidence": 0.95
        }
    }
    """
    try:
        # Step 1: Get and validate audio file
        audio_file = request.FILES.get('audio')

        if not audio_file:
            return Response({
                'error': 'No audio file provided'
            }, status=400)

        logger.info(f"🎤 Voice input from {request.user.username} ({audio_file.size} bytes)")

        # Step 2: Transcribe audio using OpenAI Whisper
        # (Reusing logic from views_image.py:6466)
        try:
            import os
            from openai import OpenAI
            from io import BytesIO

            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

            # Convert Django InMemoryUploadedFile to BytesIO for OpenAI SDK
            audio_file.seek(0)
            audio_bytes = audio_file.read()
            audio_file_like = BytesIO(audio_bytes)

            # Always use .webm extension (frontend sends audio/webm format)
            audio_file_like.name = "recording.webm"

            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file_like,
                language="en"  # Can be removed to auto-detect
            )

            user_text = transcript.text.strip()
            logger.info(f"✅ Transcribed: '{user_text[:100]}...'")

        except Exception as e:
            error_str = str(e)
            logger.error(f"❌ Transcription failed: {error_str}")
            # Distinguish client errors (bad audio) from server errors
            if 'could not be decoded' in error_str or 'format is not supported' in error_str:
                return Response({
                    'error': 'Audio format not supported. Please use webm, m4a, or wav.',
                    'details': error_str,
                    'code': 'BAD_AUDIO_FORMAT',
                }, status=400)
            if 'rate limit' in error_str.lower() or '429' in error_str:
                return Response({
                    'error': 'Transcription service temporarily unavailable. Please try again.',
                    'details': error_str,
                    'code': 'RATE_LIMITED',
                }, status=429)
            return Response({
                'error': 'Failed to transcribe audio',
                'details': error_str,
                'code': 'TRANSCRIPTION_FAILED',
            }, status=500)

        # Step 3: Send transcribed text to Personal Assistant
        # (Reusing logic from chat_with_assistant)
        try:
            # Create assistant via factory to avoid property/inheritance conflicts
            from core.services.assistant_factory import get_assistant
            assistant = get_assistant(request.user)

            # Process message with optional context
            context = request.data.get('context', {})
            context['input_method'] = 'voice'  # Mark as voice input

            response_data = assistant.process_message(user_text, context)

            logger.info(f"✅ Assistant responded to voice input")

            # Step 4: Return combined result
            return Response({
                'success': True,
                'user_text': user_text,
                'assistant_message': response_data
            })

        except Exception as e:
            logger.error(f"❌ Assistant processing failed: {str(e)}")
            # Return partial success - transcription worked
            return Response({
                'success': False,
                'user_text': user_text,
                'error': 'Transcription succeeded but assistant failed to respond',
                'details': str(e)
            }, status=500)

    except Exception as e:
        import traceback
        logger.error(f"❌ Voice input failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return Response({
            'error': 'Failed to process voice input',
            'details': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def voice_interview_response(request):
    """
    Session 456: Voice input for Profile Interview.

    Uses OpenAI Whisper to transcribe voice and submit as interview response.

    Request:
    - multipart/form-data with 'audio' file (webm/m4a/wav)

    Response:
    {
        "success": true,
        "transcribed_text": "what the user said...",
        "acknowledgment": "Great answer!",
        "question": { next question data },
        "state": { interview state }
    }
    """
    try:
        # Step 1: Get and validate audio file
        audio_file = request.FILES.get('audio')

        if not audio_file:
            return Response({
                'error': 'No audio file provided'
            }, status=400)

        logger.info(f"🎤 Voice interview input from {request.user.username} ({audio_file.size} bytes)")

        # Step 2: Transcribe audio using OpenAI Whisper
        try:
            import os
            from openai import OpenAI
            from io import BytesIO

            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

            # Convert Django InMemoryUploadedFile to BytesIO for OpenAI SDK
            audio_file.seek(0)
            audio_bytes = audio_file.read()
            audio_file_like = BytesIO(audio_bytes)

            # Always use .webm extension (frontend sends audio/webm format)
            audio_file_like.name = "recording.webm"

            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file_like,
                language="en"
            )

            transcribed_text = transcript.text.strip()
            logger.info(f"✅ Interview voice transcribed: '{transcribed_text[:100]}...'")

            if not transcribed_text:
                return Response({
                    'error': 'Could not understand audio. Please speak more clearly.',
                    'transcribed_text': ''
                }, status=400)

        except Exception as e:
            logger.error(f"❌ Interview transcription failed: {str(e)}")
            return Response({
                'error': 'Failed to transcribe audio',
                'details': str(e)
            }, status=500)

        # Step 3: Submit transcribed text as interview response
        try:
            from intelligence.personal_assistant_interviewer import personal_assistant_interviewer
            from asgiref.sync import async_to_sync

            user_id = str(request.user.id)

            # Process the response through the interview system
            # Use async_to_sync which properly handles Django's async context
            result = async_to_sync(personal_assistant_interviewer.process_response)(user_id, transcribed_text)

            if result.get('error'):
                return Response({
                    'error': result['error'],
                    'transcribed_text': transcribed_text
                }, status=400)

            logger.info(f"✅ Interview voice response processed successfully")

            return Response({
                'success': True,
                'transcribed_text': transcribed_text,
                'acknowledgment': result.get('acknowledgment', ''),
                'question': result.get('question'),
                'interview_complete': result.get('interview_complete', False),
                'profile': result.get('profile'),
                'final_message': result.get('final_message'),
                'state': result.get('state')
            })

        except Exception as e:
            logger.error(f"❌ Interview processing failed: {str(e)}")
            return Response({
                'success': False,
                'transcribed_text': transcribed_text,
                'error': 'Transcription succeeded but interview processing failed',
                'details': str(e)
            }, status=500)

    except Exception as e:
        import traceback
        logger.error(f"❌ Voice interview failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return Response({
            'error': 'Failed to process voice input',
            'details': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transcribe_only(request):
    """
    Session 456: Transcribe audio only (no interview processing).

    Useful for getting transcription before submitting to interview.

    Request:
    - multipart/form-data with 'audio' file (webm/m4a/wav)

    Response:
    {
        "success": true,
        "text": "transcribed text..."
    }
    """
    try:
        audio_file = request.FILES.get('audio')

        if not audio_file:
            return Response({
                'error': 'No audio file provided'
            }, status=400)

        logger.info(f"🎤 Transcribe-only request from {request.user.username} ({audio_file.size} bytes)")

        import os
        from openai import OpenAI
        from io import BytesIO

        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        audio_file.seek(0)
        audio_bytes = audio_file.read()
        audio_file_like = BytesIO(audio_bytes)
        audio_file_like.name = "recording.webm"

        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file_like,
            language="en"
        )

        transcribed_text = transcript.text.strip()
        logger.info(f"✅ Transcribed: '{transcribed_text[:100]}...'")

        return Response({
            'success': True,
            'text': transcribed_text
        })

    except Exception as e:
        logger.error(f"❌ Transcription failed: {str(e)}")
        return Response({
            'error': 'Failed to transcribe audio',
            'details': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_attention_items(request):
    """
    Session 574: Get attention items for the PA UI.
    Session 663: Enhanced with explanation, severity, location fields.

    Returns actionable items from SystemStateAggregator that need user attention.
    Each item can be clicked to execute via PA.
    """
    try:
        from core.services.system_state_aggregator import get_system_state_aggregator

        aggregator = get_system_state_aggregator()
        items = aggregator.get_attention_items()

        # Convert to serializable format
        attention_items = []
        for item in items[:10]:  # Max 10 items
            attention_items.append({
                'id': item.id,
                'section': item.section,
                'category': item.category,
                'priority': item.priority,
                'title': item.title[:80] if item.title else '',
                'summary': item.summary[:150] if item.summary else '',
                'action_url': item.action_url if hasattr(item, 'action_url') else '',
                # Suggested action for click-to-execute
                'suggested_action': _get_suggested_action(item),
                # Session 663: New enhanced fields from SystemIntelligenceAgent work
                'severity': getattr(item, 'severity', 'info'),  # info, warning, critical
                'explanation': getattr(item, 'explanation', '')[:300] if getattr(item, 'explanation', '') else '',
                'recommended_action': getattr(item, 'recommended_action', '')[:200] if getattr(item, 'recommended_action', '') else '',
                'location': getattr(item, 'location', ''),
            })

        # Session 663: Add summary counts by severity
        severity_counts = {
            'critical': len([i for i in items if getattr(i, 'severity', 'info') == 'critical']),
            'warning': len([i for i in items if getattr(i, 'severity', 'info') == 'warning']),
            'info': len([i for i in items if getattr(i, 'severity', 'info') == 'info']),
        }

        return Response({
            'success': True,
            'items': attention_items,
            'count': len(attention_items),
            'severity_counts': severity_counts,
        })

    except Exception as e:
        logger.error(f"Error getting attention items: {e}")
        return Response({
            'success': False,
            'items': [],
            'error': str(e)
        })


def _get_suggested_action(item):
    """Generate a suggested action command for an attention item.

    Session 574: These actions are designed to work with PA routing patterns.
    They should be clear commands that the PA can understand and execute.
    """
    section = item.section.lower() if item.section else ''
    title = item.title or 'this item'
    clean_title = title[:50].strip()

    # Session 574: Use patterns that match PA's action detection
    # Check if this is a Boardroom decision (has "Boardroom:" prefix)
    if clean_title.startswith('Boardroom:'):
        # Boardroom items - review and decide pattern (avoid triggering content agents)
        topic = clean_title.replace('Boardroom:', '').strip()
        return f"Review this pending decision and summarize the key points: {topic}"
    elif section == 'research':
        # Research items - ask for follow-up research
        return f"What are the latest developments regarding {clean_title}?"
    elif section == 'command_center':
        # Command center items - triage/review pattern
        return f"Triage and create action plan for: {clean_title}"
    elif section == 'autonomous':
        # Autonomous items - check status pattern
        return f"What is the status of {clean_title}? Summarize and suggest next steps."
    else:
        # Default - simple task pattern
        return f"Help me with: {clean_title}"


# =============================================================================
# SESSION 932: UNIFIED ATTENTION AGGREGATOR
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unified_attention(request):
    """
    Session 932: Get unified attention from all sources.

    Combines:
    - System attention: Platform health metrics (curated, ~17 items)
    - Human attention: User notifications, decisions, alerts (~600+ items)

    Query params:
        include_system: bool (default true)
        include_human: bool (default true)
        urgency: comma-separated list (critical,high,medium,low)
        limit: int (default 50)
        stats_only: bool (default false) - only return counts, not items

    Returns:
        {
            "system_attention": {"count": 17, "items": [...], "source": "platform_health"},
            "human_attention": {"count": 609, "items": [...], "source": "user_notifications"},
            "combined_urgent": 5,
            "total_count": 626,
            "by_urgency": {"critical": 2, "high": 3, "medium": 10, "low": 5}
        }
    """
    try:
        from core.services.attention_aggregator import get_attention_aggregator

        aggregator = get_attention_aggregator(request.user)

        # Parse query params
        include_system = request.GET.get('include_system', 'true').lower() == 'true'
        include_human = request.GET.get('include_human', 'true').lower() == 'true'
        urgency_param = request.GET.get('urgency', '')
        limit = int(request.GET.get('limit', 50))
        stats_only = request.GET.get('stats_only', 'false').lower() == 'true'

        urgency_filter = None
        if urgency_param:
            urgency_filter = [u.strip() for u in urgency_param.split(',')]

        # Stats only mode - fast response
        if stats_only:
            stats = aggregator.get_stats()
            return Response({
                'success': True,
                **stats
            })

        # Full response
        result = aggregator.get_unified_attention(
            include_system=include_system,
            include_human=include_human,
            urgency_filter=urgency_filter,
            limit_per_source=limit,
        )

        return Response({
            'success': True,
            **result
        })

    except Exception as e:
        logger.error(f"Error getting unified attention: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e),
            'system_attention': None,
            'human_attention': None,
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_attention_stats(request):
    """
    Session 932: Get attention statistics without full items.

    Fast endpoint for dashboard widgets that only need counts.

    Returns:
        {
            "human_attention": {"pending": 45, "total": 609, "by_urgency": {...}},
            "system_attention": {"count": 17, "by_urgency": {...}},
            "combined": {"pending": 62, "urgent": 5}
        }
    """
    try:
        from core.services.attention_aggregator import get_attention_aggregator

        aggregator = get_attention_aggregator(request.user)
        stats = aggregator.get_stats()

        return Response({
            'success': True,
            **stats
        })

    except Exception as e:
        logger.error(f"Error getting attention stats: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# SESSION 974: PA CONVERSATION HISTORY ENDPOINTS
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pa_conversations(request):
    """
    Session 974: List PA conversations for the current user.

    Returns distinct conversation sessions with title, message count,
    last message timestamp, and a preview of the first message.
    """
    try:
        from core.models import ChatConversation

        # Find conversation_ids the user has participated in
        user_conv_ids = (
            ChatConversation.objects
            .filter(user=request.user).exclude(platform='discord')
            .values_list('conversation_id', flat=True)
            .distinct()
        )
        # Show ALL messages in those conversations (includes claude-code, ops_digest, etc.)
        conversations = (
            ChatConversation.objects
            .filter(conversation_id__in=user_conv_ids)
            .values('conversation_id')
            .annotate(
                message_count=Count('id'),
                last_message_at=Max('created_at'),
            )
            .order_by('-last_message_at')[:50]
        )

        results = []
        for conv in conversations:
            first_row = ChatConversation.objects.filter(
                conversation_id=conv['conversation_id']
            ).order_by('created_at').first()

            # Session 998B: Guard against None user_message
            user_msg = (first_row.user_message or '') if first_row else ''
            title = 'Untitled'
            if first_row:
                if first_row.session_title:
                    title = first_row.session_title
                elif user_msg:
                    title = user_msg[:50] + ('...' if len(user_msg) > 50 else '')

            results.append({
                'conversation_id': conv['conversation_id'],
                'title': title,
                'message_count': conv['message_count'],
                'last_message_at': conv['last_message_at'].isoformat() if conv['last_message_at'] else None,
                'preview': user_msg[:80],
            })

        return Response({
            'success': True,
            'conversations': results,
            'total': len(results),
        })

    except Exception as e:
        logger.error(f"Error listing PA conversations: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'conversations': [],
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pa_conversation(request, conversation_id):
    """
    Session 974: Load all messages for a specific conversation.

    Each ChatConversation row contains a user_message + assistant_response pair,
    which we expand into separate message objects for the frontend.
    """
    try:
        from core.models import ChatConversation

        # Access control: user must have at least one message in the conversation,
        # or be staff/superuser.  Prevents cross-user conversation leakage.
        if not request.user.is_staff:
            has_access = ChatConversation.objects.filter(
                conversation_id=conversation_id,
                user=request.user,
            ).exists()
            if not has_access:
                # Allow access to brand-new conversations (no rows yet)
                if not ChatConversation.objects.filter(conversation_id=conversation_id).exists():
                    if conversation_id.startswith('pa-'):
                        return Response({
                            'success': True,
                            'conversation_id': conversation_id,
                            'title': 'New Conversation',
                            'messages': [],
                        })
                return Response({
                    'success': False,
                    'error': 'Conversation not found',
                }, status=404)

        rows = ChatConversation.objects.filter(
            conversation_id=conversation_id,
        ).order_by('created_at')

        if not rows.exists():
            # Session 1089: New conversations have no DB rows until first message.
            # Frontend polling hits this immediately after create — return empty
            # conversation instead of 404 to avoid console errors.
            if conversation_id.startswith('pa-'):
                return Response({
                    'success': True,
                    'conversation_id': conversation_id,
                    'title': 'New Conversation',
                    'messages': [],
                })
            return Response({
                'success': False,
                'error': 'Conversation not found',
            }, status=404)

        first_row = rows.first()
        title = first_row.session_title if first_row and first_row.session_title else 'Untitled'

        messages = []
        for row in rows:
            # Session 1074: Use real source field, fallback to metadata for old rows
            meta = row.metadata or {}
            source_label = getattr(row, 'source', None) or meta.get('source', row.platform)
            structured_type = meta.get('structured_type')

            messages.append({
                'id': f'{row.pk}-user',
                'role': 'user',
                'content': row.user_message,
                'timestamp': row.created_at.isoformat(),
                'source': source_label,
                **({"structured_type": structured_type} if structured_type else {}),
            })
            if row.assistant_response:
                messages.append({
                    'id': f'{row.pk}-assistant',
                    'role': 'assistant',
                    'content': row.assistant_response,
                    'timestamp': row.created_at.isoformat(),
                    'tools_used': row.agents_used or [],
                    'source': 'pa',
                })

        return Response({
            'success': True,
            'conversation_id': conversation_id,
            'title': title,
            'messages': messages,
        })

    except Exception as e:
        logger.error(f"Error loading PA conversation {conversation_id}: {e}")
        return Response({
            'success': False,
            'error': str(e),
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_pa_conversation(request):
    """
    Session 974: Start a new PA conversation.

    Generates a new conversation_id. No DB row is created until the first
    message is sent — this just reserves the ID.
    """
    try:
        conversation_id = f"pa-{uuid.uuid4().hex[:12]}"
        return Response({
            'success': True,
            'conversation_id': conversation_id,
        })
    except Exception as e:
        logger.error(f"Error creating PA conversation: {e}")
        return Response({
            'success': False,
            'error': str(e),
        }, status=500)


# =============================================================================
# Session Health — Context-Aware Session Management
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def session_health(request, conversation_id):
    """
    Get the health/freshness score for a conversation.

    Returns a score (0-100), recommendation, reasons, auto-summary,
    and a starter prompt for creating a fresh session.
    """
    try:
        from core.services.session_health_service import get_session_health
        health = get_session_health(conversation_id, request.user.id)
        return Response({'success': True, **health})
    except Exception as e:
        logger.error(f"Error checking session health: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# SESSION 977: Boardroom Maintenance Trigger
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_boardroom_maintenance(request):
    """
    Session 977: Run all three boardroom maintenance tasks immediately.
    Requires authentication. Runs synchronously (not via Celery) for instant results.
    """
    if not request.user.is_staff:
        return Response({'success': False, 'error': 'Staff only'}, status=403)

    from core.tasks import (
        cleanup_boardroom_junk,
        auto_approve_boardroom_items,
        cleanup_expired_boardroom_items,
    )

    results = {}
    try:
        results['cleanup_junk'] = cleanup_boardroom_junk()
    except Exception as e:
        results['cleanup_junk'] = {'error': str(e)}

    try:
        results['auto_approve'] = auto_approve_boardroom_items()
    except Exception as e:
        results['auto_approve'] = {'error': str(e)}

    try:
        results['expired_cleanup'] = cleanup_expired_boardroom_items()
    except Exception as e:
        results['expired_cleanup'] = {'error': str(e)}

    total_processed = sum(
        sum(v for v in r.values() if isinstance(v, int))
        for r in results.values()
        if isinstance(r, dict) and 'error' not in r
    )

    return Response({
        'success': True,
        'total_processed': total_processed,
        'details': results,
    })