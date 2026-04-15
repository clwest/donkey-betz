"""
Session 658: AI Decision Auto-Promoter Service

Uses GPT-5-mini (reasoning model) to evaluate and auto-promote
high-quality decisions to canonical status.

GPT-5-mini Configuration (Reasoning Model):
- Uses Responses API (not Chat Completions)
- max_output_tokens (NOT max_tokens) - give plenty for thinking!
- NO temperature parameter
- reasoning.effort: minimal/low/medium/high
- text.verbosity: low/medium/high
"""

import json
import logging
import re
from typing import Optional, Dict, Any, List
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from openai import OpenAI

from core.models_unified_system import AgentDecisionSummary
from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51

logger = logging.getLogger(__name__)


class AIDecisionPromoterService:
    """
    AI-powered decision promotion service using GPT-5-mini.

    Evaluates pending decisions and auto-promotes high-quality ones
    to canonical status based on AI assessment.
    """

    # Evaluation criteria for decisions
    EVALUATION_CRITERIA = """
1. Is it actionable and specific (not vague)?
2. Does it provide clear guidance?
3. Is it relevant to system operations, strategy, or development?
4. Does it contain concrete insights (not just platitudes)?
"""

    def __init__(self):
        self.client = get_openai_client()
        self.model = "gpt-5-mini"
        self.confidence_threshold = 0.7

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """
        Robust JSON parsing with multiple fallback strategies.

        Handles cases where GPT-5-mini includes explanation text
        around the JSON response.
        """
        # Strategy 1: Direct JSON parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Strategy 2: Find JSON object in text
        if '{' in text and '}' in text:
            try:
                json_start = text.index('{')
                json_end = text.rindex('}') + 1
                return json.loads(text[json_start:json_end])
            except (json.JSONDecodeError, ValueError):
                pass

        # Strategy 3: Regex extraction for key fields
        promote_match = re.search(r'"promote"\s*:\s*(true|false)', text, re.IGNORECASE)
        confidence_match = re.search(r'"confidence"\s*:\s*([\d.]+)', text)
        reason_match = re.search(r'"reason"\s*:\s*"([^"]*)"', text)

        if promote_match:
            return {
                "promote": promote_match.group(1).lower() == 'true',
                "confidence": float(confidence_match.group(1)) if confidence_match else 0.5,
                "reason": reason_match.group(1) if reason_match else "Parsed from response"
            }

        # Strategy 4: Look for keywords in plain text
        text_lower = text.lower()
        if 'should be promoted' in text_lower or 'recommend promotion' in text_lower:
            return {"promote": True, "confidence": 0.75, "reason": "Inferred from text"}
        if 'should not be promoted' in text_lower or 'do not recommend' in text_lower:
            return {"promote": False, "confidence": 0.75, "reason": "Inferred from text"}

        # Default: cannot parse
        return {
            "promote": False,
            "confidence": 0.0,
            "reason": "Could not parse AI response"
        }

    def evaluate_decision(self, decision: AgentDecisionSummary) -> Dict[str, Any]:
        """
        Evaluate a single decision using GPT-5-mini.

        Returns:
            dict with keys: promote (bool), confidence (float), reason (str)
        """
        topic = decision.topic or "No topic"
        insights = decision.key_insights if isinstance(decision.key_insights, list) else []
        rationale = decision.rationale or ""

        # Skip if no meaningful content
        if not insights and not rationale:
            return {
                "promote": False,
                "confidence": 0.0,
                "reason": "No insights or rationale provided"
            }

        insights_text = "\n".join([f"- {i}" for i in insights[:5]]) if insights else "None"

        prompt = f"""Evaluate this AI-generated decision for promotion to canonical policy.

DECISION TOPIC: {topic[:200]}

KEY INSIGHTS:
{insights_text[:600]}

RATIONALE:
{rationale[:500]}

EVALUATION CRITERIA:
{self.EVALUATION_CRITERIA}

Think through your evaluation carefully, then respond with JSON:
{{"promote": true, "confidence": 0.85, "reason": "explanation"}}
or
{{"promote": false, "confidence": 0.3, "reason": "explanation"}}
"""

        try:
            # GPT-5-mini: Use Responses API with proper parameters
            # Give plenty of tokens for the model to think through the evaluation
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
                reasoning={"effort": "medium"},  # Give time to think
                text={"verbosity": "medium"},    # Allow room for explanation
                max_output_tokens=500            # Plenty of tokens for reasoning
            )

            result_text = response.output_text.strip()

            # Robust JSON parsing with multiple strategies
            result = self._parse_json_response(result_text)
            return result

        except Exception as e:
            logger.error(f"Error evaluating decision {decision.id}: {e}")
            return {
                "promote": False,
                "confidence": 0.0,
                "reason": f"Evaluation error: {str(e)[:50]}"
            }

    def promote_decision(self, decision: AgentDecisionSummary, promoter: str = "AI-AutoPromoter") -> bool:
        """
        Promote a decision to canonical status.

        Args:
            decision: The decision to promote
            promoter: The name of the entity promoting (for audit trail)

        Returns:
            True if promoted successfully
        """
        try:
            with transaction.atomic():
                decision.status = 'canonical'
                decision.is_canonical = True
                decision.promoted_at = timezone.now()
                decision.promoted_by = promoter
                decision.save()
            return True
        except Exception as e:
            logger.error(f"Error promoting decision {decision.id}: {e}")
            return False

    def run_batch_promotion(
        self,
        batch_size: int = 100,
        status_filter: str = 'draft',
        promoter_name: str = "AI-AutoPromoter"
    ) -> Dict[str, Any]:
        """
        Run batch AI evaluation and promotion of decisions.

        Args:
            batch_size: Number of decisions to process
            status_filter: Only process decisions with this status
            promoter_name: Name to record as promoter

        Returns:
            Summary dict with counts
        """
        # Get pending decisions, excluding high-risk impact areas that require human judgment
        from core.services.decision_promotion_rules import NEVER_AUTO_AREAS
        decisions = AgentDecisionSummary.objects.filter(
            is_canonical=False,
            status=status_filter
        ).exclude(
            impact_area__in=NEVER_AUTO_AREAS
        ).order_by('-created_at')[:batch_size]

        total = decisions.count()
        promoted_count = 0
        rejected_count = 0
        errors = []

        logger.info(f"AI Decision Promoter: Processing {total} decisions...")

        for decision in decisions:
            # Evaluate with AI
            result = self.evaluate_decision(decision)

            if result.get("promote", False) and result.get("confidence", 0) >= self.confidence_threshold:
                # Promote
                if self.promote_decision(decision, promoter_name):
                    promoted_count += 1
                else:
                    errors.append(str(decision.id))
            else:
                rejected_count += 1

        summary = {
            "evaluated": total,
            "promoted": promoted_count,
            "rejected": rejected_count,
            "errors": len(errors),
            "promoter": promoter_name,
            "model": self.model,
            "confidence_threshold": self.confidence_threshold,
            "timestamp": timezone.now().isoformat()
        }

        logger.info(f"AI Decision Promoter Complete: {promoted_count} promoted, {rejected_count} rejected")

        return summary

    def get_promotion_stats(self) -> Dict[str, Any]:
        """Get current promotion statistics."""
        from django.db.models import Count

        total = AgentDecisionSummary.objects.count()
        canonical = AgentDecisionSummary.objects.filter(is_canonical=True).count()

        # Get promoter breakdown
        promoters = AgentDecisionSummary.objects.filter(
            is_canonical=True
        ).values('promoted_by').annotate(
            count=Count('id')
        ).order_by('-count')

        ai_promoted = sum(
            p['count'] for p in promoters
            if p['promoted_by'] and 'AI' in p['promoted_by']
        )

        return {
            "total_decisions": total,
            "canonical": canonical,
            "canonical_percentage": round(canonical / total * 100, 1) if total > 0 else 0,
            "ai_promoted": ai_promoted,
            "promoter_breakdown": list(promoters),
            "pending_draft": AgentDecisionSummary.objects.filter(
                is_canonical=False, status='draft'
            ).count()
        }


# Convenience function for one-off batch processing
def run_ai_decision_promotion(batch_size: int = 100) -> Dict[str, Any]:
    """
    Run AI decision promotion batch.

    Usage:
        from core.services.ai_decision_promoter import run_ai_decision_promotion
        result = run_ai_decision_promotion(batch_size=200)
    """
    service = AIDecisionPromoterService()
    return service.run_batch_promotion(batch_size=batch_size)
