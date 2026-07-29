"""
Decision Promotion Rules Service
Session 589: Address Pending Review backlog (DRAFT decisions awaiting action)

This service implements governance-respecting auto-promotion rules
to help manage the backlog of agent-generated suggestions.

ChatGPT's Strategic Guidance:
- Don't rush autonomous execution (needs guardrails)
- Governance-first posture is correct
- System is in "trust-critical phase"

Tiered Promotion System:
- Tier 1 (Auto-Promote): Low-risk guidelines after 24h aging
- Tier 2 (Review Required): Medium-risk decisions need human review
- Tier 3 (Never Auto): High-risk decisions (security, architecture) always manual

The goal is NOT to automate everything, but to:
1. Clear the backlog of obvious, low-risk guidelines
2. Make the pending review backlog visible to operators
3. Respect the human-in-the-loop governance model
"""

import logging
from datetime import timedelta
from typing import Dict, List, Tuple, Optional, Any
from django.utils import timezone
from django.db.models import Count, Q

logger = logging.getLogger(__name__)


# ============================================================
# PROMOTION TIERS - Governance-respecting classification
# ============================================================

# Tier 1: Auto-promotable after aging period
# These are low-risk decisions that don't require human review
AUTO_PROMOTE_ELIGIBLE = {
    # decision_type: {allowed_impact_areas}
    'guideline': {
        'prompting',      # Prompt engineering best practices
        'product',        # UX improvements
        'workflow',       # Workflow optimizations
    },
}

# Tier 2: Require human review (never auto-promote)
# These decisions have broader system impact
REQUIRE_REVIEW = {
    'architecture',   # Structural changes
    'pipeline',       # Data flow changes
    'policy',         # Binding rules
}

# Tier 3: Never auto-promote (high-risk impact areas)
# These impact areas always require human judgment
NEVER_AUTO_AREAS = {
    'security',       # Security decisions always manual
    'infrastructure', # Infrastructure changes always manual
    'agents',         # Agent behavior changes always manual
}

# Minimum age before auto-promotion (hours)
MIN_AGING_HOURS = 24

# Maximum decisions to auto-promote per run (prevent runaway)
MAX_AUTO_PROMOTE_PER_RUN = 10


class DecisionPromotionRules:
    """
    Governance-respecting decision promotion rules.

    Implements tiered auto-promotion to address the execution gap
    while respecting human oversight for high-risk decisions.
    """

    def __init__(self):
        self.stats = {
            'eligible': 0,
            'promoted': 0,
            'skipped_too_new': 0,
            'skipped_high_risk': 0,
            'skipped_review_required': 0,
        }

    def can_auto_promote(self, decision) -> Tuple[bool, str]:
        """
        Check if a decision is eligible for auto-promotion.

        Args:
            decision: AgentDecisionSummary instance

        Returns:
            Tuple of (can_promote, reason)
        """
        # Already promoted or rejected
        if decision.status in ('canonical', 'rejected', 'superseded'):
            return False, f"Already in status: {decision.status}"

        # Check Tier 3: Never auto-promote high-risk areas
        if decision.impact_area in NEVER_AUTO_AREAS:
            return False, f"High-risk impact area: {decision.impact_area}"

        # Check Tier 2: Require review for certain types
        if decision.decision_type in REQUIRE_REVIEW:
            return False, f"Decision type requires review: {decision.decision_type}"

        # Check Tier 1: Auto-promotable types
        if decision.decision_type not in AUTO_PROMOTE_ELIGIBLE:
            return False, f"Decision type not eligible: {decision.decision_type}"

        # Check if impact area is allowed for this type
        allowed_areas = AUTO_PROMOTE_ELIGIBLE.get(decision.decision_type, set())
        if decision.impact_area not in allowed_areas:
            return False, f"Impact area {decision.impact_area} not eligible for {decision.decision_type}"

        # Check aging requirement
        age_hours = (timezone.now() - decision.created_at).total_seconds() / 3600
        if age_hours < MIN_AGING_HOURS:
            return False, f"Too new: {age_hours:.1f}h < {MIN_AGING_HOURS}h minimum"

        # Passed all checks
        return True, "Eligible for auto-promotion"

    def get_promotable_decisions(self) -> List:
        """
        Get all decisions eligible for auto-promotion.

        Returns:
            List of AgentDecisionSummary instances that can be auto-promoted
        """
        from core.models_unified_system import AgentDecisionSummary

        # Age cutoff
        cutoff = timezone.now() - timedelta(hours=MIN_AGING_HOURS)

        # Get draft decisions older than cutoff
        candidates = AgentDecisionSummary.objects.filter(
            status='draft',
            created_at__lte=cutoff
        ).order_by('created_at')[:100]  # Limit candidates for performance

        promotable = []
        for decision in candidates:
            can_promote, reason = self.can_auto_promote(decision)
            if can_promote:
                promotable.append(decision)
                self.stats['eligible'] += 1
                if len(promotable) >= MAX_AUTO_PROMOTE_PER_RUN:
                    break
            else:
                # Track why not promotable
                if 'too new' in reason.lower():
                    self.stats['skipped_too_new'] += 1
                elif 'high-risk' in reason.lower():
                    self.stats['skipped_high_risk'] += 1
                elif 'requires review' in reason.lower():
                    self.stats['skipped_review_required'] += 1

        return promotable

    def promote_decision(self, decision, promoted_by: str = 'auto-promotion-rules') -> bool:
        """
        Promote a decision to canonical status.

        Args:
            decision: AgentDecisionSummary instance
            promoted_by: Who/what triggered the promotion

        Returns:
            True if successful

        S3028: after the field mutation commits, emit the canonical-
        promotion Redis broadcast so the Session 589 rules path fires
        the same event the boardroom endpoints + AI-AutoPromoter fire.
        Broadcast is best-effort and never fails promotion.

        S3029 (Fold A convergence): delegates the field mutation to the
        `AgentDecisionSummary.promote_to_canonical` model method.
        Intentionally NO `transaction.atomic()` wrapper here — this
        service is legacy Session 589 best-effort semantics; the AI
        service wraps because its own contract calls for it. Don't
        harmonize without explicit evidence-backed decision.
        """
        try:
            # S3031: gate broadcast on did_promote — if a competing path
            # already canonicalized this row, skip the duplicate broadcast.
            did_promote = decision.promote_to_canonical(promoted_by=promoted_by)
            if did_promote:
                self.stats['promoted'] += 1
                logger.info(f"Auto-promoted decision: {decision.topic[:50]}... -> canonical")
        except Exception as e:
            logger.error(f"Failed to promote decision {decision.id}: {e}")
            return False

        if did_promote:
            from core.services.canonical_decision_broadcast import (
                ACTOR_RULES_SERVICE,
                emit_canonical_promotion_broadcast,
            )
            emit_canonical_promotion_broadcast(decision, actor=ACTOR_RULES_SERVICE)
        return True

    def run_auto_promotion(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Run the auto-promotion process.

        Args:
            dry_run: If True, don't actually promote, just report what would happen

        Returns:
            Dict with promotion results and stats
        """
        logger.info(f"Starting auto-promotion run (dry_run={dry_run})")

        promotable = self.get_promotable_decisions()

        if not dry_run:
            for decision in promotable:
                self.promote_decision(decision)

        result = {
            'dry_run': dry_run,
            'eligible': len(promotable),
            'promoted': self.stats['promoted'] if not dry_run else 0,
            'would_promote': len(promotable) if dry_run else None,
            'decisions': [
                {
                    'id': str(d.id),
                    'topic': d.topic[:80],
                    'type': d.decision_type,
                    'area': d.impact_area,
                    'age_hours': round((timezone.now() - d.created_at).total_seconds() / 3600, 1),
                }
                for d in promotable
            ],
            'stats': self.stats,
        }

        logger.info(f"Auto-promotion complete: {result['promoted'] or result['would_promote']} decisions")
        return result

    def get_pending_review_metrics(self) -> Dict[str, Any]:
        """
        Get metrics showing the current pending review backlog.

        This makes the backlog visible to operators so they can
        prioritize manual review of high-impact decisions.

        Returns:
            Dict with pending review analysis metrics
        """
        from core.models_unified_system import AgentDecisionSummary

        # Total decisions by status
        by_status = dict(
            AgentDecisionSummary.objects.values('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )

        total = sum(by_status.values())
        draft_count = by_status.get('draft', 0)
        canonical_count = by_status.get('canonical', 0)
        rejected_count = by_status.get('rejected', 0)

        # Age distribution of drafts
        now = timezone.now()
        age_buckets = {
            'under_24h': 0,
            '1_to_7_days': 0,
            '7_to_30_days': 0,
            'over_30_days': 0,
        }

        drafts = AgentDecisionSummary.objects.filter(status='draft')
        for d in drafts:
            age = now - d.created_at
            if age < timedelta(hours=24):
                age_buckets['under_24h'] += 1
            elif age < timedelta(days=7):
                age_buckets['1_to_7_days'] += 1
            elif age < timedelta(days=30):
                age_buckets['7_to_30_days'] += 1
            else:
                age_buckets['over_30_days'] += 1

        # Eligible for auto-promotion
        promotable = self.get_promotable_decisions()

        # Breakdown by type/area
        by_type = dict(
            AgentDecisionSummary.objects.filter(status='draft')
            .values('decision_type')
            .annotate(count=Count('id'))
            .values_list('decision_type', 'count')
        )

        by_area = dict(
            AgentDecisionSummary.objects.filter(status='draft')
            .values('impact_area')
            .annotate(count=Count('id'))
            .values_list('impact_area', 'count')
        )

        pending_percentage = (draft_count / total * 100) if total > 0 else 0

        return {
            'total_decisions': total,
            'by_status': by_status,
            'pending_review': {
                'draft_count': draft_count,
                'draft_percentage': round(pending_percentage, 1),
                'canonical_count': canonical_count,
                'rejected_count': rejected_count,
            },
            'age_distribution': age_buckets,
            'auto_promotable': {
                'count': len(promotable),
                'percentage_of_drafts': round(len(promotable) / draft_count * 100, 1) if draft_count > 0 else 0,
            },
            'by_decision_type': by_type,
            'by_impact_area': by_area,
            'recommendation': self._generate_recommendation(pending_percentage, age_buckets, by_type),
        }

    def _generate_recommendation(
        self,
        pending_percentage: float,
        age_buckets: Dict[str, int],
        by_type: Dict[str, int]
    ) -> str:
        """Generate a human-readable recommendation based on the pending review analysis."""

        if pending_percentage < 50:
            return "Review backlog is healthy. Continue manual review cadence."

        stale_count = age_buckets.get('over_30_days', 0) + age_buckets.get('7_to_30_days', 0)
        if stale_count > 50:
            return f"Note: {stale_count} suggestions over 7 days old. Consider archiving or batch review."

        guideline_count = by_type.get('guideline', 0)
        if guideline_count > 30:
            return f"Many guidelines pending ({guideline_count}). Enable auto-promotion for low-risk guidelines."

        return f"Pending review at {pending_percentage:.0f}%. This is normal for AI systems generating many suggestions."


# Singleton instance
_rules_instance: Optional[DecisionPromotionRules] = None


def get_promotion_rules() -> DecisionPromotionRules:
    """Get singleton promotion rules instance."""
    global _rules_instance
    if _rules_instance is None:
        _rules_instance = DecisionPromotionRules()
    return _rules_instance


def run_auto_promotion(dry_run: bool = False) -> Dict[str, Any]:
    """Convenience function to run auto-promotion."""
    rules = DecisionPromotionRules()  # Fresh instance for clean stats
    return rules.run_auto_promotion(dry_run=dry_run)


def get_pending_review_metrics() -> Dict[str, Any]:
    """Convenience function to get pending review metrics."""
    rules = DecisionPromotionRules()
    return rules.get_pending_review_metrics()
