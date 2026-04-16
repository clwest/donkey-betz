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


# ── Session 1088: Quality gate — prevent noise deliverables ───────────

# Minimum content length for a deliverable to be worth persisting.
# Media agents (image/video/audio) produce short stubs like "Generated 1 image(s)"
# — those aren't useful deliverables. Smoke tests produce <200 char outputs.
MIN_CONTENT_LENGTH = 300

# Patterns that indicate the deliverable is a smoke test or diagnostic,
# not real user-requested work. Checked against lowercased title.
SMOKE_TEST_PATTERNS = [
    'smoke test', 'smoke-test', 'sanity check', 'heartbeat',
    'factory smoke', 'round 40', 'round 45', 'round 51',
    'pr1887', 'pr #1887', 'pr1893', 'one sentence status',
    'local ops smoke', 'dual-path test', 'direct router test',
    'ping test', 'verification —',
]

# Media stub agents — their "deliverables" are just "Generated 1 image(s)"
# stubs. The actual media is stored elsewhere (Cloudinary, etc.).
MEDIA_STUB_AGENTS = {'ImageAgent', 'VideoAgent', 'AudioAgent', 'ThreeDAgent'}


def _should_create_deliverable(
    title: str,
    content: str,
    agent_name: str,
    metadata: Optional[dict] = None,
) -> tuple[bool, str]:
    """
    Quality gate: decide whether this deliverable is worth persisting.

    Returns (should_create, reason). If should_create is False, the
    factory logs the skip and returns None.
    """
    content_len = len(content or '')
    title_lower = (title or '').lower()

    # Gate 1: Media stubs — tiny content from media agents
    if agent_name in MEDIA_STUB_AGENTS and content_len < MIN_CONTENT_LENGTH:
        return False, f"media stub ({content_len} chars from {agent_name})"

    # Gate 2: Smoke tests — diagnostic titles that shouldn't persist
    if any(pattern in title_lower for pattern in SMOKE_TEST_PATTERNS):
        return False, f"smoke test pattern in title"

    # Gate 3: Minimum content length (skip for user-triggered work)
    trigger = (metadata or {}).get('trigger_source', '')
    if trigger not in ('user_request', 'pa_tool', 'user_chat', 'direct'):
        if content_len < MIN_CONTENT_LENGTH:
            return False, f"below minimum content length ({content_len} < {MIN_CONTENT_LENGTH})"

    return True, "passed"


# ── Session 1088: BLOCKED content detection ───────────────────────────

def _detect_blocked_content(content: str) -> Optional[str]:
    """
    Detect if agent output contains BLOCKED warnings indicating
    incomplete work due to missing evidence/data.

    Returns the blocked reason string if found, None if content is clean.
    """
    import re
    if not content:
        return None

    # Match patterns like "BLOCKED ON: missing domain evidence"
    # or "**BLOCKED ON: missing source URL**"
    match = re.search(
        r'BLOCKED\s*(?:ON)?[:\s]*([^\n\*]{10,150})',
        content,
        re.IGNORECASE,
    )
    if match:
        return match.group(1).strip()

    return None


def _clean_deliverable_title(title: str, agent_name: str, content: str) -> str:
    """
    Generate a human-readable title from raw prompt text.

    The problem: deliverable titles are often the raw task prompt, e.g.
    "Research: Summarize this insight into 3 concrete next-steps (one
    sentence each). Do NOT do web research or too..."

    This function extracts a meaningful title from the content or
    cleans up the prompt-based title.
    """
    if not title:
        return f"{agent_name} Output"

    # Strip common agent prefixes that get prepended
    prefixes_to_strip = [
        'Research: ', 'Trend Analysis: ', 'Thinking Analysis: ',
        'Competitor Analysis: ', 'Contrarian Analysis: ',
        'Creative Direction: ', 'CTO Analysis: ', 'COO Analysis: ',
        'Brand Strategy: ', 'Performance Analysis: ',
        'Market Intelligence: ', 'System Intelligence Report: ',
        'Topic Mining: ', 'blog_post: ',
    ]
    clean = title
    for prefix in prefixes_to_strip:
        if clean.startswith(prefix):
            clean = clean[len(prefix):]
            break

    # If the title looks like a raw prompt (contains instruction words),
    # try to extract the actual topic
    prompt_indicators = [
        'summarize this', 'do not do web', 'do not do research',
        'use the run_agent tool', 'one sentence each',
        'provide a', 'identify the', 'analyze the',
        'as a participant in a strategic meeting about',
        'challenge assumptions and suggest',
        'find trending topics and opportunities in',
    ]
    is_prompt = any(ind in clean.lower() for ind in prompt_indicators)

    if is_prompt:
        # Try to extract topic from "Insight: X" pattern in the title
        import re
        insight_match = re.search(r'Insight:\s*(.{10,80}?)(?:\n|Detail:|$)', title)
        if insight_match:
            return f"{agent_name}: {insight_match.group(1).strip()}"

        # Try to extract from "about X" pattern
        about_match = re.search(r'about\s+"?(.{10,80}?)"?\s*(?:\n|$)', clean)
        if about_match:
            return f"{agent_name}: {about_match.group(1).strip()}"

        # Try first heading from content
        if content:
            heading_match = re.search(r'^##?\s+(.{10,80})$', content, re.MULTILINE)
            if heading_match:
                heading = heading_match.group(1).strip()
                if 'executive summary' not in heading.lower():
                    return f"{agent_name}: {heading}"

        # Truncate the prompt to something reasonable
        if len(clean) > 80:
            clean = clean[:77] + '...'
        return f"{agent_name}: {clean}"

    # Title is already reasonable — just ensure it's not too long
    if len(title) > 120:
        return title[:117] + '...'

    return title


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

    # --- Session 1088: Quality gate — reject noise before any DB work ---
    should_create, gate_reason = _should_create_deliverable(
        title=title, content=content, agent_name=agent_name, metadata=metadata,
    )
    if not should_create:
        logger.info(
            "[DeliverableFactory] GATE REJECT: %s — %s (title=%s)",
            agent_name, gate_reason, title[:60],
        )
        return None

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

    # --- Session 1088: Auto-tag trigger_source in metadata ---
    metadata = metadata or {}
    if 'trigger_source' not in metadata:
        # Infer trigger_source from available context
        task_lower = (agent_task or '').lower()
        if any(p in task_lower for p in SMOKE_TEST_PATTERNS):
            metadata['trigger_source'] = 'smoke_test'
        elif agent_name == 'PersonalAssistant':
            metadata['trigger_source'] = 'user_request'
        elif parent_execution_id:
            metadata['trigger_source'] = 'agent_execution'
        else:
            metadata['trigger_source'] = 'beat_task'

    # --- Session 1088: BLOCKED content detection ---
    blocked_reason = _detect_blocked_content(content)
    if blocked_reason:
        status = 'blocked'
        metadata['blocked_reason'] = blocked_reason
        logger.info(
            "[DeliverableFactory] BLOCKED content detected for %s: %s (title=%s)",
            agent_name, blocked_reason[:80], title[:60],
        )
    # else status comes from the caller (default 'ready')

    # --- Session 1088: Clean up prompt-as-title ---
    title = _clean_deliverable_title(title, agent_name, content)

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

    # Session 1088: Override status if content is BLOCKED
    if blocked_reason:
        kwargs['status'] = 'blocked'

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
    except Exception as _e:
        logger.warning(
            "deliverable_factory._get_default_user: swallowed (%s: %s) — returning default",
            type(_e).__name__, _e,
        )
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
    except Exception as _e:
        logger.warning(
            "deliverable_factory._get_active_workspace_id: swallowed (%s: %s) — returning default",
            type(_e).__name__, _e,
        )
        return None
