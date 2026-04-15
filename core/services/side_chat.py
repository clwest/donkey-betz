"""
Session 555 - Phase D: Side Chat Service

Handles "Ask Pro" / "Ask Con" scoped conversations.
Each side answers in character, using only the review document context.

Flow:
1. User asks question to Pro or Con side
2. Build context from review document
3. Apply side-specific system prompt
4. Get response from GPT-5-mini
5. Save to conversation history
6. Return response with metadata
"""

import logging
from typing import Dict, Any, List

from openai import OpenAI
from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51

logger = logging.getLogger(__name__)


class SideChatService:
    """
    Manages scoped conversations with Pro and Con sides.

    Each side has a distinct persona and argues its position.
    The conversation is grounded in the review document context.
    """

    def __init__(self):
        self.client = get_openai_client()

    # System prompts for each side
    PRO_SYSTEM_PROMPT = """You are the Pro Advocate for this proposal/artifact.

Your role:
- Argue IN FAVOR of proceeding
- Highlight benefits, opportunities, and upside potential
- Address concerns constructively (reframe them as manageable)
- Use evidence from the review document
- Be optimistic but not naive - acknowledge real constraints while showing they're surmountable

You must NOT:
- Argue against the proposal
- Concede major points to the con side without reframing
- Be wishy-washy or hedge
- Ignore legitimate concerns - address them directly

Example phrases:
- "The data strongly supports..."
- "This opportunity is significant because..."
- "While there are concerns, they're manageable because..."
- "The upside potential far outweighs..."
- "Consider the cost of NOT doing this..."
- "Other teams have proven this works by..."

Be persuasive but honest. Never fabricate evidence. Answer the human's questions clearly and convincingly from the Pro perspective."""

    CON_SYSTEM_PROMPT = """You are the Con Skeptic for this proposal/artifact.

Your role:
- Argue AGAINST proceeding (or for extreme caution)
- Highlight risks, costs, and potential downsides
- Ask tough questions and demand evidence
- Use evidence from the review document
- Be rigorous but fair (not hostile or dismissive)

You must NOT:
- Argue in favor of the proposal
- Concede major points to the pro side
- Be dismissive without reasoning
- Attack the proposer personally

Example phrases:
- "But have we fully considered..."
- "The data also shows concerning..."
- "What happens if this fails?"
- "The opportunity cost of this is..."
- "Similar attempts have failed because..."
- "Before proceeding, we need clarity on..."

Be rigorous but constructive. Your goal is to surface real risks, not to be a naysayer. Answer the human's questions clearly and thoughtfully from the Con perspective."""

    # Analysis paralysis guardrail threshold
    QUESTION_WARNING_THRESHOLD = 5

    def ask_side(self, review_doc, side: str, question: str) -> Dict[str, Any]:
        """
        Ask a question to the Pro or Con side.

        Args:
            review_doc: ReviewDocument instance
            side: 'pro' or 'con'
            question: The user's question

        Returns:
            Dict with side, question, answer, message_count, total_questions
        """
        from core.models_conversation_artifacts import SideChat

        if side not in ['pro', 'con']:
            raise ValueError("Side must be 'pro' or 'con'")

        # Get or create the side chat
        side_chat, created = SideChat.objects.get_or_create(
            review_document=review_doc,
            side=side
        )

        if created:
            logger.info(f"Created new {side} chat for review {review_doc.id}")

        # Build context from review document
        context = self._build_context(review_doc, side)

        # Build conversation history
        messages = self._build_messages(side_chat, context, question, side)

        # Get response from GPT-5-mini
        # Note: gpt-5-mini is a reasoning model - needs extra tokens for reasoning + output
        try:
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=messages,
                max_completion_tokens=2000,  # Extra for reasoning tokens
            )
            answer = response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error getting {side} response: {e}")
            answer = (
                f"I apologize, but I encountered an issue formulating my response. "
                f"Please try rephrasing your question."
            )

        # Add analysis paralysis warning if threshold exceeded
        total_questions = review_doc.questions_asked_pro + review_doc.questions_asked_con + 1
        if total_questions >= self.QUESTION_WARNING_THRESHOLD:
            answer += (
                f"\n\n---\n*Note: You've asked {total_questions} questions. "
                "Consider making a decision, or defer if you need more information from other sources.*"
            )

        # Save to chat history
        side_chat.add_message('user', question)
        side_chat.add_message('assistant', answer)

        # Update review doc stats
        if side == 'pro':
            review_doc.questions_asked_pro += 1
        else:
            review_doc.questions_asked_con += 1
        review_doc.save()

        logger.info(
            f"Side chat response: {side} for review {review_doc.id} "
            f"(question #{side_chat.message_count // 2})"
        )

        return {
            'side': side,
            'question': question,
            'answer': answer,
            'message_count': side_chat.message_count,
            'questions_this_side': (
                review_doc.questions_asked_pro if side == 'pro'
                else review_doc.questions_asked_con
            ),
            'total_questions': total_questions,
        }

    def _build_context(self, review_doc, side: str) -> str:
        """Build context string from review document."""
        from core.models_conversation_artifacts import ExtractedArtifact

        # Get target-specific context
        target_context = ""

        if review_doc.target_type == 'artifact':
            try:
                artifact = ExtractedArtifact.objects.get(id=review_doc.target_id)
                target_context = f"""
ARTIFACT DETAILS:
- Type: {artifact.get_artifact_type_display()}
- Title: {artifact.title}
- Description: {artifact.description}
- Importance: {artifact.importance_score:.2f}
- Urgency: {artifact.urgency_score:.2f}
"""
            except ExtractedArtifact.DoesNotExist:
                target_context = "ARTIFACT: Details not available"

        elif review_doc.target_type == 'dream':
            # Session 556 Option D: Dream context
            try:
                from core.models_unified_system import AgentDream
                dream = AgentDream.objects.get(id=review_doc.target_id)
                content_preview = (dream.content or '')[:500]
                if len(dream.content or '') > 500:
                    content_preview += '...'
                # Build scores display
                scores = []
                if hasattr(dream, 'actionability_score') and dream.actionability_score:
                    scores.append(f"Actionability: {dream.actionability_score:.2f}")
                if hasattr(dream, 'creativity_score') and dream.creativity_score:
                    scores.append(f"Creativity: {dream.creativity_score:.2f}")
                if hasattr(dream, 'composite_score') and dream.composite_score:
                    scores.append(f"Composite: {dream.composite_score:.2f}")
                scores_str = ' | '.join(scores) if scores else 'Not scored'
                target_context = f"""
DREAM DETAILS:
- Title: {dream.title}
- Category: {dream.dream_type or 'Unknown'}
- Dreaming Agent: {dream.agent.name if dream.agent else 'Unknown'}
- Inspiration: {dream.inspiration_source or 'Not specified'}
- Scores: {scores_str}
- Content Preview: {content_preview}
"""
            except Exception:
                target_context = "DREAM: Details not available"

        # Format open questions
        open_questions = review_doc.open_questions or []
        questions_str = '\n'.join(f"- {q}" for q in open_questions) if open_questions else "None identified"

        # Format key evidence
        key_evidence = review_doc.key_evidence or {}
        pro_evidence = key_evidence.get('pro', [])
        con_evidence = key_evidence.get('con', [])
        pro_evidence_str = '\n'.join(f"  - {e}" for e in pro_evidence) if pro_evidence else "  None"
        con_evidence_str = '\n'.join(f"  - {e}" for e in con_evidence) if con_evidence else "  None"

        return f"""
REVIEW DOCUMENT CONTEXT:

{target_context}

NEUTRAL SUMMARY:
{review_doc.neutral_summary}

PRO CASE (Arguments FOR):
{review_doc.pro_case}

CON CASE (Arguments AGAINST):
{review_doc.con_case}

OPEN QUESTIONS:
{questions_str}

KEY EVIDENCE:
Pro:
{pro_evidence_str}
Con:
{con_evidence_str}

AI RECOMMENDATION: {review_doc.ai_recommendation}
AI LEAN: {review_doc.ai_lean} (confidence: {review_doc.ai_confidence:.0%})

You are arguing the {side.upper()} side. Stay in character and be persuasive.
"""

    def _build_messages(
        self,
        side_chat,
        context: str,
        new_question: str,
        side: str
    ) -> List[Dict[str, str]]:
        """Build message list for API call."""

        system_prompt = self.PRO_SYSTEM_PROMPT if side == 'pro' else self.CON_SYSTEM_PROMPT

        messages = [
            {"role": "system", "content": f"{system_prompt}\n\n{context}"}
        ]

        # Add conversation history (existing messages)
        for msg in side_chat.messages:
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })

        # Add new question
        messages.append({"role": "user", "content": new_question})

        return messages

    def get_chat_history(self, review_doc, side: str) -> List[Dict[str, Any]]:
        """
        Get the conversation history for a side.

        Args:
            review_doc: ReviewDocument instance
            side: 'pro' or 'con'

        Returns:
            List of message dicts with role, content, timestamp
        """
        from core.models_conversation_artifacts import SideChat

        try:
            side_chat = SideChat.objects.get(review_document=review_doc, side=side)
            return side_chat.messages
        except SideChat.DoesNotExist:
            return []

    def clear_chat_history(self, review_doc, side: str) -> bool:
        """
        Clear conversation history for a side (for starting fresh).

        Args:
            review_doc: ReviewDocument instance
            side: 'pro' or 'con'

        Returns:
            True if cleared, False if chat didn't exist
        """
        from core.models_conversation_artifacts import SideChat

        try:
            side_chat = SideChat.objects.get(review_document=review_doc, side=side)
            side_chat.messages = []
            side_chat.message_count = 0
            side_chat.save()

            # Reset the question counter
            if side == 'pro':
                review_doc.questions_asked_pro = 0
            else:
                review_doc.questions_asked_con = 0
            review_doc.save()

            logger.info(f"Cleared {side} chat history for review {review_doc.id}")
            return True
        except SideChat.DoesNotExist:
            return False

    def get_both_histories(self, review_doc) -> Dict[str, List[Dict]]:
        """
        Get conversation histories for both sides.

        Returns:
            Dict with 'pro' and 'con' keys, each containing message list
        """
        return {
            'pro': self.get_chat_history(review_doc, 'pro'),
            'con': self.get_chat_history(review_doc, 'con'),
        }


# Singleton instance
side_chat_service = SideChatService()
