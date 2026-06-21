"""
ToolDispatcher ContentHandlersMixin — extracted handler methods.
"""
from core.services.pa_identity import PA_IDENTITY

"""
Tool Dispatcher - Centralized Tool Execution with No Silent Failures
=====================================================================

Session 931: Created to solve the "tool exists != tool works" problem.

Every tool call goes through this dispatcher which:
1. Wraps execution in try/catch
2. Measures latency
3. Generates trace_id for debugging
4. Returns structured result (never fails silently)

Usage:
    from core.services.tool_dispatcher import get_tool_dispatcher

    dispatcher = get_tool_dispatcher()
    result = await dispatcher.execute(
        tool_name="human_decisions_tool",
        payload={"action": "list"},
        user_id=user.id
    )

    # Result is always structured:
    # {
    #     "ok": True/False,
    #     "tool": "human_decisions_tool",
    #     "latency_ms": 234,
    #     "error_code": None,
    #     "error_message": None,
    #     "trace_id": "abc123",
    #     "result": {...}
    # }
"""

import logging
import time
import uuid
import asyncio
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from functools import wraps

logger = logging.getLogger(__name__)


# Error codes for structured failures
class ToolErrorCode:
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
    TOOL_TIMEOUT = "TOOL_TIMEOUT"
    TOOL_EXCEPTION = "TOOL_EXCEPTION"
    TOOL_INVALID_PAYLOAD = "TOOL_INVALID_PAYLOAD"
    TOOL_PERMISSION_DENIED = "TOOL_PERMISSION_DENIED"
    TOOL_DEPENDENCY_FAILED = "TOOL_DEPENDENCY_FAILED"
    AGENT_EXECUTION_FAILED = "AGENT_EXECUTION_FAILED"


@dataclass
class ToolResult:
    """Structured result from tool execution."""
    ok: bool
    tool: str
    latency_ms: int
    error_code: Optional[str]
    error_message: Optional[str]
    trace_id: str
    result: Optional[Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)




class ContentHandlersMixin:
    """Mixin providing handler methods for ToolDispatcher."""

    # ── Session 1077: Focused tool handlers (split from content_tool) ────────

    def _handle_deliverable_direct(self, tool_name, payload, user_id, trace_id):
        """Direct deliverable handler — maps deliverable_tool actions to deliverables_tool."""
        action = payload.get('action', 'list')

        # Session 1077+: Smart inference — GPT-5.2 sometimes drops action or
        # defaults to 'list' even when title+content clearly indicate create.
        if action == 'list' and payload.get('title') and payload.get('content'):
            action = 'create'
            logger.info(f"[deliverable_tool] Inferred action=create from title+content")

        # Map direct actions to the deliverables handler action names
        ACTION_MAP = {
            'list': 'list', 'detail': 'detail', 'create': 'create',
            'update': 'update', 'append': 'append', 'search': 'search',
            'save': 'save', 'unsave': 'unsave', 'stats': 'stats',
            'export_pdf': 'export_pdf', 'bulk_archive': 'bulk_archive',
        }
        mapped = ACTION_MAP.get(action, action)
        del_payload = dict(payload)
        del_payload['action'] = mapped
        # Route bulk_archive to the dedicated handler
        if action == 'bulk_archive':
            return self._handle_bulk_archive(del_payload, user_id, trace_id)
        # Session 1077: Link/unlink deliverable ↔ initiative
        if action in ('link_initiative', 'unlink_initiative'):
            return self._handle_deliverable_initiative_link(action, del_payload, user_id, trace_id)
        result = self._handle_deliverables('deliverables_tool', del_payload, user_id, trace_id)
        if isinstance(result, dict):
            result['gateway'] = 'deliverable_tool'
        return result

    def _handle_deliverable_initiative_link(self, action, payload, user_id, trace_id):
        """Link or unlink a deliverable to/from an initiative."""
        from core.models_deliverables import Deliverable
        from core.models import Initiative

        deliverable_id = payload.get('deliverable_id') or payload.get('id')
        initiative_id = payload.get('initiative_id')
        if not deliverable_id:
            return {'error': 'deliverable_id is required', 'action': action}
        try:
            deliverable = Deliverable.objects.get(id=deliverable_id)
        except Deliverable.DoesNotExist:
            return {'error': f'Deliverable {deliverable_id} not found', 'action': action}

        if action == 'link_initiative':
            if not initiative_id:
                return {'error': 'initiative_id is required for link_initiative', 'action': action}
            try:
                initiative = Initiative.objects.get(id=initiative_id)
            except Initiative.DoesNotExist:
                return {'error': f'Initiative {initiative_id} not found', 'action': action}
            deliverable.initiative = initiative
            deliverable.save(update_fields=['initiative'])
            return {
                'action': 'link_initiative',
                'deliverable_id': str(deliverable.id),
                'deliverable_title': deliverable.title,
                'initiative_id': str(initiative.id),
                'initiative_name': initiative.name,
                'gateway': 'deliverable_tool',
            }
        else:  # unlink_initiative
            old_init = deliverable.initiative
            old_name = old_init.name if old_init else None
            deliverable.initiative = None
            deliverable.save(update_fields=['initiative'])
            return {
                'action': 'unlink_initiative',
                'deliverable_id': str(deliverable.id),
                'deliverable_title': deliverable.title,
                'unlinked_from': old_name,
                'gateway': 'deliverable_tool',
            }

    def _handle_blog_direct(self, tool_name, payload, user_id, trace_id):
        """Direct blog handler — maps blog_tool actions to content_review_tool."""
        action = payload.get('action', 'stats')
        ACTION_MAP = {
            'stats': 'stats', 'list': 'list', 'detail': 'details',
            'search': 'search', 'recent': 'recent',
            'approve': 'approve', 'reject': 'reject',
        }
        if action == 'generate':
            blog_payload = dict(payload)
            result = self._handle_generate_blog('generate_blog_tool', blog_payload, user_id, trace_id)
            if isinstance(result, dict):
                result['gateway'] = 'blog_tool'
            return result
        mapped = ACTION_MAP.get(action, action)
        review_payload = dict(payload)
        review_payload['action'] = mapped
        result = self._handle_content_review('content_review_tool', review_payload, user_id, trace_id)
        if isinstance(result, dict):
            result['gateway'] = 'blog_tool'
        return result

    def _record_content_feedback(self, agent_name, action, details, user_id=None):
        """Record PA review outcome as agent feedback for the content feedback loop.

        Creates AgentMemory (type='feedback') so agents see PA decisions
        in future executions, and updates UserAgentLearning for per-user
        personalization.
        """
        try:
            from core.models_unified_system import AgentMemory, Agent, UserAgentLearning
            from django.contrib.auth import get_user_model

            agent = Agent.objects.filter(name=agent_name).first()
            if not agent:
                return

            valence_map = {'publish': 'positive', 'archive': 'negative', 'revise': 'neutral'}
            valence = valence_map.get(action, 'neutral')

            outcome_map = {'publish': 'success', 'archive': 'failure', 'revise': 'partial'}
            outcome = outcome_map.get(action, 'unknown')

            AgentMemory.objects.create(
                agent=agent,
                title=f"PA review: {action} — {details.get('title', 'content')}"[:200],
                content=details.get('feedback_summary', f"Content was {action}ed by the PA."),
                memory_type='feedback',
                valence=valence,
                memory_outcome=outcome,
                importance_score=0.7,
                source_type='task',
                tags=['pa_review', f'action_{action}'],
                safety_class='approved',
            )

            if user_id and action in ('publish', 'archive'):
                User = get_user_model()
                user = User.objects.filter(id=user_id).first()
                if user:
                    learning, _ = UserAgentLearning.objects.get_or_create(
                        user=user,
                        agent_name=agent_name,
                        learning_domain='content_creation',
                    )
                    if action == 'publish':
                        learning.record_success()
                    else:
                        learning.record_failure()

        except Exception as e:
            logger.warning(f"Failed to record content feedback for {agent_name}: {e}")

    def _handle_content_review(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 943: Content review tool for accessing Deliverables awaiting human review.

        Provides PA access to blogs, reports, and other content in 'ready' status.

        Actions:
        - list: List content ready for review
        - stats: Get content review statistics
        - details: Get details of a specific deliverable
        - publish: Mark content as published
        - archive: Archive content (reject)
        """
        from core.models_deliverables import Deliverable
        from django.db.models import Count

        action = payload.get('action', 'list')
        # Session 1075: GPT-5.2 often calls approve/reject instead of publish/archive
        # Session 1170: + mark_complete / mark_completed / done → complete
        ACTION_ALIASES = {
            'approve': 'publish',
            'reject': 'archive',
            'get': 'details',
            'mark_complete': 'complete',
            'mark_completed': 'complete',
            'done': 'complete',
        }
        action = ACTION_ALIASES.get(action, action)
        limit = payload.get('limit', 10)
        content_type = payload.get('type')  # blog, document, report, analysis, etc.
        category = payload.get('category')  # Marketing, Development, etc.

        # Session 958: If type is 'blog', query SelfBlog model instead of Deliverable
        # SelfBlog contains actual blog posts (773+ in production)
        if content_type == 'blog':
            return self._handle_blog_query(action, limit, category, payload, user_id)

        # Build base queryset - filter by user if available
        # Session 1075: Include unowned deliverables (same fix as deliverables_tool)
        from django.db.models import Q as _Qcr
        base_qs = Deliverable.objects.all()
        if user_id:
            base_qs = base_qs.filter(_Qcr(user_id=user_id) | _Qcr(user__isnull=True))

        if action == 'list':
            # Session 1101: Honor status filter from payload (default: ready)
            _STATUS_ALIASES = {'approved': 'ready', 'pending_review': 'ready', 'rejected': 'archived'}
            status_filter = payload.get('status', 'ready')
            status_filter = _STATUS_ALIASES.get(status_filter, status_filter)
            qs = base_qs.filter(status=status_filter)

            if content_type:
                qs = qs.filter(deliverable_type=content_type)
            if category:
                qs = qs.filter(category__icontains=category)

            # Session 1101: Date range filters
            created_before = payload.get('created_before')
            created_after = payload.get('created_after')
            if created_before:
                from django.utils.dateparse import parse_datetime
                dt = parse_datetime(created_before)
                if dt:
                    qs = qs.filter(created_at__lt=dt)
            if created_after:
                from django.utils.dateparse import parse_datetime
                dt = parse_datetime(created_after)
                if dt:
                    qs = qs.filter(created_at__gte=dt)

            total = qs.count()
            offset = max(payload.get('offset', 0), 0)
            items = list(
                qs.order_by('-created_at')[offset:offset + limit].values(
                    'id', 'title', 'deliverable_type', 'category',
                    'agent_name', 'quality_score', 'created_at', 'status'
                )
            )

            return {
                'action': 'list',
                'total': total,
                'count': len(items),
                'items': items,
                'filters_applied': {
                    'type': content_type,
                    'category': category,
                    'status': status_filter,
                    'created_before': created_before,
                    'created_after': created_after,
                }
            }

        elif action == 'recent':
            # Session 948: List recently created content (any status)
            # For "what content has been created?" type queries
            from django.utils import timezone
            from datetime import timedelta

            period_days = payload.get('days', 7)
            since = timezone.now() - timedelta(days=period_days)

            qs = base_qs.filter(created_at__gte=since)

            # Session 1194 — honor workspace_id filter (AC1 of
            # INITIATIVES_FIRST_BACKBONE.md). content_recent previously
            # silently ignored workspace_id, so a Donkey-Betz-scoped query
            # would return cross-workspace results and couldn't be diffed
            # against deliverable_tool.list at the row level.
            ws_id = payload.get('workspace_id') or payload.get('workspace')
            if ws_id:
                qs = qs.filter(workspace_id=ws_id)

            if content_type:
                qs = qs.filter(deliverable_type=content_type)
            if category:
                qs = qs.filter(category__icontains=category)

            # Session 1194 — add initiative_id/workspace_id projection so
            # the row shape matches deliverable_tool.list. Closes the
            # measurement gap that triggered Plan A.
            items = list(
                qs.order_by('-created_at')[:limit].values(
                    'id', 'title', 'deliverable_type', 'category',
                    'agent_name', 'quality_score', 'created_at', 'status',
                    'initiative_id', 'initiative__name',
                    'workspace_id', 'workspace__name',
                )
            )

            # Get counts by status
            status_counts = {}
            for item in items:
                s = item.get('status', 'unknown')
                status_counts[s] = status_counts.get(s, 0) + 1

            return {
                'action': 'recent',
                'count': len(items),
                'items': items,
                'period_days': period_days,
                'by_status': status_counts,
                'filters_applied': {
                    'workspace_id': ws_id,
                    'type': content_type,
                    'category': category,
                    'days': period_days,
                },
            }

        elif action == 'search':
            # Session 1042: Search deliverables + blogs by title keyword
            query = payload.get('query', '')
            if not query:
                raise ValueError("query parameter required for search action")

            # Search Deliverables
            deliverable_items = list(
                base_qs.filter(title__icontains=query)
                .order_by('-created_at')[:limit]
                .values('id', 'title', 'deliverable_type', 'category',
                        'agent_name', 'quality_score', 'created_at', 'status')
            )

            # Also search SelfBlog (where most content lives)
            from core.models_unified_system import SelfBlog
            blog_items = list(
                SelfBlog.objects.filter(title__icontains=query)
                .order_by('-created_at')[:limit]
                .values('id', 'title', 'author', 'category', 'status', 'created_at',
                        'quality_score', 'word_count', 'tone')
            )

            return {
                'action': 'search',
                'query': query,
                'deliverables': {'count': len(deliverable_items), 'items': deliverable_items},
                'blogs': {'count': len(blog_items), 'items': blog_items},
                'total_found': len(deliverable_items) + len(blog_items),
            }

        elif action == 'stats':
            # Get statistics on content requiring review
            ready_count = base_qs.filter(status='ready').count()
            draft_count = base_qs.filter(status='draft').count()
            published_count = base_qs.filter(status='published').count()

            # Session 1030: Also include SelfBlog counts for complete picture
            try:
                from core.models_unified_system import SelfBlog
                blog_qs = SelfBlog.objects.filter(category='blog')
                blog_total = blog_qs.count()
                blog_published = blog_qs.filter(status='published').count()
                blog_ready = blog_qs.filter(publish_ready=True, status__in=['approved', 'pending_review']).count()
                blog_draft = blog_qs.filter(status='draft').count()
                # Session 1102: Full status breakdown for pipeline auditability
                blog_by_status = dict(
                    blog_qs.values('status').annotate(count=Count('id'))
                    .values_list('status', 'count')
                )
            except Exception:
                blog_total = blog_published = blog_ready = blog_draft = 0
                blog_by_status = {}

            by_type = dict(
                base_qs.filter(status='ready')
                .values('deliverable_type')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
                .values_list('deliverable_type', 'count')
            )

            by_category = dict(
                base_qs.filter(status='ready')
                .values('category')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
                .values_list('category', 'count')
            )

            return {
                'action': 'stats',
                'ready_for_review': ready_count,
                'drafts': draft_count,
                'published': published_count,
                'by_type': by_type,
                'by_category': by_category,
                # Session 1030: SelfBlog counts (blogs are in SelfBlog, not Deliverable)
                'blogs': {
                    'total': blog_total,
                    'published': blog_published,
                    'publish_ready': blog_ready,
                    'drafts': blog_draft,
                    'by_status': blog_by_status,
                },
            }

        elif action == 'details':
            deliverable_id = payload.get('id')
            if not deliverable_id:
                raise ValueError("id is required for details action")

            deliverable = base_qs.filter(id=deliverable_id).first()
            if deliverable:
                return {
                    'action': 'details',
                    'content_kind': 'deliverable',
                    'id': str(deliverable.id),
                    'title': deliverable.title,
                    'type': deliverable.deliverable_type,
                    'category': deliverable.category,
                    'status': deliverable.status,
                    'agent_name': deliverable.agent_name,
                    'quality_score': deliverable.quality_score,
                    'confidence_score': deliverable.confidence_score,
                    'content_preview': (deliverable.content or '')[:1000],
                    'tags': deliverable.tags or [],
                    'created_at': deliverable.created_at.isoformat() if deliverable.created_at else None,
                }

            # Session 1101: Fallback to SelfBlog if not found in Deliverables
            # SelfBlog uses UUID PK — direct lookup
            try:
                from core.models_unified_system import SelfBlog
                blog = SelfBlog.objects.filter(id=deliverable_id).first()
                if blog:
                    return {
                        'action': 'details',
                        'content_kind': 'blog',
                        'id': str(blog.id),
                        'title': blog.title,
                        'author': blog.author,
                        'category': blog.category,
                        'status': blog.status,
                        'tone': getattr(blog, 'tone', None),
                        'word_count': getattr(blog, 'word_count', None),
                        'quality_score': getattr(blog, 'quality_score', None),
                        'publish_ready': getattr(blog, 'publish_ready', False),
                        'content': (blog.full_text or '')[:3000],
                        'created_at': blog.created_at.isoformat() if blog.created_at else None,
                    }
            except Exception as e:
                logger.warning(f"[CONTENT_DETAIL] SelfBlog fallback failed for {deliverable_id}: {e}")

            return {
                'action': 'details',
                'error': f'Content {deliverable_id} not found in deliverables or blogs — it may have been deleted',
                'status': 'gone',
            }

        elif action == 'publish':
            deliverable_id = payload.get('id')
            if not deliverable_id:
                raise ValueError("id is required for publish action")

            deliverable = base_qs.filter(id=deliverable_id, status='ready').first()
            if not deliverable:
                raise ValueError(f"Deliverable {deliverable_id} not found or not in ready status")

            deliverable.status = 'published'
            deliverable.save(update_fields=['status', 'updated_at'])

            self._record_content_feedback(
                agent_name=deliverable.agent_name,
                action='publish',
                details={
                    'title': deliverable.title,
                    'feedback_summary': 'Content published — quality met standards.',
                },
                user_id=user_id,
            )

            return {
                'action': 'publish',
                'id': str(deliverable_id),
                'title': deliverable.title,
                'new_status': 'published',
                'success': True,
            }

        elif action == 'archive':
            deliverable_id = payload.get('id')
            feedback = payload.get('feedback', 'Archived via PA')

            if not deliverable_id:
                raise ValueError("id is required for archive action")

            deliverable = base_qs.filter(id=deliverable_id).first()
            if not deliverable:
                raise ValueError(f"Deliverable {deliverable_id} not found")

            deliverable.status = 'archived'
            if deliverable.metadata is None:
                deliverable.metadata = {}
            deliverable.metadata['archive_reason'] = feedback
            deliverable.save(update_fields=['status', 'metadata', 'updated_at'])

            self._record_content_feedback(
                agent_name=deliverable.agent_name,
                action='archive',
                details={
                    'title': deliverable.title,
                    'feedback_summary': f'Content archived — reason: {feedback}',
                },
                user_id=user_id,
            )

            return {
                'action': 'archive',
                'id': str(deliverable_id),
                'title': deliverable.title,
                'new_status': 'archived',
                'success': True,
            }

        elif action == 'complete':
            # Session 1170: closes the tool gap discovered during the
            # publish-ready backlog triage — Deliverable.status='completed'
            # was a valid terminal state per the schema but no PA action
            # could flip to it. Rigby's stop-gap (title prefix + tag
            # convention) worked but lost the queryability of a real
            # status. This action mirrors `archive`'s shape (no precondition
            # on current status, feedback persisted to metadata) but flips
            # to `completed` instead. Use for one-shot analyses + ops
            # snapshots whose terminal state is "done, keep for reference"
            # rather than "rejected, hide".
            deliverable_id = payload.get('id')
            feedback = payload.get('feedback', 'Marked completed via PA')

            if not deliverable_id:
                raise ValueError("id is required for complete action")

            deliverable = base_qs.filter(id=deliverable_id).first()
            if not deliverable:
                raise ValueError(f"Deliverable {deliverable_id} not found")

            deliverable.status = 'completed'
            if deliverable.metadata is None:
                deliverable.metadata = {}
            deliverable.metadata['complete_reason'] = feedback
            deliverable.save(update_fields=['status', 'metadata', 'updated_at'])

            self._record_content_feedback(
                agent_name=deliverable.agent_name,
                action='complete',
                details={
                    'title': deliverable.title,
                    'feedback_summary': f'Content marked completed — reason: {feedback}',
                },
                user_id=user_id,
            )

            return {
                'action': 'complete',
                'id': str(deliverable_id),
                'title': deliverable.title,
                'new_status': 'completed',
                'success': True,
            }

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: list, stats, details, publish, archive, complete (aliases: approve=publish, reject=archive, mark_complete/done=complete)"
            )

    def _handle_blog_query(
        self,
        action: str,
        limit: int,
        category: Optional[str],
        payload: Dict[str, Any],
        user_id: Optional[int]
    ) -> Dict[str, Any]:
        """
        Session 958: Query SelfBlog model for actual blog content.

        SelfBlog contains:
        - 773+ blog posts in production
        - Categories: blog, audit, technical_document, research_brief, etc.
        - Status: draft, pending_review, approved, published

        This allows the PA to answer "What blogs have been written?" accurately.
        """
        from core.models_unified_system import SelfBlog
        from django.db.models import Count

        # Build base queryset for blogs
        base_qs = SelfBlog.objects.filter(category='blog')

        if action == 'list':
            # Session 1102: Honor caller's status filter (was hardcoded to pending_review/approved)
            _BLOG_STATUS_ALIASES = {
                'ready': 'approved', 'pending_review': 'approved', 'rejected': 'needs_enhancement',
            }
            status_filter = payload.get('status', '')
            if status_filter:
                status_filter = _BLOG_STATUS_ALIASES.get(status_filter, status_filter)
                qs = base_qs.filter(status=status_filter)
            else:
                # Default: show review-worthy blogs
                qs = base_qs.filter(status__in=['pending_review', 'approved'])
            items = list(
                qs.order_by('-created_at')[:limit].values(
                    'id', 'title', 'author', 'category', 'status', 'created_at',
                    'quality_score', 'novelty_score', 'structure_score',
                    'content_type', 'publish_ready', 'word_count', 'tone'
                )
            )

            return {
                'action': 'list',
                'source': 'SelfBlog',
                'count': len(items),
                'items': items,
                'filters_applied': {
                    'type': 'blog',
                    'status': status_filter or 'pending_review or approved',
                }
            }

        elif action == 'recent':
            # Session 958: List recently created blogs (any status)
            from django.utils import timezone
            from datetime import timedelta

            period_days = payload.get('days', 30)
            since = timezone.now() - timedelta(days=period_days)

            qs = base_qs.filter(created_at__gte=since)
            # Session 1102: Honor status filter for content_recent
            status_filter = payload.get('status', '')
            if status_filter:
                _BLOG_STATUS_ALIASES = {
                    'ready': 'approved', 'pending': 'pending_review',
                    'rejected': 'needs_enhancement',
                }
                status_filter = _BLOG_STATUS_ALIASES.get(status_filter, status_filter)
                qs = qs.filter(status=status_filter)
            items = list(
                qs.order_by('-created_at')[:limit].values(
                    'id', 'title', 'author', 'category', 'status', 'created_at',
                    'quality_score', 'novelty_score', 'structure_score',
                    'content_type', 'publish_ready', 'word_count', 'tone'
                )
            )

            # Get counts by status
            status_counts = {}
            for item in items:
                s = item.get('status', 'unknown')
                status_counts[s] = status_counts.get(s, 0) + 1

            # Session 959: Aggregate quality analytics
            from django.db.models import Avg
            aggregates = base_qs.filter(
                created_at__gte=since, quality_score__isnull=False
            ).aggregate(
                avg_quality=Avg('quality_score'),
                avg_novelty=Avg('novelty_score'),
                avg_structure=Avg('structure_score'),
            )
            publish_ready_count = base_qs.filter(
                created_at__gte=since, publish_ready=True
            ).count()

            return {
                'action': 'recent',
                'source': 'SelfBlog',
                'count': len(items),
                'items': items,
                'period_days': period_days,
                'by_status': status_counts,
                'avg_quality': aggregates.get('avg_quality'),
                'avg_novelty': aggregates.get('avg_novelty'),
                'avg_structure': aggregates.get('avg_structure'),
                'publish_ready_count': publish_ready_count,
            }

        elif action == 'search':
            # Session 1042: Search blogs by title keyword (any status)
            query = payload.get('query', '')
            if not query:
                raise ValueError("query parameter required for search action")

            from django.db.models import Q
            status_filter = payload.get('status')
            qs = base_qs.filter(title__icontains=query)
            if status_filter:
                qs = qs.filter(status=status_filter)

            items = list(
                qs.order_by('-created_at')[:limit].values(
                    'id', 'title', 'author', 'category', 'status', 'created_at',
                    'quality_score', 'novelty_score', 'structure_score',
                    'content_type', 'publish_ready', 'word_count', 'tone'
                )
            )

            return {
                'action': 'search',
                'source': 'SelfBlog',
                'query': query,
                'count': len(items),
                'items': items,
            }

        elif action == 'stats':
            # Get blog statistics
            from django.db.models import Avg
            total = base_qs.count()
            draft_count = base_qs.filter(status='draft').count()
            pending_count = base_qs.filter(status='pending_review').count()
            approved_count = base_qs.filter(status='approved').count()
            published_count = base_qs.filter(status='published').count()
            publish_ready_count = base_qs.filter(publish_ready=True).count()

            # Session 959: Aggregate quality averages
            quality_aggs = base_qs.filter(quality_score__isnull=False).aggregate(
                avg_quality=Avg('quality_score'),
                avg_novelty=Avg('novelty_score'),
                avg_structure=Avg('structure_score'),
            )

            return {
                'action': 'stats',
                'source': 'SelfBlog',
                'total_blogs': total,
                'by_status': {
                    'draft': draft_count,
                    'pending_review': pending_count,
                    'approved': approved_count,
                    'published': published_count,
                },
                'ready_for_review': pending_count + approved_count,
                'publish_ready_count': publish_ready_count,
                'avg_quality': quality_aggs.get('avg_quality'),
                'avg_novelty': quality_aggs.get('avg_novelty'),
                'avg_structure': quality_aggs.get('avg_structure'),
            }

        elif action == 'details':
            # Get specific blog details
            blog_id = payload.get('id')
            if not blog_id:
                raise ValueError("Blog ID required for details action")

            blog = base_qs.filter(id=blog_id).first()
            if not blog:
                raise ValueError(f"Blog {blog_id} not found")

            # Get content preview (first 500 chars) - SelfBlog uses 'full_text' field
            content_preview = (blog.full_text or '')[:500]
            if len(blog.full_text or '') > 500:
                content_preview += '...'

            blog_detail = {
                'id': str(blog.id),
                'title': blog.title,
                'author': blog.author,
                'status': blog.status,
                'category': blog.category,
                'content_type': blog.content_type,
                'quality_score': blog.quality_score,
                'novelty_score': blog.novelty_score,
                'structure_score': blog.structure_score,
                'publish_ready': blog.publish_ready,
                'gate_notes': blog.gate_notes or '',
                'tone': blog.tone or '',
                'created_at': blog.created_at.isoformat() if blog.created_at else None,
                'content_preview': content_preview,
                'word_count': blog.word_count or 0,
            }

            # Session 1080: Deliberation traceability — surface provenance
            # for blogs created by the ContentDeliberation pipeline
            delib = (blog.stats_snapshot or {}).get('deliberation')
            if delib:
                blog_detail['deliberation'] = {
                    'session_id': delib.get('session_id'),
                    'decision': delib.get('decision'),
                    'claims_count': delib.get('claims_count', 0),
                    'sources_count': delib.get('sources_count', 0),
                    'reviewers': delib.get('reviewers', []),
                    'review_verdicts': delib.get('review_verdicts', []),
                }
                # Gate result is stored on blog fields, not in stats_snapshot
                if blog.quality_score is not None:
                    blog_detail['deliberation']['gate'] = {
                        'quality': blog.quality_score,
                        'novelty': blog.novelty_score,
                        'structure': blog.structure_score,
                        'decision': 'publish' if blog.publish_ready else (
                            'enhance' if blog.status == 'needs_enhancement' else 'internal_only'
                        ),
                        'notes': blog.gate_notes or '',
                    }

            return {
                'action': 'details',
                'source': 'SelfBlog',
                'blog': blog_detail,
            }

        elif action == 'related':
            # Session 971: Find related blogs by initiative, tags, or title keywords
            blog_id = payload.get('id')
            if not blog_id:
                raise ValueError("Blog ID required for related action")

            source = base_qs.filter(id=blog_id).first()
            if not source:
                # Try all categories, not just blog
                source = SelfBlog.objects.filter(id=blog_id).first()
            if not source:
                raise ValueError(f"Blog {blog_id} not found")

            import re as _re

            STOP_WORDS = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'from', 'is', 'it', 'its', 'are', 'was', 'were',
                'be', 'been', 'has', 'had', 'have', 'how', 'what', 'when', 'where',
                'who', 'why', 'this', 'that', 'these', 'those', 'not', 'can', 'will',
                'just', 'more', 'also', 'than', 'into', 'over', 'such', 'our', 'your',
            }

            def _title_keywords(title):
                words = _re.findall(r'[a-z]+', (title or '').lower())
                return {w for w in words if len(w) >= 4 and w not in STOP_WORDS}

            from django.db.models import Q
            scored = {}

            # Signal 1: Same initiative
            if source.initiative_id:  # type: ignore[attr-defined]
                siblings = SelfBlog.objects.filter(
                    initiative_id=source.initiative_id  # type: ignore[attr-defined]
                ).exclude(id=blog_id)[:20]
                for b in siblings:
                    scored[b.id] = (1.0, 'same_initiative', b)

            # Signal 2: Tag overlap (Jaccard > 0.3)
            source_tags = set(source.tags or [])
            if source_tags:
                tag_q = Q()
                for tag in source_tags:
                    tag_q |= Q(tags__contains=[tag])
                for b in SelfBlog.objects.filter(tag_q).exclude(id=blog_id).exclude(id__in=scored.keys())[:50]:
                    b_tags = set(b.tags or [])
                    if b_tags:
                        jaccard = len(source_tags & b_tags) / len(source_tags | b_tags)
                        if jaccard > 0.3:
                            scored[b.id] = (jaccard * 0.8, 'tag_overlap', b)

            # Signal 3: Title keyword overlap
            src_kw = _title_keywords(source.title)
            if src_kw:
                kw_q = Q()
                for kw in list(src_kw)[:5]:
                    kw_q |= Q(title__icontains=kw)
                for b in SelfBlog.objects.filter(kw_q).exclude(id=blog_id).exclude(id__in=scored.keys())[:50]:
                    b_kw = _title_keywords(b.title)
                    if b_kw:
                        ratio = len(src_kw & b_kw) / len(src_kw | b_kw)
                        if ratio > 0.15:
                            scored[b.id] = (ratio * 0.5, 'title_keywords', b)

            top = sorted(scored.values(), key=lambda x: x[0], reverse=True)[:limit]

            related = []
            for score, reason, b in top:
                related.append({
                    'id': str(b.id),
                    'title': b.title,
                    'category': getattr(b, 'category', 'blog'),
                    'status': getattr(b, 'status', 'draft'),
                    'word_count': b.word_count or 0,
                    'created_at': b.created_at.isoformat() if b.created_at else None,
                    'quality_score': b.quality_score,
                    'relatedness_score': round(score, 3),
                    'relatedness_reason': reason,
                })

            return {
                'action': 'related',
                'source': 'SelfBlog',
                'blog_id': str(source.id),
                'blog_title': source.title,
                'count': len(related),
                'related': related,
            }

        elif action == 'read':
            # Session 986: Read full blog content by title for analysis
            title = payload.get('title', '')
            section_filter = payload.get('section', '')

            if not title:
                return {
                    'action': 'read',
                    'error': 'No blog title provided. Try: "read the blog titled \'Your Title Here\'"',
                }

            # Search by title (case-insensitive contains)
            blog = base_qs.filter(title__icontains=title).first()
            if not blog:
                # Fall back to all SelfBlog categories, not just 'blog'
                blog = SelfBlog.objects.filter(title__icontains=title).first()
            if not blog:
                return {
                    'action': 'read',
                    'error': f'No blog found matching "{title}".',
                }

            # Build content from structured fields
            sections_data = blog.sections or []  # list of {header, content}
            intro = blog.intro or ''
            conclusion = blog.conclusion or ''

            if section_filter:
                # Extract a specific section
                matched_section = None
                for sec in sections_data:
                    header = sec.get('header', '') or sec.get('title', '')
                    if section_filter.lower() in header.lower():
                        matched_section = sec
                        break

                if matched_section:
                    header = matched_section.get('header', '') or matched_section.get('title', '')
                    content = matched_section.get('content', '')
                    return {
                        'action': 'read',
                        'source': 'SelfBlog',
                        'blog': {
                            'id': str(blog.id),
                            'title': blog.title,
                            'status': blog.status,
                            'quality_score': blog.quality_score,
                            'word_count': blog.word_count or 0,
                            'created_at': blog.created_at.isoformat() if blog.created_at else None,
                        },
                        'section': {
                            'header': header,
                            'content': content,
                        },
                        'total_sections': len(sections_data),
                    }
                else:
                    # Section not found — return available headers
                    headers = [
                        s.get('header', '') or s.get('title', '')
                        for s in sections_data if s.get('header') or s.get('title')
                    ]
                    return {
                        'action': 'read',
                        'source': 'SelfBlog',
                        'blog': {
                            'id': str(blog.id),
                            'title': blog.title,
                        },
                        'error': f'Section "{section_filter}" not found.',
                        'available_sections': headers,
                    }
            else:
                # Return full blog content (all sections)
                full_sections = []
                if intro:
                    full_sections.append({'header': 'Introduction', 'content': intro})
                for sec in sections_data:
                    header = sec.get('header', '') or sec.get('title', '')
                    content = sec.get('content', '')
                    full_sections.append({'header': header, 'content': content})
                if conclusion:
                    full_sections.append({'header': 'Conclusion', 'content': conclusion})

                # Cap total content at ~4000 chars
                total_chars = sum(len(s['content']) for s in full_sections)
                if total_chars > 4000:
                    # Truncate last sections to fit
                    budget = 4000
                    for sec in full_sections:
                        if budget <= 0:
                            sec['content'] = '[truncated]'
                        elif len(sec['content']) > budget:
                            sec['content'] = sec['content'][:budget] + '...'
                            budget = 0
                        else:
                            budget -= len(sec['content'])

                return {
                    'action': 'read',
                    'source': 'SelfBlog',
                    'blog': {
                        'id': str(blog.id),
                        'title': blog.title,
                        'status': blog.status,
                        'quality_score': blog.quality_score,
                        'novelty_score': blog.novelty_score,
                        'structure_score': blog.structure_score,
                        'word_count': blog.word_count or 0,
                        'created_at': blog.created_at.isoformat() if blog.created_at else None,
                    },
                    'sections': full_sections,
                    'total_sections': len(full_sections),
                }

        elif action == 'revise':
            # Session 987: Revise blog using EditorAgent + re-score with PublishGate
            blog_id = payload.get('id')
            if not blog_id:
                raise ValueError("Blog ID required for revise action")

            blog = base_qs.filter(id=blog_id).first()
            if not blog:
                blog = SelfBlog.objects.filter(id=blog_id).first()
            if not blog:
                raise ValueError(f"Blog {blog_id} not found")

            # Capture before scores
            before = {
                'quality': blog.quality_score,
                'novelty': blog.novelty_score,
                'structure': blog.structure_score,
                'publish_ready': blog.publish_ready,
            }

            # If no gate_notes yet, run PublishGate first to generate editorial guidance
            from core.services.publish_gate import PublishGate
            gate = PublishGate()
            if not blog.gate_notes:
                gate.apply_to_blog(blog, save=True)
                blog.refresh_from_db()
                # Update before scores with freshly computed values
                before = {
                    'quality': blog.quality_score,
                    'novelty': blog.novelty_score,
                    'structure': blog.structure_score,
                    'publish_ready': blog.publish_ready,
                }

            # Map gate_notes into EditorAgent focus_areas
            notes_lower = (blog.gate_notes or '').lower()
            focus_areas = []
            if any(kw in notes_lower for kw in ['hook', 'opening', 'intro', 'engagement']):
                focus_areas.append('hooks')
            if any(kw in notes_lower for kw in ['header', 'heading', 'structure', 'section']):
                focus_areas.append('headers')
            if any(kw in notes_lower for kw in ['conclusion', 'cta', 'call to action', 'ending']):
                focus_areas.append('conclusion')
            if any(kw in notes_lower for kw in ['engagement', 'readability', 'audience']):
                focus_areas.append('engagement')
            if not focus_areas:
                focus_areas = ['hooks', 'headers', 'engagement', 'structure', 'conclusion']

            # Run EditorAgent
            from core.agents.editor_agent import EditorAgent
            editor = EditorAgent()
            result = editor.execute(
                task=f"Revise blog based on editorial feedback: {blog.gate_notes}",
                context={
                    'blog_id': str(blog.id),
                    'focus_areas': focus_areas,
                    'save': True,
                },
                scifi_context={},
                spider_context={},
            )

            if not result.success:
                return {
                    'action': 'revise',
                    'error': f"EditorAgent failed: {result.error}",
                    'blog_id': str(blog.id),
                    'title': blog.title,
                }

            # Re-score with PublishGate
            blog.refresh_from_db()
            gate.apply_to_blog(blog, save=True)
            blog.refresh_from_db()

            after = {
                'quality': blog.quality_score,
                'novelty': blog.novelty_score,
                'structure': blog.structure_score,
                'publish_ready': blog.publish_ready,
            }

            self._record_content_feedback(
                agent_name='ContentWriterAgent',
                action='revise',
                details={
                    'title': blog.title,
                    'feedback_summary': (
                        f"Blog revised — before: quality={before.get('quality')}, "
                        f"structure={before.get('structure')}; "
                        f"after: quality={after.get('quality')}, "
                        f"structure={after.get('structure')}. "
                        f"Focus areas: {', '.join(focus_areas)}."
                    ),
                },
                user_id=user_id,
            )

            return {
                'action': 'revise',
                'blog_id': str(blog.id),
                'title': blog.title,
                'before': before,
                'after': after,
                'changes_made': result.data.get('changes_made', []),
                'focus_areas': focus_areas,
                'gate_notes': blog.gate_notes,
                'status': blog.status,
            }

        elif action == 'needs_work':
            # Session 987: List blogs flagged as needing enhancement
            qs = SelfBlog.objects.filter(status='needs_enhancement')
            items = list(
                qs.order_by('-created_at')[:limit].values(
                    'id', 'title', 'status', 'created_at',
                    'quality_score', 'novelty_score', 'structure_score',
                    'gate_notes', 'word_count',
                )
            )
            return {
                'action': 'needs_work',
                'source': 'SelfBlog',
                'count': len(items),
                'total': qs.count(),
                'items': items,
            }

        elif action == 'batch_enhance':
            # Session 987: Trigger batch enhancement on all needs_enhancement blogs
            from core.agents.editor_agent import enhance_all_needing_enhancement
            results = enhance_all_needing_enhancement(save=True)
            succeeded = [r for r in results if r.get('success')]
            failed = [r for r in results if not r.get('success')]
            return {
                'action': 'batch_enhance',
                'total_processed': len(results),
                'succeeded': len(succeeded),
                'failed': len(failed),
                'details': [
                    {
                        'title': r.get('title', 'Untitled'),
                        'success': r.get('success', False),
                        'changes': r.get('changes', []),
                        'error': r.get('error'),
                    }
                    for r in results[:10]
                ],
            }

        # Session 993: Bulk blog triage — summarize ALL blogs grouped by quality tier
        elif action == 'triage':
            from django.utils import timezone
            from datetime import timedelta

            thirty_days_ago = timezone.now() - timedelta(days=30)

            # Tier 1: Publish-ready — passed gate AND in reviewable status
            tier1_qs = base_qs.filter(
                publish_ready=True,
                status__in=['approved', 'pending_review'],
            ).order_by('-quality_score')
            tier1 = list(tier1_qs.values(
                'id', 'title', 'status', 'quality_score', 'publish_ready',
                'created_at', 'tone', 'word_count',
            ))

            # Tier 2: Needs revision — draft/needs_enhancement, not publish-ready
            tier2_qs = base_qs.filter(
                status__in=['needs_enhancement', 'draft'],
                publish_ready=False,
            ).order_by('-quality_score')
            tier2 = list(tier2_qs.values(
                'id', 'title', 'status', 'quality_score', 'publish_ready',
                'created_at', 'tone', 'word_count',
            ))

            # Tier 3: Archive candidates — old drafts with low quality
            from django.db.models import Q as _Q
            tier3_qs = base_qs.filter(
                status='draft',
                created_at__lt=thirty_days_ago,
            ).filter(
                _Q(quality_score__lt=0.4) | _Q(quality_score__isnull=True)
            ).order_by('quality_score')
            tier3 = list(tier3_qs.values(
                'id', 'title', 'status', 'quality_score', 'publish_ready',
                'created_at', 'tone', 'word_count',
            ))

            # Serialize UUIDs / datetimes
            for tier_list in (tier1, tier2, tier3):
                for item in tier_list:
                    item['id'] = str(item['id'])
                    if item.get('created_at'):
                        item['created_at'] = item['created_at'].isoformat()

            from django.db.models import Avg
            avg_q = base_qs.filter(quality_score__isnull=False).aggregate(avg=Avg('quality_score'))

            return {
                'action': 'triage',
                'source': 'SelfBlog',
                'publish_ready': {'count': len(tier1), 'items': tier1},
                'needs_revision': {'count': len(tier2), 'items': tier2},
                'archive_candidates': {'count': len(tier3), 'items': tier3},
                'avg_quality': round(avg_q['avg'] or 0, 3),
            }

        # Session 993: Publish a single SelfBlog
        elif action == 'publish':
            blog_id = payload.get('id') or payload.get('blog_id')
            if not blog_id:
                raise ValueError("id is required for publish action")

            # Session 998: Enforce PublishGate — only publish_ready blogs
            blog = base_qs.filter(id=blog_id, status__in=['approved', 'pending_review'], publish_ready=True).first()
            if not blog:
                # Check if blog exists but isn't publish-ready
                unpublishable = base_qs.filter(id=blog_id).first()
                if unpublishable and not unpublishable.publish_ready:
                    return {
                        'action': 'publish',
                        'success': False,
                        'error': 'Blog has not passed PublishGate quality checks.',
                        'gate_notes': unpublishable.gate_notes or 'Not yet evaluated',
                        'id': str(unpublishable.id),
                        'title': unpublishable.title,
                        'status': unpublishable.status,
                    }
                raise ValueError(f"Blog {blog_id} not found or not in approved/pending_review status")

            blog.status = 'published'
            blog.save(update_fields=['status'])

            self._record_content_feedback(
                agent_name='BlogWriter',
                action='publish',
                details={
                    'title': blog.title,
                    'feedback_summary': 'Blog published via PA — quality met standards.',
                },
                user_id=user_id,
            )

            return {
                'action': 'publish',
                'id': str(blog.id),
                'title': blog.title,
                'new_status': 'published',
                'success': True,
            }

        # Session 993: Archive a single SelfBlog (sets to draft — safe, reversible)
        elif action == 'archive':
            blog_id = payload.get('id') or payload.get('blog_id')
            feedback = payload.get('feedback', 'Archived via PA')
            if not blog_id:
                raise ValueError("id is required for archive action")

            blog = base_qs.filter(id=blog_id).first()
            if not blog:
                raise ValueError(f"Blog {blog_id} not found")

            blog.status = 'draft'
            blog.publish_ready = False
            blog.save(update_fields=['status', 'publish_ready'])

            self._record_content_feedback(
                agent_name='BlogWriter',
                action='archive',
                details={
                    'title': blog.title,
                    'feedback_summary': f'Blog archived (→draft) via PA — reason: {feedback}',
                },
                user_id=user_id,
            )

            return {
                'action': 'archive',
                'id': str(blog.id),
                'title': blog.title,
                'new_status': 'draft',
                'success': True,
            }

        # Session 993: Batch publish all publish-ready blogs
        elif action == 'batch_publish':
            publish_qs = base_qs.filter(
                publish_ready=True,
                status__in=['approved', 'pending_review'],
            )[:50]

            published = []
            for blog in publish_qs:
                blog.status = 'published'
                blog.save(update_fields=['status'])
                self._record_content_feedback(
                    agent_name='BlogWriter',
                    action='publish',
                    details={
                        'title': blog.title,
                        'feedback_summary': 'Batch-published via PA.',
                    },
                    user_id=user_id,
                )
                published.append({'id': str(blog.id), 'title': blog.title})

            return {
                'action': 'batch_publish',
                'published_count': len(published),
                'items': published,
                'success': True,
            }

        # Session 993: Batch archive old low-quality drafts
        elif action == 'batch_archive':
            from django.utils import timezone
            from datetime import timedelta

            days_old = payload.get('days_old', 30)
            max_quality = payload.get('max_quality', 0.4)
            cutoff = timezone.now() - timedelta(days=days_old)

            from django.db.models import Q as _Q2
            archive_qs = base_qs.filter(
                status='draft',
                created_at__lt=cutoff,
            ).filter(
                _Q2(quality_score__lt=max_quality) | _Q2(quality_score__isnull=True)
            )[:50]

            archived = []
            for blog in archive_qs:
                blog.publish_ready = False
                blog.save(update_fields=['publish_ready'])
                self._record_content_feedback(
                    agent_name='BlogWriter',
                    action='archive',
                    details={
                        'title': blog.title,
                        'feedback_summary': f'Batch-archived via PA (age>{days_old}d, quality<{max_quality}).',
                    },
                    user_id=user_id,
                )
                archived.append({'id': str(blog.id), 'title': blog.title})

            return {
                'action': 'batch_archive',
                'archived_count': len(archived),
                'criteria': {'days_old': days_old, 'max_quality': max_quality},
                'items': archived,
                'success': True,
            }

        else:
            raise ValueError(
                f"Unknown action for blog query: {action}. "
                f"Valid actions: list, recent, stats, details, related, read, revise, "
                f"needs_work, batch_enhance, triage, publish, archive, batch_publish, batch_archive"
            )

    def _handle_generate_blog(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 993: Generate a blog through the V2 deliberation pipeline.
        Session 1057: Always async — blog generation takes 60-300s which exceeds
        the PA tool timeout. Dispatch to Celery and return immediately.
        """
        topic = payload.get('topic')
        tone = payload.get('tone', 'enthusiastic')

        if topic:
            # Session 1057: Dispatch topic-specific blog to Celery
            from core.tasks import generate_blog_with_topic_task
            task = generate_blog_with_topic_task.delay(topic=topic, tone=tone)  # type: ignore[union-attr]

            return {
                'action': 'generate_blog',
                'mode': 'async',
                'topic': topic,
                'tone': tone,
                'task_id': str(task.id),
                'message': f'Blog generation for "{topic}" queued via deliberation pipeline. '
                           f'This typically takes 2-5 minutes. Use task_breakdown_tool to check progress.',
            }
        else:
            # Async — dispatch to Celery for background generation
            from core.tasks import generate_self_blog_deliberation_task
            task = generate_self_blog_deliberation_task.delay(tone=tone)  # type: ignore[union-attr]

            return {
                'action': 'generate_blog',
                'mode': 'async',
                'tone': tone,
                'task_id': str(task.id),
                'message': 'Blog generation queued via deliberation pipeline. '
                           'This typically takes 2-5 minutes. Use task_breakdown_tool to check progress.',
            }

    def _handle_initiative(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 943: Initiative tool for PA access to project pipeline.

        Provides visibility into the 5-stage initiative pipeline.

        Actions:
        - list: List initiatives (with filters for status, stage, purpose, program)
        - stats: Get pipeline overview statistics
        - details: Get full details of a specific initiative
        - action_items: List pending action items across initiatives
        """
        from core.models_document_registry import Initiative, InitiativeActionItem
        from django.db.models import Count, Q

        action = payload.get('action', 'list')
        limit = payload.get('limit', 50)
        offset = payload.get('offset', 0)  # Session 1076: pagination support

        if action == 'list':
            # Build queryset with filters
            qs = Initiative.objects.all()

            # Filter by status (default to ACTIVE)
            status_filter = payload.get('status', 'ACTIVE')
            if status_filter and status_filter != 'all':
                qs = qs.filter(status=status_filter.upper())

            # Filter by stage
            stage_filter = payload.get('stage')
            if stage_filter:
                qs = qs.filter(current_stage=int(stage_filter))

            # Filter by purpose/program — enums removed from schema to stop GPT
            # auto-filling defaults. Apply only when value looks intentional.
            _IGNORED_PURPOSE = ('all', '', 'maintenance')
            _IGNORED_PROGRAM = ('all', '', 'uncategorized')
            purpose_filter = payload.get('purpose', '').strip().lower()
            purpose_applied = purpose_filter not in _IGNORED_PURPOSE
            if purpose_applied:
                qs = qs.filter(purpose=purpose_filter)

            program_filter = payload.get('program', '').strip().lower()
            program_applied = program_filter not in _IGNORED_PROGRAM
            if program_applied:
                qs = qs.filter(program=program_filter)

            # Session 996: Filter by owner
            # Session 1077: 'all' means no owner filter (was searching for literal 'all' in owner_agent)
            owner_filter = str(payload.get('owner', '')).strip()
            if owner_filter and owner_filter.lower() != 'all':
                if owner_filter == 'me' and user_id:
                    # Session 1077: Use User object lookup to avoid integer=UUID SQL error
                    # Session 1103c: was 'except Exception: pass' which
                    # silently dropped the owner filter on any failure,
                    # returning results for all owners when the user
                    # asked for 'me'. Privacy-adjacent; log loudly now.
                    try:
                        from django.contrib.auth import get_user_model
                        _User = get_user_model()
                        user_obj = _User.objects.filter(id=user_id).first()
                        if user_obj:
                            qs = qs.filter(owner=user_obj)
                    except Exception as e:
                        logger.warning(
                            "td_handlers_content: owner='me' filter lookup "
                            "failed for user_id=%s (%s: %s) — returning "
                            "unfiltered results which may include other "
                            "users' items",
                            user_id, type(e).__name__, e,
                        )
                elif owner_filter == 'unowned':
                    qs = qs.filter(owner__isnull=True, owner_agent='')
                else:
                    qs = qs.filter(owner_agent__icontains=owner_filter)

            # Session 1077: Filter by workspace
            ws_filter = payload.get('workspace') or payload.get('workspace_id')
            if ws_filter:
                qs = qs.filter(workspace_id=ws_filter)

            # Session 1077: Annotate action item counts to avoid N+1 queries
            # (was 2 COUNT queries per initiative in the loop)
            from django.db.models import Count, Q as _Q
            qs = qs.annotate(
                pending_actions=Count(
                    'action_items', filter=_Q(action_items__status='pending'), distinct=True
                ),
                critical_actions=Count(
                    'action_items',
                    filter=_Q(action_items__status='pending', action_items__priority='critical'),
                    distinct=True,
                ),
            )

            # Order + paginate (offset was missing before Session 1077)
            total_count = qs.count()
            start = int(offset)
            end = start + int(limit)
            items = list(
                qs.order_by('-impact_score', '-urgency', '-created_at')[start:end].values(
                    'id', 'name', 'description', 'status', 'current_stage',
                    'purpose', 'program', 'impact_score', 'urgency',
                    'confidence', 'revenue_potential', 'created_at',
                    'updated_at', 'last_activity_at',
                    'owner_id', 'owner_agent',
                    'human_id', 'seq_id',
                    'pending_actions', 'critical_actions',
                )
            )

            # Session 996: Resolve owner_ids to usernames in bulk
            owner_ids = [i['owner_id'] for i in items if i.get('owner_id')]
            owner_map = {}
            if owner_ids:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                owner_map = dict(
                    User.objects.filter(id__in=owner_ids).values_list('id', 'username')
                )

            # Serialize
            for item in items:
                desc = item.get('description') or ''
                if len(desc) > 200:
                    item['description'] = desc[:200] + '...'
                item['owner'] = (
                    owner_map.get(item.pop('owner_id'))
                    or item.pop('owner_agent', '')
                    or None
                )
                item['id'] = str(item['id'])
                for dt_field in ('created_at', 'updated_at', 'last_activity_at'):
                    if item.get(dt_field):
                        item[dt_field] = item[dt_field].isoformat()

            return {
                'action': 'list',
                'count': len(items),
                'total_count': total_count,
                'offset': start,
                'limit': int(limit),
                'items': items,
                'filters_applied': {
                    'status': status_filter,
                    'stage': stage_filter or '',
                    'purpose': purpose_filter if purpose_applied else '',
                    'program': program_filter if program_applied else '',
                    'owner': owner_filter or '',
                }
            }

        elif action == 'audit':
            from datetime import timedelta
            from django.utils import timezone
            from core.management.commands.consolidate_duplicate_initiatives import (
                find_duplicate_clusters,
            )

            audit_qs = Initiative.objects.all()
            status_filter = payload.get('status', 'all')
            if status_filter and status_filter != 'all':
                audit_qs = audit_qs.filter(status=status_filter.upper())

            total = audit_qs.count()
            cutoff = timezone.now() - timedelta(days=14)

            init_list = list(audit_qs.only(
                'id', 'name', 'status', 'current_stage',
                'last_activity_at', 'created_at', 'purpose', 'program'
            ))

            # Duplicate clustering via Jaccard similarity + BFS (Session 906)
            clusters = find_duplicate_clusters(init_list, threshold=0.6)
            duplicate_ids = set()
            for cluster in clusters:
                for init in cluster[1:]:
                    duplicate_ids.add(init.id)

            # Classify
            real, stalled, noise = [], [], []
            for init in init_list:
                if init.current_stage > 1 or init.last_activity_at:
                    real.append(init)
                elif init.created_at < cutoff:
                    stalled.append(init)
                else:
                    noise.append(init)

            return {
                'action': 'audit',
                'total': total,
                'classification': {
                    'real': {
                        'count': len(real),
                        'items': [{'human_id': i.human_id, 'name': i.name, 'stage': i.current_stage,
                                   'purpose': i.purpose} for i in real[:10]]
                    },
                    'stalled': {
                        'count': len(stalled),
                        'items': [{'human_id': i.human_id, 'name': i.name, 'created_at': str(i.created_at)[:10],
                                   'purpose': i.purpose} for i in stalled[:5]]
                    },
                    'noise': {
                        'count': len(noise),
                        'items': [{'human_id': i.human_id, 'name': i.name} for i in noise[:5]]
                    },
                    'duplicates': {
                        'count': len(duplicate_ids),
                        'cluster_count': len(clusters),
                        'clusters': [
                            {
                                'primary': cluster[0].name,
                                'count': len(cluster),
                                'examples': [c.name[:80] for c in cluster[1:3]]
                            }
                            for cluster in clusters[:10]
                        ]
                    }
                }
            }

        elif action == 'stats':
            # Get pipeline overview
            total = Initiative.objects.count()
            active = Initiative.objects.filter(status='ACTIVE').count()
            triage = Initiative.objects.filter(status='TRIAGE').count()
            completed = Initiative.objects.filter(status='COMPLETED').count()
            on_hold = Initiative.objects.filter(status='ON_HOLD').count()

            # By stage
            by_stage = {}
            for stage in range(1, 6):
                by_stage[f'stage_{stage}'] = Initiative.objects.filter(
                    status='ACTIVE',
                    current_stage=stage
                ).count()

            # By purpose
            by_purpose = dict(
                Initiative.objects.filter(status='ACTIVE')
                .values('purpose')
                .annotate(count=Count('id'))
                .values_list('purpose', 'count')
            )

            # By program
            by_program = dict(
                Initiative.objects.filter(status='ACTIVE')
                .values('program')
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
                .values_list('program', 'count')
            )

            # Action items
            pending_actions = InitiativeActionItem.objects.filter(status='pending').count()
            critical_actions = InitiativeActionItem.objects.filter(
                status='pending',
                priority='critical'
            ).count()

            return {
                'action': 'stats',
                'total': total,
                'active': active,
                'triage': triage,
                'completed': completed,
                'on_hold': on_hold,
                'by_stage': by_stage,
                'by_purpose': by_purpose,
                'by_program': by_program,
                'pending_action_items': pending_actions,
                'critical_action_items': critical_actions,
            }

        elif action == 'details':
            initiative_id = payload.get('id')
            name_query = payload.get('name')

            if not initiative_id and not name_query:
                raise ValueError("id or name is required for details action")

            # Session 1043: Support lookup by human_id (INIT-000001) or seq_id number
            if initiative_id:
                id_str = str(initiative_id).strip()
                # Session 1075: Catch non-UUID strings like "pipeline_health"
                if id_str.lower() in ('pipeline_health', 'pipeline-health', 'health'):
                    return {
                        'action': 'details',
                        'error': 'Use pipeline_orchestrator_tool(action="status") for pipeline health',
                        'hint': 'initiative_tool is for individual initiatives, not pipeline overview',
                    }
                if id_str.upper().startswith('INIT-'):
                    initiative = Initiative.objects.filter(human_id__iexact=id_str).first()
                elif id_str.isdigit():
                    initiative = Initiative.objects.filter(seq_id=int(id_str)).first()
                else:
                    try:
                        initiative = Initiative.objects.filter(id=initiative_id).first()
                    except (ValueError, Exception):
                        # Invalid UUID — try name search fallback
                        initiative = Initiative.objects.filter(name__icontains=id_str).first()
            else:
                initiative = Initiative.objects.filter(name__icontains=name_query).first()

            if not initiative:
                raise ValueError(f"Initiative not found")

            # Get action items (Session 1058: include source_stage)
            action_items = list(
                InitiativeActionItem.objects.filter(initiative=initiative)
                .order_by('-priority', 'status', '-created_at')[:10]
                .values('id', 'title', 'status', 'priority', 'due_date', 'assigned_agent', 'source_stage__stage')
            )

            # Session 987: Serialize UUIDs and datetimes
            for ai in action_items:
                ai['id'] = str(ai['id'])
                if ai.get('due_date'):
                    ai['due_date'] = ai['due_date'].isoformat()

            # Get stage info — Session 1021: fixed field names (stage, not stage_number)
            stages = list(
                initiative.stages.all()  # type: ignore[attr-defined]
                .order_by('stage')
                .values('stage', 'status', 'approved_at', 'document_id')
            )

            stage_labels = {1: 'Research Brief', 2: 'Prototype Plan', 3: 'Evaluation Protocol', 4: 'Technical Design', 5: 'Pilot Execution'}
            for s in stages:
                s['stage_name'] = stage_labels.get(s['stage'], f"Stage {s['stage']}")
                if s.get('approved_at'):
                    s['approved_at'] = s['approved_at'].isoformat()
                # Session 1021: Include stage document preview.
                # Session 1103c: loud on failure so missing stage
                # documents are visible in the initiative detail response.
                if s.get('document_id'):
                    try:
                        from core.models_unified_system import SelfBlog
                        doc = SelfBlog.objects.filter(id=s['document_id']).first()
                        if doc:
                            s['document_title'] = doc.title
                            s['document_preview'] = (doc.full_text or '')[:300]
                            s['document_length'] = len(doc.full_text or '')
                    except Exception as e:
                        logger.warning(
                            "td_handlers_content: stage document preview "
                            "lookup failed for document_id=%s (%s: %s)",
                            s.get('document_id'), type(e).__name__, e,
                        )
                s['document_id'] = str(s['document_id']) if s.get('document_id') else None

            # Session 996: Resolve owner
            owner_display = initiative.owner_agent or None
            if initiative.owner_id:  # type: ignore[attr-defined]
                owner_display = initiative.owner.username if initiative.owner else None

            return {
                'action': 'details',
                'id': str(initiative.id),
                'human_id': initiative.human_id or None,
                'name': initiative.name,
                'description': initiative.description,
                'status': initiative.status,
                'current_stage': initiative.current_stage,
                'purpose': initiative.purpose,
                'program': initiative.program,
                'impact_score': initiative.impact_score,
                'urgency': initiative.urgency,
                'confidence': initiative.confidence,
                'revenue_potential': initiative.revenue_potential,
                'created_at': initiative.created_at.isoformat() if initiative.created_at else None,
                'owner': owner_display,
                'owner_agent': initiative.owner_agent,
                'stages': stages,
                'action_items': action_items,
                'action_item_count': len(action_items),
            }

        elif action == 'action_items':
            # List pending action items across all initiatives
            # Session 1076: Added priority filter to schema, fixed ordering
            status_filter = payload.get('item_status', 'pending')
            priority_filter = payload.get('priority')

            qs = InitiativeActionItem.objects.select_related('initiative', 'source_stage')

            if status_filter and status_filter != 'all':
                qs = qs.filter(status=status_filter)

            if priority_filter:
                qs = qs.filter(priority=priority_filter)

            # Order by priority (critical > high > medium > low), then newest
            from django.db.models import Case, When, Value, IntegerField
            priority_order = Case(
                When(priority='critical', then=Value(0)),
                When(priority='high', then=Value(1)),
                When(priority='medium', then=Value(2)),
                When(priority='low', then=Value(3)),
                default=Value(4),
                output_field=IntegerField(),
            )

            # Session 1076: Total count for pagination
            total_count = qs.count()

            items = []
            for item in qs.annotate(priority_rank=priority_order).order_by('priority_rank', '-created_at')[offset:offset + limit]:
                items.append({
                    'id': str(item.id),
                    'title': item.title,
                    'status': item.status,
                    'priority': item.priority,
                    'due_date': item.due_date.isoformat() if item.due_date else None,
                    'assigned_agent': item.assigned_agent,
                    'initiative_id': str(item.initiative_id),  # type: ignore[attr-defined]
                    'initiative_name': item.initiative.name if item.initiative else 'Unknown',
                    'source_stage': item.source_stage.stage if item.source_stage else None,
                })

            return {
                'action': 'action_items',
                'count': len(items),
                'total': total_count,
                'offset': offset,
                'limit': limit,
                'items': items,
                'filters_applied': {
                    'status': status_filter,
                    'priority': priority_filter,
                }
            }

        # Session 1076: Cleanup junk action items (section headings, labels)
        elif action == 'cleanup_action_items':
            dry_run = payload.get('dry_run', True)
            from core.services.action_item_parser import ActionItemParser

            junk_qs = InitiativeActionItem.objects.filter(status='pending')
            junk_ids = []
            junk_titles = []
            for item in junk_qs.only('id', 'title'):
                if ActionItemParser._is_junk_title(item.title):
                    junk_ids.append(item.id)
                    junk_titles.append(item.title)

            cancelled = 0
            if not dry_run and junk_ids:
                cancelled = InitiativeActionItem.objects.filter(
                    id__in=junk_ids
                ).update(status='cancelled')

            return {
                'action': 'cleanup_action_items',
                'dry_run': dry_run,
                'junk_found': len(junk_ids),
                'cancelled': cancelled,
                'sample_titles': junk_titles[:20],
            }

        # Session 1040: Fetch full stage document content
        elif action == 'stage_document':
            initiative_id = payload.get('id') or payload.get('initiative_id')
            document_id = payload.get('document_id')
            stage_num = payload.get('stage')

            if not initiative_id and not document_id:
                raise ValueError("id (initiative UUID) or document_id is required")

            from core.models_unified_system import SelfBlog

            if document_id:
                doc = SelfBlog.objects.filter(id=document_id).first()
                if not doc:
                    raise ValueError(f"Document {document_id} not found")
            elif initiative_id and stage_num:
                from core.models_document_registry import InitiativeStage as IS
                stage = IS.objects.filter(
                    initiative_id=initiative_id, stage=int(stage_num)
                ).select_related('document').first()
                if not stage:
                    raise ValueError(f"Stage {stage_num} not found for initiative {initiative_id}")
                if not stage.document:
                    raise ValueError(f"Stage {stage_num} has no document attached")
                doc = stage.document
            else:
                raise ValueError("Provide document_id, or both id + stage")

            return {
                'action': 'stage_document',
                'document_id': str(doc.id),
                'title': doc.title,
                'word_count': doc.word_count,
                'status': doc.status,
                'created_at': doc.created_at.isoformat() if doc.created_at else None,
                'intro': doc.intro or '',
                'full_text': doc.full_text or '',
                'sections': doc.sections or [],
                'tags': doc.tags or [],
                'quality_score': doc.quality_score,
                'tone': doc.tone,
            }

        # Session 993: Write actions for initiatives
        elif action == 'update_status':
            initiative_id = payload.get('id') or payload.get('initiative_id')
            new_status = payload.get('status', '').upper()
            valid_statuses = ['ACTIVE', 'TRIAGE', 'ON_HOLD', 'COMPLETED', 'ARCHIVED']

            if not initiative_id:
                raise ValueError("id is required for update_status action")
            if new_status not in valid_statuses:
                raise ValueError(f"Invalid status '{new_status}'. Valid: {', '.join(valid_statuses)}")

            initiative = Initiative.objects.filter(id=initiative_id).first()
            if not initiative:
                raise ValueError(f"Initiative {initiative_id} not found")

            old_status = initiative.status
            initiative.status = new_status
            initiative.save(update_fields=['status'])

            # Session 1076: Auto-cancel orphaned action items when initiative is completed
            cancelled_items = 0
            if new_status in ('COMPLETED', 'ARCHIVED') and old_status not in ('COMPLETED', 'ARCHIVED'):
                cancelled_items = InitiativeActionItem.objects.filter(
                    initiative=initiative,
                    status='pending',
                ).update(status='cancelled')
                if cancelled_items:
                    logger.info(f"Auto-cancelled {cancelled_items} pending action items for {new_status} initiative {initiative.name}")

            return {
                'action': 'update_status',
                'id': str(initiative.id),
                'name': initiative.name,
                'old_status': old_status,
                'new_status': new_status,
                'success': True,
                'auto_cancelled_action_items': cancelled_items,
            }

        elif action == 'advance':
            initiative_id = payload.get('id') or payload.get('initiative_id')
            if not initiative_id:
                raise ValueError("id is required for advance action")

            initiative = Initiative.objects.filter(id=initiative_id).first()
            if not initiative:
                raise ValueError(f"Initiative {initiative_id} not found")

            old_stage = initiative.current_stage
            initiative.advance_stage()
            initiative.refresh_from_db()

            return {
                'action': 'advance',
                'id': str(initiative.id),
                'name': initiative.name,
                'old_stage': old_stage,
                'new_stage': initiative.current_stage,
                'success': initiative.current_stage != old_stage,
                'message': (
                    f"Advanced from stage {old_stage} to {initiative.current_stage}"
                    if initiative.current_stage != old_stage
                    else f"Cannot advance — stage {old_stage} is not approved or already at stage 5"
                ),
            }

        elif action == 'start_action_item':
            item_id = payload.get('item_id') or payload.get('id')
            if not item_id:
                raise ValueError("item_id is required for start_action_item action")
            item = InitiativeActionItem.objects.filter(id=item_id).first()
            if not item:
                raise ValueError(f"Action item {item_id} not found")
            item.start(by='human_pa')
            return {
                'action': 'start_action_item',
                'id': str(item.id),
                'title': item.title,
                'status': item.status,
            }

        elif action == 'complete_action_item':
            item_id = payload.get('item_id') or payload.get('id')
            notes = payload.get('notes', '')
            if not item_id:
                raise ValueError("item_id is required for complete_action_item action")

            item = InitiativeActionItem.objects.filter(id=item_id).first()
            if not item:
                raise ValueError(f"Action item {item_id} not found")

            item.complete(by='PA', notes=notes)

            return {
                'action': 'complete_action_item',
                'id': str(item.id),
                'title': item.title,
                'new_status': 'completed',
                'initiative_name': item.initiative.name if item.initiative else 'Unknown',
                'success': True,
            }

        elif action == 'assign_owner':
            # Session 996: Assign ownership of an initiative
            initiative_id = payload.get('id') or payload.get('initiative_id')
            agent_name = payload.get('agent_name', '')
            user_name = payload.get('user_name', '')

            if not initiative_id:
                raise ValueError("id is required for assign_owner action")

            initiative = Initiative.objects.filter(id=initiative_id).first()
            if not initiative:
                raise ValueError(f"Initiative {initiative_id} not found")

            old_owner = initiative.owner_agent or (initiative.owner.username if initiative.owner else None) or 'unowned'

            if agent_name:
                initiative.owner_agent = agent_name
                initiative.owner = None
                initiative.save(update_fields=['owner_agent', 'owner'])
                new_owner = agent_name
            elif user_name:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                if user_name == 'me':
                    user = User.objects.filter(id=user_id).first() if user_id else None
                else:
                    user = User.objects.filter(username__iexact=user_name).first()
                if not user:
                    raise ValueError(f"User '{user_name}' not found")
                initiative.owner = user
                initiative.owner_agent = ''
                initiative.save(update_fields=['owner', 'owner_agent'])
                new_owner = user.username  # type: ignore[attr-defined]
            else:
                raise ValueError("agent_name or user_name is required for assign_owner")

            return {
                'action': 'assign_owner',
                'id': str(initiative.id),
                'name': initiative.name,
                'old_owner': old_owner,
                'new_owner': new_owner,
                'success': True,
            }

        elif action == 'promote':
            # Session 1058: Human-in-the-loop promotion from TRIAGE/ON_HOLD → ACTIVE
            initiative_id = payload.get('id') or payload.get('initiative_id')
            if not initiative_id:
                raise ValueError("id is required for promote action")

            # Reuse human_id / seq_id lookup from details action
            id_str = str(initiative_id).strip()
            if id_str.upper().startswith('INIT-'):
                initiative = Initiative.objects.filter(human_id__iexact=id_str).first()
            elif id_str.isdigit():
                initiative = Initiative.objects.filter(seq_id=int(id_str)).first()
            else:
                initiative = Initiative.objects.filter(id=initiative_id).first()

            if not initiative:
                raise ValueError(f"Initiative {initiative_id} not found")

            promotable = {'TRIAGE', 'ON_HOLD'}
            if initiative.status not in promotable:
                raise ValueError(
                    f"Cannot promote: status is {initiative.status}. "
                    f"Only {', '.join(sorted(promotable))} initiatives can be promoted to ACTIVE."
                )

            old_status = initiative.status
            initiative.status = 'ACTIVE'
            initiative.save(update_fields=['status'])

            return {
                'action': 'promote',
                'id': str(initiative.id),
                'human_id': initiative.human_id or None,
                'name': initiative.name,
                'old_status': old_status,
                'new_status': 'ACTIVE',
                'success': True,
                'message': f"Promoted '{initiative.name}' from {old_status} to ACTIVE",
            }

        elif action == 'flow_metrics':
            # Session 994: Initiative pipeline health metrics
            from django.utils import timezone
            from datetime import timedelta
            now = timezone.now()
            last_24h = now - timedelta(hours=24)
            last_7d = now - timedelta(days=7)

            # Creation rate
            created_24h = Initiative.objects.filter(created_at__gte=last_24h).count()
            created_7d = Initiative.objects.filter(created_at__gte=last_7d).count()

            # Triage backlog
            triage_count = Initiative.objects.filter(status='TRIAGE').count()
            active_count = Initiative.objects.filter(status='ACTIVE').count()

            # No-activity count (created but never worked on)
            no_activity = Initiative.objects.filter(
                status__in=['ACTIVE', 'TRIAGE'],
                last_activity_at__isnull=True,
            ).count()

            # Stage progression (active initiatives by stage)
            stage_dist = {}
            for stage in range(1, 6):
                stage_dist[f'stage_{stage}'] = Initiative.objects.filter(
                    status='ACTIVE', current_stage=stage
                ).count()

            # Circuit breaker status
            from core.services.initiative_circuit_breaker import get_backlog_status
            breaker = get_backlog_status()

            # Completion rate
            completed_7d = Initiative.objects.filter(
                status='COMPLETED',
                updated_at__gte=last_7d,
            ).count()

            return {
                'action': 'flow_metrics',
                'creation_rate': {
                    'last_24h': created_24h,
                    'last_7d': created_7d,
                },
                'backlog': {
                    'triage': triage_count,
                    'active': active_count,
                    'no_activity': no_activity,
                },
                'stage_distribution': stage_dist,
                'circuit_breaker': {
                    'can_create': breaker['can_create'],
                    'pending': breaker['pending_count'],
                    'threshold': breaker['threshold'],
                    'utilization_pct': breaker['utilization_pct'],
                    'paused': breaker['paused_by_env'] or breaker['paused_by_db'] or breaker['paused_by_backlog'],
                },
                'completed_last_7d': completed_7d,
            }

        elif action == 'bulk_auto_assign':
            # Session 1000C: Auto-assign agents to unowned initiatives by keyword
            from core.agent_router import AgentRouter

            # Keyword → agent mapping for initiative content routing
            KEYWORD_AGENT_MAP = {
                'research': 'ResearchAgent',
                'competitor': 'CompetitorAnalysisAgent',
                'customer': 'CustomerResearchAgent',
                'content': 'ContentStrategyAgent',
                'blog': 'ContentStrategyAgent',
                'seo': 'SEOOptimizerAgent',
                'brand': 'BrandIdentityAgent',
                'social media': 'SocialMediaAgent',
                'image': 'ImageAgent',
                'video': 'VideoAgent',
                'audio': 'AudioAgent',
                'trend': 'TrendAnalysisAgent',
                'opportunit': 'OpportunityScoringAgent',
                'financial': 'ResearchAgent',
                'market': 'TrendAnalysisAgent',
                'stock': 'ResearchAgent',
                'prediction': 'PredictionMarketAnalyst',
                'sport': 'SportsOddsAnalyst',
                'betting': 'SportsOddsAnalyst',
                'security': 'MemoryIsolationAgent',
                'cyber': 'MemoryIsolationAgent',
                'pipeline': 'CTOAgent',
                'infrastructure': 'CTOAgent',
                'operation': 'COOAgent',
                'risk': 'COOAgent',
                'creative': 'CreativeDirectorAgent',
                'signal': 'TrendAnalysisAgent',
                'enhancement': 'ResearchAgent',
            }

            dry_run = payload.get('dry_run', False)
            limit_count = payload.get('limit', 50)

            qs = Initiative.objects.filter(status='ACTIVE').order_by('-impact_score', '-created_at')[:limit_count]
            assignments = []
            skipped = 0

            for init in qs:
                name_lower = init.name.lower()
                matched_agent = None
                for keyword, agent in KEYWORD_AGENT_MAP.items():
                    if keyword in name_lower:
                        matched_agent = agent
                        break

                if not matched_agent:
                    matched_agent = 'ResearchAgent'  # default fallback

                # Skip if already assigned to a real agent (not just creator)
                if init.owner_agent and init.owner_agent not in ('DecisionExtractor', 'ThinkingAgent', 'auto_populate', ''):
                    skipped += 1
                    continue

                if not dry_run:
                    init.owner_agent = matched_agent
                    init.save(update_fields=['owner_agent'])

                assignments.append({
                    'id': str(init.id),
                    'name': init.name[:80],
                    'agent': matched_agent,
                })

            result = {
                'action': 'bulk_auto_assign',
                'assigned': len(assignments),
                'skipped': skipped,
                'dry_run': dry_run,
                'assignments': assignments[:25],  # show first 25
            }

            # Session 1000C: Combined auto-assign + cleanup
            if payload.get('also_cleanup'):
                cleanup_result = self._handle_initiative(
                    tool_name, {**payload, 'action': 'bulk_cleanup'}, user_id, trace_id
                )
                result['cleanup'] = cleanup_result

            return result

        elif action == 'bulk_cleanup':
            # Session 1000C: Archive stalled, noise, and duplicate initiatives
            from datetime import timedelta
            from django.utils import timezone
            from core.management.commands.consolidate_duplicate_initiatives import (
                find_duplicate_clusters,
            )

            dry_run = payload.get('dry_run', False)
            cutoff = timezone.now() - timedelta(days=14)

            init_list = list(Initiative.objects.filter(
                status__in=['ACTIVE', 'TRIAGE']
            ).only('id', 'name', 'status', 'current_stage', 'last_activity_at', 'created_at'))

            # Classify
            stalled = [i for i in init_list if i.current_stage <= 1 and not i.last_activity_at and i.created_at < cutoff]
            noise = [i for i in init_list if i.current_stage <= 1 and not i.last_activity_at and i.created_at >= cutoff and (timezone.now() - i.created_at).days >= 7]

            # Duplicates
            clusters = find_duplicate_clusters(init_list, threshold=0.6)
            duplicate_ids = set()
            for cluster in clusters:
                for init in cluster[1:]:
                    duplicate_ids.add(init.id)

            archived_stalled = []
            archived_noise = []
            archived_dupes = []

            if not dry_run:
                for init in stalled:
                    init.status = 'ARCHIVED'
                    init.save(update_fields=['status'])
                    archived_stalled.append(init.name[:60])

                for init in noise:
                    init.status = 'ARCHIVED'
                    init.save(update_fields=['status'])
                    archived_noise.append(init.name[:60])

                for init in init_list:
                    if init.id in duplicate_ids:
                        init.status = 'ARCHIVED'
                        init.save(update_fields=['status'])
                        archived_dupes.append(init.name[:60])
            else:
                archived_stalled = [i.name[:60] for i in stalled]
                archived_noise = [i.name[:60] for i in noise]
                archived_dupes = [i.name[:60] for i in init_list if i.id in duplicate_ids]

            return {
                'action': 'bulk_cleanup',
                'dry_run': dry_run,
                'stalled': {'count': len(archived_stalled), 'items': archived_stalled[:10]},
                'noise': {'count': len(archived_noise), 'items': archived_noise[:10]},
                'duplicates': {'count': len(archived_dupes), 'items': archived_dupes[:10], 'cluster_count': len(clusters)},
                'total_cleaned': len(archived_stalled) + len(archived_noise) + len(archived_dupes),
            }

        elif action == 'create':
            from core.services.initiative_integration_service import (
                InitiativeIntegrationService,
                InitiativeCreationBlocked,
            )

            name = payload.get('name', '').strip()
            if not name:
                raise ValueError("'name' is required for create action")

            description = payload.get('description', '')
            purpose = payload.get('purpose', 'learning')
            program = payload.get('program', 'uncategorized')

            try:
                svc = InitiativeIntegrationService()
                # Bypass circuit breaker for explicit human-initiated creation via PA.
                # The breaker exists to prevent autonomous/auto-spawned initiatives from
                # piling up, but when a human explicitly asks the PA to create one, honour it.
                initiative, created = svc.get_or_create_initiative(
                    topic=name,
                    description=description,
                    created_by=PA_IDENTITY,
                    bypass_circuit_breaker=True,
                )
            except InitiativeCreationBlocked as e:
                return {'action': 'create', 'error': str(e), 'blocked': True}

            # Apply extra fields from payload
            update_fields = []
            for field, default in [
                ('purpose', 'learning'), ('program', 'uncategorized'),
                ('impact_score', 0.5), ('urgency', 0.5),
                ('revenue_potential', 0.0), ('execution_speed', 'balanced'),
            ]:
                val = payload.get(field)
                if val is not None:
                    if field in ('impact_score', 'urgency', 'revenue_potential'):
                        val = max(0.0, min(1.0, float(val)))
                    setattr(initiative, field, val)
                    update_fields.append(field)
            if update_fields:
                initiative.save(update_fields=update_fields)

            return {
                'action': 'create',
                'created': created,
                'id': str(initiative.id),
                'human_id': initiative.human_id,
                'name': initiative.name,
                'status': initiative.status,
                'purpose': initiative.purpose,
                'program': initiative.program,
                'current_stage': initiative.current_stage,
                'message': (
                    f"Created initiative '{initiative.name}' ({initiative.human_id})"
                    if created else
                    f"Found existing initiative '{initiative.name}' ({initiative.human_id}) — no duplicate created"
                ),
            }

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: list, stats, details, "
                f"action_items, flow_metrics, update_status, advance, start_action_item, "
                f"complete_action_item, assign_owner, bulk_auto_assign, bulk_cleanup, create"
            )

    # =========================================================================
    # Session 948: New PA Enhancement Tools
    # =========================================================================

    def _handle_spider_data(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 948: Spider data tool for querying collected intelligence.

        Provides PA access to data collected by the 77 spiders.

        Actions:
        - recent: Get recent spider data (default)
        - by_spider: Get data from a specific spider
        - by_category: Get data by spider category
        - search: Search spider data by keyword
        - stats: Get spider collection statistics
        """
        from core.models_unified_system import SpiderData
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta

        action = payload.get('action', 'recent')
        limit = payload.get('limit', 20)
        spider_name = payload.get('spider_name')
        category = payload.get('category')
        keyword = payload.get('keyword', payload.get('query', ''))
        days = payload.get('days', 7)

        cutoff = timezone.now() - timedelta(days=days)

        if action == 'recent':
            # Get recent spider data across all spiders
            # Session 989: Use actual SpiderData fields (no title/url/category/content)
            qs = SpiderData.objects.filter(created_at__gte=cutoff)

            if spider_name:
                qs = qs.filter(spider_name__icontains=spider_name)
            if category:
                qs = qs.filter(data_type__icontains=category)

            items = list(
                qs.order_by('-created_at')[:limit].values(
                    'id', 'spider_name', 'data_type', 'source_url',
                    'relevance_score', 'created_at'
                )
            )

            return {
                'action': 'recent',
                'count': len(items),
                'items': items,
                'days_back': days,
            }

        elif action == 'by_spider':
            if not spider_name:
                # List available spiders with counts
                spider_counts = dict(
                    SpiderData.objects.filter(created_at__gte=cutoff)
                    .values('spider_name')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:30]
                    .values_list('spider_name', 'count')
                )
                return {
                    'action': 'by_spider',
                    'available_spiders': spider_counts,
                    'message': 'Specify spider_name to get data from a specific spider'
                }

            # Session 989: Use actual SpiderData fields
            # Session 1030: Include processed_data for first 3 items (crypto prices live there)
            qs = SpiderData.objects.filter(
                spider_name__icontains=spider_name,
                created_at__gte=cutoff
            ).order_by('-created_at')[:limit]

            items = list(qs.values(
                'id', 'spider_name', 'data_type', 'source_url',
                'embedding_text', 'relevance_score', 'created_at'
            ))

            # Include processed_data for first 3 items only (keeps payload manageable)
            detailed_items = list(qs[:3].values(
                'id', 'processed_data'
            ))
            detail_map = {str(d['id']): d.get('processed_data') for d in detailed_items}
            for item in items[:3]:
                item['processed_data'] = detail_map.get(str(item['id']))

            return {
                'action': 'by_spider',
                'spider_name': spider_name,
                'count': len(items),
                'items': items,
            }

        elif action == 'by_category':
            if not category:
                # Session 989: Use data_type (not category) — actual SpiderData field
                category_counts = dict(
                    SpiderData.objects.filter(created_at__gte=cutoff)
                    .values('data_type')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:20]
                    .values_list('data_type', 'count')
                )
                return {
                    'action': 'by_category',
                    'available_categories': category_counts,
                    'message': 'Specify category to get data from that category'
                }

            # Session 989: Use data_type (not category)
            items = list(
                SpiderData.objects.filter(
                    data_type__icontains=category,
                    created_at__gte=cutoff
                ).order_by('-created_at')[:limit].values(
                    'id', 'spider_name', 'data_type', 'source_url',
                    'relevance_score', 'created_at'
                )
            )

            return {
                'action': 'by_category',
                'category': category,
                'count': len(items),
                'items': items,
            }

        elif action == 'search':
            if not keyword:
                return {
                    'action': 'search',
                    'error': 'keyword is required for search',
                }

            # Session 1089: Search embedding_text, source_url, AND raw_data.
            # ~72% of recent SpiderData has empty embedding_text, so searching
            # only that field returned 0 results for most queries. raw_data
            # contains the actual content (titles, descriptions, articles).
            from django.db.models import Q, TextField
            from django.db.models.functions import Cast
            qs = SpiderData.objects.filter(
                created_at__gte=cutoff
            ).annotate(
                raw_text=Cast('raw_data', TextField())
            ).filter(
                Q(embedding_text__icontains=keyword) |
                Q(source_url__icontains=keyword) |
                Q(raw_text__icontains=keyword)
            )

            if spider_name:
                qs = qs.filter(spider_name__icontains=spider_name)

            results = list(qs.order_by('-created_at')[:limit])

            # Build items with a content preview extracted from raw_data
            items = []
            for s in results:
                preview = (s.embedding_text or '')[:200]
                if not preview:
                    # Extract preview from raw_data items
                    rd = s.raw_data or {}
                    if isinstance(rd, dict):
                        rd_items = rd.get('items', [])
                        if isinstance(rd_items, list):
                            for item in rd_items[:3]:
                                if isinstance(item, dict):
                                    title = item.get('title', '')
                                    desc = item.get('description', item.get('summary', ''))
                                    if title:
                                        preview += f"{title}. "
                                    if desc:
                                        preview += f"{str(desc)[:100]} "
                            preview = preview.strip()[:300]
                        if not preview:
                            # Fallback: stringify first 300 chars
                            preview = str(rd)[:300]

                items.append({
                    'id': str(s.id),
                    'spider_name': s.spider_name,
                    'data_type': s.data_type,
                    'source_url': s.source_url,
                    'preview': preview,
                    'relevance_score': s.relevance_score,
                    'created_at': s.created_at.isoformat() if s.created_at else None,
                })

            return {
                'action': 'search',
                'keyword': keyword,
                'count': len(items),
                'items': items,
            }

        elif action == 'stats':
            total = SpiderData.objects.filter(created_at__gte=cutoff).count()
            by_spider = dict(
                SpiderData.objects.filter(created_at__gte=cutoff)
                .values('spider_name')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
                .values_list('spider_name', 'count')
            )
            # Session 989: Use data_type (not category)
            by_data_type = dict(
                SpiderData.objects.filter(created_at__gte=cutoff)
                .values('data_type')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
                .values_list('data_type', 'count')
            )

            return {
                'action': 'stats',
                'total_items': total,
                'days_back': days,
                'by_spider': by_spider,
                'by_data_type': by_data_type,
            }

        # Session 993: Trigger spider run by category or name
        elif action == 'trigger':
            category = payload.get('category')
            spider_name = payload.get('spider_name')

            if not category and not spider_name:
                raise ValueError("category or spider_name is required for trigger action")

            from core.tasks import run_spider_by_category
            target = category or spider_name
            task = run_spider_by_category.delay(category=target)  # type: ignore[union-attr]

            return {
                'action': 'trigger',
                'target': target,
                'task_id': str(task.id),
                'message': f'Spider run queued for "{target}". Check execution history for results.',
                'success': True,
            }

        else:
            logger.warning(f"Unknown spider_data action '{action}', defaulting to 'recent'")
            payload['action'] = 'recent'
            return self._handle_spider_data(tool_name, payload, user_id, trace_id)

    def _handle_execution_history(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 948: Execution history tool for viewing agent activity.

        Provides PA access to recent agent executions.

        Actions:
        - recent: Get recent executions (default)
        - by_agent: Get executions for a specific agent
        - stats: Get execution statistics
        - failures: Get recent failures for debugging
        """
        from core.models import AgentExecution
        from core.models_deliberation import DeliberationSession
        from django.db.models import Count, Avg
        from django.utils import timezone
        from datetime import timedelta

        action = payload.get('action', 'recent')
        limit = payload.get('limit', 20)
        agent_name = payload.get('agent_name')
        hours = payload.get('hours', 24)
        status_filter = payload.get('status')  # Session 1097: honour status filter

        cutoff = timezone.now() - timedelta(hours=hours)

        # Session 989: AgentExecution.agent is FK to Agent — use agent__name
        # AgentExecution has no 'success' field — use status='completed'/'failed'

        if action == 'recent':
            qs = AgentExecution.objects.filter(created_at__gte=cutoff)

            if agent_name:
                qs = qs.filter(agent__name__icontains=agent_name)
            if status_filter:
                qs = qs.filter(status=status_filter)

            items = list(
                qs.order_by('-created_at')[:limit].values(
                    'id', 'agent__name', 'task', 'status',
                    'execution_time_ms', 'created_at'
                )
            )

            # Session 988: Also include agent conversations (DeliberationSessions)
            conversations = list(
                DeliberationSession.objects.filter(
                    created_at__gte=cutoff
                ).order_by('-created_at')[:limit].values(
                    'id', 'objective', 'participants', 'status', 'created_at'
                )
            )

            return {
                'action': 'recent',
                'count': len(items),
                'items': items,
                'conversation_count': len(conversations),
                'conversations': conversations,
                'hours_back': hours,
            }

        elif action == 'by_agent':
            if not agent_name:
                # List active agents with execution counts
                agent_counts = dict(
                    AgentExecution.objects.filter(created_at__gte=cutoff)
                    .values('agent__name')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:30]
                    .values_list('agent__name', 'count')
                )
                return {
                    'action': 'by_agent',
                    'active_agents': agent_counts,
                    'message': 'Specify agent_name to see executions for a specific agent'
                }

            qs = AgentExecution.objects.filter(
                agent__name__icontains=agent_name,
                created_at__gte=cutoff
            )
            if status_filter:
                qs = qs.filter(status=status_filter)

            items = list(
                qs.order_by('-created_at')[:limit].values(
                    'id', 'agent__name', 'task', 'status',
                    'execution_time_ms', 'error_message', 'created_at'
                )
            )

            # Calculate success rate for this agent
            total = AgentExecution.objects.filter(
                agent__name__icontains=agent_name,
                created_at__gte=cutoff
            ).count()
            successes = AgentExecution.objects.filter(
                agent__name__icontains=agent_name,
                created_at__gte=cutoff,
                status='completed'
            ).count()

            return {
                'action': 'by_agent',
                'agent_name': agent_name,
                'count': len(items),
                'items': items,
                'success_rate': successes / total if total > 0 else 0,
            }

        elif action == 'stats':
            total = AgentExecution.objects.filter(created_at__gte=cutoff).count()
            successes = AgentExecution.objects.filter(
                created_at__gte=cutoff, status='completed'
            ).count()
            failures = AgentExecution.objects.filter(
                created_at__gte=cutoff, status='failed'
            ).count()

            by_agent = list(
                AgentExecution.objects.filter(created_at__gte=cutoff)
                .values('agent__name')
                .annotate(
                    count=Count('id'),
                    avg_time=Avg('execution_time_ms')
                )
                .order_by('-count')[:15]
            )

            # Session 988: Include deliberation session stats
            conv_total = DeliberationSession.objects.filter(
                created_at__gte=cutoff
            ).count()
            conv_completed = DeliberationSession.objects.filter(
                created_at__gte=cutoff, status='completed'
            ).count()

            return {
                'action': 'stats',
                'total_executions': total,
                'successes': successes,
                'failures': failures,
                'success_rate': successes / total if total > 0 else 0,
                'total_conversations': conv_total,
                'completed_conversations': conv_completed,
                'hours_back': hours,
                'by_agent': by_agent,
            }

        elif action == 'failures':
            items = list(
                AgentExecution.objects.filter(
                    created_at__gte=cutoff,
                    status='failed'
                ).order_by('-created_at')[:limit].values(
                    'id', 'agent__name', 'task', 'status', 'error_message',
                    'created_at'
                )
            )

            return {
                'action': 'failures',
                'count': len(items),
                'items': items,
                'hours_back': hours,
            }

        elif action == 'detail':
            exec_id = payload.get('id')
            if not exec_id:
                # No ID — return the most recent execution (optionally filtered by agent)
                qs = AgentExecution.objects.all()
                if agent_name:
                    qs = qs.filter(agent__name__icontains=agent_name)
                execution = qs.order_by('-created_at').first()
                if not execution:
                    return {'action': 'detail', 'error': 'No executions found'}
            else:
                execution = AgentExecution.objects.filter(id=exec_id).first()
                if not execution:
                    return {'action': 'detail', 'error': f'Execution {exec_id} not found'}

            output = execution.output_data or {}
            # Truncate very large output to avoid token explosion
            import json
            output_str = json.dumps(output, default=str)
            if len(output_str) > 8000:
                # Keep message/error/summary and truncate data
                truncated = {
                    'message': output.get('message', '')[:3000],
                    'error': output.get('error'),
                    'data': {k: v for k, v in (output.get('data') or {}).items()
                             if k in ('info_count', 'warning_count', 'critical_count',
                                      'items_count', 'execution_time', 'pipeline_steps',
                                      'final_video_url', 'type', 'summary', 'content',
                                      'result_preview', 'attempts', 'contract',
                                      'sources_count', 'query', 'evidence_claims')},
                    'result_preview': output.get('result_preview', '')[:2000],
                    'tool_calls': output.get('tool_calls', [])[:5],
                    '_truncated': True,
                    '_full_size_bytes': len(output_str),
                }
            else:
                truncated = output

            # Session 1185 F2: Reverse-link — surface deliverables produced by
            # this execution. Forward link (deliverable→execution) is in
            # provenance.origin_execution_id; this is the missing reverse pivot.
            # Cap at 25 to bound payload; document in tool schema description.
            from core.models_deliverables import Deliverable
            deliverables = list(
                Deliverable.objects.filter(
                    parent_object_id=execution.id,
                    parent_object_type='agent_execution',
                ).order_by('-created_at').values(
                    'id', 'title', 'category', 'created_at', 'is_saved',
                )[:25]
            )

            return {
                'action': 'detail',
                'id': str(execution.id),
                'agent_name': execution.agent.name if execution.agent else None,
                'task': execution.task,
                'status': execution.status,
                'error_message': execution.error_message,
                'execution_time_ms': execution.execution_time_ms,
                'created_at': execution.created_at,
                'completed_at': getattr(execution, 'completed_at', None),
                'output_data': truncated,
                'input_data_keys': list((execution.input_data or {}).keys()),
                'deliverables': deliverables,
            }

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: recent, by_agent, stats, failures, detail"
            )

    def _handle_learning_patterns(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 948: Learning patterns tool for viewing system learnings.

        Provides PA access to patterns the system has learned from execution data.

        Actions:
        - list: List active learning patterns (default)
        - by_type: Get patterns by type (tool_reliability, agent_performance, etc.)
        - stats: Get learning statistics
        """
        from core.models_unified_system import LearningPattern
        from django.db.models import Count

        action = payload.get('action', 'list')
        limit = payload.get('limit', 20)
        pattern_type = payload.get('pattern_type')
        min_confidence = payload.get('min_confidence', 0.5)

        if action == 'list':
            qs = LearningPattern.objects.filter(
                is_active=True,
                confidence__gte=min_confidence
            )

            if pattern_type:
                qs = qs.filter(pattern_type=pattern_type)

            items = list(
                qs.order_by('-confidence', '-updated_at')[:limit].values(
                    'id', 'pattern_type', 'description', 'confidence',
                    'pattern_data', 'applies_to_agents', 'times_applied',
                    'success_when_applied', 'updated_at'
                )
            )

            # Calculate effectiveness for each
            for item in items:
                applied = item.get('times_applied', 0)
                successful = item.get('success_when_applied', 0)
                item['effectiveness'] = successful / applied if applied > 0 else 0

            return {
                'action': 'list',
                'count': len(items),
                'items': items,
                'min_confidence': min_confidence,
            }

        elif action == 'by_type':
            if not pattern_type:
                # List available pattern types
                type_counts = dict(
                    LearningPattern.objects.filter(is_active=True)
                    .values('pattern_type')
                    .annotate(count=Count('id'))
                    .order_by('-count')
                    .values_list('pattern_type', 'count')
                )
                return {
                    'action': 'by_type',
                    'available_types': type_counts,
                    'message': 'Specify pattern_type to filter by type'
                }

            items = list(
                LearningPattern.objects.filter(
                    is_active=True,
                    pattern_type=pattern_type,
                    confidence__gte=min_confidence
                ).order_by('-confidence')[:limit].values(
                    'id', 'pattern_type', 'description', 'confidence',
                    'pattern_data', 'applies_to_agents', 'times_applied',
                    'success_when_applied', 'updated_at'
                )
            )

            return {
                'action': 'by_type',
                'pattern_type': pattern_type,
                'count': len(items),
                'items': items,
            }

        elif action == 'stats':
            total = LearningPattern.objects.filter(is_active=True).count()
            by_type = dict(
                LearningPattern.objects.filter(is_active=True)
                .values('pattern_type')
                .annotate(count=Count('id'))
                .order_by('-count')
                .values_list('pattern_type', 'count')
            )

            # Top performing patterns
            top_patterns = list(
                LearningPattern.objects.filter(
                    is_active=True,
                    times_applied__gt=0
                ).order_by('-confidence')[:5].values(
                    'description', 'confidence', 'pattern_type'
                )
            )

            return {
                'action': 'stats',
                'total_patterns': total,
                'by_type': by_type,
                'top_patterns': top_patterns,
            }

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: list, by_type, stats"
            )

    def _handle_feedback(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 948: Handle user feedback viewing and management.
        Session 1061: Fixed handler signature (was old-style, caused crash).

        Actions:
        - list: List feedback items (optionally filtered by status)
        - stats: Get feedback statistics
        - submit: Submit new feedback
        - update: Update feedback status (admin only)
        """
        from core.models_user_feedback import UserFeedback

        action = payload.get('action', 'list')
        status_filter = payload.get('status')
        limit = payload.get('limit', 20)

        if action == 'list':
            qs = UserFeedback.objects.all()
            if status_filter:
                qs = qs.filter(status=status_filter)
            else:
                # Default to open items
                qs = qs.filter(status='open')

            items = list(qs[:limit].values(
                'id', 'feedback_type', 'message', 'status',
                'created_at', 'trace_id'
            ))

            # Session 987: Serialize UUIDs and datetimes
            for item in items:
                item['id'] = str(item['id'])
                if item.get('created_at'):
                    item['created_at'] = item['created_at'].isoformat()

            return {
                'action': 'list',
                'status_filter': status_filter or 'open',
                'count': len(items),
                'items': items,
            }

        elif action == 'stats':
            summary = UserFeedback.get_feedback_summary()
            return {
                'action': 'stats',
                'total_open': summary['total_open'],
                'by_type': summary['by_type'],
                'by_status': summary['by_status'],
            }

        elif action == 'submit':
            from django.contrib.auth import get_user_model
            User = get_user_model()

            comment = payload.get('comment', '')
            target_type = payload.get('target_type', 'general')

            if not comment:
                return {'error': 'comment is required for submit'}

            user = User.objects.filter(id=user_id).first() if user_id else None
            if not user:
                user = User.objects.first()

            feedback = UserFeedback.objects.create(
                user=user,
                feedback_type=target_type if target_type in (
                    'ui_ux_issue', 'bug', 'feature_request', 'feedback'
                ) else 'feedback',
                message=comment,
                status='open',
                trace_id=trace_id if trace_id and not trace_id.startswith('pa-') else '',
            )

            return {
                'action': 'submit',
                'id': str(feedback.id),
                'success': True,
                'message': 'Feedback submitted successfully',
            }

        elif action == 'update':
            feedback_id = payload.get('id')
            new_status = payload.get('new_status')
            notes = payload.get('notes', '')

            if not feedback_id or not new_status:
                raise ValueError("Update requires 'id' and 'new_status'")

            try:
                feedback = UserFeedback.objects.get(id=feedback_id)
                feedback.status = new_status
                if notes:
                    feedback.resolution_notes = notes
                feedback.save()

                return {
                    'action': 'update',
                    'id': feedback_id,
                    'new_status': new_status,
                    'success': True,
                }
            except UserFeedback.DoesNotExist:
                raise ValueError(f"Feedback item {feedback_id} not found")

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: list, stats, submit, update"
            )


    # ------------------------------------------------------------------ #
    # Session 969: Live telemetry tools for PA self-awareness             #
    # ------------------------------------------------------------------ #

    def _handle_recent_activity(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 969: Recent activity tool — comprehensive activity snapshot.

        Answers "What's been going on?" across all major subsystems.

        Actions:
        - summary: High-level counts and latest items (default)
        - detailed: Same but with more items per section
        """
        from django.utils import timezone
        from django.db.models import Count
        from datetime import timedelta

        action = payload.get('action', 'summary')
        hours = payload.get('hours', 2)
        cutoff = timezone.now() - timedelta(hours=hours)
        item_limit = 5 if action == 'summary' else 15

        sections = {}

        # 1. Celery tasks — Session 983: use CeleryTaskEvent (our own
        # telemetry) instead of TaskResult (empty when backend=redis)
        try:
            from core.models_celery_telemetry import CeleryTaskEvent
            task_qs = CeleryTaskEvent.objects.filter(started_at__gte=cutoff)
            by_status = dict(
                task_qs.values('status')
                .annotate(n=Count('id'))
                .values_list('status', 'n')
            )
            sections['celery_tasks'] = {
                'total': sum(by_status.values()),
                'by_status': by_status,
            }
        except Exception as e:
            sections['celery_tasks'] = {'error': str(e)}

        # 2. Spider data
        try:
            from core.models_unified_system import SpiderData
            spider_qs = SpiderData.objects.filter(created_at__gte=cutoff)
            total_spider = spider_qs.count()
            distinct_spiders = spider_qs.values('spider_name').distinct().count()
            top_spiders = list(
                spider_qs.values('spider_name')
                .annotate(n=Count('id'))
                .order_by('-n')[:item_limit]
                .values_list('spider_name', 'n')
            )
            sections['spider_data'] = {
                'total_items': total_spider,
                'distinct_spiders': distinct_spiders,
                'top_spiders': dict(top_spiders),
            }
        except Exception as e:
            sections['spider_data'] = {'error': str(e)}

        # 3. Conversations (HiveMindSession)
        try:
            from core.models_unified_system import HiveMindSession
            conv_qs = HiveMindSession.objects.filter(created_at__gte=cutoff)
            by_status = dict(
                conv_qs.values('status')
                .annotate(n=Count('id'))
                .values_list('status', 'n')
            )
            latest = list(
                conv_qs.order_by('-created_at')[:item_limit]
                .values('question', 'status', 'created_at')
            )
            for item in latest:
                if item.get('created_at'):
                    item['created_at'] = item['created_at'].isoformat()
                # Truncate long questions
                q = item.get('question', '')
                if len(q) > 120:
                    item['question'] = q[:120] + '...'
            sections['conversations'] = {
                'total': sum(by_status.values()),
                'by_status': by_status,
                'latest': latest,
            }
        except Exception as e:
            sections['conversations'] = {'error': str(e)}

        # 4. Blogs (SelfBlog)
        try:
            from core.models_unified_system import SelfBlog
            blog_qs = SelfBlog.objects.filter(created_at__gte=cutoff)
            total_blogs = blog_qs.count()
            published = blog_qs.filter(status='published').count()
            draft = blog_qs.filter(status='draft').count()
            latest = list(
                blog_qs.order_by('-created_at')[:item_limit]
                .values('title', 'status', 'created_at')
            )
            for item in latest:
                if item.get('created_at'):
                    item['created_at'] = item['created_at'].isoformat()
            sections['blogs'] = {
                'total': total_blogs,
                'published': published,
                'draft': draft,
                'latest': latest,
            }
        except Exception as e:
            sections['blogs'] = {'error': str(e)}

        # 5. Initiative changes
        try:
            from core.models_document_registry import Initiative
            init_qs = Initiative.objects.filter(
                updated_at__gte=cutoff,
                status='ACTIVE'
            )
            total_updated = init_qs.count()
            latest = list(
                init_qs.order_by('-updated_at')[:item_limit]
                .values('name', 'updated_at')
            )
            for item in latest:
                if item.get('updated_at'):
                    item['updated_at'] = item['updated_at'].isoformat()
            sections['initiatives'] = {
                'recently_updated': total_updated,
                'latest': latest,
            }
        except Exception as e:
            sections['initiatives'] = {'error': str(e)}

        # 6. Signal clusters
        try:
            from core.models_signal_intelligence import SignalCluster
            sig_qs = SignalCluster.objects.filter(
                detected_at__gte=cutoff,
                status='active'
            )
            total_signals = sig_qs.count()
            top_signals = list(
                sig_qs.order_by('-strength')[:item_limit]
                .values('name', 'strength', 'pattern_type')
            )
            sections['signals'] = {
                'active_clusters': total_signals,
                'top_by_strength': top_signals,
            }
        except Exception as e:
            sections['signals'] = {'error': str(e)}

        return {
            'action': action,
            'hours_back': hours,
            'sections': sections,
        }

    # _handle_system_health and _handle_error_summary deleted (Session 1079 PR2).
    # ops_tool.slo_status and ops_tool.failure_signatures replace them.

    def _handle_surgical_moves_status(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 970: Surgical moves status tool — deliberation session verification.

        Answers "surgical moves status" / "what deliberations happened" with
        session details, contract counts, evidence stats, and verdicts.

        Actions:
        - summary: Recent sessions with key stats (default)
        - detailed: Full session details including contracts and evidence
        """
        import json as _json
        from django.utils import timezone
        from datetime import timedelta

        action = payload.get('action', 'summary')
        hours = payload.get('hours', 24)
        session_id = payload.get('session_id')
        cutoff = timezone.now() - timedelta(hours=hours)
        limit = 5 if action == 'summary' else 20

        try:
            from core.models_deliberation import (
                DeliberationSession,
                DeliberationTurn,
                ContractRecord,
            )
        except ImportError:
            return {
                'action': action,
                'error': 'Deliberation models not available',
            }

        try:
            if session_id:
                sessions = DeliberationSession.objects.filter(id=session_id)
            else:
                sessions = DeliberationSession.objects.filter(
                    created_at__gte=cutoff
                ).order_by('-created_at')[:limit]

            runs = []
            for s in sessions:
                turns = DeliberationTurn.objects.filter(session=s)
                contracts = ContractRecord.objects.filter(session=s)
                turn_count = turns.count()
                ep = s.evidence_pack or {}

                contract_info = []
                verdict = None
                for c in contracts:
                    cdata = c.contract_data or {}
                    data_size = len(_json.dumps(cdata))
                    contract_info.append({
                        'type': c.contract_type,
                        'data_size': data_size,
                    })
                    if c.contract_type == 'execution':
                        verdict = cdata.get('chosen_path', cdata.get('decision', ''))
                        if isinstance(verdict, str):
                            verdict = verdict[:200]

                runs.append({
                    'session_id': str(s.id),
                    'objective': (s.objective or '')[:120],
                    'status': s.status,
                    'created_at': s.created_at.isoformat() if s.created_at else None,
                    'turn_count': turn_count,
                    'contract_count': len(contract_info),
                    'contracts': contract_info,
                    'decision_verdict': verdict,
                    'evidence_stats': {
                        'sources': len(ep.get('sources', [])),
                        'claims': len(ep.get('claims', [])),
                        'contradictions': len(ep.get('contradictions', [])),
                        'internal_refs': len(ep.get('internal_refs', [])),
                    },
                })

            return {
                'action': action,
                'hours_back': hours,
                'total_sessions': len(runs),
                'runs': runs,
            }
        except Exception as e:
            logger.error(f"[Session 970] Surgical moves status error: {e}")
            return {
                'action': action,
                'hours_back': hours,
                'total_sessions': 0,
                'runs': [],
                'error': str(e),
            }


    def _handle_stock_intelligence(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 979: Stock intelligence tool for PA access to market data.

        Surfaces MarketIntelligenceBrief, StockMarketAlert, PredictionOutcome,
        and SEC Edgar filings — the same data as the /stocks dashboard.

        Actions:
        - overview: Dashboard summary (default)
        - briefs: Recent market briefs
        - alerts: Stock alerts
        - predictions: Prediction outcomes with accuracy
        - sec_filings: SEC Edgar spider data
        """
        from core.models_unified_system import MarketIntelligenceBrief, PredictionOutcome, SpiderData
        from core.models_autonomous_alerts import StockMarketAlert
        from django.db.models import Count, Avg
        from django.utils import timezone
        from datetime import timedelta

        action = payload.get('action', 'overview')
        limit = payload.get('limit', 10)

        if action == 'overview':
            # Mirrors views_stock_intelligence.stock_dashboard
            latest_brief = MarketIntelligenceBrief.objects.first()
            latest_brief_data = None
            if latest_brief:
                latest_brief_data = {
                    'id': str(latest_brief.id),
                    'brief_date': latest_brief.brief_date.isoformat(),
                    'executive_summary': latest_brief.executive_summary[:300],
                    'total_stocks_analyzed': latest_brief.total_stocks_analyzed,
                    'debate_zone_count': latest_brief.debate_zone_count,
                    'situation_health': latest_brief.situation_health,
                }

            alert_counts = dict(
                StockMarketAlert.objects.values_list('alert_type')
                .annotate(count=Count('id'))
                .values_list('alert_type', 'count')
            )
            total_alerts = sum(alert_counts.values())

            predictions_eval = PredictionOutcome.objects.filter(was_correct_7_days__isnull=False)
            total_predictions = predictions_eval.count()
            correct_7d = predictions_eval.filter(was_correct_7_days=True).count()
            accuracy_7d = round((correct_7d / total_predictions) * 100, 1) if total_predictions > 0 else None

            predictions_30d = PredictionOutcome.objects.filter(was_correct_30_days__isnull=False)
            total_30d = predictions_30d.count()
            correct_30d = predictions_30d.filter(was_correct_30_days=True).count()
            accuracy_30d = round((correct_30d / total_30d) * 100, 1) if total_30d > 0 else None

            sec_count = SpiderData.objects.filter(spider_name='sec_edgar').count()
            total_briefs = MarketIntelligenceBrief.objects.count()

            return {
                'action': 'overview',
                'latest_brief': latest_brief_data,
                'total_briefs': total_briefs,
                'total_alerts': total_alerts,
                'alert_counts_by_type': alert_counts,
                'prediction_accuracy_7d': accuracy_7d,
                'prediction_accuracy_30d': accuracy_30d,
                'total_predictions': total_predictions,
                'sec_filings_count': sec_count,
            }

        elif action == 'briefs':
            qs = MarketIntelligenceBrief.objects.all()
            total = qs.count()
            briefs = qs[:limit]
            items = []
            for b in briefs:
                items.append({
                    'id': str(b.id),
                    'brief_date': b.brief_date.isoformat(),
                    'brief_type': b.brief_type,
                    'executive_summary': b.executive_summary[:300],
                    'total_stocks_analyzed': b.total_stocks_analyzed,
                    'debate_zone_count': b.debate_zone_count,
                    'situation_health': b.situation_health,
                })
            return {'action': 'briefs', 'items': items, 'total': total}

        elif action == 'alerts':
            qs = StockMarketAlert.objects.all()
            # Session 1062: Filter by ticker if provided
            ticker = payload.get('ticker', '')
            if ticker:
                qs = qs.filter(symbol__iexact=ticker)
            total = qs.count()
            alerts = qs[:limit]
            items = []
            for a in alerts:
                items.append({
                    'id': str(a.id),
                    'alert_type': a.alert_type,
                    'symbol': a.symbol,
                    'company_name': a.company_name,
                    'title': a.title,
                    'summary': a.summary[:200],
                    'confidence_score': float(a.confidence_score),
                    'bull_score': a.bull_score,
                    'bear_score': a.bear_score,
                    'recommended_action': a.recommended_action,
                    'detected_at': a.detected_at.isoformat() if a.detected_at else None,
                })
            return {'action': 'alerts', 'items': items, 'total': total}

        elif action == 'predictions':
            qs = PredictionOutcome.objects.all()
            # Session 1062: Filter by ticker if provided
            ticker = payload.get('ticker', '')
            if ticker:
                qs = qs.filter(ticker__iexact=ticker)
            total = qs.count()
            predictions = qs[:limit]
            items = []
            for p in predictions:
                items.append({
                    'id': str(p.id),
                    'ticker': p.ticker,
                    'prediction_type': p.prediction_type,
                    'conviction_level': p.conviction_level,
                    'predicted_move': float(p.predicted_move),
                    'prediction_date': p.prediction_date.isoformat(),
                    'was_correct_7_days': p.was_correct_7_days,
                    'was_correct_30_days': p.was_correct_30_days,
                })

            evaluated = qs.filter(was_correct_7_days__isnull=False)
            eval_count = evaluated.count()
            correct_7d = evaluated.filter(was_correct_7_days=True).count()
            correct_30d = evaluated.filter(was_correct_30_days=True).count()
            stats = {
                'evaluated_count': eval_count,
                'accuracy_7d_pct': round((correct_7d / eval_count) * 100, 1) if eval_count else None,
                'accuracy_30d_pct': round((correct_30d / eval_count) * 100, 1) if eval_count else None,
            }
            return {'action': 'predictions', 'items': items, 'total': total, 'stats': stats}

        elif action == 'sec_filings':
            qs = SpiderData.objects.filter(spider_name='sec_edgar').order_by('-created_at')
            total = qs.count()
            filings = qs[:limit]
            items = []
            for f in filings:
                items.append({
                    'id': str(f.id),
                    'source_url': f.source_url,
                    'data_type': f.data_type,
                    'relevance_score': f.relevance_score,
                    'created_at': f.created_at.isoformat() if f.created_at else None,
                })
            return {'action': 'sec_filings', 'items': items, 'total': total}

        else:
            logger.warning(f"Unknown stock_intelligence action '{action}', defaulting to overview")
            payload['action'] = 'overview'
            return self._handle_stock_intelligence(tool_name, payload, user_id, trace_id)

    def _handle_sports_betting(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 995B: Sports betting intelligence tool for PA.

        Surfaces wagers, arbitrage, predictions, sharp action, line movements,
        and full betting briefs — the same data as the /betting dashboard.

        Actions:
        - overview: Dashboard summary (default)
        - arbs: Active arbitrage opportunities
        - predictions: Game predictions
        - sharp_action: Sharp action signals
        - line_movements: Detected line movements
        - wagers: User's placed wagers
        - live_odds: Current odds from TheOddsSpider
        - brief: Full betting brief from coordinator
        """
        from django.utils import timezone
        from datetime import timedelta

        action = payload.get('action', 'overview')
        limit = payload.get('limit', 10)

        if action == 'overview':
            from core.models_betting import PlacedWager, BettingStats
            from core.models_human_interface import HumanAttentionItem

            pending = PlacedWager.objects.filter(status='pending').count()
            settled = PlacedWager.objects.filter(status__in=['won', 'lost', 'push']).count()

            arb_count = HumanAttentionItem.objects.filter(
                item_type='arbitrage',
                status='watching',
            ).count()

            # Recent sharp signals from SpiderData
            from core.models_unified_system import SpiderData
            cutoff = timezone.now() - timedelta(hours=12)
            recent_odds = SpiderData.objects.filter(
                spider_name='theodds',
                created_at__gte=cutoff,
            ).count()

            # Active sports from recent odds data
            active_sports = list(
                SpiderData.objects.filter(
                    spider_name='theodds',
                    created_at__gte=cutoff,
                ).values_list('data_type', flat=True).distinct()[:10]
            )

            return {
                'action': 'overview',
                'pending_wagers': pending,
                'settled_wagers': settled,
                'active_arb_opps': arb_count,
                'hot_sharp_signals': 0,  # populated by agent runs
                'recent_odds_records': recent_odds,
                'active_sports': active_sports,
            }

        elif action == 'arbs':
            from core.models_human_interface import HumanAttentionItem
            qs = HumanAttentionItem.objects.filter(
                item_type='arbitrage',
                status='watching',
            ).order_by('-created_at')
            total = qs.count()
            items = []
            for item in qs[:limit]:
                p = item.payload or {}
                items.append({
                    'id': str(item.id),
                    'matchup': p.get('matchup', p.get('event', '')),
                    'sport': p.get('sport', ''),
                    'profit_pct': p.get('profit_pct', 0),
                    'rating': p.get('rating', ''),
                    'home_book': p.get('home_book', ''),
                    'away_book': p.get('away_book', ''),
                    'created_at': item.created_at.isoformat() if item.created_at else None,
                })
            return {'action': 'arbs', 'items': items, 'total': total}

        elif action == 'predictions':
            try:
                from sports.models import MLPrediction
                qs = MLPrediction.objects.order_by('-created_at')
                # Gap 5 fix: Apply sport filter if provided
                sport = payload.get('sport', '').strip().lower()
                if sport:
                    qs = qs.filter(sport_type__icontains=sport)
                total = qs.count()
                items = []
                for p in qs[:limit]:
                    # MLPrediction: game FK (home_team/away_team on Game), predicted_winner FK to Team
                    game = getattr(p, 'game', None)
                    if game:
                        matchup = f"{getattr(game.away_team, 'abbreviation', game.away_team)} @ {getattr(game.home_team, 'abbreviation', game.home_team)}"
                    else:
                        matchup = str(p)
                    winner = getattr(p, 'predicted_winner', None)
                    items.append({
                        'id': str(p.id),
                        'matchup': matchup,
                        'predicted_winner': str(winner) if winner else '',
                        'confidence': getattr(p, 'confidence', 0),
                        'sport_type': getattr(p, 'sport_type', ''),
                        'created_at': p.created_at.isoformat() if hasattr(p, 'created_at') and p.created_at else None,
                    })
                return {'action': 'predictions', 'items': items, 'total': total}
            except Exception as e:
                logger.warning(f"MLPrediction query failed: {e}")
                return {'action': 'predictions', 'items': [], 'total': 0, 'error': str(e)}

        elif action == 'accuracy':
            try:
                from sports.models import MLPrediction
                from core.models_betting import PlacedWager
                from django.db.models import Sum, Count, Q, Avg

                sport = payload.get('sport', None)
                days = payload.get('days', 30)

                # Overall accuracy from MLPrediction.calculate_accuracy
                overall = MLPrediction.calculate_accuracy(sport_type=sport, days=days)

                # Per-sport breakdown
                from django.utils import timezone as tz
                from datetime import timedelta
                cutoff = tz.now() - timedelta(days=days)
                sport_qs = MLPrediction.objects.filter(
                    created_at__gte=cutoff,
                    was_correct__isnull=False,
                )
                if sport:
                    sport_qs = sport_qs.filter(sport_type=sport)

                by_sport = []
                for row in sport_qs.values('sport_type').annotate(
                    total=Count('id'),
                    correct=Count('id', filter=Q(was_correct=True)),
                    avg_confidence=Avg('confidence'),
                ).order_by('-total'):
                    total_s = row['total']
                    by_sport.append({
                        'sport': row['sport_type'],
                        'total': total_s,
                        'correct': row['correct'],
                        'accuracy_pct': round((row['correct'] / total_s) * 100, 2) if total_s else 0,
                        'avg_confidence': round(row['avg_confidence'] or 0, 2),
                    })

                # Wager win/loss/push stats
                wager_qs = PlacedWager.objects.filter(placed_at__gte=cutoff)
                if user_id:
                    wager_qs = wager_qs.filter(user_id=user_id)
                agg = wager_qs.aggregate(
                    total=Count('id'),
                    won=Count('id', filter=Q(status='won')),
                    lost=Count('id', filter=Q(status='lost')),
                    push=Count('id', filter=Q(status='push')),
                    pending=Count('id', filter=Q(status='pending')),
                    total_staked=Sum('stake'),
                    total_pnl=Sum('result_amount'),
                )
                total_staked = float(agg['total_staked'] or 0)
                total_pnl = float(agg['total_pnl'] or 0)
                wager_stats = {
                    'total_wagers': agg['total'],
                    'won': agg['won'],
                    'lost': agg['lost'],
                    'push': agg['push'],
                    'pending': agg['pending'],
                    'win_rate_pct': round((agg['won'] / (agg['won'] + agg['lost'])) * 100, 2) if (agg['won'] + agg['lost']) > 0 else 0,
                    'total_staked': total_staked,
                    'total_pnl': total_pnl,
                    'roi_pct': round((total_pnl / total_staked) * 100, 2) if total_staked > 0 else 0,
                }

                return {
                    'action': 'accuracy',
                    'overall': overall,
                    'by_sport': by_sport,
                    'wager_stats': wager_stats,
                    'days': days,
                }
            except Exception as e:
                logger.warning(f"Accuracy query failed: {e}")
                return {'action': 'accuracy', 'overall': {}, 'by_sport': [], 'wager_stats': {}, 'days': payload.get('days', 30), 'error': str(e)}

        elif action == 'sharp_action':
            # Session 1075: Dispatch async — SharpActionDetector can exceed 30s tool timeout
            from core.tasks import execute_agent_task
            celery_task = execute_agent_task.apply_async(
                args=['SharpActionDetector', 'Identify sharp betting action and stale lines',
                      {'user_id': str(user_id) if user_id else None, 'limit': limit}],
                queue='long_running',
            )
            return {
                'task_id': str(celery_task.id),
                'mode': 'async',
                'action': 'sharp_action',
                'message': f'Sharp action analysis dispatched (task {celery_task.id}). Use job_status to check progress.',
            }

        elif action == 'line_movements':
            # Session 1075: Dispatch async — LineMovementAnalyzer can exceed 30s tool timeout
            from core.tasks import execute_agent_task
            celery_task = execute_agent_task.apply_async(
                args=['LineMovementAnalyzer', 'Detect sharp money line movements',
                      {'user_id': str(user_id) if user_id else None, 'limit': limit}],
                queue='long_running',
            )
            return {
                'task_id': str(celery_task.id),
                'mode': 'async',
                'action': 'line_movements',
                'message': f'Line movement analysis dispatched (task {celery_task.id}). Use job_status to check progress.',
            }

        elif action == 'wagers':
            from core.models_betting import PlacedWager
            qs = PlacedWager.objects.all().order_by('-placed_at')
            if user_id:
                qs = qs.filter(user_id=user_id)
            total = qs.count()
            items = []
            for w in qs[:limit]:
                items.append({
                    'id': str(w.id),
                    'description': w.description if hasattr(w, 'description') else str(w),  # type: ignore[attr-defined]
                    'status': w.status,
                    'stake': float(w.stake) if hasattr(w, 'stake') and w.stake else 0,
                    'potential_payout': float(w.potential_payout) if hasattr(w, 'potential_payout') and w.potential_payout else 0,
                    'placed_at': w.placed_at.isoformat() if w.placed_at else None,
                })
            return {'action': 'wagers', 'items': items, 'total': total}

        elif action == 'record_wager':
            from core.models_betting import PlacedWager
            from decimal import Decimal, InvalidOperation

            description = payload.get('description', '').strip()
            if not description:
                raise ValueError("'description' is required for record_wager")

            try:
                stake = Decimal(str(payload.get('stake', 0)))
            except (InvalidOperation, TypeError):
                raise ValueError("'stake' must be a valid number")
            if stake <= 0:
                raise ValueError("'stake' must be positive")

            try:
                odds = Decimal(str(payload.get('odds', 0)))
            except (InvalidOperation, TypeError):
                raise ValueError("'odds' must be a valid number")

            # Compute potential payout (American odds)
            if odds > 0:
                potential_payout = stake * (odds / Decimal('100'))
            elif odds < 0:
                potential_payout = stake * (Decimal('100') / abs(odds))
            else:
                potential_payout = stake  # even money fallback

            # PlacedWager has no 'description' field — use 'notes' instead
            wager_kwargs = {
                'notes': description,
                'stake': stake,
                'odds': int(odds),  # PlacedWager.odds is IntegerField
                'potential_payout': potential_payout,
                'status': 'pending',
            }
            if user_id:
                wager_kwargs['user_id'] = user_id

            extra_notes = payload.get('notes', '').strip()
            if extra_notes:
                wager_kwargs['notes'] = f"{description} | {extra_notes}"
            wager_type = payload.get('wager_type', '').strip()
            if hasattr(PlacedWager, 'wager_type') and wager_type:
                wager_kwargs['wager_type'] = wager_type

            wager = PlacedWager.objects.create(**wager_kwargs)
            return {
                'action': 'record_wager',
                'id': str(wager.id),
                'description': wager.notes,
                'stake': str(wager.stake),
                'odds': float(odds),
                'potential_payout': str(wager.potential_payout),
                'status': wager.status,
                'success': True,
            }

        elif action in ('brief', 'live_odds'):
            # Session 1088: Dispatch to Celery async — generate_brief() is slow
            # and was causing 30s TOOL_TIMEOUT in the PA.
            from core.tasks import execute_agent_task
            celery_task = execute_agent_task.apply_async(
                args=['GamePredictor', f'Generate a full betting brief ({action})',
                      {'user_id': str(user_id) if user_id else None, 'action': action}],
                queue='long_running',
            )
            return {
                'task_id': str(celery_task.id),
                'mode': 'async',
                'action': action,
                'message': f'Betting brief dispatched (task {celery_task.id}). Use job_status to check progress.',
            }

        else:
            logger.warning(f"Unknown sports_betting action '{action}', defaulting to overview")
            payload['action'] = 'overview'
            return self._handle_sports_betting(tool_name, payload, user_id, trace_id)

    def _handle_content(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """
        Session 1079: Content gateway — thin dispatcher over content_review_tool,
        generate_blog_tool, and deliverables_tool.

        Consolidates 3 content tools into one surface:
        - content_* actions → content_review_tool
        - generate_blog → generate_blog_tool
        - deliverable_* actions → deliverables_tool
        """
        action = payload.get('action', '')

        # Session 1103c: aliases for natural-name guesses that GPT-5.2
        # keeps emitting. Same pattern as work_tool stats / ops_tool
        # overview / governance_tool stats fixes earlier this session.
        ACTION_ALIASES = {
            'recent': 'content_recent',
            'list': 'content_list',
            'search': 'content_search',
            'stats': 'content_stats',
            'detail': 'content_detail',
            'details': 'content_detail',
            'approve': 'content_approve',
            'reject': 'content_reject',
            # Session 1170: terminal-state action for one-shot analyses
            # (ops snapshots, daily diagnostics) where 'archive' would
            # discard useful history. Maps to status='completed'.
            'complete': 'content_complete',
            'mark_complete': 'content_complete',
            'mark_completed': 'content_complete',
            'done': 'content_complete',
        }
        if action in ACTION_ALIASES:
            action = ACTION_ALIASES[action]
            payload = dict(payload)
            payload['action'] = action

        # Session 1077: Smart action inference — GPT-5.2 sometimes omits the
        # action field. Infer from other params present in the payload.
        if not action:
            keys = set(payload.keys())
            if 'append' in keys or 'prepend' in keys:
                action = 'deliverable_update'
            elif 'content_offset' in keys or 'content_limit' in keys:
                action = 'deliverable_detail'
            elif keys & {'full'}:
                action = 'deliverable_detail'
            elif 'topic' in keys and 'tone' in keys:
                action = 'generate_blog'
            elif 'id' in keys and 'content' in keys and len(keys) > 3:
                action = 'deliverable_update'
            elif 'id' in keys and not (keys & {'query', 'type', 'category'}):
                action = 'deliverable_detail'
            else:
                action = 'content_stats'  # safe fallback

        import logging as _cl
        _cl.getLogger('core.services.td_handlers_content').info(
            f"[content_tool] action={action!r} payload_keys={sorted(payload.keys())}"
        )

        # ── content_review_tool actions ──
        CONTENT_REVIEW_MAP = {
            'content_stats': 'stats',
            'content_list': 'list',
            'content_detail': 'details',
            'content_search': 'search',
            'content_recent': 'recent',
            'content_approve': 'approve',
            'content_reject': 'reject',
            # Session 1170: terminal-state action for one-shot analyses
            # — see _handle_content_review elif action == 'complete'.
            'content_complete': 'complete',
        }

        if action in CONTENT_REVIEW_MAP:
            review_payload = dict(payload)
            review_payload['action'] = CONTENT_REVIEW_MAP[action]
            result = self._handle_content_review('content_review_tool', review_payload, user_id, trace_id)
            if isinstance(result, dict):
                result['gateway'] = 'content_tool'
                result['action'] = action
            return result

        # ── Session 1101: Bulk archive ──
        if action == 'bulk_archive':
            return self._handle_bulk_archive(payload, user_id, trace_id)

        # ── Session 1101: Bulk archive published (admin-only, category-scoped) ──
        if action == 'bulk_archive_published':
            return self._handle_bulk_archive_published(payload, user_id, trace_id)

        # ── Session 1101: Manual cleanup trigger ──
        if action == 'run_cleanup':
            from core.tasks import cleanup_stale_content
            cutoff_days = int(payload.get('cutoff_days', 7))
            statuses = payload.get('statuses', ['ready', 'draft'])
            cap = min(int(payload.get('cap', 500)), 2000)
            protected_types = payload.get('protected_types', [])
            task = cleanup_stale_content.delay(
                cutoff_days=cutoff_days,
                statuses=statuses,
                protected_types=protected_types,
                cap=cap,
            )
            return {
                'gateway': 'content_tool',
                'action': 'run_cleanup',
                'task_id': str(task.id),
                'mode': 'async',
                'message': f'Cleanup task dispatched (cutoff={cutoff_days}d, statuses={statuses}, cap={cap}). Poll task_id for results.',
            }

        # ── generate_blog_tool ──
        if action == 'generate_blog':
            blog_payload = dict(payload)
            # generate_blog_tool expects 'topic' and optional 'tone'
            result = self._handle_generate_blog('generate_blog_tool', blog_payload, user_id, trace_id)
            if isinstance(result, dict):
                result['gateway'] = 'content_tool'
                result['action'] = action
            return result

        # ── Operator Edge Newsletter ──
        if action == 'generate_newsletter':
            from core.tasks import generate_operator_edge_newsletter
            hours = int(payload.get('hours', 72))
            cluster_limit = int(payload.get('cluster_limit', 5))
            dry_run = bool(payload.get('dry_run', False))

            if dry_run:
                # Synchronous dry run — just gather data, no LLM call
                from core.tasks_content import _gather_newsletter_evidence
                evidence = _gather_newsletter_evidence(hours=hours, cluster_limit=cluster_limit)
                clusters = evidence['clusters']
                return {
                    'gateway': 'content_tool',
                    'action': 'generate_newsletter',
                    'mode': 'dry_run',
                    'clusters_found': len(clusters),
                    'top_clusters': [c['name'] for c in clusters[:3]],
                    'evidence_preview': evidence['evidence_block'][:2000],
                    'message': f'Dry run: found {len(clusters)} clusters. '
                               f'Run with dry_run=false to generate the newsletter.',
                }

            task = generate_operator_edge_newsletter.apply_async(
                kwargs={'hours': hours, 'cluster_limit': cluster_limit, 'dry_run': False},
                queue='content',
            )
            return {
                'gateway': 'content_tool',
                'action': 'generate_newsletter',
                'mode': 'async',
                'task_id': str(task.id),
                'message': 'Operator Edge newsletter generation queued. '
                           'Typically takes 2-4 minutes. Check deliverables for the result.',
            }

        # ── deliverables_tool actions ──
        DELIVERABLE_MAP = {
            'deliverable_list': 'list',
            'deliverable_detail': 'detail',
            'deliverable_search': 'search',
            'deliverable_save': 'save',
            'deliverable_create': 'create',
            'deliverable_update': 'update',
            'deliverable_append': 'append',
            'deliverable_stats': 'stats',
            'deliverable_export_pdf': 'export_pdf',
        }

        if action in DELIVERABLE_MAP:
            del_payload = dict(payload)
            del_payload['action'] = DELIVERABLE_MAP[action]
            result = self._handle_deliverables('deliverables_tool', del_payload, user_id, trace_id)
            if isinstance(result, dict):
                result['gateway'] = 'content_tool'
                result['action'] = action
            return result

        # ── Session 1100: Podcast episodes ──
        if action == 'podcasts':
            try:
                from core.models_unified_system import AgentExecution
                limit = min(int(payload.get('limit', 10)), 30)
                eps = AgentExecution.objects.filter(
                    agent__name='PodcastCoordinatorAgent', status='completed'
                ).order_by('-created_at')[:limit]
                return {
                    'gateway': 'content_tool', 'action': action,
                    'count': len(eps),
                    'episodes': [{
                        'id': str(e.id),
                        'topic': (e.input_data or {}).get('task', '')[:150],
                        'status': e.status,
                        'created_at': e.created_at.isoformat() if e.created_at else None,
                    } for e in eps],
                }
            except Exception as e:
                return {'gateway': 'content_tool', 'action': action, 'error': str(e)}

        # ── Session 1100: AI Series workflows ──
        if action == 'series':
            try:
                from core.models_unified_system import AgentExecution
                limit = min(int(payload.get('limit', 10)), 30)
                series = AgentExecution.objects.filter(
                    agent__name='AISeriesWorkflowAgent'
                ).order_by('-created_at')[:limit]
                return {
                    'gateway': 'content_tool', 'action': action,
                    'count': len(series),
                    'series': [{
                        'id': str(s.id),
                        'topic': (s.input_data or {}).get('task', '')[:150],
                        'status': s.status,
                        'created_at': s.created_at.isoformat() if s.created_at else None,
                    } for s in series],
                }
            except Exception as e:
                return {'gateway': 'content_tool', 'action': action, 'error': str(e)}

        # ── Session 1100: Content Studio stats ──
        if action == 'content_studio':
            try:
                from core.models_unified_system import AgentExecution
                from django.db.models import Count
                studio_agents = [
                    'AutonomousContentStudioCoordinator', 'TopicMinerAgent',
                    'ContrarianAgent', 'PerformanceAnalystAgent',
                    'VoiceCriticAgent', 'ContentDiversityOrchestrator',
                ]
                stats = list(AgentExecution.objects.filter(
                    agent__name__in=studio_agents
                ).values('agent__name', 'status').annotate(count=Count('id')))
                return {
                    'gateway': 'content_tool', 'action': action,
                    'stats': stats,
                }
            except Exception as e:
                return {'gateway': 'content_tool', 'action': action, 'error': str(e)}

        # ── Session R2-5: Initiative stage document fetch ──
        if action == 'initiative_doc':
            try:
                doc_id = payload.get('document_id', '') or payload.get('id', '')
                stage_id = payload.get('stage_id', '')
                initiative_name = payload.get('initiative', '').strip()

                from core.models_document_registry import InitiativeStage
                from core.models_unified_system import SelfBlog

                stage = None
                if stage_id:
                    stage = InitiativeStage.objects.select_related('document', 'initiative').filter(id=stage_id).first()
                elif doc_id:
                    # Fetch document directly
                    doc = SelfBlog.objects.filter(id=doc_id).first()
                    if not doc:
                        return {'gateway': 'content_tool', 'action': action, 'error': f'Document {doc_id} not found'}
                    stage = InitiativeStage.objects.select_related('initiative').filter(document=doc).first()
                    return {
                        'gateway': 'content_tool', 'action': action,
                        'document_id': str(doc.id),
                        'title': doc.title,
                        'content': doc.full_text[:5000],
                        'content_type': doc.content_type,
                        'created_at': doc.created_at.isoformat(),
                        'initiative': stage.initiative.name if stage else None,
                        'stage': stage.stage if stage else None,
                        'stage_status': stage.status if stage else None,
                    }
                elif initiative_name:
                    from core.models import Initiative
                    init = Initiative.objects.filter(name__icontains=initiative_name).first()
                    if not init:
                        return {'gateway': 'content_tool', 'action': action, 'error': f'Initiative "{initiative_name}" not found'}
                    stages = InitiativeStage.objects.filter(initiative=init).select_related('document').order_by('stage')
                    return {
                        'gateway': 'content_tool', 'action': action,
                        'initiative': init.name,
                        'stages': [{
                            'stage': s.stage,
                            'status': s.status,
                            'document_id': str(s.document.id) if s.document else None,
                            'document_title': s.document.title if s.document else None,
                            'document_preview': (s.document.full_text[:300] if s.document else ''),
                        } for s in stages],
                    }
                else:
                    return {'gateway': 'content_tool', 'action': action, 'error': 'Provide document_id, stage_id, or initiative name'}

                if not stage:
                    return {'gateway': 'content_tool', 'action': action, 'error': f'Stage {stage_id} not found'}
                doc = stage.document
                return {
                    'gateway': 'content_tool', 'action': action,
                    'stage_id': str(stage.id),
                    'stage': stage.stage,
                    'status': stage.status,
                    'initiative': stage.initiative.name,
                    'document_id': str(doc.id) if doc else None,
                    'title': doc.title if doc else None,
                    'content': (doc.full_text[:5000] if doc else ''),
                    'content_type': doc.content_type if doc else None,
                }
            except Exception as e:
                return {'gateway': 'content_tool', 'action': action, 'error': str(e)}

        all_actions = sorted(
            list(CONTENT_REVIEW_MAP) + ['generate_blog', 'generate_newsletter', 'bulk_archive', 'bulk_archive_published', 'run_cleanup'] + list(DELIVERABLE_MAP)
            + ['podcasts', 'series', 'content_studio', 'initiative_doc']
        )
        return {'error': f'Unknown content_tool action: {action}. Valid: {", ".join(all_actions)}'}

    # ── Session 1101: Bulk Archive ─────────────────────────────────────────────
    def _handle_bulk_archive(self, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """
        Session 1101: Bulk archive deliverables by filter criteria.
        Supports dry_run (default) for preview before execution.
        """
        from core.models_deliverables import Deliverable
        from django.db.models import Q
        from django.utils import timezone

        dry_run = payload.get('dry_run', True)
        cap = min(int(payload.get('cap', payload.get('limit', 500))), 2000)

        # Build filter queryset
        base_qs = Deliverable.objects.all()
        if user_id:
            base_qs = base_qs.filter(Q(user_id=user_id) | Q(user__isnull=True))

        # Never archive published or already-archived items
        raw_statuses = payload.get('statuses', ['ready', 'draft', 'completed'])
        # Session 1077: Coerce string to list (GPT sometimes sends 'ready' instead of ['ready'])
        if isinstance(raw_statuses, str):
            raw_statuses = [s.strip() for s in raw_statuses.split(',') if s.strip()]
        safe_statuses = [s for s in raw_statuses if s not in ('published', 'archived')]
        if not safe_statuses:
            return {'error': 'Cannot bulk archive published/archived items. Valid statuses: ready, draft, completed, approved'}

        qs = base_qs.filter(status__in=safe_statuses)

        # Optional filters
        dtype = payload.get('type')
        if dtype:
            qs = qs.filter(deliverable_type=dtype)
        category = payload.get('category')
        if category:
            qs = qs.filter(category__iexact=category)
        agent = payload.get('agent')
        if agent:
            qs = qs.filter(agent_name__iexact=agent)

        # Session 1077: Extended filters for cleanup (designed by Rigby)
        # Multiple agent names
        agent_names = payload.get('agent_names')
        if agent_names and isinstance(agent_names, list):
            qs = qs.filter(agent_name__in=agent_names)

        # Title prefix matching — archive items whose title starts with any prefix
        title_prefixes = payload.get('title_prefixes')
        if title_prefixes and isinstance(title_prefixes, list):
            from functools import reduce
            prefix_q = reduce(lambda a, b: a | b, [Q(title__istartswith=p) for p in title_prefixes])
            qs = qs.filter(prefix_q)

        # Protected categories — exclude these from archiving
        protected_categories = payload.get('protected_categories')
        if protected_categories and isinstance(protected_categories, list):
            qs = qs.exclude(category__in=protected_categories)

        # Date range — created_before is the key filter for "older than X days"
        created_before = payload.get('created_before')
        created_after = payload.get('created_after')
        if created_before:
            from django.utils.dateparse import parse_datetime
            dt = parse_datetime(created_before)
            if dt:
                qs = qs.filter(created_at__lt=dt)
        if created_after:
            from django.utils.dateparse import parse_datetime
            dt = parse_datetime(created_after)
            if dt:
                qs = qs.filter(created_at__gte=dt)

        # Exclude pinned/saved items
        qs = qs.filter(is_saved=False)
        if hasattr(Deliverable, 'is_pinned'):
            qs = qs.filter(is_pinned=False)

        total_matching = qs.count()

        # Build summary by type/category/agent
        from django.db.models import Count
        by_type = list(qs.values('deliverable_type').annotate(count=Count('id')).order_by('-count')[:10])
        by_category = list(qs.values('category').annotate(count=Count('id')).order_by('-count')[:10])
        by_agent = list(qs.values('agent_name').annotate(count=Count('id')).order_by('-count')[:10])
        by_status = list(qs.values('status').annotate(count=Count('id')).order_by('-count'))

        # Sample items for preview
        sample = list(
            qs.order_by('created_at')[:20].values(
                'id', 'title', 'deliverable_type', 'category',
                'agent_name', 'status', 'created_at'
            )
        )

        result = {
            'action': 'bulk_archive',
            'dry_run': dry_run,
            'total_matching': total_matching,
            'cap': cap,
            'will_archive': min(total_matching, cap),
            'filters': {
                'statuses': safe_statuses,
                'type': dtype,
                'category': category,
                'agent': agent,
                'created_before': created_before,
                'created_after': created_after,
            },
            'breakdown': {
                'by_type': by_type,
                'by_category': by_category,
                'by_agent': by_agent,
                'by_status': by_status,
            },
            'sample_items': sample,
        }

        if dry_run:
            result['message'] = f'DRY RUN: {min(total_matching, cap)} items would be archived. Set dry_run=false to execute.'
            return result

        # Execute archive
        to_archive = qs.order_by('created_at')[:cap]
        archived_ids = list(to_archive.values_list('id', flat=True))
        archived_count = Deliverable.objects.filter(id__in=archived_ids).update(
            status='archived',
            updated_at=timezone.now(),
        )

        logger.info(f"[BULK_ARCHIVE] {trace_id} Archived {archived_count} deliverables "
                     f"(filters: statuses={safe_statuses}, type={dtype}, category={category}, "
                     f"agent={agent}, created_before={created_before})")

        result['archived_count'] = archived_count
        result['message'] = f'Archived {archived_count} deliverables.'
        return result

    # ── Session 1101: Bulk Archive Published (admin-only) ────────────────────
    def _handle_bulk_archive_published(self, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """
        Session 1101: Archive published deliverables by category.
        Admin-only. Requires created_before + categories. confirm=true to execute.
        Blogs are explicitly blocked.
        """
        from core.models_deliverables import Deliverable
        from django.db.models import Count, Q
        from django.utils import timezone
        from django.utils.dateparse import parse_datetime

        # ── Permission gate ──
        # Session 1103c: the previous silent swallow was fail-closed
        # (which is the right security stance) but logged nothing, so
        # if a DB hiccup denied a legit admin there was zero trail.
        # Keep fail-closed; log loudly.
        is_admin = False
        if user_id:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.filter(id=user_id).first()
                if user and (user.is_superuser or user.is_staff):
                    is_admin = True
            except Exception as e:
                logger.warning(
                    "td_handlers_content.bulk_archive_published: admin "
                    "check failed for user_id=%s (%s: %s) — denying "
                    "access",
                    user_id, type(e).__name__, e,
                )
        if not is_admin:
            return {'error': 'Permission denied. bulk_archive_published requires admin/staff.', 'status': 403}

        # ── Hard block on blogs ──
        types_filter = payload.get('types', [])
        if types_filter and 'blog' in [t.lower() for t in types_filter]:
            return {'error': 'Blogs are not supported by bulk_archive_published. Use content_reject for individual blog archival.'}

        # ── Required params ──
        categories = payload.get('categories')
        if not categories or not isinstance(categories, list):
            return {'error': 'categories (list of strings) is required. Example: ["initiative_completion"]'}

        created_before = payload.get('created_before')
        if not created_before:
            return {'error': 'created_before (ISO-8601 datetime) is required for safety.'}

        dt_before = parse_datetime(created_before)
        if not dt_before:
            return {'error': f'Invalid created_before datetime: {created_before}. Use ISO-8601 format.'}

        dry_run = payload.get('dry_run', True)
        confirm = payload.get('confirm', False)
        cap = min(int(payload.get('cap', 500)), 2000)
        agent_filter = payload.get('agent')

        # ── Build queryset ──
        qs = Deliverable.objects.filter(
            status='published',
            category__in=categories,
            created_at__lt=dt_before,
        )
        # Scope to user if not superuser-level
        if user_id:
            qs = qs.filter(Q(user_id=user_id) | Q(user__isnull=True))
        if agent_filter:
            qs = qs.filter(agent_name__iexact=agent_filter)
        # Exclude blogs at the queryset level
        qs = qs.exclude(deliverable_type__iexact='blog')

        total_matching = qs.count()

        # ── Breakdown ──
        by_type = list(qs.values('deliverable_type').annotate(count=Count('id')).order_by('-count')[:10])
        by_category = list(qs.values('category').annotate(count=Count('id')).order_by('-count')[:10])
        by_agent = list(qs.values('agent_name').annotate(count=Count('id')).order_by('-count')[:10])

        # ── Sample ──
        sample = list(
            qs.order_by('created_at')[:25].values(
                'id', 'title', 'deliverable_type', 'category',
                'agent_name', 'status', 'created_at'
            )
        )

        result = {
            'action': 'bulk_archive_published',
            'dry_run': dry_run,
            'total_matching': total_matching,
            'cap': cap,
            'will_archive': min(total_matching, cap),
            'filters': {
                'status': 'published',
                'categories': categories,
                'created_before': created_before,
                'agent': agent_filter,
            },
            'breakdown': {
                'by_type': by_type,
                'by_category': by_category,
                'by_agent': by_agent,
            },
            'sample_items': sample,
        }

        if dry_run:
            result['message'] = f'DRY RUN: {min(total_matching, cap)} published items would be archived. Set dry_run=false and confirm=true to execute.'
            return result

        # ── Execute requires confirm ──
        if not confirm:
            return {'error': 'Execute requires confirm=true. Run with dry_run=true first to preview.', **result}

        to_archive_ids = list(qs.order_by('created_at').values_list('id', flat=True)[:cap])
        archived_count = Deliverable.objects.filter(id__in=to_archive_ids).update(
            status='archived',
            updated_at=timezone.now(),
        )

        # ── Audit log ──
        logger.info(
            f"[BULK_ARCHIVE_PUBLISHED] {trace_id} user={user_id} archived={archived_count} "
            f"categories={categories} created_before={created_before} agent={agent_filter} cap={cap}"
        )

        # Remaining count under same filters
        remaining = qs.count()

        result['archived_count'] = archived_count
        result['remaining_count'] = remaining
        result['message'] = f'Archived {archived_count} published deliverables. {remaining} remaining under same filters.'
        return result

    # ── Session 1078: Ops Tool ─────────────────────────────────────────────────
