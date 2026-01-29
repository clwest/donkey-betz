"""
Core Django Signals
==================

Session 863: ConceptForge pipeline triggers
Session 822: Revenue tracking signals
Session 766: Dream execution signals

This module contains all Django signal handlers for the core app.
Signals are connected in apps.py via the _register_signals method.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


# =============================================================================
# CONCEPTFORGE SIGNALS (Session 863)
# =============================================================================

def connect_conceptforge_signals():
    """
    Connect ConceptForge pipeline signals.

    Call this from apps.py ready() method.
    """
    logger.info("🔮 Session 863: ConceptForge signals connected")


@receiver(post_save, sender='core.SelfBlog')
def handle_selfblog_save(sender, instance, created, **kwargs):
    """
    Handle SelfBlog save event.

    Triggers ConceptForge pipeline if:
    1. Blog is published (status = 'published')
    2. Quality score >= 0.80 (from stats_snapshot or calculated)
    3. Has strategic tags matching a domain lab

    Gate prevents "dossier spam" - only high-value content triggers the pipeline.
    """
    # Only trigger on publish (status change to 'published')
    if instance.status != 'published':
        return

    # Skip if this is a research_brief or audit (internal docs)
    if instance.category in ('research_brief', 'audit'):
        return

    # Check if ConceptForge already ran for this blog
    from core.models_conceptforge import ConceptForgeRun
    existing_run = ConceptForgeRun.objects.filter(
        source_type='blog',
        source_id=instance.id,
        status__in=['running', 'completed']
    ).exists()

    if existing_run:
        logger.debug(f"ConceptForge already ran for blog {instance.id}")
        return

    # Calculate quality score
    quality_score = _calculate_blog_quality_score(instance)

    # Check gate conditions
    from core.conceptforge import ConceptForgeOrchestrator
    orchestrator = ConceptForgeOrchestrator()

    tags = instance.tags if isinstance(instance.tags, list) else []
    should_trigger, reason, domain = orchestrator.should_trigger(
        quality_score=quality_score,
        tags=tags,
    )

    if not should_trigger:
        logger.debug(f"ConceptForge gate blocked blog {instance.id}: {reason}")
        return

    # Trigger pipeline via Celery task
    logger.info(
        f"🔮 ConceptForge triggered for blog '{instance.title[:50]}' "
        f"(domain={domain}, quality={quality_score:.2f})"
    )

    from core.tasks import run_conceptforge_pipeline
    run_conceptforge_pipeline.delay(
        source_type='blog',
        source_id=str(instance.id),
        source_title=instance.title,
        domain=domain,
        quality_score=quality_score,
        triggered_by='signal',
    )


def _calculate_blog_quality_score(blog) -> float:
    """
    Calculate a quality score for a blog post.

    Factors:
    - Word count (longer = better, up to a point)
    - Has sections (structured content)
    - Has tags (categorized)
    - Has meta description (SEO-ready)
    - Has intro and conclusion

    Returns float 0.0 - 1.0
    """
    score = 0.0
    max_score = 6.0

    # Word count (target: 500-2000 words)
    word_count = blog.word_count or 0
    if word_count >= 500:
        score += 1.0
    elif word_count >= 200:
        score += 0.5

    if word_count >= 1000:
        score += 0.5

    # Has structured sections
    sections = blog.sections or []
    if len(sections) >= 3:
        score += 1.0
    elif len(sections) >= 1:
        score += 0.5

    # Has tags
    tags = blog.tags or []
    if len(tags) >= 2:
        score += 1.0
    elif len(tags) >= 1:
        score += 0.5

    # Has meta description
    if blog.meta_description and len(blog.meta_description) > 50:
        score += 1.0

    # Has intro and conclusion
    if blog.intro and len(blog.intro) > 50:
        score += 0.5
    if blog.conclusion and len(blog.conclusion) > 50:
        score += 0.5

    return min(score / max_score, 1.0)


# =============================================================================
# DREAM EXECUTION SIGNALS (Session 766)
# =============================================================================

def connect_dream_signals():
    """
    Connect dream execution signals.

    Call this from apps.py ready() method.
    """
    logger.info("💭 Session 766: Dream execution signals connected")


@receiver(post_save, sender='core.AgentDream')
def handle_dream_approved(sender, instance, **kwargs):
    """
    Handle AgentDream approval.

    When a dream is approved (decision_outcome = 'approved'),
    trigger initiative creation and subsequent workflows.
    """
    if instance.decision_outcome != 'approved':
        return

    # Check if initiative already exists
    if hasattr(instance, 'initiative') and instance.initiative:
        return

    try:
        from core.services.initiative_integration_service import InitiativeIntegrationService
        service = InitiativeIntegrationService()
        service.create_initiative_from_dream(instance)
        logger.info(f"✅ Initiative created from approved dream: {instance.idea[:50]}")
    except Exception as e:
        logger.error(f"Failed to create initiative from dream: {e}")


# =============================================================================
# REVENUE TRACKING SIGNALS (Session 822)
# =============================================================================

def connect_revenue_signals():
    """
    Connect revenue tracking signals.

    Call this from apps.py ready() method.
    """
    logger.info("💰 Session 822: Revenue tracking signals connected")


# Revenue signals will be registered via decorators when models are imported
