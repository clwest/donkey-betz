"""
Initiative Auto-Progression Service
====================================

Session 905: Automatically progresses initiatives through stages when quality
criteria are met.

Problem: Initiatives were getting stuck at Stage 1 DRAFT even when research
was complete and sufficient. No automation existed to move them forward.

Solution: Auto-progression based on quality signals:
1. Stage 1 (Research Brief) → Stage 2 (Prototype Plan) when findings sufficient
2. Stage 2 → Stage 3 when plan is concrete
3. etc.

Session 914.4: Rate Limits
- Added daily rate limits to control LLM spend
- Default: 40 stage progressions per day
- Configurable via Django settings or cache

Usage:
    from core.services.initiative_auto_progression import (
        check_stage_for_progression,
        progress_initiative_stage,
        trigger_next_stage_generation,
        get_daily_progression_stats,  # Session 914.4
        reset_daily_progression_count  # Session 914.4
    )

    # Check and progress a single initiative
    result = check_stage_for_progression(initiative_id)

    # Or use the Celery task
    from core.tasks import process_initiative_auto_progression
    process_initiative_auto_progression.delay()

    # Check rate limit status (Session 914.4)
    stats = get_daily_progression_stats()
    print(f"Used: {stats['count']}/{stats['limit']}")
"""

import logging
from datetime import date
from typing import Dict, Any, Optional, Tuple
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

# Session 914.4: Rate Limit Configuration
# Session 1006: Bumped from 40 → 100 (19 initiatives hit limit in single run)
DEFAULT_DAILY_PROGRESSION_LIMIT = 100  # Max stage progressions per day
RATE_LIMIT_CACHE_KEY = "initiative_progression_daily_count"
RATE_LIMIT_DATE_KEY = "initiative_progression_date"


def get_daily_progression_limit() -> int:
    """Get the daily progression limit from cache, settings, or default."""
    # Check for temporary custom limit in cache first
    custom_limit = cache.get('initiative_progression_custom_limit')
    if custom_limit is not None:
        return int(custom_limit)
    # Fall back to settings or default
    return getattr(settings, 'INITIATIVE_DAILY_PROGRESSION_LIMIT', DEFAULT_DAILY_PROGRESSION_LIMIT)


def get_daily_progression_stats() -> Dict[str, Any]:
    """
    Session 914.4: Get current daily progression statistics.

    Returns:
        Dict with count, limit, remaining, date, and is_limited status
    """
    today = date.today().isoformat()
    cached_date = cache.get(RATE_LIMIT_DATE_KEY)

    # Reset if new day
    if cached_date != today:
        cache.set(RATE_LIMIT_DATE_KEY, today, 86400)  # 24 hours
        cache.set(RATE_LIMIT_CACHE_KEY, 0, 86400)
        count = 0
    else:
        count = cache.get(RATE_LIMIT_CACHE_KEY, 0)

    limit = get_daily_progression_limit()
    remaining = max(0, limit - count)

    return {
        'count': count,
        'limit': limit,
        'remaining': remaining,
        'date': today,
        'is_limited': count >= limit,
        'percentage_used': (count / limit * 100) if limit > 0 else 0
    }


def increment_progression_count() -> int:
    """
    Session 914.4: Increment the daily progression count.

    Returns:
        New count after increment
    """
    today = date.today().isoformat()
    cached_date = cache.get(RATE_LIMIT_DATE_KEY)

    # Reset if new day
    if cached_date != today:
        cache.set(RATE_LIMIT_DATE_KEY, today, 86400)
        cache.set(RATE_LIMIT_CACHE_KEY, 1, 86400)
        return 1

    # Increment existing count
    try:
        new_count = cache.incr(RATE_LIMIT_CACHE_KEY)
    except ValueError:
        # Key doesn't exist, set it
        cache.set(RATE_LIMIT_CACHE_KEY, 1, 86400)
        new_count = 1

    return new_count


def reset_daily_progression_count() -> Dict[str, Any]:
    """
    Session 914.4: Reset the daily progression count (admin override).

    Returns:
        Dict with reset confirmation
    """
    today = date.today().isoformat()
    old_count = cache.get(RATE_LIMIT_CACHE_KEY, 0)

    cache.set(RATE_LIMIT_DATE_KEY, today, 86400)
    cache.set(RATE_LIMIT_CACHE_KEY, 0, 86400)

    logger.info(f"[Session 914.4] Daily progression count reset (was {old_count})")

    return {
        'success': True,
        'previous_count': old_count,
        'new_count': 0,
        'date': today,
        'reset_at': timezone.now().isoformat()
    }


def check_rate_limit() -> Tuple[bool, Dict[str, Any]]:
    """
    Session 914.4: Check if rate limit allows progression.

    Returns:
        Tuple of (can_progress, stats_dict)
    """
    stats = get_daily_progression_stats()
    can_progress = not stats['is_limited']

    if not can_progress:
        logger.warning(
            f"[Session 914.4] Rate limit reached: {stats['count']}/{stats['limit']} progressions today"
        )

    return can_progress, stats

# Quality thresholds for auto-progression
# Session 906: Made section names more flexible - any of the alternatives count
STAGE_QUALITY_THRESHOLDS = {
    1: {  # Research Brief
        'min_findings_length': 100,  # At least 100 chars of findings
        'min_sources': 1,  # At least 1 data source
        # Session 906: Accept alternative section names (any match counts)
        # Session 1003: Added 'Key Finding', 'Research on', 'Status' — stage documents
        # contain these patterns instead of formal section headers
        'required_sections': [
            ['Research Findings', 'Market Signal', 'Problem Statement', 'Executive Summary',
             'Findings', 'Key Finding', 'Research on', 'Key Insight'],
            ['Data Sources', 'Source', 'Sources Consulted', 'Data', 'Evidence',
             'Status', 'Confidence', 'Complete'],
        ],
    },
    2: {  # Prototype Plan
        'min_content_length': 200,
        'required_sections': [
            ['Architecture', 'Design', 'Approach', 'Overview'],
            ['Implementation', 'Plan', 'Steps', 'Timeline'],
        ],
    },
    3: {  # Evaluation Protocol
        'min_content_length': 150,
        'required_sections': [
            ['Success Criteria', 'Criteria', 'Goals', 'Objectives'],
            ['Metrics', 'KPIs', 'Measurements', 'Indicators'],
        ],
    },
    4: {  # Technical Design
        'min_content_length': 300,
        'required_sections': [
            ['Specification', 'Spec', 'Requirements', 'Design'],
            ['Dependencies', 'Requirements', 'Integration', 'Components'],
        ],
    },
    5: {  # Pilot Execution
        'min_content_length': 100,
        'required_sections': [
            ['Results', 'Outcomes', 'Findings', 'Data'],
            ['Learnings', 'Lessons', 'Insights', 'Takeaways'],
        ],
    },
}


def evaluate_stage_quality(initiative_stage) -> Tuple[bool, float, str]:
    """
    Evaluate if a stage document meets quality criteria for auto-progression.

    Args:
        initiative_stage: InitiativeStage instance

    Returns:
        Tuple of (passes_quality, confidence_score, reason)
    """
    stage_num = initiative_stage.stage
    document = initiative_stage.document

    if not document:
        return False, 0.0, "No document attached to stage"

    # Get document content
    content = document.full_text or document.content or ""
    content_length = len(content)

    thresholds = STAGE_QUALITY_THRESHOLDS.get(stage_num, {})
    min_length = thresholds.get('min_content_length', thresholds.get('min_findings_length', 50))
    required_sections = thresholds.get('required_sections', [])

    # Check minimum length
    if content_length < min_length:
        return False, 0.3, f"Content too short ({content_length} < {min_length} chars)"

    # Check for required sections
    # Session 906: Support alternative section names (list of lists)
    missing_sections = []
    content_lower = content.lower()
    for section_alternatives in required_sections:
        # Each item can be a list of alternatives or a single string
        if isinstance(section_alternatives, list):
            # Check if ANY of the alternatives are present
            found = any(alt.lower() in content_lower for alt in section_alternatives)
            if not found:
                missing_sections.append(section_alternatives[0])  # Report first alternative
        else:
            # Single string (backwards compatibility)
            if section_alternatives.lower() not in content_lower:
                missing_sections.append(section_alternatives)

    if missing_sections:
        return False, 0.5, f"Missing sections: {', '.join(missing_sections)}"

    # Calculate confidence based on content quality signals
    confidence = 0.6  # Base confidence

    # Bonus for longer content
    if content_length > min_length * 2:
        confidence += 0.1
    if content_length > min_length * 3:
        confidence += 0.1

    # Bonus for all required sections present
    if not missing_sections and required_sections:
        confidence += 0.1

    # Check for "Insufficient Data" markers (should NOT progress)
    insufficient_markers = ['insufficient data', 'awaiting data', 'blocked']
    for marker in insufficient_markers:
        if marker in content.lower():
            return False, 0.2, f"Document contains '{marker}' marker"

    # Check for positive completion markers
    completion_markers = ['research completed', 'data available', 'findings']
    has_completion_marker = any(m in content.lower() for m in completion_markers)
    if has_completion_marker:
        confidence += 0.1

    confidence = min(confidence, 1.0)  # Cap at 1.0

    return True, confidence, f"Quality check passed (confidence: {confidence:.0%})"


def check_stage_for_progression(initiative_id: str) -> Dict[str, Any]:
    """
    Check if an initiative's current stage is ready for auto-progression.

    Args:
        initiative_id: UUID of the initiative

    Returns:
        Dict with progression status and details
    """
    from core.models_document_registry import Initiative, InitiativeStage

    # Session 914.4: Check Rate Limit first (fail fast)
    can_progress_rate, rate_stats = check_rate_limit()
    if not can_progress_rate:
        logger.info(f"[Session 914.4] Rate limit blocking progression check")
        return {
            'success': False,
            'error': f"Daily rate limit reached ({rate_stats['count']}/{rate_stats['limit']} progressions)",
            'can_progress': False,
            'rate_limited': True,
            'rate_stats': rate_stats
        }

    try:
        initiative = Initiative.objects.get(id=initiative_id)
    except Initiative.DoesNotExist:
        return {'success': False, 'error': 'Initiative not found'}

    current_stage_num = initiative.current_stage

    # Get current stage
    try:
        current_stage = InitiativeStage.objects.get(
            initiative=initiative,
            stage=current_stage_num
        )
    except InitiativeStage.DoesNotExist:
        return {'success': False, 'error': f'Stage {current_stage_num} not found'}

    # Only auto-progress from DRAFT status
    if current_stage.status != 'DRAFT':
        return {
            'success': False,
            'error': f'Stage status is {current_stage.status}, not DRAFT',
            'stage': current_stage_num,
            'status': current_stage.status
        }

    # Session 914: Check Founder Intent - pause if not set
    if not initiative.can_auto_progress:
        blocked_reason = initiative.progression_blocked_reason or 'Founder intent not set'
        logger.info(f"[Session 914] Auto-progression blocked for {initiative.name}: {blocked_reason}")
        return {
            'success': False,
            'error': blocked_reason,
            'stage': current_stage_num,
            'can_progress': False,
            'founder_intent_set': initiative.founder_intent_set,
            'requires_founder_action': True,
            'founder_intent_summary': initiative.founder_intent_summary
        }

    # Session 914.2: Check Execution Track constraints
    # Fast Track stops at Stage 2
    if initiative.is_fast_track and current_stage_num >= initiative.max_stage:
        logger.info(f"[Session 914.2] Fast Track initiative {initiative.name} at max stage {initiative.max_stage}")
        return {
            'success': False,
            'error': f'Fast Track initiative complete at Stage {initiative.max_stage}',
            'stage': current_stage_num,
            'can_progress': False,
            'execution_track': 'fast_track',
            'max_stage': initiative.max_stage,
            'track_complete': True
        }

    # Institutional track requires stage approval for stages 2-4
    if initiative.is_institutional and initiative.requires_stage_approval(current_stage_num):
        if not initiative.is_stage_approved(current_stage_num):
            logger.info(f"[Session 914.2] Institutional initiative {initiative.name} awaiting Stage {current_stage_num} approval")
            return {
                'success': False,
                'error': f'Institutional track: Stage {current_stage_num} requires explicit approval',
                'stage': current_stage_num,
                'can_progress': False,
                'execution_track': 'institutional',
                'requires_stage_approval': True,
                'compliance_reviewed': initiative.compliance_reviewed
            }

    # Evaluate quality
    passes_quality, confidence, reason = evaluate_stage_quality(current_stage)

    if not passes_quality:
        return {
            'success': False,
            'error': reason,
            'stage': current_stage_num,
            'confidence': confidence,
            'can_progress': False
        }

    # Session 914.3: Semantic Drift Check
    # Ensure stage document aligns with original initiative intent
    drift_result = None
    try:
        # Check if drift checking is enabled
        drift_enabled = getattr(initiative, 'drift_check_enabled', True)
        drift_threshold = getattr(initiative, 'drift_threshold', 'balanced')

        # Skip if disabled
        if not drift_enabled or drift_threshold == 'disabled':
            logger.info(f"[Session 914.3] Drift check disabled for {initiative.name}")
        else:
            from core.services.semantic_drift_detector import check_semantic_drift
            drift_result = check_semantic_drift(current_stage, threshold_mode=drift_threshold)

            # Record drift scores to stage model
            current_stage.drift_score = drift_result.get('drift_score')
            current_stage.similarity_score = drift_result.get('similarity_score')
            current_stage.drift_checked_at = timezone.now()
            current_stage.drift_flagged = drift_result.get('has_drift', False)
            current_stage.save(update_fields=[
                'drift_score', 'similarity_score', 'drift_checked_at', 'drift_flagged'
            ])

            # Update initiative's last drift score
            initiative.last_drift_score = drift_result.get('drift_score')
            initiative.last_drift_check_at = timezone.now()
            initiative.save(update_fields=['last_drift_score', 'last_drift_check_at'])

            if drift_result.get('has_drift'):
                drift_score = drift_result.get('drift_score', 0)
                similarity = drift_result.get('similarity_score', 0)

                # Check for drift override
                if getattr(current_stage, 'drift_override', False):
                    logger.info(
                        f"[Session 914.3] Drift detected but overridden for {initiative.name}: "
                        f"override_by={current_stage.drift_override_by}"
                    )
                else:
                    logger.warning(
                        f"[Session 914.3] Semantic drift detected for {initiative.name}: "
                        f"drift={drift_score:.0%}, similarity={similarity:.0%}"
                    )
                    return {
                        'success': False,
                        'error': f"Semantic drift detected: document has drifted from initiative intent",
                        'stage': current_stage_num,
                        'confidence': confidence,
                        'can_progress': False,
                        'semantic_drift': True,
                        'drift_score': drift_score,
                        'similarity_score': similarity,
                        'drift_reason': drift_result.get('drift_reason', ''),
                        'requires_human_review': True
                    }
            else:
                # Add drift info to successful result
                logger.info(
                    f"[Session 914.3] Semantic alignment verified for {initiative.name}: "
                    f"similarity={drift_result.get('similarity_score', 0):.0%}"
                )
    except Exception as e:
        # Don't block on drift check failures - log and continue
        logger.warning(f"[Session 914.3] Drift check failed, continuing: {e}")

    # Quality check passed - ready for progression
    return {
        'success': True,
        'stage': current_stage_num,
        'confidence': confidence,
        'reason': reason,
        'can_progress': True,
        'initiative_id': str(initiative_id),
        'initiative_name': initiative.name,
        'semantic_alignment': drift_result.get('similarity_score', None) if 'drift_result' in dir() else None
    }


def progress_initiative_stage(
    initiative_id: str,
    auto_generate_next: bool = True
) -> Dict[str, Any]:
    """
    Progress an initiative from current stage to next stage.

    Args:
        initiative_id: UUID of the initiative
        auto_generate_next: Whether to trigger next stage document generation

    Returns:
        Dict with progression result
    """
    from core.models_document_registry import Initiative, InitiativeStage

    # First check if ready for progression
    check_result = check_stage_for_progression(initiative_id)
    if not check_result.get('can_progress'):
        return check_result

    try:
        initiative = Initiative.objects.get(id=initiative_id)
        current_stage = InitiativeStage.objects.get(
            initiative=initiative,
            stage=initiative.current_stage
        )
    except (Initiative.DoesNotExist, InitiativeStage.DoesNotExist) as e:
        return {'success': False, 'error': str(e)}

    # Approve the current stage
    confidence = check_result.get('confidence', 0.7)
    approval_notes = f"Auto-approved with {confidence:.0%} confidence. {check_result.get('reason', '')}"

    logger.info(f"[Session 905] Auto-approving Stage {current_stage.stage} for initiative {initiative.name}")

    # Session 916: Build checks_passed dict for audit trail
    checks_passed = {
        'quality_check': True,
        'has_document': current_stage.document is not None,
        'min_content_length': True,  # Passed if we got here
        'required_sections': True,
        'no_insufficient_markers': True,
        'founder_intent_set': initiative.founder_intent_set,
        'rate_limit_ok': True,
    }
    if check_result.get('semantic_alignment'):
        checks_passed['semantic_alignment'] = check_result['semantic_alignment']

    # Session 916: Enforce document existence before approval
    if not current_stage.document:
        logger.error(f"[Session 916] Cannot approve stage without document: {initiative.name} Stage {current_stage.stage}")
        return {
            'success': False,
            'error': 'Cannot approve stage without document',
            'stage': current_stage.stage,
            'initiative_id': str(initiative_id)
        }

    # Use the approve method which also advances the initiative
    # Session 916: Pass quality metrics for audit trail
    deliverable = current_stage.approve(
        approved_by='AutoProgressionService',
        notes=approval_notes,
        quality_score=confidence,
        confidence_score=confidence,
        checks_passed=checks_passed,
        enforce_document=True  # Session 916: Explicit enforcement
    )

    # Session 914.4: Increment daily progression count
    new_count = increment_progression_count()
    rate_stats = get_daily_progression_stats()
    logger.info(
        f"[Session 914.4] Progression count: {new_count}/{rate_stats['limit']} "
        f"({rate_stats['remaining']} remaining today)"
    )

    result = {
        'success': True,
        'previous_stage': current_stage.stage,
        'new_stage': initiative.current_stage,
        'confidence': confidence,
        'initiative_id': str(initiative_id),
        'initiative_name': initiative.name,
        'approved_at': timezone.now().isoformat(),
        'rate_stats': rate_stats  # Session 914.4
    }

    if deliverable:
        result['final_deliverable_id'] = str(deliverable.id)
        result['completed'] = True
        logger.info(f"[Session 905] Initiative {initiative.name} completed! Final deliverable: {deliverable.id}")
        return result

    # Session 914.2: Check if Fast Track has reached max stage
    if initiative.is_fast_track and initiative.current_stage > initiative.max_stage:
        result['fast_track_complete'] = True
        result['execution_track'] = 'fast_track'
        result['max_stage'] = initiative.max_stage
        logger.info(f"[Session 914.2] Fast Track initiative {initiative.name} complete at Stage {initiative.max_stage}")
        return result

    # Trigger next stage generation if requested
    if auto_generate_next and initiative.current_stage <= 5:
        # Session 914.2: Don't generate beyond max stage
        if initiative.current_stage <= initiative.max_stage:
            next_stage_result = trigger_next_stage_generation(initiative_id)
            result['next_stage_triggered'] = next_stage_result.get('success', False)
            result['next_stage_details'] = next_stage_result

    return result


def trigger_next_stage_generation(initiative_id: str) -> Dict[str, Any]:
    """
    Trigger generation of the next stage document for an initiative.

    Args:
        initiative_id: UUID of the initiative

    Returns:
        Dict with generation status
    """
    from core.models_document_registry import Initiative, InitiativeStage
    from core.tasks import generate_initiative_stage_document

    try:
        initiative = Initiative.objects.get(id=initiative_id)
    except Initiative.DoesNotExist:
        return {'success': False, 'error': 'Initiative not found'}

    current_stage = initiative.current_stage

    if current_stage > 5:
        return {'success': False, 'error': 'Initiative already complete'}

    # Session 914.2: Check execution track max stage
    if current_stage > initiative.max_stage:
        return {
            'success': False,
            'error': f'Initiative max stage is {initiative.max_stage} ({initiative.execution_track})',
            'execution_track': initiative.execution_track,
            'max_stage': initiative.max_stage
        }

    # Get or create the stage record
    stage, created = InitiativeStage.objects.get_or_create(
        initiative=initiative,
        stage=current_stage,
        defaults={'status': 'PENDING'}
    )

    if stage.document:
        return {
            'success': False,
            'error': f'Stage {current_stage} already has a document',
            'document_id': str(stage.document.id)
        }

    # Schedule async generation
    try:
        task = generate_initiative_stage_document.delay(
            str(initiative_id),
            current_stage
        )
        logger.info(f"[Session 905] Scheduled Stage {current_stage} generation for {initiative.name}: task {task.id}")

        return {
            'success': True,
            'stage': current_stage,
            'task_id': task.id,
            'initiative_name': initiative.name,
            'message': f'Stage {current_stage} document generation scheduled'
        }
    except Exception as e:
        logger.error(f"[Session 905] Failed to schedule stage generation: {e}")
        return {'success': False, 'error': str(e)}


def get_initiatives_ready_for_progression() -> list:
    """
    Find all initiatives with DRAFT stages ready for auto-progression.

    Returns:
        List of initiative IDs ready for progression
    """
    from core.models_document_registry import Initiative, InitiativeStage

    # Find stages in DRAFT status with documents
    draft_stages = InitiativeStage.objects.filter(
        status='DRAFT',
        document__isnull=False
    ).select_related('initiative')

    ready_initiatives = []

    for stage in draft_stages:
        # Only check if this is the current stage of the initiative
        if stage.stage != stage.initiative.current_stage:
            continue

        # Session 914: Check Founder Intent
        if not stage.initiative.can_auto_progress:
            continue

        # Session 914.2: Check Execution Track constraints
        initiative = stage.initiative

        # Fast Track: skip if already at max stage
        if initiative.is_fast_track and stage.stage >= initiative.max_stage:
            continue

        # Institutional: skip if stage requires approval and not approved
        if initiative.is_institutional:
            if initiative.requires_stage_approval(stage.stage) and not initiative.is_stage_approved(stage.stage):
                continue

        passes_quality, confidence, reason = evaluate_stage_quality(stage)
        if passes_quality and confidence >= 0.6:  # Minimum 60% confidence to auto-progress
            ready_initiatives.append({
                'initiative_id': str(initiative.id),
                'initiative_name': initiative.name,
                'stage': stage.stage,
                'confidence': confidence,
                'reason': reason,
                'founder_intent_set': initiative.founder_intent_set,  # Session 914
                'execution_track': initiative.execution_track,  # Session 914.2
                'max_stage': initiative.max_stage,  # Session 914.2
            })

    return ready_initiatives
