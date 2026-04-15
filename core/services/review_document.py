"""
Session 555 - Phase D: Review Document Generation Service

Generates interactive decision briefs with pro/con cases.
Uses GPT-5-mini for balanced analysis.

Flow:
1. Load artifact and context (source conversation, agent, etc.)
2. Generate neutral summary
3. Generate pro case (arguments FOR proceeding)
4. Generate con case (arguments AGAINST / risks)
5. Identify open questions
6. Provide AI recommendation with confidence
"""

import json
import logging
from typing import Dict, Any

from django.db import transaction
from openai import OpenAI
from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51

logger = logging.getLogger(__name__)


class ReviewDocumentService:
    """
    Generates ReviewDocuments for pending artifacts.

    Creates balanced decision briefs with pro/con cases,
    open questions, and AI recommendations.
    """

    def __init__(self):
        self.client = get_openai_client()

    def generate_review_document(self, artifact) -> 'ReviewDocument':
        """
        Generate a complete review document for an artifact.

        Args:
            artifact: ExtractedArtifact instance

        Returns:
            ReviewDocument: The generated review document
        """
        from core.models_conversation_artifacts import ReviewDocument, SideChat

        logger.info(f"Generating review document for artifact: {artifact.title[:50]}")

        # 1. Gather context
        context = self._gather_context(artifact)

        # 2. Generate all sections via GPT-5-mini
        analysis = self._generate_analysis(artifact, context)

        # 3. Create ReviewDocument with transaction
        with transaction.atomic():
            review_doc = ReviewDocument.objects.create(
                target_type='artifact',
                target_id=artifact.id,
                neutral_summary=analysis.get('neutral_summary', 'Summary not available'),
                pro_case=analysis.get('pro_case', 'Pro case not available'),
                con_case=analysis.get('con_case', 'Con case not available'),
                open_questions=analysis.get('open_questions', []),
                key_evidence=analysis.get('key_evidence', {'pro': [], 'con': []}),
                ai_recommendation=analysis.get('ai_recommendation', 'No recommendation'),
                ai_lean=analysis.get('ai_lean', 'neutral'),
                ai_confidence=float(analysis.get('ai_confidence', 0.5)),
                status='awaiting_human',
            )

            # 4. Create empty side chats for Pro and Con
            SideChat.objects.create(review_document=review_doc, side='pro')
            SideChat.objects.create(review_document=review_doc, side='con')

        logger.info(
            f"Review document created: {review_doc.id} "
            f"(AI lean: {review_doc.ai_lean}, confidence: {review_doc.ai_confidence:.0%})"
        )

        return review_doc

    def _gather_context(self, artifact) -> Dict[str, Any]:
        """Gather all relevant context for the artifact."""
        context = {
            'artifact_type': artifact.artifact_type,
            'artifact_type_display': artifact.get_artifact_type_display(),
            'title': artifact.title,
            'description': artifact.description,
            'details': artifact.details or {},
            'importance_score': artifact.importance_score,
            'urgency_score': artifact.urgency_score,
            'composite_score': artifact.composite_score,
            'source_agent': artifact.source_agent.name if artifact.source_agent else None,
        }

        # Add conversation context if available
        if artifact.conversation:
            context['conversation_topic'] = artifact.conversation.topic
            context['conversation_conclusion'] = (
                artifact.conversation.conclusion[:500]
                if artifact.conversation.conclusion else None
            )
            # Get participant agents
            participants = artifact.conversation.participants.all()[:5]
            context['conversation_participants'] = [p.name for p in participants]

        return context

    def _generate_analysis(self, artifact, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate all review sections via GPT-5-mini.

        Returns dict with:
        - neutral_summary
        - pro_case
        - con_case
        - open_questions
        - key_evidence
        - ai_recommendation
        - ai_lean
        - ai_confidence
        """
        # Format context for prompt
        details_str = json.dumps(context['details'], indent=2) if context['details'] else 'None'
        participants_str = ', '.join(context.get('conversation_participants', [])) or 'Unknown'

        prompt = f"""Analyze this artifact for human review and provide a balanced assessment.

ARTIFACT:
Type: {context['artifact_type_display']}
Title: {context['title']}
Description: {context['description']}

Details:
{details_str}

Scores: Importance {context['importance_score']:.2f} | Urgency {context['urgency_score']:.2f} | Composite {context['composite_score']:.2f}
Source Agent: {context.get('source_agent', 'Unknown')}
Conversation Topic: {context.get('conversation_topic', 'N/A')}
Participants: {participants_str}

TASK: Provide a balanced decision brief in JSON format with:

1. "neutral_summary": 2-3 sentence objective summary of what's being proposed. Be factual and neutral.

2. "pro_case": 3-5 bullet points arguing FOR this (benefits, opportunities, upside potential). Format as a single string with newlines between bullets.

3. "con_case": 3-5 bullet points arguing AGAINST this (risks, costs, potential downsides). Format as a single string with newlines between bullets.

4. "open_questions": List of 2-4 questions that need answers before deciding. Each as a string in an array.

5. "key_evidence": Object with "pro" array (evidence supporting) and "con" array (evidence against). Each item is a brief string.

6. "ai_recommendation": 2-3 sentence recommendation with nuance. Consider tradeoffs.

7. "ai_lean": One of: "strong_approve", "lean_approve", "neutral", "lean_decline", "strong_decline", "pilot", "defer"

8. "ai_confidence": Float from 0.0 to 1.0 indicating confidence in the recommendation.

Be balanced and fair. Present strong arguments for BOTH sides. The goal is to help a human make an informed decision, not to bias them one way or another.

If the artifact lacks detail, note that in open_questions and reduce confidence accordingly."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an objective analyst preparing decision briefs for a Chief of Staff. "
                            "Be balanced, fair, and thorough. Present strong arguments for BOTH sides. "
                            "Your job is to inform, not to decide. Return valid JSON only."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=2000,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            # Validate ai_lean is a valid choice
            valid_leans = [
                'strong_approve', 'lean_approve', 'neutral',
                'lean_decline', 'strong_decline', 'pilot', 'defer'
            ]
            if result.get('ai_lean') not in valid_leans:
                result['ai_lean'] = 'neutral'

            # Validate ai_confidence is a float between 0 and 1
            try:
                result['ai_confidence'] = max(0.0, min(1.0, float(result.get('ai_confidence', 0.5))))
            except (TypeError, ValueError):
                result['ai_confidence'] = 0.5

            logger.info(
                f"Analysis generated: lean={result.get('ai_lean')}, "
                f"confidence={result.get('ai_confidence'):.0%}"
            )
            return result

        except Exception as e:
            logger.error(f"Failed to generate analysis: {e}")
            # Return fallback analysis
            return {
                'neutral_summary': (
                    f"This is a {context['artifact_type_display'].lower()} titled "
                    f"'{context['title']}'. Review the details below to make a decision."
                ),
                'pro_case': (
                    f"- Proposed by {context.get('source_agent', 'an agent')}\n"
                    f"- Importance score: {context['importance_score']:.2f}\n"
                    f"- Identified during agent collaboration"
                ),
                'con_case': (
                    "- Requires human review and validation\n"
                    "- May need additional context\n"
                    "- Resource implications unclear"
                ),
                'open_questions': [
                    "What resources are needed to proceed?",
                    "What is the expected timeline?",
                    "Are there dependencies on other work?",
                ],
                'key_evidence': {
                    'pro': ['Agent collaboration identified this as valuable'],
                    'con': ['Automated extraction may miss nuance']
                },
                'ai_recommendation': (
                    "Unable to generate full analysis. Please review the artifact "
                    "details directly and consider consulting with relevant agents."
                ),
                'ai_lean': 'neutral',
                'ai_confidence': 0.3,
            }

    def get_or_create_for_artifact(self, artifact_id: str) -> 'ReviewDocument':
        """
        Get existing or create new review document for an artifact.

        Args:
            artifact_id: UUID of the artifact

        Returns:
            ReviewDocument: Existing or newly created review document
        """
        from core.models_conversation_artifacts import ReviewDocument, ExtractedArtifact

        try:
            return ReviewDocument.objects.get(
                target_type='artifact',
                target_id=artifact_id
            )
        except ReviewDocument.DoesNotExist:
            artifact = ExtractedArtifact.objects.get(id=artifact_id)
            return self.generate_review_document(artifact)

    def regenerate_review_document(self, review_doc) -> 'ReviewDocument':
        """
        Regenerate analysis for an existing review document.

        Useful if the original analysis was incomplete or context has changed.
        """
        from core.models_conversation_artifacts import ExtractedArtifact

        if review_doc.target_type != 'artifact':
            raise ValueError("Can only regenerate for artifact targets")

        artifact = ExtractedArtifact.objects.get(id=review_doc.target_id)
        context = self._gather_context(artifact)
        analysis = self._generate_analysis(artifact, context)

        # Update the review document
        review_doc.neutral_summary = analysis.get('neutral_summary', review_doc.neutral_summary)
        review_doc.pro_case = analysis.get('pro_case', review_doc.pro_case)
        review_doc.con_case = analysis.get('con_case', review_doc.con_case)
        review_doc.open_questions = analysis.get('open_questions', review_doc.open_questions)
        review_doc.key_evidence = analysis.get('key_evidence', review_doc.key_evidence)
        review_doc.ai_recommendation = analysis.get('ai_recommendation', review_doc.ai_recommendation)
        review_doc.ai_lean = analysis.get('ai_lean', review_doc.ai_lean)
        review_doc.ai_confidence = float(analysis.get('ai_confidence', review_doc.ai_confidence))
        review_doc.save()

        logger.info(f"Review document regenerated: {review_doc.id}")
        return review_doc

    def get_pending_reviews(self, limit: int = 20):
        """Get review documents awaiting human decision."""
        from core.models_conversation_artifacts import ReviewDocument
        return ReviewDocument.objects.filter(
            status='awaiting_human'
        ).order_by('-created_at')[:limit]

    def get_review_stats(self) -> Dict[str, Any]:
        """Get statistics about review documents."""
        from core.models_conversation_artifacts import ReviewDocument

        total = ReviewDocument.objects.count()
        by_status = {}
        for status, _ in ReviewDocument.STATUS_CHOICES:
            by_status[status] = ReviewDocument.objects.filter(status=status).count()

        by_lean = {}
        for lean, _ in ReviewDocument.AI_LEAN_CHOICES:
            by_lean[lean] = ReviewDocument.objects.filter(ai_lean=lean).count()

        return {
            'total': total,
            'by_status': by_status,
            'by_ai_lean': by_lean,
            'awaiting_human': by_status.get('awaiting_human', 0),
        }

    # =========================================================================
    # Session 556 Option D: Dream Reviews
    # =========================================================================

    def generate_dream_review(self, dream) -> 'ReviewDocument':
        """
        Generate a review document for an AgentDream.

        Args:
            dream: AgentDream instance

        Returns:
            ReviewDocument: The generated review document
        """
        from core.models_conversation_artifacts import ReviewDocument, SideChat

        logger.info(f"Generating review document for dream: {dream.title[:50]}")

        # 1. Gather dream context
        context = self._gather_dream_context(dream)

        # 2. Generate analysis
        analysis = self._generate_dream_analysis(dream, context)

        # 3. Create ReviewDocument with transaction
        with transaction.atomic():
            review_doc = ReviewDocument.objects.create(
                target_type='dream',
                target_id=dream.id,
                neutral_summary=analysis.get('neutral_summary', 'Summary not available'),
                pro_case=analysis.get('pro_case', 'Pro case not available'),
                con_case=analysis.get('con_case', 'Con case not available'),
                open_questions=analysis.get('open_questions', []),
                key_evidence=analysis.get('key_evidence', {'pro': [], 'con': []}),
                ai_recommendation=analysis.get('ai_recommendation', 'No recommendation'),
                ai_lean=analysis.get('ai_lean', 'neutral'),
                ai_confidence=float(analysis.get('ai_confidence', 0.5)),
                status='awaiting_human',
            )

            # Create side chats
            SideChat.objects.create(review_document=review_doc, side='pro')
            SideChat.objects.create(review_document=review_doc, side='con')

        logger.info(
            f"Dream review created: {review_doc.id} "
            f"(AI lean: {review_doc.ai_lean}, confidence: {review_doc.ai_confidence:.0%})"
        )

        return review_doc

    def _gather_dream_context(self, dream) -> Dict[str, Any]:
        """Gather context from an AgentDream."""
        # Create a brief description from the first 200 chars of content
        content = dream.content or ''
        brief_description = content[:200] + '...' if len(content) > 200 else content

        context = {
            'dream_type': 'Agent Dream',
            'title': dream.title,
            'description': brief_description,
            'dream_content': content,
            'priority': getattr(dream, 'priority', 'medium'),
            'source_agent': dream.agent.name if dream.agent else 'Unknown',
            'dreamed_at': dream.dreamed_at.isoformat() if dream.dreamed_at else None,
        }

        # Add dream-specific scoring fields
        if hasattr(dream, 'vividness_score'):
            context['vividness_score'] = dream.vividness_score
        if hasattr(dream, 'creativity_score'):
            context['creativity_score'] = dream.creativity_score
        if hasattr(dream, 'actionability_score'):
            context['actionability_score'] = dream.actionability_score
        if hasattr(dream, 'relevance_score'):
            context['relevance_score'] = dream.relevance_score
        if hasattr(dream, 'composite_score'):
            context['composite_score'] = dream.composite_score
        if hasattr(dream, 'inspiration_source') and dream.inspiration_source:
            context['inspiration_source'] = dream.inspiration_source
        if hasattr(dream, 'related_topics') and dream.related_topics:
            context['related_topics'] = dream.related_topics
        if hasattr(dream, 'dream_type') and dream.dream_type:
            context['dream_category'] = dream.dream_type

        return context

    def _generate_dream_analysis(self, dream, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analysis for a dream."""

        # Truncate content if too long
        content_preview = context.get('dream_content', '')[:1500]
        if len(context.get('dream_content', '')) > 1500:
            content_preview += '...'

        # Build scores section
        scores_section = ""
        if 'vividness_score' in context:
            scores_section += f"Vividness: {context['vividness_score']:.2f} | "
        if 'creativity_score' in context:
            scores_section += f"Creativity: {context['creativity_score']:.2f} | "
        if 'actionability_score' in context:
            scores_section += f"Actionability: {context['actionability_score']:.2f} | "
        if 'relevance_score' in context:
            scores_section += f"Relevance: {context['relevance_score']:.2f}"
        if 'composite_score' in context:
            scores_section += f"\nComposite Score: {context['composite_score']:.2f}"

        prompt = f"""Analyze this Agent Dream for human review and provide a balanced assessment.

DREAM:
Title: {context['title']}
Summary: {context['description']}
Category: {context.get('dream_category', 'Unknown')}

Content:
{content_preview}

Dreaming Agent: {context.get('source_agent', 'Unknown')}
Inspiration: {context.get('inspiration_source', 'Not specified')}
Related Topics: {', '.join(context.get('related_topics', [])) if context.get('related_topics') else 'None'}

SCORES:
{scores_section if scores_section else 'Not scored'}

TASK: Provide a balanced decision brief in JSON format with:

1. "neutral_summary": 2-3 sentence objective summary of what this dream proposes. Be factual and neutral.

2. "pro_case": 3-5 bullet points arguing FOR investing in this dream (benefits, innovation potential, strategic value). Format as a single string with newlines between bullets.

3. "con_case": 3-5 bullet points arguing AGAINST or highlighting risks (resource cost, uncertainty, opportunity cost). Format as a single string with newlines between bullets.

4. "open_questions": List of 2-4 questions to resolve before committing. Each as a string in an array.

5. "key_evidence": Object with "pro" array (supporting points) and "con" array (concerning points). Each item is a brief string.

6. "ai_recommendation": 2-3 sentence recommendation with nuance.

7. "ai_lean": One of: "strong_approve", "lean_approve", "neutral", "lean_decline", "strong_decline", "pilot", "defer"

8. "ai_confidence": Float from 0.0 to 1.0 indicating confidence in the recommendation.

Consider: Is this dream actionable? Does it align with platform goals? What's the potential ROI? Is the agent qualified to execute this?"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an objective analyst evaluating Agent Dreams for investment. "
                            "Be balanced, consider resource implications, and provide actionable insights. "
                            "Return valid JSON only."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=2000,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            # Validate ai_lean
            valid_leans = [
                'strong_approve', 'lean_approve', 'neutral',
                'lean_decline', 'strong_decline', 'pilot', 'defer'
            ]
            if result.get('ai_lean') not in valid_leans:
                result['ai_lean'] = 'neutral'

            # Validate ai_confidence
            try:
                result['ai_confidence'] = max(0.0, min(1.0, float(result.get('ai_confidence', 0.5))))
            except (TypeError, ValueError):
                result['ai_confidence'] = 0.5

            logger.info(
                f"Dream analysis generated: lean={result.get('ai_lean')}, "
                f"confidence={result.get('ai_confidence'):.0%}"
            )
            return result

        except Exception as e:
            logger.error(f"Failed to generate dream analysis: {e}")
            return self._fallback_dream_analysis(context)

    def _fallback_dream_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis if API fails."""
        return {
            'neutral_summary': (
                f"Dream from {context.get('source_agent', 'an agent')}: {context['title']}. "
                "This dream proposes a new initiative that requires human evaluation."
            ),
            'pro_case': (
                "- Agent has identified an opportunity worth exploring\n"
                "- Could advance platform capabilities\n"
                "- Shows proactive thinking from the agent"
            ),
            'con_case': (
                "- Requires investment of resources\n"
                "- May have opportunity costs\n"
                "- Details may need clarification"
            ),
            'open_questions': [
                "What specific resources are needed?",
                "What is the expected timeline?",
                "How does this align with current priorities?",
            ],
            'key_evidence': {
                'pro': ['Agent-initiated proposal shows engagement'],
                'con': ['Automated analysis unavailable - needs manual review']
            },
            'ai_recommendation': (
                "Unable to generate full analysis. Please review the dream "
                "details directly and consider the agent's track record."
            ),
            'ai_lean': 'neutral',
            'ai_confidence': 0.3,
        }

    def get_or_create_for_dream(self, dream_id: str) -> 'ReviewDocument':
        """
        Get existing or create new review document for a dream.

        Args:
            dream_id: UUID of the dream

        Returns:
            ReviewDocument: Existing or newly created review document
        """
        from core.models_conversation_artifacts import ReviewDocument
        from core.models_unified_system import AgentDream

        try:
            return ReviewDocument.objects.get(
                target_type='dream',
                target_id=dream_id
            )
        except ReviewDocument.DoesNotExist:
            dream = AgentDream.objects.get(id=dream_id)
            return self.generate_dream_review(dream)


# Singleton instance
review_service = ReviewDocumentService()
