"""
DeliverableFactory — Single gateway for creating Deliverables.

Consolidates 23+ scattered Deliverable.objects.create() calls into one
factory with consistent metadata, workspace assignment, and provenance tracking.

Usage:
    from core.services.deliverable_factory import create_deliverable

    deliverable = create_deliverable(
        title="Market Analysis Report",
        content="## Findings\n...",
        agent_name="ResearchAgent",
        category="Research",
        user=request.user,
        # Optional:
        workspace_id=workspace.id,
        trace_id=trace_id,
        parent_execution_id=execution.id,
        tags=["research", "market"],
        content_format="markdown",
        quality_score=0.85,
        metadata={"source": "scheduled_run"},
    )
"""

import hashlib
import logging
import uuid
from typing import Optional, List, Any

from django.conf import settings

logger = logging.getLogger(__name__)


def _content_hash(title: str, content: str, agent_name: str) -> str:
    """
    Generate a deterministic hash from deliverable content for dedup.
    Uses title + first 2000 chars of content + agent_name.
    """
    normalized = f"{title.strip().lower()}|{(content or '')[:2000].strip()}|{agent_name.strip().lower()}"
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:32]


def create_deliverable(
    title: str,
    content: str,
    agent_name: str,
    category: str = 'General',
    deliverable_type: str = 'document',
    user=None,
    workspace_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    parent_execution_id: Optional[str] = None,
    parent_object_type: str = '',
    tags: Optional[List[str]] = None,
    content_format: str = 'markdown',
    quality_score: float = 0.0,
    confidence_score: float = 0.0,
    is_saved: bool = False,
    is_pinned: bool = False,
    agent_task: str = '',
    metadata: Optional[dict] = None,
    initiative_id: Optional[str] = None,
    dream_id: Optional[str] = None,
    source_operation_id: Optional[str] = None,
    # Pass-through for any additional model fields
    **extra_fields,
) -> Any:
    """
    Create a Deliverable with consistent metadata and workspace assignment.

    This is the ONLY function that should create Deliverables going forward.
    All 23+ existing creation paths should migrate to this factory.

    Returns the created Deliverable instance.
    """
    from core.models_deliverables import Deliverable

    # --- Provenance dedupe guard ---
    # If a parent_execution_id is provided, check for existing deliverable
    # from the same execution to prevent duplicates from retries/replays.
    if parent_execution_id:
        existing = Deliverable.objects.filter(
            parent_object_type=parent_object_type or 'agent_execution',
            parent_object_id=parent_execution_id,
        ).first()
        if existing:
            logger.info(
                f"[DeliverableFactory] Dedupe: returning existing {existing.id} "
                f"for execution {parent_execution_id}"
            )
            # Update content if newer (idempotent upsert)
            if content and content != existing.content:
                existing.content = content
                existing.preview_content = content[:500]
                existing.quality_score = quality_score or existing.quality_score
                existing.confidence_score = confidence_score or existing.confidence_score
                existing.save(update_fields=[
                    'content', 'preview_content', 'quality_score',
                    'confidence_score', 'updated_at',
                ])
                logger.info(f"[DeliverableFactory] Updated content for {existing.id}")
            return existing

    # --- Title-based dedupe (4h window) ---
    # Same agent + same title within 4 hours = update instead of duplicate
    from django.utils import timezone as tz
    from datetime import timedelta
    dedup_window = tz.now() - timedelta(hours=4)
    title_existing = Deliverable.objects.filter(
        title=title[:500],
        agent_name=agent_name,
        created_at__gte=dedup_window,
    ).order_by('-created_at').first()
    if title_existing:
        title_existing.content = content or title_existing.content
        title_existing.preview_content = (content[:500] if content else '')
        title_existing.quality_score = quality_score or title_existing.quality_score
        title_existing.confidence_score = confidence_score or title_existing.confidence_score
        title_existing.metadata = metadata or title_existing.metadata
        title_existing.save(update_fields=[
            'content', 'preview_content', 'quality_score',
            'confidence_score', 'metadata', 'updated_at',
        ])
        logger.info(
            f"[DeliverableFactory] Title dedupe: updated {title_existing.id} "
            f"'{title[:60]}' by {agent_name}"
        )
        return title_existing

    # --- Content-hash dedupe (72h window) ---
    # Catches duplicates that slip past title-based dedupe (e.g., recurring
    # scheduled tasks producing identical content across runs > 4h apart).
    if content and len(content) > 50:  # Skip trivially short content
        c_hash = _content_hash(title, content, agent_name)
        hash_window = tz.now() - timedelta(hours=72)
        hash_existing = Deliverable.objects.filter(
            content_hash=c_hash,
            created_at__gte=hash_window,
        ).order_by('-created_at').first()
        if hash_existing:
            logger.info(
                f"[DeliverableFactory] Content-hash dedupe: returning existing "
                f"{hash_existing.id} '{title[:60]}' (hash={c_hash[:12]})"
            )
            return hash_existing

    # Auto-assign user if not provided (agent/Celery context)
    if not user:
        user = _get_default_user()

    # Auto-assign workspace if not provided — filters by allow_autonomous_writes
    # so autonomous/scheduled agents never silently inherit a personal/game
    # workspace just because the user marked it is_active in the UI.
    explicit_workspace = bool(workspace_id)
    if not workspace_id and user:
        workspace_id = _get_active_workspace_id(user)

    if not explicit_workspace and not workspace_id:
        logger.warning(
            "[DeliverableFactory] No eligible autonomous workspace for "
            "agent=%s title=%r — deliverable will be created without "
            "workspace. Caller should pass workspace_id explicitly.",
            agent_name, title[:80],
        )

    # Build preview
    preview = content[:500] if content else ''

    # Auto-generate slug if not provided
    if 'slug' not in extra_fields:
        from django.utils.text import slugify
        import uuid as _uuid
        base_slug = slugify(title[:100]) if title else 'untitled'
        extra_fields['slug'] = f"{base_slug}-{_uuid.uuid4().hex[:8]}"

    # Build creation kwargs
    kwargs = {
        'title': title[:500],  # Enforce max length
        'content': content,
        'agent_name': agent_name,
        'category': category,
        'deliverable_type': deliverable_type,
        'content_format': content_format,
        'preview_content': preview,
        'quality_score': quality_score,
        'confidence_score': confidence_score,
        'is_saved': is_saved,
        'is_pinned': is_pinned,
        'agent_task': agent_task,
        'tags': tags or [],
        'metadata': metadata or {},
    }

    # Optional foreign keys
    if user:
        kwargs['user'] = user
    if workspace_id:
        kwargs['workspace_id'] = workspace_id
    if trace_id:
        # Apr 2026: trace_id is a UUIDField on Deliverable but tool_dispatcher
        # generates non-UUID trace IDs like "tool-1-6a55c355". Validate before passing.
        import uuid as _uuid_mod
        try:
            _uuid_mod.UUID(trace_id)
            kwargs['trace_id'] = trace_id
        except (ValueError, AttributeError):
            pass  # Skip non-UUID trace IDs
    if parent_execution_id:
        kwargs['parent_object_type'] = parent_object_type or 'agent_execution'
        kwargs['parent_object_id'] = parent_execution_id
    if initiative_id:
        kwargs['initiative_id'] = initiative_id
    if dream_id:
        kwargs['dream_id'] = dream_id
    if source_operation_id:
        kwargs['source_operation_id'] = source_operation_id

    # Content hash for dedup (stored on model for future lookups)
    if content and len(content) > 50:
        kwargs['content_hash'] = _content_hash(title, content, agent_name)

    # Merge any extra fields (for backward compat with existing callers)
    kwargs.update(extra_fields)

    try:
        deliverable = Deliverable.objects.create(**kwargs)
        logger.info(
            f"[DeliverableFactory] Created: {deliverable.id} "
            f"'{title[:60]}' by {agent_name} "
            f"(workspace={workspace_id or 'none'}, user={getattr(user, 'id', 'none')})"
        )
        return deliverable
    except Exception as e:
        logger.error(
            f"[DeliverableFactory] Failed to create deliverable: {e} "
            f"(title='{title[:60]}', agent={agent_name})"
        )
        raise


def _get_default_user():
    """Get the default user for agent/Celery-created deliverables (first superuser)."""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.filter(is_superuser=True).order_by('date_joined').first()
    except Exception:
        return None


def _get_active_workspace_id(user) -> Optional[str]:
    """Get the user's active workspace ID for autonomous fallback writes.

    Only returns workspaces flagged ``allow_autonomous_writes=True`` so
    personal/game/tool workspaces (Ironwood, MentorForge, etc.) can't
    accidentally receive scheduled agent output when they happen to be
    the user's currently-active workspace. Returns None if no eligible
    workspace exists — callers must handle the None case explicitly
    rather than silently landing deliverables somewhere wrong.
    """
    try:
        from core.models_skin_layer import ProjectWorkspace
        ws = ProjectWorkspace.objects.filter(
            user=user, is_active=True, allow_autonomous_writes=True,
        ).values_list('id', flat=True).first()
        if ws:
            return str(ws)
        # Secondary fallback: any content-safe workspace owned by user
        ws = ProjectWorkspace.objects.filter(
            user=user, allow_autonomous_writes=True,
        ).values_list('id', flat=True).first()
        return str(ws) if ws else None
    except Exception:
        return None
